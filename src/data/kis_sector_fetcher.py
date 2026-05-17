"""KIS sector snapshot client.

This module intentionally avoids logging credentials. Callers pass the app key
and secret in memory, then persist only API response fields and fetch status.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TOKEN_URL = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
SEARCH_STOCK_INFO_URL = (
    "https://openapi.koreainvestment.com:9443"
    "/uapi/domestic-stock/v1/quotations/search-stock-info"
)

SECTOR_FIELD_NAMES = [
    "pdno",
    "prdt_name",
    "mket_id_cd",
    "scty_grp_id_cd",
    "idx_bztp_lcls_cd",
    "idx_bztp_lcls_cd_name",
    "idx_bztp_mcls_cd",
    "idx_bztp_mcls_cd_name",
    "idx_bztp_scls_cd",
    "idx_bztp_scls_cd_name",
    "std_idst_clsf_cd",
    "std_idst_clsf_cd_name",
]

LISTING_FIELD_PREFIXES = ("lstg_", "dlst_", "prdt_clsf_", "prdt_stat_")


class KISAPIError(RuntimeError):
    """Raised when a KIS API request fails after retry handling."""

    def __init__(self, message: str, http_status_code: int | None = None) -> None:
        super().__init__(message)
        self.http_status_code = http_status_code


@dataclass(frozen=True)
class FetchResult:
    ticker: str
    output: dict[str, Any]
    fetch_status: str
    http_status_code: int | None
    error_message: str = ""


class KISSectorClient:
    """Small urllib-based client for KIS CTPF1002R stock info."""

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._app_key = app_key
        self._app_secret = app_secret
        self._opener = opener
        self._sleep = sleep
        self._access_token: str | None = None

    def issue_token(self, *, force_refresh: bool = False) -> str:
        """Issue or return the cached KIS access token."""
        if self._access_token and not force_refresh:
            return self._access_token

        payload = {
            "grant_type": "client_credentials",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            TOKEN_URL,
            data=data,
            headers={"content-type": "application/json"},
            method="POST",
        )
        body, _status = self._request_json(request)
        token = body.get("access_token")
        if not token:
            raise KISAPIError("KIS token response did not include access_token")
        self._access_token = str(token)
        return self._access_token

    def fetch_stock_info(
        self,
        ticker: str,
        *,
        max_attempts: int = 3,
        initial_backoff_seconds: float = 1.0,
    ) -> FetchResult:
        """Fetch sector/product metadata for one six-digit Korean ticker."""
        normalized = normalize_ticker(ticker)
        last_status: int | None = None
        last_error = ""

        for attempt in range(max_attempts):
            try:
                token = self.issue_token()
                output, status_code = self._fetch_stock_info_once(normalized, token)
                return FetchResult(
                    ticker=normalized,
                    output=output,
                    fetch_status="success",
                    http_status_code=status_code,
                )
            except KISAPIError as exc:
                last_status = exc.http_status_code
                last_error = str(exc)
                if last_status in {401, 403}:
                    self.issue_token(force_refresh=True)
                if attempt + 1 < max_attempts:
                    self._sleep(initial_backoff_seconds * (2**attempt))
            except (URLError, TimeoutError) as exc:
                last_error = str(exc)
                if attempt + 1 < max_attempts:
                    self._sleep(initial_backoff_seconds * (2**attempt))

        return FetchResult(
            ticker=normalized,
            output={},
            fetch_status="fail",
            http_status_code=last_status,
            error_message=last_error,
        )

    def _fetch_stock_info_once(
        self, ticker: str, access_token: str
    ) -> tuple[dict[str, Any], int]:
        params = urlencode({"PDNO": ticker, "PRDT_TYPE_CD": "300"})
        request = Request(
            f"{SEARCH_STOCK_INFO_URL}?{params}",
            headers={
                "authorization": f"Bearer {access_token}",
                "appkey": self._app_key,
                "appsecret": self._app_secret,
                "tr_id": "CTPF1002R",
                "custtype": "P",
            },
            method="GET",
        )
        body, status_code = self._request_json(request)
        output = body.get("output", {})
        if isinstance(output, list):
            output = output[0] if output else {}
        if not isinstance(output, dict):
            raise KISAPIError("KIS stock info response output was not an object", status_code)
        return output, status_code

    def _request_json(self, request: Request) -> tuple[dict[str, Any], int]:
        try:
            with self._opener(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                status_code = int(getattr(response, "status", 200))
        except HTTPError as exc:
            status_code = int(exc.code)
            message = exc.read().decode("utf-8", errors="replace")
            raise KISAPIError(f"KIS HTTP {status_code}: {message}", status_code) from exc

        try:
            body = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise KISAPIError("KIS response was not valid JSON", status_code) from exc
        if not isinstance(body, dict):
            raise KISAPIError("KIS response JSON root was not an object", status_code)
        return body, status_code


def normalize_ticker(value: str | int) -> str:
    """Return a KRX-style six-digit ticker code."""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        raise ValueError(f"ticker has no digits: {value!r}")
    return digits.zfill(6)


def parse_env_file(path: str) -> dict[str, str]:
    """Parse simple KEY=VALUE lines from an env file without expanding values."""
    values: dict[str, str] = {}
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            values[key.strip()] = value
    return values


def listing_related_fields(output: dict[str, Any]) -> dict[str, Any]:
    """Return listing/delisting/product status fields requested for the snapshot."""
    return {
        key: value
        for key, value in output.items()
        if any(key.startswith(prefix) for prefix in LISTING_FIELD_PREFIXES)
    }
