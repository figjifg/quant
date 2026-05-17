from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.strategies.d001_factor_aggregation import run_d001_variants


def test_d001_factor_quarterly_gate_uses_next_day_execution() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    runs, candidates = run_d001_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=_quarterly_regime(["2025-03-31", "2025-06-30"], [True, False]),
        market_breadth=_market_breadth(dates),
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    assert set(runs) == {"factor_macro_gate_mcap", "kospi_buy_and_hold", "cash"}
    assert candidates["factor_macro_gate_mcap"]["signal_date"].unique().tolist() == [pd.Timestamp("2025-03-31")]
    assert runs["factor_macro_gate_mcap"].trades["entry_date"].tolist() == [pd.Timestamp("2025-04-01")] * 5
    assert all(runs["factor_macro_gate_mcap"].trades["entry_date"] > runs["factor_macro_gate_mcap"].trades["signal_date"])


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
            "composite": [0.1 if on else -0.1 for on in regime_on],
            "regime_score": [0.1 if on else -0.1 for on in regime_on],
            "regime_on": regime_on,
        }
    )


def _market_breadth(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] + [0.01] * (len(dates) - 1)})
