from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import run_candidate_backtest
from src.features.flow_ratios import build_atr_pct


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def _panel(
    *,
    periods: int = 48,
    tickers: list[str] | None = None,
    stop_close_index: int | None = None,
    stop_close_price: float = 97.9,
    open_nan_index: int | None = None,
) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    rows = []
    for ticker in tickers or ["000001"]:
        for index, date in enumerate(dates):
            open_price = 100.0
            close_price = 100.0
            if stop_close_index is not None and index == stop_close_index and ticker == "000001":
                close_price = stop_close_price
            if open_nan_index is not None and index == open_nan_index and ticker == "000001":
                open_price = pd.NA
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": open_price,
                    "고가": 100.5,
                    "저가": 99.5,
                    "KRX종가": close_price,
                }
            )
    return pd.DataFrame(rows)


def _candidates(
    dates: tuple[pd.Timestamp, ...],
    *,
    execution_indices: list[int],
    ticker: str = "000001",
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "execution_date": dates[index],
                "signal_date": dates[index - 1],
                "종목코드": ticker,
                "fnv_5": 0.1,
                "inv_5": 0.1,
                "combined_flow_5": 1.0,
            }
            for index in execution_indices
        ]
    )


def test_vol_stop_triggers_on_close_and_exits_next_open() -> None:
    panel = _panel(stop_close_index=24, stop_close_price=97.9)
    calendar = derive_trading_calendar(panel)
    atr = build_atr_pct(panel, calendar, window=20)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates, execution_indices=[21]),
        _costs(),
        period_start=calendar.dates[21],
        period_end=calendar.dates[30],
        vol_stop_k=2.0,
        vol_stop_atr_window=20,
        atr_features=atr,
        holding=20,
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == calendar.dates[21]
    assert trade["exit_date"] == calendar.dates[25]
    assert trade["exit_price"] == 100.0
    assert trade["exit_reason"] == "vol_stop"


def test_time_cap_exits_at_close_when_no_stop() -> None:
    panel = _panel(periods=50)
    calendar = derive_trading_calendar(panel)
    atr = build_atr_pct(panel, calendar, window=20)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates, execution_indices=[21]),
        _costs(),
        period_start=calendar.dates[21],
        period_end=calendar.dates[-1],
        vol_stop_k=2.0,
        vol_stop_atr_window=20,
        atr_features=atr,
        holding=20,
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.add_trading_days(calendar.dates[21], 20)
    assert trade["exit_price"] == 100.0
    assert trade["exit_reason"] == "time_cap"


def test_vol_stop_fallback_when_next_open_nan() -> None:
    panel = _panel(stop_close_index=24, stop_close_price=97.9, open_nan_index=25)
    calendar = derive_trading_calendar(panel)
    atr = build_atr_pct(panel, calendar, window=20)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates, execution_indices=[21]),
        _costs(),
        period_start=calendar.dates[21],
        period_end=calendar.dates[30],
        vol_stop_k=2.0,
        vol_stop_atr_window=20,
        atr_features=atr,
        holding=20,
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.dates[26]
    assert trade["exit_price"] == 100.0
    assert trade["exit_reason"] == "vol_stop_fallback"


def test_engine_unchanged_when_vol_stop_k_is_none() -> None:
    panel = _panel(periods=36, tickers=["000001", "000002"])
    calendar = derive_trading_calendar(panel)
    candidates = _candidates(calendar.dates, execution_indices=[21, 22, 23])

    before = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[20],
        period_end=calendar.dates[35],
        holding=5,
    )
    after = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[20],
        period_end=calendar.dates[35],
        holding=5,
        vol_stop_k=None,
    )

    pd.testing.assert_frame_equal(after.trades, before.trades)
    pd.testing.assert_frame_equal(after.equity_curve, before.equity_curve)


def test_atr_pct_20_uses_strictly_prior_rows() -> None:
    panel = _panel(periods=35)
    calendar = derive_trading_calendar(panel)
    target_date = calendar.dates[21]
    before = build_atr_pct(panel, calendar, window=20)

    mutated = panel.copy()
    future_mask = mutated["날짜"].ge(target_date)
    mutated.loc[future_mask, "고가"] = 999.0
    mutated.loc[future_mask, "저가"] = 1.0
    mutated.loc[future_mask, "KRX종가"] = 2.0
    after = build_atr_pct(mutated, calendar, window=20)

    before_value = before.loc[
        before["날짜"].eq(target_date) & before["종목코드"].eq("000001"),
        "atr_pct_20",
    ].iloc[0]
    after_value = after.loc[
        after["날짜"].eq(target_date) & after["종목코드"].eq("000001"),
        "atr_pct_20",
    ].iloc[0]
    assert after_value == before_value


def test_stop_then_no_rebuy_same_day() -> None:
    panel = _panel(stop_close_index=24, stop_close_price=97.9)
    calendar = derive_trading_calendar(panel)
    atr = build_atr_pct(panel, calendar, window=20)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates, execution_indices=[21, 25]),
        _costs(),
        period_start=calendar.dates[21],
        period_end=calendar.dates[30],
        vol_stop_k=2.0,
        vol_stop_atr_window=20,
        atr_features=atr,
        holding=20,
    )

    assert len(result.trades) == 1
    assert result.trades.iloc[0]["exit_date"] == calendar.dates[25]
