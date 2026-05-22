from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.s001_common import CRISIS_SIGNAL, PRIMARY_SIGNALS, ensure_dir, markdown_table, nav_metrics, read_s000_random, read_s000_trades, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_b_real_sleeve_simulation")


VARIANTS = {
    "r1d_lt_m3_hold1": ["r1d_lt_m3_hold1"],
    "r1d_lt_m3_hold3": ["r1d_lt_m3_hold3"],
    "r1d_lt_m3_hold5": ["r1d_lt_m3_hold5"],
    "r3d_lt_m7_hold3_crisis_only": [CRISIS_SIGNAL],
}


def simulate(trades: pd.DataFrame, signal_names: list[str], sleeve_size: float, max_position: float, max_new_per_day: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = trades.loc[trades["signal"].isin(signal_names)].sort_values(["execution_date", "signal_value"], ascending=[True, False]).copy()
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame()
    dates = pd.date_range(selected["execution_date"].min(), selected["exit_date"].max(), freq="D")
    active: list[dict] = []
    cash = sleeve_size
    nav = sleeve_size
    daily_rows = []
    trade_rows = []
    by_entry = {date: g for date, g in selected.groupby("execution_date")}
    for date in dates:
        new_active = []
        for pos in active:
            if pos["exit_date"] <= date:
                pnl = pos["weight"] * pos["net_return"]
                cash += pos["weight"] * (1.0 + pos["net_return"])
                trade_rows.append({**pos, "realized_pnl": pnl})
            else:
                new_active.append(pos)
        active = new_active
        available = max(sleeve_size - sum(p["weight"] for p in active), 0.0)
        entries = by_entry.get(pd.Timestamp(date), pd.DataFrame()).head(max_new_per_day)
        if not entries.empty and available > 0:
            weight = min(max_position, available / len(entries))
            for row in entries.itertuples(index=False):
                if cash < weight or weight <= 0:
                    continue
                cash -= weight
                active.append({"signal": row.signal, "ticker": row.ticker, "entry_date": row.execution_date, "exit_date": row.exit_date, "weight": weight, "net_return": row.net_return})
        exposure = sum(p["weight"] for p in active)
        nav = cash + exposure
        daily_rows.append({"date": date, "nav": nav, "cash": cash, "n_positions": len(active), "exposure": exposure, "cash_drag": max(sleeve_size - exposure, 0.0)})
    return pd.DataFrame(daily_rows), pd.DataFrame(trade_rows)


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    random = read_s000_random()
    rows = []
    curves = []
    for source, frame in [("candidate", trades), ("random_control", random)]:
        if frame.empty:
            continue
        for variant, signal_names in VARIANTS.items():
            for sleeve in [1.0, 0.05, 0.10]:
                for max_position in [0.01, 0.02]:
                    daily, realized = simulate(frame, signal_names, sleeve, max_position, 5)
                    if daily.empty:
                        continue
                    metrics = nav_metrics(daily)
                    metrics.update(
                        {
                            "source": source,
                            "variant": variant,
                            "sleeve_size": sleeve,
                            "max_position": max_position,
                            "max_new_per_day": 5,
                            "turnover_proxy": float(realized["weight"].sum()) if not realized.empty else 0.0,
                            "hit_rate": float((realized["net_return"] > 0).mean()) if not realized.empty else 0.0,
                            "average_exposure": float(daily["exposure"].mean() / sleeve),
                            "average_cash": float(daily["cash"].mean() / sleeve),
                        }
                    )
                    rows.append(metrics)
                    curves.append(daily.assign(source=source, variant=variant, sleeve_size=sleeve, max_position=max_position))
    summary = pd.DataFrame(rows)
    equity = pd.concat(curves, ignore_index=True) if curves else pd.DataFrame()
    summary.to_csv(out / "sleeve_metrics.csv", index=False)
    equity.to_csv(out / "daily_nav.csv", index=False)
    pass_rows = summary.loc[(summary["source"].eq("candidate")) & (summary["variant"].eq("r1d_lt_m3_hold1")) & (summary["total_return"] > 0)]
    random_rows = summary.loc[(summary["source"].eq("random_control")) & (summary["variant"].eq("r1d_lt_m3_hold1"))]
    pass_flag = not pass_rows.empty and (pass_rows["total_return"].max() > random_rows["total_return"].max() if not random_rows.empty else True)
    write_json(out / "metrics.json", {"verdict": "PASS" if pass_flag else "FAIL", "summary": summary.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-B Real Sleeve Daily NAV Simulation",
        [
            ("Verdict", "PASS" if pass_flag else "FAIL"),
            ("Metrics", markdown_table(summary.head(40))),
            ("Rule", "No leverage: exposure is capped at sleeve NAV; excess signals are limited by 5 new names/day and max 1%/2% position caps. Cash remains idle."),
        ],
    )


if __name__ == "__main__":
    main()
