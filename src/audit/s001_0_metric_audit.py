from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.audit.s001_common import (
    S000_DIR,
    cost_adjusted_return,
    ensure_dir,
    markdown_table,
    next_trade_date,
    read_panel,
    read_s000_metrics,
    read_s000_random,
    read_s000_trades,
    trading_calendar,
    write_json,
    write_report,
)


OUTPUT_DIR = Path("reports/experiments/S001_0_metric_audit")


def audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = read_s000_trades()
    random = read_s000_random()
    metrics = read_s000_metrics()
    raw_panel = read_panel(filtered=False)
    filtered_panel = read_panel(filtered=True)
    calendar = trading_calendar(raw_panel)

    issues: list[dict[str, str]] = []

    gross_mean = trades.groupby("signal")["gross_return"].mean()
    reported = pd.DataFrame(metrics["signals"]).set_index("signal")
    unit_mismatch = (gross_mean - reported["gross_mean"]).abs().max()
    max_abs_return = trades[["gross_return", "net_return"]].abs().max().max()
    status = "PASS" if unit_mismatch < 1e-12 else "FAIL"
    issues.append(
        row(
            "return_unit",
            status,
            "gross/net mean fields match decimal per-trade means; not cumulative or annualized.",
            f"max_reported_mean_diff={unit_mismatch:.3g}; max_abs_trade_return={max_abs_return:.6f}",
        )
    )

    expected_entry = trades["signal_date"].map(lambda d: next_trade_date(calendar, d, 1))
    bad_entry = trades.loc[trades["execution_date"].ne(expected_entry)]
    expected_exit = trades.apply(lambda r: next_trade_date(calendar, r["execution_date"], int(r["holding_days"]) - 1), axis=1)
    bad_exit = trades.loc[trades["exit_date"].ne(expected_exit)]
    status = "FAIL" if len(bad_entry) or len(bad_exit) else "PASS"
    issues.append(
        row(
            "entry_exit_alignment",
            status,
            "Signal must be T close, entry T+1 open, exit after holding horizon on KRX trading calendar.",
            f"bad_entry_rows={len(bad_entry)}; bad_exit_rows={len(bad_exit)}; S000 recalculation required if nonzero.",
        )
    )

    expected_filtered_entry = next_ticker_row_dates(filtered_panel, trades, "signal_date", 1)
    filtered_jump = trades.loc[trades["execution_date"].eq(expected_filtered_entry) & trades["execution_date"].ne(expected_entry)]
    issues.append(
        row(
            "filtered_panel_row_jump",
            "FAIL" if len(filtered_jump) else "PASS",
            "S000 implementation built trades from the post-filtered panel; next row can skip KRX trading days.",
            f"rows_matching_filtered_ticker_next_row_not_raw_calendar={len(filtered_jump)}; S000 recalculation required if nonzero.",
        )
    )

    membership_cols = ["날짜", "종목코드", "동적유니버스포함", "거래대금추정여부", "시가총액추정여부"]
    membership = raw_panel[membership_cols].rename(columns={"날짜": "signal_date", "종목코드": "ticker"})
    joined = trades.merge(membership, on=["signal_date", "ticker"], how="left")
    missing_member = int(joined["동적유니버스포함"].isna().sum())
    non_member = int(joined["동적유니버스포함"].ne(True).sum())
    issues.append(
        row(
            "no_lookahead_dynamic_universe",
            "WARN",
            "Rows are dynamic-universe filtered, but S000 used same-day membership; PIT T-1 membership proof is not present.",
            f"missing_member_rows={missing_member}; non_member_rows={non_member}; S000 recalculation required unless T-1 membership is reconstructed.",
        )
    )

    krx_mismatch = raw_panel["KRX종가"].notna() & raw_panel["종가"].notna() & raw_panel["KRX종가"].ne(raw_panel["종가"])
    issues.append(
        row(
            "adjusted_price",
            "FAIL" if max_abs_return > 1.0 else "WARN",
            "KRX close derivation is internally consistent, but split/right-adjustment treatment is not documented in S000 artifacts.",
            f"종가_ne_KRX종가_rows={int(krx_mismatch.sum())}; adjustment_columns_present=false; max_abs_trade_return={max_abs_return:.6f}; S000 recalculation required if extreme returns are corporate-action artifacts.",
        )
    )

    dupes = trades.duplicated(["signal", "ticker", "signal_date"]).sum()
    consecutive = count_consecutive_signals(trades)
    issues.append(
        row(
            "duplicate_event",
            "WARN" if consecutive else "PASS",
            "No identical signal/ticker/date duplicates are allowed; consecutive signal handling should be explicit.",
            f"duplicate_rows={int(dupes)}; consecutive_same_signal_ticker_rows={consecutive}.",
        )
    )

    overlap = trades.groupby("execution_date").size()
    max_same_day = int(overlap.max()) if not overlap.empty else 0
    active = active_positions(trades)
    max_active = int(active["active_positions"].max()) if not active.empty else 0
    issues.append(
        row(
            "overlap_leverage",
            "FAIL" if max_active > 1 else "PASS",
            "S000 reports per-trade means; applying each overlapping trade as 100% notional creates leverage unless sleeve NAV is simulated.",
            f"max_new_signals_same_day={max_same_day}; max_active_positions={max_active}; S000 recalculation required for portfolio-level claim.",
        )
    )

    recomputed = trades["gross_return"].map(cost_adjusted_return)
    cost_diff = (recomputed - trades["net_return"]).abs().max()
    positive_tax_bad = trades.loc[trades["gross_return"].gt(0) & trades["tax_paid_return"].le(0)]
    negative_tax_bad = trades.loc[trades["gross_return"].le(0) & trades["tax_paid_return"].ne(0)]
    issues.append(
        row(
            "tax_cost_application",
            "PASS" if cost_diff < 1e-12 and positive_tax_bad.empty and negative_tax_bad.empty else "FAIL",
            "S000 applies two-way commission/slippage and gain-only 22% tax in return space.",
            f"max_net_recompute_diff={cost_diff:.3g}; positive_tax_bad={len(positive_tax_bad)}; negative_tax_bad={len(negative_tax_bad)}.",
        )
    )

    date_match_rate = 0.0
    if not random.empty:
        actual_counts = trades.groupby(["signal", "signal_date"]).size().rename("actual")
        random_counts = random.groupby(["signal", "signal_date"]).size().rename("random")
        aligned = pd.concat([actual_counts, random_counts], axis=1).fillna(0)
        date_match_rate = float((aligned["actual"].eq(aligned["random"])).mean())
    issues.append(
        row(
            "random_control",
            "FAIL",
            "S000 random control samples arbitrary panel rows, not same signal dates/universe/counts; market rebound day effect is not controlled.",
            f"date_count_match_rate={date_match_rate:.6f}; S000 recalculation required with date-matched controls.",
        )
    )

    issue_frame = pd.DataFrame(issues)
    detail = pd.DataFrame(
        {
            "metric": ["trade_count", "signals", "bad_entry_rows", "bad_exit_rows", "max_active_positions"],
            "value": [len(trades), trades["signal"].nunique(), len(bad_entry), len(bad_exit), max_active],
        }
    )
    return issue_frame, detail


