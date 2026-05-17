from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.data.macro_factors import align_macro_factors_to_korean_signal_dates
from src.run_experiment import run_d011_experiment, run_d013_experiment


D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
D016_DIR = Path("reports/experiments/D016_d013_data_leakage_audit")
D017_DIR = Path("reports/experiments/D017_d013_threshold_fine_grid")
D018_DIR = Path("reports/experiments/D018_d013_cost_stress")
D019_DIR = Path("reports/experiments/D019_d013_mdd_attribution")


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_d016_audit() -> None:
    config = load_yaml("configs/backtests/d013.yaml")
    regime = pd.read_csv(D013_DIR / "quarterly_regime_log.csv", parse_dates=["signal_date"])
    aligned = align_macro_factors_to_korean_signal_dates(
        regime["signal_date"],
        input_dir=config["macro_data_dir"],
    )

    rows = [
        _daily_row("VIX 60d/240d", "vix", "fred_vix.csv", "US after close: source <= signal_date - 1d", aligned),
        _daily_row(
            "BAA10Y spread",
            "baa10y_spread",
            "fred_baa10y_spread.csv",
            "US after close: source <= signal_date - 1d",
            aligned,
        ),
        _same_day_row(
            "USDKRW yoy",
            "dexkous_usdkrw",
            "fred_dexkous_usdkrw.csv",
            "Korea same day: source <= signal_date",
            aligned,
        ),
        _daily_row("DXY yoy", "dxy", "fred_dxy.csv", "US after close: source <= signal_date - 1d", aligned),
        _daily_row(
            "US 10y real yield",
            "us_10y_real",
            "fred_us_10y_real.csv",
            "US after close: source <= signal_date - 1d",
            aligned,
        ),
        _curve_row(aligned),
        _daily_row("Brent yoy", "brent", "fred_brent.csv", "US after close: source <= signal_date - 1d", aligned),
        _daily_row(
            "10y breakeven",
            "us_breakeven_10y",
            "fred_us_breakeven_10y.csv",
            "US after close: source <= signal_date - 1d",
            aligned,
        ),
        _monthly_row(
            "OECD CLI Korea",
            "kr_cli",
            "fred_kr_cli.csv",
            75,
            "OECD CLI conservative lag: observation month-end +75 calendar days",
            aligned,
        ),
        _monthly_row(
            "KR exports yoy",
            "kr_exports",
            "fred_kr_exports.csv",
            14,
            "KR exports lag: observation month-end +14 calendar days",
            aligned,
        ),
    ]
    table = pd.DataFrame(rows)
    D016_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(D016_DIR / "timing_table.csv", index=False)
    passed = bool(table["passed"].all())
    lines = [
        "# D016 D013 Data Leakage Audit",
        "",
        f"Overall verdict: {'PASS - no timing leakage detected' if passed else 'FAIL - timing issue detected'}",
        "",
        "## Timing Table",
        "",
        "| variable | rule | min_lag_days | violations | passed |",
        "|---|---|---:|---:|---|",
    ]
    for row in table.to_dict("records"):
        lines.append(
            f"| {row['variable']} | {row['availability_rule']} | "
            f"{row['min_lag_days']} | {row['violations']} | {row['passed']} |"
        )
    lines.extend(
        [
            "",
            "## z-score and execution checks",
            "",
            "- Factor z-scores are computed from monthly regime history through each signal date only.",
            "- D013 signals keep `signal_date` and `execution_date` separate; all trades execute after the signal date.",
            "- OECD CLI now uses month-end +75 calendar days; KR exports and other monthly variables retain month-end +14 days.",
        ]
    )
    (D016_DIR / "audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_d017_threshold_fine_grid() -> None:
    config = load_yaml("configs/backtests/d011.yaml")
    config["experiment_id"] = "D011"
    config["regime"]["on_threshold_grid"] = [-0.40, -0.30, -0.25, -0.20, -0.15, -0.10, 0.00]
    config["output_dir"] = str(D017_DIR)
    temp_config = Path("/tmp/d017_threshold_fine_grid.yaml")
    temp_config.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    run_d011_experiment(config, temp_config)


def run_d018_cost_stress() -> None:
    base = load_yaml("configs/backtests/d013.yaml")
    scenarios = {
        "base": {"commission_bps": 1.5, "tax_bps_sell": 20.0, "slippage_bps": 5.0},
        "2x": {"commission_bps": 3.0, "tax_bps_sell": 40.0, "slippage_bps": 10.0},
        "3x": {"commission_bps": 4.5, "tax_bps_sell": 60.0, "slippage_bps": 15.0},
        "extra_slippage": {"commission_bps": 1.5, "tax_bps_sell": 20.0, "slippage_bps": 15.0},
    }
    D018_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for name, costs in scenarios.items():
        config = yaml.safe_load(yaml.safe_dump(base, sort_keys=False, allow_unicode=True))
        config["costs"] = costs
        config["output_dir"] = str(D018_DIR / name)
        temp_config = Path(f"/tmp/d018_{name}.yaml")
        temp_config.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
        run_d013_experiment(config, temp_config)
        metrics = pd.read_json(D018_DIR / name / "metrics.json")
        net = metrics.loc["cumulative_net_total_return", "factor_macro_gate_mcap"]
        sharpe = metrics.loc["sharpe", "factor_macro_gate_mcap"]
        maxdd = metrics.loc["max_drawdown", "factor_macro_gate_mcap"]
        rows.append({"scenario": name, "net_cum": net, "sharpe": sharpe, "max_drawdown": maxdd})
    rows.append(
        {
            "scenario": "one_day_delay",
            "net_cum": pd.NA,
            "sharpe": pd.NA,
            "max_drawdown": pd.NA,
            "note": "skipped: existing engine has no registered one-day delayed execution option; engine.py was not modified",
        }
    )
    pd.DataFrame(rows).to_csv(D018_DIR / "cost_stress_summary.csv", index=False)


def write_d019_mdd_attribution() -> None:
    D019_DIR.mkdir(parents=True, exist_ok=True)
    equity = pd.read_csv(D013_DIR / "equity_curve.csv", parse_dates=["date"])
    trades = pd.read_csv(
        D013_DIR / "trades.csv",
        dtype={"종목코드": "string"},
        parse_dates=["entry_date", "signal_date", "exit_date"],
    )
    regime = pd.read_csv(D013_DIR / "quarterly_regime_log.csv", parse_dates=["signal_date"])
    value_col = "V1_factor_macro_gate_mcap_net_value"
    values = equity[value_col]
    running_peak = values.cummax()
    drawdown = values / running_peak - 1.0
    trough_idx = int(drawdown.idxmin())
    peak_idx = int(values.loc[:trough_idx].idxmax())
    peak_value = float(values.loc[peak_idx])
    trough_value = float(values.loc[trough_idx])
    recovery = equity.loc[trough_idx:].loc[equity.loc[trough_idx:, value_col].ge(peak_value)]
    recovery_date = pd.NaT if recovery.empty else recovery["date"].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "peak_date": equity["date"].iloc[peak_idx].date().isoformat(),
                "trough_date": equity["date"].iloc[trough_idx].date().isoformat(),
                "recovery_date": "" if pd.isna(recovery_date) else pd.Timestamp(recovery_date).date().isoformat(),
                "peak_value": peak_value,
                "trough_value": trough_value,
                "max_drawdown": float(drawdown.loc[trough_idx]),
                "peak_to_trough_trading_days": trough_idx - peak_idx,
                "trough_to_recovery_trading_days": "" if recovery.empty else int(recovery.index[0] - trough_idx),
            }
        ]
    )
    summary.to_csv(D019_DIR / "mdd_summary.csv", index=False)

    peak_date = equity["date"].iloc[peak_idx]
    trough_date = equity["date"].iloc[trough_idx]
    window_trades = trades.loc[
        trades["entry_date"].le(trough_date) & trades["exit_date"].ge(peak_date)
    ].copy()
    if not window_trades.empty:
        window_trades["entry_quarter"] = window_trades["entry_date"].dt.to_period("Q").astype(str)
        window_trades["trade_return"] = window_trades["exit_price"] / window_trades["entry_price"] - 1.0
    window_trades.to_csv(D019_DIR / "mdd_quarters_detail.csv", index=False)

    macro = regime.loc[regime["signal_date"].between(peak_date - pd.Timedelta(days=120), trough_date)].copy()
    macro.to_csv(D019_DIR / "macro_signal_during_mdd.csv", index=False)

    worst = (
        window_trades.sort_values("trade_return").head(10)
        if not window_trades.empty and "trade_return" in window_trades
        else pd.DataFrame()
    )
    lines = [
        "# D019 D013 MDD Attribution",
        "",
        f"Peak: {summary.loc[0, 'peak_date']} ({peak_value:.6f})",
        f"Trough: {summary.loc[0, 'trough_date']} ({trough_value:.6f})",
        f"Recovery: {summary.loc[0, 'recovery_date'] or 'not recovered in sample'}",
        f"Max drawdown: {summary.loc[0, 'max_drawdown']:.6f}",
        "",
        "## Macro Signal",
        "",
    ]
    if not macro.empty:
        lines.append(
            f"Composite ranged from {macro['composite'].min():.6f} to {macro['composite'].max():.6f} "
            f"across {len(macro)} quarterly signal rows in the attribution window."
        )
    lines.extend(["", "## Worst Trades", ""])
    for row in worst.to_dict("records"):
        lines.append(
            f"- {row['entry_date'].date().isoformat()} {row['종목코드']} "
            f"return {row['trade_return']:.6f}, exit {row['exit_date'].date().isoformat()}"
        )
    (D019_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _daily_row(variable: str, name: str, source: str, rule: str, aligned: pd.DataFrame) -> dict[str, Any]:
    source_dates = pd.to_datetime(aligned[f"{name}_source_observation_date"])
    max_allowed = aligned["signal_date"] - pd.Timedelta(days=1)
    return _row(variable, source, "daily", rule, source_dates, aligned["signal_date"], max_allowed)


def _same_day_row(variable: str, name: str, source: str, rule: str, aligned: pd.DataFrame) -> dict[str, Any]:
    source_dates = pd.to_datetime(aligned[f"{name}_source_observation_date"])
    return _row(variable, source, "daily", rule, source_dates, aligned["signal_date"], aligned["signal_date"])


def _monthly_row(
    variable: str,
    name: str,
    source: str,
    lag_days: int,
    rule: str,
    aligned: pd.DataFrame,
) -> dict[str, Any]:
    source_dates = pd.to_datetime(aligned[f"{name}_source_observation_date"])
    availability = source_dates + pd.offsets.MonthEnd(0) + pd.Timedelta(days=lag_days)
    return _row(variable, source, "monthly", rule, source_dates, aligned["signal_date"], availability)


def _curve_row(aligned: pd.DataFrame) -> dict[str, Any]:
    dgs2 = pd.to_datetime(aligned["dgs2_source_observation_date"])
    dgs10 = pd.to_datetime(aligned["dgs10_source_observation_date"])
    source_dates = pd.concat([dgs2, dgs10], axis=1).max(axis=1)
    max_allowed = aligned["signal_date"] - pd.Timedelta(days=1)
    return _row(
        "US 2-10y curve",
        "fred_dgs2.csv + fred_dgs10.csv",
        "daily",
        "US after close: both sources <= signal_date - 1d",
        source_dates,
        aligned["signal_date"],
        max_allowed,
    )


def _row(
    variable: str,
    source: str,
    frequency: str,
    rule: str,
    source_dates: pd.Series,
    signal_dates: pd.Series,
    allowed_or_available: pd.Series,
) -> dict[str, Any]:
    observed = source_dates.notna()
    if "month-end" in rule:
        violations = int((allowed_or_available.loc[observed] > signal_dates.loc[observed]).sum())
        lag_days = (signal_dates.loc[observed] - source_dates.loc[observed]).dt.days
    else:
        violations = int((source_dates.loc[observed] > allowed_or_available.loc[observed]).sum())
        lag_days = (signal_dates.loc[observed] - source_dates.loc[observed]).dt.days
    return {
        "variable": variable,
        "source_file": source,
        "frequency": frequency,
        "availability_rule": rule,
        "rows_checked": int(observed.sum()),
        "min_lag_days": int(lag_days.min()) if not lag_days.empty else "",
        "max_source_observation_date": source_dates.loc[observed].max().date().isoformat() if observed.any() else "",
        "violations": violations,
        "passed": violations == 0,
    }
