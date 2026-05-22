from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ops.nav_update import DEFAULT_PORTFOLIOS, ROOT, load_component_nav

OUTPUT_DIR = ROOT / "paper_trading/operations/rebalance_reports"
TARGET = DEFAULT_PORTFOLIOS["P08_IEF30"]


def generate_rebalance_report(
    quarter: str,
    portfolio_value_krw: float = 100_000_000.0,
    output_path: str | Path | None = None,
) -> Path:
    """Generate a paper rebalance report template for P08_IEF30."""

    as_of = quarter_end_proxy(quarter)
    component_nav = load_component_nav(as_of)
    component_nav = component_nav.loc[component_nav.index >= quarter_start_proxy(quarter)]
    current_weights = drifted_weights(component_nav, TARGET)
    rows = []
    for ticker, target_weight in TARGET.items():
        current_weight = current_weights[ticker]
        trade_krw = (target_weight - current_weight) * portfolio_value_krw
        rows.append(
            {
                "ticker": ticker,
                "current_weight": current_weight,
                "target_weight": target_weight,
                "drift_pp": (current_weight - target_weight) * 100.0,
                "action": "BUY" if trade_krw > 0 else "SELL" if trade_krw < 0 else "HOLD",
                "trade_amount_krw": trade_krw,
            }
        )

    table = pd.DataFrame(rows)
    lines = [
        f"# {quarter} P08_IEF30 rebalance report",
        "",
        "- Status: paper operations tooling; no live order authorization.",
        "- Target weights: SPY 29 / QQQ 21 / H001 20 / IEF 30.",
        "- Tax assumption: HIFO lot selection, KRW 2.5M annual exemption, 22% overseas ETF capital gains tax.",
        "- Tax professional confirmation is required before any live implementation.",
        "",
        "## Current vs target weights",
        "",
        format_markdown_table(table),
        "",
        "## Trade list",
        "",
        "- BUY/SELL amounts are paper KRW notional estimates from current drift.",
        "- Quantity must be filled by the execution layer using broker quotes and FX conversion at trade time.",
        "- Expected realized gains: pending lot-level broker export.",
        "- Expected tax: apply HIFO lot selection and remaining KRW 2.5M annual exemption before live use.",
        "- Expected FX conversion: KRW to USD for SPY, QQQ, IEF legs; H001 remains KRW-denominated.",
        "",
        "## HIFO lot selection suggestion",
        "",
        "- For SPY, QQQ, and IEF sells, select highest-cost KRW tax-basis lots first.",
        "- Do not apply overseas ETF capital gains tax to H001 under the current Korean non-large-shareholder assumption.",
        "- Confirm broker lot accounting, FX tax basis, and reporting treatment with a tax professional before live trading.",
    ]
    path = Path(output_path) if output_path else OUTPUT_DIR / f"rebalance_report_{quarter}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def quarter_end_proxy(quarter: str) -> pd.Timestamp:
    year, q = quarter.split("-Q")
    month = int(q) * 3
    return pd.Timestamp(year=int(year), month=month, day=1) + pd.offsets.MonthEnd(0)


def quarter_start_proxy(quarter: str) -> pd.Timestamp:
    year, q = quarter.split("-Q")
    month = (int(q) - 1) * 3 + 1
    return pd.Timestamp(year=int(year), month=month, day=1)


def drifted_weights(component_nav: pd.DataFrame, target: dict[str, float]) -> dict[str, float]:
    first = component_nav.iloc[0]
    latest = component_nav.iloc[-1]
    values = {ticker: weight * latest[ticker] / first[ticker] for ticker, weight in target.items()}
    total = sum(values.values())
    return {ticker: value / total for ticker, value in values.items()}


def format_markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_rebalance_report("2026-Q2").relative_to(ROOT))
