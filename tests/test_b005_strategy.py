from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.strategies.b002_signal_reversal import build_b002_candidates
from src.strategies.b005_relative_flow import VARIANTS, build_b005_candidates, run_b005_variants


def _panel() -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", periods=5)
    rows = []
    for date_index, date in enumerate(dates):
        for ticker_index in range(1, 33):
            ticker = f"{ticker_index:06d}"
            price = 100.0 + ticker_index + date_index
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": price,
                    "KRX종가": price + 0.5,
                }
            )
    return pd.DataFrame(rows)


def _features(panel: pd.DataFrame, calendar: object) -> pd.DataFrame:
    rows = []
    for date_index, signal_date in enumerate(calendar.dates[:-1]):
        execution_date = calendar.dates[date_index + 1]
        for ticker_index in range(1, 33):
            ticker = f"{ticker_index:06d}"
            centered = ticker_index - 16.5
            rows.append(
                {
                    "날짜": signal_date,
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "fnv_5": centered / 100.0,
                    "inv_5": centered / 100.0,
                    "combined_flow_5": centered / 50.0,
                }
            )
    return pd.DataFrame(rows)


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_b005_absolute_baseline_candidates_match_b002() -> None:
    panel = _panel()
    calendar = derive_trading_calendar(panel)
    features = _features(panel, calendar)
    universe = _universe(features)

    candidates, _, _ = build_b005_candidates(features, universe, min_count=30)

    pd.testing.assert_frame_equal(candidates["absolute_baseline"], build_b002_candidates(features, universe))


def test_b005_relative_variants_produce_non_trivial_synthetic_trades() -> None:
    panel = _panel()
    calendar = derive_trading_calendar(panel)
    features = _features(panel, calendar)
    universe = _universe(features)

    runs, candidates, _, _ = run_b005_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        min_count=30,
    )

    assert tuple(runs) == VARIANTS
    assert all(len(runs[variant].trades) > 0 for variant in VARIANTS)
    assert all(len(candidates[variant]) > 0 for variant in VARIANTS)
