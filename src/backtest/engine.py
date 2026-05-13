from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost, sell_cost


TRADE_COLUMNS = (
    "entry_date",
    "signal_date",
    "exit_date",
    "종목코드",
    "entry_price",
    "exit_price",
    "shares",
    "notional_at_entry",
    "buy_cost",
    "sell_cost",
    "exit_reason",
)
EQUITY_COLUMNS = (
    "date",
    "cash",
    "mtm_value",
    "gross_value",
    "net_value",
    "n_positions",
)
PANEL_REQUIRED_COLUMNS = ("날짜", "종목코드", "시가", "KRX종가")
FEATURE_REQUIRED_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
)
UNIVERSE_REQUIRED_COLUMNS = ("execution_date", "signal_date", "종목코드")
CANDIDATE_REQUIRED_COLUMNS = ("execution_date", "signal_date", "종목코드")


@dataclass(frozen=True)
class BacktestResult:
    trades: pd.DataFrame
    equity_curve: pd.DataFrame


@dataclass
class _Slot:
    ticker: str
    entry_date: pd.Timestamp
    entry_price: float
    shares: float
    notional_at_entry: float
    buy_cost_paid: float
    exit_date: pd.Timestamp
    signal_date: pd.Timestamp
    exit_reason: str = "holding_period"
    stop_price: float | None = None
    cap_exit_date: pd.Timestamp | None = None
    pending_stop_exit_date: pd.Timestamp | None = None
    pending_stop_fallback: bool = False
    last_close: float | None = None


def run_headline_backtest(
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    period_start: object,
    period_end: object,
    *,
    max_positions: int = 5,
    holding: int = 5,
    initial_cash: float = 1.0,
) -> BacktestResult:
    """Run the E001 headline slot-based fixed-holding backtest."""
    from src.strategies.e001_flow_filter import build_e001_flow_filter_candidates

    _validate_inputs(panel, flow_features, universe)
    candidates = build_e001_flow_filter_candidates(flow_features, universe)
    return run_candidate_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=costs,
        period_start=period_start,
        period_end=period_end,
        max_positions=max_positions,
        holding=holding,
        initial_cash=initial_cash,
    )


def run_candidate_backtest(
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    period_start: object,
    period_end: object,
    *,
    max_positions: int = 5,
    holding: int = 5,
    initial_cash: float = 1.0,
    vol_stop_k: float | None = None,
    vol_stop_atr_window: int = 20,
    atr_features: pd.DataFrame | None = None,
) -> BacktestResult:
    """Run the slot-based engine on pre-ranked entry candidates."""
    if max_positions <= 0:
        raise ValueError("max_positions must be positive.")
    if holding <= 0:
        raise ValueError("holding must be positive.")

    _validate_candidate_inputs(panel, candidates)
    atr_lookup = _ATRLookup(atr_features, vol_stop_atr_window) if vol_stop_k is not None else None
    prices = _PriceLookup(panel)
    period_dates = _period_dates(calendar, period_start, period_end)
    if not period_dates:
        return BacktestResult(_empty_trades(), _empty_equity_curve())

    cash = float(initial_cash)
    slots: list[_Slot | None] = [None] * max_positions
    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []

    for current_date in period_dates:
        exited_tickers: set[str] = set()
        if vol_stop_k is None:
            cash = _process_due_exits(
                current_date=current_date,
                slots=slots,
                prices=prices,
                calendar=calendar,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
            )
        else:
            cash = _process_pending_stop_exits(
                current_date=current_date,
                slots=slots,
                prices=prices,
                calendar=calendar,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
                exited_tickers=exited_tickers,
            )

        mtm_before_entries = _mtm_value(slots, prices, current_date)
        nav_for_entries = cash + mtm_before_entries

        cash = _process_entries(
            current_date=current_date,
            slots=slots,
            prices=prices,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            nav_for_entries=nav_for_entries,
            cash=cash,
            max_positions=max_positions,
            holding=holding,
            vol_stop_k=vol_stop_k,
            atr_lookup=atr_lookup,
            exited_tickers=exited_tickers,
        )

        if vol_stop_k is not None:
            cash = _process_dynamic_close_rules(
                current_date=current_date,
                slots=slots,
                prices=prices,
                calendar=calendar,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
                exited_tickers=exited_tickers,
            )

        mtm_after_entries = _mtm_value(slots, prices, current_date)
        equity_value = cash + mtm_after_entries
        equity_rows.append(
            {
                "date": current_date,
                "cash": cash,
                "mtm_value": mtm_after_entries,
                "gross_value": equity_value,
                "net_value": equity_value,
                "n_positions": sum(slot is not None for slot in slots),
            }
        )

    cash = _force_period_end_exits(
        current_date=period_dates[-1],
        slots=slots,
        prices=prices,
        costs=costs,
        cash=cash,
        trade_rows=trade_rows,
    )
    if equity_rows:
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


