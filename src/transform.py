"""transform.py

Small helpers that transform exchange-rate matrices into graph weights and
back. The canonical transform used by the algorithms in this repository is
`W[i][j] = -log(R[i][j])` which converts multiplicative rates to additive
weights so shortest-path algorithms can be used.
"""

import math
from typing import List, Dict


def rates_to_neglog_weights(R: List[List[float]], eps: float = 0.0) -> List[List[float]]:
    """Convert an n×n rate matrix R into -log weights matrix W.

    eps: epsilon guard for nonpositive entries (if present).
    """
    n = len(R)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                W[i][j] = 0.0
            else:
                r = R[i][j]
                W[i][j] = -math.log(r if r > 0.0 else max(r, eps))
    return W


def matrix_from_base_snapshot(base: str, rates: Dict[str, float], labels: List[str]) -> List[List[float]]:
    """Build an n×n rate matrix R from a single-base snapshot.

    Useful adapter for API responses that report rates relative to a single
    base currency.
    """
    base = base.upper()
    labels = [s.upper() for s in labels]
    n = len(labels)

    if base not in labels:
        raise ValueError(f"Base {base} must be included in labels")

    base_to = {base: 1.0, **{k.upper(): float(v) for k, v in rates.items()}}

    R = [[0.0] * n for _ in range(n)]
    for i in range(n):
        R[i][i] = 1.0
    for i, src in enumerate(labels):
        for j, dst in enumerate(labels):
            if i == j:
                continue
            b_src = base_to.get(src)
            b_dst = base_to.get(dst)
            if b_src and b_dst:
                R[i][j] = b_dst / b_src
    return R
