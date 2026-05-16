from __future__ import annotations

import pandas as pd

from src.features.relative_flow import build_relative_flow_features, cross_sectional_std_diagnostic


def _features(signal_date: str = "2025-01-08", *, count: int = 30) -> pd.DataFrame:
    signal_ts = pd.Timestamp(signal_date)
    execution_ts = signal_ts + pd.Timedelta(days=1)
    return pd.DataFrame(
        [
            {
                "날짜": signal_ts,
                "execution_date": execution_ts,
                "signal_date": signal_ts,
                "종목코드": f"{ticker:06d}",
                "fnv_5": float(ticker),
                "inv_5": float(ticker + 100),
                "combined_flow_5": float(ticker + 200),
            }
            for ticker in range(1, count + 1)
        ]
    )


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_relative_flow_features_match_known_cross_sectional_moments() -> None:
    features = _features(count=30)

    result = build_relative_flow_features(features, _universe(features), min_count=30)
    row = result.loc[result["종목코드"].eq("000030")].iloc[0]

    expected_fnv_z = (30.0 - features["fnv_5"].mean()) / features["fnv_5"].std(ddof=1)
    expected_inv_rel = 130.0 - features["inv_5"].median()
    expected_combined_rel = 230.0 - features["combined_flow_5"].median()

    assert row["fnv_5_z"] == expected_fnv_z
    assert row["inv_5_rel"] == expected_inv_rel
    assert row["combined_flow_5_rel"] == expected_combined_rel


def test_relative_flow_features_are_nan_when_universe_smaller_than_min_count() -> None:
    features = _features(count=29)

    result = build_relative_flow_features(features, _universe(features), min_count=30)

    assert result["fnv_5_z"].isna().all()
    assert result["inv_5_rel"].isna().all()


def test_relative_flow_zscores_are_nan_when_cross_sectional_std_is_zero() -> None:
    features = _features(count=30)
    features["fnv_5"] = 1.0

    result = build_relative_flow_features(features, _universe(features), min_count=30)

    assert result["fnv_5_z"].isna().all()
    assert result["fnv_5_rel"].eq(0.0).all()


def test_relative_flow_features_only_populate_rows_in_universe() -> None:
    features = _features(count=31)
    universe = _universe(features).iloc[:30].copy()

    result = build_relative_flow_features(features, universe, min_count=30)

    assert result.loc[result["종목코드"].eq("000031"), "fnv_5_rel"].isna().all()
    assert result.loc[result["종목코드"].eq("000030"), "fnv_5_rel"].notna().all()


def test_relative_flow_cross_sectional_moments_ignore_future_signal_dates() -> None:
    current = _features("2025-01-08", count=30)
    future = _features("2025-01-09", count=30)
    features = pd.concat([current, future], ignore_index=True)
    universe = _universe(features)
    before = build_relative_flow_features(features, universe, min_count=30)
    before_row = before.loc[
        before["signal_date"].eq(pd.Timestamp("2025-01-08")) & before["종목코드"].eq("000030")
    ].iloc[0]

    mutated = features.copy()
    mutated.loc[mutated["signal_date"].eq(pd.Timestamp("2025-01-09")), "fnv_5"] = 999_000.0
    after = build_relative_flow_features(mutated, universe, min_count=30)
    after_row = after.loc[
        after["signal_date"].eq(pd.Timestamp("2025-01-08")) & after["종목코드"].eq("000030")
    ].iloc[0]

    assert after_row["fnv_5_z"] == before_row["fnv_5_z"]
    assert after_row["fnv_5_rel"] == before_row["fnv_5_rel"]


def test_cross_sectional_std_diagnostic_uses_universe_rows() -> None:
    features = _features(count=31)
    universe = _universe(features).iloc[:30].copy()

    result = cross_sectional_std_diagnostic(features, universe)

    assert len(result) == 1
    assert result.loc[0, "universe_count"] == 30
    assert result.loc[0, "fnv_5_std"] == features.iloc[:30]["fnv_5"].std(ddof=1)
