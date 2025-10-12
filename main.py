# main.py
import os
from src.runner import run_case

# NEW: import the parser (to reuse labels/R) and the debug helper.
from src.io_parsing import read_matrix_file, ParseError
from src.dump_all_arbitrage import dump_all_arbitrage

def run_all_tests():
    # Directory containing your test input files
    TEST_DIR = "tests"

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

# ====================
# TESTING / BENCHMARKS
# ====================

# run_all_tests() # -->RUN ALL TESTS
# run_single_test("tests/mega_matrix.txt") # --> RUN A SINGLE TEST
# run_single_with_dump("tests/mega_matrix.txt") # --> Only run when n < ~5

# benchmark testing 3 currency matrix, 6, 9, 12, ... up to 24 currencies
# assumptions: ALL matrices are consistent (rate[i][j] = (J + 1) / (I + 1))

# does not detect no arbitrage (as expected) as these are not perfectly consistent
# once represented as 6 decimal floats then run through -log math. microscopic negative cycles are created.
run_single_test("benchmarks/matrix_3_curr.txt")
run_single_test("benchmarks/matrix_6_curr.txt")
run_single_test("benchmarks/matrix_9_curr.txt")
run_single_test("benchmarks/matrix_12_curr.txt")
run_single_test("benchmarks/matrix_15_curr.txt")
run_single_test("benchmarks/matrix_18_curr.txt")
run_single_test("benchmarks/matrix_21_curr.txt")
run_single_test("benchmarks/matrix_24_curr.txt")