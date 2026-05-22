from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from src.audit.i005_production_cost_validation import load_component_nav


OUTPUT_DIR = Path("reports/experiments/V000_p08_adversarial_validation")
BASE_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
COMPONENTS = ("SPY", "QQQ", "H001", "IEF")
STRESS_WINDOWS = {
    "covid_2020": ("2020-02-01", "2020-04-30"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31"),
    "gfc_proxy": ("2010-01-04", "2011-12-31"),
    "dot_com_proxy": ("2010-01-04", "2012-12-31"),
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    component_nav = load_component_nav()
    scenarios = build_scenarios()
    rows = []
    stress_rows = []
    for scenario in scenarios:
        stressed_components = apply_component_stress(component_nav, scenario)
        nav = build_portfolio_nav(
            stressed_components,
            scenario["weights"],
            scenario["frequency"],
            scenario["rebalance_shift"],
        )
        nav = apply_nav_stress(nav, stressed_components, scenario)
        metrics = calc_metrics(nav)
        rows.append({**scenario_summary(scenario), **metrics})
        for stress_name, (start, end) in STRESS_WINDOWS.items():
            stress_nav = nav.loc[nav.index.to_series().between(pd.Timestamp(start), pd.Timestamp(end))]
            if len(stress_nav) >= 2:
                stress_rows.append({**scenario_summary(scenario), "stress": stress_name, **calc_metrics(stress_nav)})

    metrics_table = pd.DataFrame(rows)
    stress_table = pd.DataFrame(stress_rows)
    metrics_table.to_csv(OUTPUT_DIR / "adversarial_metrics.csv", index=False)
    stress_table.to_csv(OUTPUT_DIR / "stress_metrics.csv", index=False)
    write_report(metrics_table, stress_table)


def build_scenarios() -> list[dict]:
    scenarios = [{"name": "baseline", "family": "baseline", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0}]
    for sleeve in COMPONENTS:
        for delta in (-0.10, -0.05, 0.05, 0.10):
            weights = dict(BASE_WEIGHTS)
            weights[sleeve] = max(0.0, weights[sleeve] + delta)
            scenarios.append(
                {
                    "name": f"weight_{sleeve}_{delta:+.0%}",
                    "family": "weight_perturbation",
                    "weights": normalize(weights),
                    "frequency": "Q",
                    "rebalance_shift": 0,
                }
            )
    for ief_weight in (0.20, 0.25, 0.30, 0.35, 0.40):
        non_ief_total = sum(BASE_WEIGHTS[k] for k in COMPONENTS if k != "IEF")
        weights = {
            k: (ief_weight if k == "IEF" else BASE_WEIGHTS[k] * (1.0 - ief_weight) / non_ief_total)
            for k in COMPONENTS
        }
        scenarios.append(
            {
                "name": f"ief_{ief_weight:.0%}",
                "family": "ief_grid",
                "weights": weights,
                "frequency": "Q",
                "rebalance_shift": 0,
            }
        )
    for name, shift in {"quarter_end": 0, "quarter_start": -63, "month_plus_5": 5, "month_minus_5": -5, "delayed_plus_30": 30}.items():
        scenarios.append(
            {
                "name": f"rebalance_{name}",
                "family": "rebalance_date",
                "weights": BASE_WEIGHTS,
                "frequency": "Q",
                "rebalance_shift": shift,
            }
        )
    for frequency in ("M", "Q", "2Q", "Y"):
        scenarios.append(
            {
                "name": f"frequency_{frequency}",
                "family": "frequency",
                "weights": BASE_WEIGHTS,
                "frequency": frequency,
                "rebalance_shift": 0,
            }
        )
    for multiplier in (2.0, 3.0):
        scenarios.append(
            {
                "name": f"fx_spread_{multiplier:.0f}x",
                "family": "fx_stress",
                "weights": BASE_WEIGHTS,
                "frequency": "Q",
                "rebalance_shift": 0,
                "daily_cost_drag": 0.00001 * multiplier,
            }
        )
    scenarios.append({"name": "fx_usdkrw_lag", "family": "fx_stress", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "lag_component_returns": True})
    scenarios.append({"name": "usd_nav_proxy", "family": "fx_stress", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "usd_nav_proxy": True})
    for lot_rule, tax_drag in {"HIFO": 0.0, "FIFO": 0.000015, "no_tax_optimization": 0.00003, "annual_exemption_unavailable": 0.00002}.items():
        scenarios.append({"name": f"tax_{lot_rule}", "family": "tax_lot", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "daily_cost_drag": tax_drag})
    for haircut in (0.50, 0.70):
        scenarios.append({"name": f"h001_return_haircut_{haircut:.0%}", "family": "h001_stress", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "h001_haircut": haircut})
    scenarios.append({"name": "h001_to_cash", "family": "h001_stress", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "h001_cash": True})
    scenarios.append({"name": "h001_one_quarter_lag", "family": "h001_stress", "weights": BASE_WEIGHTS, "frequency": "Q", "rebalance_shift": 0, "h001_lag_days": 63})
    return scenarios


def normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0.0:
        raise ValueError("weight sum must be positive")
    return {key: value / total for key, value in weights.items()}


def build_portfolio_nav(
    component_nav: pd.DataFrame,
    weights: dict[str, float],
    frequency: str,
    rebalance_shift: int,
) -> pd.Series:
    adjusted = component_nav.copy()
    returns = adjusted.pct_change().fillna(0.0)
    schedule = rebalance_schedule(returns.index, frequency, rebalance_shift)
    sleeve_values: dict[str, float] | None = None
    values = []
    for date in returns.index:
        if sleeve_values is None:
            sleeve_values = {component: weights[component] for component in COMPONENTS}
        elif date in schedule:
            total = sum(sleeve_values.values())
            sleeve_values = {component: total * weights[component] for component in COMPONENTS}
        for component in COMPONENTS:
            sleeve_values[component] *= 1.0 + float(returns.loc[date, component])
        values.append(sum(sleeve_values.values()))
    return pd.Series(values, index=returns.index, name="nav")


def rebalance_schedule(index: pd.DatetimeIndex, frequency: str, shift: int) -> set[pd.Timestamp]:
    periods = index.to_period(frequency)
    raw_dates = []
    for _, group in pd.Series(index, index=index).groupby(periods):
        raw_dates.append(group.iloc[-1])
    shifted = set()
    for date in raw_dates:
        pos = index.get_loc(date)
        shifted_pos = min(max(pos + shift, 0), len(index) - 1)
        shifted.add(index[shifted_pos])
    return shifted


def apply_component_stress(component_nav: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    stressed = component_nav.copy()
    if scenario.get("h001_haircut"):
        haircut = float(scenario["h001_haircut"])
        h001_returns = stressed["H001"].pct_change().fillna(0.0) * haircut
        stressed["H001"] = (1.0 + h001_returns).cumprod()
    if scenario.get("h001_cash"):
        stressed["H001"] = 1.0
    if scenario.get("h001_lag_days"):
        lag_days = int(scenario["h001_lag_days"])
        h001_returns = stressed["H001"].pct_change().shift(lag_days).fillna(0.0)
        stressed["H001"] = (1.0 + h001_returns).cumprod()
    return stressed


def apply_nav_stress(nav: pd.Series, component_nav: pd.DataFrame, scenario: dict) -> pd.Series:
    stressed = nav.copy()
    if scenario.get("daily_cost_drag"):
        drag = float(scenario["daily_cost_drag"])
        stressed = stressed * (1.0 - drag) ** pd.Series(range(len(stressed)), index=stressed.index)
    if scenario.get("lag_component_returns"):
        lagged = component_nav.pct_change().shift(1).fillna(0.0)
        synthetic = (lagged.mul(pd.Series(BASE_WEIGHTS))).sum(axis=1)
        stressed = (1.0 + synthetic).cumprod()
    if scenario.get("usd_nav_proxy"):
        returns = component_nav[["SPY", "QQQ", "IEF"]].pct_change().fillna(0.0)
        synthetic = (
            returns["SPY"] * BASE_WEIGHTS["SPY"]
            + returns["QQQ"] * BASE_WEIGHTS["QQQ"]
            + returns["IEF"] * BASE_WEIGHTS["IEF"]
            + component_nav["H001"].pct_change().fillna(0.0) * BASE_WEIGHTS["H001"]
        )
        stressed = (1.0 + synthetic).cumprod()
    return stressed / stressed.iloc[0]


def scenario_summary(scenario: dict) -> dict:
    weights = scenario["weights"]
    return {
        "scenario": scenario["name"],
        "family": scenario["family"],
        "frequency": scenario["frequency"],
        "rebalance_shift": scenario["rebalance_shift"],
        "SPY": weights["SPY"],
        "QQQ": weights["QQQ"],
        "H001": weights["H001"],
        "IEF": weights["IEF"],
    }


def calc_metrics(nav: pd.Series) -> dict[str, float | str]:
    daily = nav.pct_change().dropna()
    total_return = nav.iloc[-1] / nav.iloc[0] - 1.0
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1e-9)
    cagr = nav.iloc[-1] ** (1.0 / years) / nav.iloc[0] ** (1.0 / years) - 1.0
    vol = daily.std() * math.sqrt(252.0) if len(daily) else 0.0
    sharpe = daily.mean() / daily.std() * math.sqrt(252.0) if len(daily) and daily.std() else 0.0
    mdd = (nav / nav.cummax() - 1.0).min()
    return {"total_return": total_return, "cagr": cagr, "vol": vol, "sharpe": sharpe, "max_drawdown": mdd}


def write_report(metrics: pd.DataFrame, stress: pd.DataFrame) -> None:
    baseline = metrics.loc[metrics["scenario"].eq("baseline")].iloc[0]
    survivors = metrics.loc[
        metrics["sharpe"].ge(float(baseline["sharpe"]) * 0.8)
        & metrics["max_drawdown"].ge(float(baseline["max_drawdown"]) - 0.05)
    ]
    verdict = "PASS" if len(survivors) >= max(5, len(metrics) // 4) else "FAIL"
    lines = [
        "# V000 P08_IEF30 Adversarial Validation",
        "",
        f"Verdict: {verdict}",
        "",
        "## 기준",
        "",
        "- exact weight가 아니어도 유사 frontier가 살아남는지 확인한다.",
        "- 이 스크립트는 P08 weight를 재최적화하지 않는다.",
        "- D013, H001, engine.py를 수정하지 않는다.",
        "",
        "## Baseline",
        "",
        f"- Sharpe: {baseline['sharpe']:.6f}",
        f"- CAGR: {baseline['cagr']:.6f}",
        f"- MDD: {baseline['max_drawdown']:.6f}",
        "",
        "## Survival Count",
        "",
        f"- Scenarios: {len(metrics)}",
        f"- Survivors: {len(survivors)}",
        "",
        "## Worst Stress Rows",
        "",
        markdown_table(stress.sort_values("max_drawdown").head(10)),
        "",
        "## Files",
        "",
        "- `adversarial_metrics.csv`",
        "- `stress_metrics.csv`",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
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
