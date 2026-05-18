from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
OUTPUT_DIR = Path("reports/experiments/H000_off_regime_diagnostics")
MACRO_DIR = Path("research_input_data/inputs/macro_features")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quarterly = build_quarterly_dataset()
    off_stats = build_off_stats(quarterly)
    returns = build_return_distribution(quarterly)
    crash_rally = build_missed_rally_avoided_crash(quarterly)
    sleeve = build_sleeve_candidate_returns(quarterly)
    inverse = build_inverse_diagnostic(quarterly)

    off_stats.to_csv(OUTPUT_DIR / "A_off_regime_stats.csv", index=False)
    returns.to_csv(OUTPUT_DIR / "B_return_distribution.csv", index=False)
    crash_rally.to_csv(OUTPUT_DIR / "C_missed_rally_avoided_crash.csv", index=False)
    sleeve.to_csv(OUTPUT_DIR / "D_sleeve_candidate_returns.csv", index=False)
    inverse.to_csv(OUTPUT_DIR / "E_kospi_inverse_diagnostic.csv", index=False)
    write_report(off_stats, returns, crash_rally, sleeve, inverse)


def build_quarterly_dataset() -> pd.DataFrame:
    regime = pd.read_csv(D013_DIR / "quarterly_regime_log.csv", parse_dates=["signal_date"])
    regime = regime[["signal_date", "regime_on"]].copy()
    regime["quarter"] = regime["signal_date"].dt.to_period("Q").astype(str)
    regime["regime"] = regime["regime_on"].map({True: "ON", False: "OFF"})

    kospi = pd.read_csv(MACRO_DIR / "krx_market_breadth_kospi_2010_2026.csv", parse_dates=["date"])
    kospi["quarter"] = kospi["date"].dt.to_period("Q").astype(str)
    kospi_q = (
        kospi.groupby("quarter", sort=True)["cap_weighted_return"]
        .apply(lambda returns: (1.0 + returns).prod() - 1.0)
        .rename("kospi_quarter_return")
        .reset_index()
    )

    dates = regime[["signal_date", "quarter"]].copy()
    usdk_rw = load_daily_end_series(MACRO_DIR / "fred_dexkous_usdkrw.csv", "DEXKOUS", dates, "usdk_rw")
    dgs10 = load_daily_end_series(MACRO_DIR / "fred_dgs10.csv", "DGS10", dates, "us10y")
    kr_short = load_monthly_kr_short_carry(MACRO_DIR / "fred_kr_short_rate.csv", dates)

    quarterly = (
        regime.merge(kospi_q, on="quarter", how="left")
        .merge(usdk_rw, on=["signal_date", "quarter"], how="left")
        .merge(dgs10, on=["signal_date", "quarter"], how="left")
        .merge(kr_short, on=["signal_date", "quarter"], how="left")
        .sort_values("signal_date")
        .reset_index(drop=True)
    )
    quarterly["usdk_rw_quarter_change"] = quarterly["usdk_rw"].pct_change()
    quarterly["usdk_rw_yoy"] = quarterly["usdk_rw"].pct_change(4)
    quarterly["us10y_quarter_change_bps"] = quarterly["us10y"].diff() * 100.0
    quarterly["d013_cash_baseline_return"] = 0.0
    return quarterly


def load_daily_end_series(path: Path, value_col: str, dates: pd.DataFrame, output_col: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=[value_col]).sort_values("observation_date")
    aligned = pd.merge_asof(
        dates.sort_values("signal_date"),
        data[["observation_date", value_col]],
        left_on="signal_date",
        right_on="observation_date",
        direction="backward",
    )
    return aligned.drop(columns=["observation_date"]).rename(columns={value_col: output_col})


