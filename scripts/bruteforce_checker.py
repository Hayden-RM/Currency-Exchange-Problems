#!/usr/bin/env python3
"""
Brute-force checker for Currency-Exchange-Problems.
- Computes ground-truth expected outputs by exhaustive search (best arbitrage cycle or best s->t path when no arbitrage)
- Runs the project's `run_case` function for each test and compares the printed output to the expected output.

Do not modify project files; this script only imports and calls existing functions.

Usage: python3 scripts/bruteforce_checker.py
"""
import os
import math
from typing import List, Tuple, Optional
from io import StringIO
import sys
from contextlib import redirect_stdout

# Ensure project root is on sys.path so `src` package can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import project functions
from src.io_parsing import read_matrix_file, ParseError
from src.runner import run_case


# Helpers: brute-force search for best cycle and best path

def best_cycle_bruteforce(R: List[List[float]], tol: float = 1e-12) -> Optional[Tuple[List[int], float]]:
    n = len(R)
    best_prod = 0.0
    best_cycle = None

    def dfs(start: int, curr: int, visited: List[int], prod: float):
        nonlocal best_prod, best_cycle
        for nxt in range(n):
            rate = R[curr][nxt]
            if rate <= 0:
                continue
            if nxt == start and len(visited) >= 1:
                # close cycle
                cycle_prod = prod * rate
                if cycle_prod > best_prod + tol:
                    best_prod = cycle_prod
                    best_cycle = visited.copy()
                elif abs(cycle_prod - best_prod) <= tol and best_prod > 0.0:
                    # tie-breaker: prefer shorter cycle, then lexicographic labels (indices)
                    if best_cycle is not None:
                        if len(visited) < len(best_cycle):
                            best_cycle = visited.copy()
                        elif len(visited) == len(best_cycle) and tuple(visited) < tuple(best_cycle):
                            best_cycle = visited.copy()
                # do not continue after closing
            elif nxt not in visited and nxt != start:
                visited.append(nxt)
                dfs(start, nxt, visited, prod * rate)
                visited.pop()

    for s in range(n):
        dfs(s, s, [s], 1.0)  # start path contains s; will consider cycles that revisit s

    if best_cycle is None:
        return None
    # best_cycle currently holds visited nodes including start repeated? We stored visited as include s and path nodes; ensure it's a cycle without repeated final
    # Normalize cycle to start with first element as stored
    # If best_cycle length >=1 (includes s as first), convert to indices sequence without duplicate trailing
    # Our stored visited contains the nodes in order, starting at s; ensure first element is s
    if len(best_cycle) >= 1 and best_cycle[0] != best_cycle[-1]:
        # drop possible trailing repetition
        pass
    # Return cycle as list of indices (without duplicate closure) and product
    # Compute product for safety
    prod = 1.0
    cyc = best_cycle
    for i in range(len(cyc)):
        j = (i + 1) % len(cyc)
        prod *= R[cyc[i]][cyc[j]]

    return cyc, prod


def best_path_bruteforce(R: List[List[float]], s: int, t: int, tol: float = 1e-12) -> Optional[Tuple[List[int], float]]:
    n = len(R)
    best_prod = 0.0
    best_path = None

    def dfs(curr: int, visited: List[int], prod: float):
        nonlocal best_prod, best_path
        if curr == t:
            if prod > best_prod + tol:
                best_prod = prod
                best_path = visited.copy()
            elif abs(prod - best_prod) <= tol and best_path is not None:
                # tie-breaker: shorter path, then lexicographic
                if len(visited) < len(best_path):
                    best_path = visited.copy()
                elif len(visited) == len(best_path) and tuple(visited) < tuple(best_path):
                    best_path = visited.copy()
            return
        for nxt in range(n):
            if nxt in visited:
                continue
            rate = R[curr][nxt]
            if rate <= 0:
                continue
            visited.append(nxt)
            dfs(nxt, visited, prod * rate)
            visited.pop()

    dfs(s, [s], 1.0)
    if best_path is None:
        return None
    return best_path, best_prod


