# main.py

from src.execute_utils import *
# ====================================
# TESTING / BENCHMARKS / LIVE API DATA
# ====================================

# TESTS
# ~~~~
# run_all_tests("tests") # -->RUN ALL TESTS from "tests" folder
# run_single_test("") # --> RUN A SINGLE TEST
# run_single_with_dump("") # --> Only run when n < ~5, used for debugging

# BENCHMARKS
# ~~~~~~~~~~
# benchmark testing 3 currency matrix, 6, 9, 12, ... up to 24 currencies
# assumption: ALL matrices are consistent (rate[i][j] = (J + 1) / (I + 1))

# run_all_tests("benchmarks") # --> Run all benchmarks from "benchmarks" folder

# LIVE API DATA
# ~~~~~~~~~~~~~~~
currency_labels = ["DKK","EUR","JPY","NOK","AUD"]
run_live_demo(labels=currency_labels) # --> Run live demo with these labels

