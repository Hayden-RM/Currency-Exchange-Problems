# src/providers/exchangerates_api.py
from __future__ import annotations
import os
import time
import datetime as dt
from typing import Dict, Iterable, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

load_dotenv()

class ExchangeRatesClient:
    """
    Minimal client for https://exchangeratesapi.io (apilayer).
    Supports: latest, historical (by date), timeseries.
    Adds: retries, timeouts, basic in-memory caching (TTL).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.exchangeratesapi.io/v1",
        timeout: float = 5.0,
        cache_ttl_sec: int = 10,
    ):
        self.api_key = api_key or os.getenv("EXCHANGERATES_API_KEY")
        if not self.api_key:
            raise RuntimeError("EXCHANGERATES_API_KEY missing. Set env or pass api_key=…")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache_ttl = cache_ttl_sec

        # requests session with robust retries
        self.sess = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}) 
        )
        self.sess.mount("https://", HTTPAdapter(max_retries=retries))
        self._cache: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], Tuple[float, dict]] = {}

    # -------- public API --------

    def latest(
        self,
        base: Optional[str] = None,
        symbols: Optional[Iterable[str]] = None,
    ) -> dict:
        """
        GET /latest
        Params:
          - base: e.g., "USD"
          - symbols: ["EUR","JPY"]
        """
        data = self._get(
            "latest",
            params=self._params(base=base, symbols=symbols),
        )

        # If the response looks like a /latest snapshot, attempt to normalize
        # and write the transformed R matrix to latest_data_from_api/latest.txt.
        # This is a best-effort side-effect and should not interfere with
        # normal operation if the response shape is unexpected.
        try:
            # import here to avoid top-level circular import
            from src.providers.normalize import matrix_from_latest
            from pathlib import Path

            if isinstance(data, dict) and "base" in data and "rates" in data:
                # The caller may have requested specific symbols, but matrix_from_latest
                # requires a labels list; use the 'rates' keys plus the base to build an
                # ordered labels list where base is first followed by sorted symbols.
                base_label = data.get("base")
                rates = data.get("rates", {})
                labels = [base_label] + [k for k in sorted(rates.keys()) if k != base_label]
                R = matrix_from_latest(data, labels)

                out_dir = Path.cwd() / "latest_data_from_api"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / "latest.txt"

                # Write a simple textual format: first line `n, L1, L2, ...`, then rows
                with out_path.open("w", encoding="utf-8") as fw:
                    fw.write(f"{len(labels)}, " + ", ".join(labels) + "\n")
                    for row in R:
                        fw.write(" ".join(f"{v:.12g}" for v in row) + "\n")
        except Exception:
            # Silently ignore any issues when attempting to write the matrix; we
            # don't want the side-effect to break normal API usage.
            pass

        return data

    def historical(
        self,
        date: dt.date | str,
        base: Optional[str] = None,
        symbols: Optional[Iterable[str]] = None,
    ) -> dict:
        """
        GET /{date} where date is "YYYY-MM-DD"
        """
        if isinstance(date, dt.date):
            date_str = date.isoformat()
        else:
            date_str = str(date)
        return self._get(
            date_str,
            params=self._params(base=base, symbols=symbols),
        )

    def timeseries(
        self,
        start_date: dt.date | str,
        end_date: dt.date | str,
        base: Optional[str] = None,
        symbols: Optional[Iterable[str]] = None,
    ) -> dict:
        """
        GET /timeseries
        """
        if isinstance(start_date, dt.date):
            start_date = start_date.isoformat()
        if isinstance(end_date, dt.date):
            end_date = end_date.isoformat()

        return self._get(
            "timeseries",
            params=self._params(base=base, symbols=symbols, extra={
                "start_date": str(start_date),
                "end_date": str(end_date),
            }),
        )

    def symbols(self) -> dict:
        """
        GET /symbols — list of supported currencies.
        """
        return self._get("symbols")

    # -------- internals --------

    def _params(
        self,
        *,
        base: Optional[str] = None,
        symbols: Optional[Iterable[str]] = None,
        extra: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        p = {"access_key": self.api_key}
        if base:
            p["base"] = base.upper()
        if symbols:
            p["symbols"] = ",".join(s.upper() for s in symbols)
        if extra:
            p.update(extra)
        return p

    def _cache_key(self, path: str, params: Dict[str, str]) -> Tuple[str, Tuple[Tuple[str, str], ...]]:
        # normalize key: path + sorted params
        return path, tuple(sorted(params.items()))

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        params = params or {"access_key": self.api_key}

        # check cache
        key = self._cache_key(path, params)
        now = time.time()
        hit = self._cache.get(key)
        if hit and (now - hit[0] <= self.cache_ttl):
            return hit[1]

        # call API
        r = self.sess.get(url, params=params, timeout=self.timeout)
        # raise for 4xx/5xx that weren't retried
        r.raise_for_status()
        data = r.json()

        # API-level error format:
        # {"success": false, "error": {"code": ..., "info": "..."}}
        if isinstance(data, dict) and data.get("success") is False:
            info = data.get("error", {}).get("info", "Unknown API error")
            code = data.get("error", {}).get("code", "unknown")
            raise RuntimeError(f"exchangeratesapi error [{code}]: {info}")

        # cache & return
        self._cache[key] = (now, data)
        return data


# Backwards-compatible export name: some modules expect the class to be named
# `ExchangeratesAPIClient`. Provide a simple alias so older imports continue to work.
ExchangeratesAPIClient = ExchangeRatesClient
