from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.features.stress_filter import (
    apply_stress_filter_to_weights,
    stress_exposure_scalar,
    stress_filter_scalars,
)


def test_g002_configs_freeze_stress_filter_parameters_and_carriers() -> None:
    d013 = yaml.safe_load(Path("configs/backtests/g002_d013.yaml").read_text(encoding="utf-8"))
    e014 = yaml.safe_load(Path("configs/backtests/g002_e014.yaml").read_text(encoding="utf-8"))

    expected = {
        "z_window": 60,
        "usdkrw_yoy_lookback_days": 252,
        "kospi_vol_window": 60,
        "normal_threshold": 1.0,
        "extreme_threshold": 2.0,
        "extreme_scalar": 0.5,
    }
    assert d013["experiment_id"] == "G002"
    assert e014["experiment_id"] == "G002"
    assert d013["carrier"] == "d013"
    assert e014["carrier"] == "e014"
    assert d013["stress_filter"] == expected
    assert e014["stress_filter"] == expected
    assert d013["output_dir"] == e014["output_dir"] == "reports/experiments/G002_stress_filter"


def test_stress_scalar_formula_boundaries_nan_and_weight_cash_filler() -> None:
    score = pd.Series([pd.NA, 0.99, 1.0, 1.5, 2.0, 2.1], dtype="Float64")
    scalar = stress_exposure_scalar(score)
    assert scalar.tolist() == pytest.approx([1.0, 1.0, 1.0, 0.75, 0.5, 0.5])

    dates = pd.date_range("2025-01-01", periods=2, freq="B")
    scalars = pd.DataFrame(
        {
            "signal_date": dates,
            "stress_score": [1.5, 2.5],
            "exposure_scalar": [0.75, 0.5],
        }
    )
    candidates = pd.DataFrame(
        {
            "signal_date": [dates[0], dates[0]],
            "종목코드": ["000001", "000002"],
            "target_weight": [0.5, 0.5],
        }
    )
    targeted = apply_stress_filter_to_weights(candidates, scalars)
    assert targeted["target_weight_before_stress"].tolist() == pytest.approx([0.5, 0.5])
    assert targeted["target_weight"].sum() == pytest.approx(0.75)


def test_stress_filter_uses_only_data_through_signal_date(monkeypatch: pytest.MonkeyPatch) -> None:
    dates = pd.date_range("2025-01-01", periods=12, freq="B")
    aligned = pd.DataFrame(
        {
            "signal_date": dates,
            "vix": [20, 19, 18, 21, 22, 23, 24, 26, 27, 28, 29, 30],
            "dexkous_usdkrw": [1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100, 1110],
        }
    )
    market_breadth = pd.DataFrame(
        {
            "date": dates,
            "cap_weighted_return": [0.01, -0.01, 0.02, -0.02, 0.03, -0.03, 0.01, -0.01, 0.02, -0.02, 0.03, -0.03],
        }
    )

    def fake_align(signal_dates: object, input_dir: str) -> pd.DataFrame:
        wanted = pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()
        return aligned.loc[aligned["signal_date"].isin(wanted)].reset_index(drop=True)

    monkeypatch.setattr("src.features.stress_filter.align_macro_factors_to_korean_signal_dates", fake_align)
    before = stress_filter_scalars(
        dates,
        macro_data_dir="unused",
        market_breadth=market_breadth,
        z_window=3,
        usdkrw_yoy_lookback_days=3,
        kospi_vol_window=3,
    )

    mutated_aligned = aligned.copy()
    mutated_aligned.loc[mutated_aligned["signal_date"].gt(dates[8]), ["vix", "dexkous_usdkrw"]] = 9999.0
    mutated_breadth = market_breadth.copy()
    mutated_breadth.loc[pd.to_datetime(mutated_breadth["date"]).gt(dates[8]), "cap_weighted_return"] = 9.0

    def fake_mutated_align(signal_dates: object, input_dir: str) -> pd.DataFrame:
        wanted = pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()
        return mutated_aligned.loc[mutated_aligned["signal_date"].isin(wanted)].reset_index(drop=True)

    monkeypatch.setattr("src.features.stress_filter.align_macro_factors_to_korean_signal_dates", fake_mutated_align)
    after = stress_filter_scalars(
        dates,
        macro_data_dir="unused",
        market_breadth=mutated_breadth,
        z_window=3,
        usdkrw_yoy_lookback_days=3,
        kospi_vol_window=3,
    )

    columns = ["VIX_z", "USDKRW_z", "KOSPI_vol_z", "stress_score", "exposure_scalar"]
    before_row = before.loc[before["signal_date"].eq(dates[8]), columns].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(dates[8]), columns].reset_index(drop=True)
    pd.testing.assert_frame_equal(before_row, after_row)
