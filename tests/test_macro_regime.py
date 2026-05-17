from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.macro_factors import FRED_SERIES
from src.features.macro_regime import (
    build_macro_regime_daily,
    factor_aggregation_composite,
    monthly_regime_log,
    quarterly_regime_log,
)


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


def test_macro_regime_copper_yoy_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    copper = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01", "2026-04-01"],
            "PCOPPUSDM": [100.0, 125.0, 999.0],
        }
    )
    copper.to_csv(tmp_path / "fred_copper.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve", "brent_yoy", "copper_yoy"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["Copper_yoy"] == pytest.approx(125.0 / 100.0 - 1.0)
    assert row["favorable_Copper"] == True
    assert row["regime_score"] == 4
    assert row["regime_on"] == True
    assert "USDCNY_yoy" not in regime.columns
    assert "favorable_USDCNY" not in regime.columns


def test_macro_regime_copper_unfavorable_when_yoy_is_not_positive(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    copper = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "PCOPPUSDM": [100.0, 95.0],
        }
    )
    copper.to_csv(tmp_path / "fred_copper.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=["usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve", "brent_yoy", "copper_yoy"],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["Copper_yoy"] == pytest.approx(95.0 / 100.0 - 1.0)
    assert row["favorable_Copper"] == False


def test_macro_regime_kr10y_yoy_change_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    kr10y = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01", "2026-04-01"],
            "IRLTLT01KRM156N": [3.50, 3.00, 9.99],
        }
    )
    kr10y.to_csv(tmp_path / "fred_kr10y.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["KR10Y_yoy_change"] == pytest.approx(-0.50)
    assert row["KR10Y_yoy_change"] != pytest.approx(3.00 / 3.50 - 1.0)
    assert row["favorable_KR10Y"] == True
    assert row["regime_score"] == 4
    assert row["regime_on"] == True
    assert "Copper_yoy" not in regime.columns
    assert "favorable_Copper" not in regime.columns


def test_macro_regime_kr10y_unfavorable_when_yield_change_is_positive(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    kr10y = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "IRLTLT01KRM156N": [3.00, 3.25],
        }
    )
    kr10y.to_csv(tmp_path / "fred_kr10y.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["KR10Y_yoy_change"] == pytest.approx(0.25)
    assert row["favorable_KR10Y"] == False


def test_macro_regime_kr3m_yoy_change_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    kr3m = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01", "2026-04-01"],
            "IR3TIB01KRM156N": [3.25, 2.75, 9.99],
        }
    )
    kr3m.to_csv(tmp_path / "fred_kr3m.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "kr3m_yoy_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["KR3M_yoy_change"] == pytest.approx(-0.50)
    assert row["KR3M_yoy_change"] != pytest.approx(2.75 / 3.25 - 1.0)
    assert row["favorable_KR3M"] == True
    assert row["regime_score"] == 5
    assert row["regime_on"] == True
    assert "Copper_yoy" not in regime.columns
    assert "favorable_Copper" not in regime.columns
    assert "USDCNY_yoy" not in regime.columns


def test_macro_regime_kr3m_unfavorable_when_rate_change_is_positive(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=340)
    kr3m = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "IR3TIB01KRM156N": [3.00, 3.25],
        }
    )
    kr3m.to_csv(tmp_path / "fred_kr3m.csv", index=False)
    dates = pd.to_datetime(["2025-03-28", "2026-03-31"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "kr3m_yoy_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    assert row["KR3M_yoy_change"] == pytest.approx(0.25)
    assert row["favorable_KR3M"] == False


def test_macro_regime_us_cpi_decel_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_cpi = pd.DataFrame(
        {
            "observation_date": ["2024-02-01", "2024-03-01", "2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "CPIAUCSL": [99.0, 100.0, 110.0, 110.0, 121.0, 115.0],
        }
    )
    us_cpi.to_csv(tmp_path / "fred_us_cpi.csv", index=False)
    dates = pd.to_datetime(["2024-03-14", "2024-04-14", "2025-03-14", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["US_CPI_yoy"] == pytest.approx(121.0 / 110.0 - 1.0)
    assert april_release["US_CPI_yoy"] == pytest.approx(115.0 / 110.0 - 1.0)
    assert april_release["US_CPI_decel"] == pytest.approx((115.0 / 110.0 - 1.0) - (110.0 / 100.0 - 1.0))
    assert april_release["favorable_US_CPI"] == True
    assert april_release["regime_on"] == True
    assert "KR3M_yoy_change" not in regime.columns
    assert "Copper_yoy" not in regime.columns


def test_macro_regime_us_cpi_unfavorable_when_inflation_accelerates(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_cpi = pd.DataFrame(
        {
            "observation_date": ["2024-03-01", "2025-03-01", "2026-03-01"],
            "CPIAUCSL": [100.0, 102.0, 110.0],
        }
    )
    us_cpi.to_csv(tmp_path / "fred_us_cpi.csv", index=False)
    dates = pd.to_datetime(["2024-04-14", "2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["US_CPI_decel"] == pytest.approx((110.0 / 102.0 - 1.0) - (102.0 / 100.0 - 1.0))
    assert row["favorable_US_CPI"] == False


def test_macro_regime_us_ppi_decel_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_ppi = pd.DataFrame(
        {
            "observation_date": ["2024-02-01", "2024-03-01", "2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "PPIACO": [99.0, 100.0, 110.0, 110.0, 121.0, 115.0],
        }
    )
    us_cpi = pd.DataFrame(
        {
            "observation_date": ["2024-02-01", "2024-03-01", "2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "CPIAUCSL": [199.0, 200.0, 210.0, 210.0, 221.0, 215.0],
        }
    )
    us_ppi.to_csv(tmp_path / "fred_us_ppi.csv", index=False)
    us_cpi.to_csv(tmp_path / "fred_us_cpi.csv", index=False)
    dates = pd.to_datetime(["2024-03-14", "2024-04-14", "2025-03-14", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["US_PPI_yoy"] == pytest.approx(121.0 / 110.0 - 1.0)
    assert april_release["US_PPI_yoy"] == pytest.approx(115.0 / 110.0 - 1.0)
    assert april_release["US_PPI_decel"] == pytest.approx((115.0 / 110.0 - 1.0) - (110.0 / 100.0 - 1.0))
    assert april_release["favorable_US_PPI"] == True
    assert april_release["regime_on"] == True
    assert "KR3M_yoy_change" not in regime.columns
    assert "Copper_yoy" not in regime.columns
    assert "USDCNY_yoy" not in regime.columns


def test_macro_regime_us_ppi_unfavorable_when_inflation_accelerates(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_ppi = pd.DataFrame(
        {
            "observation_date": ["2024-03-01", "2025-03-01", "2026-03-01"],
            "PPIACO": [100.0, 102.0, 110.0],
        }
    )
    us_ppi.to_csv(tmp_path / "fred_us_ppi.csv", index=False)
    dates = pd.to_datetime(["2024-04-14", "2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["US_PPI_decel"] == pytest.approx((110.0 / 102.0 - 1.0) - (102.0 / 100.0 - 1.0))
    assert row["favorable_US_PPI"] == False


def test_factor_aggregation_composite_z_score_signs_and_blocks() -> None:
    dates = pd.date_range("2020-01-31", periods=61, freq="ME")
    regime = _factor_regime_frame(dates, base=1.0)

    result = factor_aggregation_composite(regime, z_score_window_months=60)

    warmup = result.iloc[58]
    row = result.iloc[59]
    expected_z = (60.0 - 30.5) / pd.Series(range(1, 61), dtype="float64").std(ddof=0)
    assert pd.isna(warmup["composite"])
    assert warmup["regime_on"] == False
    assert row["usdkrw_yoy_z"] == pytest.approx(expected_z)
    assert row["usdkrw_yoy_fav_score"] == pytest.approx(-expected_z)
    assert row["us_2_10_curve_fav_score"] == pytest.approx(expected_z)
    assert row["block_usd_fx_score"] == pytest.approx((-expected_z + -expected_z) / 2.0)
    assert row["block_inflation_score"] == pytest.approx((-expected_z + -expected_z) / 2.0)
    assert row["composite"] == pytest.approx((-5.0 * expected_z + expected_z) / 6.0)
    assert row["regime_on"] == False


def test_factor_aggregation_composite_accepts_24_month_window() -> None:
    dates = pd.date_range("2020-01-31", periods=60, freq="ME")
    regime = _factor_regime_frame(dates, base=1.0)

    result_24 = factor_aggregation_composite(regime, z_score_window_months=24)
    result_60 = factor_aggregation_composite(regime, z_score_window_months=60)

    expected_z_24 = (24.0 - 12.5) / pd.Series(range(1, 25), dtype="float64").std(ddof=0)
    assert pd.isna(result_24.loc[22, "composite"])
    assert not pd.isna(result_24.loc[23, "composite"])
    assert result_24.loc[23, "usdkrw_yoy_z"] == pytest.approx(expected_z_24)
    assert pd.isna(result_60.loc[23, "composite"])
    assert result_24.loc[59, "composite"] != pytest.approx(result_60.loc[59, "composite"])


def test_factor_aggregation_composite_zero_std_is_neutral_and_nan_off() -> None:
    dates = pd.date_range("2020-01-31", periods=60, freq="ME")
    regime = _factor_regime_frame(dates, base=1.0)
    for column in (
        "USDKRW_yoy",
        "DXY_yoy",
        "US_2_10_curve_spread",
        "Brent_yoy",
        "KR10Y_yoy_change",
        "US_CPI_decel",
        "US_PPI_decel",
    ):
        regime[column] = 1.0
    regime["VIX_60d_avg"] = 10.0
    regime["VIX_240d_avg"] = 10.0

    result = factor_aggregation_composite(regime, z_score_window_months=60)

    row = result.iloc[-1]
    assert row["composite"] == pytest.approx(0.0)
    assert row["regime_on"] == True


def test_factor_aggregation_composite_uses_no_future_rows() -> None:
    dates = pd.date_range("2020-01-31", periods=61, freq="ME")
    before = _factor_regime_frame(dates, base=1.0)
    after = before.copy()
    signal_columns = [
        "USDKRW_yoy",
        "DXY_yoy",
        "US_2_10_curve_spread",
        "Brent_yoy",
        "KR10Y_yoy_change",
        "US_CPI_decel",
        "US_PPI_decel",
        "VIX_60d_avg",
    ]
    after.loc[60, signal_columns] = 9999.0

    before_result = factor_aggregation_composite(before, z_score_window_months=60)
    after_result = factor_aggregation_composite(after, z_score_window_months=60)

    columns = [column for column in before_result.columns if column.endswith("_z") or column.startswith("block_")]
    columns.append("composite")
    pd.testing.assert_series_equal(before_result.loc[59, columns], after_result.loc[59, columns])


def test_macro_regime_us_m2_yoy_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_m2 = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "M2SL": [20000.0, 21000.0, 21100.0, 22050.0],
        }
    )
    us_m2.to_csv(tmp_path / "fred_us_m2.csv", index=False)
    dates = pd.to_datetime(["2025-03-14", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "us_m2_yoy",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["US_M2_yoy"] == pytest.approx(21100.0 / 20000.0 - 1.0)
    assert april_release["US_M2_yoy"] == pytest.approx(22050.0 / 21000.0 - 1.0)
    assert april_release["favorable_US_M2"] == True
    assert "KR_exports_yoy" not in regime.columns
    assert "favorable_KR_exports" not in regime.columns
    assert "US_UNRATE_yoy_change" not in regime.columns


def test_macro_regime_us_m2_unfavorable_below_five_percent_growth(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_m2 = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "M2SL": [20000.0, 20900.0],
        }
    )
    us_m2.to_csv(tmp_path / "fred_us_m2.csv", index=False)
    dates = pd.to_datetime(["2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "us_m2_yoy",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["US_M2_yoy"] == pytest.approx(20900.0 / 20000.0 - 1.0)
    assert row["favorable_US_M2"] == False


def test_macro_regime_us_unrate_change_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_unrate = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "UNRATE": [4.0, 4.1, 4.4, 4.7],
        }
    )
    us_unrate.to_csv(tmp_path / "fred_us_unrate.csv", index=False)
    dates = pd.to_datetime(["2025-03-14", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "us_unrate_change",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["US_UNRATE_yoy_change"] == pytest.approx(4.4 - 4.0)
    assert april_release["US_UNRATE_yoy_change"] == pytest.approx(4.7 - 4.1)
    assert april_release["favorable_US_UNRATE"] == True
    assert "KR3M_yoy_change" not in regime.columns
    assert "Copper_yoy" not in regime.columns
    assert "USDCNY_yoy" not in regime.columns


def test_macro_regime_us_unrate_unfavorable_when_yoy_change_is_negative(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    us_unrate = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "UNRATE": [4.2, 3.8],
        }
    )
    us_unrate.to_csv(tmp_path / "fred_us_unrate.csv", index=False)
    dates = pd.to_datetime(["2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "us_unrate_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["US_UNRATE_yoy_change"] == pytest.approx(-0.4)
    assert row["favorable_US_UNRATE"] == False


def test_macro_regime_kr_cpi_decel_uses_already_yoy_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    kr_cpi = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01"],
            "KORCPALTT01CTGYM": [3.0, 3.2, 2.8, 2.7],
        }
    )
    kr_cpi.to_csv(tmp_path / "fred_kr_cpi.csv", index=False)
    dates = pd.to_datetime(["2025-03-14", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_cpi_decel",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["KR_CPI_yoy"] == pytest.approx(2.8)
    assert march_end["KR_CPI_decel"] == pytest.approx(2.8 - 3.0)
    assert april_release["KR_CPI_yoy"] == pytest.approx(2.7)
    assert april_release["KR_CPI_decel"] == pytest.approx(2.7 - 3.2)
    assert april_release["favorable_KR_CPI"] == True
    assert "US_UNRATE_yoy_change" not in regime.columns
    assert "favorable_US_UNRATE" not in regime.columns


def test_macro_regime_kr_cpi_unfavorable_when_yoy_accelerates(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=420)
    kr_cpi = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "KORCPALTT01CTGYM": [2.5, 3.0],
        }
    )
    kr_cpi.to_csv(tmp_path / "fred_kr_cpi.csv", index=False)
    dates = pd.to_datetime(["2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_cpi_decel",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["KR_CPI_decel"] == pytest.approx(0.5)
    assert row["favorable_KR_CPI"] == False


def test_macro_regime_kr_cpi_stale_gap_is_false_but_composite_still_counts_other_signals(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=900)
    kr_cpi = pd.DataFrame(
        {
            "observation_date": ["2025-04-01", "2026-04-01"],
            "KORCPALTT01CTGYM": [3.0, 2.0],
        }
    )
    kr_cpi.to_csv(tmp_path / "fred_kr_cpi.csv", index=False)
    dates = pd.to_datetime(["2025-09-30", "2026-05-14", "2026-09-30", "2027-09-30"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_cpi_decel",
        ],
    )

    fresh = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-05-14"))].iloc[0]
    stale = regime.loc[regime["signal_date"].eq(pd.Timestamp("2027-09-30"))].iloc[0]
    assert fresh["KR_CPI_decel"] == pytest.approx(-1.0)
    assert fresh["favorable_KR_CPI"] == True
    assert pd.isna(stale["KR_CPI_decel"])
    assert stale["favorable_KR_CPI"] == False


def test_macro_regime_kr_exports_yoy_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    kr_exports = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01", "2026-04-01"],
            "XTEXVA01KRM664S": [100.0, 100.0, 110.0, 125.0, 999.0],
        }
    )
    kr_exports.to_csv(tmp_path / "fred_kr_exports.csv", index=False)
    pd.DataFrame(
        {
            "observation_date": ["2024-03-01", "2025-03-01", "2026-03-01"],
            "CPIAUCSL": [100.0, 110.0, 120.0],
        }
    ).to_csv(tmp_path / "fred_us_cpi.csv", index=False)
    pd.DataFrame(
        {
            "observation_date": ["2024-03-01", "2025-03-01", "2026-03-01"],
            "PPIACO": [100.0, 110.0, 120.0],
        }
    ).to_csv(tmp_path / "fred_us_ppi.csv", index=False)
    dates = pd.to_datetime(["2024-04-15", "2025-03-14", "2025-04-15", "2026-04-13", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_exports_yoy",
        ],
    )

    before_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-13"))].iloc[0]
    after_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert before_release["KR_exports_yoy"] == pytest.approx(110.0 / 100.0 - 1.0)
    assert after_release["KR_exports_yoy"] == pytest.approx(125.0 / 100.0 - 1.0)
    assert after_release["favorable_KR_exports"] == True
    favorable_columns = [column for column in regime.columns if column.startswith("favorable_")]
    assert after_release["regime_score"] == sum(bool(after_release[column]) for column in favorable_columns)
    assert after_release["regime_on"] == True
    assert "KR_CPI_decel" not in regime.columns
    assert "US_UNRATE_yoy_change" not in regime.columns


def test_macro_regime_kr_exports_unfavorable_when_yoy_is_negative(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    kr_exports = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "XTEXVA01KRM664S": [100.0, 95.0],
        }
    )
    kr_exports.to_csv(tmp_path / "fred_kr_exports.csv", index=False)
    dates = pd.to_datetime(["2025-04-15", "2026-04-15"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_exports_yoy",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-15"))].iloc[0]
    assert row["KR_exports_yoy"] == pytest.approx(95.0 / 100.0 - 1.0)
    assert row["favorable_KR_exports"] == False


def test_macro_regime_kr_cli_value_uses_monthly_level_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    kr_cli = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01", "2026-04-01"],
            "KORLOLITOAASTSAM": [99.0, 100.0, 101.0, 102.0, 999.0],
        }
    )
    kr_cli.to_csv(tmp_path / "fred_kr_cli.csv", index=False)
    dates = pd.to_datetime(["2025-03-31", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "kr_exports_yoy",
            "kr_cli_value",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["KR_CLI_value"] == pytest.approx(101.0)
    assert april_release["KR_CLI_value"] == pytest.approx(102.0)
    assert april_release["favorable_KR_CLI"] == True


def test_macro_regime_usdjpy_yoy_uses_available_observation_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    usdjpy = pd.read_csv(tmp_path / "fred_jpy.csv")
    usdjpy.loc[usdjpy["observation_date"].eq("2025-01-01"), "DEXJPUS"] = 100.0
    usdjpy.loc[usdjpy["observation_date"].eq("2025-01-02"), "DEXJPUS"] = 110.0
    usdjpy.loc[usdjpy["observation_date"].eq("2025-01-03"), "DEXJPUS"] = 999.0
    usdjpy.to_csv(tmp_path / "fred_jpy.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "usdjpy_yoy",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["USDJPY_yoy"] == pytest.approx(110.0 / 100.0 - 1.0)
    assert row["favorable_USDJPY"] == True
    assert "US_M2_yoy" not in regime.columns
    assert "KR_exports_yoy" not in regime.columns


def test_macro_regime_usdjpy_unfavorable_when_yen_strengthens(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    usdjpy = pd.read_csv(tmp_path / "fred_jpy.csv")
    usdjpy.loc[usdjpy["observation_date"].eq("2025-01-01"), "DEXJPUS"] = 100.0
    usdjpy.loc[usdjpy["observation_date"].eq("2025-01-02"), "DEXJPUS"] = 95.0
    usdjpy.to_csv(tmp_path / "fred_jpy.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=3, freq="B")

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "usdjpy_yoy",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert row["USDJPY_yoy"] == pytest.approx(95.0 / 100.0 - 1.0)
    assert row["favorable_USDJPY"] == False


def test_macro_regime_jp10y_yoy_change_uses_monthly_value_without_lookahead(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    jp10y = pd.DataFrame(
        {
            "observation_date": ["2025-02-01", "2025-03-01", "2026-02-01", "2026-03-01", "2026-04-01"],
            "IRLTLT01JPM156N": [0.80, 0.75, 0.60, 0.50, 9.99],
        }
    )
    jp10y.to_csv(tmp_path / "fred_jp10y.csv", index=False)
    dates = pd.to_datetime(["2025-03-31", "2025-04-14", "2026-03-31", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "jp10y_yoy_change",
        ],
    )

    march_end = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-03-31"))].iloc[0]
    april_release = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert march_end["JP10Y_yoy_change"] == pytest.approx(-0.20)
    assert april_release["JP10Y_yoy_change"] == pytest.approx(-0.25)
    assert april_release["JP10Y_yoy_change"] != pytest.approx(0.50 / 0.75 - 1.0)
    assert april_release["favorable_JP10Y"] == True
    assert "USDJPY_yoy" in regime.columns
    assert "favorable_USDJPY" not in regime.columns
    assert "US_M2_yoy" not in regime.columns


def test_macro_regime_jp10y_unfavorable_when_yield_change_is_positive(tmp_path: Path) -> None:
    _write_macro_files(tmp_path, periods=520)
    jp10y = pd.DataFrame(
        {
            "observation_date": ["2025-03-01", "2026-03-01"],
            "IRLTLT01JPM156N": [0.50, 1.25],
        }
    )
    jp10y.to_csv(tmp_path / "fred_jp10y.csv", index=False)
    dates = pd.to_datetime(["2025-04-14", "2026-04-14"])

    regime = build_macro_regime_daily(
        dates,
        macro_data_dir=str(tmp_path),
        yoy_lookback=1,
        vix_short_window=1,
        vix_long_window=1,
        macro_signals=[
            "usdkrw_yoy",
            "vix_60d_vs_240d",
            "dxy_yoy",
            "us_2_10_curve",
            "brent_yoy",
            "kr10y_yoy_change",
            "us_cpi_decel",
            "us_ppi_decel",
            "jp10y_yoy_change",
        ],
    )

    row = regime.loc[regime["signal_date"].eq(pd.Timestamp("2026-04-14"))].iloc[0]
    assert row["JP10Y_yoy_change"] == pytest.approx(0.75)
    assert row["favorable_JP10Y"] == False


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


def _factor_regime_frame(dates: pd.DatetimeIndex, *, base: float) -> pd.DataFrame:
    values = [base + index for index in range(len(dates))]
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
        "BAA10Y": [2.0] * periods,
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
