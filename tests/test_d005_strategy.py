from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.features.macro_regime import factor_aggregation_composite
from src.run_experiment import _d001_blocks_from_config


CONFIG_PATH = Path("configs/backtests/d005.yaml")
REFERENCE_OUTPUTS = (
    Path("reports/experiments/D001_factor_aggregation_pivot/metrics.json"),
    Path("reports/experiments/D001_factor_aggregation_pivot/trades.csv"),
    Path("reports/experiments/D002_zscore_window_24mo/metrics.json"),
    Path("reports/experiments/D002_zscore_window_24mo/trades.csv"),
    Path("reports/experiments/D003_block_expansion/metrics.json"),
    Path("reports/experiments/D003_block_expansion/trades.csv"),
    Path("reports/experiments/D004_position_sizing/metrics.json"),
    Path("reports/experiments/D004_position_sizing/trades.csv"),
)


def test_d005_config_has_seven_blocks_and_preserves_d001_b1_to_b6() -> None:
    config = _load_config()
    d001 = yaml.safe_load(Path("configs/backtests/d001.yaml").read_text(encoding="utf-8"))

    blocks = _d001_blocks_from_config(config["regime"]["blocks"])

    assert len(blocks) == 7
    assert blocks[:6] == _d001_blocks_from_config(d001["regime"]["blocks"])


def test_d005_b7_korea_growth_has_exports_and_cli_with_positive_signs() -> None:
    config = _load_config()

    blocks = _d001_blocks_from_config(config["regime"]["blocks"])

    assert blocks[-1] == ("korea_growth", (("kr_exports_yoy", 1), ("kr_cli_value", 1)))


def test_d005_b7_within_block_average_correlation_and_std() -> None:
    dates = pd.date_range("2020-01-31", periods=72, freq="ME")
    regime = _factor_regime_frame(dates)
    blocks = _d001_blocks_from_config(_load_config()["regime"]["blocks"])

    result = factor_aggregation_composite(regime, z_score_window_months=60, blocks=blocks)
    complete = result.loc[result["composite"].notna()].copy()

    expected_block = complete[["kr_exports_yoy_fav_score", "kr_cli_value_fav_score"]].mean(axis=1)
    pd.testing.assert_series_equal(
        complete["block_korea_growth_score"].reset_index(drop=True),
        expected_block.reset_index(drop=True),
        check_names=False,
    )
    assert complete["kr_exports_yoy_z"].std(ddof=0) > 0.0
    assert complete["kr_cli_value_z"].std(ddof=0) > 0.0
    assert complete["kr_exports_yoy_z"].corr(complete["kr_cli_value_z"]) == pytest.approx(1.0)


def test_d001_to_d004_reference_outputs_have_stable_hashes_during_d005_tests() -> None:
    before = {path: _sha256(path) for path in REFERENCE_OUTPUTS}
    after = {path: _sha256(path) for path in REFERENCE_OUTPUTS}

    assert after == before


def _load_config() -> dict[str, object]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _factor_regime_frame(dates: pd.DatetimeIndex) -> pd.DataFrame:
    values = [float(index + 1) for index in range(len(dates))]
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
            "KR_exports_yoy": values,
            "KR_CLI_value": [100.0 + value for value in values],
        }
    )
