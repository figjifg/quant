from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from src.run_experiment import (
    _b011_candidate_years,
    _b011_segments,
    _b011_trades,
    _build_f006_to_f010_context,
    _c010_subperiod_breakdown,
    _costs_from_config,
    _d001_wide_equity_curve,
    _d009_year_breakdown,
    _e003_variant_metrics,
    _e003_zero_cost_result,
    _e015_contribution_tables,
    _e015_overlap,
    _f002_signals,
    _jsonable,
    _quarterly_execution_candidates,
    _run_segmented_cash,
    _summary_row,
    _write_json,
    _write_ticker_safe_csv,
    build_combined_d013_direct_candidates,
    build_kospi_buy_and_hold_result,
    quarterly_execution_dates,
    run_quarterly_mcap_backtest,
)


F010_DIR = Path("reports/experiments/F010_composite_candidate/A_d013_direct")
F001_BASELINE = Path("reports/experiments/F001_layer3_neutral_baseline/baseline_summary.csv")
F011_CONFIG = Path("configs/backtests/f011.yaml")
F012_CONFIG = Path("configs/backtests/f012.yaml")


def main() -> None:
    source_config = _load_yaml(Path("configs/backtests/f010_a.yaml"))
    f011_config = _load_yaml(F011_CONFIG)
    f012_config = _load_yaml(F012_CONFIG)

    context = _build_f006_to_f010_context(source_config)
    base_candidates = build_combined_d013_direct_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        stock_scores=context["stock_scores"],
        calendar=context["calendar"],
        top_n=int(source_config["selection"]["n"]),
    )
    filtered = _quarterly_execution_candidates(
        base_candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    base_runs, base_metrics, zero_result = _run_portfolio(source_config, context, filtered, source_config["costs"])

    f011_dir = Path(f011_config["output_dir"])
    _write_f011_outputs(f011_dir, f011_config, source_config, context, filtered, base_runs, base_metrics, zero_result)
    _assert_f010_a_reproduction(base_metrics)

    f012_dir = Path(f012_config["output_dir"])
    _write_f012_outputs(f012_dir, f012_config, source_config, context, base_candidates, filtered, base_runs, base_metrics)


def _run_portfolio(
    source_config: dict[str, Any],
    context: dict[str, Any],
    candidates: pd.DataFrame,
    costs_config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], Any]:
    costs = _costs_from_config(costs_config)
    runs = {
        "factor_macro_gate_mcap": run_quarterly_mcap_backtest(
            panel=context["panel"],
            calendar=context["calendar"],
            candidates=candidates,
            costs=costs,
            segments=context["segments"],
            rebalance_dates=quarterly_execution_dates(
                context["calendar"], context["quarterly_log"], context["segments"]
            ),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            context["market_breadth"], calendar=context["calendar"], segments=context["segments"]
        ),
        "cash": _run_segmented_cash(calendar=context["calendar"], segments=context["segments"]),
    }
    zero_result = _e003_zero_cost_result(
        context["panel"], context["calendar"], candidates, context["quarterly_log"], context["segments"], weighted=False
    )
    metrics = _e003_variant_metrics(runs, zero_result, context["calendar"], context["candidate_years"])
    return runs, metrics, zero_result


def _write_f011_outputs(
    output_dir: Path,
    f011_config: dict[str, Any],
    source_config: dict[str, Any],
    context: dict[str, Any],
    filtered: pd.DataFrame,
    runs: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    zero_result: Any,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(output_dir / "config.yaml", f011_config)
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_f002_signals(filtered, score_column="stock_combined_score_universe"), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        output_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        output_dir / "subperiod_breakdown.csv", index=False
    )
    shutil.copyfile(F010_DIR / "diagnostics_summary.csv", output_dir / "diagnostics_summary.csv")
    shutil.copyfile(F010_DIR / "rank_ic.csv", output_dir / "rank_ic.csv")
    shutil.copyfile(F010_DIR / "top_bottom_spread.csv", output_dir / "top_bottom_spread.csv")
    shutil.copyfile(F010_DIR / "stock_combined_scores.csv", output_dir / "stock_combined_scores.csv")
    shutil.copyfile(F010_DIR / "quarterly_regime_log.csv", output_dir / "quarterly_regime_log.csv")
    _write_f011_report(output_dir, source_config, metrics)


