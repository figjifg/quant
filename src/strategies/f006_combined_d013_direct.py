from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.c004_quarterly_macro_gate import _quarterly_gate_series
from src.strategies.e003_b_count_matched import _require_columns
from src.strategies.f002_stock_rs_d013_direct import _zscore


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
    "combined_variant",
    "stock_combined_score",
    "stock_combined_score_universe",
    "raw_stock_combined_score",
]


def build_combined_d013_direct_score_universe(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    stock_scores: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    _require_columns(
        stock_scores,
        (
            "signal_date",
            "ticker",
            "sector_code",
            "sector_name",
            "combined_variant",
            "stock_combined_score",
            "raw_stock_combined_score",
        ),
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
            "combined_variant",
            "stock_combined_score",
            "raw_stock_combined_score",
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
    ranked["stock_combined_score_universe"] = ranked.groupby("signal_date", group_keys=False)[
        "raw_stock_combined_score"
    ].transform(_zscore)
    return ranked.dropna(subset=["stock_combined_score_universe"]).reset_index(drop=True)


def build_combined_d013_direct_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    stock_scores: pd.DataFrame,
    calendar: KRXTradingCalendar,
    top_n: int = 5,
) -> pd.DataFrame:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    ranked = build_combined_d013_direct_score_universe(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        stock_scores=stock_scores,
    )
    if ranked.empty:
        return _candidate_frame()

    rows: list[pd.Series] = []
    next_execution_by_signal = {
        signal_date: calendar.next_trading_day(signal_date)
        for signal_date in sorted(ranked["signal_date"].drop_duplicates())
    }
    for signal_date, date_group in ranked.groupby("signal_date", sort=True):
        selected = date_group.sort_values(
            ["stock_combined_score_universe", "market_cap", "종목코드"],
            ascending=[False, False, True],
        ).head(top_n)
        for rank, (_, row) in enumerate(selected.iterrows(), start=1):
            row = row.copy()
            row["rank"] = rank
            row["execution_date"] = next_execution_by_signal[pd.Timestamp(signal_date).normalize()]
            rows.append(row)

    if not rows:
        return _candidate_frame()
    selected = pd.DataFrame(rows)
    selected["fnv_5"] = 0.0
    selected["inv_5"] = 0.0
    selected["combined_flow_5"] = selected["stock_combined_score_universe"]
    return selected.loc[:, _CANDIDATE_COLUMNS].sort_values(["signal_date", "rank"]).reset_index(drop=True)


def _candidate_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_CANDIDATE_COLUMNS)
