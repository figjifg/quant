from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SanityCheckConfig:
    max_abs_single_period_return: float = 0.50
    max_gross_exposure: float = 1.0
    require_signal_execution_separation: bool = True


def check_impossible_returns(trades: pd.DataFrame) -> int:
    columns = [column for column in ("gross_return", "net_return", "return") if column in trades.columns]
    if not columns:
        return 0
    mask = pd.Series(False, index=trades.index)
    for column in columns:
        threshold = 1.0 if column != "return" else 0.50
        mask |= pd.to_numeric(trades[column], errors="coerce").abs().gt(threshold).fillna(False)
    return int(mask.sum())


def check_active_exposure(simulator) -> float:
    if hasattr(simulator, "nav_frame"):
        nav = simulator.nav_frame()
    else:
        nav = simulator
    if nav is None or len(nav) == 0 or "exposure" not in nav:
        return 0.0
    base = float(getattr(simulator, "initial_capital", nav["net_value"].iloc[0] if "net_value" in nav else 1.0))
    return float(pd.to_numeric(nav["exposure"], errors="coerce").max() / base)


def check_duplicate_signals(events: pd.DataFrame) -> int:
    columns = [column for column in ("signal_date", "date", "날짜") if column in events.columns]
    tickers = [column for column in ("ticker", "종목코드") if column in events.columns]
    if not columns or not tickers:
        return 0
    subset = [columns[0], tickers[0]]
    if "signal" in events.columns:
        subset.append("signal")
    return int(events.duplicated(subset=subset).sum())


def check_entry_exit_lineage(trades: pd.DataFrame, calendar) -> int:
    required = {"signal_date", "entry_date", "exit_date"}
    if "execution_date" in trades.columns and "entry_date" not in trades.columns:
        trades = trades.rename(columns={"execution_date": "entry_date"})
    if not required.issubset(trades.columns):
        return 0
    signal = pd.to_datetime(trades["signal_date"]).dt.normalize()
    entry = pd.to_datetime(trades["entry_date"]).dt.normalize()
    exit_ = pd.to_datetime(trades["exit_date"]).dt.normalize()
    bad = entry.le(signal) | exit_.lt(entry)
    calendar_dates = set(calendar.dates)
    bad |= ~entry.isin(calendar_dates) | ~exit_.isin(calendar_dates)
    return int(bad.sum())


def check_benchmark_alignment(strategy_returns: pd.Series | pd.DataFrame, benchmark: pd.Series | pd.DataFrame) -> int:
    left = strategy_returns.index if isinstance(strategy_returns, pd.Series) else pd.to_datetime(strategy_returns.iloc[:, 0])
    right = benchmark.index if isinstance(benchmark, pd.Series) else pd.to_datetime(benchmark.iloc[:, 0])
    return int(len(set(pd.to_datetime(left).normalize()).symmetric_difference(set(pd.to_datetime(right).normalize()))))


def check_no_same_day_execution(signals: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    if "execution_date" in trades.columns and "entry_date" not in trades.columns:
        trades = trades.rename(columns={"execution_date": "entry_date"})
    if not {"signal_date", "entry_date"}.issubset(trades.columns):
        return pd.DataFrame([{"check": "no_same_day_execution", "fail_count": 0}])
    fail = pd.to_datetime(trades["entry_date"]).dt.normalize().le(pd.to_datetime(trades["signal_date"]).dt.normalize())
    return pd.DataFrame([{"check": "no_same_day_execution", "fail_count": int(fail.sum())}])


def check_no_filtered_row_execution(trades: pd.DataFrame, tradability: pd.DataFrame) -> pd.DataFrame:
    if "execution_date" in trades.columns and "entry_date" not in trades.columns:
        trades = trades.rename(columns={"execution_date": "entry_date"})
    if trades.empty or tradability.empty or "tradable" not in tradability.columns:
        return pd.DataFrame([{"check": "no_filtered_row_execution", "fail_count": 0}])
    date_col = "date" if "date" in tradability.columns else "날짜"
    ticker_col = "ticker" if "ticker" in tradability.columns else "종목코드"
    allowed = set(
        zip(
            tradability.loc[tradability["tradable"].astype(bool), ticker_col].astype(str),
            pd.to_datetime(tradability.loc[tradability["tradable"].astype(bool), date_col]).dt.normalize(),
        )
    )
    fail = [
        (str(row.ticker), pd.Timestamp(row.entry_date).normalize()) not in allowed
        for row in trades.itertuples(index=False)
        if hasattr(row, "ticker") and hasattr(row, "entry_date")
    ]
    return pd.DataFrame([{"check": "no_filtered_row_execution", "fail_count": int(sum(fail))}])


def check_no_impossible_returns(returns: pd.DataFrame, config: SanityCheckConfig) -> pd.DataFrame:
    col = "return" if "return" in returns.columns else ("gross_return" if "gross_return" in returns.columns else None)
    fail = 0 if col is None else int(pd.to_numeric(returns[col], errors="coerce").abs().gt(config.max_abs_single_period_return).fillna(False).sum())
    return pd.DataFrame([{"check": "no_impossible_returns", "fail_count": fail}])


def check_no_implicit_leverage(nav: pd.DataFrame, config: SanityCheckConfig) -> pd.DataFrame:
    if nav.empty or "exposure" not in nav.columns:
        fail = 0
        max_exposure = 0.0
    else:
        denominator = pd.to_numeric(nav["net_value"], errors="coerce").replace(0, pd.NA) if "net_value" in nav.columns else 1.0
        exposure = pd.to_numeric(nav["exposure"], errors="coerce") / denominator
        max_exposure = float(exposure.max())
        fail = int(exposure.gt(config.max_gross_exposure + 1e-9).sum())
    return pd.DataFrame([{"check": "no_implicit_leverage", "fail_count": fail, "max_exposure": max_exposure}])


def run_all_checks(
    trades: pd.DataFrame,
    events: pd.DataFrame | None = None,
    simulator_or_nav=None,
    calendar=None,
    strategy_returns=None,
    benchmark=None,
) -> dict[str, float | int]:
    report: dict[str, float | int] = {
        "impossible_return_fail_count": check_impossible_returns(trades),
        "duplicate_signal_fail_count": check_duplicate_signals(events if events is not None else trades),
    }
    if simulator_or_nav is not None:
        report["max_exposure_ratio"] = check_active_exposure(simulator_or_nav)
        report["exposure_fail_count"] = int(report["max_exposure_ratio"] > 1.0 + 1e-9)
    if calendar is not None:
        report["entry_exit_lineage_bad_count"] = check_entry_exit_lineage(trades, calendar)
    if strategy_returns is not None and benchmark is not None:
        report["benchmark_alignment_mismatch_count"] = check_benchmark_alignment(strategy_returns, benchmark)
    return report
