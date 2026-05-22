from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.s001_common import KOSPI_PROXY_PATH, MARKET_FLOW_PATH, PRIMARY_SIGNALS, add_panel_features, ensure_dir, markdown_table, read_panel, read_s000_trades, summary_metrics, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_f_mechanism")


def bucket_metrics(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for value, group in frame.groupby(group_col, dropna=False, observed=False):
        rows.append({"bucket": group_col, "value": str(value), **summary_metrics(group["net_return"], group["holding_days"].mean() if not group.empty else 1)})
    return pd.DataFrame(rows)


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    target = trades.loc[trades["signal"].isin(PRIMARY_SIGNALS)].copy()
    panel = add_panel_features(read_panel(filtered=False))
    features = panel.rename(columns={"종목코드": "ticker", "날짜": "signal_date"})[
        [
            "ticker",
            "signal_date",
            "ret_1d",
            "ret_3d",
            "gap_open",
            "intraday_return",
            "volatility_20d",
            "mcap_bucket",
            "기관순매수금액추정",
            "외국인순매수금액추정",
        ]
    ]
    merged = target.merge(features, on=["ticker", "signal_date"], how="left")
    kospi = pd.read_csv(KOSPI_PROXY_PATH, encoding="utf-8-sig", parse_dates=["date"])
    merged = merged.merge(kospi[["date", "cap_weighted_return"]].rename(columns={"date": "signal_date"}), on="signal_date", how="left")
    if MARKET_FLOW_PATH.exists():
        flow = pd.read_csv(MARKET_FLOW_PATH, encoding="utf-8-sig")
        date_col = "날짜" if "날짜" in flow.columns else "date"
        flow[date_col] = pd.to_datetime(flow[date_col])
        flow_cols = [c for c in flow.columns if "foreign" in c or "institution" in c or "외국인" in c or "기관" in c]
        keep = [date_col] + flow_cols[:4]
        flow = flow[keep].rename(columns={date_col: "signal_date"})
        merged = merged.merge(flow, on="signal_date", how="left")

    merged["d013_state"] = "unknown_not_in_s000_artifact"
    merged["kospi_day"] = merged["cap_weighted_return"].map(lambda x: "down" if pd.notna(x) and x < 0 else "up_or_flat")
    merged["drop_type"] = merged.apply(lambda r: "market_drop" if pd.notna(r["cap_weighted_return"]) and r["cap_weighted_return"] < -0.02 else "stock_specific", axis=1)
    merged["foreign_flow"] = merged["외국인순매수금액추정"].map(lambda x: "foreign_net_sell" if pd.notna(x) and x < 0 else "foreign_not_sell")
    merged["institution_flow"] = merged["기관순매수금액추정"].map(lambda x: "institution_net_sell" if pd.notna(x) and x < 0 else "institution_not_sell")
    merged["gap_bucket"] = pd.cut(merged["gap_open"], bins=[-10, -0.03, 0.0, 10], labels=["gapdown_gt3pct", "gapdown_0_3pct", "flat_or_gapup"])
    merged["intraday_bucket"] = merged["intraday_return"].map(lambda x: "intraday_rebound" if pd.notna(x) and x > 0 else "intraday_weak")
    merged["vol_regime"] = pd.qcut(merged["volatility_20d"], 3, labels=["low_vol", "mid_vol", "high_vol"], duplicates="drop")

    parts = []
    for col in ["d013_state", "kospi_day", "drop_type", "foreign_flow", "institution_flow", "mcap_bucket", "gap_bucket", "intraday_bucket", "vol_regime"]:
        parts.append(bucket_metrics(merged, col))
    attribution = pd.concat(parts, ignore_index=True)
    attribution.to_csv(out / "mechanism_breakdown.csv", index=False)
    merged.to_csv(out / "trade_mechanism_features.csv", index=False)
    hypotheses = pd.DataFrame(
        [
            {"hypothesis": "forced_selling_liquidity_rebound", "support": "diagnostic", "evidence": "compare foreign/institution net-sell buckets and intraday rebound buckets"},
            {"hypothesis": "large_cap_panic_overshoot", "support": "diagnostic", "evidence": "compare mcap buckets and market-drop buckets"},
            {"hypothesis": "individual_stock_microstructure_bounce", "support": "diagnostic", "evidence": "compare stock_specific and gap/intraday buckets"},
            {"hypothesis": "index_program_flow_reversal", "support": "unproven", "evidence": "requires explicit program/index flow data not in S000 artifacts"},
        ]
    )
    hypotheses.to_csv(out / "mechanism_hypotheses.csv", index=False)
    write_json(out / "metrics.json", {"verdict": "DIAGNOSTIC_ONLY", "breakdown": attribution.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-F Mechanism Analysis",
        [
            ("Verdict", "DIAGNOSTIC_ONLY"),
            ("Breakdown", markdown_table(attribution.head(80))),
            ("Hypotheses", markdown_table(hypotheses)),
            ("Limitations", "D013 ON/OFF and sector classifications are not present in S000 artifacts. Sector split remains pending unless a PIT sector map is supplied."),
        ],
    )


if __name__ == "__main__":
    main()
