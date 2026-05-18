from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.c004_quarterly_macro_gate import _quarterly_gate_series
from src.strategies.e003_b_count_matched import _require_columns
from src.strategies.e007_flow_rs_breadth import _top_sector_ranks
from src.strategies.e014_rs_breadth_top4 import rs_breadth_score_view
from src.strategies.f002_stock_rs_e014 import TOP4_SECTOR_STOCK_COUNTS


_CANDIDATE_COLUMNS = [
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
    "market_cap",
    "rank",
    "sector_code",
    "sector_name",
    "sector_rank",
    "sector_flow_score",
    "sector_rs_score",
    "sector_breadth_score",
    "sector_combined_score",
    "stock_foreign_flow_score",
    "raw_stock_foreign_flow_score",
    "target_weight",
]


def build_f003_e014_selection_universe(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    stock_scores: pd.DataFrame,
    top_sector_counts: tuple[int, ...] = TOP4_SECTOR_STOCK_COUNTS,
) -> pd.DataFrame:
    if not top_sector_counts or any(count <= 0 for count in top_sector_counts):
        raise ValueError("top_sector_counts must contain positive counts.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    _require_columns(
        stock_scores,
        ("signal_date", "ticker", "stock_foreign_flow_score", "raw_stock_foreign_flow_score"),
        "stock_scores",
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

    scores = stock_scores.loc[
        :,
        [
            "signal_date",
            "ticker",
            "sector_code",
            "sector_name",
            "stock_foreign_flow_score",
            "raw_stock_foreign_flow_score",
        ],
    ].copy()
    scores["signal_date"] = pd.to_datetime(scores["signal_date"], errors="raise").dt.normalize()
    scores["ticker"] = scores["ticker"].astype("string").str.zfill(6)
    scores["sector_code"] = scores["sector_code"].astype("string").str.zfill(2)
    ranked = ranked.merge(
        scores,
        left_on=["signal_date", "종목코드"],
        right_on=["signal_date", "ticker"],
        how="inner",
        validate="one_to_one",
    ).drop(columns=["ticker"])
    ranked = ranked.loc[ranked["market_cap"].gt(0)].copy()

    sector_ranks = _top_sector_ranks(rs_breadth_score_view(combined_scores), top_n=len(top_sector_counts))
    ranked = ranked.merge(sector_ranks, on=["signal_date", "sector_code"], how="inner", validate="many_to_one")
    return ranked.dropna(subset=["stock_foreign_flow_score"]).reset_index(drop=True)


def build_f003_foreign_flow_e014_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    stock_scores: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...] = TOP4_SECTOR_STOCK_COUNTS,
) -> pd.DataFrame:
    ranked = build_f003_e014_selection_universe(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        stock_scores=stock_scores,
        top_sector_counts=top_sector_counts,
    )
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
                ["stock_foreign_flow_score", "market_cap", "종목코드"],
                ascending=[False, False, True],
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
    selected["combined_flow_5"] = selected["stock_foreign_flow_score"]
    selected["target_weight"] = 1.0 / selected.groupby("signal_date")["종목코드"].transform("count")
    return selected.loc[:, _CANDIDATE_COLUMNS].sort_values(["signal_date", "rank"]).reset_index(drop=True)


def _candidate_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_CANDIDATE_COLUMNS)
