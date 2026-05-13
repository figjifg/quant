from __future__ import annotations

import pandas as pd
import pytest

from src.strategies.a004_strength_quintile import (
    build_e004_quintile_membership,
    build_e004_top_quintile_candidates,
)


def _features_for_day(signal_date: str, execution_date: str, values: list[float]) -> pd.DataFrame:
    rows = []
    for index, combined_flow in enumerate(values, start=1):
        rows.append(
            {
                "execution_date": pd.Timestamp(execution_date),
                "signal_date": pd.Timestamp(signal_date),
                "종목코드": f"{index:06d}",
                "fnv_5": 0.01,
                "inv_5": 0.01,
                "combined_flow_5": combined_flow,
            }
        )
    return pd.DataFrame(rows)


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_top_quintile_returns_top_20_percent_when_universe_large() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])

    result = build_e004_top_quintile_candidates(features, _universe(features))

    assert list(result["종목코드"]) == ["000025", "000024", "000023", "000022", "000021"]


def test_safety_filter_drops_negative_components_after_quintile_selection() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])
    features.loc[features["종목코드"].eq("000025"), "inv_5"] = -0.01

    result = build_e004_top_quintile_candidates(features, _universe(features))

    assert list(result["종목코드"]) == ["000024", "000023", "000022", "000021"]
    assert "000020" not in set(result["종목코드"])


def test_insufficient_universe_returns_no_candidates_that_day() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(15)])

    result = build_e004_top_quintile_candidates(features, _universe(features))

    assert result.empty


def test_nan_combined_flow_excluded_from_quintile() -> None:
    values = [float(value) for value in range(25)]
    features = _features_for_day("2025-01-06", "2025-01-07", values)
    features.loc[features["종목코드"].eq("000025"), "combined_flow_5"] = pd.NA

    result = build_e004_top_quintile_candidates(features, _universe(features))

    assert "000025" not in set(result["종목코드"])
    assert list(result["종목코드"]) == ["000024", "000023", "000022", "000021", "000020"]


def test_quintile_membership_is_per_signal_date_independent() -> None:
    day_1 = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])
    day_2 = _features_for_day("2025-01-07", "2025-01-08", [100.0 + float(value) for value in range(25)])
    features = pd.concat([day_1, day_2], ignore_index=True)

    result = build_e004_top_quintile_candidates(features, _universe(features))
    by_date = {
        date: list(group["종목코드"])
        for date, group in result.groupby("signal_date", sort=True)
    }

    assert by_date[pd.Timestamp("2025-01-06")] == ["000025", "000024", "000023", "000022", "000021"]
    assert by_date[pd.Timestamp("2025-01-07")] == ["000025", "000024", "000023", "000022", "000021"]


def test_bottom_quintile_returns_bottom_20_percent() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])

    result = build_e004_top_quintile_candidates(features, _universe(features), quintile_value=1)

    assert list(result["종목코드"]) == ["000005", "000004", "000003", "000002", "000001"]


def test_quintile_labels_are_monotonic() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])

    labeled = build_e004_quintile_membership(features, _universe(features))
    by_ticker = labeled.set_index("종목코드")["quantile_label"]

    assert by_ticker["000001"] == 1
    assert by_ticker["000005"] == 1
    assert by_ticker["000006"] == 2
    assert by_ticker["000025"] == 5


def test_invalid_quintile_raises() -> None:
    features = _features_for_day("2025-01-06", "2025-01-07", [float(value) for value in range(25)])

    with pytest.raises(ValueError, match="quintile_value"):
        build_e004_top_quintile_candidates(features, _universe(features), quintile_value=6)
