from __future__ import annotations

import pandas as pd

from src.roles.exits import exit_signal_reversal_rel, exit_signal_reversal_z


def _features() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-01-08"), pd.Timestamp("2025-01-09")],
            "종목코드": ["000010", "000020"],
            "fnv_5_z": [0.1, -0.2],
            "inv_5_z": [0.3, -0.4],
            "fnv_5_rel": [1.0, -2.0],
            "inv_5_rel": [3.0, -4.0],
        }
    )


def test_exit_signal_reversal_z_renames_relative_columns_for_engine() -> None:
    result = exit_signal_reversal_z(_features())

    signal_exit_features = result["signal_exit_features"]
    assert result["holding"] == 5
    assert list(signal_exit_features.columns) == ["날짜", "종목코드", "fnv_5", "inv_5"]
    assert list(signal_exit_features["fnv_5"]) == [0.1, -0.2]
    assert list(signal_exit_features["inv_5"]) == [0.3, -0.4]


def test_exit_signal_reversal_rel_renames_relative_columns_for_engine() -> None:
    result = exit_signal_reversal_rel(_features())

    signal_exit_features = result["signal_exit_features"]
    assert result["holding"] == 5
    assert list(signal_exit_features.columns) == ["날짜", "종목코드", "fnv_5", "inv_5"]
    assert list(signal_exit_features["fnv_5"]) == [1.0, -2.0]
    assert list(signal_exit_features["inv_5"]) == [3.0, -4.0]
