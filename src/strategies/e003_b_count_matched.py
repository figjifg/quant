from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import _empty_candidates, _run_segmented_cash
from src.strategies.c004_quarterly_macro_gate import (
    _quarterly_execution_candidates,
    _quarterly_gate_series,
    quarterly_execution_dates,
    run_quarterly_mcap_backtest,
)


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def build_count_matched_sector_candidates(
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    *,
    max_positions: int = 5,
) -> pd.DataFrame:
    if max_positions <= 0:
        raise ValueError("max_positions must be positive.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    _require_columns(sector_mapping, ("ticker", "final_sector_code", "final_sector_name"), "sector_mapping")

    eligible = universe.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    eligible["execution_date"] = pd.to_datetime(eligible["execution_date"], errors="raise").dt.normalize()
    eligible["signal_date"] = pd.to_datetime(eligible["signal_date"], errors="raise").dt.normalize()
    eligible["종목코드"] = eligible["종목코드"].astype("string").str.zfill(6)
    gate = _quarterly_gate_series(quarterly_regime)
    gate_on_dates = {pd.Timestamp(date).normalize() for date, on in gate.items() if bool(on)}
    eligible = eligible.loc[eligible["signal_date"].isin(gate_on_dates)]

    mcap = _market_cap_by_signal_date(panel)
    mcap["종목코드"] = mcap["종목코드"].astype("string").str.zfill(6)
    ranked = eligible.merge(
        mcap,
        left_on=["signal_date", "종목코드"],
        right_on=["날짜", "종목코드"],
        how="inner",
        validate="one_to_one",
    )
    ranked = _attach_sector(ranked, sector_mapping)
    ranked = ranked.loc[ranked["market_cap"].gt(0)].copy()
    ranked = ranked.sort_values(["signal_date", "market_cap", "종목코드"], ascending=[True, False, True])

    rows: list[pd.Series] = []
    for _, group in ranked.groupby("signal_date", sort=False):
        seen: set[str] = set()
        selected = 0
        for _, row in group.iterrows():
            sector_code = str(row["sector_code"])
            if sector_code in seen:
                continue
            seen.add(sector_code)
            selected += 1
            row = row.copy()
            row["rank"] = selected
            rows.append(row)
            if selected >= max_positions:
                break

    if not rows:
        return _candidate_frame()
    selected = pd.DataFrame(rows)
    selected["fnv_5"] = 0.0
    selected["inv_5"] = 0.0
    selected["combined_flow_5"] = selected["market_cap"]
    selected["target_weight"] = 1.0 / selected.groupby("signal_date")["종목코드"].transform("count")
    return selected.loc[:, _CANDIDATE_COLUMNS].reset_index(drop=True)


def run_e003_b_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    candidates = build_count_matched_sector_candidates(
        panel,
        universe,
        quarterly_regime,
        sector_mapping,
        max_positions=max_positions,
    )
    candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_regime, segments)
    runs = {
        "factor_macro_gate_mcap": run_quarterly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    return runs, {
        "factor_macro_gate_mcap": candidates,
        "kospi_buy_and_hold": _empty_candidates(),
        "cash": _empty_candidates(),
    }


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
    "target_weight",
]


def _candidate_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_CANDIDATE_COLUMNS)


def _attach_sector(data: pd.DataFrame, sector_mapping: pd.DataFrame) -> pd.DataFrame:
    mapping = sector_mapping.loc[:, ["ticker", "final_sector_code", "final_sector_name"]].copy()
    mapping["ticker"] = mapping["ticker"].astype("string").str.zfill(6)
    mapping["sector_code"] = mapping["final_sector_code"].astype("string").str.zfill(2)
    mapping["sector_name"] = mapping["final_sector_name"].astype("string")
    merged = data.merge(
        mapping.loc[:, ["ticker", "sector_code", "sector_name"]],
        left_on="종목코드",
        right_on="ticker",
        how="inner",
        validate="many_to_one",
    )
    return merged.drop(columns=["ticker"])


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
