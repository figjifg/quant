from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost, sell_cost
from src.backtest.engine import BacktestResult, EQUITY_COLUMNS, TRADE_COLUMNS
from src.strategies.c003_monthly_macro_gate import _PriceLookup, _segment_dates


VARIANT = "factor_macro_gate_mcap"
COST_SCENARIO_ORDER = ("base", "3x", "5x", "10x")
SLIPPAGE_SCENARIO_ORDER = ("base", "5bps", "10bps", "20bps")
CAPACITY_SCENARIO_ORDER = (
    "aum_1e8",
    "aum_5e8",
    "aum_1e9",
    "aum_3e9",
    "aum_5e9",
    "aum_1e10",
    "aum_3e10",
    "aum_5e10",
    "aum_1e11",
)


@dataclass(frozen=True)
class CapacityResult:
    result: BacktestResult
    candidates: pd.DataFrame


class _CapacityPosition:
    def __init__(
        self,
        *,
        ticker: str,
        entry_date: pd.Timestamp,
        signal_date: pd.Timestamp,
        entry_price: float,
        shares: float,
        notional_at_entry: float,
        buy_cost_paid: float,
        impact_bps: float,
        participation: float,
    ) -> None:
        self.ticker = ticker
        self.entry_date = entry_date
        self.signal_date = signal_date
        self.entry_price = entry_price
        self.shares = shares
        self.notional_at_entry = notional_at_entry
        self.buy_cost_paid = buy_cost_paid
        self.impact_bps = impact_bps
        self.participation = participation


def costs_with_slippage(costs: Costs, slippage_bps: float) -> Costs:
    return Costs(
        commission_bps=costs.commission_bps,
        tax_bps_sell=costs.tax_bps_sell,
        slippage_bps=float(slippage_bps),
    )


def multiply_costs(costs: Costs, multiplier: float) -> Costs:
    return Costs(
        commission_bps=costs.commission_bps * float(multiplier),
        tax_bps_sell=costs.tax_bps_sell * float(multiplier),
        slippage_bps=costs.slippage_bps * float(multiplier),
    )


