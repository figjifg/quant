from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.features.flow_ratios import build_flow_ratios


def _synthetic_panel() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=30, freq="B")
    rows = []
    for ticker_index, ticker in enumerate(["000010", "000020", "000030"], start=1):
        for day_index, date in enumerate(dates, start=1):
            if ticker == "000020" and date == dates[7]:
                continue
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "KRX종가": 100.0 * ticker_index + day_index,
                    "거래대금추정": 1_000.0 + day_index,
                    "시가총액추정": 100_000.0 + ticker_index * 10_000.0 + day_index,
                    "외국인순매수금액추정": 10.0 * ticker_index + day_index,
                    "기관순매수금액추정": 20.0 * ticker_index + day_index,
                }
            )
    return pd.DataFrame(rows)


def _feature_row(features: pd.DataFrame, ticker: str, date: pd.Timestamp) -> pd.Series:
    rows = features.loc[(features["종목코드"] == ticker) & (features["날짜"] == date)]
    assert len(rows) == 1
    return rows.iloc[0]


def test_flow_ratio_uses_closed_form_sum_ending_at_signal_date() -> None:
    panel = _synthetic_panel()
    calendar = derive_trading_calendar(panel)
    features = build_flow_ratios(panel, calendar)
    ticker = "000010"
    signal_date = pd.Timestamp("2025-01-15")

    window = panel.loc[
        (panel["종목코드"] == ticker)
        & (panel["날짜"].between(pd.Timestamp("2025-01-09"), signal_date))
    ]
    expected = window["외국인순매수금액추정"].sum() / window["거래대금추정"].sum()

    row = _feature_row(features, ticker, signal_date)
    assert row["fnv_5"] == expected
    assert row["signal_date"] == signal_date
    assert row["execution_date"] == pd.Timestamp("2025-01-16")


def test_future_row_mutation_does_not_change_feature_at_prior_date() -> None:
    panel = _synthetic_panel()
    calendar = derive_trading_calendar(panel)
    ticker = "000010"
    signal_date = pd.Timestamp("2025-01-15")

    before = _feature_row(build_flow_ratios(panel, calendar), ticker, signal_date)
    mutated = panel.copy()
    mutated.loc[mutated["날짜"] > signal_date, "거래대금추정"] = 0.0
    after = _feature_row(build_flow_ratios(mutated, calendar), ticker, signal_date)

    assert after["fnv_5"] == before["fnv_5"]
    assert after["traded_value_5"] == before["traded_value_5"]
    assert after["combined_flow_5"] == before["combined_flow_5"]


def test_nan_inputs_propagate_within_each_feature_window() -> None:
    panel = _synthetic_panel()
    ticker = "000010"
    signal_date = pd.Timestamp("2025-01-15")
    nan_date = pd.Timestamp("2025-01-13")
    panel.loc[
        (panel["종목코드"] == ticker) & (panel["날짜"] == nan_date),
        "외국인순매수금액추정",
    ] = pd.NA

    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    row = _feature_row(features, ticker, signal_date)

    assert pd.isna(row["foreign_net_5"])
    assert pd.isna(row["fnv_5"])
    assert not pd.isna(row["traded_value_5"])


def test_missing_ticker_date_does_not_contaminate_other_tickers() -> None:
    panel = _synthetic_panel()
    calendar = derive_trading_calendar(panel)
    features = build_flow_ratios(panel, calendar)
    signal_date = pd.Timestamp("2025-01-15")

    ticker_with_gap = _feature_row(features, "000020", signal_date)
    ticker_without_gap = _feature_row(features, "000010", signal_date)

    assert pd.isna(ticker_with_gap["fnv_5"])
    assert not pd.isna(ticker_without_gap["fnv_5"])


def test_recent_return_uses_per_ticker_shift_only() -> None:
    panel = _synthetic_panel()
    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    signal_date = pd.Timestamp("2025-01-16")
    row = _feature_row(features, "000030", signal_date)
    ticker_panel = panel.loc[panel["종목코드"] == "000030"].sort_values("날짜")
    current_close = ticker_panel.loc[ticker_panel["날짜"] == signal_date, "KRX종가"].iloc[0]
    shifted_close = ticker_panel.loc[ticker_panel["날짜"] == pd.Timestamp("2025-01-09"), "KRX종가"].iloc[0]

    assert row["recent_return_5"] == current_close / shifted_close - 1


def test_last_calendar_date_keeps_row_with_nat_execution_date() -> None:
    panel = _synthetic_panel()
    features = build_flow_ratios(panel, derive_trading_calendar(panel))
    row = _feature_row(features, "000010", pd.Timestamp("2025-02-12"))

    assert pd.isna(row["execution_date"])
