from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.features.macro_regime import exposure_scalar
from src.strategies.d001_factor_aggregation import run_d001_variants
from src.strategies.d004_position_sizing import run_d004_variants


def test_d004_exposure_scalar_fixed_linear_math() -> None:
    assert exposure_scalar(-0.5) == pytest.approx(0.0)
    assert exposure_scalar(0.0) == pytest.approx(0.0)
    assert exposure_scalar(0.3) == pytest.approx(0.3)
    assert exposure_scalar(0.6) == pytest.approx(0.6)
    assert exposure_scalar(1.0) == pytest.approx(1.0)
    assert exposure_scalar(2.0) == pytest.approx(1.0)
    with pytest.raises(ValueError, match="fixed k=1.0"):
        exposure_scalar(0.5, k=2.0)


def test_d004_per_stock_weight_and_cash_filler() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    runs, candidates = run_d004_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=_quarterly_regime(["2025-03-31", "2025-06-30"], [0.6, -0.1]),
        market_breadth=_market_breadth(dates),
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    selected = candidates["factor_macro_sized_mcap"]
    assert selected["target_weight"].tolist() == pytest.approx([0.12] * 5)
    assert selected["exposure_scalar"].tolist() == pytest.approx([0.6] * 5)
    first_entry = runs["factor_macro_sized_mcap"].equity_curve.loc[
        runs["factor_macro_sized_mcap"].equity_curve["date"].eq(pd.Timestamp("2025-04-01"))
    ].iloc[0]
    assert first_entry["cash"] == pytest.approx(0.4)
    assert first_entry["mtm_value"] == pytest.approx(0.6)
    assert first_entry["net_value"] == pytest.approx(1.0)


def test_d004_full_exposure_matches_d001_carrier_on_tiny_zero_cost_case() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)
    kwargs = {
        "panel": _panel(dates),
        "calendar": calendar,
        "universe": _universe(dates),
        "quarterly_regime": _quarterly_regime(["2025-03-31", "2025-06-30"], [1.0, -0.1]),
        "market_breadth": _market_breadth(dates),
        "costs": Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        "segments": ((dates[0], dates[-1]),),
        "max_positions": 5,
    }

    d001_runs, _ = run_d001_variants(**kwargs)
    d004_runs, d004_candidates = run_d004_variants(**kwargs)

    d001 = d001_runs["factor_macro_gate_mcap"]
    d004 = d004_runs["factor_macro_sized_mcap"]
    pd.testing.assert_series_equal(d001.equity_curve["net_value"], d004.equity_curve["net_value"], check_names=False)
    pd.testing.assert_series_equal(d001.trades["notional_at_entry"], d004.trades["notional_at_entry"], check_names=False)
    assert d004_candidates["factor_macro_sized_mcap"]["target_weight"].tolist() == pytest.approx([0.2] * 5)
    assert all(d004.trades["entry_date"] > d004.trades["signal_date"])


def _panel(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for date in dates:
        for ticker_index in range(6):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": f"00000{ticker_index}",
                    "시가": 100.0,
                    "KRX종가": 100.0,
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


def _quarterly_regime(signal_dates: list[str], composites: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": pd.to_datetime(signal_dates),
            "composite": composites,
            "regime_score": composites,
            "regime_on": [value >= 0.0 for value in composites],
        }
    )


def _market_breadth(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] + [0.01] * (len(dates) - 1)})
