from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost, sell_cost
from src.backtest.engine import BacktestResult, EQUITY_COLUMNS, TRADE_COLUMNS
from src.roles.exits import exit_on_gate_off
from src.strategies.b004_regime_gate import build_gate_only_equal_weight_candidates
from src.strategies.b011_gate_only_full_timeline import build_kospi_buy_and_hold_result
from src.utils.ohlcv_quarantine import assert_panel_has_valid_mask


VARIANTS = ("macro_gate_mcap", "kospi_buy_and_hold", "cash")


def run_c003_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    monthly_regime: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame]]:
    """Run C003's monthly macro-gated top-mcap strategy and comparators."""
    # Closed-strategy guard hardening per KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE.
    assert_panel_has_valid_mask(panel, context="src/strategies/c003_monthly_macro_gate.py:run_c003_variants")
    gate = _monthly_gate_series(monthly_regime)
    candidates = build_gate_only_equal_weight_candidates(
        panel,
        universe,
        gate,
        max_positions=max_positions,
    )
    candidates = _monthly_execution_candidates(candidates, calendar, monthly_regime, segments)
    gate_exit_kwargs = exit_on_gate_off(_gate_off_flip_dates(gate))
    del gate_exit_kwargs

    runs = {
        "macro_gate_mcap": run_monthly_mcap_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=monthly_execution_dates(calendar, monthly_regime, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            market_breadth,
            calendar=calendar,
            segments=segments,
        ),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    return runs, {"macro_gate_mcap": candidates, "kospi_buy_and_hold": _empty_candidates(), "cash": _empty_candidates()}


def run_monthly_mcap_backtest(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    initial_cash: float = 1.0,
    rebalance_dates: set[pd.Timestamp] | None = None,
) -> BacktestResult:
    """Run a monthly open-to-open rebalance loop without touching the daily engine."""
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
                exit_reason="monthly_rebalance",
            )
            if not target.empty:
                cash = _open_equal_weight_positions(
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
    def __init__(self, panel: pd.DataFrame) -> None:
        required = ("날짜", "종목코드", "시가", "KRX종가")
        missing = [column for column in required if column not in panel.columns]
        if missing:
            raise ValueError(f"panel is missing required price columns: {missing}")
        data = panel.loc[:, list(required)].copy()
        data["날짜"] = pd.to_datetime(data["날짜"], errors="raise").dt.normalize()
        data["종목코드"] = data["종목코드"].astype("string")
        if data.duplicated(["날짜", "종목코드"]).any():
            raise ValueError("panel contains duplicate rows for (날짜, 종목코드).")
        self._open = data.set_index(["날짜", "종목코드"])["시가"]
        self._close = data.set_index(["날짜", "종목코드"])["KRX종가"]

    def open(self, ticker: str, date: pd.Timestamp) -> float:
        return float(self._open.get((pd.Timestamp(date).normalize(), ticker), float("nan")))

    def close(self, ticker: str, date: pd.Timestamp) -> float:
        return float(self._close.get((pd.Timestamp(date).normalize(), ticker), float("nan")))


def _open_equal_weight_positions(
    *,
    current_date: pd.Timestamp,
    target: pd.DataFrame,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    costs: Costs,
    cash: float,
) -> float:
    tickers = target["종목코드"].astype(str).tolist()
    allocation = cash / len(tickers)
    for _, row in target.iterrows():
        ticker = str(row["종목코드"])
        entry_price = prices.open(ticker, current_date)
        if pd.isna(entry_price) or entry_price <= 0.0:
            continue
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


def _close_all_at_open(
    *,
    current_date: pd.Timestamp,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    costs: Costs,
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
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason=exit_reason,
        )
    return cash


def _close_all_at_close(
    *,
    current_date: pd.Timestamp,
    positions: dict[str, _Position],
    prices: _PriceLookup,
    costs: Costs,
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
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason=exit_reason,
        )
    return cash


def _close_position(
    *,
    position: _Position,
    exit_date: pd.Timestamp,
    exit_price: float,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    exit_notional = position.shares * exit_price
    sell_cost_paid = sell_cost(exit_notional, costs)
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


def _monthly_gate_series(monthly_regime: pd.DataFrame) -> pd.Series:
    data = monthly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    return pd.Series(data["regime_on"].to_numpy(dtype=bool), index=pd.Index(data["signal_date"], name="signal_date"))


def _monthly_execution_candidates(
    candidates: pd.DataFrame,
    calendar: KRXTradingCalendar,
    monthly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
) -> pd.DataFrame:
    if candidates.empty:
        return candidates.copy()
    segment_dates = set(_segment_dates(calendar, segments))
    monthly_signal_dates = set(pd.to_datetime(monthly_regime["signal_date"], errors="raise").dt.normalize())
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = pd.to_datetime(data["execution_date"], errors="raise").dt.normalize()
    return data.loc[data["signal_date"].isin(monthly_signal_dates) & data["execution_date"].isin(segment_dates)].copy()


def monthly_execution_dates(
    calendar: KRXTradingCalendar,
    monthly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
) -> set[pd.Timestamp]:
    segment_dates = set(_segment_dates(calendar, segments))
    dates: set[pd.Timestamp] = set()
    for signal_date in pd.to_datetime(monthly_regime["signal_date"], errors="raise"):
        try:
            execution_date = calendar.next_trading_day(pd.Timestamp(signal_date).normalize())
        except ValueError:
            continue
        if execution_date in segment_dates:
            dates.add(execution_date)
    return dates


def _gate_off_flip_dates(gate: pd.Series) -> set[pd.Timestamp]:
    normalized = pd.Series(gate.to_numpy(dtype=bool), index=pd.to_datetime(gate.index, errors="raise"))
    previous = normalized.shift(1, fill_value=False)
    flips = normalized.eq(False) & previous.eq(True)
    return {pd.Timestamp(date).normalize() for date in normalized.index[flips]}


def _run_segmented_cash(
    *,
    calendar: KRXTradingCalendar,
    segments: tuple[tuple[object, object], ...],
) -> BacktestResult:
    rows = [
        {
            "date": date,
            "cash": 1.0,
            "mtm_value": 0.0,
            "gross_value": 1.0,
            "net_value": 1.0,
            "n_positions": 0,
        }
        for date in _segment_dates(calendar, segments)
    ]
    return BacktestResult(trades=_empty_trades(), equity_curve=pd.DataFrame(rows, columns=EQUITY_COLUMNS))


def _segment_dates(
    calendar: KRXTradingCalendar,
    segments: tuple[tuple[object, object], ...],
) -> list[pd.Timestamp]:
    dates: list[pd.Timestamp] = []
    for start, end in segments:
        start_ts = pd.Timestamp(start).normalize()
        end_ts = pd.Timestamp(end).normalize()
        dates.extend(date for date in calendar.dates if start_ts <= date <= end_ts)
    return dates


def _empty_candidates() -> pd.DataFrame:
    return pd.DataFrame(columns=["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"])


def _empty_trades() -> pd.DataFrame:
    return pd.DataFrame(columns=TRADE_COLUMNS)
