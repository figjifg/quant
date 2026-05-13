from __future__ import annotations

import pandas as pd

from src.strategies.b002_signal_reversal import build_b002_candidates, build_b002_signal_exit_features


def _features() -> pd.DataFrame:
    execution_date = pd.Timestamp("2025-01-09")
    signal_date = pd.Timestamp("2025-01-08")
    return pd.DataFrame(
        [
            {
                "날짜": signal_date,
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000010",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 0.90,
            },
            {
                "날짜": signal_date,
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000020",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 1.20,
            },
            {
                "날짜": signal_date,
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000030",
                "fnv_5": 0.00,
                "inv_5": 0.10,
                "combined_flow_5": 2.00,
            },
            {
                "날짜": signal_date,
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000040",
                "fnv_5": 0.10,
                "inv_5": -0.10,
                "combined_flow_5": 2.10,
            },
        ]
    )


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_b002_candidates_use_strict_positive_a_family_signal() -> None:
    features = _features()

    result = build_b002_candidates(features, _universe(features))

    assert list(result["종목코드"]) == ["000020", "000010"]


def test_b002_signal_exit_features_preserve_raw_signal_components() -> None:
    features = _features()

    result = build_b002_signal_exit_features(features)

    assert list(result.columns) == ["날짜", "종목코드", "fnv_5", "inv_5"]
    pd.testing.assert_frame_equal(result, features.loc[:, ["날짜", "종목코드", "fnv_5", "inv_5"]])
