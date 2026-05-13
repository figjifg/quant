from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.features.flow_ratios import build_flow_ratios


def _panel() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=8, freq="B")
    rows = []
    for day_index, date in enumerate(dates, start=1):
        rows.append(
            {
                "날짜": date,
                "종목코드": "000010",
                "KRX종가": 100.0 + day_index,
                "거래대금추정": 1_000.0 + day_index,
                "시가총액추정": 100_000.0 + day_index * 1_000.0,
                "외국인순매수금액추정": 100.0 + day_index,
                "기관순매수금액추정": 50.0 + day_index,
            }
        )
    return pd.DataFrame(rows)


def _feature_row(features: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    rows = features.loc[(features["종목코드"] == "000010") & (features["날짜"] == date)]
    assert len(rows) == 1
    return rows.iloc[0]


def test_combined_flow_5_mcap_uses_five_day_net_buy_over_same_day_mcap() -> None:
    panel = _panel()
    signal_date = pd.Timestamp("2025-01-08")

    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    row = _feature_row(features, signal_date)
    window = panel.loc[panel["날짜"].between(pd.Timestamp("2025-01-02"), signal_date)]
    numerator = window["외국인순매수금액추정"].sum() + window["기관순매수금액추정"].sum()
    denominator = panel.loc[panel["날짜"].eq(signal_date), "시가총액추정"].iloc[0]

    assert row["combined_flow_5_mcap"] == numerator / denominator


def test_combined_flow_5_mcap_is_nan_when_market_cap_is_nan() -> None:
    panel = _panel()
    signal_date = pd.Timestamp("2025-01-08")
    panel.loc[panel["날짜"].eq(signal_date), "시가총액추정"] = pd.NA

    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    row = _feature_row(features, signal_date)

    assert pd.isna(row["combined_flow_5_mcap"])


def test_combined_flow_5_mcap_is_nan_when_market_cap_is_non_positive() -> None:
    panel = _panel()
    signal_date = pd.Timestamp("2025-01-08")
    panel.loc[panel["날짜"].eq(signal_date), "시가총액추정"] = 0.0

    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    row = _feature_row(features, signal_date)

    assert pd.isna(row["combined_flow_5_mcap"])


def test_combined_flow_5_mcap_ignores_future_panel_rows() -> None:
    panel = _panel()
    signal_date = pd.Timestamp("2025-01-08")
    calendar = derive_trading_calendar(panel)
    before = _feature_row(build_flow_ratios(panel, calendar), signal_date)

    mutated = panel.copy()
    mutated.loc[mutated["날짜"].gt(signal_date), "외국인순매수금액추정"] = 999_000.0
    mutated.loc[mutated["날짜"].gt(signal_date), "기관순매수금액추정"] = 999_000.0
    mutated.loc[mutated["날짜"].gt(signal_date), "시가총액추정"] = 1.0
    after = _feature_row(build_flow_ratios(mutated, calendar), signal_date)

    assert after["combined_flow_5_mcap"] == before["combined_flow_5_mcap"]
