from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, EQUITY_COLUMNS, TRADE_COLUMNS, run_candidate_backtest
from src.features.regime import regime_gate_on
from src.roles.exits import exit_on_gate_off
from src.strategies.b004_regime_gate import build_gate_only_equal_weight_candidates


VARIANTS = ("gate_only_mcap", "kospi_buy_and_hold", "cash")


def run_b011_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    universe: pd.DataFrame,
    kospi_proxy: pd.DataFrame,
    market_breadth: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], pd.Series]:
    """Run B011's frozen B004(c) gate-only strategy and passive comparators."""
    gate = regime_gate_on(kospi_proxy)
    gate_candidates = build_gate_only_equal_weight_candidates(
        panel,
        universe,
        gate,
        max_positions=max_positions,
    )
    gate_exit_kwargs = exit_on_gate_off(_gate_off_flip_dates(gate))
    gate_only = _run_segmented_gate_only(
        panel=panel,
        calendar=calendar,
        candidates=gate_candidates,
        universe=universe,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
        exit_kwargs=gate_exit_kwargs,
    )
    passive = build_kospi_buy_and_hold_result(
        market_breadth,
        calendar=calendar,
        segments=segments,
    )
    cash = _run_segmented_cash(calendar=calendar, segments=segments)
    candidates = {
        "gate_only_mcap": gate_candidates,
        "kospi_buy_and_hold": _empty_candidates(),
        "cash": _empty_candidates(),
    }
    runs = {
        "gate_only_mcap": gate_only,
        "kospi_buy_and_hold": passive,
        "cash": cash,
    }
    return runs, candidates, gate


def build_kospi_buy_and_hold_result(
    market_breadth: pd.DataFrame,
    *,
    calendar: KRXTradingCalendar,
    segments: tuple[tuple[object, object], ...],
) -> BacktestResult:
    """Build V2 directly from cap_weighted_return, normalized to 1.0 on start."""
    _require_columns(market_breadth, ("date", "cap_weighted_return"), "market_breadth")
    data = market_breadth.loc[:, ["date", "cap_weighted_return"]].copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    data["cap_weighted_return"] = pd.to_numeric(data["cap_weighted_return"], errors="raise")
    if data["date"].duplicated().any():
        raise ValueError("market_breadth contains duplicate date rows.")
    data = data.set_index("date").sort_index()

    dates = _segment_dates(calendar, segments)
    returns = data.reindex(dates)["cap_weighted_return"]
    if returns.isna().any():
        missing = [date.date().isoformat() for date in returns.index[returns.isna()]]
        raise ValueError(f"market_breadth is missing cap_weighted_return for dates: {missing[:5]}")

    values = (1.0 + returns).cumprod()
    if not values.empty:
        values = values / float(values.iloc[0])
    equity = pd.DataFrame(
        {
            "date": list(returns.index),
            "cash": 0.0,
            "mtm_value": values.to_numpy(),
            "gross_value": values.to_numpy(),
            "net_value": values.to_numpy(),
            "n_positions": 1,
        },
        columns=EQUITY_COLUMNS,
    )
    return BacktestResult(trades=_empty_trades(), equity_curve=equity)


def _run_segmented_gate_only(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    candidates: pd.DataFrame,
    universe: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    max_positions: int,
    exit_kwargs: dict[str, object],
) -> BacktestResult:
    trade_frames: list[pd.DataFrame] = []
    equity_frames: list[pd.DataFrame] = []
    initial_cash = 1.0
    universe_signal_tickers = _universe_signal_tickers(universe)
    for start, end in segments:
        result = run_candidate_backtest(
            panel,
            calendar,
            candidates,
            costs,
            start,
            end,
            max_positions=max_positions,
            initial_cash=initial_cash,
            universe_exit_signal_tickers=universe_signal_tickers,
            **exit_kwargs,
        )
        trade_frames.append(result.trades)
        equity_frames.append(result.equity_curve)
        if not result.equity_curve.empty:
            initial_cash = float(result.equity_curve["net_value"].iloc[-1])
    return BacktestResult(
        trades=pd.concat(trade_frames, ignore_index=True) if trade_frames else _empty_trades(),
        equity_curve=pd.concat(equity_frames, ignore_index=True) if equity_frames else _empty_equity(),
    )


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


def _gate_off_flip_dates(gate: pd.Series) -> set[pd.Timestamp]:
    normalized = pd.Series(gate.to_numpy(dtype=bool), index=pd.to_datetime(gate.index, errors="raise"))
    previous = normalized.shift(1, fill_value=False)
    flips = normalized.eq(False) & previous.eq(True)
    return {pd.Timestamp(date).normalize() for date in normalized.index[flips]}


def _universe_signal_tickers(universe: pd.DataFrame) -> set[tuple[pd.Timestamp, str]]:
    return {
        (pd.Timestamp(signal_date).normalize(), str(ticker))
        for signal_date, ticker in zip(universe["signal_date"], universe["종목코드"], strict=False)
    }


def _empty_candidates() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"]
    )


def _empty_trades() -> pd.DataFrame:
    return pd.DataFrame(columns=TRADE_COLUMNS)


def _empty_equity() -> pd.DataFrame:
    return pd.DataFrame(columns=EQUITY_COLUMNS)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