def add_capacity_impact(
    *,
    panel: pd.DataFrame,
    candidates: pd.DataFrame,
    aum_krw: float,
    max_positions: int,
    impact_constant: float = 10.0,
    adv_window: int = 60,
) -> pd.DataFrame:
    if candidates.empty:
        data = candidates.copy()
        data["avg_traded_value_60d"] = pd.Series(dtype="float64")
        data["order_notional_krw"] = pd.Series(dtype="float64")
        data["participation"] = pd.Series(dtype="float64")
        data["impact_bps"] = pd.Series(dtype="float64")
        return data
    required = {"날짜", "종목코드", "거래대금추정"}
    missing = sorted(required - set(panel.columns))
    if missing:
        raise ValueError(f"panel is missing capacity columns: {missing}")

    liquidity = panel.loc[:, ["날짜", "종목코드", "거래대금추정"]].copy()
    liquidity["날짜"] = pd.to_datetime(liquidity["날짜"], errors="raise").dt.normalize()
    liquidity["종목코드"] = liquidity["종목코드"].astype("string")
    liquidity["거래대금추정"] = pd.to_numeric(liquidity["거래대금추정"], errors="coerce")
    liquidity = liquidity.sort_values(["종목코드", "날짜"])
    liquidity["avg_traded_value_60d"] = (
        liquidity.groupby("종목코드", sort=False)["거래대금추정"]
        .rolling(adv_window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = pd.to_datetime(data["execution_date"], errors="raise").dt.normalize()
    data["종목코드"] = data["종목코드"].astype("string")
    data = data.merge(
        liquidity.loc[:, ["날짜", "종목코드", "avg_traded_value_60d"]],
        left_on=["signal_date", "종목코드"],
        right_on=["날짜", "종목코드"],
        how="left",
        validate="many_to_one",
    ).drop(columns=["날짜"])
    data["order_notional_krw"] = float(aum_krw) / int(max_positions)
    data["participation"] = data["order_notional_krw"] / data["avg_traded_value_60d"]
    invalid = data["avg_traded_value_60d"].isna() | data["avg_traded_value_60d"].le(0.0)
    data.loc[invalid, "participation"] = pd.NA
    data["impact_bps"] = impact_constant * data["participation"].clip(lower=0.0).map(
        lambda value: sqrt(float(value)) if pd.notna(value) else pd.NA
    )
    return data


def run_capacity_backtest(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    base_costs: Costs,
    segments: tuple[tuple[object, object], ...],
    rebalance_dates: set[pd.Timestamp],
    initial_cash: float = 1.0,
) -> CapacityResult:
    prices = _PriceLookup(panel)
    period_dates = _segment_dates(calendar, segments)
    execution_dates = {pd.Timestamp(date).normalize() for date in candidates["execution_date"].unique()}
    execution_dates.update(pd.Timestamp(date).normalize() for date in rebalance_dates)
    candidates_by_execution = {
        date: group.sort_values(["rank", "종목코드"]).reset_index(drop=True)
        for date, group in candidates.groupby("execution_date", sort=False)
    }

    cash = float(initial_cash)
    positions: dict[str, _CapacityPosition] = {}
    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []

    for current_date in period_dates:
        if current_date in execution_dates:
            cash = _close_all_at_open(
                current_date=current_date,
                positions=positions,
                prices=prices,
                base_costs=base_costs,
                cash=cash,
                trade_rows=trade_rows,
                exit_reason="monthly_rebalance",
            )
            target = candidates_by_execution.get(current_date, pd.DataFrame())
            if not target.empty:
                cash = _open_equal_weight_positions(
                    current_date=current_date,
                    target=target,
                    positions=positions,
                    prices=prices,
                    base_costs=base_costs,
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
            base_costs=base_costs,
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

    trades = pd.DataFrame(trade_rows, columns=(*TRADE_COLUMNS, "participation", "impact_bps"))
    return CapacityResult(
        result=BacktestResult(
            trades=trades,
            equity_curve=pd.DataFrame(equity_rows, columns=EQUITY_COLUMNS),
        ),
        candidates=candidates,
    )


def capacity_summary_fields(candidates: pd.DataFrame, trades: pd.DataFrame) -> dict[str, Any]:
    participation = pd.to_numeric(candidates.get("participation", pd.Series(dtype="float64")), errors="coerce")
    impact = pd.to_numeric(candidates.get("impact_bps", pd.Series(dtype="float64")), errors="coerce")
    trade_impact = pd.to_numeric(trades.get("impact_bps", pd.Series(dtype="float64")), errors="coerce")
    return {
        "mean_participation": float(participation.mean()) if participation.notna().any() else float("nan"),
        "max_participation": float(participation.max()) if participation.notna().any() else float("nan"),
        "mean_impact_bps": float(impact.mean()) if impact.notna().any() else float("nan"),
        "mean_traded_impact_bps": float(trade_impact.mean()) if trade_impact.notna().any() else float("nan"),
    }


def _position_costs(base_costs: Costs, impact_bps: float) -> Costs:
    return Costs(
        commission_bps=base_costs.commission_bps,
        tax_bps_sell=base_costs.tax_bps_sell,
        slippage_bps=base_costs.slippage_bps + float(impact_bps),
    )


def _open_equal_weight_positions(
    *,
    current_date: pd.Timestamp,
    target: pd.DataFrame,
    positions: dict[str, _CapacityPosition],
    prices: _PriceLookup,
    base_costs: Costs,
    cash: float,
) -> float:
    allocation = cash / len(target)
    for _, row in target.iterrows():
        ticker = str(row["종목코드"])
        entry_price = prices.open(ticker, current_date)
        impact_bps = float(row["impact_bps"]) if pd.notna(row["impact_bps"]) else float("inf")
        participation = float(row["participation"]) if pd.notna(row["participation"]) else float("nan")
        if pd.isna(entry_price) or entry_price <= 0.0 or not pd.notna(impact_bps):
            continue
        costs = _position_costs(base_costs, impact_bps)
        cost_paid = buy_cost(allocation, costs)
        if allocation + cost_paid > cash:
            allocation = cash / (1.0 + (costs.commission_bps + costs.slippage_bps) / 1e4)
            cost_paid = buy_cost(allocation, costs)
        cash -= allocation + cost_paid
        positions[ticker] = _CapacityPosition(
            ticker=ticker,
            entry_date=current_date,
            signal_date=pd.Timestamp(row["signal_date"]).normalize(),
            entry_price=entry_price,
            shares=allocation / entry_price,
            notional_at_entry=allocation,
            buy_cost_paid=cost_paid,
            impact_bps=impact_bps,
            participation=participation,
        )
    return cash


def _close_all_at_open(
    *,
    current_date: pd.Timestamp,
    positions: dict[str, _CapacityPosition],
    prices: _PriceLookup,
    base_costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    for ticker in list(positions):
        exit_price = prices.open(ticker, current_date)
        if pd.isna(exit_price):
            continue
        cash = _close_position(
            position=positions.pop(ticker),
            exit_date=current_date,
            exit_price=exit_price,
            base_costs=base_costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason=exit_reason,
        )
    return cash


def _close_all_at_close(
    *,
    current_date: pd.Timestamp,
    positions: dict[str, _CapacityPosition],
    prices: _PriceLookup,
    base_costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    for ticker in list(positions):
        exit_price = prices.close(ticker, current_date)
        if pd.isna(exit_price):
            continue
        cash = _close_position(
            position=positions.pop(ticker),
            exit_date=current_date,
            exit_price=exit_price,
            base_costs=base_costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason=exit_reason,
        )
    return cash


def _close_position(
    *,
    position: _CapacityPosition,
    exit_date: pd.Timestamp,
    exit_price: float,
    base_costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    exit_notional = position.shares * exit_price
    sell_cost_paid = sell_cost(exit_notional, _position_costs(base_costs, position.impact_bps))
    cash += exit_notional - sell_cost_paid
    trade_rows.append(
        {
            "entry_date": position.entry_date,
            "signal_date": position.signal_date,
            "exit_date": exit_date,
            "종목코드": position.ticker,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "shares": position.shares,
            "notional_at_entry": position.notional_at_entry,
            "buy_cost": position.buy_cost_paid,
            "sell_cost": sell_cost_paid,
            "exit_reason": exit_reason,
            "participation": position.participation,
            "impact_bps": position.impact_bps,
        }
    )
    return cash


def _mark_to_market(positions: dict[str, _CapacityPosition], prices: _PriceLookup, current_date: pd.Timestamp) -> float:
    total = 0.0
    for position in positions.values():
        close_price = prices.close(position.ticker, current_date)
        if pd.isna(close_price):
            close_price = position.entry_price
        total += position.shares * close_price
    return total
