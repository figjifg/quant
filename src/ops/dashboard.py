from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ops.gross_tax_nav import load_defensive_shadow_component_nav
from src.ops.nav_update import ROOT, add_nav_metrics, load_component_nav
from src.ops.rebalance_report import drifted_weights, format_markdown_table, quarter_start_proxy

OUTPUT_PATH = ROOT / "paper_trading/operations/dashboard.md"

FINAL_DASHBOARD_PORTFOLIOS: dict[str, dict[str, float]] = {
    "P08_IEF30": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30},
    "N002_B_cash_10": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "CASH": 0.10},
    "N001_B_GLD_10": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
    "QQQ_100": {"QQQ": 1.00},
    "SPY_100": {"SPY": 1.00},
    "H001": {"H001": 1.00},
}


def generate_dashboard(
    as_of_date: str | pd.Timestamp | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Generate the final six-portfolio paper tracking dashboard."""

    as_of = pd.Timestamp(as_of_date) if as_of_date else None
    component_nav = load_defensive_shadow_component_nav(as_of)
    latest_date = component_nav.index.max()
    quarter = f"{latest_date.year}-Q{((latest_date.month - 1) // 3) + 1}"
    quarter_nav = component_nav.loc[component_nav.index >= quarter_start_proxy(quarter)]

    rows = []
    for portfolio, weights in FINAL_DASHBOARD_PORTFOLIOS.items():
        nav = sum(component_nav[ticker] * weight for ticker, weight in weights.items())
        metrics = add_nav_metrics(pd.DataFrame({"date": component_nav.index, "nav": nav.values}))
        latest = metrics.iloc[-1]
        drift_pp = _max_abs_drift_pp(quarter_nav, weights)
        rows.append(
            {
                "portfolio": portfolio,
                "role": _portfolio_role(portfolio),
                "nav": latest["nav"],
                "qtd_return": latest["quarterly_return"],
                "ytd_return": latest["ytd_return"],
                "mdd": metrics["mdd"].min(),
                "max_abs_drift_pp": drift_pp,
            }
        )

    table = pd.DataFrame(rows)
    lines = [
        "# Final Paper Dashboard",
        "",
        f"- As-of date: {latest_date:%Y-%m-%d}",
        "- Scope: six portfolio Research Freeze v2 dashboard.",
        "- Status: paper operations only; no live order authorization.",
        "",
        "## Portfolio View",
        "",
        format_markdown_table(table),
        "",
        "## Decision View",
        "",
        "- Primary remains `P08_IEF30`.",
        "- `N002_B_cash_10` and `N001_B_GLD_10` are defensive shadows only.",
        "- `QQQ_100`, `SPY_100`, and `H001` are benchmarks/reference sleeves.",
        "- Four quarters of forward tracking are required before any go/no-go review.",
        "- Tax-professional and broker-operation confirmation are required before live use.",
    ]

    path = Path(output_path) if output_path else OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _max_abs_drift_pp(component_nav: pd.DataFrame, target: dict[str, float]) -> float:
    if len(component_nav) < 2:
        return 0.0
    current_weights = drifted_weights(component_nav, target)
    return max(abs(current_weights[ticker] - weight) for ticker, weight in target.items()) * 100.0


def _portfolio_role(portfolio: str) -> str:
    roles = {
        "P08_IEF30": "primary",
        "N002_B_cash_10": "defensive shadow",
        "N001_B_GLD_10": "defensive shadow",
        "QQQ_100": "benchmark",
        "SPY_100": "benchmark",
        "H001": "Korean sleeve only",
    }
    return roles[portfolio]


if __name__ == "__main__":
    print(generate_dashboard().relative_to(ROOT))
