from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import (
    build_e007_flow_rs_breadth_top_sector_candidates,
    _top_sector_ranks,
)


TOPK_GRID: tuple[tuple[int, ...], ...] = ((3, 2), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1))


def topk_label(top_sector_counts: tuple[int, ...]) -> str:
    return f"top_{len(top_sector_counts)}"


def build_e008_topk_grid_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts_grid: tuple[tuple[int, ...], ...] = TOPK_GRID,
) -> dict[str, pd.DataFrame]:
    _validate_grid(top_sector_counts_grid)
    return {
        topk_label(counts): build_e007_flow_rs_breadth_top_sector_candidates(
            panel=panel,
            universe=universe,
            quarterly_regime=quarterly_regime,
            combined_scores=combined_scores,
            sector_mapping=sector_mapping,
            calendar=calendar,
            top_sector_counts=counts,
        )
        for counts in top_sector_counts_grid
    }


def build_e008_sector_selection_log(candidates: pd.DataFrame, combined_scores: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=[
                "signal_date",
                "sector_rank",
                "sector_code",
                "sector_name",
                "flow_score",
                "rs_score",
                "breadth_score",
                "combined_score",
                "n_holdings",
                "tickers",
            ]
        )
    top_n = int(pd.to_numeric(candidates["sector_rank"], errors="raise").max())
    score_ranks = _top_sector_ranks(combined_scores, top_n=top_n)
    sector_names = (
        combined_scores.loc[:, ["sector_code", "sector_name"]]
        .assign(sector_code=lambda frame: frame["sector_code"].astype("string").str.zfill(2))
        .drop_duplicates()
        .set_index("sector_code")["sector_name"]
        .to_dict()
    )
    rows = []
    signal_dates = pd.to_datetime(candidates["signal_date"], errors="raise").dt.normalize()
    sector_codes = candidates["sector_code"].astype("string").str.zfill(2)
    for _, sector in score_ranks.iterrows():
        signal_date = pd.Timestamp(sector["signal_date"]).normalize()
        sector_code = str(sector["sector_code"]).zfill(2)
        holdings = candidates.loc[signal_dates.eq(signal_date) & sector_codes.eq(sector_code)]
        rows.append(
            {
                "signal_date": signal_date,
                "sector_rank": int(sector["sector_rank"]),
                "sector_code": sector_code,
                "sector_name": sector_names.get(sector_code, ""),
                "flow_score": float(sector["sector_flow_score"]),
                "rs_score": float(sector["sector_rs_score"]),
                "breadth_score": float(sector["sector_breadth_score"]),
                "combined_score": float(sector["sector_combined_score"]),
                "n_holdings": int(len(holdings)),
                "tickers": (
                    " ".join(holdings["종목코드"].astype(str).str.zfill(6).sort_values())
                    if not holdings.empty
                    else ""
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["signal_date", "sector_rank"]).reset_index(drop=True)


def _validate_grid(top_sector_counts_grid: tuple[tuple[int, ...], ...]) -> None:
    if not top_sector_counts_grid:
        raise ValueError("top_sector_counts_grid must not be empty.")
    labels = [topk_label(counts) for counts in top_sector_counts_grid]
    if len(labels) != len(set(labels)):
        raise ValueError("top_sector_counts_grid must have unique K values.")
    for counts in top_sector_counts_grid:
        if not counts or any(count <= 0 for count in counts):
            raise ValueError("top_sector_counts_grid entries must contain positive counts.")
        if sum(counts) != 5:
            raise ValueError("Each top_sector_counts_grid entry must select exactly 5 stocks.")
