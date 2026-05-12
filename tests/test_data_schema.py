from __future__ import annotations

import pandas as pd
import pytest

from src.data.equity_panel import load_equity_panel


def _write_csv(path, rows: list[dict], include_krx_close: bool = True) -> None:
    columns = [
        "날짜",
        "종목코드",
        "시가",
        "종가",
        "거래대금추정",
        "외국인순매수금액추정",
        "기관순매수금액추정",
        "수급금액추정여부",
        "거래대금추정여부",
        "동적유니버스포함",
    ]
    if include_krx_close:
        columns.insert(4, "KRX종가")
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, encoding="utf-8-sig")


def _row(
    date: str = "2025-01-02",
    ticker: str = "005930",
    close: float = 101.0,
    krx_close: float | None = 101.0,
    flow_flag: bool | str = "False",
    traded_value_flag: bool | str = "False",
    universe_flag: bool | str = "True",
) -> dict:
    row = {
        "날짜": date,
        "종목코드": ticker,
        "시가": 100.0,
        "종가": close,
        "거래대금추정": 1_000_000_000.0,
        "외국인순매수금액추정": 10_000_000.0,
        "기관순매수금액추정": 20_000_000.0,
        "수급금액추정여부": flow_flag,
        "거래대금추정여부": traded_value_flag,
        "동적유니버스포함": universe_flag,
    }
    if krx_close is not None:
        row["KRX종가"] = krx_close
    return row


def test_load_equity_panel_normalizes_schema_and_sorts_rows(tmp_path) -> None:
    csv_path = tmp_path / "panel.csv"
    rows = [
        _row(date="2025-01-03", ticker="000020", flow_flag=True, universe_flag=False),
        _row(date="2025-01-02", ticker="000020", traded_value_flag=False),
        _row(date="2025-01-02", ticker="000010"),
    ]
    _write_csv(csv_path, rows)

    panel = load_equity_panel([csv_path])

    assert list(panel["종목코드"]) == ["000010", "000020", "000020"]
    assert list(panel["날짜"]) == [
        pd.Timestamp("2025-01-02"),
        pd.Timestamp("2025-01-02"),
        pd.Timestamp("2025-01-03"),
    ]
    assert panel["종목코드"].dtype == "string"
    assert panel["날짜"].dtype == "datetime64[ns]"
    assert panel["수급금액추정여부"].dtype == bool
    assert panel["거래대금추정여부"].dtype == bool
    assert panel["동적유니버스포함"].dtype == bool
    assert panel["krx_close_source"].dtype.name == "category"
    assert set(panel["krx_close_source"]) == {"native"}


def test_pre_nxt_csv_without_krx_close_uses_raw_close_fallback(tmp_path) -> None:
    csv_path = tmp_path / "pre_nxt.csv"
    _write_csv(csv_path, [_row(krx_close=None)], include_krx_close=False)

    panel = load_equity_panel([csv_path])

    assert panel.loc[0, "KRX종가"] == panel.loc[0, "종가"]
    assert panel.loc[0, "krx_close_source"] == "from_종가_fallback"


def test_post_nxt_csv_with_krx_close_uses_native_source(tmp_path) -> None:
    csv_path = tmp_path / "post_nxt.csv"
    _write_csv(csv_path, [_row(close=101.0, krx_close=101.0)])

    panel = load_equity_panel([csv_path])

    assert panel.loc[0, "KRX종가"] == 101.0
    assert panel.loc[0, "krx_close_source"] == "native"


def test_post_nxt_close_mismatch_raises(tmp_path) -> None:
    csv_path = tmp_path / "post_nxt_bad.csv"
    _write_csv(csv_path, [_row(close=101.0, krx_close=100.0)])

    with pytest.raises(ValueError, match="종가 != KRX종가"):
        load_equity_panel([csv_path])


def test_missing_required_column_raises(tmp_path) -> None:
    csv_path = tmp_path / "missing.csv"
    row = _row()
    row.pop("거래대금추정")
    pd.DataFrame([row]).to_csv(csv_path, index=False, encoding="utf-8-sig")

    with pytest.raises(ValueError, match="Missing required equity panel columns"):
        load_equity_panel([csv_path])


def test_invalid_bool_value_raises(tmp_path) -> None:
    csv_path = tmp_path / "bad_bool.csv"
    _write_csv(csv_path, [_row(flow_flag="yes")])

    with pytest.raises(ValueError, match="non-boolean value"):
        load_equity_panel([csv_path])


def test_numeric_nans_are_preserved(tmp_path) -> None:
    csv_path = tmp_path / "nan.csv"
    row = _row()
    row["거래대금추정"] = pd.NA
    _write_csv(csv_path, [row])

    panel = load_equity_panel([csv_path])

    assert pd.isna(panel.loc[0, "거래대금추정"])
