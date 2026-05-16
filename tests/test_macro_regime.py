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
        "PCOPPUSDM": [9000.0 + index for index in range(periods)],
        "IRLTLT01KRM156N": [3.5 - index * 0.01 for index in range(periods)],
        "IR3TIB01KRM156N": [3.0 - index * 0.01 for index in range(periods)],
        "CPIAUCSL": [300.0 + index for index in range(periods)],
        "PPIACO": [250.0 + index for index in range(periods)],
        "DEXKOUS": [1300.0 + index for index in range(periods)],
    }
    for spec in FRED_SERIES:
        pd.DataFrame(
            {
                "observation_date": dates,
                spec.fred_series: values[spec.fred_series],
            }
        ).to_csv(base / spec.filename, index=False)
