# src/execute_utils.py
"""Convenience execution helpers used by top-level scripts.

Provides small utilities to run all tests in a directory, run a single test,
and to run a live demo that fetches data from an exchange-rates provider.
"""

import os
from src.runner import run_case

# NEW: import the parser (to reuse labels/R) and the debug helper.
from src.io_parsing import read_matrix_file, ParseError
from src.dump_all_arbitrage import dump_all_arbitrage
from src.providers.exchangerates_api import ExchangeratesAPIClient as ExchangeRatesClient
from src.providers.normalize import matrix_from_latest

def run_all_tests(file_path: str):
    # Directory containing your test input files
    TEST_DIR = file_path

    print(f"\n=== Running all test cases in: {TEST_DIR} ===\n")

    # Loop through every .txt file in that folder
    for fname in sorted(os.listdir(TEST_DIR)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(TEST_DIR, fname)
        print(f"\n--- Running: {fname} ---")
        run_case(fpath)
        print("--- End of case ---\n")

    print("\n=== All test cases complete ===")


def run_single_test(file_path: str):
    print(f"\n=== Running single test case: {file_path} ===\n")
    run_case(file_path)
    print("\n=== Test case complete ===")

# CAUTION: This function is intended for debugging purposes only.
# Used to launch a single test with the debug dump, useful for debugging on low n cases.
# Uses brute-force enumeration to find and print ALL arbitrage cycles.
def run_single_with_dump(file_path: str):
    print(f"\n=== Running single test case with dump: {file_path} ===\n")
    run_case(file_path)

    # NEW: Try to parse and dump *all* arbitrage cycles (for debugging).
    #      - If parsing fails, ignore here; run_case already printed the parse error.
    try:
        labels, R = read_matrix_file(file_path)
        # One-line debug dump; prints ONLY if arbitrage cycles exist.
        dump_all_arbitrage(R, labels, profit_tol=1e-9)
    except ParseError:
        pass

    print("\n=== Test case complete ===")



def run_live_demo(labels: list[str]) -> None:
    """
    Fetch /latest from exchangeratesapi.io and print a quick arbitrage/best-path result.
    Requires EXCHANGERATES_API_KEY in env or passable via the client.
    """
    fx = ExchangeRatesClient()
    # Ensure provider returns all requested symbols—include the base itself too.
    symbols = list({*labels})
    latest = fx.latest(symbols=symbols)

    print("\n=== Live API snapshot ===")
    print(f"Provider base: {latest.get('base')}  date: {latest.get('date')}")
    R = matrix_from_latest(latest, labels)
    print(f"Built R matrix for labels: {', '.join(labels)}")

    # Write a tiny temp file-like run: use run_case-style printouts by composing an in-memory case
    # or simply run detect/best directly. For simplicity, reuse run_case by writing a temp file
    # is overkill—so just do a small summary here.
    from src.arbitrage import detect_arbitrage
    from src.best_rate import best_conversion

    exists, cyc, prof = detect_arbitrage(R, eps=1e-12, tol=1e-12)
    if exists and cyc:
        cyc_labels = [labels[i] for i in cyc] + [labels[cyc[0]]]
        profit_pct = (prof - 1.0) * 100 if prof else 0.0
        print("Arbitrage detected!")
        print(f"Arbitrage cycle: {' -> '.join(cyc_labels)}.")
        print(f"Profit: {profit_pct:.6f}%.")
    else:
        print("No arbitrage detected.")
        # Simple policy: if >=2 labels, show base->second
        s, t = 0, 1 if len(labels) >= 2 else 0
        rate, path = best_conversion(R, s, t, eps=1e-12)
        if rate and path:
            names = [labels[i] for i in path]
            print(f"Best conversion rate from {labels[s]} to {labels[t]}: {rate:.6f}.")
            print(f"Best path: {' -> '.join(names)}.")
        else:
            print(f"Best conversion rate from {labels[s]} to {labels[t]}: N/A")
