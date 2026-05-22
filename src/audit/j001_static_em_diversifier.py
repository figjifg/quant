from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.audit.k001_static_sector_diversifier import (
    BASELINE_WEIGHTS,
    build_delta_vs_baseline,
    build_full_history_metrics,
    build_kr_cash_nav,
    build_rebalanced_nav,
    build_variant_stress_rows,
    load_h001_nav,
    records_for_json,
    write_json,
)


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
MACRO_DIR = ROOT / "research_input_data/inputs/macro_features"
USDKRW_PATH = MACRO_DIR / "fred_dexkous_usdkrw.csv"
H001_EQUITY_PATH = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "reports/experiments/J001_static_em_diversifier"

J001_VARIANTS = {
    "J001-A": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "VWO": 0.05},
    "J001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "VWO": 0.10},
    "J001-C": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "EWJ": 0.05},
    "J001-D": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "EWJ": 0.10},
    "J001-E": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "EWY": 0.05},
    "J001-F": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "EWY": 0.10},
}
COMPARATOR_WEIGHTS = {
    "N001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
    "N002-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "cash": 0.10},
    "K001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLP": 0.10},
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tickers = ("SPY", "QQQ", "IEF", "GLD", "XLP", "VWO", "EWJ", "EWY")
    etf_nav = load_etf_nav_krw(tickers)
    h001 = load_h001_nav()
    cash = build_kr_cash_nav(etf_nav.index.union(h001.index))
    components = etf_nav.join(h001.rename("H001"), how="outer").join(cash.rename("cash"), how="outer").ffill()

    baseline_stress = pd.DataFrame(build_variant_stress_rows("P08_IEF30", BASELINE_WEIGHTS, components))
    j001_stress = pd.DataFrame(
        row for variant, weights in J001_VARIANTS.items() for row in build_variant_stress_rows(variant, weights, components)
    )
    comparator_stress = pd.DataFrame(
        row
        for variant, weights in COMPARATOR_WEIGHTS.items()
        for row in build_variant_stress_rows(variant, weights, components)
    )

    daily_nav = pd.DataFrame({variant: build_rebalanced_nav(components, weights) for variant, weights in J001_VARIANTS.items()})
    comparator_nav = pd.DataFrame(
        {
            "P08_IEF30": build_rebalanced_nav(components, BASELINE_WEIGHTS),
            **{variant: build_rebalanced_nav(components, weights) for variant, weights in COMPARATOR_WEIGHTS.items()},
        }
    )
    full_metrics = build_full_history_metrics(pd.concat([daily_nav, comparator_nav], axis=1).sort_index())
    delta_vs_baseline = build_delta_vs_baseline(j001_stress, baseline_stress)
    delta_vs_comparators = build_delta_vs_comparators(j001_stress, comparator_stress)
    overall = build_j001_overall_score_ranking(
        pd.concat([delta_vs_baseline, build_delta_vs_baseline(comparator_stress, baseline_stress)], ignore_index=True)
    )
    metrics = build_metrics_payload(full_metrics, j001_stress, delta_vs_baseline, delta_vs_comparators, overall)

    daily_nav.reset_index(names="date").to_csv(OUTPUT_DIR / "daily_nav.csv", index=False)
    j001_stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    delta_vs_baseline.to_csv(OUTPUT_DIR / "delta_vs_baseline.csv", index=False)
    delta_vs_comparators.to_csv(OUTPUT_DIR / "delta_vs_comparators.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "overall_score_ranking.csv", index=False)
    write_config()
    write_json(metrics, OUTPUT_DIR / "metrics.json")
    write_report(full_metrics, j001_stress, delta_vs_baseline, delta_vs_comparators, overall)


def load_etf_nav_krw(tickers: tuple[str, ...]) -> pd.DataFrame:
    usdk = load_usdkrw()
    frames = {}
    for ticker in tickers:
        path = etf_path(ticker)
        if not path.exists():
            raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
        data = pd.read_csv(path, parse_dates=["Date"])
        close = pd.to_numeric(data["Close"], errors="coerce")
        prices = (
            pd.DataFrame({"date": data["Date"], "close_usd": close})
            .dropna(subset=["date", "close_usd"])
            .sort_values("date")
            .drop_duplicates(subset=["date"], keep="last")
        )
        frame = prices.merge(usdk, on="date", how="left").sort_values("date")
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame["close_krw"] = frame["close_usd"] * frame["USDKRW"]
        series = frame.set_index("date")["close_krw"].dropna()
        frames[ticker] = series / series.iloc[0]
    return pd.DataFrame(frames).sort_index()


def etf_path(ticker: str) -> Path:
    if ticker in {"VWO", "EWJ", "EWY"}:
        return ETF_DIR / f"yf_em_{ticker}.csv"
    if ticker == "XLP":
        return ETF_DIR / "yf_sector_XLP.csv"
    long_path = ETF_DIR / f"yf_{ticker}_long.csv"
    if long_path.exists():
        return long_path
    return ETF_DIR / f"yf_{ticker}.csv"


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_PATH, parse_dates=["observation_date"], na_values=["."])
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return (
        data.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
    )


