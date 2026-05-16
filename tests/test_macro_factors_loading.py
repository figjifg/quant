from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.macro_factors import (
    FRED_SERIES,
    align_macro_factors_to_korean_signal_dates,
    build_macro_factor_changes,
    load_all_fred_series,
    load_fred_series,
)


MACRO_DIR = Path("research_input_data/inputs/macro_features")


def test_all_registered_fred_series_load_from_input_directory() -> None:
    loaded = load_all_fred_series(MACRO_DIR)

    assert set(loaded) == {spec.name for spec in FRED_SERIES}
    for spec in FRED_SERIES:
        frame = loaded[spec.name]
        assert list(frame.columns) == ["observation_date", spec.name]
        assert frame["observation_date"].is_monotonic_increasing
        assert frame["observation_date"].duplicated().sum() == 0
        assert frame[spec.name].notna().sum() > 0


def test_brent_fred_series_is_registered_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["brent"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "DCOILBRENTEU"
    assert spec.filename == "fred_brent.csv"
    assert list(frame.columns) == ["observation_date", "brent"]
    assert frame["brent"].notna().sum() > 0


def test_copper_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["copper"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "PCOPPUSDM"
    assert spec.filename == "fred_copper.csv"
    assert spec.frequency == "monthly"
    assert list(frame.columns) == ["observation_date", "copper"]
    assert frame["copper"].notna().sum() > 0


def test_kr10y_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["kr10y"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "IRLTLT01KRM156N"
    assert spec.filename == "fred_kr10y.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "diff"
    assert list(frame.columns) == ["observation_date", "kr10y"]
    assert frame["kr10y"].notna().sum() > 0


def test_kr3m_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["kr3m"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "IR3TIB01KRM156N"
    assert spec.filename == "fred_kr3m.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "diff"
    assert list(frame.columns) == ["observation_date", "kr3m"]
    assert frame["kr3m"].notna().sum() > 0


def test_us_cpi_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["us_cpi"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "CPIAUCSL"
    assert spec.filename == "fred_us_cpi.csv"
    assert spec.frequency == "monthly"
    assert list(frame.columns) == ["observation_date", "us_cpi"]
    assert frame["us_cpi"].notna().sum() > 0


def test_us_ppi_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["us_ppi"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "PPIACO"
    assert spec.filename == "fred_us_ppi.csv"
    assert spec.frequency == "monthly"
    assert list(frame.columns) == ["observation_date", "us_ppi"]
    assert frame["us_ppi"].notna().sum() > 0


def test_us_unrate_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["us_unrate"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "UNRATE"
    assert spec.filename == "fred_us_unrate.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "diff"
    assert list(frame.columns) == ["observation_date", "us_unrate"]
    assert frame["us_unrate"].notna().sum() > 0


def test_us_m2_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["us_m2"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "M2SL"
    assert spec.filename == "fred_us_m2.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "pct_change"
    assert list(frame.columns) == ["observation_date", "us_m2"]
    assert frame["us_m2"].notna().sum() > 0


def test_usdjpy_fred_series_is_registered_as_daily_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["usdjpy"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "DEXJPUS"
    assert spec.filename == "fred_jpy.csv"
    assert spec.frequency == "daily"
    assert spec.transform == "pct_change"
    assert list(frame.columns) == ["observation_date", "usdjpy"]
    assert frame["usdjpy"].notna().sum() > 0


def test_kr_cpi_fred_series_is_registered_as_monthly_yoy_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["kr_cpi"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "KORCPALTT01CTGYM"
    assert spec.filename == "fred_kr_cpi.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "diff"
    assert list(frame.columns) == ["observation_date", "kr_cpi"]
    assert frame["kr_cpi"].notna().sum() > 0


def test_kr_exports_fred_series_is_registered_as_monthly_and_loads() -> None:
    specs = {spec.name: spec for spec in FRED_SERIES}
    spec = specs["kr_exports"]

    frame = load_fred_series(MACRO_DIR / spec.filename, spec)

    assert spec.fred_series == "XTEXVA01KRM664S"
    assert spec.filename == "fred_kr_exports.csv"
    assert spec.frequency == "monthly"
    assert spec.transform == "pct_change"
    assert list(frame.columns) == ["observation_date", "kr_exports"]
    assert frame["kr_exports"].notna().sum() > 0


def test_load_fred_series_rejects_missing_value_column(tmp_path: Path) -> None:
    path = tmp_path / "fred_vix.csv"
    path.write_text("observation_date,WRONG\n2025-01-02,10.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required FRED columns"):
        load_fred_series(path, FRED_SERIES[0])


def test_us_after_close_series_use_prior_observation_date(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    signal_dates = pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    assert aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-01-03")), "vix"].item() == 10.0
    assert aligned.loc[
        aligned["signal_date"].eq(pd.Timestamp("2025-01-03")),
        "vix_source_observation_date",
    ].item() == pd.Timestamp("2025-01-02")
    assert aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-01-06")), "vix"].item() == 11.0
    assert aligned.loc[
        aligned["signal_date"].eq(pd.Timestamp("2025-01-06")),
        "vix_source_observation_date",
    ].item() == pd.Timestamp("2025-01-03")


def test_usdkrw_uses_same_korean_signal_date(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    signal_dates = pd.to_datetime(["2025-01-02", "2025-01-03"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    assert aligned.loc[
        aligned["signal_date"].eq(pd.Timestamp("2025-01-03")), "dexkous_usdkrw"
    ].item() == 1470.0
    assert aligned.loc[
        aligned["signal_date"].eq(pd.Timestamp("2025-01-03")),
        "dexkous_usdkrw_source_observation_date",
    ].item() == pd.Timestamp("2025-01-03")


def test_monthly_us_cpi_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    cpi = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "CPIAUCSL": [300.0, 301.0, 999.0],
        }
    )
    cpi.to_csv(tmp_path / "fred_us_cpi.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["us_cpi"] == 301.0
    assert march_end["us_cpi_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["us_cpi"] == 999.0
    assert april_release["us_cpi_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_monthly_us_ppi_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    ppi = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "PPIACO": [250.0, 251.0, 999.0],
        }
    )
    ppi.to_csv(tmp_path / "fred_us_ppi.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["us_ppi"] == 251.0
    assert march_end["us_ppi_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["us_ppi"] == 999.0
    assert april_release["us_ppi_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_monthly_us_unrate_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    unrate = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "UNRATE": [4.0, 4.1, 9.9],
        }
    )
    unrate.to_csv(tmp_path / "fred_us_unrate.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["us_unrate"] == 4.1
    assert march_end["us_unrate_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["us_unrate"] == 9.9
    assert april_release["us_unrate_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_monthly_us_m2_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    m2 = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "M2SL": [21000.0, 21100.0, 99999.0],
        }
    )
    m2.to_csv(tmp_path / "fred_us_m2.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["us_m2"] == 21100.0
    assert march_end["us_m2_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["us_m2"] == 99999.0
    assert april_release["us_m2_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_monthly_kr_cpi_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    kr_cpi = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "KORCPALTT01CTGYM": [2.0, 2.1, 9.9],
        }
    )
    kr_cpi.to_csv(tmp_path / "fred_kr_cpi.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["kr_cpi"] == 2.1
    assert march_end["kr_cpi_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["kr_cpi"] == 9.9
    assert april_release["kr_cpi_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_monthly_kr_exports_uses_post_month_end_lag_without_lookahead(tmp_path: Path) -> None:
    _write_minimal_macro_files(tmp_path)
    kr_exports = pd.DataFrame(
        {
            "observation_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "XTEXVA01KRM664S": [100.0, 101.0, 999.0],
        }
    )
    kr_exports.to_csv(tmp_path / "fred_kr_exports.csv", index=False)
    signal_dates = pd.to_datetime(["2025-03-31", "2025-04-14"])

    aligned = align_macro_factors_to_korean_signal_dates(signal_dates, tmp_path)

    march_end = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-03-31"))].iloc[0]
    april_release = aligned.loc[aligned["signal_date"].eq(pd.Timestamp("2025-04-14"))].iloc[0]
    assert march_end["kr_exports"] == 101.0
    assert march_end["kr_exports_source_observation_date"] == pd.Timestamp("2025-02-01")
    assert april_release["kr_exports"] == 999.0
    assert april_release["kr_exports_source_observation_date"] == pd.Timestamp("2025-03-01")


def test_build_macro_factor_changes_uses_no_forward_fill() -> None:
    aligned = pd.DataFrame({"signal_date": pd.date_range("2025-01-02", periods=3, freq="B")})
    for spec in FRED_SERIES:
        aligned[spec.name] = [1.0, pd.NA, 4.0]

    changes = build_macro_factor_changes(aligned)

    assert pd.isna(changes.loc[1, "vix_ret"])
    assert pd.isna(changes.loc[2, "vix_ret"])
    assert pd.isna(changes.loc[1, "dgs3mo_diff"])
    assert pd.isna(changes.loc[2, "dgs3mo_diff"])


def _write_minimal_macro_files(base: Path) -> None:
    values = {
        "VIXCLS": [10.0, 11.0],
        "DTWEXBGS": [100.0, 101.0],
        "DEXJPUS": [150.0, 151.0],
        "DGS2": [4.0, 4.1],
        "DGS10": [4.5, 4.6],
        "DEXCHUS": [7.2, 7.3],
        "BAA10Y": [2.0, 2.1],
        "DGS3MO": [5.0, 5.1],
        "DCOILBRENTEU": [80.0, 81.0],
        "PCOPPUSDM": [9000.0, 9100.0],
        "IRLTLT01KRM156N": [3.5, 3.4],
        "IR3TIB01KRM156N": [3.0, 2.9],
        "CPIAUCSL": [300.0, 301.0],
        "PPIACO": [250.0, 251.0],
        "UNRATE": [4.0, 4.1],
        "M2SL": [21000.0, 21100.0],
        "KORCPALTT01CTGYM": [2.0, 2.1],
        "XTEXVA01KRM664S": [100.0, 101.0],
        "DEXKOUS": [1460.0, 1470.0],
    }
    for spec in FRED_SERIES:
        pd.DataFrame(
            {
                "observation_date": ["2025-01-02", "2025-01-03"],
                spec.fred_series: values[spec.fred_series],
            }
        ).to_csv(base / spec.filename, index=False)
