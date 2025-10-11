from typing import List, Tuple, Union

class ParseError(Exception):
    """Custom exception for parsing errors."""
    pass

def _parse_header(line: str) -> Tuple[int, list[str]]:
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
        raise ParseError(f"Count {n} does not match the number of currencies provided {len(currencies)}.")

    if len(set(currencies)) != len(currencies):
        raise ParseError("Currency labels must be unique.")

    return n, currencies

def _parse_row(line: str, expected_len: int, row_idx: int) -> List[float]:

    toks = line.strip().split()
    if len(toks) != expected_len:
        raise ParseError(f"Row {row_idx} length {len(toks)} does not match expected length {expected_len}.")
    
    vals: List[float] = []
    for j, t in enumerate(toks):
        try:
            x = float(t)
        except ValueError:
            raise ParseError(f"Row {row_idx}, column {j} value '{t}' is not a valid float.")
        vals.append(x)

    return vals

def read_matrix_file(path: str) -> Tuple[List[str], List[List[float]]]:
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln for ln in (l.strip() for l in f.readlines) if ln]

    if not lines:
        raise ParseError("Input file is empty.")
    
    n, currencies = _parse_header(lines[0])
    if len(lines[1:]) < n:
        raise ParseError(f"Expected {n} rows of data, but found only {len(lines[1:])}.")
    
    matrix: List[List[float]] = []

    for i in range(n):
        row = _parse_row(lines[i + 1], n, i)
        matrix.append(row)

    return currencies, matrix