def _process_due_exits(
    *,
    current_date: pd.Timestamp,
    slots: list[_Slot | None],
    prices: _PriceLookup,
    calendar: KRXTradingCalendar,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
) -> float:
    for index, slot in enumerate(slots):
        if slot is None or slot.exit_date != current_date:
            continue

        exit_price = prices.close(slot.ticker, current_date)
        if pd.isna(exit_price):
            slot.exit_date = prices.next_non_null_close_date(slot.ticker, current_date, calendar)
            slot.exit_reason = "missing_price_fallback"
            continue

        cash = _close_slot(
            slot=slot,
            exit_date=current_date,
            exit_price=float(exit_price),
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
        )
        slots[index] = None
    return cash


def _process_entries(
    *,
    current_date: pd.Timestamp,
    slots: list[_Slot | None],
    prices: _PriceLookup,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    costs: Costs,
    nav_for_entries: float,
    cash: float,
    max_positions: int,
    holding: int,
    vol_stop_k: float | None = None,
    atr_lookup: _ATRLookup | None = None,
    exited_tickers: set[str] | None = None,
) -> float:
    open_slots = [index for index, slot in enumerate(slots) if slot is None]
    if not open_slots or pd.isna(nav_for_entries):
        return cash

    try:
        scheduled_exit_date: pd.Timestamp = calendar.add_trading_days(current_date, holding)
    except ValueError:
        scheduled_exit_date = pd.NaT

    held_tickers = {slot.ticker for slot in slots if slot is not None}
    if exited_tickers:
        held_tickers.update(exited_tickers)
    todays_candidates = candidates.loc[candidates["execution_date"] == current_date]
    todays_candidates = todays_candidates.loc[~todays_candidates["종목코드"].isin(held_tickers)]
    todays_candidates = todays_candidates.head(len(open_slots))

    for slot_index, (_, row) in zip(open_slots, todays_candidates.iterrows(), strict=False):
        ticker = row["종목코드"]
        entry_price = prices.open(ticker, current_date)
        if pd.isna(entry_price):
            continue
        signal_date = pd.Timestamp(row["signal_date"]).normalize()

        stop_price: float | None = None
        cap_exit_date = scheduled_exit_date
        exit_reason = "holding_period"
        if vol_stop_k is not None:
            if atr_lookup is None:
                raise ValueError("atr_features is required when vol_stop_k is set.")
            atr_pct = atr_lookup.value(ticker, signal_date)
            if pd.isna(atr_pct):
                continue
            stop_price = float(entry_price) * (1.0 - float(vol_stop_k) * float(atr_pct))
            exit_reason = "time_cap"

        notional = float(nav_for_entries) / max_positions
        cost_paid = buy_cost(notional, costs)
        cash -= notional + cost_paid
        slots[slot_index] = _Slot(
            ticker=ticker,
            entry_date=current_date,
            entry_price=float(entry_price),
            shares=notional / float(entry_price),
            notional_at_entry=notional,
            buy_cost_paid=cost_paid,
            exit_date=scheduled_exit_date,
            signal_date=signal_date,
            exit_reason=exit_reason,
            stop_price=stop_price,
            cap_exit_date=cap_exit_date,
        )

    return cash


