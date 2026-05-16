from __future__ import annotations

import pandas as pd

from src.roles.rankings import rank_by_combined_flow_5_rel, rank_by_combined_flow_5_z


def _triggered() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "execution_date": [pd.Timestamp("2025-01-09")] * 4,
            "signal_date": [pd.Timestamp("2025-01-08")] * 4,
            "종목코드": ["000010", "000020", "000030", "000040"],
            "combined_flow_5_z": [0.4, pd.NA, 0.7, 0.7],
            "combined_flow_5_rel": [4.0, pd.NA, 7.0, 7.0],
        }
    )


def test_rank_by_combined_flow_5_z_drops_nan_and_sorts_descending() -> None:
    result = rank_by_combined_flow_5_z(_triggered())

    assert list(result["종목코드"]) == ["000030", "000040", "000010"]
    assert list(result["rank_score"]) == [0.7, 0.7, 0.4]


def test_rank_by_combined_flow_5_rel_drops_nan_and_sorts_descending() -> None:
    result = rank_by_combined_flow_5_rel(_triggered())

    assert list(result["종목코드"]) == ["000030", "000040", "000010"]
    assert list(result["rank_score"]) == [7.0, 7.0, 4.0]
