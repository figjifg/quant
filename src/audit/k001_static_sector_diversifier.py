from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
MACRO_DIR = ROOT / "research_input_data/inputs/macro_features"
USDKRW_PATH = MACRO_DIR / "fred_dexkous_usdkrw.csv"
H001_EQUITY_PATH = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "reports/experiments/K001_static_sector_diversifier"

RATE_COLUMN = "IR3TIB01KRM156N"
BASELINE_VARIANT = "N000"
BASELINE_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}

K001_VARIANTS = {
    "K001-A": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "XLP": 0.05},
    "K001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLP": 0.10},
    "K001-C": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "XLU": 0.05},
    "K001-D": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLU": 0.10},
    "K001-E": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "XLV": 0.05},
    "K001-F": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLV": 0.10},
}

N_FAMILY_COMPARATORS = {
    "N001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
    "N002-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "cash": 0.10},
}

STRESS_WINDOWS = {
    "dot_com_proxy_2002_07_2003_12": {
        "start": "2002-07-01",
        "end": "2003-12-31",
        "label": "proxy",
    },
    "gfc_proxy_2008_2009": {
        "start": "2008-01-01",
        "end": "2009-12-31",
        "label": "proxy",
    },
    "covid_2020_02_2020_03": {
        "start": "2020-02-01",
        "end": "2020-03-31",
        "label": "exact",
    },
    "rate_shock_2022": {
        "start": "2022-01-01",
        "end": "2022-12-31",
        "label": "exact",
    },
}

STRESS_LABELS = {
    "dot_com_proxy_2002_07_2003_12": "dot-com proxy 2002-07~2003-12",
    "gfc_proxy_2008_2009": "GFC proxy 2008-2009",
    "covid_2020_02_2020_03": "COVID 2020-02~2020-03",
    "rate_shock_2022": "2022 rate shock",
}