def _process_pending_stop_exits(
    *,
    current_date: pd.Timestamp,
    slots: list[_Slot | None],
    prices: _PriceLookup,
    calendar: KRXTradingCalendar,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exited_tickers: set[str],
) -> float:
    for index, slot in enumerate(slots):
        if slot is None or slot.pending_stop_exit_date != current_date:
            continue

        exit_price = prices.open(slot.ticker, current_date)
        if pd.isna(exit_price):
            slot.pending_stop_exit_date = _next_trading_day_or_nat(calendar, current_date)
            slot.pending_stop_fallback = True
            continue

        reason = "vol_stop_fallback" if slot.pending_stop_fallback else "vol_stop"
        cash = _close_slot(
            slot=slot,
            exit_date=current_date,
            exit_price=float(exit_price),
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason=reason,
        )
        exited_tickers.add(slot.ticker)
        slots[index] = None
    return cash


def _process_dynamic_close_rules(
    *,
    current_date: pd.Timestamp,
    slots: list[_Slot | None],
    prices: _PriceLookup,
    calendar: KRXTradingCalendar,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exited_tickers: set[str],
) -> float:
    for index, slot in enumerate(slots):
        if slot is None or slot.ticker in exited_tickers:
            continue

        close_price = prices.close(slot.ticker, current_date)
        if not pd.isna(close_price):
            slot.last_close = float(close_price)

        if current_date <= slot.entry_date:
            continue

        if not pd.isna(close_price) and slot.stop_price is not None and float(close_price) <= slot.stop_price:
            slot.pending_stop_exit_date = _next_trading_day_or_nat(calendar, current_date)
            slot.pending_stop_fallback = False
            continue

        if slot.cap_exit_date is not None and current_date >= slot.cap_exit_date:
            if pd.isna(close_price):
                slot.cap_exit_date = _next_trading_day_or_nat(calendar, current_date)
                slot.exit_reason = "time_cap_fallback"
                continue
            cash = _close_slot(
                slot=slot,
                exit_date=current_date,
                exit_price=float(close_price),
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
                exit_reason=slot.exit_reason,
            )
            exited_tickers.add(slot.ticker)
            slots[index] = None
    return cash


def _force_period_end_exits(
    *,
    current_date: pd.Timestamp,
    slots: list[_Slot | None],
    prices: _PriceLookup,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
) -> float:
    for index, slot in enumerate(slots):
        if slot is None:
            continue
        exit_price = prices.close(slot.ticker, current_date)
        if pd.isna(exit_price) and slot.stop_price is not None and slot.last_close is not None:
            exit_price = slot.last_close
        cash = _close_slot(
            slot=slot,
            exit_date=current_date,
            exit_price=float(exit_price),
            costs=costs,
            cash=cash,
            trade_rows=trade_rows,
            exit_reason="period_end",
        )
        slots[index] = None
    return cash


def _close_slot(
    *,
    slot: _Slot,
    exit_date: pd.Timestamp,
    exit_price: float,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str | None = None,
) -> float:
    exit_notional = slot.shares * exit_price
    sell_cost_paid = sell_cost(exit_notional, costs)
    trade_rows.append(
        {
            "entry_date": slot.entry_date,
            "signal_date": slot.signal_date,
            "exit_date": exit_date,
            "종목코드": slot.ticker,
            "entry_price": slot.entry_price,
            "exit_price": exit_price,
            "shares": slot.shares,
            "notional_at_entry": slot.notional_at_entry,
            "buy_cost": slot.buy_cost_paid,
            "sell_cost": sell_cost_paid,
            "exit_reason": exit_reason or slot.exit_reason,
        }
    )
    return cash + exit_notional - sell_cost_paid


def _mtm_value(
    slots: list[_Slot | None],
    prices: _PriceLookup,
    current_date: pd.Timestamp,
) -> float:
    values = []
    for slot in slots:
        if slot is None:
            continue
        close_price = prices.close(slot.ticker, current_date)
        if pd.isna(close_price):
            if slot.stop_price is None or slot.last_close is None:
                return float("nan")
            close_price = slot.last_close
        else:
            if slot.stop_price is not None:
                slot.last_close = float(close_price)
        values.append(slot.shares * float(close_price))
    return float(sum(values))


