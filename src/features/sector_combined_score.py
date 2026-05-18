from __future__ import annotations

import pandas as pd

from src.features.sector_flow_score import (
    build_rank_ic_diagnostics as _build_flow_rank_ic_diagnostics,
    build_sector_forward_returns,
    build_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics as _build_flow_top_bottom_spread_diagnostics,
    diagnostics_pass,
)


REQUIRED_FLOW_COLUMNS = ("signal_date", "sector_code", "sector_name", "flow_score")
REQUIRED_RS_COLUMNS = ("signal_date", "sector_code", "sector_name", "rs_score")
REQUIRED_BREADTH_COLUMNS = ("signal_date", "sector_code", "sector_name", "breadth_score")


def build_sector_combined_scores(
    flow_scores: pd.DataFrame,
    rs_scores: pd.DataFrame,
    breadth_scores: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Combine pre-timestamped sector scores with a simple mean."""
    _require_columns(flow_scores, REQUIRED_FLOW_COLUMNS, "flow_scores")
    _require_columns(rs_scores, REQUIRED_RS_COLUMNS, "rs_scores")

    flow = flow_scores.loc[:, ["signal_date", "sector_code", "sector_name", "flow_score"]].copy()
    flow["signal_date"] = pd.to_datetime(flow["signal_date"], errors="raise").dt.normalize()
    flow["sector_code"] = flow["sector_code"].astype("string").str.zfill(2)
    flow["sector_name"] = flow["sector_name"].astype("string")
    flow["flow_score"] = pd.to_numeric(flow["flow_score"], errors="coerce")

    rs = rs_scores.loc[:, ["signal_date", "sector_code", "sector_name", "rs_score"]].copy()
    rs["signal_date"] = pd.to_datetime(rs["signal_date"], errors="raise").dt.normalize()
    rs["sector_code"] = rs["sector_code"].astype("string").str.zfill(2)
    rs["sector_name"] = rs["sector_name"].astype("string")
    rs["rs_score"] = pd.to_numeric(rs["rs_score"], errors="coerce")

    combined = flow.merge(
        rs.loc[:, ["signal_date", "sector_code", "rs_score"]],
        on=["signal_date", "sector_code"],
        how="inner",
        validate="one_to_one",
    )
    component_columns = ["flow_score", "rs_score"]
    if breadth_scores is not None:
        _require_columns(breadth_scores, REQUIRED_BREADTH_COLUMNS, "breadth_scores")
        breadth = breadth_scores.loc[:, ["signal_date", "sector_code", "breadth_score"]].copy()
        breadth["signal_date"] = pd.to_datetime(breadth["signal_date"], errors="raise").dt.normalize()
        breadth["sector_code"] = breadth["sector_code"].astype("string").str.zfill(2)
        breadth["breadth_score"] = pd.to_numeric(breadth["breadth_score"], errors="coerce")
        combined = combined.merge(
            breadth,
            on=["signal_date", "sector_code"],
            how="inner",
            validate="one_to_one",
        )
        component_columns.append("breadth_score")
    combined["combined_score"] = combined[component_columns].mean(axis=1, skipna=False)
    combined["eligible_for_score"] = combined[component_columns].notna().all(axis=1)
    output_columns = [
        "signal_date",
        "sector_code",
        "sector_name",
        "flow_score",
        "rs_score",
    ]
    if breadth_scores is not None:
        output_columns.append("breadth_score")
    output_columns.extend(["combined_score", "eligible_for_score"])
    return combined.loc[
        :,
        output_columns,
    ].sort_values(["signal_date", "sector_code"]).reset_index(drop=True)


def build_rank_ic_diagnostics(scores: pd.DataFrame, forward_returns: pd.DataFrame) -> pd.DataFrame:
    return _build_flow_rank_ic_diagnostics(_as_flow_score_frame(scores), forward_returns)


def build_top_bottom_spread_diagnostics(
    scores: pd.DataFrame,
    forward_returns: pd.DataFrame,
    *,
    k: int = 3,
) -> pd.DataFrame:
    return _build_flow_top_bottom_spread_diagnostics(_as_flow_score_frame(scores), forward_returns, k=k)


def _as_flow_score_frame(scores: pd.DataFrame) -> pd.DataFrame:
    _require_columns(scores, ("signal_date", "sector_code", "sector_name", "combined_score"), "scores")
    data = scores.loc[:, ["signal_date", "sector_code", "sector_name", "combined_score"]].copy()
    return data.rename(columns={"combined_score": "flow_score"})


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
