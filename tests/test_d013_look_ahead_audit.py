from __future__ import annotations

import pandas as pd

from src.data.macro_factors import align_macro_factors_to_korean_signal_dates


def test_d013_cli_and_exports_monthly_availability_rules() -> None:
    regime = pd.read_csv(
        "reports/experiments/D013_d009_threshold_minus_0p2/quarterly_regime_log.csv",
        parse_dates=["signal_date"],
    )
    aligned = align_macro_factors_to_korean_signal_dates(
        regime["signal_date"],
        input_dir="research_input_data/inputs/macro_features",
    )

    cli_source = pd.to_datetime(aligned["kr_cli_source_observation_date"]).dropna()
    cli_signals = aligned.loc[cli_source.index, "signal_date"]
    exports_source = pd.to_datetime(aligned["kr_exports_source_observation_date"]).dropna()
    exports_signals = aligned.loc[exports_source.index, "signal_date"]

    assert not cli_source.empty
    assert not exports_source.empty
    assert (cli_source + pd.offsets.MonthEnd(0) + pd.Timedelta(days=75)).le(cli_signals).all()
    assert (exports_source + pd.offsets.MonthEnd(0) + pd.Timedelta(days=14)).le(exports_signals).all()


def test_d013_daily_macro_sources_are_available_to_signal_date() -> None:
    regime = pd.read_csv(
        "reports/experiments/D013_d009_threshold_minus_0p2/quarterly_regime_log.csv",
        parse_dates=["signal_date"],
    )
    aligned = align_macro_factors_to_korean_signal_dates(
        regime["signal_date"],
        input_dir="research_input_data/inputs/macro_features",
    )

    us_after_close = [
        "vix",
        "dxy",
        "dgs2",
        "dgs10",
        "baa10y_spread",
        "us_10y_real",
        "us_breakeven_10y",
        "brent",
    ]
    for name in us_after_close:
        source = pd.to_datetime(aligned[f"{name}_source_observation_date"]).dropna()
        signals = aligned.loc[source.index, "signal_date"]
        assert source.le(signals - pd.Timedelta(days=1)).all()

    usdkrw_source = pd.to_datetime(aligned["dexkous_usdkrw_source_observation_date"]).dropna()
    usdkrw_signals = aligned.loc[usdkrw_source.index, "signal_date"]
    assert usdkrw_source.le(usdkrw_signals).all()
