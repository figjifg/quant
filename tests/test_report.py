from __future__ import annotations

import pandas as pd

from src.reporting.metrics import METRIC_KEYS
from src.reporting.report import write_report


def _metric_block(trade_count: int) -> dict[str, float | int]:
    return {
        "total_return": 0.01,
        "annualized_return": 0.02,
        "annualized_volatility": 0.03,
        "sharpe": 0.6666666667,
        "max_drawdown": -0.04,
        "hit_rate": 0.5,
        "average_trade_return": 0.001,
        "median_trade_return": 0.001,
        "profit_factor": 1.5,
        "average_holding_period": 5.0,
        "trade_count": trade_count,
        "turnover": 2.0,
        "cost_paid_total": 0.01,
        "return_before_cost": 0.02,
        "return_after_cost": 0.01,
        "exposure_ratio": 0.7,
        "max_consecutive_losses": 2,
    }


def test_write_report_contains_required_sections_and_metric_keys(tmp_path) -> None:
    metrics = {
        "is": _metric_block(10),
        "oos": _metric_block(5),
        "full": _metric_block(15),
        "estimate_included_diagnostic": {"is": _metric_block(11), "oos": _metric_block(6)},
    }
    baselines = {
        name: {"is": _metric_block(index), "oos": _metric_block(index + 10)}
        for index, name in enumerate(
            ["B0_cash", "B1_buy_and_hold", "B2_universe_5d_rebalance", "B3_price_momentum"]
        )
    }
    metadata = {
        "panels_used": ["panel_a.csv", "panel_b.csv"],
        "is_start": "2018-01-02",
        "is_end": "2022-12-30",
        "oos_start": "2023-01-02",
        "oos_end": "2026-05-04",
        "estimate_row_policy": "exclude headline estimated rows",
        "integrated_column_policy": "use KRX종가 only",
        "calendar_source": "panel KRX종가 non-null dates",
        "krx_close_derivation_summary": {"native": 3, "from_종가_fallback": 2},
        "n_tickers": 2,
        "n_trading_days": 3,
    }

    write_report(
        tmp_path,
        metadata,
        metrics,
        baselines,
        pd.DataFrame([{"cost_multiplier": 0, "total_return": 0.02}]),
    )

    report = (tmp_path / "report.md").read_text(encoding="utf-8")

    assert "## Metadata" in report
    assert "## IS Metrics" in report
    assert "## OOS Metrics" in report
    assert "## IS Baseline Comparison" in report
    assert "## OOS Baseline Comparison" in report
    assert "## Cost Sensitivity" in report
    assert "estimate_included_diagnostic" in report
    for key in METRIC_KEYS:
        assert f"| {key} |" in report