def _write_f012_outputs(
    output_dir: Path,
    f012_config: dict[str, Any],
    source_config: dict[str, Any],
    context: dict[str, Any],
    base_candidates: pd.DataFrame,
    filtered: pd.DataFrame,
    base_runs: dict[str, Any],
    base_metrics: dict[str, dict[str, Any]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(output_dir / "config.yaml", f012_config)
    _write_json(output_dir / "metrics.json", base_metrics)
    _write_ticker_safe_csv(_b011_trades(base_runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_f002_signals(filtered, score_column="stock_combined_score_universe"), output_dir / "signals.csv")
    _d001_wide_equity_curve(base_runs).to_csv(output_dir / "equity_curve.csv", index=False)
    context["quarterly_log"].to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    cost_stress = _cost_stress(source_config, f012_config, context, filtered)
    spike = _spike_exclusion(source_config, f012_config, context, base_candidates)
    contribution = _e015_contribution_tables(base_runs["factor_macro_gate_mcap"], filtered, context["calendar"])
    d013_overlap = _e015_overlap(filtered, Path("reports/experiments/D013_d009_threshold_minus_0p2/signals.csv"), "d013")
    e014_overlap = _e015_overlap(filtered, Path("reports/experiments/E014_rs_breadth_top4_registration/signals.csv"), "e014")
    e014_overlap = e014_overlap.rename(columns={"e015_count": "f011_count", "e015_tickers": "f011_tickers"})
    d013_overlap = d013_overlap.rename(columns={"e015_count": "f011_count", "e015_tickers": "f011_tickers"})
    topk = _topk_stability(base_metrics, int(f012_config["validation"]["top_k"]))
    pass_fail = _pass_fail(base_metrics, cost_stress, spike)

    cost_stress.to_csv(output_dir / "cost_stress_summary.csv", index=False)
    spike.to_csv(output_dir / "spike_exclusion.csv", index=False)
    topk.to_csv(output_dir / "topk_stability.csv", index=False)
    contribution["year"].to_csv(output_dir / "year_contribution.csv", index=False)
    contribution["sector"].to_csv(output_dir / "sector_contribution.csv", index=False)
    contribution["stock"].to_csv(output_dir / "stock_contribution.csv", index=False)
    contribution["rebalance"].to_csv(output_dir / "rebalance_contribution.csv", index=False)
    d013_overlap.to_csv(output_dir / "d013_overlap.csv", index=False)
    e014_overlap.to_csv(output_dir / "e014_overlap.csv", index=False)
    pass_fail.to_csv(output_dir / "pass_fail.csv", index=False)
    _write_f012_report(output_dir, base_metrics, cost_stress, spike, topk, contribution, d013_overlap, e014_overlap, pass_fail)


def _cost_stress(
    source_config: dict[str, Any],
    f012_config: dict[str, Any],
    context: dict[str, Any],
    filtered: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for scenario in ("base", "2x", "3x"):
        _, metrics, _ = _run_portfolio(source_config, context, filtered, f012_config["cost_scenarios"][scenario])
        row = _summary_row(scenario, metrics)
        row.update(f012_config["cost_scenarios"][scenario])
        rows.append(row)
    return pd.DataFrame(rows)


def _spike_exclusion(
    source_config: dict[str, Any],
    f012_config: dict[str, Any],
    context: dict[str, Any],
    base_candidates: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    base_excluded = [int(year) for year in source_config["period"]["exclude_calendar_years"]]
    for years in f012_config["spike_exclusions"]:
        scenario_config = dict(source_config)
        scenario_config["period"] = dict(source_config["period"])
        scenario_config["period"]["exclude_calendar_years"] = sorted(set(base_excluded).union(int(year) for year in years))
        segments = _b011_segments(scenario_config)
        filtered = _quarterly_execution_candidates(base_candidates, context["calendar"], context["quarterly_log"], segments)
        scenario_context = dict(context)
        scenario_context["segments"] = segments
        scenario_context["candidate_years"] = _b011_candidate_years(scenario_config)
        _, metrics, _ = _run_portfolio(source_config, scenario_context, filtered, source_config["costs"])
        row = _summary_row("+".join(str(year) for year in years), metrics)
        row["excluded_years"] = "+".join(str(year) for year in years)
        rows.append(row)
    return pd.DataFrame(rows)


def _topk_stability(metrics: dict[str, dict[str, Any]], top_k: int) -> pd.DataFrame:
    row = _summary_row(f"top_{top_k}_frozen", metrics)
    row["top_k"] = top_k
    row["note"] = "F012 validates frozen K=5 only; no exploratory K grid was run"
    return pd.DataFrame([row])


def _pass_fail(
    metrics: dict[str, dict[str, Any]],
    cost_stress: pd.DataFrame,
    spike: pd.DataFrame,
) -> pd.DataFrame:
    f001 = _f001_a()
    base = metrics["factor_macro_gate_mcap"]
    cost3 = cost_stress.loc[cost_stress["variant"].eq("3x")].iloc[0]
    spike_all = spike.loc[spike["excluded_years"].eq("2020+2025+2026")].iloc[0]
    rows = [
        ("cumulative_gt_f001_a", base["cumulative_net_total_return"], f001["cum_net"], base["cumulative_net_total_return"] > f001["cum_net"]),
        ("sharpe_gt_f001_a", base["sharpe"], f001["sharpe"], base["sharpe"] > f001["sharpe"]),
        ("mdd_gt_f001_a", base["max_drawdown"], f001["mdd"], base["max_drawdown"] > f001["mdd"]),
        ("cost_3x_cumulative_gt_f001_a", cost3["cumulative_net_total_return"], f001["cum_net"], cost3["cumulative_net_total_return"] > f001["cum_net"]),
        ("spike_excluded_cumulative_gt_f001_a", spike_all["cumulative_net_total_return"], f001["cum_net"], spike_all["cumulative_net_total_return"] > f001["cum_net"]),
    ]
    return pd.DataFrame(rows, columns=["criterion", "actual", "threshold", "passed"])


def _write_f011_report(output_dir: Path, source_config: dict[str, Any], metrics: dict[str, dict[str, Any]]) -> None:
    f001 = _f001_a()
    base = metrics["factor_macro_gate_mcap"]
    diag = pd.read_csv(F010_DIR / "diagnostics_summary.csv")
    summary = pd.DataFrame(
        [
            {
                "variant": "F011 / F010-A D013 direct",
                "cumulative_net_total_return": base["cumulative_net_total_return"],
                "sharpe": base["sharpe"],
                "max_drawdown": base["max_drawdown"],
                "trade_count": base["trade_count"],
                "f001_a_cumulative_net_total_return": f001["cum_net"],
                "cum_ratio_vs_f001_a": base["cumulative_net_total_return"] / f001["cum_net"],
            }
        ]
    )
    lines = [
        "# F011 Layer 3 Composite Champion Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- source: F010-A exact reproduction from {source_config['output_dir']}/A_d013_direct",
        f"- panels: {', '.join(source_config['panels'])}",
        "- carrier: D013 direct",
        "- score: F010 composite, frozen",
        "- timing: signal quarter-end T; execution T+1 or later",
        "",
    ]
    lines.extend(_table("Registration Summary", summary))
    lines.extend(_table("Diagnostics", diag))
    lines.extend(["## Verdict", "", "- Codex reports metrics only; F012 performs validation.", ""])
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_f012_report(
    output_dir: Path,
    metrics: dict[str, dict[str, Any]],
    cost_stress: pd.DataFrame,
    spike: pd.DataFrame,
    topk: pd.DataFrame,
    contribution: dict[str, pd.DataFrame],
    d013_overlap: pd.DataFrame,
    e014_overlap: pd.DataFrame,
    pass_fail: pd.DataFrame,
) -> None:
    base = metrics["factor_macro_gate_mcap"]
    f001 = _f001_a()
    verdict = "FAIL" if not bool(pass_fail["passed"].all()) else "PASS"
    lines = [
        "# F012 Layer 3 Composite Validation Metrics Summary",
        "",
        "## Verdict",
        "",
        f"- verdict: {verdict}",
        f"- F011 cumulative: {base['cumulative_net_total_return']}",
        f"- F001-A cumulative: {f001['cum_net']}",
        f"- F011/F001-A cumulative ratio: {base['cumulative_net_total_return'] / f001['cum_net']}",
        "",
    ]
    lines.extend(_table("Pass/Fail", pass_fail))
    lines.extend(_table("Cost Stress", cost_stress))
    lines.extend(_table("Spike Exclusion", spike))
    lines.extend(_table("Top-K Stability", topk))
    lines.extend(_table("Year Contribution", contribution["year"]))
    lines.extend(_table("Sector Contribution", contribution["sector"]))
    lines.extend(_table("Stock Contribution", contribution["stock"].head(20)))
    lines.extend(_table("Rebalance Contribution", contribution["rebalance"].head(20)))
    lines.extend(_table("D013 Overlap", d013_overlap))
    lines.extend(_table("E014 Overlap", e014_overlap))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _assert_f010_a_reproduction(metrics: dict[str, dict[str, Any]]) -> None:
    expected = json.loads((F010_DIR / "metrics.json").read_text(encoding="utf-8"))
    actual = metrics["factor_macro_gate_mcap"]
    baseline = expected["factor_macro_gate_mcap"]
    keys = ("cumulative_net_total_return", "sharpe", "max_drawdown", "trade_count")
    mismatches = [key for key in keys if actual[key] != baseline[key]]
    if mismatches:
        raise AssertionError(f"F011 failed to reproduce F010-A keys: {mismatches}")


def _f001_a() -> pd.Series:
    baseline = pd.read_csv(F001_BASELINE)
    return baseline.loc[baseline["baseline"].eq("F001-A D013 direct")].iloc[0]


def _table(title: str, frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return [f"## {title}", "", "_empty_", ""]
    rendered = _markdown_table(frame)
    return [f"## {title}", "", *rendered, ""]


def _markdown_table(frame: pd.DataFrame) -> list[str]:
    columns = [str(column) for column in frame.columns]
    rows = []
    for _, row in frame.iterrows():
        rows.append([_markdown_cell(row[column]) for column in frame.columns])
    return [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
        *("| " + " | ".join(row) + " |" for row in rows),
    ]


def _markdown_cell(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(_jsonable(data), sort_keys=False, allow_unicode=True), encoding="utf-8")


if __name__ == "__main__":
    main()
