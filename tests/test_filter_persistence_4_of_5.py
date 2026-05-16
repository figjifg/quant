from __future__ import annotations

import pandas as pd

from src.roles.filters import filter_persistence_4_of_5


def test_filter_persistence_4_of_5_requires_f1_and_four_positive_days() -> None:
    dates = pd.bdate_range("2025-01-02", periods=5)
    features = pd.DataFrame(
        {
            "execution_date": dates + pd.offsets.BDay(1),
            "signal_date": dates,
            "종목코드": ["000010"] * 5,
            "fnv_5": [0.1] * 5,
            "inv_5": [0.1] * 4 + [-0.1],
            "combined_flow_5": [0.2] * 5,
        }
    )
    daily = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    daily["combined_flow_1"] = [0.1, -0.1, 0.2, 0.3, 0.4]

    result = filter_persistence_4_of_5(features, daily)

    assert result.empty


def test_filter_persistence_4_of_5_uses_full_right_labeled_five_day_window() -> None:
    dates = pd.bdate_range("2025-01-02", periods=6)
    features = pd.DataFrame(
        {
            "execution_date": dates + pd.offsets.BDay(1),
            "signal_date": dates,
            "종목코드": ["000010"] * 6,
            "fnv_5": [0.1] * 6,
            "inv_5": [0.1] * 6,
            "combined_flow_5": [0.2] * 6,
        }
    )
    daily = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    daily["combined_flow_1"] = [0.1, 0.2, 0.3, -0.1, 0.4, -0.2]

    result = filter_persistence_4_of_5(features, daily)

    assert list(result["signal_date"]) == [dates[4]]
    assert list(result["positive_combined_flow_1_count_5"]) == [4.0]


def test_filter_persistence_4_of_5_is_computed_per_ticker() -> None:
    dates = pd.bdate_range("2025-01-02", periods=5)
    rows = []
    for ticker, values in {"000010": [0.1, 0.2, 0.3, -0.1, 0.4], "000020": [-0.1] * 5}.items():
        for signal_date, combined_flow_1 in zip(dates, values, strict=True):
            rows.append(
                {
                    "execution_date": signal_date + pd.offsets.BDay(1),
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "fnv_5": 0.1,
                    "inv_5": 0.1,
                    "combined_flow_5": 0.2,
                    "combined_flow_1": combined_flow_1,
                }
            )
    data = pd.DataFrame(rows)

    result = filter_persistence_4_of_5(data.drop(columns="combined_flow_1"), data)

    assert list(result["종목코드"]) == ["000010"]
    assert list(result["signal_date"]) == [dates[4]]


def test_filter_persistence_4_of_5_ignores_future_rows() -> None:
    dates = pd.bdate_range("2025-01-02", periods=6)
    features = pd.DataFrame(
        {
            "execution_date": dates + pd.offsets.BDay(1),
            "signal_date": dates,
            "종목코드": ["000010"] * 6,
            "fnv_5": [0.1] * 6,
            "inv_5": [0.1] * 6,
            "combined_flow_5": [0.2] * 6,
        }
    )
    daily = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    daily["combined_flow_1"] = [0.1, 0.2, 0.3, -0.1, 0.4, -0.2]
    before = filter_persistence_4_of_5(features, daily)

    mutated = daily.copy()
    mutated.loc[mutated["signal_date"].gt(dates[4]), "combined_flow_1"] = 999.0
    after = filter_persistence_4_of_5(features, mutated)

    before_row = before.loc[before["signal_date"].eq(dates[4])].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(dates[4])].reset_index(drop=True)
    pd.testing.assert_frame_equal(after_row, before_row)
