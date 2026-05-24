from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs, buy_cost, sell_cost
from src.backtest.engine import (
    BacktestResult,
    EQUITY_COLUMNS,
    TRADE_COLUMNS,
    run_candidate_backtest,
)
from src.roles.rankings import rank_by_recent_return_5
from src.utils.ohlcv_quarantine import assert_panel_has_valid_mask


BASELINE_NAMES = ("B0_cash", "B1_buy_and_hold", "B2_universe_5d_rebalance", "B3_price_momentum")


def run_baseline(
    name: str,
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
    """Run one E001 baseline by name."""
    # Closed-strategy guard hardening per KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE.
    assert_panel_has_valid_mask(panel, context=f"src/strategies/baselines.py:run_baseline[{name}]")
    runners: dict[str, Callable[..., BacktestResult]] = {
        "B0_cash": run_b0_cash,
        "B1_buy_and_hold": run_b1_buy_and_hold,
        "B2_universe_5d_rebalance": run_b2_universe_5d_rebalance,
        "B3_price_momentum": run_b3_price_momentum,
    }
    if name not in runners:
        raise ValueError(f"Unknown baseline {name!r}; expected one of {BASELINE_NAMES}.")
    return runners[name](
        panel,
        calendar,
        flow_features,
        universe,
        costs,
        period_start,
        period_end,
        max_positions=max_positions,
        holding=holding,
        initial_cash=initial_cash,
    )


def run_b0_cash(
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
    del panel, flow_features, universe, costs, max_positions, holding
    rows = [
        {
            "date": date,
            "cash": float(initial_cash),
            "mtm_value": 0.0,
            "gross_value": float(initial_cash),
            "net_value": float(initial_cash),
            "n_positions": 0,
        }
        for date in _period_dates(calendar, period_start, period_end)
    ]
    return BacktestResult(_empty_trades(), pd.DataFrame(rows, columns=EQUITY_COLUMNS))


def run_b1_buy_and_hold(
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
    """Buy all first-day eligible universe names and hold.

    Pass the diagnostic universe slice built with
    exclude_estimated_flag_rows=False; B1 is a universe ownership baseline,
    so it must not be penalized by E001's headline estimate-row filter.
    """
    del flow_features, max_positions
    period_dates = _period_dates(calendar, period_start, period_end)
    if not period_dates:
        return BacktestResult(_empty_trades(), _empty_equity_curve())

    prices = _PriceLookup(panel)
    entry_date = period_dates[0]
    tickers = _eligible_tickers(universe, entry_date)
    tickers = [ticker for ticker in tickers if not pd.isna(prices.open(ticker, entry_date))]
    if not tickers:
        return _flat_cash_result(period_dates, initial_cash)

    entry_notional = float(initial_cash) / len(tickers)
    holdings: dict[str, _Holding] = {}
    cash = float(initial_cash)
    for ticker in tickers:
        entry_price = float(prices.open(ticker, entry_date))
        cost_paid = buy_cost(entry_notional, costs)
        cash -= entry_notional + cost_paid
        holdings[ticker] = _Holding(
            ticker=ticker,
            entry_date=entry_date,
            entry_price=entry_price,
            shares=entry_notional / entry_price,
            notional_at_entry=entry_notional,
            buy_cost_paid=cost_paid,
            signal_date=entry_date,
        )

    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []
    missing_streaks = {ticker: 0 for ticker in holdings}
    last_closes = {
        ticker: prices.close(ticker, entry_date)
        for ticker in holdings
        if not pd.isna(prices.close(ticker, entry_date))
    }

    for current_date in period_dates:
        for ticker, holding_row in list(holdings.items()):
            close_price = prices.close(ticker, current_date)
            if pd.isna(close_price):
                missing_streaks[ticker] += 1
                if missing_streaks[ticker] >= holding and ticker in last_closes:
                    cash = _close_holding(
                        holding_row,
                        current_date,
                        float(last_closes[ticker]),
                        costs,
                        cash,
                        trade_rows,
                        "missing_price_fallback",
                    )
                    del holdings[ticker]
                continue

            missing_streaks[ticker] = 0
            last_closes[ticker] = float(close_price)

        equity_rows.append(_equity_row(current_date, cash, holdings, prices))

    period_end_date = period_dates[-1]
    for ticker, holding_row in list(holdings.items()):
        close_price = prices.close(ticker, period_end_date)
        if pd.isna(close_price):
            close_price = last_closes.get(ticker, float("nan"))
        cash = _close_holding(
            holding_row,
            period_end_date,
            float(close_price),
            costs,
            cash,
            trade_rows,
            "period_end",
        )
        del holdings[ticker]

    equity_rows[-1] = _closed_equity_row(period_end_date, cash)
    return BacktestResult(
        pd.DataFrame(trade_rows, columns=TRADE_COLUMNS),
        pd.DataFrame(equity_rows, columns=EQUITY_COLUMNS),
    )


def run_b2_universe_5d_rebalance(
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
    """Rebalance every five KRX days into the full eligible universe.

    Pass the diagnostic universe slice built with
    exclude_estimated_flag_rows=False; B2 is a universe ownership baseline,
    so it must not be penalized by E001's headline estimate-row filter.
    """
    del flow_features, max_positions
    period_dates = _period_dates(calendar, period_start, period_end)
    if not period_dates:
        return BacktestResult(_empty_trades(), _empty_equity_curve())

    prices = _PriceLookup(panel)
    rebalance_dates = set(_rebalance_dates(period_dates, holding))
    holdings: dict[str, _Lot] = {}
    cash = float(initial_cash)
    trade_rows: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []

    for current_date in period_dates:
        if current_date in rebalance_dates:
            cash = _rebalance_equal_weight(
                current_date=current_date,
                holdings=holdings,
                target_tickers=_eligible_tickers(universe, current_date),
                prices=prices,
                costs=costs,
                cash=cash,
                trade_rows=trade_rows,
            )
        equity_rows.append(_equity_row(current_date, cash, holdings, prices))

    period_end_date = period_dates[-1]
    for ticker, lot in list(holdings.items()):
        close_price = prices.close(ticker, period_end_date)
        if pd.isna(close_price):
            continue
        cash = _close_lot(
            lot,
            period_end_date,
            float(close_price),
            costs,
            cash,
            trade_rows,
            "period_end",
        )
        del holdings[ticker]

    equity_rows[-1] = _closed_equity_row(period_end_date, cash)
    return BacktestResult(
        pd.DataFrame(trade_rows, columns=TRADE_COLUMNS),
        pd.DataFrame(equity_rows, columns=EQUITY_COLUMNS),
    )


def run_b3_price_momentum(
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
    candidates = build_price_momentum_candidates(flow_features, universe)
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


def build_price_momentum_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> pd.DataFrame:
    feature_columns = ("execution_date", "signal_date", "종목코드", "recent_return_5")
    _require_columns(flow_features, feature_columns, "flow_features")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")
    merged = universe.merge(
        flow_features.loc[:, list(feature_columns)],
        on=["execution_date", "signal_date", "종목코드"],
        how="inner",
        validate="one_to_one",
    )
    candidates = merged.loc[merged["recent_return_5"].gt(0)].copy()
    return rank_by_recent_return_5(candidates)


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

    def _value(self, ticker: str, date: pd.Timestamp, column: str) -> float:
        key = (pd.Timestamp(date).normalize(), ticker)
        if key not in self._prices.index:
            return float("nan")
        value = self._prices.loc[key, column]
        if pd.isna(value) or value <= 0:
            return float("nan")
        return float(value)


class _Holding:
    def __init__(
        self,
        *,
        ticker: str,
        entry_date: pd.Timestamp,
        entry_price: float,
        shares: float,
        notional_at_entry: float,
        buy_cost_paid: float,
        signal_date: pd.Timestamp,
    ) -> None:
        self.ticker = ticker
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.notional_at_entry = notional_at_entry
        self.buy_cost_paid = buy_cost_paid
        self.signal_date = signal_date


class _Lot(_Holding):
    pass


def _period_dates(
    calendar: KRXTradingCalendar,
    period_start: object,
    period_end: object,
) -> list[pd.Timestamp]:
    start = pd.Timestamp(period_start).normalize()
    end = pd.Timestamp(period_end).normalize()
    return [date for date in calendar.dates if start <= date <= end]


def _rebalance_dates(period_dates: list[pd.Timestamp], holding: int) -> list[pd.Timestamp]:
    if holding <= 0:
        raise ValueError("holding must be positive.")
    return period_dates[::holding]


def _eligible_tickers(universe: pd.DataFrame, execution_date: pd.Timestamp) -> list[str]:
    _require_columns(universe, ("execution_date", "종목코드"), "universe")
    eligible = universe.loc[universe["execution_date"] == execution_date, "종목코드"]
    return sorted(eligible.astype("string").dropna().unique())


def _rebalance_equal_weight(
    *,
    current_date: pd.Timestamp,
    holdings: dict[str, _Lot],
    target_tickers: list[str],
    prices: _PriceLookup,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
) -> float:
    target_tickers = [ticker for ticker in target_tickers if not pd.isna(prices.open(ticker, current_date))]
    current_nav = cash + _mtm_value(holdings, prices, current_date)
    if not target_tickers or pd.isna(current_nav):
        for ticker, lot in list(holdings.items()):
            exit_price = prices.open(ticker, current_date)
            if pd.isna(exit_price):
                continue
            cash = _close_lot(
                lot,
                current_date,
                float(exit_price),
                costs,
                cash,
                trade_rows,
                "rebalance",
            )
            del holdings[ticker]
        return cash

    target_value = float(current_nav) / len(target_tickers)
    target_set = set(target_tickers)

    for ticker, lot in list(holdings.items()):
        exit_price = prices.open(ticker, current_date)
        if ticker not in target_set:
            if pd.isna(exit_price):
                continue
            cash = _close_lot(
                lot,
                current_date,
                float(exit_price),
                costs,
                cash,
                trade_rows,
                "rebalance",
            )
            del holdings[ticker]
            continue

        current_price = prices.open(ticker, current_date)
        if pd.isna(current_price):
            continue
        current_value = lot.shares * float(current_price)
        if current_value > target_value:
            shares_to_sell = (current_value - target_value) / float(current_price)
            cash = _close_partial_lot(
                lot,
                shares_to_sell,
                current_date,
                float(current_price),
                costs,
                cash,
                trade_rows,
            )

    for ticker in target_tickers:
        entry_price = prices.open(ticker, current_date)
        if pd.isna(entry_price):
            continue
        current_value = 0.0
        if ticker in holdings:
            current_value = holdings[ticker].shares * float(entry_price)
        buy_notional = target_value - current_value
        if buy_notional <= 0:
            continue
        cost_paid = buy_cost(buy_notional, costs)
        cash -= buy_notional + cost_paid
        if ticker in holdings:
            holdings[ticker].shares += buy_notional / float(entry_price)
            holdings[ticker].notional_at_entry += buy_notional
            holdings[ticker].buy_cost_paid += cost_paid
        else:
            holdings[ticker] = _Lot(
                ticker=ticker,
                entry_date=current_date,
                entry_price=float(entry_price),
                shares=buy_notional / float(entry_price),
                notional_at_entry=buy_notional,
                buy_cost_paid=cost_paid,
                signal_date=current_date,
            )
    return cash


def _close_holding(
    holding: _Holding,
    exit_date: pd.Timestamp,
    exit_price: float,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    exit_notional = holding.shares * exit_price
    sell_cost_paid = sell_cost(exit_notional, costs)
    trade_rows.append(
        {
            "entry_date": holding.entry_date,
            "signal_date": holding.signal_date,
            "exit_date": exit_date,
            "종목코드": holding.ticker,
            "entry_price": holding.entry_price,
            "exit_price": exit_price,
            "shares": holding.shares,
            "notional_at_entry": holding.notional_at_entry,
            "buy_cost": holding.buy_cost_paid,
            "sell_cost": sell_cost_paid,
            "exit_reason": exit_reason,
        }
    )
    return cash + exit_notional - sell_cost_paid


def _close_lot(
    lot: _Lot,
    exit_date: pd.Timestamp,
    exit_price: float,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
    exit_reason: str,
) -> float:
    return _close_holding(lot, exit_date, exit_price, costs, cash, trade_rows, exit_reason)


def _close_partial_lot(
    lot: _Lot,
    shares_to_sell: float,
    exit_date: pd.Timestamp,
    exit_price: float,
    costs: Costs,
    cash: float,
    trade_rows: list[dict[str, object]],
) -> float:
    fraction = shares_to_sell / lot.shares
    sold_entry_notional = lot.notional_at_entry * fraction
    sold_buy_cost = lot.buy_cost_paid * fraction
    exit_notional = shares_to_sell * exit_price
    sell_cost_paid = sell_cost(exit_notional, costs)
    trade_rows.append(
        {
            "entry_date": lot.entry_date,
            "signal_date": lot.signal_date,
            "exit_date": exit_date,
            "종목코드": lot.ticker,
            "entry_price": lot.entry_price,
            "exit_price": exit_price,
            "shares": shares_to_sell,
            "notional_at_entry": sold_entry_notional,
            "buy_cost": sold_buy_cost,
            "sell_cost": sell_cost_paid,
            "exit_reason": "rebalance",
        }
    )
    lot.shares -= shares_to_sell
    lot.notional_at_entry -= sold_entry_notional
    lot.buy_cost_paid -= sold_buy_cost
    return cash + exit_notional - sell_cost_paid


def _equity_row(
    date: pd.Timestamp,
    cash: float,
    holdings: dict[str, _Holding],
    prices: _PriceLookup,
) -> dict[str, object]:
    mtm = _mtm_value(holdings, prices, date)
    nav = cash + mtm
    return {
        "date": date,
        "cash": cash,
        "mtm_value": mtm,
        "gross_value": nav,
        "net_value": nav,
        "n_positions": len(holdings),
    }


def _closed_equity_row(date: pd.Timestamp, cash: float) -> dict[str, object]:
    return {
        "date": date,
        "cash": cash,
        "mtm_value": 0.0,
        "gross_value": cash,
        "net_value": cash,
        "n_positions": 0,
    }


def _mtm_value(
    holdings: dict[str, _Holding],
    prices: _PriceLookup,
    date: pd.Timestamp,
) -> float:
    total = 0.0
    for ticker, holding in holdings.items():
        close_price = prices.close(ticker, date)
        if pd.isna(close_price):
            return float("nan")
        total += holding.shares * float(close_price)
    return total


def _flat_cash_result(period_dates: list[pd.Timestamp], initial_cash: float) -> BacktestResult:
    return BacktestResult(
        _empty_trades(),
        pd.DataFrame([_closed_equity_row(date, float(initial_cash)) for date in period_dates]),
    )


def _empty_trades() -> pd.DataFrame:
    return pd.DataFrame(columns=TRADE_COLUMNS)


def _empty_equity_curve() -> pd.DataFrame:
    return pd.DataFrame(columns=EQUITY_COLUMNS)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
