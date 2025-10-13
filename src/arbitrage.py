"""arbitrage.py

Utilities for detecting arbitrage cycles in an exchange-rate matrix R.

This module exposes a single high-level function `detect_arbitrage(R, ...)`
which returns whether an arbitrage exists and the best simple cycle found.
"""

import math
from typing import List, Optional, Tuple
from .bellman_ford import bellman_ford_single_source
from .transform import rates_to_neglog_weights


def _cycle_profit(R: List[List[float]], cyc: List[int]) -> float:
    """Return the multiplicative profit for a simple cycle.

    R: exchange-rate matrix
    cyc: nodes in cycle order [u0,u1,...,uk] representing edges u0->u1->...->uk->u0
    """
    prod = 1.0
    m = len(cyc)
    for k in range(m):
        u = cyc[k]
        v = cyc[(k + 1) % m]
        prod *= R[u][v]
    return prod

def _best_simple_cycle_from_closed_walk(walk: List[int], R: List[List[float]], profit_tol: float = 1e-12
                                        ) -> Optional[Tuple[List[int], float]]:
    """
    Given a closed walk (not necessarily explicitly closed), examine ALL repeated
    vertices v_i == v_j (i < j) and treat walk[i:j] as a candidate simple cycle.
    Return the cycle with the highest true profit and its profit.
    """
    if not walk:
        return None
    # ensure explicit closure when scanning (makes last candidate well-formed)
    closed = list(walk)
    if closed[0] != closed[-1]:
        closed.append(closed[0])

    positions = {}
    best_cyc: Optional[List[int]] = None
    best_profit = 1.0

    for idx, v in enumerate(closed):
        positions.setdefault(v, []).append(idx)

    # For every repeated vertex, try all (i,j) pairs to extract candidate simple cycles
    for _, idxs in positions.items():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs) - 1):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                cyc = closed[i:j]
                if len(cyc) < 2:
                    continue
                profit = _cycle_profit(R, cyc)
                if profit > 1.0 + abs(profit_tol) and profit > best_profit:
                    best_profit = profit
                    best_cyc = cyc

    if best_cyc is None:
        return None
    return best_cyc, best_profit

def detect_arbitrage(R: List[List[float]], eps: float = 1e-12, tol: float = 1e-10
                     ) -> Tuple[bool, Optional[List[int]], Optional[float]]:
    """
    Detect arbitrage by running Bellman-Ford from every source and collecting
    any negative cycles reachable from that source. Return the most profitable
    simple cycle found (by true product in R).
    """
    W = rates_to_neglog_weights(R, eps=eps)
    n = len(R)

    best_cycle: Optional[List[int]] = None
    best_profit = 1.0

    # Run BF from each source to detect reachable negative cycles
    for s in range(n):
        dist, pred, cycle = bellman_ford_single_source(W, s, tol=tol)
        if cycle is None:
            continue
        # cycle is returned as list of nodes in forward order via pred-unwind
        # convert to simple cycle (in case pred-based reconstruction produced order quirks)
        # Compute profit directly and update best
        profit = _cycle_profit(R, cycle)
        if profit > best_profit:
            best_profit = profit
            best_cycle = cycle

    if not best_cycle:
        return False, None, None
    return True, best_cycle, best_profit
