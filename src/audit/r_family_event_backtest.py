from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.equity_panel import load_equity_panel


ROOT = Path(__file__).resolve().parents[2]
EVENT_PATH = ROOT / "research_input_data" / "inputs" / "events" / "opendart_kospi_disclosures_20180101_20260505.parquet"
PANEL_PATHS = (
    ROOT / "research_input_data" / "inputs" / "equity_panels" / "dynamic_top100_2018_2024_panel.csv",
    ROOT / "research_input_data" / "inputs" / "equity_panels" / "dynamic_top100_2025_2026_krx_panel.csv",
)
KOSPI_PATH = ROOT / "research_input_data" / "inputs" / "macro_features" / "krx_market_breadth_kospi_2010_2026.csv"
HOLDING_DAYS = (21, 63, 126)
SUBPERIODS = {
    "2018_2021": (pd.Timestamp("2018-01-01"), pd.Timestamp("2021-12-31")),
    "2022_2026": (pd.Timestamp("2022-01-01"), pd.Timestamp("2026-12-31")),
}

CORRECTION_KEYWORDS = ("정정", "첨부정정", "기재정정")
CANCEL_KEYWORDS = ("취소", "철회")


@dataclass(frozen=True)
class EventSpec:
    experiment: str
    slug: str
    event_types: tuple[str, ...]
    include_corrections: bool = False
    collapse_nearby: bool = False


EVENT_TYPE_KEYWORDS = {
    "buyback_announcement": ("자기주식취득", "자사주취득", "자사주 취득", "자기주식취득신탁계약"),
    "buyback_retirement": ("자기주식소각", "자사주소각", "자사주 소각", "소각결정"),
    "dividend": ("현금ㆍ현물배당", "현금/현물배당", "현금배당", "중간배당", "분기배당"),
}


SPECS = {
    "R001": EventSpec("R001", "buyback_announcement", ("buyback_announcement",)),
    "R002": EventSpec("R002", "buyback_cancellation_retirement", ("buyback_retirement",)),
    "R003": EventSpec("R003", "dividend_increase", ("dividend",)),
    "R004": EventSpec(
        "R004",
        "shareholder_return_composite",
        ("buyback_announcement", "buyback_retirement", "dividend"),
        collapse_nearby=True,
    ),
}


def main(default_experiment: str | None = None) -> int:
    parser = argparse.ArgumentParser(description="R-family Korean shareholder-return event study.")
    parser.add_argument("--experiment", choices=sorted(SPECS), default=default_experiment)
    parser.add_argument("--event-path", type=Path, default=EVENT_PATH)
    parser.add_argument("--kospi-path", type=Path, default=KOSPI_PATH)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.experiment is None:
        parser.error("--experiment is required")
    spec = SPECS[args.experiment]
    output_dir = args.output_dir or ROOT / "reports" / "experiments" / f"{spec.experiment}_{spec.slug}"
    run(spec, args.event_path, PANEL_PATHS, args.kospi_path, output_dir)
    return 0


def run(
    spec: EventSpec,
    event_path: Path = EVENT_PATH,
    panel_paths: tuple[Path, ...] = PANEL_PATHS,
    kospi_path: Path = KOSPI_PATH,
    output_dir: Path | None = None,
) -> None:
    output_dir = output_dir or ROOT / "reports" / "experiments" / f"{spec.experiment}_{spec.slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_price_panel(panel_paths)
    calendar = pd.DatetimeIndex(sorted(panel["date"].dropna().unique()))
    kospi = load_kospi(kospi_path, calendar)
    events = load_events(event_path, spec, calendar)
    signals = build_signals(events, panel, calendar, spec)
    trades = build_trades(signals, panel, kospi, calendar)

    metrics = build_metrics(trades, signals, spec)
    distributions = build_distributions(signals)
    equity_curve = build_equity_curve(trades)
    comparison = build_r_family_comparison(output_dir.parent, spec.experiment, metrics)

    write_config(output_dir / "config.yaml", spec, event_path, panel_paths, kospi_path)
    signals.to_csv(output_dir / "signals.csv", index=False)
    trades.to_csv(output_dir / "trades.csv", index=False)
    equity_curve.to_csv(output_dir / "equity_curve.csv", index=False)
    distributions.to_csv(output_dir / "sector_size_distribution.csv", index=False)
    comparison.to_csv(output_dir / "r_family_standalone_comparison.csv", index=False)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(output_dir / "report.md", spec, metrics, distributions)


