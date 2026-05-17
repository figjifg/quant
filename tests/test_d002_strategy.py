from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.features.macro_regime import factor_aggregation_composite
from src.strategies.d002_zscore_24mo import run_d002_variants


def test_d002_factor_quarterly_gate_uses_next_day_execution() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    runs, candidates = run_d002_variants(
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


def test_d002_zscore_warmup_is_two_years_not_five_years() -> None:
    dates = pd.date_range("2010-01-31", periods=24, freq="ME")
    regime = _factor_regime_frame(dates)

    result_24 = factor_aggregation_composite(regime, z_score_window_months=24)
    result_60 = factor_aggregation_composite(regime, z_score_window_months=60)

    assert not pd.isna(result_24.loc[23, "composite"])
    assert pd.isna(result_60.loc[23, "composite"])


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


def _factor_regime_frame(dates: pd.DatetimeIndex) -> pd.DataFrame:
    values = [1.0 + index for index in range(len(dates))]
    return pd.DataFrame(
        {
            "signal_date": dates,
            "USDKRW_yoy": values,
            "VIX_60d_avg": values,
            "VIX_240d_avg": [1.0] * len(dates),
            "DXY_yoy": values,
            "US_2_10_curve_spread": values,
            "Brent_yoy": values,
            "KR10Y_yoy_change": values,
            "US_CPI_decel": values,
            "US_PPI_decel": values,
        }
    )
