from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.run_experiment import run_h001_experiment


SLEEVE_VARIANT = "d013_kr_short_rate_sleeve"
BASELINE_VARIANT = "d013_baseline"


def run_h008_robustness(config_path: str | Path) -> None:
    config_path = Path(config_path)
    config = _read_yaml(config_path)
    base_config_path = Path(config["base_config"])
    base_config = _read_yaml(base_config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    scenario_config_dir = output_dir / "_scenario_configs"
    scenario_config_dir.mkdir(parents=True, exist_ok=True)

    cost_rows = []
    cost_outputs: dict[str, Path] = {}
    for label, multiplier in config["cost_stress"].items():
        scenario = _cost_multiplied_config(base_config, float(multiplier))
        scenario_dir = output_dir / "cost_stress" / str(label)
        _run_h001_scenario(scenario, scenario_dir, scenario_config_dir / f"cost_{label}.yaml")
        cost_outputs[str(label)] = scenario_dir
        cost_rows.append(_scenario_summary_row(str(label), scenario, scenario_dir, multiplier=float(multiplier)))
    cost_stress = pd.DataFrame(cost_rows)
    cost_stress.to_csv(output_dir / "cost_stress.csv", index=False)

    slippage_rows = []
    slippage_outputs: dict[str, Path] = {}
    base_slippage = float(base_config["costs"]["slippage_bps"])
    for label, extra_bps in config["slippage_stress"].items():
        scenario = copy.deepcopy(base_config)
        scenario["costs"] = dict(scenario["costs"])
        scenario["costs"]["slippage_bps"] = base_slippage + float(extra_bps)
        scenario_dir = output_dir / "slippage_stress" / str(label)
        _run_h001_scenario(scenario, scenario_dir, scenario_config_dir / f"slippage_{label}.yaml")
        slippage_outputs[str(label)] = scenario_dir
        slippage_rows.append(
            _scenario_summary_row(str(label), scenario, scenario_dir, extra_slippage_bps=float(extra_bps))
        )
    slippage_stress = pd.DataFrame(slippage_rows)
    slippage_stress.to_csv(output_dir / "slippage_stress.csv", index=False)

    base_dir = cost_outputs["base"]
    subperiod = _subperiod_breakdown(base_dir, config)
    subperiod.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    year_decomp = _year_decomposition(base_dir)
    year_decomp.to_csv(output_dir / "sleeve_year_decomposition.csv", index=False)
    carry_by_year = _carry_contribution_by_year(base_dir)
    carry_by_year.to_csv(output_dir / "carry_contribution_by_year.csv", index=False)

    verdict = _verdict_table(config, cost_stress, slippage_stress, subperiod, year_decomp)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_json(output_dir / "robustness_summary.json", _summary_payload(cost_stress, slippage_stress, subperiod, year_decomp, verdict))
    _write_report(output_dir, cost_stress, slippage_stress, subperiod, year_decomp, verdict)


def _run_h001_scenario(config: dict[str, Any], output_dir: Path, scenario_config_path: Path) -> None:
    scenario = copy.deepcopy(config)
    scenario["experiment_id"] = "H001"
    scenario["output_dir"] = str(output_dir)
    scenario_config_path.write_text(yaml.safe_dump(scenario, allow_unicode=True, sort_keys=False), encoding="utf-8")
    run_h001_experiment(scenario, scenario_config_path)


def _cost_multiplied_config(base_config: dict[str, Any], multiplier: float) -> dict[str, Any]:
    scenario = copy.deepcopy(base_config)
    scenario["costs"] = {
        key: float(value) * multiplier
        for key, value in base_config["costs"].items()
    }
    return scenario


def _scenario_summary_row(
    label: str,
    config: dict[str, Any],
    output_dir: Path,
    *,
    multiplier: float | None = None,
    extra_slippage_bps: float | None = None,
) -> dict[str, Any]:
    metrics = _read_metrics(output_dir)[SLEEVE_VARIANT]
    baseline = _read_metrics(output_dir)[BASELINE_VARIANT]
    return {
        "scenario": label,
        "cost_multiplier": multiplier,
        "extra_slippage_bps": extra_slippage_bps,
        "commission_bps": float(config["costs"]["commission_bps"]),
        "tax_bps_sell": float(config["costs"]["tax_bps_sell"]),
        "slippage_bps": float(config["costs"]["slippage_bps"]),
        "h001_cumulative_net_total_return": float(metrics["cumulative_net_total_return"]),
        "h001_sharpe": float(metrics["sharpe"]),
        "h001_max_drawdown": float(metrics["max_drawdown"]),
        "d013_cumulative_net_total_return": float(baseline["cumulative_net_total_return"]),
        "delta_vs_d013": float(metrics["cumulative_net_total_return"]) - float(baseline["cumulative_net_total_return"]),
    }


def _subperiod_breakdown(base_dir: Path, config: dict[str, Any]) -> pd.DataFrame:
    equity = _read_equity(base_dir)
    rows = []
    for period in config["subperiods"]:
        start = pd.Timestamp(period["start"])
        end = pd.Timestamp(period["end"])
        h001_return = _window_return(equity, "h001", start, end)
        d013_return = _window_return(equity, "d013", start, end)
        rows.append(
            {
                "subperiod": period["name"],
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "h001_cumulative_return": h001_return,
                "d013_cumulative_return": d013_return,
                "delta_vs_d013": h001_return - d013_return,
            }
        )
    excluded_years = set(int(year) for year in config["spike_exclusion_years"])
    h001_ex = _excluded_year_return(equity, "h001", excluded_years)
    d013_ex = _excluded_year_return(equity, "d013", excluded_years)
    rows.append(
        {
            "subperiod": "exclude_2020_2025",
            "start": equity["date"].min().date().isoformat(),
            "end": equity["date"].max().date().isoformat(),
            "h001_cumulative_return": h001_ex,
            "d013_cumulative_return": d013_ex,
            "delta_vs_d013": h001_ex - d013_ex,
        }
    )
    return pd.DataFrame(rows)


def _year_decomposition(base_dir: Path) -> pd.DataFrame:
    equity = _read_equity(base_dir)
    years = sorted(equity["date"].dt.year.unique())
    full_delta = _window_return(equity, "h001", equity["date"].min(), equity["date"].max()) - _window_return(
        equity, "d013", equity["date"].min(), equity["date"].max()
    )
    rows = []
    for year in years:
        year_data = equity.loc[equity["date"].dt.year.eq(year)]
        if year_data.empty:
            continue
        start = year_data["date"].min()
        end = year_data["date"].max()
        h001_return = _window_return(equity, "h001", start, end)
        d013_return = _window_return(equity, "d013", start, end)
        delta = h001_return - d013_return
        rows.append(
            {
                "year": int(year),
                "h001_return": h001_return,
                "d013_return": d013_return,
                "delta_vs_d013": delta,
                "delta_share_of_total_delta": delta / full_delta if full_delta else float("nan"),
            }
        )
    data = pd.DataFrame(rows)
    abs_sum = data["delta_vs_d013"].abs().sum()
    data["abs_delta_share"] = data["delta_vs_d013"].abs() / abs_sum if abs_sum else float("nan")
    return data


def _carry_contribution_by_year(base_dir: Path) -> pd.DataFrame:
    carry = pd.read_csv(base_dir / "off_carry_contribution.csv", parse_dates=["signal_date", "execution_date"])
    if carry.empty:
        return pd.DataFrame(columns=["year", "off_quarters", "quarter_carry_sum", "quarter_carry_compounded"])
    carry["year"] = carry["execution_date"].dt.year
    rows = []
    for year, group in carry.groupby("year", sort=True):
        rows.append(
            {
                "year": int(year),
                "off_quarters": int(len(group)),
                "quarter_carry_sum": float(group["quarter_carry"].sum()),
                "quarter_carry_compounded": float((1.0 + group["quarter_carry"]).prod() - 1.0),
            }
        )
    return pd.DataFrame(rows)


def _verdict_table(
    config: dict[str, Any],
    cost_stress: pd.DataFrame,
    slippage_stress: pd.DataFrame,
    subperiod: pd.DataFrame,
    year_decomp: pd.DataFrame,
) -> pd.DataFrame:
    criteria = config["pass_criteria"]
    cost_by_scenario = cost_stress.set_index("scenario")
    slippage_by_scenario = slippage_stress.set_index("scenario")
    subperiod_by_name = subperiod.set_index("subperiod")
    max_year_share = float(year_decomp["abs_delta_share"].max())
    rows = [
        _verdict_row(
            "3x cost cumulative",
            float(cost_by_scenario.loc["3x", "h001_cumulative_net_total_return"]),
            float(criteria["cost_3x_cumulative_min"]),
            ">=",
        ),
        _verdict_row(
            "5x cost cumulative",
            float(cost_by_scenario.loc["5x", "h001_cumulative_net_total_return"]),
            float(criteria["cost_5x_cumulative_min"]),
            ">=",
        ),
        _verdict_row(
            "+20bps slippage cumulative",
            float(slippage_by_scenario.loc["plus_20_bps", "h001_cumulative_net_total_return"]),
            float(criteria["plus_20bps_slippage_cumulative_min"]),
            ">=",
        ),
        _verdict_row(
            "spike years excluded cumulative",
            float(subperiod_by_name.loc["exclude_2020_2025", "h001_cumulative_return"]),
            float(criteria["spike_excluded_cumulative_min"]),
            ">=",
        ),
        _verdict_row(
            "max single-year contribution share",
            max_year_share,
            float(criteria["max_single_year_delta_share"]),
            "<",
        ),
    ]
    verdict = pd.DataFrame(rows)
    verdict.loc[:, "overall_pass"] = bool(verdict["passes"].all())
    return verdict


def _verdict_row(name: str, value: float, threshold: float, op: str) -> dict[str, Any]:
    passes = value >= threshold if op == ">=" else value < threshold
    return {"criterion": name, "value": value, "operator": op, "threshold": threshold, "passes": bool(passes)}


def _summary_payload(*frames: pd.DataFrame) -> dict[str, Any]:
    names = ["cost_stress", "slippage_stress", "subperiod_breakdown", "sleeve_year_decomposition", "verdict"]
    return {name: json.loads(frame.to_json(orient="records")) for name, frame in zip(names, frames)}


def _write_report(
    output_dir: Path,
    cost_stress: pd.DataFrame,
    slippage_stress: pd.DataFrame,
    subperiod: pd.DataFrame,
    year_decomp: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = [
        "# H008 H001 Robustness",
        "",
        "## Cost Stress",
        _markdown_table(cost_stress, ["scenario", "h001_cumulative_net_total_return", "h001_sharpe", "h001_max_drawdown"]),
        "",
        "## Slippage Stress",
        _markdown_table(slippage_stress, ["scenario", "slippage_bps", "h001_cumulative_net_total_return", "h001_sharpe"]),
        "",
        "## Subperiod",
        _markdown_table(subperiod, ["subperiod", "h001_cumulative_return", "d013_cumulative_return", "delta_vs_d013"]),
        "",
        "## Year Decomposition",
        _markdown_table(year_decomp, ["year", "h001_return", "d013_return", "delta_vs_d013", "abs_delta_share"]),
        "",
        "## Verdict",
        _markdown_table(verdict, ["criterion", "value", "operator", "threshold", "passes"]),
    ]
    output_dir.joinpath("report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    data = frame.loc[:, columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in data.itertuples(index=False):
        lines.append("| " + " | ".join(_format_value(value) for value in row) + " |")
    return "\n".join(lines)


def _format_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _read_equity(base_dir: Path) -> pd.DataFrame:
    equity = pd.read_csv(base_dir / "equity_curve.csv", parse_dates=["date"])
    return equity.rename(
        columns={
            "d013_baseline_net_value": "d013",
            "d013_kr_short_rate_sleeve_net_value": "h001",
        }
    )


def _window_return(equity: pd.DataFrame, column: str, start: pd.Timestamp, end: pd.Timestamp) -> float:
    data = equity.loc[equity["date"].between(start, end), ["date", column]]
    if data.empty:
        return float("nan")
    values = pd.to_numeric(data[column], errors="raise")
    return float(values.iloc[-1] / values.iloc[0] - 1.0)


def _excluded_year_return(equity: pd.DataFrame, column: str, excluded_years: set[int]) -> float:
    values = pd.to_numeric(equity[column], errors="raise")
    returns = values.pct_change().fillna(0.0)
    years = equity["date"].dt.year
    prev_years = years.shift(1).fillna(years)
    keep = ~years.isin(excluded_years) & ~prev_years.isin(excluded_years)
    return float((1.0 + returns.loc[keep]).prod() - 1.0)


def _read_metrics(output_dir: Path) -> dict[str, dict[str, Any]]:
    return json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))


def _read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run H008 H001 robustness validation.")
    parser.add_argument("--config", default="configs/backtests/h008.yaml")
    args = parser.parse_args(argv)
    run_h008_robustness(args.config)


if __name__ == "__main__":
    main()
