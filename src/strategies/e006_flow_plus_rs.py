from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.c003_monthly_macro_gate import _empty_candidates
from src.strategies.c004_quarterly_macro_gate import _quarterly_gate_series
from src.strategies.e003_b_count_matched import _attach_sector, _require_columns


VARIANTS = ("factor_macro_gate_flow_plus_rs_top3", "kospi_buy_and_hold", "cash")

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
    "sector_combined_score",
    "target_weight",
]


def build_e006_flow_plus_rs_top_sector_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_sector_counts: tuple[int, ...] = (2, 2, 1),
) -> pd.DataFrame:
    if not top_sector_counts or any(count <= 0 for count in top_sector_counts):
        raise ValueError("top_sector_counts must contain positive counts.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    _require_columns(
        combined_scores,
        ("signal_date", "sector_code", "sector_name", "flow_score", "rs_score", "combined_score"),
        "combined_scores",
    )
    _require_columns(sector_mapping, ("ticker", "final_sector_code", "final_sector_name"), "sector_mapping")

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
    ranked = _attach_sector(ranked, sector_mapping)
    ranked = ranked.loc[ranked["market_cap"].gt(0)].copy()
    score_ranks = _top_sector_ranks(combined_scores, top_n=len(top_sector_counts))
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


def build_e006_sector_selection_log(candidates: pd.DataFrame, combined_scores: pd.DataFrame) -> pd.DataFrame:
    score_ranks = _top_sector_ranks(combined_scores, top_n=3)
    sector_names = (
        combined_scores.loc[:, ["sector_code", "sector_name"]]
        .assign(sector_code=lambda frame: frame["sector_code"].astype("string").str.zfill(2))
        .drop_duplicates()
        .set_index("sector_code")["sector_name"]
        .to_dict()
    )
    rows = []
    for _, sector in score_ranks.iterrows():
        signal_date = pd.Timestamp(sector["signal_date"]).normalize()
        sector_code = str(sector["sector_code"]).zfill(2)
        holdings = candidates.loc[
            pd.to_datetime(candidates.get("signal_date", pd.Series(dtype="datetime64[ns]")), errors="coerce")
            .dt.normalize()
            .eq(signal_date)
            & candidates.get("sector_code", pd.Series(dtype="string")).astype("string").str.zfill(2).eq(sector_code)
        ]
        rows.append(
            {
                "signal_date": signal_date,
                "sector_rank": int(sector["sector_rank"]),
                "sector_code": sector_code,
                "sector_name": sector_names.get(sector_code, ""),
                "flow_score": float(sector["sector_flow_score"]),
                "rs_score": float(sector["sector_rs_score"]),
                "combined_score": float(sector["sector_combined_score"]),
                "n_holdings": int(len(holdings)),
                "tickers": " ".join(holdings["종목코드"].astype(str).str.zfill(6).sort_values()) if not holdings.empty else "",
            }
        )
    return pd.DataFrame(rows).sort_values(["signal_date", "sector_rank"]).reset_index(drop=True)


def empty_candidates_by_variant() -> dict[str, pd.DataFrame]:
    return {
        "factor_macro_gate_flow_plus_rs_top3": _candidate_frame(),
        "kospi_buy_and_hold": _empty_candidates(),
        "cash": _empty_candidates(),
    }


def _top_sector_ranks(combined_scores: pd.DataFrame, *, top_n: int) -> pd.DataFrame:
    scores = combined_scores.loc[:, ["signal_date", "sector_code", "flow_score", "rs_score", "combined_score"]].copy()
    scores["signal_date"] = pd.to_datetime(scores["signal_date"], errors="raise").dt.normalize()
    scores["sector_code"] = scores["sector_code"].astype("string").str.zfill(2)
    scores["sector_flow_score"] = pd.to_numeric(scores["flow_score"], errors="coerce")
    scores["sector_rs_score"] = pd.to_numeric(scores["rs_score"], errors="coerce")
    scores["sector_combined_score"] = pd.to_numeric(scores["combined_score"], errors="coerce")
    scores = scores.dropna(subset=["sector_combined_score"]).sort_values(
        ["signal_date", "sector_combined_score", "sector_code"], ascending=[True, False, True]
    )
    scores["sector_rank"] = scores.groupby("signal_date").cumcount() + 1
    return scores.loc[
        scores["sector_rank"].le(top_n),
        [
            "signal_date",
            "sector_code",
            "sector_flow_score",
            "sector_rs_score",
            "sector_combined_score",
            "sector_rank",
        ],
    ]


def _candidate_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_CANDIDATE_COLUMNS)
