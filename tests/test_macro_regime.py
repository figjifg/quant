from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.macro_factors import FRED_SERIES
from src.features.macro_regime import build_macro_regime_daily, monthly_regime_log


def test_macro_regime_uses_only_available_us_observations(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=300)
    dates = pd.date_range("2025-01-01", periods=260, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=2,
        vix_short_window=2,
        vix_long_window=3,
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["USDKRW_yoy"] == pytest.approx(1303.0 / 1301.0 - 1.0)
    assert row["DXY_yoy"] == pytest.approx(102.0 / 100.0 - 1.0)
    assert row["VIX_60d_avg"] == (11.0 + 12.0) / 2.0
    assert row["VIX_240d_avg"] == (10.0 + 11.0 + 12.0) / 3.0


def test_macro_regime_score_requires_complete_windows(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=3,
        vix_short_window=2,
        vix_long_window=3,
    )

    assert pd.isna(regime.loc[0, "regime_score"])
    assert regime.loc[0, "regime_on"] == False
    assert not pd.isna(regime.loc[3, "regime_score"])


def test_macro_regime_carries_short_fred_holiday_gap(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    path = tmp_path / "fred_vix.csv"
    frame = pd.read_csv(path, dtype={"VIXCLS": "object"})
    frame.loc[2, "VIXCLS"] = "."
    frame.to_csv(path, index=False)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=2,
        vix_short_window=2,
        vix_long_window=3,
    )

    assert regime.loc[2, "VIX_60d_avg"] == pytest.approx((11.0 + 11.0) / 2.0)


def test_monthly_regime_log_selects_last_trading_day_each_month() -> None:
    daily = pd.DataFrame(
        {
            "signal_date": pd.to_datetime(["2025-01-02", "2025-01-31", "2025-02-03", "2025-02-28"]),
            "regime_score": [1, 2, 3, 0],
        }
    )

    monthly = monthly_regime_log(daily)

    assert monthly["signal_date"].tolist() == [pd.Timestamp("2025-01-31"), pd.Timestamp("2025-02-28")]
    assert monthly["regime_score"].tolist() == [2, 0]


def _write_macro_files(base: Path, *, periods: int) -> None:
    dates = pd.date_range("2024-12-31", periods=periods, freq="B")
    values = {
        "VIXCLS": [10.0 + index for index in range(periods)],
        "DTWEXBGS": [100.0 + index for index in range(periods)],
        "DGS2": [4.0] * periods,
        "DGS10": [4.5] * periods,
        "DEXCHUS": [7.2] * periods,
        "BAA10Y": [2.0] * periods,
        "DGS3MO": [5.0] * periods,
        "DEXKOUS": [1300.0 + index for index in range(periods)],
    }
    for spec in FRED_SERIES:
        pd.DataFrame(
            {
                "observation_date": dates,
                spec.fred_series: values[spec.fred_series],
            }
        ).to_csv(base / spec.filename, index=False)
