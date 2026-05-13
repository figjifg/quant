from __future__ import annotations

import pandas as pd

from src.strategies.b001_mcap_normalized import build_b001_mcap_normalized_candidates


def _features() -> pd.DataFrame:
    execution_date = pd.Timestamp("2025-01-09")
    signal_date = pd.Timestamp("2025-01-08")
    return pd.DataFrame(
        [
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000010",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 0.90,
                "combined_flow_5_mcap": 0.20,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000020",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 0.20,
                "combined_flow_5_mcap": 0.50,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000030",
                "fnv_5": -0.10,
                "inv_5": 0.10,
                "combined_flow_5": 1.00,
                "combined_flow_5_mcap": 1.00,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000040",
                "fnv_5": 0.10,
                "inv_5": -0.10,
                "combined_flow_5": 1.10,
                "combined_flow_5_mcap": 1.10,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000050",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 1.20,
                "combined_flow_5_mcap": pd.NA,
            },
        ]
    )


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_b001_keeps_a_family_sign_filter_and_drops_nan_mcap_signal() -> None:
    features = _features()

    result = build_b001_mcap_normalized_candidates(features, _universe(features))

    assert set(result["종목코드"]) == {"000010", "000020"}


def test_b001_ranks_by_mcap_normalized_signal_not_traded_value_signal() -> None:
    features = _features()

    result = build_b001_mcap_normalized_candidates(features, _universe(features))

    assert list(result["종목코드"]) == ["000020", "000010"]


def test_b001_ties_break_by_ticker_code_ascending() -> None:
    execution_date = pd.Timestamp("2025-01-09")
    signal_date = pd.Timestamp("2025-01-08")
    features = pd.DataFrame(
        [
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000020",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 0.30,
                "combined_flow_5_mcap": 0.50,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "000010",
                "fnv_5": 0.10,
                "inv_5": 0.10,
                "combined_flow_5": 0.20,
                "combined_flow_5_mcap": 0.50,
            },
        ]
    )

    result = build_b001_mcap_normalized_candidates(features, _universe(features))

    assert list(result["종목코드"]) == ["000010", "000020"]
