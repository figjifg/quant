from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import _empty_candidates, _run_segmented_cash
from src.strategies.c004_quarterly_macro_gate import quarterly_execution_dates, run_quarterly_mcap_backtest


VARIANT = "factor_macro_gate_mcap"
VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")
STATUS_COLUMNS = ("거래정지여부", "관리종목여부", "상장폐지여부", "거래정지", "관리종목", "상장폐지")


@dataclass(frozen=True)
class ProductionConstraints:
    max_single_weight: float = 0.25
    max_top2_weight: float = 0.50
    min_avg_traded_value_20d: float = 5_000_000_000.0
    max_quarterly_turnover: float = 1.0
    aum_cap_krw: float | None = None


def constraints_from_config(config: dict[str, Any]) -> ProductionConstraints:
    return ProductionConstraints(
        max_single_weight=float(config["max_single_weight"]),
        max_top2_weight=float(config["max_top2_weight"]),
        min_avg_traded_value_20d=float(config["min_avg_traded_value_20d"]),
        max_quarterly_turnover=float(config["max_quarterly_turnover"]),
        aum_cap_krw=None if config.get("aum_cap_krw") is None else float(config["aum_cap_krw"]),
    )


def apply_p005_constraints(
    *,
    candidates: pd.DataFrame,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    constraints: ProductionConstraints,
    max_positions: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        return candidates.copy(), _empty_binding_log()

    constrained = _attach_candidate_inputs(candidates, panel, universe)
    before_counts = constrained.groupby("signal_date")["종목코드"].nunique()
    constrained["liquidity_blocked"] = ~constrained["avg_traded_value_20d"].ge(
        constraints.min_avg_traded_value_20d
    ).fillna(False)
    quarter_logs = []
    previous: set[str] = set()
    min_names_for_weight = int(1.0 / constraints.max_single_weight)

    filtered = constrained.loc[
        constrained["avg_traded_value_20d"].ge(constraints.min_avg_traded_value_20d).fillna(False)
        & ~constrained["status_blocked"]
    ].copy()
    filtered = filtered.sort_values(["signal_date", "rank", "종목코드"])
    filtered["rank"] = filtered.groupby("signal_date").cumcount() + 1
    filtered = filtered.loc[filtered["rank"].le(max_positions)].copy()

    viable_frames = []
    for signal_date, original in constrained.groupby("signal_date", sort=True):
        group = filtered.loc[filtered["signal_date"].eq(signal_date)].copy()
        pre_weight_count = len(group)
        if pre_weight_count < min_names_for_weight:
            group = group.iloc[0:0].copy()
        if not group.empty:
            group["intended_weight"] = 1.0 / len(group)
            group["top2_weight"] = group["intended_weight"].where(group["rank"].le(2), 0.0).sum()
            viable_frames.append(group)

        tickers = set(group["종목코드"].astype(str))
        weight_by_ticker = dict(zip(group["종목코드"].astype(str), group.get("intended_weight", pd.Series(dtype="float64")), strict=False))
        buy_turnover = sum(weight_by_ticker[ticker] for ticker in tickers - previous)
        sell_turnover = (
            1.0
            if previous and not tickers
            else sum(1.0 / len(previous) for ticker in previous - tickers)
            if previous
            else 0.0
        )
        one_way_turnover = max(buy_turnover, sell_turnover)
        single_weight_bound = pre_weight_count > 0 and pre_weight_count < min_names_for_weight
        top2_weight_bound = pre_weight_count in (1, 2, 3)
        quarter_logs.append(
            _binding_row(
                signal_date=signal_date,
                before_count=int(before_counts.get(signal_date, 0)),
                after_count=len(group),
                liquidity_removed=int(original["liquidity_blocked"].sum()),
                status_removed=int(original["status_removed"].sum()),
                single_weight_bound=single_weight_bound,
                top2_weight_bound=top2_weight_bound,
                turnover=one_way_turnover,
                turnover_bound=bool(one_way_turnover > constraints.max_quarterly_turnover),
            )
        )
        previous = tickers

    filtered = pd.concat(viable_frames, ignore_index=True) if viable_frames else filtered.iloc[0:0].copy()
    binding_log = pd.DataFrame(quarter_logs).sort_values("signal_date").reset_index(drop=True)
    output_columns = ["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5", "market_cap", "rank"]
    return filtered.loc[:, output_columns].reset_index(drop=True), binding_log


def run_p005_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    constrained_candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
) -> dict[str, BacktestResult]:
    rebalance_dates = quarterly_execution_dates(calendar, quarterly_regime, segments)
    return {
        VARIANT: run_quarterly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=constrained_candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=rebalance_dates,
        ),
        "d013_baseline": run_quarterly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=rebalance_dates,
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }


def binding_frequency(binding_log: pd.DataFrame) -> pd.DataFrame:
    if binding_log.empty:
        return pd.DataFrame(columns=["constraint", "binding_quarters", "total_quarters", "binding_frequency"])
    constraints = (
        "single_weight_bound",
        "top2_weight_bound",
        "liquidity_bound",
        "status_bound",
        "turnover_bound",
    )
    rows = []
    total = len(binding_log)
    for name in constraints:
        count = int(binding_log[name].sum())
        rows.append(
            {
                "constraint": name,
                "binding_quarters": count,
                "total_quarters": total,
                "binding_frequency": count / total if total else 0.0,
            }
        )
    return pd.DataFrame(rows)


def _attach_candidate_inputs(candidates: pd.DataFrame, panel: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    required = {"signal_date", "execution_date", "종목코드", "rank"}
    missing = sorted(required - set(candidates.columns))
    if missing:
        raise ValueError(f"candidates is missing required columns: {missing}")
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = pd.to_datetime(data["execution_date"], errors="raise").dt.normalize()
    data["종목코드"] = data["종목코드"].astype("string")

    liquidity = universe.loc[:, ["signal_date", "execution_date", "종목코드", "avg_traded_value_20d"]].copy()
    liquidity["signal_date"] = pd.to_datetime(liquidity["signal_date"], errors="raise").dt.normalize()
    liquidity["execution_date"] = pd.to_datetime(liquidity["execution_date"], errors="raise").dt.normalize()
    liquidity["종목코드"] = liquidity["종목코드"].astype("string")
    data = data.merge(liquidity, on=["signal_date", "execution_date", "종목코드"], how="left", validate="one_to_one")
    data["liquidity_removed"] = data["avg_traded_value_20d"].isna()

    status = _status_flags(panel)
    if not status.empty:
        data = data.merge(status, left_on=["signal_date", "종목코드"], right_on=["날짜", "종목코드"], how="left", validate="many_to_one")
        data["status_blocked"] = data["status_blocked"].fillna(False)
        data = data.drop(columns=["날짜"])
    else:
        data["status_blocked"] = False
    data["status_removed"] = data["status_blocked"]
    return data


def _status_flags(panel: pd.DataFrame) -> pd.DataFrame:
    columns = [column for column in STATUS_COLUMNS if column in panel.columns]
    if not columns:
        return pd.DataFrame()
    data = panel.loc[:, ["날짜", "종목코드", *columns]].copy()
    data["날짜"] = pd.to_datetime(data["날짜"], errors="raise").dt.normalize()
    data["종목코드"] = data["종목코드"].astype("string")
    status = pd.Series(False, index=data.index)
    for column in columns:
        status |= data[column].fillna(False).astype(bool)
    return data.assign(status_blocked=status).loc[:, ["날짜", "종목코드", "status_blocked"]]


def _binding_row(
    *,
    signal_date: object,
    before_count: int,
    after_count: int,
    liquidity_removed: int,
    status_removed: int,
    single_weight_bound: bool,
    top2_weight_bound: bool,
    turnover: float,
    turnover_bound: bool,
) -> dict[str, Any]:
    return {
        "signal_date": pd.Timestamp(signal_date).date().isoformat(),
        "candidate_count_before": before_count,
        "candidate_count_after": after_count,
        "liquidity_removed_count": liquidity_removed,
        "status_removed_count": status_removed,
        "single_weight_bound": single_weight_bound,
        "top2_weight_bound": top2_weight_bound,
        "liquidity_bound": liquidity_removed > 0,
        "status_bound": status_removed > 0,
        "quarterly_turnover": turnover,
        "turnover_bound": turnover_bound,
    }


def _empty_binding_log() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "signal_date",
            "candidate_count_before",
            "candidate_count_after",
            "liquidity_removed_count",
            "status_removed_count",
            "single_weight_bound",
            "top2_weight_bound",
            "liquidity_bound",
            "status_bound",
            "quarterly_turnover",
            "turnover_bound",
        ]
    )
