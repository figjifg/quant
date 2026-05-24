from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost, sell_cost
from src.backtest.engine import BacktestResult, EQUITY_COLUMNS, TRADE_COLUMNS
from src.strategies.c003_monthly_macro_gate import _segment_dates
from src.utils.ohlcv_quarantine import assert_panel_has_valid_mask


SCENARIOS: dict[str, dict[str, Any]] = {
    "A_next_day_close": {
        "label": "A: next-day close",
        "delay_trading_days": 1,
        "entry_price": "KRX종가",
        "exit_price": "KRX종가",
        "deploy_fraction": 1.0,
        "cash_fallback": False,
    },
    "B_1day_delay": {
        "label": "B: 1-day delay",
        "delay_trading_days": 2,
        "entry_price": "시가",
        "exit_price": "시가",
        "deploy_fraction": 1.0,
        "cash_fallback": False,
    },
    "C_2day_delay": {
        "label": "C: 2-day delay",
        "delay_trading_days": 3,
        "entry_price": "시가",
        "exit_price": "시가",
        "deploy_fraction": 1.0,
        "cash_fallback": False,
    },
    "D_unfavorable_fill": {
        "label": "D: unfavorable fill",
        "delay_trading_days": 1,
        "entry_price": "고가",
        "exit_price": "저가",
        "deploy_fraction": 1.0,
        "cash_fallback": False,
    },
    "E_partial_fill": {
        "label": "E: partial fill 80%",
        "delay_trading_days": 1,
        "entry_price": "시가",
        "exit_price": "시가",
        "deploy_fraction": 0.8,
        "cash_fallback": False,
    },
    "F_cash_fallback": {
        "label": "F: cash fallback",
        "delay_trading_days": 1,
        "entry_price": "시가",
        "exit_price": "시가",
        "deploy_fraction": 1.0,
        "cash_fallback": True,
    },
}

STATUS_COLUMNS = ("거래정지여부", "관리종목여부", "거래정지", "관리종목")


@dataclass(frozen=True)
class P002ExecutionResult:
    result: BacktestResult
    candidates: pd.DataFrame
    fallback_events: pd.DataFrame


class _Position:
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
    ) -> None:
        self.ticker = ticker
        self.entry_date = entry_date
        self.signal_date = signal_date
        self.entry_price = entry_price
        self.shares = shares
        self.notional_at_entry = notional_at_entry
        self.buy_cost_paid = buy_cost_paid


class _PriceLookup:
    def __init__(self, panel: pd.DataFrame, required_price_columns: tuple[str, ...]) -> None:
        required = ("날짜", "종목코드", "KRX종가", *required_price_columns)
        missing = [column for column in dict.fromkeys(required) if column not in panel.columns]
        if missing:
            raise ValueError(f"panel is missing required P002 price columns: {missing}")
        status_columns = [column for column in STATUS_COLUMNS if column in panel.columns]
        data = panel.loc[:, list(dict.fromkeys(required + tuple(status_columns)))].copy()
        data["날짜"] = pd.to_datetime(data["날짜"], errors="raise").dt.normalize()
        data["종목코드"] = data["종목코드"].astype("string")
        if data.duplicated(["날짜", "종목코드"]).any():
            raise ValueError("panel contains duplicate rows for (날짜, 종목코드).")
        self._data = data.set_index(["날짜", "종목코드"]).sort_index()
        self._status_columns = tuple(status_columns)

    def price(self, ticker: str, date: pd.Timestamp, column: str) -> float:
        key = (pd.Timestamp(date).normalize(), ticker)
        if key not in self._data.index:
            return float("nan")
        value = self._data.loc[key, column]
        if pd.isna(value) or value <= 0:
            return float("nan")
        return float(value)

    def close(self, ticker: str, date: pd.Timestamp) -> float:
        return self.price(ticker, date, "KRX종가")

    def is_fallback_ticker(self, ticker: str, date: pd.Timestamp) -> bool:
        key = (pd.Timestamp(date).normalize(), ticker)
        if key not in self._data.index:
            return True
        for column in self._status_columns:
            value = self._data.loc[key, column]
            if pd.notna(value) and bool(value):
                return True
        return False


def p002_rebalance_dates(
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    delay_trading_days: int,
) -> set[pd.Timestamp]:
    segment_dates = set(_segment_dates(calendar, segments))
    dates: set[pd.Timestamp] = set()
    for signal_date in pd.to_datetime(quarterly_regime["signal_date"], errors="raise"):
        try:
            execution_date = calendar.add_trading_days(pd.Timestamp(signal_date).normalize(), delay_trading_days)
        except ValueError:
            continue
        if execution_date in segment_dates:
            dates.add(execution_date)
    return dates


def p002_shift_candidates(
    candidates: pd.DataFrame,
    calendar: KRXTradingCalendar,
    *,
    delay_trading_days: int,
    segments: tuple[tuple[object, object], ...],
) -> pd.DataFrame:
    if candidates.empty:
        return candidates.copy()
    segment_dates = set(_segment_dates(calendar, segments))
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = [
        _add_or_nat(calendar, signal_date, delay_trading_days) for signal_date in data["signal_date"]
    ]
    data = data.loc[data["execution_date"].isin(segment_dates)].copy()
    return data


