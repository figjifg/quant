"""Unit tests for src/utils/ohlcv_quarantine.py — guard module."""
from __future__ import annotations

import pandas as pd
import pytest

from src.utils.ohlcv_quarantine import (
    OhlcvQuarantineError,
    apply_ohlcv_quarantine,
    assert_no_invalid_ohlcv,
    clear_guard_ack_log,
    get_guard_ack_log,
    invalid_ohlcv_mask,
    require_guarded_field_use,
    ANNOTATION_VALID_MASK_COL,
    ANNOTATION_REASON_COL,
    ANNOTATION_RUN_COL,
    S1,
    S2,
    S3,
    S4,
    S5,
    S6,
)


def _make_panel(rows):
    cols = ["날짜", "종목코드", "시가", "고가", "저가", "종가", "거래량",
            "거래대금추정", "거래대금추정여부"]
    return pd.DataFrame(rows, columns=cols)


def _clean_row():
    return ["2024-01-02", "000020", 100.0, 110.0, 95.0, 105.0, 1000.0, 105000.0, "True"]


def test_s1_vendor_non_trading_forward():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 0.0, 0.0, 0.0, 105.0, 0.0, 0.0, "True"],
    ]
    df = _make_panel(rows)
    mask = invalid_ohlcv_mask(df)
    assert not mask.iloc[0]
    assert mask.iloc[1]


def test_s2_nonpos_price():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", -1.0, 110.0, 95.0, 105.0, 1000.0, 105000.0, "True"],
        ["2024-01-04", "000020", 100.0, 0.0, 95.0, 105.0, 1000.0, 105000.0, "True"],
    ]
    df = _make_panel(rows)
    mask = invalid_ohlcv_mask(df)
    assert not mask.iloc[0]
    assert mask.iloc[1]
    assert mask.iloc[2]


def test_s3_ordering_violations():
    # high < low
    rows = [_clean_row(), ["2024-01-03", "000020", 100.0, 90.0, 95.0, 92.0, 1000.0, 92000.0, "True"]]
    df = _make_panel(rows)
    assert invalid_ohlcv_mask(df).iloc[1]
    # high < open
    df.loc[1, "고가"] = 99.0
    df.loc[1, "저가"] = 90.0
    df.loc[1, "시가"] = 100.0
    df.loc[1, "종가"] = 95.0
    assert invalid_ohlcv_mask(df).iloc[1]
    # low > open
    df.loc[1, "고가"] = 110.0
    df.loc[1, "저가"] = 105.0
    df.loc[1, "시가"] = 100.0
    df.loc[1, "종가"] = 108.0
    assert invalid_ohlcv_mask(df).iloc[1]


def test_s4_negative_volume_or_value():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 100.0, 110.0, 95.0, 105.0, -10.0, 105000.0, "True"],
        ["2024-01-04", "000020", 100.0, 110.0, 95.0, 105.0, 1000.0, -100.0, "True"],
    ]
    df = _make_panel(rows)
    mask = invalid_ohlcv_mask(df)
    assert not mask.iloc[0]
    assert mask.iloc[1]
    assert mask.iloc[2]


def test_s5_tv_estimated_mismatch():
    # clean: close*volume = 100*1000 = 100000 ≠ 999999 → mismatch when flag=True
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 100.0, 110.0, 95.0, 100.0, 1000.0, 999999.0, "True"],
        # flag=False → should NOT trigger S5
        ["2024-01-04", "000020", 100.0, 110.0, 95.0, 100.0, 1000.0, 999999.0, "False"],
    ]
    df = _make_panel(rows)
    mask = invalid_ohlcv_mask(df)
    assert not mask.iloc[0]
    assert mask.iloc[1]  # S5 hit
    assert not mask.iloc[2]  # flag False → S5 skipped, still valid


def test_s6_adjusted_missing():
    rows = [
        ["2024-01-02", "000020", 100.0, 110.0, 95.0, 105.0, 1000.0, 105000.0, "True"],
    ]
    df = _make_panel(rows)
    # require_adjusted=True but adjusted columns absent → S6 fires for all rows
    mask = invalid_ohlcv_mask(df, require_adjusted=True)
    assert bool(mask.iloc[0])
    # With adjusted columns present and non-null → S6 passes
    df2 = df.copy()
    df2["adj_open"] = 100.0
    df2["adj_high"] = 110.0
    df2["adj_low"] = 95.0
    df2["adj_close"] = 105.0
    mask2 = invalid_ohlcv_mask(df2, require_adjusted=True)
    assert not bool(mask2.iloc[0])