def load_monthly_kr_short_carry(path: Path, dates: pd.DataFrame) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    data["IR3TIB01KRM156N"] = pd.to_numeric(data["IR3TIB01KRM156N"], errors="coerce")
    data = data.dropna(subset=["IR3TIB01KRM156N"]).copy()
    data["quarter"] = data["observation_date"].dt.to_period("Q").astype(str)
    monthly_carry = data["IR3TIB01KRM156N"] / 100.0 / 12.0
    data["kr_short_quarter_carry"] = monthly_carry
    carry = (
        data.groupby("quarter", sort=True)["kr_short_quarter_carry"]
        .apply(lambda returns: (1.0 + returns).prod() - 1.0)
        .reset_index()
    )
    return dates.merge(carry, on="quarter", how="left")


def build_off_stats(quarterly: pd.DataFrame) -> pd.DataFrame:
    off = quarterly["regime"].eq("OFF")
    on = quarterly["regime"].eq("ON")
    durations = []
    current = 0
    for is_off in off:
        if is_off:
            current += 1
        elif current:
            durations.append(current)
            current = 0
    if current:
        durations.append(current)

    rows = [
        {"metric": "off_quarters", "value": int(off.sum())},
        {"metric": "off_quarter_pct", "value": float(off.mean())},
        {"metric": "on_quarters", "value": int(on.sum())},
        {"metric": "on_quarter_pct", "value": float(on.mean())},
        {"metric": "avg_off_duration_quarters", "value": float(pd.Series(durations).mean())},
        {"metric": "longest_off_streak_quarters", "value": int(max(durations))},
        {"metric": "on_off_transition_count", "value": int(quarterly["regime"].ne(quarterly["regime"].shift()).sum() - 1)},
    ]
    return pd.DataFrame(rows)


def build_return_distribution(quarterly: pd.DataFrame) -> pd.DataFrame:
    variables = {
        "kospi_quarter_return": "KOSPI quarterly return",
        "usdk_rw_quarter_change": "USDKRW quarterly change",
        "us10y_quarter_change_bps": "US 10y yield quarterly change bps",
        "kr_short_quarter_carry": "KR short-rate quarterly carry",
    }
    rows = []
    for regime, group in quarterly.groupby("regime", sort=True):
        for column, label in variables.items():
            values = group[column].dropna()
            rows.append(summary_row(regime, label, values))
    return pd.DataFrame(rows)


def summary_row(regime: str, variable: str, values: pd.Series) -> dict[str, float | int | str]:
    return {
        "regime": regime,
        "variable": variable,
        "n": int(values.shape[0]),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std(ddof=1)),
        "min": float(values.min()),
        "max": float(values.max()),
        "positive_pct": float(values.gt(0.0).mean()),
    }


def build_missed_rally_avoided_crash(quarterly: pd.DataFrame) -> pd.DataFrame:
    off = quarterly.loc[quarterly["regime"].eq("OFF")].copy()
    on = quarterly.loc[quarterly["regime"].eq("ON")].copy()
    rows = []
    for label, frame in [
        ("off_top5_positive_missed_rally", off.sort_values("kospi_quarter_return", ascending=False).head(5)),
        ("off_top5_negative_avoided_crash", off.sort_values("kospi_quarter_return", ascending=True).head(5)),
    ]:
        for rank, row in enumerate(frame.itertuples(index=False), start=1):
            rows.append(
                {
                    "section": label,
                    "rank": rank,
                    "quarter": row.quarter,
                    "regime": row.regime,
                    "kospi_quarter_return": row.kospi_quarter_return,
                    "count": "",
                    "share": "",
                }
            )
    for label, frame, threshold, op in [
        ("off_kospi_gt_plus_10pct", off, 0.10, "gt"),
        ("off_kospi_lt_minus_10pct", off, -0.10, "lt"),
        ("on_kospi_lt_minus_10pct", on, -0.10, "lt"),
    ]:
        mask = frame["kospi_quarter_return"].gt(threshold) if op == "gt" else frame["kospi_quarter_return"].lt(threshold)
        rows.append(
            {
                "section": label,
                "rank": "",
                "quarter": "",
                "regime": "OFF" if label.startswith("off") else "ON",
                "kospi_quarter_return": "",
                "count": int(mask.sum()),
                "share": float(mask.mean()),
            }
        )
    return pd.DataFrame(rows)


