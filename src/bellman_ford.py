from typing import List, Optional, Tuple
import math

INF = 1e300

def bellman_ford_single_source(W: List[List[float]], s: int, tol: float = 1e-12) -> Tuple[List[float], List[Optional[int]], Optional[List[int]]]:
    """
    Run Bellman-Ford from source s on weight matrix W.

    Returns (dist, pred, cycle) where:
      - dist: distances from s
      - pred: predecessor list (index or None)
      - cycle: a simple negative cycle as a list of node indices (in forward order),
               or None if no negative cycle reachable from s.
    """
    n = len(W)
    dist: List[float] = [INF] * n
    pred: List[Optional[int]] = [None] * n
    dist[s] = 0.0

    # Relax edges up to n-1 times
    for _ in range(n - 1):
        updated = False
        for u in range(n):
            du = dist[u]
            if du >= INF:
                continue
            for v in range(n):
                if v == u:
                    # skip self-edge relaxations to avoid self-predecessors
                    continue
                w = W[u][v]
                alt = du + w
                if alt < dist[v] - abs(tol):
                    dist[v] = alt
                    pred[v] = u
                    updated = True
        if not updated:
            break

    # One more pass to detect negative cycle
    for u in range(n):
        du = dist[u]
        if du >= INF:
            continue
        for v in range(n):
            if v == u:
                continue
            w = W[u][v]
            if du + w < dist[v] - abs(tol):
                # Negative cycle reachable; reconstruct it
                # Start from v and follow predecessors n times to ensure inside cycle
                x = v
                for _ in range(n):
                    if pred[x] is None:
                        break
                    x = pred[x]
                # Now collect cycle nodes
                cycle = []
                cur = x
                while True:
                    cycle.append(cur)
                    cur = pred[cur] if pred[cur] is not None else None
                    if cur is None or cur in cycle:
                        break
                if cur is None:
                    # shouldn't happen for a true negative cycle, continue searching
                    continue
                # cycle now ends at a repeated node; extract the simple cycle
                if cur in cycle:
                    idx = cycle.index(cur)
                    simple = cycle[idx:]
                    # reverse predecessor order to forward traversal
                    simple_forward = list(reversed(simple))
                    return dist, pred, simple_forward
    return dist, pred, None
