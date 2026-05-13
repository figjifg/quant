from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar


MARKET_FLOW_COLUMNS = ("kospi_foreign_net", "kospi_institution_net")
PANEL_PROXY_COLUMNS = ("날짜", "종목코드", "KRX종가", "거래대금추정")
GATE_WINDOW = 5


def build_market_gate_features(
    market_flow_df: pd.DataFrame,
    calendar: KRXTradingCalendar,
    kospi_close_series: pd.Series | None = None,
) -> pd.DataFrame:
    """Build E003 market-flow and price-gate features.

    `kospi_close_series` is optional so unit tests can pass a controlled close
    series. The E003 runner supplies a locked-data KOSPI proxy from
    `build_kospi_proxy_close_series`, not an external official KOSPI index.
    """
    _require_columns(market_flow_df, MARKET_FLOW_COLUMNS, "market_flow_df")

    calendar_index = pd.Index(calendar.dates, name="signal_date")
    flow = market_flow_df.copy()
    if "date" in flow.columns:
        flow["date"] = pd.to_datetime(flow["date"], errors="raise").dt.normalize()
        flow = flow.set_index("date")
    flow.index = pd.to_datetime(flow.index, errors="raise").normalize()
    flow = flow.sort_index()

    aligned = flow.loc[:, list(MARKET_FLOW_COLUMNS)].reindex(calendar_index)
    combined_daily = aligned["kospi_foreign_net"] + aligned["kospi_institution_net"]
    combined_net_5 = combined_daily.rolling(GATE_WINDOW, min_periods=GATE_WINDOW).sum()
    market_gate_defined = combined_net_5.notna()
    market_gate_on = combined_net_5.gt(0).fillna(False)

    kospi_5d_return = _kospi_5d_return(kospi_close_series, calendar_index)
    price_gate_on = kospi_5d_return.gt(0).fillna(False)

    result = pd.DataFrame(
        {
            "signal_date": calendar_index,
            "execution_date": _execution_dates(calendar),
            "kospi_combined_net_5": combined_net_5.to_numpy(),
            "market_gate_on": market_gate_on.to_numpy(dtype=bool),
            "market_gate_defined": market_gate_defined.to_numpy(dtype=bool),
            "market_gate_off": ((~market_gate_on) & market_gate_defined).to_numpy(dtype=bool),
            "kospi_5d_return": kospi_5d_return.to_numpy(),
            "price_gate_on": price_gate_on.to_numpy(dtype=bool),
        }
    )
    result["double_gate_on"] = result["market_gate_on"] & result["price_gate_on"]
    return result


def build_kospi_proxy_close_series(panel: pd.DataFrame, calendar: KRXTradingCalendar) -> pd.Series:
    """Build a locked-data KOSPI proxy from dynamic-Top100 value-weighted returns.

    This intentionally does not read an official KOSPI index. Per the E003
    ticket's preferred option, it compounds the daily traded-value-weighted
    return of the current equity panel into a close-like index level.
    """
    _require_columns(panel, PANEL_PROXY_COLUMNS, "panel")
    frame = panel.loc[:, list(PANEL_PROXY_COLUMNS)].copy()
    frame["날짜"] = pd.to_datetime(frame["날짜"], errors="raise").dt.normalize()
    frame["종목코드"] = frame["종목코드"].astype("string")
    frame["KRX종가"] = pd.to_numeric(frame["KRX종가"], errors="coerce")
    frame["거래대금추정"] = pd.to_numeric(frame["거래대금추정"], errors="coerce")
    frame = frame.sort_values(["종목코드", "날짜"])

    frame["prev_close"] = frame.groupby("종목코드", sort=False)["KRX종가"].shift(1)
    valid = (
        frame["KRX종가"].gt(0)
        & frame["prev_close"].gt(0)
        & frame["거래대금추정"].gt(0)
        & frame["날짜"].isin(calendar.dates)
    )
    returns = frame.loc[valid].assign(daily_return=frame.loc[valid, "KRX종가"] / frame.loc[valid, "prev_close"] - 1)
    weighted_return = returns.groupby("날짜", sort=True).apply(
        lambda group: (group["daily_return"] * group["거래대금추정"]).sum() / group["거래대금추정"].sum(),
        include_groups=False,
    )
    weighted_return = weighted_return.reindex(pd.Index(calendar.dates, name="날짜")).fillna(0.0)
    return (1.0 + weighted_return).cumprod()


def _kospi_5d_return(
    kospi_close_series: pd.Series | None,
    calendar_index: pd.Index,
) -> pd.Series:
    if kospi_close_series is None:
        return pd.Series(float("nan"), index=calendar_index, dtype="float64")

    close = kospi_close_series.copy()
    close.index = pd.to_datetime(close.index, errors="raise").normalize()
    close = pd.to_numeric(close, errors="coerce").reindex(calendar_index)
    return close / close.shift(GATE_WINDOW) - 1.0


def _execution_dates(calendar: KRXTradingCalendar) -> pd.Series:
    dates = list(calendar.dates[1:]) + [pd.NaT]
    return pd.Series(dates, dtype="datetime64[ns]")


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
