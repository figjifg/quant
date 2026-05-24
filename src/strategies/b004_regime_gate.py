from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.features.regime import regime_gate_on
from src.roles.exits import exit_on_gate_off, exit_signal_reversal
from src.strategies.b002_signal_reversal import build_b002_candidates
from src.utils.ohlcv_quarantine import assert_panel_has_valid_mask


VARIANTS = ("signal_plus_gate", "signal_only", "gate_only_equal_weight", "cash")
MCAP_COLUMNS = ("날짜", "종목코드", "KRX종가", "상장주식수", "시가총액", "시가총액추정")


def build_gate_only_equal_weight_candidates(
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    gate: pd.Series,
    *,
    max_positions: int = 5,
) -> pd.DataFrame:
    """Build variant (c) top-market-cap candidates on gate-on signal dates."""
    if max_positions <= 0:
        raise ValueError("max_positions must be positive.")
    _require_columns(universe, ("execution_date", "signal_date", "종목코드"), "universe")

    mcap = _market_cap_by_signal_date(panel)
    eligible = universe.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    eligible["execution_date"] = pd.to_datetime(eligible["execution_date"], errors="raise").astype("datetime64[ns]")
    eligible["signal_date"] = pd.to_datetime(eligible["signal_date"], errors="raise").astype("datetime64[ns]")
    eligible["종목코드"] = eligible["종목코드"].astype("string")
    gate_on_dates = {pd.Timestamp(date).normalize() for date, on in gate.items() if bool(on)}
    eligible = eligible.loc[eligible["signal_date"].isin(gate_on_dates)]

    ranked = eligible.merge(
        mcap,
        left_on=["signal_date", "종목코드"],
        right_on=["날짜", "종목코드"],
        how="inner",
        validate="one_to_one",
    )
    ranked = ranked.loc[ranked["market_cap"].gt(0)]
    ranked = ranked.sort_values(
        ["signal_date", "market_cap", "종목코드"],
        ascending=[True, False, True],
    )
    ranked["rank"] = ranked.groupby("signal_date").cumcount() + 1
    selected = ranked.loc[ranked["rank"].le(max_positions)].copy()
    selected["fnv_5"] = 0.0
    selected["inv_5"] = 0.0
    selected["combined_flow_5"] = selected["market_cap"]
    columns = ["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5", "market_cap", "rank"]
    return selected.loc[:, columns].reset_index(drop=True)


def run_b004_variants(
    *,
    panel: pd.DataFrame,
    calendar: KRXTradingCalendar,
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    kospi_proxy: pd.DataFrame,
    costs: Costs,
    period_start: object,
    period_end: object,
    max_positions: int,
) -> tuple[dict[str, BacktestResult], dict[str, pd.DataFrame], pd.DataFrame]:
    """Run B004's four pre-registered variants."""
    # Closed-strategy guard hardening per KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE.
    assert_panel_has_valid_mask(panel, context="src/strategies/b004_regime_gate.py:run_b004_variants")
    gate = regime_gate_on(kospi_proxy)
    gate_dates = {pd.Timestamp(date).normalize() for date, on in gate.items() if bool(on)}
    gate_off_flips = _gate_off_flip_dates(gate)
    b002_candidates = build_b002_candidates(flow_features, universe)
    signal_exit_kwargs = exit_signal_reversal(flow_features)
    gate_candidates = build_gate_only_equal_weight_candidates(
        panel,
        universe,
        gate,
        max_positions=max_positions,
    )
    gate_exit_kwargs = exit_on_gate_off(gate_off_flips)

    runs = {
        "signal_plus_gate": run_candidate_backtest(
            panel,
            calendar,
            b002_candidates,
            costs,
            period_start,
            period_end,
            max_positions=max_positions,
            regime_gate_dates=gate_dates,
            **signal_exit_kwargs,
        ),
        "signal_only": run_candidate_backtest(
            panel,
            calendar,
            b002_candidates,
            costs,
            period_start,
            period_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        ),
        "gate_only_equal_weight": run_candidate_backtest(
            panel,
            calendar,
            gate_candidates,
            costs,
            period_start,
            period_end,
            max_positions=max_positions,
            universe_exit_signal_tickers=_universe_signal_tickers(universe),
            **gate_exit_kwargs,
        ),
        "cash": _cash_result(calendar, period_start, period_end),
    }
    candidates = {
        "signal_plus_gate": b002_candidates,
        "signal_only": b002_candidates,
        "gate_only_equal_weight": gate_candidates,
        "cash": pd.DataFrame(columns=["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"]),
    }
    return runs, candidates, gate.to_frame()


def _market_cap_by_signal_date(panel: pd.DataFrame) -> pd.DataFrame:
    required = ("날짜", "종목코드", "KRX종가")
    _require_columns(panel, required, "panel")
    data = panel.copy()
    data["날짜"] = pd.to_datetime(data["날짜"], errors="raise").astype("datetime64[ns]")
    data["종목코드"] = data["종목코드"].astype("string")
    if "상장주식수" in data.columns:
        shares = pd.to_numeric(data["상장주식수"], errors="coerce")
        close = pd.to_numeric(data["KRX종가"], errors="coerce")
        data["market_cap"] = close * shares
    elif "시가총액" in data.columns:
        data["market_cap"] = pd.to_numeric(data["시가총액"], errors="coerce")
    elif "시가총액추정" in data.columns:
        data["market_cap"] = pd.to_numeric(data["시가총액추정"], errors="coerce")
    else:
        raise ValueError("panel requires 상장주식수 or a market-cap fallback column.")
    if data.duplicated(["날짜", "종목코드"]).any():
        raise ValueError("Panel contains duplicate rows for (날짜, 종목코드).")
    return data.loc[:, ["날짜", "종목코드", "market_cap"]]


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


def _cash_result(calendar: KRXTradingCalendar, period_start: object, period_end: object) -> BacktestResult:
    start = pd.Timestamp(period_start).normalize()
    end = pd.Timestamp(period_end).normalize()
    dates = [date for date in calendar.dates if start <= date <= end]
    equity = pd.DataFrame(
        {
            "date": dates,
            "cash": 1.0,
            "mtm_value": 0.0,
            "gross_value": 1.0,
            "net_value": 1.0,
            "n_positions": 0,
        }
    )
    trades = pd.DataFrame(
        columns=[
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
        ]
    )
    return BacktestResult(trades=trades, equity_curve=equity)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
