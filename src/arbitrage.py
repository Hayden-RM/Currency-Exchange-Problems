import math
from typing import List, Optional, Tuple
from .floyd_warshall import floyd_warshall, any_negative_cycle, reconstruct_cycle_from_fw  
from .transform import rates_to_neglog_weights

def cycle_profit(R: List[List[float]], cyc: List[int]) -> float:

    n = len(cyc)
    prod = 1.0
    for i in range(n):
        u = cyc[i]
        v = cyc[(i + 1) % n]
        prod *= R[u][v]

    return prod

def detect_arbitrage(R: List[List[float]], eps: float = 1e-12, tol: float = 1e-12) -> Optional[Tuple[List[int], float]]:

    W = _rates_to_neglog_weights(R, eps)
    dist, nxt = floyd_warshall(W)
    s = any_negative_cycle(dist, tol=tol)
    if s is None:
        return None

    cyc = reconstruct_cycle_from_fw(nxt, s)
    if not cyc or len(cyc) < 2:
        cycc = [i]

    

    profit = cycle_profit(R, cyc)
    return True, cyc, profit