TOLERANCE_PP = 1e-9


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_tickers = ("SPY", "QQQ", "IEF", "XLP", "XLU", "XLV", "GLD")
    etf_nav = load_etf_nav_krw(all_tickers)
    h001 = load_h001_nav()
    cash = build_kr_cash_nav(etf_nav.index.union(h001.index))
    components = etf_nav.join(h001.rename("H001"), how="outer").join(cash.rename("cash"), how="outer").ffill()

    baseline_stress = pd.DataFrame(build_variant_stress_rows(BASELINE_VARIANT, BASELINE_WEIGHTS, components))
    k001_stress = pd.DataFrame(
        [
            row
            for variant, weights in K001_VARIANTS.items()
            for row in build_variant_stress_rows(variant, weights, components)
        ]
    )
    comparator_stress = pd.DataFrame(
        [
            row
            for variant, weights in N_FAMILY_COMPARATORS.items()
            for row in build_variant_stress_rows(variant, weights, components)
        ]
    )

    daily_nav = pd.DataFrame(
        {
            variant: build_rebalanced_nav(components, weights)
            for variant, weights in K001_VARIANTS.items()
        }
    ).sort_index()

    delta_vs_baseline = build_delta_vs_baseline(k001_stress, baseline_stress)
    delta_vs_n_family = build_delta_vs_n_family(k001_stress, comparator_stress)
    overall = build_overall_score_ranking(
        pd.concat(
            [
                delta_vs_baseline,
                build_delta_vs_baseline(comparator_stress, baseline_stress),
            ],
            ignore_index=True,
        )
    )
    full_metrics = build_full_history_metrics(daily_nav)
    metrics = build_metrics_payload(
        full_metrics,
        k001_stress,
        delta_vs_baseline,
        delta_vs_n_family,
        overall,
    )

    daily_nav.reset_index(names="date").to_csv(OUTPUT_DIR / "daily_nav.csv", index=False)
    k001_stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    delta_vs_baseline.to_csv(OUTPUT_DIR / "delta_vs_baseline.csv", index=False)
    delta_vs_n_family.to_csv(OUTPUT_DIR / "delta_vs_n_family.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "overall_score_ranking.csv", index=False)
    write_config()
    write_json(metrics, OUTPUT_DIR / "metrics.json")
    write_report(full_metrics, k001_stress, delta_vs_baseline, delta_vs_n_family, overall)


def load_etf_nav_krw(tickers: tuple[str, ...]) -> pd.DataFrame:
    usdk = load_usdkrw()
    frames = {}
    for ticker in tickers:
        path = etf_path(ticker)
        if not path.exists():
            raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
        data = pd.read_csv(path, parse_dates=["Date"])
        required = {"Date", "Close"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        prices = (
            pd.DataFrame({"date": data["Date"], "close_usd": pd.to_numeric(data["Close"], errors="coerce")})
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
    if ticker in {"XLP", "XLU", "XLV"}:
        return ETF_DIR / f"yf_sector_{ticker}.csv"
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


def load_h001_nav() -> pd.Series:
    data = pd.read_csv(H001_EQUITY_PATH, parse_dates=["date"])
    required = {"date", "net_value"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{H001_EQUITY_PATH} missing columns: {sorted(missing)}")
    series = (
        pd.DataFrame({"date": data["date"], "H001": pd.to_numeric(data["net_value"], errors="coerce")})
        .dropna(subset=["date", "H001"])
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
        .set_index("date")["H001"]
    )
    return series / series.iloc[0]


def build_kr_cash_nav(dates: pd.Index) -> pd.Series:
    rates = pd.read_csv(MACRO_DIR / "fred_kr_short_rate.csv", parse_dates=["observation_date"], na_values=["."])
    rates[RATE_COLUMN] = pd.to_numeric(rates[RATE_COLUMN], errors="coerce")
    rates = rates.dropna(subset=[RATE_COLUMN]).sort_values("observation_date")
    frame = pd.DataFrame({"date": pd.DatetimeIndex(dates).sort_values().unique()})
    aligned = pd.merge_asof(
        frame,
        rates[["observation_date", RATE_COLUMN]],
        left_on="date",
        right_on="observation_date",
        direction="backward",
    )
    daily_return = (1.0 + aligned[RATE_COLUMN] / 100.0 / 12.0) ** (12.0 / 252.0) - 1.0
    nav = (1.0 + daily_return.fillna(0.0)).cumprod()
    nav.index = aligned["date"]
    return nav / nav.iloc[0]


def build_rebalanced_nav(component_nav: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    missing = sorted(set(weights).difference(component_nav.columns))
    if missing:
        raise ValueError(f"Missing components for portfolio: {missing}")
    components = component_nav[list(weights)].dropna(how="all").ffill().dropna(subset=list(weights))
    returns = components.pct_change().fillna(0.0)

    values = []
    sleeve_values: dict[str, float] | None = None
    last_quarter = None
    for date, row in returns.iterrows():
        quarter = date.to_period("Q")
        if sleeve_values is None:
            sleeve_values = weights.copy()
        elif quarter != last_quarter:
            portfolio_value = sum(sleeve_values.values())
            sleeve_values = {ticker: portfolio_value * weight for ticker, weight in weights.items()}
        sleeve_values = {ticker: value * (1.0 + float(row[ticker])) for ticker, value in sleeve_values.items()}
        values.append((date, sum(sleeve_values.values())))
        last_quarter = quarter

    nav = pd.Series(dict(values), name="nav").sort_index()
    return nav / nav.iloc[0]


def build_variant_stress_rows(
    variant: str,
    registered_weights: dict[str, float],
    components: pd.DataFrame,
) -> list[dict[str, object]]:
    rows = []
    for stress_name, spec in STRESS_WINDOWS.items():
        start = pd.Timestamp(spec["start"])
        end = pd.Timestamp(spec["end"])
        if spec["label"] == "exact":
            weights = registered_weights
            measurement_type = "exact"
            excluded = []
        else:
            weights, excluded = proxy_weights_for_window(registered_weights, components, start, end)
            measurement_type = "proxy" if not excluded else "proxy_rescaled_missing_sleeves"
        nav = build_rebalanced_nav(components, weights)
        window = nav.loc[nav.index.to_series().between(start, end)].dropna()
        if window.empty:
            raise ValueError(f"No observations for {variant} {stress_name}")
        row = metrics_for_window(stress_name, measurement_type, variant, weights, window)
        row["registered_weights"] = weights_to_text(registered_weights)
        row["proxy_excluded_sleeves"] = ";".join(excluded)
        rows.append(row)
    return rows


def proxy_weights_for_window(
    weights: dict[str, float],
    components: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[dict[str, float], list[str]]:
    available = {}
    excluded = []
    for ticker, weight in weights.items():
        if ticker == "H001":
            excluded.append(ticker)
            continue
        series = components[ticker].loc[components.index.to_series().between(start, end)].dropna()
        if series.empty:
            excluded.append(ticker)
            continue
        available[ticker] = weight
    total = sum(available.values())
    if total <= 0.0:
        raise ValueError("Proxy window has no available registered sleeves.")
    return {ticker: weight / total for ticker, weight in available.items()}, excluded


def metrics_for_window(
    stress_name: str,
    measurement_type: str,
    variant: str,
    weights: dict[str, float],
    nav: pd.Series,
) -> dict[str, object]:
    returns = nav.pct_change().fillna(0.0)
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    peak_value = nav.loc[peak_date]
    recovered = nav.loc[trough_date:].loc[lambda data: data >= peak_value]
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1.0 / 365.25)
    daily_std = float(returns.std())
    return {
        "variant": variant,
        "stress_window": stress_name,
        "measurement_type": measurement_type,
        "portfolio_series": variant,
        "weights": weights_to_text(weights),
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "n_observations": int(nav.shape[0]),
        "total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "gross_sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), daily_std),
        "annualized_volatility": daily_std * math.sqrt(252.0),
        "daily_max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
        "mdd_recovery_date": None if recovered.empty else recovered.index[0].date().isoformat(),
    }


def build_delta_vs_baseline(stress: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    baseline_ref = baseline.loc[:, ["stress_window", "total_return", "daily_max_drawdown"]].rename(
        columns={
            "total_return": "baseline_total_return",
            "daily_max_drawdown": "baseline_daily_max_drawdown",
        }
    )
    data = stress.merge(baseline_ref, on="stress_window", how="left", validate="many_to_one")
    data["delta_total_return"] = data["total_return"] - data["baseline_total_return"]
    data["delta_daily_max_drawdown"] = data["daily_max_drawdown"] - data["baseline_daily_max_drawdown"]
    data["delta_return_pp"] = data["delta_total_return"] * 100.0
    data["delta_mdd_pp"] = data["delta_daily_max_drawdown"] * 100.0
    return data[
        [
            "variant",
            "stress_window",
            "measurement_type",
            "total_return",
            "baseline_total_return",
            "delta_total_return",
            "delta_return_pp",
            "daily_max_drawdown",
            "baseline_daily_max_drawdown",
            "delta_daily_max_drawdown",
            "delta_mdd_pp",
            "proxy_excluded_sleeves",
        ]
    ]


def build_delta_vs_n_family(k001_stress: pd.DataFrame, comparator_stress: pd.DataFrame) -> pd.DataFrame:
    rows = []
    comparator_ref = comparator_stress.loc[
        :, ["variant", "stress_window", "total_return", "daily_max_drawdown"]
    ].rename(
        columns={
            "variant": "comparator",
            "total_return": "comparator_total_return",
            "daily_max_drawdown": "comparator_daily_max_drawdown",
        }
    )
    for comparator in ("N001-B", "N002-B"):
        merged = k001_stress.merge(
            comparator_ref.loc[comparator_ref["comparator"].eq(comparator)],
            on="stress_window",
            how="left",
            validate="many_to_one",
        )
        merged["comparator"] = comparator
        merged["delta_return_vs_comparator_pp"] = (
            merged["total_return"] - merged["comparator_total_return"]
        ) * 100.0
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


def build_full_history_metrics(daily_nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant, nav in daily_nav.items():
        rows.append(metrics_for_window("full_history_2010_2026", "exact", variant, {}, nav.dropna()))
    return pd.DataFrame(rows)


def build_overall_score_ranking(delta: pd.DataFrame) -> pd.DataFrame:
    rows = delta.copy()
    rows["return_improved"] = rows["delta_return_pp"] > TOLERANCE_PP
    rows["mdd_improved"] = rows["delta_mdd_pp"] > TOLERANCE_PP
    rows["return_worsened"] = rows["delta_return_pp"] < -TOLERANCE_PP
    rows["mdd_worsened"] = rows["delta_mdd_pp"] < -TOLERANCE_PP
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
    scores = scores.sort_values(
        ["mdd_score_pp", "return_score_pp", "balanced_score_pp", "variant"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    scores.insert(0, "overall_rank", range(1, len(scores) + 1))
    scores["family"] = scores["variant"].map(lambda value: "K001" if value.startswith("K001") else "N-family")
    return scores


def build_metrics_payload(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta_vs_baseline: pd.DataFrame,
    delta_vs_n_family: pd.DataFrame,
    overall: pd.DataFrame,
) -> dict[str, object]:
    return {
        "experiment": "K001_static_sector_diversifier",
        "purpose": "static defensive sector sleeve stress comparison",
        "guardrails": {
            "defensive_sectors_only": ["XLP", "XLU", "XLV"],
            "other_sectors": False,
            "weights_grid": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "role": "backlog_candidate_library",
        },
        "currency": "KRW",
        "fx_policy": "USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "variants": K001_VARIANTS,
        "full_history": records_for_json(full_metrics),
        "stress_windows": records_for_json(stress),
        "delta_vs_baseline": records_for_json(delta_vs_baseline),
        "delta_vs_n_family": records_for_json(delta_vs_n_family),
        "overall_score_ranking": records_for_json(overall),
    }


def write_config() -> None:
    lines = [
        "experiment: K001_static_sector_diversifier",
        "status: generated",
        "mode: stress_response_only",
        "search: none",
        "promotion: none",
        "candidate_status: backlog_candidate_library",
        "base_candidate: P08_IEF30",
        "rebalance: quarterly",
        "nav_basis: gross",
        "tax_model: none",
        "currency: KRW",
        "fx_policy: USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "allowed_sector_sleeves:",
        "  - XLP",
        "  - XLU",
        "  - XLV",
        "prohibited_sector_sleeves:",
        "  - XLE",
        "  - XLF",
        "  - XLK",
        "  - XLI",
        "  - XLY",
        "  - XLB",
        "  - XLRE",
        "  - XLC",
        "pre_2010_proxy:",
        "  rule: exclude H001 and sleeves without local observations in the stress window, then rescale remaining registered weights",
        "baseline:",
        "  N000:",
        *[f"    {ticker}: {weight:.10f}" for ticker, weight in BASELINE_WEIGHTS.items()],
        "variants:",
    ]
    for variant, weights in K001_VARIANTS.items():
        lines.append(f"  {variant}:")
        lines.extend(f"    {ticker}: {weight:.10f}" for ticker, weight in weights.items())
    lines.extend(
        [
            "comparators:",
            "  N001-B: GLD 10%",
            "  N002-B: cash 10%",
            "sources:",
            f"  etf_dir: {ETF_DIR.relative_to(ROOT)}",
            f"  usdk_rw_file: {USDKRW_PATH.relative_to(ROOT)}",
            f"  h001_equity_curve: {H001_EQUITY_PATH.relative_to(ROOT)}",
            f"  kr_cash_rate: {(MACRO_DIR / 'fred_kr_short_rate.csv').relative_to(ROOT)}",
            "guardrails:",
            "  best_sharpe_search: false",
            "  p08_ief30_modified: false",
            "  direct_promotion: false",
            "  role: backlog_candidate_library",
            "",
        ]
    )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta_vs_baseline: pd.DataFrame,
    delta_vs_n_family: pd.DataFrame,
    overall: pd.DataFrame,
) -> None:
    best_k001 = overall.loc[overall["family"].eq("K001")].iloc[0]
    best_overall = overall.iloc[0]
    all_improvers = all_stress_improvers(delta_vs_baseline)
    best_gfc = best_variant_for_stress(delta_vs_baseline, "gfc_proxy_2008_2009")
    best_2022 = best_variant_for_stress(delta_vs_baseline, "rate_shock_2022")
    best_xlv_10 = "K001-F"
    xlv_10_gfc = delta_for(delta_vs_baseline, best_xlv_10, "gfc_proxy_2008_2009")
    xlv_10_2022 = delta_for(delta_vs_baseline, best_xlv_10, "rate_shock_2022")
    sector_10_vs_n = delta_vs_n_family.loc[
        delta_vs_n_family["variant"].isin(["K001-B", "K001-D", "K001-F"])
    ].copy()

    lines = [
        "# K001 Static Sector Diversifier",
        "",
        "Status: GENERATED BY `src.audit.k001_static_sector_diversifier`",
        "",
        "## 범위",
        "",
        "- K001 = N-family 확장. XLP / XLU / XLV defensive sector만 실행했다.",
        "- 5% / 10% 사전 등록 후보 6개만 실행했다. 새 weights grid X.",
        "- `P08_IEF30` 직접 promote X. 결과는 backlog candidate library 전용이다.",
        "- Gross NAV 비교다. HIFO / 250만 공제 / 양도세는 적용하지 않았다.",
        "- ETF sleeve는 로컬 USDKRW를 ETF 거래일에 선형 보간 후 forward-fill하여 KRW NAV로 환산했다.",
        "",
        "## 6 K001 Variant x 4 Stress",
        "",
        table_for_report(
            stress,
            [
                "variant",
                "stress_window",
                "measurement_type",
                "total_return",
                "daily_max_drawdown",
                "gross_sharpe",
                "proxy_excluded_sleeves",
            ],
        ),
        "",
        "## N000 Baseline 대비 변화",
        "",
        f"- Best K001: {best_k001['variant']} (return score {best_k001['return_score_pp']:.4f}pp, MDD score {best_k001['mdd_score_pp']:.4f}pp).",
        f"- GFC best K001: {best_gfc['variant']} (return {best_gfc['delta_return_pp']:.4f}pp, MDD {best_gfc['delta_mdd_pp']:.4f}pp).",
        f"- 2022 best K001: {best_2022['variant']} (return {best_2022['delta_return_pp']:.4f}pp, MDD {best_2022['delta_mdd_pp']:.4f}pp).",
        f"- 4 stress 모두 return과 MDD를 동시에 개선한 K001 variant: {', '.join(all_improvers) if all_improvers else '없음'}.",
        f"- XLV 10% ({best_xlv_10})는 GFC return {xlv_10_gfc['delta_return_pp']:.4f}pp / MDD {xlv_10_gfc['delta_mdd_pp']:.4f}pp, 2022 return {xlv_10_2022['delta_return_pp']:.4f}pp / MDD {xlv_10_2022['delta_mdd_pp']:.4f}pp다.",
        "",
        table_for_report(
            delta_vs_baseline,
            [
                "variant",
                "stress_window",
                "delta_return_pp",
                "delta_mdd_pp",
                "total_return",
                "baseline_total_return",
                "daily_max_drawdown",
                "baseline_daily_max_drawdown",
            ],
        ),
        "",
        "## GLD 10% / Cash 10% 비교",
        "",
        "- N001-B는 GLD 10%, N002-B는 cash 10% 비교군이다. 둘 다 K001와 같은 KRW-converted framework에서 재계산했다.",
        "",
        table_for_report(
            sector_10_vs_n,
            [
                "variant",
                "comparator",
                "stress_window",
                "delta_return_vs_comparator_pp",
                "delta_mdd_vs_comparator_pp",
                "total_return",
                "comparator_total_return",
                "daily_max_drawdown",
                "comparator_daily_max_drawdown",
            ],
        ),
        "",
        "## Multi-stress Overall Score",
        "",
        f"- Overall best across K001 + N001-B + N002-B: {best_overall['variant']} ({best_overall['family']}).",
        "- Ranking은 N005와 동일하게 4 stress 평균 return score + MDD score를 계산하고, MDD score 우선 / return score 보조로 정렬했다.",
        "",
        table_for_report(
            overall,
            [
                "overall_rank",
                "variant",
                "family",
                "return_score_pp",
                "mdd_score_pp",
                "balanced_score_pp",
                "return_improved_count",
                "mdd_improved_count",
                "return_worsened_count",
                "mdd_worsened_count",
            ],
        ),
        "",
        "## Full History Metrics",
        "",
        table_for_report(
            full_metrics,
            ["variant", "start_date", "end_date", "total_return", "gross_sharpe", "daily_max_drawdown"],
        ),
        "",
        "## Verdict",
        "",
        f"- K001 best가 N-family best보다 우수한가: {'예' if best_overall['family'] == 'K001' else '아니오'}. 현재 ranking 1위는 {best_overall['variant']}이고, K001 내부 1위는 {best_k001['variant']}다.",
        f"- Paper tracking shadow 추가 가치: {'있음' if best_k001['overall_rank'] <= 3 else '제한적'}. K001 best의 MDD score는 {best_k001['mdd_score_pp']:.4f}pp이고 return score는 {best_k001['return_score_pp']:.4f}pp다.",
        "- `P08_IEF30` 직접 promote X. K001 결과는 backlog candidate library에만 추가한다.",
        "- K002(one-shot momentum)는 진행 권고. 단, K001처럼 사전 등록 universe와 weights/search guardrail을 먼저 고정해야 한다.",
        "",
        "## 산출물",
        "",
        "- config.yaml",
        "- daily_nav.csv",
        "- stress_windows.csv",
        "- delta_vs_baseline.csv",
        "- delta_vs_n_family.csv",
        "- overall_score_ranking.csv",
        "- metrics.json",
        "- report.md",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def all_stress_improvers(delta: pd.DataFrame) -> list[str]:
    rows = delta.copy()
    rows["both_improved"] = (rows["delta_return_pp"] > TOLERANCE_PP) & (rows["delta_mdd_pp"] > TOLERANCE_PP)
    counts = rows.groupby("variant", sort=False)["both_improved"].sum()
    return counts.loc[counts.eq(len(STRESS_WINDOWS))].index.tolist()


def best_variant_for_stress(delta: pd.DataFrame, stress_window: str) -> pd.Series:
    rows = delta.loc[delta["stress_window"].eq(stress_window)].copy()
    return rows.sort_values(["delta_mdd_pp", "delta_return_pp", "variant"], ascending=[False, False, True]).iloc[0]


def delta_for(delta: pd.DataFrame, variant: str, stress_window: str) -> pd.Series:
    rows = delta.loc[delta["variant"].eq(variant) & delta["stress_window"].eq(stress_window)]
    if rows.empty:
        raise ValueError(f"Missing delta row: {variant} {stress_window}")
    return rows.iloc[0]


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


def records_for_json(data: pd.DataFrame) -> list[dict[str, object]]:
    records = []
    for record in data.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            clean[key] = None if pd.isna(value) else value
        records.append(clean)
    return records


def write_json(payload: dict[str, object], path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def weights_to_text(weights: dict[str, float]) -> str:
    return ";".join(f"{ticker}:{weight:.4f}" for ticker, weight in weights.items())


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0 or math.isnan(denominator):
        return None
    return numerator / denominator


if __name__ == "__main__":
    main()
