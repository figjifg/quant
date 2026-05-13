from __future__ import annotations

import pandas as pd

from src.roles.filters import filter_flow_sign_both_positive
from src.roles.triggers import trigger_acceleration, trigger_freshness, trigger_persistence_3d


def _features(states: list[tuple[str, float, float, float, float]]) -> pd.DataFrame:
    rows = []
    dates = pd.date_range("2025-01-02", periods=len(states), freq="B")
    for date, (ticker, fnv_5, inv_5, combined_flow_1, combined_flow_5) in zip(dates, states, strict=True):
        rows.append(
            {
                "signal_date": date,
                "execution_date": date + pd.offsets.BDay(1),
                "종목코드": ticker,
                "fnv_5": fnv_5,
                "inv_5": inv_5,
                "combined_flow_1": combined_flow_1,
                "combined_flow_5": combined_flow_5,
            }
        )
    return pd.DataFrame(rows)


def test_trigger_freshness_fires_only_on_false_to_true_transitions() -> None:
    full = _features(
        [
            ("000010", -0.1, 0.2, 0.00, 0.00),
            ("000010", 0.1, 0.2, 0.10, 0.50),
            ("000010", 0.2, 0.2, 0.10, 0.50),
            ("000010", 0.2, -0.1, 0.00, 0.00),
            ("000010", 0.3, 0.1, 0.10, 0.50),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)

    result = trigger_freshness(filtered, full)

    assert list(result["signal_date"]) == [pd.Timestamp("2025-01-03"), pd.Timestamp("2025-01-08")]


def test_trigger_freshness_uses_only_prior_rows() -> None:
    full = _features(
        [
            ("000010", -0.1, 0.2, 0.00, 0.00),
            ("000010", 0.1, 0.2, 0.10, 0.50),
            ("000010", 0.2, 0.2, 0.10, 0.50),
            ("000010", 0.2, -0.1, 0.00, 0.00),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)
    before = trigger_freshness(filtered, full)

    mutated = full.copy()
    mutated.loc[mutated["signal_date"].gt(pd.Timestamp("2025-01-03")), ["fnv_5", "inv_5"]] = -1.0
    after = trigger_freshness(filtered, mutated)

    pd.testing.assert_frame_equal(
        before.loc[before["signal_date"].le(pd.Timestamp("2025-01-03"))].reset_index(drop=True),
        after.loc[after["signal_date"].le(pd.Timestamp("2025-01-03"))].reset_index(drop=True),
    )


def test_trigger_acceleration_fires_only_when_one_day_exceeds_five_day_average() -> None:
    full = _features(
        [
            ("000010", 0.1, 0.1, 0.11, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.09, 0.50),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)

    result = trigger_acceleration(filtered, full)

    assert list(result["signal_date"]) == [pd.Timestamp("2025-01-02")]


def test_trigger_acceleration_uses_only_same_day_context() -> None:
    full = _features(
        [
            ("000010", 0.1, 0.1, 0.11, 0.50),
            ("000010", 0.1, 0.1, 0.20, 0.50),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)
    before = trigger_acceleration(filtered, full)

    mutated = full.copy()
    mutated.loc[mutated["signal_date"].gt(pd.Timestamp("2025-01-02")), "combined_flow_1"] = -99.0
    after = trigger_acceleration(filtered, mutated)

    pd.testing.assert_frame_equal(
        before.loc[before["signal_date"].eq(pd.Timestamp("2025-01-02"))].reset_index(drop=True),
        after.loc[after["signal_date"].eq(pd.Timestamp("2025-01-02"))].reset_index(drop=True),
    )


def test_trigger_persistence_3d_requires_three_consecutive_true_days() -> None:
    full = _features(
        [
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", -0.1, 0.1, 0.00, 0.00),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)

    result = trigger_persistence_3d(filtered, full)

    assert list(result["signal_date"]) == [pd.Timestamp("2025-01-06"), pd.Timestamp("2025-01-13")]


def test_trigger_persistence_3d_uses_only_prior_rows() -> None:
    full = _features(
        [
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
            ("000010", 0.1, 0.1, 0.10, 0.50),
        ]
    )
    filtered = filter_flow_sign_both_positive(full)
    before = trigger_persistence_3d(filtered, full)

    mutated = full.copy()
    mutated.loc[mutated["signal_date"].gt(pd.Timestamp("2025-01-06")), ["fnv_5", "inv_5"]] = -1.0
    after = trigger_persistence_3d(filtered, mutated)

    pd.testing.assert_frame_equal(
        before.loc[before["signal_date"].eq(pd.Timestamp("2025-01-06"))].reset_index(drop=True),
        after.loc[after["signal_date"].eq(pd.Timestamp("2025-01-06"))].reset_index(drop=True),
    )
