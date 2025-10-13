# main.py
from src.logging_conf import setup_logging
from src.execute_utils import * 

def main() -> None:
    # Set up logging first. File goes to logs/debug.log
    # Tip: set A1_DEBUG=1 to get DEBUG logs; otherwise INFO.
    setup_logging(logfile="logs/debug.log")

    # Run the given test cases
    run_all_tests("tests")

    # if necessary, you can run a single test like this:
    run_single_test("tests/tc_arb_c1.txt")

    # run benchamrks (used in empirical performance analysis)
    run_all_tests("benchmarks")

    # Run live API demo with these labels
    currency_labels = ["DKK","EUR","JPY","NOK","AUD"]
    run_live_demo(labels=currency_labels)

if __name__ == "__main__":
    
    main()
