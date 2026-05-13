from __future__ import annotations

import pandas as pd
import pytest

from src.strategies.e001_flow_filter import build_e001_flow_filter_candidates
from src.strategies.e003_market_gate import build_e003_market_gated_candidates


def _flow_features() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "execution_date": pd.Timestamp("2025-01-07"),
                "signal_date": pd.Timestamp("2025-01-06"),
                "종목코드": "000010",
                "fnv_5": 0.1,
                "inv_5": 0.2,
                "combined_flow_5": 0.3,
            },
            {
                "execution_date": pd.Timestamp("2025-01-07"),
                "signal_date": pd.Timestamp("2025-01-06"),
                "종목코드": "000020",
                "fnv_5": 0.2,
                "inv_5": 0.3,
                "combined_flow_5": 0.5,
            },
            {
                "execution_date": pd.Timestamp("2025-01-08"),
                "signal_date": pd.Timestamp("2025-01-07"),
                "종목코드": "000010",
                "fnv_5": 0.4,
                "inv_5": 0.5,
                "combined_flow_5": 0.7,
            },
            {
                "execution_date": pd.Timestamp("2025-01-09"),
                "signal_date": pd.Timestamp("2025-01-08"),
                "종목코드": "000030",
                "fnv_5": 0.4,
                "inv_5": -0.1,
                "combined_flow_5": 0.1,
            },
        ]
    )


def _universe(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()


def test_gate_on_days_preserve_e001_candidates_and_order() -> None:
    features = _flow_features()
    universe = _universe(features)
    gate = pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-01-06"), pd.Timestamp("2025-01-07")],
            "execution_date": [pd.Timestamp("2025-01-07"), pd.Timestamp("2025-01-08")],
            "market_gate_on": [True, False],
        }
    )

    result = build_e003_market_gated_candidates(features, universe, gate, "market_gate_on")
    expected = build_e001_flow_filter_candidates(features, universe)
    expected = expected.loc[expected["execution_date"].eq(pd.Timestamp("2025-01-07"))].reset_index(drop=True)

    pd.testing.assert_frame_equal(result, expected)


def test_gate_off_execution_date_has_zero_candidates() -> None:
    features = _flow_features()
    gate = pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-01-06"), pd.Timestamp("2025-01-07")],
            "execution_date": [pd.Timestamp("2025-01-07"), pd.Timestamp("2025-01-08")],
            "market_gate_on": [False, False],
        }
    )

    result = build_e003_market_gated_candidates(features, _universe(features), gate, "market_gate_on")

    assert result.empty


def test_nan_or_missing_gate_is_treated_as_off() -> None:
    features = _flow_features()
    gate = pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-01-06")],
            "execution_date": [pd.Timestamp("2025-01-07")],
            "market_gate_on": [pd.NA],
        }
    )

    result = build_e003_market_gated_candidates(features, _universe(features), gate, "market_gate_on")

    assert result.empty


def test_gate_column_is_parameterized_for_price_and_double_variants() -> None:
    features = _flow_features()
    gate = pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-01-06"), pd.Timestamp("2025-01-07")],
            "execution_date": [pd.Timestamp("2025-01-07"), pd.Timestamp("2025-01-08")],
            "price_gate_on": [False, True],
        }
    )

    result = build_e003_market_gated_candidates(features, _universe(features), gate, "price_gate_on")

    assert list(result["execution_date"].unique()) == [pd.Timestamp("2025-01-08")]
    assert list(result["종목코드"]) == ["000010"]


def test_missing_gate_column_raises() -> None:
    features = _flow_features()
    gate = pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-01-06")],
            "execution_date": [pd.Timestamp("2025-01-07")],
            "market_gate_on": [True],
        }
    )

    with pytest.raises(ValueError, match="missing gate column"):
        build_e003_market_gated_candidates(features, _universe(features), gate, "double_gate_on")
