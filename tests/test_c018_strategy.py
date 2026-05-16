from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.strategies.c018_quarterly_macro_v15 import run_c018_variants


def test_c018_us_m2_nine_signal_quarterly_gate_uses_next_day_execution() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    runs, candidates = run_c018_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=_quarterly_regime(["2025-03-31", "2025-06-30"], [True, False]),
        market_breadth=_market_breadth(dates),
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    assert set(runs) == {"macro_gate_mcap", "kospi_buy_and_hold", "cash"}
    assert candidates["macro_gate_mcap"]["signal_date"].unique().tolist() == [pd.Timestamp("2025-03-31")]
    assert runs["macro_gate_mcap"].trades["entry_date"].tolist() == [pd.Timestamp("2025-04-01")] * 5
    assert all(runs["macro_gate_mcap"].trades["entry_date"] > runs["macro_gate_mcap"].trades["signal_date"])


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
            "US_2_10_curve_spread": [0.5] * len(signal_dates),
            "US10Y_yoy_change": [-0.1] * len(signal_dates),
            "Brent_yoy": [0.0] * len(signal_dates),
            "KR10Y_yoy_change": [-0.1] * len(signal_dates),
            "US_CPI_yoy": [0.03] * len(signal_dates),
            "US_CPI_decel": [-0.01] * len(signal_dates),
            "US_PPI_yoy": [0.02] * len(signal_dates),
            "US_PPI_decel": [-0.02] * len(signal_dates),
            "US_M2_yoy": [0.06] * len(signal_dates),
            "favorable_USDKRW": [True] * len(signal_dates),
            "favorable_VIX": [True] * len(signal_dates),
            "favorable_DXY": [True] * len(signal_dates),
            "favorable_US_2_10_curve": [True] * len(signal_dates),
            "favorable_Brent": [True] * len(signal_dates),
            "favorable_KR10Y": [True] * len(signal_dates),
            "favorable_US_CPI": [True] * len(signal_dates),
            "favorable_US_PPI": [True] * len(signal_dates),
            "favorable_US_M2": [True] * len(signal_dates),
            "regime_score": [2 if on else 1 for on in regime_on],
            "regime_on": regime_on,
        }
    )


def _market_breadth(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] + [0.01] * (len(dates) - 1)})
