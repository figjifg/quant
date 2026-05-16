from __future__ import annotations

import pandas as pd

from src.roles.filters import filter_relative_AND_absolute_positive


def test_filter_relative_AND_absolute_positive_requires_all_four_positive() -> None:
    features = pd.DataFrame(
        {
            "execution_date": pd.to_datetime(["2025-01-03"] * 5),
            "signal_date": pd.to_datetime(["2025-01-02"] * 5),
            "종목코드": ["000010", "000020", "000030", "000040", "000050"],
            "fnv_5": [0.1, -0.1, 0.1, 0.1, 0.1],
            "inv_5": [0.2, 0.2, 0.0, 0.2, 0.2],
            "combined_flow_5": [0.3, 0.1, 0.1, 0.3, 0.3],
        }
    )
    relative_features = pd.DataFrame(
        {
            "execution_date": pd.to_datetime(["2025-01-03"] * 5),
            "signal_date": pd.to_datetime(["2025-01-02"] * 5),
            "종목코드": ["000010", "000020", "000030", "000040", "000050"],
            "fnv_5_rel": [0.01, 0.01, 0.01, -0.01, pd.NA],
            "inv_5_rel": [0.02, 0.02, 0.02, 0.02, 0.02],
        }
    )

    result = filter_relative_AND_absolute_positive(features, relative_features)

    assert list(result["종목코드"]) == ["000010"]


def test_filter_relative_AND_absolute_positive_aligns_by_signal_and_execution_date() -> None:
    features = pd.DataFrame(
        {
            "execution_date": pd.to_datetime(["2025-01-03"]),
            "signal_date": pd.to_datetime(["2025-01-02"]),
            "종목코드": ["000010"],
            "fnv_5": [0.1],
            "inv_5": [0.1],
        }
    )
    relative_features = pd.DataFrame(
        {
            "execution_date": pd.to_datetime(["2025-01-06"]),
            "signal_date": pd.to_datetime(["2025-01-03"]),
            "종목코드": ["000010"],
            "fnv_5_rel": [0.1],
            "inv_5_rel": [0.1],
        }
    )

    result = filter_relative_AND_absolute_positive(features, relative_features)

    assert result.empty