def build_sleeve_candidate_returns(quarterly: pd.DataFrame) -> pd.DataFrame:
    off = quarterly.loc[quarterly["regime"].eq("OFF")]
    rows = [
        metric_row("off_usdk_rw_mean_yoy", off["usdk_rw_yoy"]),
        metric_row("off_us10y_mean_quarter_change_bps", off["us10y_quarter_change_bps"]),
        metric_row("off_kr_short_rate_mean_quarter_carry", off["kr_short_quarter_carry"]),
        metric_row("off_d013_cash_baseline_return", off["d013_cash_baseline_return"]),
    ]
    return pd.DataFrame(rows)


def metric_row(metric: str, values: pd.Series) -> dict[str, float | int | str]:
    clean = values.dropna()
    return {"metric": metric, "n": int(clean.shape[0]), "mean": float(clean.mean())}


def build_inverse_diagnostic(quarterly: pd.DataFrame) -> pd.DataFrame:
    short_returns = -quarterly.loc[quarterly["regime"].eq("OFF"), "kospi_quarter_return"].dropna()
    mean = float(short_returns.mean())
    conclusion = "positive_expected_value" if mean > 0.0 else "not_positive_expected_value"
    return pd.DataFrame(
        [
            {
                "scope": "OFF quarters simple KOSPI short, no decay",
                "n": int(short_returns.shape[0]),
                "mean": mean,
                "median": float(short_returns.median()),
                "std": float(short_returns.std(ddof=1)),
                "min": float(short_returns.min()),
                "max": float(short_returns.max()),
                "positive_pct": float(short_returns.gt(0.0).mean()),
                "conclusion": conclusion,
            }
        ]
    )


