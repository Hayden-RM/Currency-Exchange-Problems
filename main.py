# main.py
from src.logging_conf import setup_logging
from src.execute_utils import * 
from src.test_runners import run_given_test_cases, run_extra_test_cases, run_live_sample

def main() -> None:
    # Set up logging first. File goes to logs/debug.log
    # Tip: set A1_DEBUG=1 to get DEBUG logs; otherwise INFO.
    setup_logging(logfile="logs/debug.log")

    # << TEST EXAMPLES >> 

    # --> Run the given test cases <--
    # run_all_tests("tests_given")

    # --> Run the extra test cases <-- 
    # run_all_tests("tests_extra")

    # --> if necessary, you can run a single test like this: <--
    # run_single_test("tests_given/tc_arb_c1.txt")

    # --> run benchamrks (used in empirical performance analysis) <--
    # run_all_tests("tests_benchmarks")

    # --> Run live API demo with the below labels <--
    # currency_labels = ["DKK","EUR","JPY","NOK","AUD"]
    # run_live_demo(labels=currency_labels)

    # The groups of test cases are encapsualed in functions in src/test_runners.py
    # Which are run in the lines below.
    
    # << END OF EXAMPLES >>

    # ==========
    # TEST CASES
    # ==========

    run_given_test_cases()
    run_extra_test_cases()
    run_live_sample()
   

if __name__ == "__main__":
    main()
