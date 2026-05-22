from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.s001_common import PRIMARY_SIGNALS, ensure_dir, markdown_table, read_s000_trades, summary_metrics, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_e_tax_model")


SCENARIOS = {
    "conservative_s000_gain_tax_22pct": {"gain_tax": 0.22, "sell_tax": 0.0, "commission": 0.0025, "slippage": 0.0005},
    "ordinary_domestic_listed_small_shareholder": {"gain_tax": 0.0, "sell_tax": 0.0018, "commission": 0.00015, "slippage": 0.0005},
    "large_shareholder_special_case": {"gain_tax": 0.22, "sell_tax": 0.0018, "commission": 0.00015, "slippage": 0.0005},
}


def apply_tax(gross: pd.Series, scenario: dict[str, float]) -> pd.Series:
    two_way = 2.0 * (scenario["commission"] + scenario["slippage"])
    return gross - two_way - scenario["sell_tax"] - gross.clip(lower=0.0) * scenario["gain_tax"]


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    target = trades.loc[trades["signal"].isin(PRIMARY_SIGNALS)].copy()
    rows = []
    for name, scenario in SCENARIOS.items():
        net = apply_tax(target["gross_return"], scenario)
        rows.append({"scenario": name, **scenario, **summary_metrics(net, target["holding_days"].mean())})
    summary = pd.DataFrame(rows)
    summary.to_csv(out / "tax_model_summary.csv", index=False)
    pass_flag = bool((summary["mean"] > 0).all())
    write_json(out / "metrics.json", {"verdict": "PASS" if pass_flag else "FAIL", "scenarios": summary.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-E Tax Model",
        [
            ("Verdict", "PASS" if pass_flag else "FAIL"),
            ("Scenarios", markdown_table(summary)),
            ("Policy", "This script tests tax arithmetic only. It does not decide legal treatment for a real account."),
        ],
    )


if __name__ == "__main__":
    main()
