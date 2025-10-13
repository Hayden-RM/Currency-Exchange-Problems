# src/transform.py

import math
from typing import List, Dict

def rates_to_neglog_weights(R: List[List[float]], eps: float = 0.0) -> List[List[float]]:

    n = len(R)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            W[i][j] = -math.log(R[i][j] + eps)
    return W

def matrix_from_base_snapshot(base: str, rates: Dict[str, float], labels: List[str]) -> List[List[float]]:
    """
    Build an n×n matrix R where R[i][j] is the rate labels[i] -> labels[j],
    given a snapshot with a single base and a dict of base->quote rates.

    - base: the base currency of the snapshot (e.g., "USD")
    - rates: mapping QUOTE -> rate(base->QUOTE)
    - labels: ordered currency list you want in the matrix
    """
    base = base.upper()
    labels = [s.upper() for s in labels]
    n = len(labels)

    if base not in labels:
        raise ValueError(f"Base {base} must be included in labels")

    # base->X map (include base->base = 1.0)
    base_to = {base: 1.0, **{k.upper(): float(v) for k, v in rates.items()}}

    R = [[0.0] * n for _ in range(n)]
    for i in range(n):
        R[i][i] = 1.0
    for i, src in enumerate(labels):
        for j, dst in enumerate(labels):
            if i == j:
                continue
            # src->dst = (base->dst) / (base->src), when both exist
            b_src = base_to.get(src)
            b_dst = base_to.get(dst)
            if b_src and b_dst:
                R[i][j] = b_dst / b_src
    return R
