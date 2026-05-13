from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.reporting.metrics import METRIC_KEYS


BASELINE_ROWS = (
    "headline",
    "B0_cash",
    "B1_buy_and_hold",
    "B2_universe_5d_rebalance",
    "B3_price_momentum",
)
BASELINE_COLUMNS = (
    "total_return",
    "annualized_return",
    "sharpe",
    "max_drawdown",
    "hit_rate",
    "trade_count",
)
METADATA_KEYS = (
    "panels_used",
    "is_start",
    "is_end",
    "oos_start",
    "oos_end",
    "estimate_row_policy",
    "integrated_column_policy",
    "signal_exit_policy",
    "calendar_source",
    "krx_close_derivation_summary",
    "n_tickers",
    "n_trading_days",
)


def write_report(
    output_dir: Path,
    run_metadata: dict[str, Any],
    metrics: dict[str, Any],
    baselines: dict[str, dict[str, Any]],
    cost_sensitivity: pd.DataFrame | None,
) -> None:
    """Write deterministic E001 report.md content from generated artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# E001 Metrics Summary", ""]

    lines.extend(_metadata_block(run_metadata))
    lines.extend(_metric_table("IS Metrics", metrics.get("is", {})))
    lines.extend(_metric_table("OOS Metrics", metrics.get("oos", {})))
    lines.extend(_baseline_table("IS Baseline Comparison", metrics, baselines, "is"))
    lines.extend(_baseline_table("OOS Baseline Comparison", metrics, baselines, "oos"))
    if cost_sensitivity is not None:
        lines.extend(_dataframe_table("Cost Sensitivity", cost_sensitivity))
    lines.extend(_diagnostic_keys(metrics, baselines))

    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _metadata_block(run_metadata: dict[str, Any]) -> list[str]:
    lines = ["## Metadata", "", "| key | value |", "| --- | --- |"]
    for key in METADATA_KEYS:
        lines.append(f"| {key} | {_format_value(run_metadata.get(key))} |")
    lines.append("")
    return lines


def _metric_table(title: str, metric_block: dict[str, Any]) -> list[str]:
    lines = [f"## {title}", "", "| metric | value |", "| --- | ---: |"]
    for key in METRIC_KEYS:
        lines.append(f"| {key} | {_format_value(metric_block.get(key))} |")
    lines.append("")
    return lines


def _baseline_table(
    title: str,
    headline_metrics: dict[str, Any],
    baselines: dict[str, dict[str, Any]],
    split: str,
) -> list[str]:
    rows: dict[str, dict[str, Any]] = {"headline": headline_metrics.get(split, {})}
    rows.update({name: baselines.get(name, {}).get(split, {}) for name in BASELINE_ROWS if name != "headline"})

    lines = [
        f"## {title}",
        "",
        "| run | " + " | ".join(BASELINE_COLUMNS) + " |",
        "| --- | " + " | ".join("---:" for _ in BASELINE_COLUMNS) + " |",
    ]
    for row_name in BASELINE_ROWS:
        values = " | ".join(_format_value(rows.get(row_name, {}).get(column)) for column in BASELINE_COLUMNS)
        lines.append(f"| {row_name} | {values} |")
    lines.append("")
    return lines


def _dataframe_table(title: str, data: pd.DataFrame) -> list[str]:
    lines = [f"## {title}", ""]
    if data.empty:
        lines.extend(["| empty |", "| --- |", ""])
        return lines

    columns = [str(column) for column in data.columns]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for _, row in data.iterrows():
        lines.append("| " + " | ".join(_format_value(row[column]) for column in data.columns) + " |")
    lines.append("")
    return lines


def _diagnostic_keys(metrics: dict[str, Any], baselines: dict[str, dict[str, Any]]) -> list[str]:
    standard_metric_keys = {"is", "oos", "full"}
    keys = sorted(
        key
        for key in set(metrics) | set(baselines)
        if key not in standard_metric_keys and key not in BASELINE_ROWS
    )
    lines = ["## Diagnostic Keys", ""]
    if keys:
        lines.extend(f"- {key}" for key in keys)
    else:
        lines.append("- None")
    lines.append("")
    return lines


def _format_value(value: Any) -> str:
    normalized = json.loads(json.dumps(_jsonable(value), allow_nan=True, sort_keys=True))
    if isinstance(normalized, float):
        return f"{normalized:.6g}"
    if isinstance(normalized, (list, dict)):
        return json.dumps(normalized, ensure_ascii=False, allow_nan=True, sort_keys=True, separators=(",", ":"))
    if normalized is None:
        return ""
    return str(normalized)


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, tuple):
        return [_jsonable(inner) for inner in value]
    if isinstance(value, list):
        return [_jsonable(inner) for inner in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(inner) for key, inner in value.items()}
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return float("nan")
    return value
