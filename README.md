# Currency-Exchange-Problems

A small toolkit for detecting currency exchange arbitrage and computing optimal conversion paths between currencies. The project includes:

- Implementations of Bellman–Ford negative-cycle detection and helper algorithms for best-conversion paths.
- Utilities to parse plain-text currency matrix test cases and run them in batch.
- A provider adapter for exchangeratesapi.io with a convenience to write the latest matrix snapshot to disk.
- Diagnostic helpers (brute-force enumerator, debug dump) for validating correctness on small inputs.

This README explains how to run the code, the input file format, how to add tests, and common developer tasks.

## Quick start

Requirements

- Python 3.9+ (the codebase targets 3.9 compatibility)
- Optional: `requests` and `python-dotenv` if you want to use live API features

Install dependencies (recommended in a virtualenv):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run all packaged test cases:

```bash
python3 main.py
```

Enable debug logging (writes to `debug.log` and appends instead of truncating):

```bash
A1_DEBUG=1 python3 main.py
```

## Input file format (tests)

Test files are plain text. Example structure:

```
3, USD, EUR, JPY
1.0 0.9 110.0
1.1 1.0 120.0
0.0091 0.0083 1.0
```

- First line: `n, LABEL1, LABEL2, ..., LABELn` where `n` is the number of currencies.
- Next `n` lines: each contains `n` whitespace-separated positive floats describing the exchange-rate matrix R where `R[i][j]` is the rate from currency i to j. Diagonal elements are typically `1.0`.

Files in `tests_given/` follow this format and are used by `run_all_tests`.

## What the program prints

- For each test case, the runner prints either:

  - "Arbitrage detected!" with a reported simple cycle and profit percentage, or
  - "No arbitrage detected." followed by the best conversion rate and path for a policy-selected pair of currencies.

- Diagnostic brute-force dumps (for small `n`) can be produced using `run_single_with_dump` or `dump_all_arbitrage`.

## Live API support

If you want to run against exchangeratesapi.io (apilayer):

1. Set environment variable `EXCHANGERATES_API_KEY` (or put it in `.env`):

```bash
export EXCHANGERATES_API_KEY="your_api_key_here"
```

2. Use `run_live_demo` from `src.execute_utils` or run `client.py` which demonstrates fetching latest rates and summarizing arbitrage/best-path information.

Every call to the existing `latest()` API adapter writes a snapshot file to `latest_data_from_api/latest.txt` (overwrites on each call). The format mirrors test inputs (header `n, LABELS...` followed by matrix rows), so you can re-run the runner against that file.

## Developer notes

- Main algorithmic modules:

  - `src/arbitrage.py` — orchestrates detection of arbitrage cycles (Bellman–Ford based)
  - `src/bellman_ford.py` — single-source Bellman–Ford implementation with negative-cycle reconstruction
  - `src/best_rate.py` — best conversion (s->t) using shortest-path on -log rates
  - `src/transform.py` — utilities to convert between R and weight matrices (neg-log transform)

- Test harness and utilities:

  - `src/runner.py` — reads test files and prints results. Uses logging (appends to `debug.log`) and preserves console output.
  - `src/dump_all_arbitrage.py` — brute-force enumerator used for validation on small inputs.
  - `scripts/bruteforce_checker.py` — helper script that computes brute-force expected outputs and compares them to program output (useful for regression testing).

- Compatibility and naming notes:
  - The API client class is available as both `ExchangeRatesClient` and `ExchangeratesAPIClient` for compatibility with older imports.
  - `latest_data_from_api/latest.txt` is overwritten on each `latest()` call. If you prefer timestamped snapshots, modify the provider adapter accordingly.

## Troubleshooting

To see debug logging run "A1_DEBUG=1 python3 main.py" in terminal.

- `debug.log` empty: the runner config uses Python's `logging` module. Ensure `A1_DEBUG=1` is set to enable DEBUG logging and that code emits `logging.info/debug` messages (some messages are printed with `print()`). The file is opened in append mode so logs are preserved between runs.

- API errors: the API adapter surfaces provider error messages when the HTTP response includes JSON error details. Ensure your API key is correct and your subscription supports the requested endpoints.