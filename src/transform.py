import math
from typing import List

def rates_to_neglog_weights(R: List[List[float]], eps: float = 0.0) -> List[List[float]]:


    n = len(R)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            W[i][j] = -math.log(R[i][j] + eps)
    return W


