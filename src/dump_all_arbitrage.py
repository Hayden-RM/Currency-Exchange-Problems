"""Brute-force enumerator for small exchange graphs.

This module provides `dump_all_arbitrage(R, labels, ...)` which prints all
simple arbitrage cycles found by exhaustive search. Intended for debugging
and validation on small `n` (e.g., n <= 6).
"""

from typing import List, Tuple, Optional, Set


def dump_all_arbitrage(
    R: List[List[float]],
    labels: List[str],
    *,
    profit_tol: float = 1e-9,
    max_len: Optional[int] = None,
    limit: Optional[int] = None,
    sort_desc: bool = True,
) -> None:
    """
    Brute-force enumerate and print ALL simple arbitrage cycles (profit > 1 + profit_tol).
    Prints nothing if no arbitrage cycles are found (so you can sprinkle it in tests safely).

    Parameters
    ----------
    R : List[List[float]]
        Exchange-rate matrix where R[u][v] > 0 means a directed edge u->v exists with that rate.
    labels : List[str]
        Names for each index in R.
    profit_tol : float
        Minimum excess over 1 to accept a cycle; use 1e-9 to ignore FP noise.
    max_len : Optional[int]
        Optional cap on the cycle length (#distinct nodes in cycle). Default: n (no extra cap).
    limit : Optional[int]
        Optional cap on total cycles printed (useful for big graphs).
    sort_desc : bool
        Sort cycles by profit descending (True) or ascending (False).
    """
    cycles = _all_arbitrage_opportunities(R, profit_tol=profit_tol, max_len=max_len, limit=limit)
    if not cycles:
        return  # no-op if none (keeps runner output clean unless there is arb)

    # Sort by profit
    cycles.sort(key=lambda x: x[1], reverse=sort_desc)

    # Summary header
    best_mult = cycles[0][1]
    best_gain = (best_mult - 1.0) * 100.0
    print("=== Arbitrage Debug ===")
    print(f"Found {len(cycles)} arbitrage cycle(s). Best: +{best_gain:.6f}% (×{best_mult:.9f})")

    # Detailed list
    for i, (cyc, prof) in enumerate(cycles, 1):
        names = _format_cycle(labels, cyc)
        print(f"[{i:02d}] {names} | profit = {(prof - 1.0) * 100:.6f}% (multiplier {prof:.9f})")
    print("=======================")


# =========================
# Internals
# =========================

def _format_cycle(labels: List[str], cyc: List[int]) -> str:
    """Helper to format a cycle as label1 -> label2 -> ... -> label1."""
    return " -> ".join(labels[u] for u in cyc) + f" -> {labels[cyc[0]]}"

def _cycle_profit(R: List[List[float]], cyc: List[int]) -> float:
    """Multiply true rates along a simple cycle (u0->u1->...->uk->u0)."""
    prod = 1.0
    m = len(cyc)
    for i in range(m):
        u = cyc[i]
        v = cyc[(i + 1) % m]
        prod *= R[u][v]
    return prod

def _canonical_cycle(nodes: List[int]) -> Tuple[int, ...]:
    """
    Canonicalize a simple cycle (without repeated end) to dedupe rotations and direction.
    - Rotate so the smallest node id is first
    - Compare forward vs reversed order; choose lexicographically smaller
    """
    if not nodes:
        return tuple()
    m = len(nodes)

    # All rotations starting at minimal element (forward)
    mn = min(nodes)
    starts = [i for i, v in enumerate(nodes) if v == mn]
    candidates = [nodes[i:] + nodes[:i] for i in starts]

    # All rotations starting at minimal element (reversed)
    rev = list(reversed(nodes))
    mn_r = min(rev)
    starts_r = [i for i, v in enumerate(rev) if v == mn_r]
    candidates.extend(rev[i:] + rev[:i] for i in starts_r)

    return tuple(min(candidates))  # lexicographically smallest

def _all_arbitrage_opportunities(
    R: List[List[float]],
    *,
    profit_tol: float = 1e-12,
    max_len: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[Tuple[List[int], float]]:
    """
    Enumerate all simple arbitrage cycles (profit > 1 + profit_tol) via DFS with de-duplication.

    Returns
    -------
    List[(cycle_nodes, profit_multiplier)]
      - cycle_nodes is [u0,u1,...,uk] meaning edges u0->u1->...->uk->u0
    """
    n = len(R)
    if n == 0:
        return []

    if max_len is None:
        max_len = n  # simple cycles cannot exceed n distinct vertices

    seen: Set[Tuple[int, ...]] = set()
    results: List[Tuple[List[int], float]] = []

    def dfs(start: int, u: int, path: List[int], visited: Set[int], acc_prod: float):
        nonlocal results
        if limit is not None and len(results) >= limit:
            return

        for v in range(n):
            rate = R[u][v]
            if rate <= 0.0:
                continue
            if v == start:
                # close a cycle; need at least 2 edges (len(path) >= 2)
                if len(path) >= 2:
                    profit = acc_prod * rate
                    if profit > 1.0 + abs(profit_tol):
                        cyc_nodes = path[:]  # [start,...,u]
                        cano = _canonical_cycle(cyc_nodes)
                        if cano not in seen:
                            seen.add(cano)
                            results.append((cyc_nodes, profit))
                continue

            if v in visited:
                continue  # simple cycles only (no repeated interior nodes)

            if len(path) + 1 > max_len:
                continue

            visited.add(v)
            path.append(v)
            dfs(start, v, path, visited, acc_prod * rate)
            path.pop()
            visited.remove(v)

    # Launch a DFS from each node
    for s in range(n):
        visited = {s}
        dfs(s, s, [s], visited, 1.0)
        if limit is not None and len(results) >= limit:
            break

    return results
