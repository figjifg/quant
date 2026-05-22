from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.s001_common import PRIMARY_SIGNALS, ensure_dir, markdown_table, read_panel, read_s000_trades, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_c_execution_capacity")
CAPITALS = [100_000_000, 1_000_000_000, 3_000_000_000, 10_000_000_000]
SLIPPAGE_BPS = [0, 10, 30, 50, 100]
PARTICIPATION_LIMITS = [0.01, 0.03, 0.05]


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    panel = read_panel(filtered=False)
    adv = panel.sort_values(["종목코드", "날짜"]).copy()
    adv["adv20"] = adv.groupby("종목코드")["거래대금추정"].transform(lambda x: x.rolling(20, min_periods=5).mean())
    adv_lookup = adv.rename(columns={"종목코드": "ticker", "날짜": "execution_date"})[["ticker", "execution_date", "adv20"]]
    target = trades.loc[trades["signal"].isin(PRIMARY_SIGNALS)].merge(adv_lookup, on=["ticker", "execution_date"], how="left")
    daily_counts = target.groupby("execution_date").size().rename("new_signals")
    target = target.merge(daily_counts, on="execution_date", how="left")
    target["base_weight"] = 1.0 / target["new_signals"].clip(lower=1)

    rows = []
    for capital in CAPITALS:
        for slip_bps in SLIPPAGE_BPS:
            for participation in PARTICIPATION_LIMITS:
                notional = capital * target["base_weight"]
                participation_rate = notional / target["adv20"]
                capacity_ok = participation_rate.le(participation).fillna(False)
                stressed_return = target["net_return"] - 2.0 * slip_bps / 10000.0
                fill50 = stressed_return * 0.50
                fill30 = stressed_return * 0.30
                rows.append(
                    {
                        "capital_krw": capital,
                        "entry_exit_extra_slippage_bps": slip_bps,
                        "participation_limit": participation,
                        "mean_net_baseline_fill": stressed_return.mean(),
                        "mean_net_50pct_fill_vwap": fill50.mean(),
                        "mean_net_30pct_fill_vwap": fill30.mean(),
                        "capacity_pass_rate": capacity_ok.mean(),
                        "max_participation_rate": participation_rate.replace([float("inf")], pd.NA).max(),
                        "panic_day_spread_widening_bps": slip_bps * 2,
                        "max_daily_signal_count": int(daily_counts.max()),
                    }
                )
    stress = pd.DataFrame(rows)
    stress.to_csv(out / "execution_capacity_stress.csv", index=False)
    possible_1b_10b = stress.loc[stress["capital_krw"].isin([100_000_000, 1_000_000_000]) & stress["mean_net_baseline_fill"].gt(0) & stress["capacity_pass_rate"].ge(0.95)]
    possible_30b_100b = stress.loc[stress["capital_krw"].isin([3_000_000_000, 10_000_000_000]) & stress["mean_net_baseline_fill"].gt(0) & stress["capacity_pass_rate"].ge(0.95)]
    if not possible_1b_10b.empty and possible_30b_100b.empty:
        verdict = "small-capacity tactical sleeve"
    elif not possible_30b_100b.empty:
        verdict = "scalable"
    else:
        verdict = "capacity-limited"
    write_json(out / "metrics.json", {"verdict": verdict, "stress_rows": stress.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-C Execution / Capacity Stress",
        [
            ("Verdict", verdict),
            ("Stress Summary", markdown_table(stress.head(60))),
            ("Assumptions", "Baseline T+1 open mid; extra slippage is applied symmetrically to entry and exit. Limit-down/suspension skip requires exchange status data not present in S000 artifacts, so this row remains WARN until source data exists."),
        ],
    )


if __name__ == "__main__":
    main()
