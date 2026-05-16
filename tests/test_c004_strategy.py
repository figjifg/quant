from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.strategies.c004_quarterly_macro_gate import quarterly_execution_dates, run_c004_variants


def test_c004_quarterly_gate_buys_only_on_quarter_end_signals() -> None:
    dates = pd.to_datetime(
        [
            "2025-03-28",
            "2025-03-31",
            "2025-04-01",
            "2025-06-30",
            "2025-07-01",
        ]
    )
    calendar = KRXTradingCalendar(dates)
    costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    quarterly_regime = _quarterly_regime(["2025-03-31", "2025-06-30"], [True, False])

    runs, candidates = run_c004_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=quarterly_regime,
        market_breadth=_market_breadth(dates),
        costs=costs,
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    assert candidates["macro_gate_mcap"]["signal_date"].unique().tolist() == [
        pd.Timestamp("2025-03-31"),
    ]
    assert runs["macro_gate_mcap"].trades["entry_date"].tolist() == [pd.Timestamp("2025-04-01")] * 5
    assert runs["macro_gate_mcap"].trades["exit_date"].tolist() == [pd.Timestamp("2025-07-01")] * 5


def test_c004_execution_is_first_trading_day_after_signal() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    executions = quarterly_execution_dates(
        calendar,
        _quarterly_regime(["2025-03-31", "2025-06-30"], [True, True]),
        segments=((dates[0], dates[-1]),),
    )

    assert executions == {pd.Timestamp("2025-04-01"), pd.Timestamp("2025-07-01")}
    assert all(execution > signal for signal, execution in zip(pd.to_datetime(["2025-03-31", "2025-06-30"]), sorted(executions)))


def test_c004_kospi_and_cash_variants_are_reported() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01"])
    calendar = KRXTradingCalendar(dates)

    runs, _ = run_c004_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=_quarterly_regime(["2025-03-31"], [False]),
        market_breadth=_market_breadth(dates),
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    assert set(runs) == {"macro_gate_mcap", "kospi_buy_and_hold", "cash"}
    assert runs["macro_gate_mcap"].trades.empty
    assert runs["kospi_buy_and_hold"].equity_curve["net_value"].round(6).tolist() == [1.0, 1.01]
    assert runs["cash"].equity_curve["net_value"].tolist() == [1.0, 1.0]


def _panel(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for date_index, date in enumerate(dates):
        for ticker_index in range(6):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": f"00000{ticker_index}",
                    "시가": 100.0 + date_index,
                    "KRX종가": 101.0 + date_index,
                    "상장주식수": 1_000_000 + ticker_index,
                }
            )
    return pd.DataFrame(rows)


def _universe(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for signal_date, execution_date in zip(dates[:-1], dates[1:], strict=False):
        for ticker_index in range(6):
            rows.append(
                {
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": f"00000{ticker_index}",
                }
            )
    return pd.DataFrame(rows)


def _quarterly_regime(signal_dates: list[str], regime_on: list[bool]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": pd.to_datetime(signal_dates),
            "USDKRW_yoy": [0.0] * len(signal_dates),
            "VIX_60d_avg": [10.0] * len(signal_dates),
            "VIX_240d_avg": [11.0] * len(signal_dates),
            "DXY_yoy": [0.0] * len(signal_dates),
            "regime_score": [2 if on else 1 for on in regime_on],
            "regime_on": regime_on,
        }
    )


def _market_breadth(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] + [0.01] * (len(dates) - 1)})
