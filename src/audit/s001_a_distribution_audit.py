from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.audit.s001_common import PRIMARY_SIGNALS, ensure_dir, markdown_table, read_s000_trades, summary_metrics, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_a_distribution_audit")


def bootstrap_mean(data: pd.DataFrame, group_col: str | None, seed: int = 20260520, n: int = 1000) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    if data.empty:
        return {"mean": 0.0, "ci_p05": 0.0, "ci_p50": 0.0, "ci_p95": 0.0}
    if group_col is None:
        values = data["net_return"].to_numpy()
        samples = [rng.choice(values, size=len(values), replace=True).mean() for _ in range(n)]
    else:
        groups = [g["net_return"].to_numpy() for _, g in data.groupby(group_col)]
        samples = []
        for _ in range(n):
            chosen = rng.choice(len(groups), size=len(groups), replace=True)
            samples.append(np.concatenate([groups[i] for i in chosen]).mean())
    arr = np.asarray(samples)
    return {"mean": float(data["net_return"].mean()), "ci_p05": float(np.quantile(arr, 0.05)), "ci_p50": float(np.quantile(arr, 0.50)), "ci_p95": float(np.quantile(arr, 0.95))}


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    target = trades.loc[trades["signal"].isin(PRIMARY_SIGNALS)].copy()
    target["year"] = target["signal_date"].dt.year

    quantile_rows = []
    for signal, group in target.groupby("signal"):
        q = group["net_return"].quantile([0.01, 0.05, 0.25, 0.75, 0.95, 0.99])
        quantile_rows.append(
            {
                "signal": signal,
                "count": len(group),
                "mean": group["net_return"].mean(),
                "median": group["net_return"].median(),
                "p1": q.loc[0.01],
                "p5": q.loc[0.05],
                "p25": q.loc[0.25],
                "p75": q.loc[0.75],
                "p95": q.loc[0.95],
                "p99": q.loc[0.99],
                "min": group["net_return"].min(),
                "max": group["net_return"].max(),
            }
        )
    distribution = pd.DataFrame(quantile_rows)

    total_net = target["net_return"].sum()
    top_trade_rows = []
    for n in [10, 20]:
        top = target.nlargest(n, "net_return")
        top_trade_rows.append({"cut": f"top_{n}_trades", "count": len(top), "net_sum": top["net_return"].sum(), "share_of_total_net_sum": top["net_return"].sum() / total_net if total_net else 0.0})
    date_contrib = target.groupby("signal_date")["net_return"].sum().sort_values(ascending=False)
    for n in [5, 10]:
        top = date_contrib.head(n)
        top_trade_rows.append({"cut": f"top_{n}_dates", "count": len(top), "net_sum": top.sum(), "share_of_total_net_sum": top.sum() / total_net if total_net else 0.0})
    concentration = pd.DataFrame(top_trade_rows)

    exclusion_rows = []
    for label, frame in [
        ("exclude_2020", target.loc[target["year"].ne(2020)]),
        ("exclude_2018_2020", target.loc[~target["year"].between(2018, 2020)]),
        ("exclude_top_1pct_trades", target.loc[target["net_return"] < target["net_return"].quantile(0.99)]),
        ("exclude_top_5pct_trades", target.loc[target["net_return"] < target["net_return"].quantile(0.95)]),
    ]:
        exclusion_rows.append({"scenario": label, **summary_metrics(frame["net_return"], frame["holding_days"].mean() if not frame.empty else 1)})
    exclusions = pd.DataFrame(exclusion_rows)

    boot_rows = []
    for label, group_col in [("trade_level", None), ("date_cluster", "signal_date"), ("stock_cluster", "ticker")]:
        boot_rows.append({"bootstrap": label, **bootstrap_mean(target, group_col)})
    boot = pd.DataFrame(boot_rows)

    distribution.to_csv(out / "return_distribution.csv", index=False)
    concentration.to_csv(out / "top_contributors.csv", index=False)
    exclusions.to_csv(out / "crisis_exclusion.csv", index=False)
    boot.to_csv(out / "bootstrap_ci.csv", index=False)

    pass_flag = bool((exclusions["mean"] > 0).all())
    write_json(out / "metrics.json", {"verdict": "PASS" if pass_flag else "FAIL", "pass_rule": "top trades/dates and crisis exclusions keep r1d_lt_m3 net positive", "exclusions": exclusions.to_dict("records"), "bootstrap": boot.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-A Distribution / Attribution Audit",
        [
            ("Verdict", "PASS" if pass_flag else "FAIL"),
            ("Distribution", markdown_table(distribution)),
            ("Concentration", markdown_table(concentration)),
            ("Exclusions", markdown_table(exclusions)),
            ("Bootstrap CI", markdown_table(boot)),
        ],
    )


if __name__ == "__main__":
    main()
