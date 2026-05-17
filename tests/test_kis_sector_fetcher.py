from __future__ import annotations

import io
import json
from urllib.error import HTTPError

from src.data.kis_sector_fetcher import KISSectorClient, listing_related_fields, normalize_ticker


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_normalize_ticker_zero_pads_numeric_codes():
    assert normalize_ticker(20) == "000020"
    assert normalize_ticker("005930") == "005930"
    assert normalize_ticker("1234.0") == "001234"


def test_fetch_stock_info_uses_cached_token_and_extracts_output():
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        if "oauth2/tokenP" in request.full_url:
            return FakeResponse({"access_token": "token-1", "expires_in": 21600})
        return FakeResponse(
            {
                "output": {
                    "pdno": "005930",
                    "prdt_name": "삼성전자",
                    "idx_bztp_mcls_cd_name": "전기전자",
                    "lstg_stqt": "5969782550",
                }
            }
        )

    client = KISSectorClient("app-key", "app-secret", opener=opener, sleep=lambda _: None)

    first = client.fetch_stock_info("5930")
    second = client.fetch_stock_info("005930")

    assert first.fetch_status == "success"
    assert first.output["idx_bztp_mcls_cd_name"] == "전기전자"
    assert second.fetch_status == "success"
    assert sum("oauth2/tokenP" in url for url in calls) == 1
    assert sum("search-stock-info" in url for url in calls) == 2


def test_fetch_stock_info_refreshes_token_after_unauthorized_response():
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        if "oauth2/tokenP" in request.full_url:
            return FakeResponse({"access_token": f"token-{len(calls)}"})
        if sum("search-stock-info" in url for url in calls) == 1:
            raise HTTPError(
                request.full_url,
                401,
                "Unauthorized",
                hdrs=None,
                fp=io.BytesIO(b'{"msg1":"expired"}'),
            )
        return FakeResponse({"output": {"pdno": "005930", "prdt_name": "삼성전자"}})

    client = KISSectorClient("app-key", "app-secret", opener=opener, sleep=lambda _: None)
    result = client.fetch_stock_info("005930")

    assert result.fetch_status == "success"
    assert result.http_status_code == 200
    assert sum("oauth2/tokenP" in url for url in calls) == 2
    assert sum("search-stock-info" in url for url in calls) == 2


def test_listing_related_fields_keeps_requested_prefixes_only():
    output = {
        "pdno": "005930",
        "lstg_dt": "19750611",
        "dlst_dt": "",
        "prdt_clsf_cd": "01",
        "prdt_stat_cd": "01",
        "idx_bztp_mcls_cd_name": "전기전자",
    }

    assert listing_related_fields(output) == {
        "lstg_dt": "19750611",
        "dlst_dt": "",
        "prdt_clsf_cd": "01",
        "prdt_stat_cd": "01",
    }