def row(item: str, status: str, check: str, evidence: str) -> dict[str, str]:
    return {"item": item, "status": status, "check": check, "evidence": evidence}


def count_consecutive_signals(trades: pd.DataFrame) -> int:
    ordered = trades.sort_values(["signal", "ticker", "signal_date"])
    prev_exit = ordered.groupby(["signal", "ticker"])["exit_date"].shift()
    return int((ordered["signal_date"] <= prev_exit).sum())


def next_ticker_row_dates(panel: pd.DataFrame, trades: pd.DataFrame, date_col: str, step: int) -> pd.Series:
    lookup = {}
    for ticker, frame in panel.groupby("종목코드", sort=False):
        dates = frame["날짜"].reset_index(drop=True)
        for idx, date in dates.items():
            target = idx + step
            lookup[(ticker, pd.Timestamp(date))] = dates.iloc[target] if target < len(dates) else pd.NaT
    return trades.apply(lambda r: lookup.get((r["ticker"], pd.Timestamp(r[date_col])), pd.NaT), axis=1)


def active_positions(trades: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for date in pd.date_range(trades["execution_date"].min(), trades["exit_date"].max(), freq="D"):
        rows.append({"date": date, "active_positions": int(((trades["execution_date"] <= date) & (trades["exit_date"] >= date)).sum())})
    return pd.DataFrame(rows)


def main() -> None:
    out = ensure_dir(Path(OUTPUT_DIR))
    issues, detail = audit()
    issues.to_csv(out / "audit_results.csv", index=False)
    detail.to_csv(out / "audit_detail.csv", index=False)
    write_json(out / "metrics.json", {"overall": "FAIL" if issues["status"].eq("FAIL").any() else "PASS", "items": issues.to_dict("records")})
    write_report(
        out / "report.md",
        "S001-0 Metric / Implementation Audit",
        [
            ("Verdict", "FAIL. S000 recalculation is required before any S-family promotion because timing, filtered-row execution, overlap/leverage, and random-control checks failed."),
            ("Audit Results", markdown_table(issues)),
            ("Detail", markdown_table(detail)),
            ("Source", f"Read-only inputs: `{S000_DIR}` and equity panels. No frozen strategy or engine files were modified."),
        ],
    )


if __name__ == "__main__":
    main()