def write_report(
    off_stats: pd.DataFrame,
    returns: pd.DataFrame,
    crash_rally: pd.DataFrame,
    sleeve: pd.DataFrame,
    inverse: pd.DataFrame,
) -> None:
    stat = dict(zip(off_stats["metric"], off_stats["value"]))
    ret = returns.set_index(["regime", "variable"])
    off_kospi = ret.loc[("OFF", "KOSPI quarterly return")]
    on_kospi = ret.loc[("ON", "KOSPI quarterly return")]
    off_usd = ret.loc[("OFF", "USDKRW quarterly change")]
    off_10y = ret.loc[("OFF", "US 10y yield quarterly change bps")]
    off_kr = ret.loc[("OFF", "KR short-rate quarterly carry")]
    sleeve_s = sleeve.set_index("metric")["mean"]
    inv = inverse.iloc[0]

    if off_kospi["mean"] < -0.03:
        character = "risk-off"
        priority = "H001 USDKRW, H002 Treasury, H004 Gold/defensive 순서가 우선입니다."
    elif off_kospi["mean"] > 0.03:
        character = "missed rally"
        priority = "sleeve보다 gate 문제 점검이 우선이며, H001-H005는 보수적으로 낮은 우선순위입니다."
    else:
        off_gt_10 = crash_count(crash_rally, "off_kospi_gt_plus_10pct")
        off_lt_10 = crash_count(crash_rally, "off_kospi_lt_minus_10pct")
        if off_gt_10 > 0 and off_lt_10 > 0:
            character = "sideways with bipolar tails"
            priority = (
                "H003 KR short-rate carry 1순위, H001 USDKRW 2순위, H005 defensive/static sleeve 3순위, "
                "H002 Treasury 4순위, H004 Gold는 H000 제외 데이터라 H004 단계에서 별도 검증입니다."
            )
        else:
            character = "sideways"
            priority = (
                "H003 KR short-rate carry가 1순위이며, H001 USDKRW와 H002 Treasury는 보조 진단입니다. "
                "H004 Gold는 H000 제외 데이터라 H004 단계에서 별도 검증입니다."
            )

    inverse_verdict = (
        "OFF 평균 KOSPI가 양수라 단순 inverse/short의 기대값은 음수입니다. H006 KOSPI inverse는 sleeve 후보 가치가 낮습니다."
        if inv["mean"] <= 0.0
        else "OFF 평균 KOSPI가 음수라 단순 inverse/short의 1차 후보 가치는 있습니다."
    )

    lines = [
        "# H000 D013 OFF Regime Diagnostics",
        "",
        "## A. OFF regime statistics",
        "",
        f"- OFF quarters: {int(stat['off_quarters'])} ({stat['off_quarter_pct']:.2%})",
        f"- ON quarters: {int(stat['on_quarters'])} ({stat['on_quarter_pct']:.2%})",
        f"- Average OFF duration: {stat['avg_off_duration_quarters']:.2f} quarters",
        f"- Longest OFF streak: {int(stat['longest_off_streak_quarters'])} quarters",
        f"- ON/OFF transitions: {int(stat['on_off_transition_count'])}",
        "",
        "## B. Return distribution",
        "",
        f"- OFF KOSPI quarterly return mean: {off_kospi['mean']:.6f}; median: {off_kospi['median']:.6f}; positive: {off_kospi['positive_pct']:.2%}",
        f"- ON KOSPI quarterly return mean: {on_kospi['mean']:.6f}; median: {on_kospi['median']:.6f}; positive: {on_kospi['positive_pct']:.2%}",
        f"- OFF USDKRW quarterly change mean: {off_usd['mean']:.6f}; OFF USDKRW yoy mean: {sleeve_s['off_usdk_rw_mean_yoy']:.6f}",
        f"- OFF US 10y quarterly change mean: {off_10y['mean']:.2f} bps",
        f"- OFF KR short-rate quarterly carry mean: {off_kr['mean']:.6f}",
        "",
        "## C. Missed rally / avoided crash",
        "",
        f"- OFF and KOSPI > +10%: {crash_count(crash_rally, 'off_kospi_gt_plus_10pct')} quarters",
        f"- OFF and KOSPI < -10%: {crash_count(crash_rally, 'off_kospi_lt_minus_10pct')} quarters",
        f"- ON and KOSPI < -10%: {crash_count(crash_rally, 'on_kospi_lt_minus_10pct')} quarters",
        "",
        "## D. Sleeve candidate OFF returns",
        "",
        f"- USDKRW mean yoy during OFF: {sleeve_s['off_usdk_rw_mean_yoy']:.6f}",
        f"- US 10y mean quarterly change during OFF: {sleeve_s['off_us10y_mean_quarter_change_bps']:.2f} bps",
        f"- KR short-rate mean quarterly carry during OFF: {sleeve_s['off_kr_short_rate_mean_quarter_carry']:.6f}",
        f"- D013 virtual cash baseline during OFF: {sleeve_s['off_d013_cash_baseline_return']:.6f}",
        "",
        "## E. KOSPI inverse diagnostic",
        "",
        f"- Simple OFF short mean: {inv['mean']:.6f}; std: {inv['std']:.6f}; positive: {inv['positive_pct']:.2%}",
        f"- Conclusion: {inv['conclusion']}",
        "",
        "## Verdict",
        "",
        f"- OFF character: {character}",
        f"- Sleeve priority: {priority}",
        f"- H006 KOSPI inverse: {inverse_verdict} 이 진단은 decay와 ETF 비용을 제외한 H000 범위의 1차 필터입니다.",
        "",
        "## Metadata",
        "",
        "- No new backtest was run.",
        "- D013 strategy and existing D/E/F/G/P family outputs were not modified.",
        "- Gold is excluded in H000 per current task instruction.",
        "- KOSPI return source: krx_market_breadth_kospi_2010_2026.csv cap_weighted_return, compounded by quarter.",
        "- USDKRW and US 10y source: FRED files aligned to latest observation on or before each D013 quarterly signal_date.",
        "- KR short-rate source: fred_kr_short_rate.csv; monthly annualized rates converted to monthly carry and compounded by quarter.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def crash_count(table: pd.DataFrame, section: str) -> int:
    value = table.loc[table["section"].eq(section), "count"].iloc[0]
    return int(value)


if __name__ == "__main__":
    main()