def load_price_panel(panel_paths: tuple[Path, ...]) -> pd.DataFrame:
    panel = load_equity_panel(panel_paths)
    panel = panel.loc[~panel["거래대금추정여부"]].copy()
    panel["date"] = pd.to_datetime(panel["날짜"])
    panel["ticker"] = panel["종목코드"].astype(str).str.extract(r"(\d+)", expand=False).str.zfill(6)
    panel["open"] = pd.to_numeric(panel["시가"], errors="coerce")
    panel["close"] = pd.to_numeric(panel["KRX종가"], errors="coerce")
    panel["mcap"] = pd.to_numeric(panel["시가총액추정"], errors="coerce")
    panel["name"] = panel["종목명"].astype(str)
    panel = panel.dropna(subset=["date", "ticker", "open", "close"])
    panel = panel.loc[(panel["open"] > 0) & (panel["close"] > 0)].copy()
    panel = panel.sort_values(["ticker", "date"]).reset_index(drop=True)
    return panel[["date", "ticker", "name", "open", "close", "mcap", "동적유니버스포함", "krx_close_source"]]


def load_kospi(path: Path, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    kospi = pd.read_csv(path, parse_dates=["date"])
    kospi = kospi.loc[kospi["date"].isin(calendar), ["date", "cap_weighted_return"]].copy()
    kospi["cap_weighted_return"] = pd.to_numeric(kospi["cap_weighted_return"], errors="coerce").fillna(0.0)
    kospi = kospi.sort_values("date").reset_index(drop=True)
    kospi["kospi_nav"] = (1.0 + kospi["cap_weighted_return"]).cumprod()
    return kospi


def load_events(path: Path, spec: EventSpec, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    raw = pd.read_parquet(path)
    out = raw[["rcept_no", "rcept_dt", "stock_code", "corp_name", "report_nm", "dart_url"]].copy()
    out["title"] = out["report_nm"].fillna("").astype(str)
    out["title_normalized"] = out["title"].str.lower().str.replace(" ", "", regex=False)
    out["event_type"] = out["title_normalized"].map(classify_event_type)
    out = out.loc[out["event_type"].isin(spec.event_types)].copy()
    out["is_correction"] = out["title"].map(lambda value: contains_any(value, CORRECTION_KEYWORDS))
    out["is_cancellation_title"] = out["title"].map(lambda value: contains_any(value, CANCEL_KEYWORDS))
    if not spec.include_corrections:
        out = out.loc[~out["is_correction"] & ~out["is_cancellation_title"]].copy()
    out["signal_date"] = pd.to_datetime(out["rcept_dt"].astype(str).str.extract(r"(\d{8})", expand=False), errors="coerce")
    out["ticker"] = out["stock_code"].astype(str).str.extract(r"(\d+)", expand=False).str.zfill(6)
    out["event_time"] = ""
    out["session"] = "date_only_next_open"
    out = out.dropna(subset=["signal_date", "ticker"]).sort_values(["ticker", "signal_date", "rcept_no"])
    out["execution_date"] = out["signal_date"].map(lambda date: next_trading_day(date, calendar))
    out = out.dropna(subset=["execution_date"]).copy()
    out["execution_date"] = pd.to_datetime(out["execution_date"])
    if spec.collapse_nearby:
        out = collapse_nearby_events(out, calendar, min_gap=21)
    return out.reset_index(drop=True)


def classify_event_type(text: str) -> str:
    for event_type, keywords in EVENT_TYPE_KEYWORDS.items():
        if any(keyword.lower().replace(" ", "") in text for keyword in keywords):
            return event_type
    return "other"


def contains_any(text: object, keywords: tuple[str, ...]) -> bool:
    value = str(text).lower()
    return any(keyword.lower() in value for keyword in keywords)


def next_trading_day(date: pd.Timestamp, calendar: pd.DatetimeIndex) -> pd.Timestamp | pd.NaT:
    idx = calendar.searchsorted(pd.Timestamp(date), side="right")
    if idx >= len(calendar):
        return pd.NaT
    return calendar[idx]


def collapse_nearby_events(events: pd.DataFrame, calendar: pd.DatetimeIndex, min_gap: int) -> pd.DataFrame:
    day_number = pd.Series(range(len(calendar)), index=calendar)
    keep = []
    last_kept: dict[str, int] = {}
    for row in events.sort_values(["ticker", "execution_date", "event_type", "rcept_no"]).itertuples(index=False):
        current = int(day_number.loc[row.execution_date])
        previous = last_kept.get(row.ticker)
        should_keep = previous is None or current - previous > min_gap
        keep.append(should_keep)
        if should_keep:
            last_kept[row.ticker] = current
    return events.loc[keep].copy()


def build_signals(events: pd.DataFrame, panel: pd.DataFrame, calendar: pd.DatetimeIndex, spec: EventSpec) -> pd.DataFrame:
    entry = panel.rename(columns={"date": "execution_date", "open": "entry_price", "name": "panel_name"})
    signals = events.merge(
        entry[["execution_date", "ticker", "panel_name", "entry_price", "mcap", "동적유니버스포함", "krx_close_source"]],
        on=["execution_date", "ticker"],
        how="left",
    )
    signals["included_in_trade"] = signals["entry_price"].notna()
    signals["signal_value"] = 1.0
    signals["sector"] = "unknown"
    signals["size_bucket"] = assign_size_buckets(signals)
    signals["date"] = signals["signal_date"]
    signals["experiment"] = spec.experiment
    signals["universe"] = "dynamic_top100_price_matched"
    columns = [
        "experiment",
        "date",
        "ticker",
        "corp_name",
        "panel_name",
        "event_type",
        "title",
        "signal_value",
        "signal_date",
        "execution_date",
        "event_time",
        "session",
        "included_in_trade",
        "entry_price",
        "mcap",
        "size_bucket",
        "sector",
        "is_correction",
        "is_cancellation_title",
        "rcept_no",
        "dart_url",
        "krx_close_source",
    ]
    return signals[columns].sort_values(["signal_date", "ticker", "event_type"]).reset_index(drop=True)


def assign_size_buckets(signals: pd.DataFrame) -> pd.Series:
    buckets = pd.Series("unknown", index=signals.index, dtype=object)
    valid = signals["mcap"].notna()
    if valid.sum() < 3:
        return buckets
    ranks = signals.loc[valid, "mcap"].rank(method="first", pct=True)
    buckets.loc[valid & (ranks <= 1 / 3)] = "small"
    buckets.loc[valid & (ranks > 1 / 3) & (ranks <= 2 / 3)] = "mid"
    buckets.loc[valid & (ranks > 2 / 3)] = "large"
    return buckets


def build_trades(signals: pd.DataFrame, panel: pd.DataFrame, kospi: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    tradable = signals.loc[signals["included_in_trade"]].copy()
    close_panel = panel.rename(columns={"date": "exit_date", "close": "exit_price"})
    day_number = pd.Series(range(len(calendar)), index=calendar)
    kospi_nav = kospi.set_index("date")["kospi_nav"]
    rows = []
    for holding_days in HOLDING_DAYS:
        tmp = tradable.copy()
        tmp["holding_days"] = holding_days
        tmp["_entry_i"] = tmp["execution_date"].map(day_number)
        tmp["_exit_i"] = tmp["_entry_i"] + holding_days
        tmp = tmp.loc[tmp["_exit_i"] < len(calendar)].copy()
        if tmp.empty:
            continue
        tmp["exit_date"] = tmp["_exit_i"].map(lambda idx: calendar[int(idx)])
        tmp = tmp.merge(close_panel[["exit_date", "ticker", "exit_price"]], on=["exit_date", "ticker"], how="left")
        tmp = tmp.dropna(subset=["exit_price"]).copy()
        tmp["gross_return"] = tmp["exit_price"] / tmp["entry_price"] - 1.0
        tmp["kospi_return"] = tmp.apply(lambda row: benchmark_return(row.execution_date, row.exit_date, kospi_nav), axis=1)
        tmp["excess_return"] = tmp["gross_return"] - tmp["kospi_return"]
        tmp["cost_paid"] = 0.0
        tmp["exit_reason"] = f"{holding_days}d_horizon"
        rows.append(tmp)
    if not rows:
        return empty_trades()
    trades = pd.concat(rows, ignore_index=True)
    columns = [
        "experiment",
        "ticker",
        "corp_name",
        "event_type",
        "title",
        "signal_date",
        "execution_date",
        "entry_price",
        "exit_date",
        "exit_price",
        "holding_days",
        "gross_return",
        "kospi_return",
        "excess_return",
        "cost_paid",
        "exit_reason",
        "size_bucket",
        "sector",
        "rcept_no",
    ]
    return trades[columns].sort_values(["holding_days", "signal_date", "ticker"]).reset_index(drop=True)


def benchmark_return(start: pd.Timestamp, end: pd.Timestamp, kospi_nav: pd.Series) -> float:
    if start not in kospi_nav.index or end not in kospi_nav.index:
        return math.nan
    return float(kospi_nav.loc[end] / kospi_nav.loc[start] - 1.0)


def empty_trades() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "experiment",
            "ticker",
            "corp_name",
            "event_type",
            "title",
            "signal_date",
            "execution_date",
            "entry_price",
            "exit_date",
            "exit_price",
            "holding_days",
            "gross_return",
            "kospi_return",
            "excess_return",
            "cost_paid",
            "exit_reason",
            "size_bucket",
            "sector",
            "rcept_no",
        ]
    )


def build_metrics(trades: pd.DataFrame, signals: pd.DataFrame, spec: EventSpec) -> dict[str, object]:
    metrics: dict[str, object] = {
        "experiment": spec.experiment,
        "status": "GENERATED",
        "cost_model": "gross_only_R005_pending",
        "event_rows": int(len(signals)),
        "tradable_event_rows": int(signals["included_in_trade"].sum()) if not signals.empty else 0,
        "excluded_unmatched_price_rows": int((~signals["included_in_trade"]).sum()) if not signals.empty else 0,
        "timing_policy": "date-only OPENDART rows execute next KRX trading day open",
        "overall": {},
        "subperiod": {},
        "by_event_type": {},
        "verdict": {},
    }
    for holding_days in HOLDING_DAYS:
        horizon = trades.loc[trades["holding_days"] == holding_days].copy()
        key = f"{holding_days}d"
        metrics["overall"][key] = summarize_returns(horizon)
        metrics["subperiod"][key] = {
            name: summarize_returns(
                horizon.loc[horizon["signal_date"].between(start, end)]
            )
            for name, (start, end) in SUBPERIODS.items()
        }
        metrics["by_event_type"][key] = {
            event_type: summarize_returns(group)
            for event_type, group in horizon.groupby("event_type", dropna=False)
        }
        metrics["verdict"][key] = verdict(metrics["overall"][key], metrics["subperiod"][key])
    return metrics


def summarize_returns(frame: pd.DataFrame) -> dict[str, float | int | None]:
    if frame.empty:
        return {
            "event_count": 0,
            "mean_excess_return": None,
            "median_excess_return": None,
            "hit_rate": None,
            "mean_gross_return": None,
            "mean_kospi_return": None,
            "sharpe_like": None,
        }
    excess = pd.to_numeric(frame["excess_return"], errors="coerce").dropna()
    gross = pd.to_numeric(frame["gross_return"], errors="coerce").dropna()
    kospi = pd.to_numeric(frame["kospi_return"], errors="coerce").dropna()
    std = float(excess.std(ddof=1)) if len(excess) > 1 else math.nan
    return {
        "event_count": int(len(excess)),
        "mean_excess_return": none_if_nan(excess.mean()),
        "median_excess_return": none_if_nan(excess.median()),
        "hit_rate": none_if_nan((excess > 0).mean()),
        "mean_gross_return": none_if_nan(gross.mean()),
        "mean_kospi_return": none_if_nan(kospi.mean()),
        "sharpe_like": none_if_nan(excess.mean() / std if std and not math.isnan(std) else math.nan),
    }


def none_if_nan(value: float) -> float | None:
    value = float(value)
    return None if math.isnan(value) else value


def verdict(overall: dict[str, object], subperiod: dict[str, dict[str, object]]) -> str:
    mean = overall.get("mean_excess_return")
    hit = overall.get("hit_rate")
    if mean is None or hit is None:
        return "FAIL"
    sub_means = [block.get("mean_excess_return") for block in subperiod.values()]
    consistent = all(value is not None and value > 0 for value in sub_means)
    if mean > 0 and hit > 0.5 and consistent:
        return "STRONG" if mean > 0.02 and hit > 0.55 else "OK"
    if mean > 0 or hit > 0.5:
        return "WEAK"
    return "FAIL"


def build_distributions(signals: pd.DataFrame) -> pd.DataFrame:
    tradable = signals.loc[signals["included_in_trade"]].copy()
    if tradable.empty:
        return pd.DataFrame(columns=["dimension", "bucket", "event_count", "pct"])
    rows = []
    for dimension in ("event_type", "sector", "size_bucket"):
        counts = tradable[dimension].fillna("unknown").value_counts().sort_index()
        for bucket, count in counts.items():
            rows.append({"dimension": dimension, "bucket": bucket, "event_count": int(count), "pct": float(count / len(tradable))})
    return pd.DataFrame(rows)


def build_equity_curve(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["date", "gross_value", "net_value", "cash", "n_positions"])
    base = trades.loc[trades["holding_days"] == 21, ["exit_date", "gross_return"]].copy()
    if base.empty:
        return pd.DataFrame(columns=["date", "gross_value", "net_value", "cash", "n_positions"])
    daily = base.groupby("exit_date").agg(mean_return=("gross_return", "mean"), n_positions=("gross_return", "size")).reset_index()
    daily = daily.sort_values("exit_date")
    daily["gross_value"] = (1.0 + daily["mean_return"].fillna(0.0)).cumprod()
    daily["net_value"] = daily["gross_value"]
    daily["cash"] = 0.0
    return daily.rename(columns={"exit_date": "date"})[["date", "gross_value", "net_value", "cash", "n_positions"]]


def build_r_family_comparison(base_dir: Path, current_experiment: str, metrics: dict[str, object]) -> pd.DataFrame:
    rows = metric_rows(current_experiment, metrics)
    for path in sorted(base_dir.glob("R00[1-4]_*/*metrics.json")):
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if loaded.get("experiment") != current_experiment:
            rows.extend(metric_rows(str(loaded.get("experiment")), loaded))
    return pd.DataFrame(rows).drop_duplicates(["experiment", "holding_days"], keep="first").sort_values(["experiment", "holding_days"])


def metric_rows(experiment: str, metrics: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for key, block in metrics.get("overall", {}).items():
        rows.append(
            {
                "experiment": experiment,
                "holding_days": int(key.removesuffix("d")),
                "event_count": block.get("event_count"),
                "mean_excess_return": block.get("mean_excess_return"),
                "median_excess_return": block.get("median_excess_return"),
                "hit_rate": block.get("hit_rate"),
                "verdict": metrics.get("verdict", {}).get(key),
            }
        )
    return rows


def write_config(path: Path, spec: EventSpec, event_path: Path, panel_paths: tuple[Path, ...], kospi_path: Path) -> None:
    lines = [
        f"experiment: {spec.experiment}_{spec.slug}",
        f"event_path: {relative(event_path)}",
        "panel_paths:",
        *[f"  - {relative(panel)}" for panel in panel_paths],
        f"kospi_path: {relative(kospi_path)}",
        "universe: dynamic_top100_price_matched",
        "cost_model: gross_only_R005_pending",
        "network: disabled",
        "engine_changes: none",
        "strategy_changes: none",
        "execution_policy: signal_date_plus_next_krx_trading_day_open",
        "holding_days: [21, 63, 126]",
        "subperiods: [2018_2021, 2022_2026]",
        f"event_types: {list(spec.event_types)}",
        f"collapse_nearby_events: {spec.collapse_nearby}",
        "nearby_event_gap_trading_days: 21",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def write_report(path: Path, spec: EventSpec, metrics: dict[str, object], distributions: pd.DataFrame) -> None:
    lines = [
        f"# {spec.experiment} {spec.slug}",
        "",
        "Status: GENERATED BY `src.audit.r_family_event_backtest`",
        "",
        "## Metadata",
        "",
        "- OPENDART source: `research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet`",
        "- Price universe: dynamic_top100 2018-2024 + 2025-2026 KRX panels, price-matched events only.",
        "- Timing: OPENDART rows in this file are date-only; every signal executes at the next KRX trading-day open.",
        "- Cost: gross only; R005 is reserved for cost/execution lag.",
        "- KOSPI benchmark: `cap_weighted_return` from `krx_market_breadth_kospi_2010_2026.csv`.",
        "- Sector: source sector is unavailable in current event/panel files, so sector distribution is `unknown`.",
        "",
        "## Coverage",
        "",
        f"- Event rows after title filters: {metrics['event_rows']}",
        f"- Tradable price-matched events: {metrics['tradable_event_rows']}",
        f"- Excluded unmatched price rows: {metrics['excluded_unmatched_price_rows']}",
        "",
        "## Headline Metrics",
        "",
        "| Holding | Events | Mean excess | Median excess | Hit rate | Sharpe-like | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for holding_days in HOLDING_DAYS:
        key = f"{holding_days}d"
        block = metrics["overall"][key]
        lines.append(
            "| "
            + " | ".join(
                [
                    key,
                    str(block["event_count"]),
                    fmt(block["mean_excess_return"]),
                    fmt(block["median_excess_return"]),
                    fmt(block["hit_rate"]),
                    fmt(block["sharpe_like"]),
                    metrics["verdict"][key],
                ]
            )
            + " |"
        )
    lines.extend(["", "## Subperiod Breakdown", ""])
    for holding_days in HOLDING_DAYS:
        key = f"{holding_days}d"
        lines.extend([f"### {key}", "", "| Subperiod | Events | Mean excess | Hit rate | Verdict input |", "| --- | ---: | ---: | ---: | --- |"])
        for name, block in metrics["subperiod"][key].items():
            lines.append(f"| {name} | {block['event_count']} | {fmt(block['mean_excess_return'])} | {fmt(block['hit_rate'])} | mean>0 required |")
        lines.append("")
    lines.extend(["## Event / Size Distribution", ""])
    if distributions.empty:
        lines.append("No tradable distribution rows.")
    else:
        lines.extend(["| Dimension | Bucket | Events | Pct |", "| --- | --- | ---: | ---: |"])
        for row in distributions.itertuples(index=False):
            lines.append(f"| {row.dimension} | {row.bucket} | {row.event_count} | {fmt(row.pct)} |")
    lines.extend(
        [
            "",
            "## Verdict Criteria",
            "",
            "Pre-registered gate: mean excess > 0, hit rate > 50%, and both subperiod mean excess returns > 0. The per-horizon verdict above applies that rule mechanically.",
            "",
            "## Limitations",
            "",
            "- Disclosure amount, dividend increase versus prior year, first-dividend flags, and retirement size / market-cap ratios are not available in the R000 disclosure-title parquet and are therefore not used.",
            "- KOSPI benchmark uses close-to-close daily index returns while stock entries use next-day open and horizon exit close.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"


if __name__ == "__main__":
    raise SystemExit(main())
