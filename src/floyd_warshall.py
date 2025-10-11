from typing import List, Optional, Tuple

INF = 1e300

def floyd_warshall(weights: List[List[float]]) -> Tuple[List[List[float]], List[List[Optional[int]]]]:
   
   n = len(weights)
   dist = [[weights[i][j] for j in range(n)] for i in range(n)]
   nxt: List[List[Optional[int]]] = [[None]*n for _ in range(n)]

   for i in range(n):
      for j in range(n):
         if i == j and dist[i][j] > 0.0:
            pass
         if dist[i][j] < INF:
            nxt[i][j] = j

   # Allow i==j zero distance if needed
   for i in range(n):
      if dist[i][i] > 0:
         dist[i][i] = 0.0
         nxt[i][i] = i

   for k in range(n):
      dk = dist[k]
      for i in range(n):
         dik = dist[i][k]
         if dik == INF:
            continue
         di = dist[i]
         ni = nxt[i]
         dkk = dk
         for j in range(n):
            alt = dik + dkk[j]
            if alt < di[j]:
               di[j] = alt
               ni[j] = ni[k]

   return dist, nxt



def reconstruct_path(nxt: List[List[Optional[int]]], s: int, t: int) -> Optional[List[int]]:
   
   if nxt[s][t] is None:
      return None
   path = [s]
   cur = s
   while cur != t:
      cur = nxt[cur][t]
      if cur is None:
         return None
      path.append(cur)
      if len(path) > len(nxt) + 5:
         return None
       
   return path


def any_negative_cycle(dist: List[List[float]], tol: float = 0.0) -> Optional[int]:
    
    n = len(dist)
    for i in range(n):
        if dist[i][i] < -abs(tol):
            return i
    return None

def reconstruct_cycle_from_fw(nxt: List[List[Optional[int]]], start: int) -> Optional[List[int]]:
   
   n = len(nxt)
   if nxt[start][start] is None:
      return None
   
   seen = {}
   cur = start
   cycle = []

   for _ in range(n * 2):
      if cur in seen:
         # Extract the cycle slice from first occurence
         idx = seen[cur]
         cyc = cycle[idx]

         return cyc
      
      seen[cur] = len(cycle)
      cycle.append(cur)
      cur = nxt[cur][start]
      if cur is None:
         return None

   return None


