import math
from typing import List, Optional, Tuple
from .floyd_warshall import floyd_warshall, reconstruct_path
from .transform import _rates_to_neglog_weights

def best_conversion(R: List[List[float]], s: int, t: int, eps: float = 0.0) -> Optional[Tuple[List[int], float]]:
   
   if s == t:
      return [s], 1.0

   W = _rates_to_neglog_weights(R, eps)
   dist, nxt = floyd_warshall(W)
   path = reconstruct_path(nxt, s, t)

   if path is None:
      return None
   
   best_rate = math.exp(-dist[s][t])
   return path, best_rate


