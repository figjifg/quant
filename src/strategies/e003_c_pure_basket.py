from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost
from src.backtest.engine import BacktestResult, EQUITY_COLUMNS, TRADE_COLUMNS
from src.strategies.b004_regime_gate import _market_cap_by_signal_date
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.strategies.c003_monthly_macro_gate import (
    _Position,
    _PriceLookup,
    _close_all_at_close,
    _close_all_at_open,
    _empty_candidates,
    _mark_to_market,
    _run_segmented_cash,
    _segment_dates,
)
from src.strategies.c004_quarterly_macro_gate import (
    _quarterly_execution_candidates,
    _quarterly_gate_series,
    quarterly_execution_dates,
)
from src.strategies.e003_b_count_matched import _attach_sector, _require_columns


VARIANTS = ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash")


def build_pure_sector_basket_candidates(
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    *,
    min_sector_members: int = 3,
    excluded_sector_codes: tuple[str, ...] = ("99",),
) -> pd.DataFrame:
    if min_sector_members <= 0:
        raise ValueError("min_sector_members must be positive.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")

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
    excluded = {str(code).zfill(2) for code in excluded_sector_codes}
    ranked = ranked.loc[ranked["market_cap"].gt(0) & ~ranked["sector_code"].isin(excluded)].copy()
    if ranked.empty:
        return _candidate_frame()

    sector_counts = ranked.groupby(["signal_date", "sector_code"])["종목코드"].transform("count")
    ranked = ranked.loc[sector_counts.ge(min_sector_members)].copy()
    if ranked.empty:
        return _candidate_frame()

    sector_count_by_date = ranked.groupby("signal_date")["sector_code"].transform("nunique")
    sector_mcap = ranked.groupby(["signal_date", "sector_code"])["market_cap"].transform("sum")
    ranked["target_weight"] = (1.0 / sector_count_by_date) * (ranked["market_cap"] / sector_mcap)
    ranked = ranked.sort_values(
        ["signal_date", "sector_code", "market_cap", "종목코드"],
        ascending=[True, True, False, True],
    )
    ranked["rank"] = ranked.groupby("signal_date").cumcount() + 1
    ranked["fnv_5"] = 0.0
    ranked["inv_5"] = 0.0
    ranked["combined_flow_5"] = ranked["market_cap"]
    return ranked.loc[:, _CANDIDATE_COLUMNS].reset_index(drop=True)


def run_e003_c_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    min_sector_members: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    candidates = build_pure_sector_basket_candidates(
        panel,
        universe,
        quarterly_regime,
        sector_mapping,
        min_sector_members=min_sector_members,
    )
    candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_regime, segments)
    runs = {
        "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
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


def run_weighted_quarterly_basket_backtest(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    initial_cash: float = 1.0,
    rebalance_dates: set[pd.Timestamp] | None = None,
) -> BacktestResult:
    prices = _PriceLookup(panel)
    period_dates = _segment_dates(calendar, segments)
    execution_dates = {pd.Timestamp(date).normalize() for date in candidates["execution_date"].unique()}
    if rebalance_dates is not None:
        execution_dates.update(pd.Timestamp(date).normalize() for date in rebalance_dates)
    candidates_by_execution = {
        date: group.sort_values(["rank", "종목코드"]).reset_index(drop=True)
        for date, group in candidates.groupby("execution_date", sort=False)
    }

    cash = float(initial_cash)
    positions: dict[str, _Position] = {}
    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []

    for current_date in period_dates:
        if current_date in execution_dates:
            target = candidates_by_execution.get(current_date, pd.DataFrame())
            cash = _close_all_at_open(
                current_date=current_date,
                positions=positions,
                prices=prices,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
                exit_reason="quarterly_rebalance",
            )
            if not target.empty:
                cash = _open_weighted_positions(
                    current_date=current_date,
                    target=target,
                    positions=positions,
                    prices=prices,
                    costs=costs,
                    cash=cash,
                )

        mtm = _mark_to_market(positions, prices, current_date)
        equity_rows.append(
            {
                "date": current_date,
                "cash": cash,
                "mtm_value": mtm,
                "gross_value": cash + mtm,
                "net_value": cash + mtm,
                "n_positions": len(positions),
            }
        )

    if period_dates:
        cash = _close_all_at_close(
            current_date=period_dates[-1],
            positions=positions,
            prices=prices,
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason="period_end",
        )
        equity_rows[-1] = {
            "date": period_dates[-1],
            "cash": cash,
            "mtm_value": 0.0,
            "gross_value": cash,
            "net_value": cash,
            "n_positions": 0,
        }

    return BacktestResult(
        trades=pd.DataFrame(trade_rows, columns=TRADE_COLUMNS),
        equity_curve=pd.DataFrame(equity_rows, columns=EQUITY_COLUMNS),
    )


def _open_weighted_positions(
    *,
    current_date: pd.Timestamp,
    target: pd.DataFrame,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    costs: Costs,
    cash: float,
) -> float:
    weights = pd.to_numeric(target["target_weight"], errors="raise")
    positive = target.loc[weights.gt(0)].copy()
    if positive.empty:
        return cash
    weights = pd.to_numeric(positive["target_weight"], errors="raise")
    weights = weights / weights.sum()
    deployable_cash = cash
    for (_, row), weight in zip(positive.iterrows(), weights, strict=False):
        ticker = str(row["종목코드"])
        entry_price = prices.open(ticker, current_date)
        if pd.isna(entry_price) or entry_price <= 0.0:
            continue
        allocation = deployable_cash * float(weight)
        cost_paid = buy_cost(allocation, costs)
        if allocation + cost_paid > cash:
            allocation = cash / (1.0 + (costs.commission_bps + costs.slippage_bps) / 1e4)
            cost_paid = buy_cost(allocation, costs)
        cash -= allocation + cost_paid
        positions[ticker] = _Position(
            ticker=ticker,
            entry_date=current_date,
            signal_date=pd.Timestamp(row["signal_date"]).normalize(),
            entry_price=entry_price,
            shares=allocation / entry_price,
            notional_at_entry=allocation,
            buy_cost_paid=cost_paid,
        )
    return cash


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
