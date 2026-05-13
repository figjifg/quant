from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar


MIN_AVG_TRADED_VALUE_20D = 5_000_000_000
LIQUIDITY_LOOKBACK = 20
SIGNAL_LOOKBACK = 5
KEY_COLUMNS = ("종목코드", "날짜")
REQUIRED_COLUMNS = (
    "날짜",
    "종목코드",
    "KRX종가",
    "거래대금추정",
    "수급금액추정여부",
    "거래대금추정여부",
    "동적유니버스포함",
)
OUTPUT_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "avg_traded_value_20d",
)


def build_execution_universe(
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    *,
    min_avg_traded_value_20d: float = MIN_AVG_TRADED_VALUE_20D,
    exclude_estimated_flag_rows: bool = True,
) -> pd.DataFrame:
    """Build E001 entry eligibility by execution date.

    The first calendar date has no prior KRX trading day, so it never emits
    eligible rows. The 20-day liquidity rule uses the last 20 observed panel
    rows per ticker through the prior trading day; tickers with fewer than 20
    such rows are ineligible.
    """
    _validate_panel(panel)

    sorted_panel = panel.copy()
    sorted_panel["날짜"] = pd.to_datetime(sorted_panel["날짜"], errors="raise").astype("datetime64[ns]")
    sorted_panel["종목코드"] = sorted_panel["종목코드"].astype("string")
    sorted_panel = sorted_panel.sort_values(list(KEY_COLUMNS)).reset_index(drop=True)

    universe_frames = [
        _universe_for_ticker(
            ticker=ticker,
            group=group,
            calendar=calendar,
            min_avg_traded_value_20d=min_avg_traded_value_20d,
            exclude_estimated_flag_rows=exclude_estimated_flag_rows,
        )
        for ticker, group in sorted_panel.groupby("종목코드", sort=False)
    ]

    if not universe_frames:
        return _empty_universe()

    universe = pd.concat(universe_frames, ignore_index=True)
    if universe.empty:
        return _empty_universe()

    return universe.sort_values(["execution_date", "종목코드"]).reset_index(drop=True)


def _universe_for_ticker(
    *,
    ticker: str,
    group: pd.DataFrame,
    calendar: KRXTradingCalendar,
    min_avg_traded_value_20d: float,
    exclude_estimated_flag_rows: bool,
) -> pd.DataFrame:
    dates = pd.Index(calendar.dates, name="execution_date")
    if len(dates) < 2:
        return _empty_universe()

    signal_dates = pd.Index(calendar.dates[:-1], name="signal_date")
    execution_dates = pd.Index(calendar.dates[1:], name="execution_date")

    by_date = group.set_index("날짜").sort_index()
    row_positions = by_date.index.searchsorted(signal_dates, side="right") - 1
    has_prior_row = row_positions >= 0

    primary_universe_member = pd.Series(False, index=execution_dates)
    avg_traded_value_20d = pd.Series(pd.NA, index=execution_dates, dtype="Float64")

    if has_prior_row.any():
        current_rows = by_date.iloc[row_positions[has_prior_row]]
        primary_universe_member.loc[execution_dates[has_prior_row]] = (
            current_rows["동적유니버스포함"] & current_rows["KRX종가"].notna()
        ).to_numpy(dtype=bool)

        traded_value_20d = by_date["거래대금추정"].rolling(
            LIQUIDITY_LOOKBACK,
            min_periods=LIQUIDITY_LOOKBACK,
        ).mean()
        current_liquidity = traded_value_20d.iloc[row_positions[has_prior_row]]
        avg_traded_value_20d.loc[execution_dates[has_prior_row]] = current_liquidity.to_numpy()

    eligible = primary_universe_member & avg_traded_value_20d.ge(
        min_avg_traded_value_20d
    ).fillna(False)

    if exclude_estimated_flag_rows:
        eligible &= _signal_window_estimates_are_clean(by_date, calendar).reindex(
            execution_dates,
            fill_value=False,
        )

    result = pd.DataFrame(
        {
            "execution_date": execution_dates,
            "signal_date": signal_dates,
            "종목코드": ticker,
            "avg_traded_value_20d": avg_traded_value_20d.to_numpy(),
            "eligible": eligible.to_numpy(dtype=bool),
        }
    )
    return result.loc[result["eligible"], list(OUTPUT_COLUMNS)]


def _signal_window_estimates_are_clean(
    by_date: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> pd.Series:
    calendar_index = pd.Index(calendar.dates, name="날짜")
    aligned = by_date.reindex(calendar_index)

    clean_row = (
        aligned["거래대금추정여부"].eq(False)
        & aligned["거래대금추정여부"].notna()
    )
    clean_window = clean_row.rolling(SIGNAL_LOOKBACK, min_periods=SIGNAL_LOOKBACK).sum().eq(
        SIGNAL_LOOKBACK
    )

    return pd.Series(
        clean_window.iloc[:-1].to_numpy(dtype=bool),
        index=pd.Index(calendar.dates[1:], name="execution_date"),
    )


def _empty_universe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "execution_date": pd.Series(dtype="datetime64[ns]"),
            "signal_date": pd.Series(dtype="datetime64[ns]"),
            "종목코드": pd.Series(dtype="string"),
            "avg_traded_value_20d": pd.Series(dtype="float64"),
        }
    )


def _validate_panel(panel: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in panel.columns]
    if missing:
        raise ValueError(f"Missing required universe columns: {missing}")

    if panel.duplicated(list(KEY_COLUMNS)).any():
        raise ValueError("Panel contains duplicate rows for (종목코드, 날짜).")
