from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


PANEL_PATHS = [
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv"),
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"),
]
KOSPI_PROXY_PATH = Path("research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv")
OUTPUT_DIR = Path("reports/experiments/S000_korean_short_mean_reversion_feasibility")

COMMISSION_RATE = 0.0025
SLIPPAGE_RATE = 0.0005
CAPITAL_GAINS_TAX_RATE = 0.22
RANDOM_SEED = 20260520


SIGNALS = [
    {"name": "r1d_lt_m3_hold1", "return_col": "ret_1d", "threshold": -0.03, "hold_days": 1, "need_volume_z": False},
    {"name": "r1d_lt_m3_hold3", "return_col": "ret_1d", "threshold": -0.03, "hold_days": 3, "need_volume_z": False},
    {"name": "r1d_lt_m3_hold5", "return_col": "ret_1d", "threshold": -0.03, "hold_days": 5, "need_volume_z": False},
    {"name": "r3d_lt_m7_hold3", "return_col": "ret_3d", "threshold": -0.07, "hold_days": 3, "need_volume_z": False},
    {"name": "volume_z_gt2_crash_hold1", "return_col": "ret_1d", "threshold": -0.03, "hold_days": 1, "need_volume_z": True},
    {"name": "volume_z_gt2_crash_hold3", "return_col": "ret_1d", "threshold": -0.03, "hold_days": 3, "need_volume_z": True},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    enriched = add_features(panel)
    all_metrics = []
    all_events = []
    random_rows = []
    subperiod_rows = []
    for spec in SIGNALS:
        events = select_events(enriched, spec)
        trades = build_trades(enriched, events, spec)
        random_trades = build_random_control(enriched, trades, spec)
        metrics = {
            "signal": spec["name"],
            **calc_trade_metrics(trades),
            **prefixed("random_", calc_trade_metrics(random_trades)),
        }
        metrics["verdict"] = verdict_for(metrics, trades, random_trades)
        all_metrics.append(metrics)
        all_events.append(trades)
        random_rows.append(random_trades.assign(signal=spec["name"]))
        subperiod_rows.append(build_subperiod_breakdown(trades, spec["name"]))

    metrics_table = pd.DataFrame(all_metrics)
    trades_table = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    random_table = pd.concat(random_rows, ignore_index=True) if random_rows else pd.DataFrame()
    subperiod_table = pd.concat(subperiod_rows, ignore_index=True) if subperiod_rows else pd.DataFrame()
    daily_nav = build_daily_nav(trades_table)
    benchmark = load_kospi_proxy()

    metrics_table.to_csv(OUTPUT_DIR / "gross_net_metrics.csv", index=False)
    trades_table.to_csv(OUTPUT_DIR / "trades.csv", index=False)
    random_table.to_csv(OUTPUT_DIR / "random_control_distribution.csv", index=False)
    subperiod_table.to_csv(OUTPUT_DIR / "subperiod_breakdown.csv", index=False)
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav.csv", index=False)
    benchmark.to_csv(OUTPUT_DIR / "kospi_proxy_benchmark.csv", index=False)
    write_json_metrics(metrics_table)
    write_report(metrics_table, subperiod_table)


def load_panel() -> pd.DataFrame:
    frames = []
    for path in PANEL_PATHS:
        data = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["날짜"], dtype={"종목코드": str})
        required = {"날짜", "종목코드", "시가", "종가", "거래대금추정", "거래대금추정여부", "동적유니버스포함"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        if "KRX종가" not in data.columns:
            data["KRX종가"] = data["종가"]
            data["krx_close_source"] = "synthesized_from_pre_nxt_close"
        else:
            mismatch = data["KRX종가"].notna() & data["종가"].notna() & (data["KRX종가"] != data["종가"])
            if mismatch.any():
                raise ValueError(f"{path} has {int(mismatch.sum())} rows where 종가 != KRX종가")
            data["krx_close_source"] = "on_disk_krx_close"
        frames.append(data)
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.sort_values(["종목코드", "날짜"]).reset_index(drop=True)
    panel["시가"] = pd.to_numeric(panel["시가"], errors="coerce")
    panel["KRX종가"] = pd.to_numeric(panel["KRX종가"], errors="coerce")
    panel["거래대금추정"] = pd.to_numeric(panel["거래대금추정"], errors="coerce")
    panel = panel.loc[
        panel["동적유니버스포함"].eq(True)
        & panel["거래대금추정여부"].eq(False)
        & panel["시가"].gt(0)
        & panel["KRX종가"].gt(0)
        & panel["거래대금추정"].gt(0)
    ].copy()
    return panel


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    group = out.groupby("종목코드", sort=False)
    out["ret_1d"] = group["KRX종가"].pct_change(1)
    out["ret_3d"] = group["KRX종가"].pct_change(3)
    out["ret_5d"] = group["KRX종가"].pct_change(5)
    trade_value_mean = group["거래대금추정"].transform(lambda x: x.rolling(20, min_periods=10).mean())
    trade_value_std = group["거래대금추정"].transform(lambda x: x.rolling(20, min_periods=10).std())
    out["trade_value_z20"] = (out["거래대금추정"] - trade_value_mean) / trade_value_std
    out["quarter"] = out["날짜"].dt.to_period("Q")
    out["row_in_ticker"] = group.cumcount()
    return out


def select_events(data: pd.DataFrame, spec: dict) -> pd.DataFrame:
    candidates = data.loc[data[spec["return_col"]].lt(spec["threshold"])].copy()
    if spec["need_volume_z"]:
        candidates = candidates.loc[candidates["trade_value_z20"].gt(2.0)].copy()
    candidates["signal_value"] = -candidates[spec["return_col"]]
    candidates = candidates.sort_values(["quarter", "signal_value", "거래대금추정"], ascending=[True, False, False])
    return candidates.groupby("quarter", group_keys=False).head(20).reset_index(drop=True)


def build_trades(data: pd.DataFrame, events: pd.DataFrame, spec: dict) -> pd.DataFrame:
    by_ticker = {ticker: frame.reset_index(drop=True) for ticker, frame in data.groupby("종목코드", sort=False)}
    rows = []
    for event in events.itertuples(index=False):
        ticker_frame = by_ticker[event.종목코드]
        matches = ticker_frame.index[ticker_frame["날짜"].eq(event.날짜)].tolist()
        if not matches:
            continue
        signal_pos = matches[0]
        entry_pos = signal_pos + 1
        exit_pos = entry_pos + int(spec["hold_days"]) - 1
        if exit_pos >= len(ticker_frame):
            continue
        entry = ticker_frame.iloc[entry_pos]
        exit_row = ticker_frame.iloc[exit_pos]
        gross_return = float(exit_row["KRX종가"] / entry["시가"] - 1.0)
        net_return = apply_costs(gross_return)
        rows.append(
            {
                "signal": spec["name"],
                "ticker": event.종목코드,
                "signal_date": event.날짜,
                "execution_date": entry["날짜"],
                "exit_date": exit_row["날짜"],
                "holding_days": spec["hold_days"],
                "entry_price": entry["시가"],
                "exit_price": exit_row["KRX종가"],
                "signal_value": event.signal_value,
                "gross_return": gross_return,
                "net_return": net_return,
                "tax_paid_return": max(gross_return, 0.0) * CAPITAL_GAINS_TAX_RATE,
            }
        )
    return pd.DataFrame(rows)


def apply_costs(gross_return: float) -> float:
    trading_cost = 2.0 * (COMMISSION_RATE + SLIPPAGE_RATE)
    tax_cost = max(gross_return, 0.0) * CAPITAL_GAINS_TAX_RATE
    return gross_return - trading_cost - tax_cost


def build_random_control(data: pd.DataFrame, trades: pd.DataFrame, spec: dict) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    rng = pd.Series(range(len(data))).sample(n=len(trades), replace=False, random_state=RANDOM_SEED)
    events = data.iloc[rng.to_numpy()].copy()
    events["signal_value"] = 0.0
    events["quarter"] = events["날짜"].dt.to_period("Q")
    return build_trades(data, events, {**spec, "name": spec["name"] + "_random"})


def calc_trade_metrics(trades: pd.DataFrame) -> dict[str, float | int]:
    if trades.empty:
        return {"trade_count": 0, "gross_mean": 0.0, "net_mean": 0.0, "gross_hit_rate": 0.0, "net_hit_rate": 0.0, "sharpe": 0.0}
    net = trades["net_return"]
    return {
        "trade_count": int(len(trades)),
        "gross_mean": float(trades["gross_return"].mean()),
        "net_mean": float(net.mean()),
        "gross_hit_rate": float((trades["gross_return"] > 0).mean()),
        "net_hit_rate": float((net > 0).mean()),
        "sharpe": float(net.mean() / net.std() * math.sqrt(252.0 / trades["holding_days"].mean())) if net.std() else 0.0,
    }


def prefixed(prefix: str, values: dict) -> dict:
    return {prefix + key: value for key, value in values.items()}


def verdict_for(metrics: dict, trades: pd.DataFrame, random_trades: pd.DataFrame) -> str:
    if metrics["trade_count"] < 30:
        return "FAIL_insufficient_events"
    if metrics["gross_mean"] <= 0.0:
        return "FAIL_gross_edge_weak"
    if metrics["net_mean"] <= 0.0:
        return "FAIL_net_negative"
    if metrics["net_mean"] <= metrics["random_net_mean"]:
        return "FAIL_random_similar_or_better"
    subperiod = build_subperiod_breakdown(trades, str(metrics["signal"]))
    if (subperiod["net_mean"] > 0).sum() <= 1:
        return "FAIL_one_subperiod_only"
    return "PASS_diagnostic_only"


def build_subperiod_breakdown(trades: pd.DataFrame, signal: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["signal", "subperiod", "trade_count", "gross_mean", "net_mean"])
    out = trades.copy()
    out["year"] = pd.to_datetime(out["signal_date"]).dt.year
    out["subperiod"] = pd.cut(
        out["year"],
        bins=[2017, 2020, 2023, 2026],
        labels=["2018_2020", "2021_2023", "2024_2026"],
        include_lowest=True,
    )
    return (
        out.groupby("subperiod", observed=False)
        .agg(trade_count=("net_return", "size"), gross_mean=("gross_return", "mean"), net_mean=("net_return", "mean"))
        .reset_index()
        .assign(signal=signal)
        .loc[:, ["signal", "subperiod", "trade_count", "gross_mean", "net_mean"]]
    )


def load_kospi_proxy() -> pd.DataFrame:
    data = pd.read_csv(KOSPI_PROXY_PATH, encoding="utf-8-sig", parse_dates=["date"])
    columns = ["date", "cap_weighted_return", "equal_weight_return", "top_equal_weight_return"]
    missing = set(columns).difference(data.columns)
    if missing:
        raise ValueError(f"{KOSPI_PROXY_PATH} missing columns: {sorted(missing)}")
    out = data[columns].copy()
    for column in columns[1:]:
        out[column + "_nav"] = (1.0 + out[column].fillna(0.0)).cumprod()
    return out


def build_daily_nav(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["date", "signal", "daily_return", "nav"])
    rows = []
    for signal, group in trades.groupby("signal", sort=False):
        dates = pd.date_range(group["execution_date"].min(), group["exit_date"].max(), freq="D")
        daily = pd.Series(0.0, index=dates)
        exit_returns = group.groupby("exit_date")["net_return"].mean()
        for date, value in exit_returns.items():
            daily.loc[pd.Timestamp(date)] = float(value)
        nav = (1.0 + daily).cumprod()
        rows.append(pd.DataFrame({"date": daily.index, "signal": signal, "daily_return": daily.values, "nav": nav.values}))
    return pd.concat(rows, ignore_index=True)


def write_json_metrics(metrics_table: pd.DataFrame) -> None:
    payload = {
        "experiment": "S000_korean_short_mean_reversion_feasibility",
        "verdict": "PASS" if metrics_table["verdict"].astype(str).str.startswith("PASS").any() else "FAIL",
        "signals": metrics_table.to_dict(orient="records"),
        "costs": {
            "commission_rate_per_leg": COMMISSION_RATE,
            "slippage_rate_per_leg": SLIPPAGE_RATE,
            "capital_gains_tax_rate_on_positive_gains": CAPITAL_GAINS_TAX_RATE,
        },
    }
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_report(metrics: pd.DataFrame, subperiod: pd.DataFrame) -> None:
    overall = "PASS" if metrics["verdict"].astype(str).str.startswith("PASS").any() else "FAIL"
    lines = [
        "# S000 Korean Short-Horizon Mean Reversion Feasibility",
        "",
        f"Verdict: {overall}",
        "",
        "## Gate Results",
        "",
        markdown_table(metrics),
        "",
        "## Subperiod Breakdown",
        "",
        markdown_table(subperiod),
        "",
        "## Timing Policy",
        "",
        "- Signal date T uses KRX close data available after close.",
        "- Execution date is T+1 open or later.",
        "- Rows with `거래대금추정여부 == True` are excluded.",
        "- Pre-NXT panels synthesize `KRX종가` from `종가`; NXT panel rows assert equality.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
