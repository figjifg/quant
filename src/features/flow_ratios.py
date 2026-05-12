from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar


LOOKBACK = 5
KEY_COLUMNS = ("종목코드", "날짜")
REQUIRED_COLUMNS = (
    "날짜",
    "종목코드",
    "KRX종가",
    "거래대금추정",
    "외국인순매수금액추정",
    "기관순매수금액추정",
)
FEATURE_COLUMNS = (
    "traded_value_5",
    "foreign_net_5",
    "institution_net_5",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
    "recent_return_5",
)


def build_flow_ratios(panel: pd.DataFrame, calendar: KRXTradingCalendar) -> pd.DataFrame:
    """Build E001 flow features using per-ticker, right-labeled 5-day windows."""
    _validate_panel(panel)

    sorted_panel = panel.copy()
    sorted_panel["날짜"] = pd.to_datetime(sorted_panel["날짜"], errors="raise").astype("datetime64[ns]")
    sorted_panel["종목코드"] = sorted_panel["종목코드"].astype("string")
    sorted_panel = sorted_panel.sort_values(list(KEY_COLUMNS)).reset_index(drop=True)

    feature_frames = [
        _features_for_ticker(ticker, group, calendar)
        for ticker, group in sorted_panel.groupby("종목코드", sort=False)
    ]
    features = pd.concat(feature_frames, ignore_index=True)

    result = sorted_panel.merge(features, on=list(KEY_COLUMNS), how="left", validate="one_to_one")
    result = result.assign(
        signal_date=result["날짜"],
        execution_date=_execution_dates(result["날짜"], calendar),
    )
    return result


def _features_for_ticker(
    ticker: str,
    group: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> pd.DataFrame:
    calendar_index = pd.Index(calendar.dates, name="날짜")
    by_date = group.set_index("날짜")
    aligned = by_date.reindex(calendar_index)

    traded_value_5 = aligned["거래대금추정"].rolling(LOOKBACK, min_periods=LOOKBACK).sum()
    foreign_net_5 = aligned["외국인순매수금액추정"].rolling(LOOKBACK, min_periods=LOOKBACK).sum()
    institution_net_5 = aligned["기관순매수금액추정"].rolling(LOOKBACK, min_periods=LOOKBACK).sum()

    features = pd.DataFrame(
        {
            "종목코드": ticker,
            "traded_value_5": traded_value_5,
            "foreign_net_5": foreign_net_5,
            "institution_net_5": institution_net_5,
            "fnv_5": foreign_net_5 / traded_value_5,
            "inv_5": institution_net_5 / traded_value_5,
            "combined_flow_5": (foreign_net_5 + institution_net_5) / traded_value_5,
            "recent_return_5": aligned["KRX종가"] / aligned["KRX종가"].shift(LOOKBACK) - 1,
        }
    ).reset_index()

    original_dates = pd.Index(group["날짜"])
    return features.loc[features["날짜"].isin(original_dates), ["종목코드", "날짜", *FEATURE_COLUMNS]]


def _execution_dates(dates: pd.Series, calendar: KRXTradingCalendar) -> pd.Series:
    calendar_index = pd.Index(calendar.dates)

    def next_or_nat(date: pd.Timestamp) -> pd.Timestamp | pd.NaT:
        position = int(calendar_index.searchsorted(date, side="right"))
        if position >= len(calendar_index):
            return pd.NaT
        return calendar_index[position]

    return dates.map(next_or_nat).astype("datetime64[ns]")


def _validate_panel(panel: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in panel.columns]
    if missing:
        raise ValueError(f"Missing required flow feature columns: {missing}")

    if panel.duplicated(list(KEY_COLUMNS)).any():
        raise ValueError("Panel contains duplicate rows for (종목코드, 날짜).")
