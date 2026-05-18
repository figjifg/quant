from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.features.mdd_cooldown import apply_mdd_cooldown_to_weights, mdd_cooldown_scalars


def test_g001_configs_freeze_mdd_cooldown_parameters_and_carriers() -> None:
    d013 = yaml.safe_load(Path("configs/backtests/g001_d013.yaml").read_text(encoding="utf-8"))
    e014 = yaml.safe_load(Path("configs/backtests/g001_e014.yaml").read_text(encoding="utf-8"))

    expected = {
        "drawdown_lookback_days": 252,
        "warning_threshold": -0.05,
        "hard_threshold": -0.15,
        "hard_scalar": 0.5,
    }
    assert d013["experiment_id"] == "G001"
    assert e014["experiment_id"] == "G001"
    assert d013["carrier"] == "d013"
    assert e014["carrier"] == "e014"
    assert d013["mdd_cooldown"] == expected
    assert e014["mdd_cooldown"] == expected
    assert d013["output_dir"] == e014["output_dir"] == "reports/experiments/G001_mdd_cooldown"


def test_mdd_scalar_uses_only_portfolio_value_through_signal_date() -> None:
    dates = pd.date_range("2025-01-01", periods=12, freq="B")
    before = pd.DataFrame({"date": dates, "net_value": [100, 110, 120, 115, 108, 102, 96, 98, 100, 101, 102, 103]})
    after = before.copy()
    after.loc[11, "net_value"] = 10.0

    before_scalar = mdd_cooldown_scalars(before, [dates[10]], drawdown_lookback_days=5)
    after_scalar = mdd_cooldown_scalars(after, [dates[10]], drawdown_lookback_days=5)

    pd.testing.assert_frame_equal(before_scalar, after_scalar)


def test_mdd_scalar_formula_boundaries_and_weight_cash_filler() -> None:
    dates = pd.date_range("2025-01-01", periods=4, freq="B")
    equity = pd.DataFrame({"date": dates, "net_value": [100.0, 95.0, 90.0, 80.0]})

    scalars = mdd_cooldown_scalars(equity, dates, drawdown_lookback_days=252)
    assert scalars["portfolio_drawdown"].tolist() == pytest.approx([0.0, -0.05, -0.10, -0.20])
    assert scalars["exposure_scalar"].tolist() == pytest.approx([1.0, 1.0, 0.75, 0.5])

    candidates = pd.DataFrame(
        {
            "signal_date": [dates[2], dates[2]],
            "종목코드": ["000001", "000002"],
            "target_weight": [0.5, 0.5],
        }
    )
    targeted = apply_mdd_cooldown_to_weights(candidates, scalars)
    assert targeted["target_weight_before_mdd"].tolist() == pytest.approx([0.5, 0.5])
    assert targeted["target_weight"].sum() == pytest.approx(0.75)