class _ATRLookup:
    def __init__(self, atr_features: pd.DataFrame | None, window: int) -> None:
        if atr_features is None:
            raise ValueError("atr_features is required when vol_stop_k is set.")
        feature_column = f"atr_pct_{window}"
        _require_columns(atr_features, ("날짜", "종목코드", feature_column), "atr_features")
        features = atr_features.loc[:, ["날짜", "종목코드", feature_column]].copy()
        features["날짜"] = pd.to_datetime(features["날짜"], errors="raise").astype("datetime64[ns]")
        features["종목코드"] = features["종목코드"].astype("string")
        if features.duplicated(["날짜", "종목코드"]).any():
            raise ValueError("ATR features contain duplicate rows for (날짜, 종목코드).")
        self._feature_column = feature_column
        self._features = features.set_index(["날짜", "종목코드"]).sort_index()

    def value(self, ticker: str, date: pd.Timestamp) -> float:
        key = (pd.Timestamp(date).normalize(), ticker)
        if key not in self._features.index:
            raise ValueError(f"Missing ATR feature for ticker {ticker} on {pd.Timestamp(date).date()}.")
        value = self._features.loc[key, self._feature_column]
        if pd.isna(value):
            return float("nan")
        return float(value)


class _PriceLookup:
    def __init__(self, panel: pd.DataFrame) -> None:
        prices = panel.loc[:, ["날짜", "종목코드", "시가", "KRX종가"]].copy()
        prices["날짜"] = pd.to_datetime(prices["날짜"], errors="raise").astype("datetime64[ns]")
        prices["종목코드"] = prices["종목코드"].astype("string")
        if prices.duplicated(["날짜", "종목코드"]).any():
            raise ValueError("Panel contains duplicate rows for (날짜, 종목코드).")
        self._prices = prices.set_index(["날짜", "종목코드"]).sort_index()

    def open(self, ticker: str, date: pd.Timestamp) -> float:
        return self._value(ticker, date, "시가")

    def close(self, ticker: str, date: pd.Timestamp) -> float:
        return self._value(ticker, date, "KRX종가")

    def next_non_null_close_date(
        self,
        ticker: str,
        date: pd.Timestamp,
        calendar: KRXTradingCalendar,
    ) -> pd.Timestamp:
        for candidate_date in calendar.dates:
            if candidate_date <= date:
                continue
            close_price = self.close(ticker, candidate_date)
            if not pd.isna(close_price):
                return candidate_date
        raise ValueError(f"No non-null KRX종가 after {date.date()} for ticker {ticker}.")

    def _value(self, ticker: str, date: pd.Timestamp, column: str) -> float:
        key = (pd.Timestamp(date).normalize(), ticker)
        if key not in self._prices.index:
            return float("nan")
        value = self._prices.loc[key, column]
        if pd.isna(value) or value <= 0:
            return float("nan")
        return float(value)


def _period_dates(
    calendar: KRXTradingCalendar,
    period_start: object,
    period_end: object,
) -> list[pd.Timestamp]:
    start = pd.Timestamp(period_start).normalize()
    end = pd.Timestamp(period_end).normalize()
    return [date for date in calendar.dates if start <= date <= end]


def _next_trading_day_or_nat(calendar: KRXTradingCalendar, date: pd.Timestamp) -> pd.Timestamp:
    try:
        return calendar.next_trading_day(date)
    except ValueError:
        return pd.NaT


def _empty_trades() -> pd.DataFrame:
    return pd.DataFrame(columns=TRADE_COLUMNS)


def _empty_equity_curve() -> pd.DataFrame:
    return pd.DataFrame(columns=EQUITY_COLUMNS)


def _validate_inputs(
    panel: pd.DataFrame,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> None:
    _require_columns(panel, PANEL_REQUIRED_COLUMNS, "panel")
    _require_columns(flow_features, FEATURE_REQUIRED_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_REQUIRED_COLUMNS, "universe")


def _validate_candidate_inputs(panel: pd.DataFrame, candidates: pd.DataFrame) -> None:
    _require_columns(panel, PANEL_REQUIRED_COLUMNS, "panel")
    _require_columns(candidates, CANDIDATE_REQUIRED_COLUMNS, "candidates")


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
