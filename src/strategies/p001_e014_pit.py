from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.c004_quarterly_macro_gate import _quarterly_gate_series
from src.strategies.e003_b_count_matched import _require_columns
from src.strategies.e007_flow_rs_breadth import _CANDIDATE_COLUMNS, _candidate_frame, _top_sector_ranks
from src.strategies.e014_rs_breadth_top4 import TOP4_SECTOR_STOCK_COUNTS, rs_breadth_score_view


def build_p001_e014_pit_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    pit_sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...] = TOP4_SECTOR_STOCK_COUNTS,
) -> pd.DataFrame:
    """Build E014 candidates with point-in-time sector membership by signal_date."""
    if not top_sector_counts or any(count <= 0 for count in top_sector_counts):
        raise ValueError("top_sector_counts must contain positive counts.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    _require_columns(
        combined_scores,
        ("signal_date", "sector_code", "sector_name", "flow_score", "rs_score", "breadth_score", "combined_score"),
        "combined_scores",
    )
    _require_columns(
        pit_sector_mapping,
        ("date", "ticker", "final_sector_code", "final_sector_name"),
        "pit_sector_mapping",
    )

    gate = _quarterly_gate_series(quarterly_regime)
    gate_on_dates = {pd.Timestamp(date).normalize() for date, on in gate.items() if bool(on)}
    eligible = universe.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    eligible["execution_date"] = pd.to_datetime(eligible["execution_date"], errors="raise").dt.normalize()
    eligible["signal_date"] = pd.to_datetime(eligible["signal_date"], errors="raise").dt.normalize()
    eligible["종목코드"] = eligible["종목코드"].astype("string").str.zfill(6)
    eligible = eligible.loc[eligible["signal_date"].isin(gate_on_dates)].copy()
    if eligible.empty:
        return _candidate_frame()

    mcap = _market_cap_by_signal_date(panel)
    mcap["종목코드"] = mcap["종목코드"].astype("string").str.zfill(6)
    ranked = eligible.merge(
        mcap,
        left_on=["signal_date", "종목코드"],
        right_on=["날짜", "종목코드"],
        how="inner",
        validate="one_to_one",
    ).drop(columns=["날짜"])
    ranked = _attach_pit_sector(ranked, pit_sector_mapping)
    ranked = ranked.loc[ranked["market_cap"].gt(0)].copy()
    score_ranks = _top_sector_ranks(rs_breadth_score_view(combined_scores), top_n=len(top_sector_counts))
    ranked = ranked.merge(score_ranks, on=["signal_date", "sector_code"], how="inner", validate="many_to_one")
    if ranked.empty:
        return _candidate_frame()

    rows: list[pd.Series] = []
    next_execution_by_signal = {
        signal_date: calendar.next_trading_day(signal_date)
        for signal_date in sorted(ranked["signal_date"].drop_duplicates())
    }
    for signal_date, date_group in ranked.groupby("signal_date", sort=True):
        selected_for_date: list[pd.Series] = []
        for sector_rank, count in enumerate(top_sector_counts, start=1):
            sector_group = date_group.loc[date_group["sector_rank"].eq(sector_rank)].sort_values(
                ["market_cap", "종목코드"], ascending=[False, True]
            )
            selected_for_date.extend(row.copy() for _, row in sector_group.head(count).iterrows())
        for rank, row in enumerate(selected_for_date, start=1):
            row["rank"] = rank
            row["execution_date"] = next_execution_by_signal[pd.Timestamp(signal_date).normalize()]
            rows.append(row)

    if not rows:
        return _candidate_frame()
    selected = pd.DataFrame(rows)
    selected["fnv_5"] = 0.0
    selected["inv_5"] = 0.0
    selected["combined_flow_5"] = selected["sector_combined_score"]
    selected["target_weight"] = 1.0 / selected.groupby("signal_date")["종목코드"].transform("count")
    return selected.loc[:, _CANDIDATE_COLUMNS].sort_values(["signal_date", "rank"]).reset_index(drop=True)


def _attach_pit_sector(data: pd.DataFrame, pit_sector_mapping: pd.DataFrame) -> pd.DataFrame:
    mapping = pit_sector_mapping.loc[:, ["date", "ticker", "final_sector_code", "final_sector_name"]].copy()
    mapping["date"] = pd.to_datetime(mapping["date"], errors="raise").dt.normalize()
    mapping["ticker"] = mapping["ticker"].astype("string").str.zfill(6)
    mapping["sector_code"] = mapping["final_sector_code"].astype("string").str.zfill(2)
    mapping["sector_name"] = mapping["final_sector_name"].astype("string")
    mapping = mapping.drop_duplicates(["date", "ticker"], keep="last")
    merged = data.merge(
        mapping.loc[:, ["date", "ticker", "sector_code", "sector_name"]],
        left_on=["signal_date", "종목코드"],
        right_on=["date", "ticker"],
        how="inner",
        validate="one_to_one",
    )
    return merged.drop(columns=["date", "ticker"])
