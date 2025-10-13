# src/providers/normalize.py
from typing import List
from src.transform import matrix_from_base_snapshot

def matrix_from_latest(latest: dict, labels: List[str]) -> List[List[float]]:
    """
    Adapter for exchangeratesapi.io's /latest response shape.
    """
    base = latest["base"]
    rates = latest["rates"]
    return matrix_from_base_snapshot(base, rates, labels)
