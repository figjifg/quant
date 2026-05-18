from __future__ import annotations

import pandas as pd
import pytest

from src.features.sector_combined_score import build_sector_combined_scores


def _flow_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": ["2025-03-31", "2025-03-31", "2025-06-30"],
            "sector_code": ["1", "02", "01"],
            "sector_name": ["sector_01", "sector_02", "sector_01"],
            "flow_score": [1.0, -0.5, 99.0],
        }
    )


def _rs_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": ["2025-03-31", "2025-03-31", "2025-06-30"],
            "sector_code": ["01", "2", "01"],
            "sector_name": ["sector_01", "sector_02", "sector_01"],
            "rs_score": [0.5, 1.5, -99.0],
        }
    )


def test_combined_score_is_simple_mean_of_flow_and_rs_scores() -> None:
    result = build_sector_combined_scores(_flow_scores(), _rs_scores())
    by_sector = result.loc[result["signal_date"].eq(pd.Timestamp("2025-03-31"))].set_index("sector_code")

    assert by_sector.loc["01", "combined_score"] == pytest.approx(0.75)
    assert by_sector.loc["02", "combined_score"] == pytest.approx(0.5)
    assert by_sector.loc["01", "eligible_for_score"]
    assert by_sector.loc["02", "eligible_for_score"]


def test_combined_score_requires_both_components() -> None:
    rs = _rs_scores()
    rs.loc[0, "rs_score"] = pd.NA

    result = build_sector_combined_scores(_flow_scores(), rs)
    row = result.loc[
        result["signal_date"].eq(pd.Timestamp("2025-03-31")) & result["sector_code"].eq("01")
    ].iloc[0]

    assert pd.isna(row["combined_score"])
    assert not bool(row["eligible_for_score"])


def test_combined_score_at_signal_date_is_unchanged_by_future_component_rows() -> None:
    signal_date = pd.Timestamp("2025-03-31")
    before = build_sector_combined_scores(_flow_scores(), _rs_scores())

    mutated_flow = _flow_scores()
    mutated_rs = _rs_scores()
    mutated_flow.loc[pd.to_datetime(mutated_flow["signal_date"]).gt(signal_date), "flow_score"] = -999_999.0
    mutated_rs.loc[pd.to_datetime(mutated_rs["signal_date"]).gt(signal_date), "rs_score"] = 999_999.0
    after = build_sector_combined_scores(mutated_flow, mutated_rs)

    pd.testing.assert_series_equal(
        before.loc[before["signal_date"].eq(signal_date)].sort_values("sector_code")["combined_score"].reset_index(drop=True),
        after.loc[after["signal_date"].eq(signal_date)].sort_values("sector_code")["combined_score"].reset_index(drop=True),
    )
