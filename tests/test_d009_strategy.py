from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.data.macro_factors import FRED_SERIES
from src.features.macro_regime import D009_SIGNAL_NAMES, build_macro_regime_daily, factor_aggregation_composite
from src.run_experiment import _d001_blocks_from_config


CONFIG_PATH = Path("configs/backtests/d009.yaml")
STRATEGY_HASHES = {
    Path("src/strategies/d001_factor_aggregation.py"): "1513e2a285cc3744147f7c85220b965314602501d5f74244beabe79aa6d616df",
    Path("src/strategies/d002_zscore_24mo.py"): "d377f884d47cb1ea7fdeceac6a502572270da93ce323e02a7575c254c725807e",
    Path("src/strategies/d003_block_expansion.py"): "5960bc4a7309d5d85e02266e5963a5a662d8209b5ffd9077c2f81c730bd66b13",
    Path("src/strategies/d004_position_sizing.py"): "45a2b1243ab79f33424265069ff69f37053d379986de4839e51ad9852e6cabac",
    Path("src/strategies/d005_korea_growth.py"): "74ef73182994965c71e354868c402ff8b960aa2d81af1ba86144c0d0b98b1e66",
    Path("src/strategies/d006_window_grid.py"): "0243f7c1e2cda59237d7a8f197b5c032594d8565d086f29db05d0b770cf868e1",
    Path("src/strategies/d007_threshold_grid.py"): "dd6ceb9fce162c39e92f1d434b2fc5055fbc5616a61b99911add2f926b58e072",
    Path("src/strategies/d008_subperiod_analysis.py"): "b3ddd7697c7552bc096dcf2883f4d8f3987a83587e9ad3fe73c34f6a1f60b258",
}


def test_d009_config_has_five_two_variable_blocks() -> None:
    blocks = _d001_blocks_from_config(_load_config()["regime"]["blocks"])

    assert len(blocks) == 5
    assert all(len(variables) == 2 for _, variables in blocks)


def test_d009_sign_conventions_match_ticket() -> None:
    blocks = _d001_blocks_from_config(_load_config()["regime"]["blocks"])

    assert blocks == (
        ("global_risk", (("vix_60d_vs_240d", -1), ("baa10y_spread_level", -1))),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_10y_real_level", -1), ("us_2_10_curve", 1))),
        ("inflation", (("brent_yoy", -1), ("us_breakeven_level", -1))),
        ("growth", (("kr_cli_value", 1), ("kr_exports_yoy", 1))),
    )


def test_d009_factor_zscore_at_trade_quarter_uses_no_future_rows() -> None:
    dates = pd.date_range("2010-01-31", periods=62, freq="ME")
    before = _factor_regime_frame(dates)
    after = before.copy()
    after.loc[61, after.columns.difference(["signal_date"])] = 9999.0
    blocks = _d001_blocks_from_config(_load_config()["regime"]["blocks"])

    before_result = factor_aggregation_composite(before, z_score_window_months=60, blocks=blocks)
    after_result = factor_aggregation_composite(after, z_score_window_months=60, blocks=blocks)

    columns = [column for column in before_result.columns if column.endswith("_z") or column.startswith("block_")]
    columns.extend(["composite", "regime_on"])
    pd.testing.assert_series_equal(before_result.loc[60, columns], after_result.loc[60, columns])


def test_d009_raw_us_level_inputs_use_prior_us_observation_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    for filename, column in (
        ("fred_baa10y_spread.csv", "BAA10Y"),
        ("fred_us_10y_real.csv", "DFII10"),
        ("fred_us_breakeven_10y.csv", "T10YIE"),
    ):
        data = pd.read_csv(tmp_path / filename)
        data.loc[data["observation_date"].eq("2025-01-03"), column] = 999.0
        data.to_csv(tmp_path / filename, index=False)

    regime = build_macro_regime_daily(
        pd.date_range("2025-01-01", periods=4, freq="B"),
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=D009_SIGNAL_NAMES,
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["BAA10Y_spread_level"] == pytest.approx(2.2)
    assert row["US_10Y_real_level"] == pytest.approx(1.7)
    assert row["US_breakeven_level"] == pytest.approx(2.5)


def test_d001_to_d008_strategy_modules_are_byte_identical() -> None:
    observed = {path: _sha256(path) for path in STRATEGY_HASHES}

    assert observed == STRATEGY_HASHES


def _load_config() -> dict[str, object]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _factor_regime_frame(dates: pd.DatetimeIndex) -> pd.DataFrame:
    base = pd.Series(range(1, len(dates) + 1), dtype="float64")
    reverse = base.iloc[::-1].reset_index(drop=True)
    return pd.DataFrame(
        {
            "signal_date": dates,
            "USDKRW_yoy": base,
            "VIX_60d_avg": base,
            "VIX_240d_avg": [1.0] * len(dates),
            "DXY_yoy": reverse,
            "US_2_10_curve_spread": base + 0.1,
            "Brent_yoy": reverse + 0.2,
            "BAA10Y_spread_level": base + 0.3,
            "US_10Y_real_level": reverse + 0.4,
            "US_breakeven_level": base + 0.5,
            "KR_exports_yoy": reverse + 0.6,
            "KR_CLI_value": base + 100.0,
        }
    )


def _write_macro_files(base: Path, *, periods: int) -> None:
    dates = pd.date_range("2024-12-31", periods=periods, freq="B")
    values = {
        "VIXCLS": [10.0 + index for index in range(periods)],
        "DTWEXBGS": [100.0 + index for index in range(periods)],
        "DEXJPUS": [150.0 + index for index in range(periods)],
        "DGS2": [4.0] * periods,
        "DGS10": [4.5] * periods,
        "DEXCHUS": [7.2] * periods,
        "BAA10Y": [2.0 + index * 0.1 for index in range(periods)],
        "DFII10": [1.5 + index * 0.1 for index in range(periods)],
        "T10YIE": [2.3 + index * 0.1 for index in range(periods)],
        "DGS3MO": [5.0] * periods,
        "DCOILBRENTEU": [100.0 - index for index in range(periods)],
        "PCOPPUSDM": [9000.0 + index for index in range(periods)],
        "IRLTLT01KRM156N": [3.5 - index * 0.01 for index in range(periods)],
        "IRLTLT01JPM156N": [0.8 - index * 0.001 for index in range(periods)],
        "IR3TIB01KRM156N": [3.0 - index * 0.01 for index in range(periods)],
        "CPIAUCSL": [300.0 + index for index in range(periods)],
        "PPIACO": [250.0 + index for index in range(periods)],
        "UNRATE": [4.0 + index * 0.01 for index in range(periods)],
        "M2SL": [21000.0 + index for index in range(periods)],
        "KORCPALTT01CTGYM": [2.0 + index * 0.01 for index in range(periods)],
        "XTEXVA01KRM664S": [100.0 + index for index in range(periods)],
        "KORLOLITOAASTSAM": [99.0 + index * 0.01 for index in range(periods)],
        "DEXKOUS": [1300.0 + index for index in range(periods)],
    }
    for spec in FRED_SERIES:
        pd.DataFrame(
            {
                "observation_date": dates,
                spec.fred_series: values[spec.fred_series],
            }
        ).to_csv(base / spec.filename, index=False)
