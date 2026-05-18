from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.features.volatility_targeting import apply_volatility_target_to_weights, volatility_scalars


def test_g000_configs_freeze_target_vol_and_carriers() -> None:
    d013 = yaml.safe_load(Path("configs/backtests/g000_d013.yaml").read_text(encoding="utf-8"))
    e014 = yaml.safe_load(Path("configs/backtests/g000_e014.yaml").read_text(encoding="utf-8"))

    assert d013["experiment_id"] == "G000"
    assert e014["experiment_id"] == "G000"
    assert d013["carrier"] == "d013"
    assert e014["carrier"] == "e014"
    assert d013["volatility_targeting"] == {"target_vol": 0.20, "window": 60, "annualization": 252}
    assert e014["volatility_targeting"] == {"target_vol": 0.20, "window": 60, "annualization": 252}
    assert d013["output_dir"] == e014["output_dir"] == "reports/experiments/G000_layer4_design"


def test_vol_scalar_uses_only_returns_through_signal_date() -> None:
    dates = pd.date_range("2025-01-01", periods=63, freq="B")
    returns = [0.0] + [0.01, -0.01] * 31
    net_value = pd.Series([1.0 + value for value in returns], dtype="float64").cumprod()
    before = pd.DataFrame({"date": dates, "net_value": net_value})
    after = before.copy()
    after.loc[62, "net_value"] = after.loc[61, "net_value"] * 100.0

    before_scalar = volatility_scalars(before, [dates[61]], target_vol=0.20)
    after_scalar = volatility_scalars(after, [dates[61]], target_vol=0.20)

    pd.testing.assert_frame_equal(before_scalar, after_scalar)


def test_vol_scalar_formula_and_weight_cash_filler() -> None:
    dates = pd.date_range("2025-01-01", periods=61, freq="B")
    returns = [0.0] + [0.02, -0.02] * 30
    net_value = pd.Series([1.0 + value for value in returns], dtype="float64").cumprod()
    equity = pd.DataFrame({"date": dates, "net_value": net_value})

    scalars = volatility_scalars(equity, [dates[-1]], target_vol=0.20)
    expected_vol = pd.Series(returns[1:], dtype="float64").std(ddof=1) * math.sqrt(252)
    expected_scalar = min(1.0, 0.20 / expected_vol)
    assert scalars.loc[0, "realized_vol_60d"] == pytest.approx(expected_vol)
    assert scalars.loc[0, "vol_scalar"] == pytest.approx(expected_scalar)

    candidates = pd.DataFrame(
        {
            "signal_date": [dates[-1], dates[-1]],
            "종목코드": ["000001", "000002"],
            "target_weight": [0.5, 0.5],
        }
    )
    targeted = apply_volatility_target_to_weights(candidates, scalars)
    assert targeted["target_weight_before_vol"].tolist() == pytest.approx([0.5, 0.5])
    assert targeted["target_weight"].sum() == pytest.approx(expected_scalar)
