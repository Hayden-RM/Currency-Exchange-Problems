# src/arbitrage.py
from typing import List, Optional, Tuple
from .transform import rates_to_neglog_weights
from .bellman_ford import bellman_ford_single_source

def _cycle_profit(R: List[List[float]], cyc: List[int]) -> float:
    """Multiply edge rates along a simple cycle cyc (in forward order)."""
    prod = 1.0
    for i in range(len(cyc)):
        u = cyc[i]
        v = cyc[(i + 1) % len(cyc)]
        prod *= R[u][v]
    return prod

def detect_arbitrage(
    R: List[List[float]],
    eps: float = 1e-12,
    tol: float = 1e-10,         # detection tolerance in -log space
    profit_tol: float = 1e-3    # 0.10% economic threshold; suppress rounding artifacts
) -> Tuple[bool, Optional[List[int]], Optional[float]]:
    """
    Detects an arbitrage opportunity in the exchange rate table R.
    - Transforms rates to -log weights
    - Runs Bellman-Ford from each node to find a negative cycle
    - Among. cyccles found, returns the most profitable (by true product on R),
    but only if profit > 1 = + profit_tol.
    
    Returns:
    -(exists, cycle_nodes, profit_multiple)
    where cycle nodes = [u0,u1,...,uk] means edges u0->u1->...->uk->u0
    and profit_multiple = R[u0->u1] * R[u1->u2] * ... * R[uk->u0]
    If no arbitrage found, returns (False, None, None).
    """
    W = rates_to_neglog_weights(R, eps=eps)
    n = len(R)

    best_cycle: Optional[List[int]] = None
    best_profit = 1.0

    for s in range(n):
        dist, pred, cycle = bellman_ford_single_source(W, s, tol=tol)
        # ----- GUARD: skip if no cycle found from this source -----
        if not cycle:
            continue
        # If any reconstruction returned a closed list like [a,b,c,a], normalize to [a,b,c]
        if len(cycle) >= 2 and cycle[0] == cycle[-1]:
            cycle = cycle[:-1]
        if len(cycle) < 2:
            continue

        prof = _cycle_profit(R, cycle)
        # Gate by economic threshold to avoid +0.00% / +0.01% false positives
        if prof > 1.0 + abs(profit_tol) and prof > best_profit:
            best_profit = prof
            best_cycle = cycle

    if not best_cycle:
        return False, None, None
    return True, best_cycle, best_profit
