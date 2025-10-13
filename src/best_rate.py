"""best_rate.py

Utilities to compute the best conversion rate between two currencies
using shortest-path algorithms in -log space.

Public function: best_conversion(R, s, t, ...)
"""

import math
from typing import List, Optional, Tuple


INF = 1e300


def _path_product(R: List[List[float]], path: List[int]) -> float:
    """Multiply real rates along a discrete path (product of R[u->v])."""
    prod = 1.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        prod *= R[u][v]
    return prod

def _rates_to_neglog_weights(R: List[List[float]], eps: float = 0.0) -> List[List[float]]:
    """
    Local, minimal transform to avoid surprises. Only uses eps to guard nonpositive entries.
    """
    n = len(R)
    W = [[INF]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                W[i][j] = 0.0
            else:
                r = R[i][j]
                if r > 0.0:
                    W[i][j] = -math.log(r)
                elif eps > 0.0:
                    W[i][j] = -math.log(eps)
                # else keep INF
    return W

def _bellman_ford_sssp(W: List[List[float]], s: int, tol: float = 1e-12
) -> Tuple[List[float], List[Optional[int]]]:
    """
    Standard single-source Bellman–Ford (dense graph).
    Returns (dist, pred). No negative-cycle gating here—runner calls us only when there’s no arbitrage.
    """
    n = len(W)
    dist = [INF] * n
    pred: List[Optional[int]] = [None] * n
    dist[s] = 0.0

    for _ in range(n - 1):
        updated = False
        for u in range(n):
            du = dist[u]
            if du >= INF:
                continue
            row = W[u]
            for v in range(n):
                if u == v:
                    continue
                w = row[v]
                if w >= INF:
                    continue
                cand = du + w
                if cand < dist[v] - abs(tol):
                    dist[v] = cand
                    pred[v] = u
                    updated = True
        if not updated:
            break

    return dist, pred

def _reconstruct_path_pred(pred: List[Optional[int]], s: int, t: int) -> Optional[List[int]]:
    if s == t:
        return [s]
    path_rev = []
    cur = t
    steps = 0
    limit = len(pred) + 5
    while cur is not None and steps <= limit:
        path_rev.append(cur)
        if cur == s:
            path_rev.reverse()
            return path_rev
        cur = pred[cur]
        steps += 1
    return None

def _reconstruct_path_consistent(
    dist: List[float], W: List[List[float]], s: int, t: int, tol: float = 1e-8
) -> Optional[List[int]]:
    """
    Greedy distance-consistent reconstruction:
    at node u, choose v minimizing residual = |(dist[u] + W[u][v]) - dist[v]|,
    and require residual <= tol. This is more tolerant than strict equality.
    """
    n = len(W)
    if s == t:
        return [s]
    if dist[s] >= INF or dist[t] >= INF:
        return None

    path = [s]
    u = s
    steps = 0
    max_steps = max(3, 3 * n)
    while u != t and steps < max_steps:
        best_v = None
        best_res = float('inf')
        row = W[u]
        for v in range(n):
            if v == u:
                continue
            w = row[v]
            if w >= INF or dist[v] >= INF:
                continue
            res = abs((dist[u] + w) - dist[v])
            if res < best_res:
                best_res = res
                best_v = v
        if best_v is None or best_res > abs(tol):
            return None
        path.append(best_v)
        u = best_v
        steps += 1

    return path if u == t else None

def best_conversion(
    R: List[List[float]],
    s: int,
    t: int,
    eps: float = 0.0,
    tol: float = 1e-12,
    *,
    exact_from_R: bool = False
) -> Tuple[Optional[float], Optional[List[int]]]:
    """
    Best conversion s->t using Bellman–Ford in −log space.
    IMPORTANT: We do NOT fail on negative-cycle hints here; runner already calls this
    only when arbitrage is not detected. We just return the best finite path if it exists.
    """
    n = len(R)
    if s < 0 or t < 0 or s >= n or t >= n:
        return None, None

    W = _rates_to_neglog_weights(R, eps=eps)
    dist, pred = _bellman_ford_sssp(W, s, tol=tol)

    if dist[t] >= INF:
        return None, None

    # Try predecessor chain first
    path = _reconstruct_path_pred(pred, s, t)

    # If pred chain is thin, try distance-consistent reconstruction
    if not path or (len(path) < 2 and s != t):
        path = _reconstruct_path_consistent(dist, W, s, t, tol=1e-8)

    if not path or (len(path) < 2 and s != t):
        return None, None

    if exact_from_R:
        return _path_product(R, path), path
    else:
        # dist[t] is total −log(rate)
        return math.exp(-dist[t]), path

