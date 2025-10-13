# src/io_parsing.py
"""Input parsing utilities for plain-text exchange-rate matrix files.

Exposes `read_matrix_file(path)` which returns (labels, R) where `labels` is
an ordered list of currency names and `R` is the n×n exchange-rate matrix.
"""

from typing import List, Tuple, Optional

class ParseError(Exception):
    """Custom exception for parsing errors."""
    pass

def _parse_header(line: str) -> Tuple[int, List[str]]:
    # Parse the header line to extract "3, A, B, C" with arbitrary spaces
    parts = [part.strip() for part in line.split(',')]
    if len(parts) < 2:
        raise ParseError("Header must contain at least a count and one label. (n, C1, C2, C3...)")
    
    try:
        n = int(parts[0])
    except ValueError:
        raise ParseError("The first part of the header must be an integer representing the count.")
    

    currencies = parts[1:]

    if n != len(currencies):
        raise ParseError("Invalid Input. Currency count does not match the number of nodes provided.")

    if len(set(currencies)) != len(currencies):
        raise ParseError("Currency labels must be unique.")

    return n, currencies

def _parse_row(line: str, expected_len: int, row_idx: int, label: Optional[str] = None) -> List[float]:

    toks = line.strip().split()
    if len(toks) != expected_len:
        # Prefer mentioning the currency label when available.
        if label:
            raise ParseError(f"Incomplete row for currency {label}. Each row must have exactly {expected_len} values.")
        else:
            raise ParseError(f"Incomplete row at row {row_idx+1}. Each row must have exactly {expected_len} values.")
    
    vals: List[float] = []
    for j, t in enumerate(toks):
        try:
            x = float(t)
        except ValueError:
            # Use 1-based indices in user-facing messages
            raise ParseError(f"Invalid numeric value in exchange matrix (row {row_idx+1}, col {j+1}).")
        if x <= 0.0:
            # Generic positive-rate message to match expected wording
            raise ParseError("Invalid exchange rate detected. Rates must be positive numbers.")
        vals.append(x)

    return vals

def read_matrix_file(path: str) -> Tuple[List[str], List[List[float]]]:
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln for ln in (l.strip() for l in f.readlines()) if ln]

    if not lines:
        raise ParseError("Input file is empty.")
    
    n, currencies = _parse_header(lines[0])
    if len(lines[1:]) < n:
        raise ParseError(f"Expected {n} rows of data, but found only {len(lines[1:])}.")
    
    matrix: List[List[float]] = []

    for i in range(n):
        row = _parse_row(lines[i + 1], n, i, label=currencies[i] if i < len(currencies) else None)
        matrix.append(row)

    return currencies, matrix