def run_p002_execution_backtest(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    scenario: str,
    initial_cash: float = 1.0,
) -> P002ExecutionResult:
    # Closed-strategy guard hardening per KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE.
    # This strategy remains CLOSED under Research Freeze v2; the assert ensures any
    # accidental reactivation fails closed without a quarantine-annotated panel.
    assert_panel_has_valid_mask(panel, context="src/strategies/p002_d013_execution.py:run_p002_execution_backtest")
    if scenario not in SCENARIOS:
        raise ValueError(f"Unsupported P002 scenario: {scenario!r}.")
    spec = SCENARIOS[scenario]
    entry_column = str(spec["entry_price"])
    exit_column = str(spec["exit_price"])
    deploy_fraction = float(spec["deploy_fraction"])
    cash_fallback = bool(spec["cash_fallback"])
    delay = int(spec["delay_trading_days"])

    shifted = p002_shift_candidates(candidates, calendar, delay_trading_days=delay, segments=segments)
    prices = _PriceLookup(panel, (entry_column, exit_column))
    period_dates = _segment_dates(calendar, segments)
    rebalance_dates = p002_rebalance_dates(
        calendar=calendar,
        quarterly_regime=quarterly_regime,
        segments=segments,
        delay_trading_days=delay,
    )
    execution_dates = set(rebalance_dates)
    execution_dates.update(pd.Timestamp(date).normalize() for date in shifted["execution_date"].unique())
    candidates_by_execution = {
        date: group.sort_values(["rank", "종목코드"]).reset_index(drop=True)
        for date, group in shifted.groupby("execution_date", sort=False)
    }

    cash = float(initial_cash)
    positions: dict[str, _Position] = {}
    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []
    fallback_rows: list[dict[str, object]] = []

    for current_date in period_dates:
        if current_date in execution_dates:
            target = candidates_by_execution.get(current_date, pd.DataFrame())
            cash = _close_all(
                current_date=current_date,
                positions=positions,
                prices=prices,
                price_column=exit_column,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
                exit_reason="quarterly_rebalance",
            )
            if not target.empty:
                cash = _open_targets(
                    current_date=current_date,
                    target=target,
                    positions=positions,
                    prices=prices,
                    price_column=entry_column,
                    costs=costs,
                    cash=cash,
                    deploy_fraction=deploy_fraction,
                    cash_fallback=cash_fallback,
                    fallback_rows=fallback_rows,
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
        period_end_exit_column = exit_column if scenario == "D_unfavorable_fill" else "KRX종가"
        cash = _close_all(
            current_date=period_dates[-1],
            positions=positions,
            prices=prices,
            price_column=period_end_exit_column,
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

    return P002ExecutionResult(
        result=BacktestResult(
            trades=pd.DataFrame(trade_rows, columns=TRADE_COLUMNS),
            equity_curve=pd.DataFrame(equity_rows, columns=EQUITY_COLUMNS),
        ),
        candidates=shifted,
        fallback_events=pd.DataFrame(
            fallback_rows,
            columns=("execution_date", "signal_date", "종목코드", "reason"),
        ),
    )


def _open_targets(
    *,
    current_date: pd.Timestamp,
    target: pd.DataFrame,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    price_column: str,
    costs: Costs,
    cash: float,
    deploy_fraction: float,
    cash_fallback: bool,
    fallback_rows: list[dict[str, object]],
) -> float:
    allocation = cash * deploy_fraction / len(target)
    for _, row in target.iterrows():
        ticker = str(row["종목코드"])
        signal_date = pd.Timestamp(row["signal_date"]).normalize()
        if cash_fallback and prices.is_fallback_ticker(ticker, current_date):
            fallback_rows.append(
                {
                    "execution_date": current_date,
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "reason": "status_or_missing_row",
                }
            )
            continue
        entry_price = prices.price(ticker, current_date, price_column)
        if pd.isna(entry_price):
            fallback_rows.append(
                {
                    "execution_date": current_date,
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "reason": f"missing_{price_column}",
                }
            )
            continue
        cost_paid = buy_cost(allocation, costs)
        if allocation + cost_paid > cash:
            allocation = cash / (1.0 + (costs.commission_bps + costs.slippage_bps) / 1e4)
            cost_paid = buy_cost(allocation, costs)
        cash -= allocation + cost_paid
        positions[ticker] = _Position(
            ticker=ticker,
            entry_date=current_date,
            signal_date=signal_date,
            entry_price=entry_price,
            shares=allocation / entry_price,
            notional_at_entry=allocation,
            buy_cost_paid=cost_paid,
        )
    return cash


def _close_all(
    *,
    current_date: pd.Timestamp,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    price_column: str,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    for ticker in list(positions):
        exit_price = prices.price(ticker, current_date, price_column)
        if pd.isna(exit_price):
            continue
        position = positions.pop(ticker)
        exit_notional = position.shares * exit_price
        sell_cost_paid = sell_cost(exit_notional, costs)
        cash += exit_notional - sell_cost_paid
        trade_rows.append(
            {
                "entry_date": position.entry_date,
                "signal_date": position.signal_date,
                "exit_date": current_date,
                "종목코드": position.ticker,
                "entry_price": position.entry_price,
                "exit_price": exit_price,
                "shares": position.shares,
                "notional_at_entry": position.notional_at_entry,
                "buy_cost": position.buy_cost_paid,
                "sell_cost": sell_cost_paid,
                "exit_reason": exit_reason,
            }
        )
    return cash


def _mark_to_market(positions: dict[str, _Position], prices: _PriceLookup, current_date: pd.Timestamp) -> float:
    total = 0.0
    for position in positions.values():
        close_price = prices.close(position.ticker, current_date)
        if pd.isna(close_price):
            close_price = position.entry_price
        total += position.shares * close_price
    return total


def _add_or_nat(calendar: KRXTradingCalendar, date: object, delay_trading_days: int) -> pd.Timestamp:
    try:
        return calendar.add_trading_days(pd.Timestamp(date).normalize(), delay_trading_days)
    except ValueError:
        return pd.NaT
