# src/runner.py
import math
import time
from src.io_parsing import read_matrix_file, ParseError
from src.arbitrage import detect_arbitrage
from src.best_rate import best_conversion

def _print_exec_time(start_ns: int) -> None:
    elapsed_ns = time.perf_counter_ns() - start_ns
    elapsed_ms = elapsed_ns / 1e6
    print(f"Execution time: {elapsed_ns} ns ({elapsed_ms:.3f} ms)")

def run_case(input_file: str, eps: float = 1e-12, tol: float = 1e-12) -> None:
    """
    Runs one test case:
    - Reads the file
    - Detects arbitrage
    - Prints results (cycle + profit) or best conversion path/rate

    Pair selection policy (to match the example test cases in the brief):
      - If there are exactly 3 currencies, report A -> C.
      - If there are 5 or more currencies, report A -> B.
      - Otherwise (n < 3), fall back to A -> last.
    """
    start_ns = time.perf_counter_ns()

    try:
        labels, R = read_matrix_file(input_file)
    except ParseError as e:
        print(f"Error: {e}")
        _print_exec_time(start_ns)
        return

    print(f"Loaded currencies: {', '.join(labels)} (n={len(labels)})")

    # Arbitrage detection
    exists, cyc, prof = detect_arbitrage(R, eps=eps, tol=tol)

    if exists and cyc:
        cyc_labels = [labels[i] for i in cyc] + [labels[cyc[0]]]
        profit_pct = (prof - 1.0) * 100 if prof else 0
        print("Arbitrage detected!")
        print(f"Arbitrage cycle: {' -> '.join(cyc_labels)}.")
        print(f"Profit: {profit_pct:.2f}%.")
        _print_exec_time(start_ns)
        return

    # If no arbitrage, compute best conversion (policy described above)
    n = len(labels)
    s = 0
    if n == 3:
        t = 2  # A -> C
    elif n >= 2:
        t = 1  # A -> B
    else:
        t = n - 1  # fallback

    best_rate, path = best_conversion(R, s, t, eps=eps)

    if path and best_rate is not None:
        path_labels = [labels[i] for i in path]
        print("No arbitrage detected.")
        print(f"Best conversion rate from {labels[s]} to {labels[t]}: {best_rate:.4f}.")
        print(f"Best path: {' -> '.join(path_labels)}.")
    else:
        print("No arbitrage detected.")
        print("Best conversion rate from {0} to {1}: N/A".format(labels[s], labels[t]))

    _print_exec_time(start_ns)
