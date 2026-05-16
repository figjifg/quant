from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.macro_factors import FRED_SERIES
from src.features.macro_regime import build_macro_regime_daily, monthly_regime_log, quarterly_regime_log


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


def test_macro_regime_default_preserves_three_signal_columns(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=2,
        vix_short_window=2,
        vix_long_window=3,
    )

    assert "US_2_10_curve_spread" not in regime.columns
    assert "favorable_US_2_10_curve" not in regime.columns


def test_macro_regime_yield_curve_uses_available_observation_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    dgs2 = pd.read_csv(tmp_path / "fred_dgs2.csv")
    dgs10 = pd.read_csv(tmp_path / "fred_dgs10.csv")
    dgs2.loc[dgs2["observation_date"].eq("2025-01-03"), "DGS2"] = 10.0
    dgs10.loc[dgs10["observation_date"].eq("2025-01-03"), "DGS10"] = 1.0
    dgs2.to_csv(tmp_path / "fred_dgs2.csv", index=False)
    dgs10.to_csv(tmp_path / "fred_dgs10.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["US_2_10_curve_spread"] == pytest.approx(0.5)
    assert row["favorable_US_2_10_curve"] == True


def test_macro_regime_yield_curve_formula_and_score(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["US_2_10_curve_spread"] == pytest.approx(row["US_2_10_curve_spread"])
    assert row["US_2_10_curve_spread"] == pytest.approx(4.5 - 4.0)
    assert row["regime_score"] == 2
    assert row["regime_on"] == True


def test_macro_regime_yield_curve_flag_is_independent_of_other_incomplete_windows(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    dates = pd.date_range("2025-01-01", periods=2, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=3,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-02"))].iloc[0]
    assert row["US_2_10_curve_spread"] == pytest.approx(0.5)
    assert row["favorable_US_2_10_curve"] == True
    assert pd.isna(row["regime_score"])
    assert row["regime_on"] == False


def test_macro_regime_usdcny_yoy_uses_available_observation_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    usdcny = pd.read_csv(tmp_path / "fred_dexchus.csv")
    usdcny.loc[usdcny["observation_date"].eq("2025-01-01"), "DEXCHUS"] = 7.5
    usdcny.loc[usdcny["observation_date"].eq("2025-01-02"), "DEXCHUS"] = 7.0
    usdcny.loc[usdcny["observation_date"].eq("2025-01-03"), "DEXCHUS"] = 99.0
    usdcny.to_csv(tmp_path / "fred_dexchus.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve", "usdcny_yoy"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["USDCNY_yoy"] == pytest.approx(7.0 / 7.5 - 1.0)
    assert row["favorable_USDCNY"] == True
    assert row["regime_score"] == 3
    assert row["regime_on"] == True


def test_macro_regime_brent_yoy_uses_available_observation_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=10)
    brent = pd.read_csv(tmp_path / "fred_brent.csv")
    brent.loc[brent["observation_date"].eq("2025-01-01"), "DCOILBRENTEU"] = 100.0
    brent.loc[brent["observation_date"].eq("2025-01-02"), "DCOILBRENTEU"] = 90.0
    brent.loc[brent["observation_date"].eq("2025-01-03"), "DCOILBRENTEU"] = 999.0
    brent.to_csv(tmp_path / "fred_brent.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve", "brent_yoy"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["Brent_yoy"] == pytest.approx(90.0 / 100.0 - 1.0)
    assert row["favorable_Brent"] == True
    assert row["regime_score"] == 3
    assert row["regime_on"] == True
    assert "USDCNY_yoy" not in regime.columns
    assert "favorable_USDCNY" not in regime.columns


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


def test_quarterly_regime_log_selects_last_trading_day_each_quarter() -> None:
    daily = pd.DataFrame(
        {
            "signal_date": pd.to_datetime(
                ["2025-03-28", "2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"]
            ),
            "regime_score": [1, 2, 3, 0, 1],
        }
    )

    quarterly = quarterly_regime_log(daily)

    assert quarterly["signal_date"].tolist() == [
        pd.Timestamp("2025-03-31"),
        pd.Timestamp("2025-06-30"),
    ]
    assert quarterly["regime_score"].tolist() == [2, 0]


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
        "DCOILBRENTEU": [100.0 - index for index in range(periods)],
        "DEXKOUS": [1300.0 + index for index in range(periods)],
    }
    for spec in FRED_SERIES:
        pd.DataFrame(
            {
                "observation_date": dates,
                spec.fred_series: values[spec.fred_series],
            }
        ).to_csv(base / spec.filename, index=False)