def expected_output_for_file(path: str) -> Tuple[str, str]:
    """Return (expected_text, summary_key) for the given test file.
    summary_key is a short single-line canonical representation used for comparison (for easy diffing).
    """
    try:
        labels, R = read_matrix_file(path)
    except ParseError as e:
        expected = f"Error: {e}"
        return expected, expected

    n = len(labels)
    # Determine s and t according to run_case policy
    s = 0
    if n == 3:
        t = 2
    elif n >= 2:
        t = 1
    else:
        t = n - 1

    # Arbitrage brute-force
    cyc_res = best_cycle_bruteforce(R)
    if cyc_res is not None:
        cyc, prod = cyc_res
        # cyc is a list of node indices in order; runner constructs cyc_labels = [labels[i] for i in cyc] + [labels[cyc[0]]]
        cyc_labels = [labels[i] for i in cyc] + [labels[cyc[0]]]
        profit_pct = (prod - 1.0) * 100.0
        expected_lines = [
            "Arbitrage detected!",
            f"Arbitrage cycle: {' -> '.join(cyc_labels)}.",
            f"Profit: {profit_pct:.2f}%.",
        ]
        expected = "\n".join(expected_lines)
        # summary key
        key = f"ARBITRAGE|{','.join(cyc_labels)}|{profit_pct:.6f}"
        return expected, key

    # No arbitrage: compute best conversion s->t
    path_res = best_path_bruteforce(R, s, t)
    if path_res is not None:
        path, rate = path_res
        path_labels = [labels[i] for i in path]
        expected_lines = [
            "No arbitrage detected.",
            f"Best conversion rate from {labels[s]} to {labels[t]}: {rate:.4f}.",
            f"Best path: {' -> '.join(path_labels)}.",
        ]
        expected = "\n".join(expected_lines)
        key = f"RATE|{labels[s]}->{labels[t]}|{rate:.12f}|{','.join(path_labels)}"
        return expected, key

    # No path
    expected = f"No arbitrage detected.\nBest conversion rate from {labels[s]} to {labels[t]}: N/A"
    return expected, expected


def run_checker():
    test_dir = os.path.join(os.getcwd(), "tests")
    files = sorted(f for f in os.listdir(test_dir) if f.endswith('.txt'))

    overall = []

    for fname in files:
        fpath = os.path.join(test_dir, fname)
        print(f"--- Checking: {fname} ---")
        # Compute expected
        expected_text, expected_key = expected_output_for_file(fpath)

        # Capture program output for this single case by calling run_case
        buf = StringIO()
        with redirect_stdout(buf):
            run_case(fpath)
        program_out = buf.getvalue().strip()

        # For easier comparison, extract meaningful lines from program_out
        # We will look for either Error: ... line or the block printed in run_case
        prog_key = None
        if program_out.startswith("Error:"):
            prog_key = program_out.strip()
        else:
            # Normalize multiline blocks: remove "Loaded currencies" header, compare remaining block
            lines = [ln.strip() for ln in program_out.splitlines() if ln.strip() and not ln.strip().startswith('Loaded currencies:')]
            prog_text = "\n".join(lines).strip()
            prog_key = prog_text

        # Now compare expected_key with prog_key in a robust way
        match = False
        if expected_key == prog_key:
            match = True
        else:
            # Try looser comparison: compare numeric values (profit or rate) within tolerance
            try:
                if expected_key.startswith('ARBITRAGE') and prog_key.startswith('Arbitrage detected'):
                    # parse numbers
                    # expected_key like ARBITRAGE|A,B,C,A|profit
                    exp_parts = expected_key.split('|')
                    exp_profit = float(exp_parts[2])
                    # extract profit from prog_key
                    # find last line Profit: X%
                    for ln in prog_key.splitlines()[1:]:
                        if ln.startswith('Profit:'):
                            prog_profit = float(ln.split(':',1)[1].strip().rstrip('%.'))
                            # program prints percent already; expected_key is percent too
                            if abs(prog_profit - exp_profit) < 1e-6:
                                match = True
                            break
                elif expected_key.startswith('RATE') and prog_key.startswith('No arbitrage detected'):
                    # compare rate numerically
                    exp_parts = expected_key.split('|')
                    exp_rate = float(exp_parts[2])
                    # extract rate from program
                    for ln in prog_key.splitlines():
                        if ln.startswith('Best conversion rate from'):
                            # format "Best conversion rate from A to B: 0.8550."
                            num = ln.split(':',1)[1].strip().rstrip('.')
                            prog_rate = float(num)
                            if abs(prog_rate - exp_rate) < 1e-8:
                                match = True
                            break
            except Exception:
                match = False

        status = "OK" if match else "MISMATCH"
        print(f"Expected (key): {expected_key}")
        print(f"Program  (key): {prog_key}")
        print(f"Result: {status}\n")
        overall.append((fname, status, expected_key, prog_key))

    # Summary
    print("=== Summary ===")
    ok = sum(1 for r in overall if r[1] == 'OK')
    total = len(overall)
    print(f"{ok} / {total} tests match expected brute-force outputs.")
    for fname, status, exp, prog in overall:
        if status != 'OK':
            print(f"- {fname}: {status}")


if __name__ == '__main__':
    run_checker()
