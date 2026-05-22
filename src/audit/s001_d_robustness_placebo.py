from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.audit.s001_common import cost_adjusted_return, ensure_dir, markdown_table, read_panel, read_s000_trades, summary_metrics, write_json, write_report


OUTPUT_DIR = Path("reports/experiments/S001_d_robustness_placebo")


def build_grid(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    data = panel.loc[panel["동적유니버스포함"].eq(True) & panel["거래대금추정여부"].eq(False)].sort_values(["종목코드", "날짜"]).copy()
    group = data.groupby("종목코드", sort=False)
    data["ret_1d"] = group["KRX종가"].pct_change(1)
    data["ret_3d"] = group["KRX종가"].pct_change(3)
    for threshold in [-0.02, -0.03, -0.04, -0.05]:
        for hold in [1, 2, 3, 5, 10]:
            events = data.loc[data["ret_1d"].lt(threshold)].copy()
            rows.append(calc_event_return(data, events, f"r1d_lt_{abs(threshold):.0%}_hold{hold}", hold))
    for threshold in [-0.05, -0.07, -0.10]:
        for hold in [1, 2, 3, 5, 10]:
            events = data.loc[data["ret_3d"].lt(threshold)].copy()
            rows.append(calc_event_return(data, events, f"r3d_lt_{abs(threshold):.0%}_hold{hold}", hold))
    return pd.DataFrame(rows)


def calc_event_return(data: pd.DataFrame, events: pd.DataFrame, label: str, hold: int) -> dict:
    returns = []
    by_ticker = {ticker: frame.reset_index(drop=True) for ticker, frame in data.groupby("종목코드", sort=False)}
    for event in events.head(2000).itertuples(index=False):
        frame = by_ticker[event.종목코드]
        loc = frame.index[frame["날짜"].eq(event.날짜)]
        if len(loc) == 0:
            continue
        entry_pos = int(loc[0]) + 1
        exit_pos = entry_pos + hold - 1
        if exit_pos >= len(frame):
            continue
        gross = frame.iloc[exit_pos]["KRX종가"] / frame.iloc[entry_pos]["시가"] - 1.0
        returns.append(cost_adjusted_return(gross))
    metrics = summary_metrics(pd.Series(returns), hold)
    return {"variant": label, "hold_days": hold, **metrics}


def placebo(trades: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(20260520)
    target = trades.loc[trades["signal"].eq("r1d_lt_m3_hold1")].copy()
    rows = []
    rows.append({"placebo": "date_matched_random_existing_s000_proxy", **summary_metrics(target.sample(frac=1.0, random_state=1)["net_return"], 1)})
    rows.append({"placebo": "drop_matched_random_bucket_proxy", **summary_metrics(target.assign(bucket=pd.qcut(target["signal_value"], 5, duplicates="drop")).groupby("bucket", observed=False)["net_return"].sample(frac=1.0, random_state=2), 1)})
    stock_sample = target.groupby("ticker", group_keys=False).apply(lambda g: g.sample(n=len(g), replace=True, random_state=int(rng.integers(1, 1_000_000))))
    rows.append({"placebo": "stock_matched_random_date_proxy", **summary_metrics(stock_sample["net_return"], 1)})
    rows.append({"placebo": "time_shift_plus_5d_proxy", **summary_metrics(target["net_return"].shift(5).dropna(), 1)})
    rows.append({"placebo": "time_shift_minus_5d_proxy", **summary_metrics(target["net_return"].shift(-5).dropna(), 1)})
    rows.append({"placebo": "opposite_signal_proxy", **summary_metrics(-target["net_return"], 1)})
    return pd.DataFrame(rows)


def main() -> None:
    out = ensure_dir(OUTPUT_DIR)
    trades = read_s000_trades()
    panel = read_panel(filtered=False)
    grid = build_grid(panel)
    placebos = placebo(trades)
    plateau = grid.loc[grid["variant"].str.startswith("r1d") & grid["mean"].gt(0)]
    grid.to_csv(out / "threshold_holding_grid.csv", index=False)
    placebos.to_csv(out / "placebo_controls.csv", index=False)
    pass_flag = len(plateau) >= 4 and placebos["mean"].max() < trades.loc[trades["signal"].eq("r1d_lt_m3_hold1"), "net_return"].mean()
    write_json(out / "metrics.json", {"verdict": "PASS" if pass_flag else "FAIL", "positive_r1d_grid_points": int(len(plateau))})
    write_report(
        out / "report.md",
        "S001-D Robustness / Placebo",
        [
            ("Verdict", "PASS" if pass_flag else "FAIL"),
            ("Threshold / Holding Grid", markdown_table(grid.head(80))),
            ("Placebo Controls", markdown_table(placebos)),
            ("Note", "Placebo rows are artifact-level proxies unless rebuilt from a corrected S000 engine; S001-0 failure takes precedence."),
        ],
    )


if __name__ == "__main__":
    main()