def test_fail_closed_on_missing_price_cols():
    df = pd.DataFrame({"foo": [1.0], "bar": [2.0]})
    with pytest.raises(OhlcvQuarantineError):
        invalid_ohlcv_mask(df)


def test_fail_closed_on_explicit_missing_col():
    rows = [_clean_row()]
    df = _make_panel(rows)
    with pytest.raises(OhlcvQuarantineError):
        invalid_ohlcv_mask(df, price_cols=["시가", "고가", "저가", "doesnotexist"])


def test_apply_filter_drops_invalid_rows():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 0.0, 0.0, 0.0, 105.0, 0.0, 0.0, "True"],
        _clean_row(),
    ]
    df = _make_panel(rows)
    out = apply_ohlcv_quarantine(df, mode="filter")
    assert len(out) == 2
    assert (out["시가"] > 0).all()


def test_apply_mask_preserves_rowcount_nan_invalid():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 0.0, 0.0, 0.0, 105.0, 0.0, 0.0, "True"],
    ]
    df = _make_panel(rows)
    out = apply_ohlcv_quarantine(df, mode="mask")
    assert len(out) == 2
    # Invalid row has NaN'd prices
    assert pd.isna(out.iloc[1]["시가"])
    assert pd.isna(out.iloc[1]["고가"])
    assert pd.isna(out.iloc[1]["저가"])
    assert pd.isna(out.iloc[1]["종가"])
    # Valid row preserved
    assert out.iloc[0]["시가"] == 100.0


def test_apply_annotate_adds_three_columns():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 0.0, 0.0, 0.0, 105.0, 0.0, 0.0, "True"],
    ]
    df = _make_panel(rows)
    out = apply_ohlcv_quarantine(df, mode="annotate")
    for col in (ANNOTATION_VALID_MASK_COL, ANNOTATION_REASON_COL, ANNOTATION_RUN_COL):
        assert col in out.columns
    assert bool(out.iloc[0][ANNOTATION_VALID_MASK_COL])
    assert not bool(out.iloc[1][ANNOTATION_VALID_MASK_COL])
    assert "S1" in out.iloc[1][ANNOTATION_REASON_COL] or "S2" in out.iloc[1][ANNOTATION_REASON_COL]


def test_assert_passes_on_clean_rows():
    rows = [_clean_row()]
    df = _make_panel(rows)
    # Should not raise
    assert_no_invalid_ohlcv(df, context="test_clean")


def test_assert_raises_on_invalid_rows():
    rows = [
        _clean_row(),
        ["2024-01-03", "000020", 0.0, 0.0, 0.0, 105.0, 0.0, 0.0, "True"],
    ]
    df = _make_panel(rows)
    with pytest.raises(OhlcvQuarantineError) as exc:
        assert_no_invalid_ohlcv(df, context="test_invalid")
    assert "test_invalid" in str(exc.value)


def test_require_guarded_field_use_appends_log():
    clear_guard_ack_log()
    assert get_guard_ack_log() == []
    require_guarded_field_use("Change", "src/features/example.py:42")
    log = get_guard_ack_log()
    assert log == [("Change", "src/features/example.py:42")]
    require_guarded_field_use("기관순매수금액추정", "src/features/another.py:7")
    assert len(get_guard_ack_log()) == 2


def test_require_guarded_field_use_rejects_empty():
    with pytest.raises(TypeError):
        require_guarded_field_use("", "ctx")
    with pytest.raises(TypeError):
        require_guarded_field_use("Change", "")


def test_mode_invalid_raises_value_error():
    rows = [_clean_row()]
    df = _make_panel(rows)
    with pytest.raises(ValueError):
        apply_ohlcv_quarantine(df, mode="invalid_mode")
    with pytest.raises(ValueError):
        invalid_ohlcv_mask(df, mode="invalid_mode")


def test_non_dataframe_raises_type_error():
    with pytest.raises(TypeError):
        invalid_ohlcv_mask([1, 2, 3])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        apply_ohlcv_quarantine(None)  # type: ignore[arg-type]


def test_adjusted_only_panel_resolves_default_cols():
    df = pd.DataFrame({
        "adj_open": [100.0, 0.0],
        "adj_high": [110.0, 0.0],
        "adj_low": [95.0, 0.0],
        "adj_close": [105.0, 100.0],
        "adj_volume": [1000.0, 0.0],
    })
    mask = invalid_ohlcv_mask(df)
    assert not bool(mask.iloc[0])
    assert bool(mask.iloc[1])


def test_nan_price_fails_closed_via_s2():
    rows = [_clean_row()]
    df = _make_panel(rows)
    df.loc[0, "종가"] = float("nan")
    assert bool(invalid_ohlcv_mask(df).iloc[0])
