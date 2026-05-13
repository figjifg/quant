from __future__ import annotations

import pandas as pd


SORT_COLUMNS = ("execution_date", "rank_score", "종목코드")


def rank_by_combined_flow_5(triggered: pd.DataFrame) -> pd.DataFrame:
    """Return candidates ranked by 5-day combined flow."""
    return _rank_by_column(triggered, "combined_flow_5", drop_na=False)


def rank_by_combined_flow_5_mcap(triggered: pd.DataFrame) -> pd.DataFrame:
    """Return candidates ranked by market-cap-normalized 5-day combined flow."""
    return _rank_by_column(triggered, "combined_flow_5_mcap", drop_na=False)


def rank_by_recent_return_5(triggered: pd.DataFrame) -> pd.DataFrame:
    """Return candidates ranked by 5-day recent return, dropping NaN scores."""
    return _rank_by_column(triggered, "recent_return_5", drop_na=True)


def _rank_by_column(triggered: pd.DataFrame, score_column: str, *, drop_na: bool) -> pd.DataFrame:
    _require_columns(triggered, ("execution_date", "종목코드", score_column), "triggered")
    candidates = triggered.copy()
    if drop_na:
        candidates = candidates.loc[candidates[score_column].notna()].copy()
    candidates["rank_score"] = candidates[score_column]
    return candidates.sort_values(
        list(SORT_COLUMNS),
        ascending=[True, False, True],
    ).reset_index(drop=True)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
