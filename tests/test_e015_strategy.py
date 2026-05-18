from __future__ import annotations

import pandas as pd

from src.backtest.engine import BacktestResult
from src.strategies.e015_validation import (
    PASS_THRESHOLDS,
    SPIKE_EXCLUSION_GROUPS,
    TOPK_STABILITY_GRID,
    drawdown_summary,
    e015_segments_for_trading_window,
    topk_label,
)


def test_e015_validation_grid_is_pre_registered_only() -> None:
    assert TOPK_STABILITY_GRID == ((2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1))
    assert tuple(topk_label(counts) for counts in TOPK_STABILITY_GRID) == ("top_3", "top_4", "top_5")
    assert SPIKE_EXCLUSION_GROUPS == ((2020,), (2025,), (2026,), (2020, 2025, 2026))
    assert PASS_THRESHOLDS["topk_sharpe_floor"] == 0.40


def test_e015_restricts_trading_window_without_exploration() -> None:
    segments = ((pd.Timestamp("2010-01-04"), pd.Timestamp("2026-05-04")),)

    restricted = e015_segments_for_trading_window(
        segments=segments,
        trading_start=pd.Timestamp("2021-01-01"),
        trading_end=pd.Timestamp("2026-05-04"),
    )

    assert restricted == ((pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-04")),)


def test_e015_drawdown_summary_identifies_peak_trough_and_recovery() -> None:
    result = BacktestResult(
        equity_curve=pd.DataFrame(
            {
                "date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"]),
                "net_value": [1.0, 1.2, 0.6, 1.25],
            }
        ),
        trades=pd.DataFrame(),
    )

    summary = drawdown_summary(result)

    assert summary["peak_date"] == pd.Timestamp("2025-01-03")
    assert summary["trough_date"] == pd.Timestamp("2025-01-06")
    assert summary["recovery_date"] == pd.Timestamp("2025-01-07")
    assert summary["max_drawdown"] == -0.5