def build_delta_vs_comparators(j001_stress: pd.DataFrame, comparator_stress: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref = comparator_stress.loc[:, ["variant", "stress_window", "total_return", "daily_max_drawdown"]].rename(
        columns={
            "variant": "comparator",
            "total_return": "comparator_total_return",
            "daily_max_drawdown": "comparator_daily_max_drawdown",
        }
    )
    for comparator in COMPARATOR_WEIGHTS:
        merged = j001_stress.merge(ref.loc[ref["comparator"].eq(comparator)], on="stress_window", how="left")
        merged["comparator"] = comparator
        merged["delta_return_vs_comparator_pp"] = (merged["total_return"] - merged["comparator_total_return"]) * 100.0
        merged["delta_mdd_vs_comparator_pp"] = (
            merged["daily_max_drawdown"] - merged["comparator_daily_max_drawdown"]
        ) * 100.0
        rows.append(merged)
    data = pd.concat(rows, ignore_index=True)
    return data[
        [
            "variant",
            "comparator",
            "stress_window",
            "measurement_type",
            "total_return",
            "comparator_total_return",
            "delta_return_vs_comparator_pp",
            "daily_max_drawdown",
            "comparator_daily_max_drawdown",
            "delta_mdd_vs_comparator_pp",
            "proxy_excluded_sleeves",
        ]
    ]


def build_j001_overall_score_ranking(delta: pd.DataFrame) -> pd.DataFrame:
    rows = delta.copy()
    rows["return_improved"] = rows["delta_return_pp"] > 1e-9
    rows["mdd_improved"] = rows["delta_mdd_pp"] > 1e-9
    rows["return_worsened"] = rows["delta_return_pp"] < -1e-9
    rows["mdd_worsened"] = rows["delta_mdd_pp"] < -1e-9
    scores = (
        rows.groupby("variant", sort=False)
        .agg(
            return_score_pp=("delta_return_pp", "mean"),
            mdd_score_pp=("delta_mdd_pp", "mean"),
            stress_count=("stress_window", "count"),
            return_improved_count=("return_improved", "sum"),
            mdd_improved_count=("mdd_improved", "sum"),
            return_worsened_count=("return_worsened", "sum"),
            mdd_worsened_count=("mdd_worsened", "sum"),
        )
        .reset_index()
    )
    scores["balanced_score_pp"] = (scores["return_score_pp"] + scores["mdd_score_pp"]) / 2.0
    scores["family"] = scores["variant"].map(lambda value: "J001" if str(value).startswith("J001") else value.split("-")[0])
    scores = scores.sort_values(
        ["mdd_score_pp", "return_score_pp", "balanced_score_pp", "variant"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    scores.insert(0, "overall_rank", range(1, len(scores) + 1))
    return scores


def build_metrics_payload(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta_vs_baseline: pd.DataFrame,
    delta_vs_comparators: pd.DataFrame,
    overall: pd.DataFrame,
) -> dict[str, object]:
    return {
        "experiment": "J001_static_em_diversifier",
        "purpose": "static EM equity sleeve stress comparison",
        "guardrails": {
            "registered_candidates_only": True,
            "weight_grid": False,
            "additional_em_etfs": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "role": "backlog_candidate_library",
        },
        "variants": J001_VARIANTS,
        "comparators": COMPARATOR_WEIGHTS,
        "full_history": records_for_json(full_metrics),
        "stress_windows": records_for_json(stress),
        "delta_vs_baseline": records_for_json(delta_vs_baseline),
        "delta_vs_comparators": records_for_json(delta_vs_comparators),
        "overall_score_ranking": records_for_json(overall),
    }


def write_config() -> None:
    lines = [
        "experiment: J001_static_em_diversifier",
        "status: generated",
        "candidate_status: backlog_candidate_library",
        "base_candidate: P08_IEF30",
        "direct_promote_p08_ief30: false",
        "rebalance: quarterly",
        "nav_basis: gross",
        "tax_model: none",
        "currency: KRW",
        "fx_policy: USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "baseline:",
        *[f"  {ticker}: {weight:.10f}" for ticker, weight in BASELINE_WEIGHTS.items()],
        "variants:",
    ]
    for variant, weights in J001_VARIANTS.items():
        lines.append(f"  {variant}:")
        lines.extend(f"    {ticker}: {weight:.10f}" for ticker, weight in weights.items())
    lines.extend(
        [
            "comparators:",
            "  N001-B: GLD 10%",
            "  N002-B: cash 10%",
            "  K001-B: XLP 10%",
            "notes:",
            "  - J001-E and J001-F may double expose Korea through H001 plus EWY.",
            "sources:",
            f"  etf_dir: {ETF_DIR.relative_to(ROOT)}",
            f"  usdk_rw_file: {USDKRW_PATH.relative_to(ROOT)}",
            f"  h001_equity_curve: {H001_EQUITY_PATH.relative_to(ROOT)}",
            "prohibited:",
            "  weight_grid: true",
            "  additional_em_etfs: true",
            "  external_network: true",
            "  engine_modification: true",
            "",
        ]
    )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta_vs_baseline: pd.DataFrame,
    delta_vs_comparators: pd.DataFrame,
    overall: pd.DataFrame,
) -> None:
    variants = list(J001_VARIANTS)
    best_mdd = full_metrics.loc[full_metrics["variant"].isin(variants)].sort_values("daily_max_drawdown", ascending=False).iloc[0]
    lines = [
        "# J001 Static EM Diversifier",
        "",
        "Status: GENERATED BY `src.audit.j001_static_em_diversifier`",
        "",
        "## Scope",
        "",
        "- Six pre-registered candidates only: VWO/EWJ/EWY at 5% and 10%.",
        "- Quarterly gross NAV, no tax model, KRW conversion with local USDKRW interpolation.",
        "- EM is treated as a risk asset, not a stress hedge.",
        "- J-family remains backlog candidate library; `P08_IEF30` direct promote X.",
        "- J001-E/J001-F have possible Korea double exposure through H001 plus EWY.",
        "",
        "## Full-history Metrics",
        "",
        f"- Best J001 full-history MDD: {best_mdd['variant']} ({best_mdd['daily_max_drawdown']:.6f}).",
        "",
        table_for_report(full_metrics.loc[full_metrics["variant"].isin([*variants, "P08_IEF30", "N001-B", "N002-B", "K001-B"])], ["variant", "cagr", "gross_sharpe", "daily_max_drawdown", "start_date", "end_date"]),
        "",
        "## Delta vs P08_IEF30",
        "",
        table_for_report(delta_vs_baseline, ["variant", "stress_window", "measurement_type", "delta_return_pp", "delta_mdd_pp", "proxy_excluded_sleeves"]),
        "",
        "## Delta vs N/K Comparators",
        "",
        table_for_report(delta_vs_comparators, ["variant", "comparator", "stress_window", "delta_return_vs_comparator_pp", "delta_mdd_vs_comparator_pp"]),
        "",
        "## Stress Windows",
        "",
        table_for_report(stress, ["variant", "stress_window", "measurement_type", "total_return", "gross_sharpe", "daily_max_drawdown"]),
        "",
        "## Ranking",
        "",
        table_for_report(overall, ["overall_rank", "variant", "family", "return_score_pp", "mdd_score_pp", "balanced_score_pp", "return_improved_count", "mdd_improved_count"]),
        "",
        "## Verdict",
        "",
        "- J001 is diagnostic/backlog only; no `P08_IEF30` promotion is made here.",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def table_for_report(data: pd.DataFrame, columns: list[str]) -> str:
    rows = data.loc[:, columns].copy()
    for column in rows.columns:
        if pd.api.types.is_float_dtype(rows[column]):
            rows[column] = rows[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.6f}")
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join("" if pd.isna(value) else str(value) for value in row) + " |"
        for row in rows.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


if __name__ == "__main__":
    main()
