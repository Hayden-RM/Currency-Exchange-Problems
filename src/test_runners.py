from src.execute_utils import run_single_test, run_live_demo

def run_given_test_cases():
    print(" ===================================")
    print(" ||    START OF GIVEN TEST CASES  ||")
    print(" ===================================\n")

    # B. Input handling
    # Case 1: Invalid currency count
    print("\n--- Input handling, Case 1: Invalid currency count ---")
    run_single_test("tests/tests_given/tc_input_handling_c1.txt")
    print("^ Expected output: Invalid Input. Currency count does not match the number of nodes provided")
    print("\n--- End of case. ----\n")

    # Case 2: Missing exchange rates
    print("\n--- Input handling, Case 2: Missing exchange rates ---")
    run_single_test("tests/tests_given/tc_input_handling_c2.txt")
    print("^ Expected output:Error: Incomplete row for currency A. Each row must have exactly 3 values.")
    print("\n--- End of case. ----\n")

    # Case 3: Negative exchange rate
    print("\n--- Input handling, Case 3: Negative exchange rate ---")
    run_single_test("tests/tests_given/tc_input_handling_c3.txt")
    print("^ Expected Output: Error: Invalid exchange rate detected. Rates must be positive numbers.")
    print("\n--- End of case. ----\n")

    # Case 4: Non-numeric entry
    print("\n--- Input handling, Case 4: Non-numeric entry ---")
    run_single_test("tests/tests_given/tc_input_handling_c4.txt")
    print("^ Expected output: Error: Invalid numeric value in exchange matrix (row 1, col 2).")
    print("\n--- End of case. ----\n")

    # B. No arbitrage (direct path)
    # Case 1: 3 currencies
    print("\n--- No arbitrage, Case 1: 3 currencies ---")
    run_single_test("tests/tests_given/tc_noarb_c1.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to C: 0.8550.\nBest path: A -> B -> C.")
    print("\n--- End of case. ----\n")

    # Case 2: 5 currencies, equal rates
    print("\n--- No arbitrage, Case 2: 5 currencies, equal rates ---")
    run_single_test("tests/tests_given/tc_noarb_c2.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to B: 1.0000.\nBest path: A -> B.")
    print("\n--- End of case. ----\n")

    # Case 3:  5 currencies (indirect optimal path)
    print("\n--- No arbitrage, Case 3: 5 currencies (indirect optimal path) ---")
    run_single_test("tests/tests_given/tc_noarb_c3.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to B: 0.9000.\nBest path: A -> D -> B.")
    print("\n--- End of case. ----\n")

    # C. Arbitrage exists
    # Case 1: 3 currencies
    print("\n--- Arbitrage exists, Case 1: 3 currencies ---")
    run_single_test("tests/tests_given/tc_arb_c1.txt")
    print("^ Expected Output:\nArbitrage detected!\nArbitrage cycle: A -> B -> C -> A.\nProfit: 6.04%.")
    print("\n--- End of case. ----\n")
    
    # Case 2: 5 currencies
    print("\n--- Arbitrage exists, Case 2: 5 currencies ---")
    run_single_test("tests/tests_given/tc_arb_c2.txt")
    print("^ Expected Output:\nArbitrage detected!\nArbitrage cycle: A -> D -> C -> A.\nProfit: 71.10%.")
    print("\n--- End of case. ----\n")

    print(" =================================")
    print(" ||    END OF GIVEN TEST CASES  ||")
    print(" =================================\n")
    
def run_extra_test_cases():

    print(" ===================================")
    print(" ||    START OF EXTRA TEST CASES  ||")
    print(" ===================================\n")

    # Abritrage exists
    run_single_test("tests/tests_extra/tc_arb_c1.txt")
    print("^ Expected Output:\nArbitrage detected!\nArbitrage cycle: A -> B -> C -> A.\nProfit: 5.30%.")
    print("\n--- End of case. ----\n")

    run_single_test("tests/tests_extra/tc_arb_c2.txt")
    print("^ Expected Output:\nArbitrage detected!\nArbitrage cycle: A -> D -> C -> A.\nProfit: 71.10%.")
    print("\n--- End of case. ----\n")

    run_single_test("tests/tests_extra/tc_arb_c3.txt")
    print("^ Expected Output:\nArbitrage detected!\nArbitrage cycle: AUD -> GBP -> AUD.\nProfit: 0.70%")
    print("\n--- End of case. ----\n")

    # No arbitrage
    run_single_test("tests/tests_extra/tc_noarb_c1.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to C: 1.5000.\nBest path: A -> C.")
    print("\n--- End of case. ----\n")

    run_single_test("tests/tests_extra/tc_noarb_c2.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to B: 1.0000.\nBest path: A -> B.")
    print("\n--- End of case. ----\n")

    run_single_test("tests/tests_extra/tc_noarb_c3.txt")
    print("^ Expected Output:\nNo arbitrage detected.\nBest conversion rate from A to B: 0.9000.\nBest path: A -> B.")
    print("\n--- End of case. ----\n")
    
    print(" =================================")
    print(" ||    END OF GIVEN TEST CASES  ||")
    print(" =================================\n")


def run_live_sample():

    print(" ===================================")
    print(" ||   LIVE API SAMPLE TEST CASE  ||")
    print(" ===================================\n")

    # to see fetched API data transformed to operable matrix, see tests_fetched_api/latest.txt
    currency_labels = ["DKK","EUR","JPY","NOK","AUD", "USD", "CAD"]
    run_live_demo(labels=currency_labels)

    currency_labels = ["EUR","AUD","JPY","USD","NZD"]
    run_live_demo(labels=currency_labels)

    currency_labels = ["HKD","EUR","GBP"]
    run_live_demo(labels=currency_labels)

    print("\n")
    print(" ====================================")
    print(" ||    END OF LIVE API TEST CASES  ||")
    print(" =================================\n")

