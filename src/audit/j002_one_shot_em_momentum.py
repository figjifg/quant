from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from src.audit.k002_one_shot_sector_momentum import (
    BASELINE_WEIGHTS,
    PRE_2010_P08_PROXY_WEIGHTS,
    TOLERANCE,
    all_stress_improved,
    better_on_return_mdd_sharpe,
    build_kr_cash_nav,
    build_metrics_table,
    build_rebalanced_nav,
    build_spike_exclusion,
    build_subperiod_split,
    metrics_for_nav,
    rebase_frame,
    records_for_json,
    score_rows,
    table_for_report,
    write_json,
)
from src.audit.k001_static_sector_diversifier import load_h001_nav


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_PATH = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
H001_EQUITY_PATH = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "reports/experiments/J002_one_shot_em_momentum"

EM_ETFS = ["VWO", "EWY", "EWJ", "EWZ", "MCHI"]
LOOKBACK_DAYS = 252
TOP_K = 2
J002_VARIANTS = {
    "J002-A": {"QQQ": 0.21, "H001": 0.20, "IEF": 0.30, "EMMomentum": 0.29},
    "J002-B": {"H001": 0.20, "IEF": 0.30, "EMMomentum": 0.50},
    "J002-C": {"EMMomentum": 1.00},
}
COMPARATOR_WEIGHTS = {
    "P08_IEF30": BASELINE_WEIGHTS,
    "SPY_100": {"SPY": 1.00},
    "QQQ_100": {"QQQ": 1.00},
    "K001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLP": 0.10},
    "N001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
    "N002-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "cash": 0.10},
}
STRESS_WINDOWS = {
    "dot_com_proxy_2000_2002": ("2000-01-01", "2002-12-31", "proxy_em_momentum_only"),
    "gfc_proxy_2008_2009": ("2008-01-01", "2009-12-31", "proxy_em_momentum_only"),
    "covid_2020_02_2020_03": ("2020-02-01", "2020-03-31", "exact"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31", "exact"),
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    usdk = load_usdkrw()
    etf_nav = load_etf_nav_krw(("SPY", "QQQ", "IEF", "GLD", "XLP"), usdk)
    em_prices = load_em_prices_krw(usdk)
    momentum_nav, hold_history = build_em_momentum_nav(em_prices, etf_nav["SPY"])
    h001 = load_h001_nav()
    cash = build_kr_cash_nav(etf_nav.index.union(h001.index))
    p08_proxy_nav = build_rebalanced_nav(etf_nav[["SPY", "QQQ", "IEF"]], PRE_2010_P08_PROXY_WEIGHTS)

    components = (
        etf_nav.join(h001.rename("H001"), how="outer")
        .join(cash.rename("cash"), how="outer")
        .join(momentum_nav.rename("EMMomentum"), how="outer")
        .sort_index()
        .ffill()
    )
    variant_nav = build_variant_navs(components, J002_VARIANTS)
    comparator_nav = build_variant_navs(components, COMPARATOR_WEIGHTS)
    stress_nav = pd.concat([variant_nav, comparator_nav], axis=1)
    analysis_nav = rebase_frame(
        stress_nav.loc[stress_nav.index.to_series().between(pd.Timestamp("2010-01-01"), pd.Timestamp("2026-12-31"))]
    )

    full_metrics = build_metrics_table(analysis_nav, "full_history_2010_2026")
    stress = build_stress_windows(stress_nav, momentum_nav, p08_proxy_nav)
    turnover = build_turnover_by_year(hold_history)
    delta = build_delta_vs_comparators(full_metrics, "J002-A")
    subperiod = build_subperiod_split(analysis_nav)
    spike = build_spike_exclusion(analysis_nav)
    overall = build_overall_score_ranking(stress)
    promotion = evaluate_promotion(full_metrics, stress, subperiod, spike)
    metrics = build_metrics_payload(full_metrics, stress, turnover, delta, subperiod, spike, overall, promotion)

    analysis_nav[list(J002_VARIANTS)].reset_index(names="date").to_csv(OUTPUT_DIR / "daily_nav.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    turnover.to_csv(OUTPUT_DIR / "turnover_by_year.csv", index=False)
    hold_history.to_csv(OUTPUT_DIR / "em_hold_history.csv", index=False)
    delta.to_csv(OUTPUT_DIR / "delta_vs_baseline.csv", index=False)
    subperiod.to_csv(OUTPUT_DIR / "subperiod_split.csv", index=False)
    spike.to_csv(OUTPUT_DIR / "2025_spike_exclusion.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "overall_score_ranking.csv", index=False)
    write_config()
    write_json(metrics, OUTPUT_DIR / "metrics.json")
    write_report(full_metrics, stress, turnover, hold_history, delta, subperiod, spike, overall, promotion)


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_PATH, parse_dates=["observation_date"], na_values=["."])
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return (
        data.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
    )


def load_etf_nav_krw(tickers: tuple[str, ...], usdk: pd.DataFrame) -> pd.DataFrame:
    frames = {}
    for ticker in tickers:
        prices = load_price(ticker, etf_path(ticker))
        frame = prices.merge(usdk, on="date", how="left").sort_values("date")
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame["close_krw"] = frame["close_usd"] * frame["USDKRW"]
        series = frame.set_index("date")["close_krw"].dropna()
        frames[ticker] = series / series.iloc[0]
    return pd.DataFrame(frames).sort_index()


def load_em_prices_krw(usdk: pd.DataFrame) -> pd.DataFrame:
    frames = {}
    for ticker in EM_ETFS:
        prices = load_price(ticker, ETF_DIR / f"yf_em_{ticker}.csv")
        frame = prices.merge(usdk, on="date", how="left").sort_values("date")
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame[ticker] = frame["close_usd"] * frame["USDKRW"]
        frames[ticker] = frame.set_index("date")[ticker].dropna()
    return pd.DataFrame(frames).sort_index()


def load_price(ticker: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    return (
        pd.DataFrame({"date": data["Date"], "close_usd": pd.to_numeric(data["Close"], errors="coerce")})
        .dropna(subset=["date", "close_usd"])
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
    )


def etf_path(ticker: str) -> Path:
    if ticker == "XLP":
        return ETF_DIR / "yf_sector_XLP.csv"
    long_path = ETF_DIR / f"yf_{ticker}_long.csv"
    if long_path.exists():
        return long_path
    return ETF_DIR / f"yf_{ticker}.csv"


def build_em_momentum_nav(em_prices: pd.DataFrame, warmup_nav: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    prices = em_prices.sort_index()
    returns = prices.pct_change(fill_method=None)
    calendar = prices.index
    rebalance_dates = first_trading_days_by_quarter(calendar)
    warmup_returns = warmup_nav.reindex(calendar).ffill().pct_change().fillna(0.0)

    current_weights: dict[str, float] = {}
    previous_target: dict[str, float] = {}
    value = 1.0
    rows = []
    hold_rows = []

    for date in calendar:
        if date in rebalance_dates:
            signal_date = previous_trading_day(calendar, date)
            if signal_date is not None:
                ranked = rank_em(prices, signal_date)
                if len(ranked) >= TOP_K:
                    top = ranked[:TOP_K]
                    current_weights = {ticker: 1.0 / TOP_K for ticker in top}
                    turnover = one_way_turnover(previous_target, current_weights)
                    hold_rows.append(
                        {
                            "execution_date": date.date().isoformat(),
                            "signal_date": signal_date.date().isoformat(),
                            "quarter": date.to_period("Q").strftime("Q%q-%Y"),
                            "available_ticker_count": int(len(ranked)),
                            "rank_1": top[0],
                            "rank_2": top[1],
                            "rank_1_return_252d": float(momentum_return(prices[top[0]], signal_date)),
                            "rank_2_return_252d": float(momentum_return(prices[top[1]], signal_date)),
                            "turnover_one_way": turnover,
                        }
                    )
                    previous_target = current_weights.copy()
        if current_weights:
            daily_return = sum(
                (0.0 if math.isnan(float(returns.at[date, ticker])) else float(returns.at[date, ticker])) * weight
                for ticker, weight in current_weights.items()
            )
        else:
            daily_return = float(warmup_returns.loc[date])
        value *= 1.0 + daily_return
        rows.append((date, value))

    nav = pd.Series(dict(rows), name="EMMomentum").sort_index()
    return nav / nav.iloc[0], pd.DataFrame(hold_rows)


def first_trading_days_by_quarter(calendar: pd.DatetimeIndex) -> set[pd.Timestamp]:
    data = pd.Series(calendar, index=calendar)
    first_by_quarter = data.groupby(data.index.to_period("Q")).min()
    return set(first_by_quarter.iloc[1:])


def previous_trading_day(calendar: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | None:
    loc = calendar.get_loc(date)
    if isinstance(loc, slice) or isinstance(loc, pd.Series):
        raise ValueError("Calendar index must be unique")
    if loc == 0:
        return None
    return calendar[loc - 1]


def rank_em(prices: pd.DataFrame, signal_date: pd.Timestamp) -> list[str]:
    values = []
    for ticker in EM_ETFS:
        value = momentum_return(prices[ticker], signal_date)
        if not pd.isna(value):
            values.append((ticker, float(value)))
    values.sort(key=lambda item: (-item[1], item[0]))
    return [ticker for ticker, _ in values]


def momentum_return(series: pd.Series, signal_date: pd.Timestamp) -> float:
    history = series.loc[:signal_date].dropna()
    if len(history) <= LOOKBACK_DAYS:
        return float("nan")
    return float(history.iloc[-1] / history.iloc[-1 - LOOKBACK_DAYS] - 1.0)


def one_way_turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    if not previous:
        return 1.0
    keys = sorted(set(previous).union(current))
    return 0.5 * sum(abs(previous.get(key, 0.0) - current.get(key, 0.0)) for key in keys)


def build_variant_navs(components: pd.DataFrame, variants: dict[str, dict[str, float]]) -> pd.DataFrame:
    return pd.DataFrame({variant: build_rebalanced_nav(components, weights) for variant, weights in variants.items()})


def build_stress_windows(nav_frame: pd.DataFrame, momentum_nav: pd.Series, p08_proxy_nav: pd.Series) -> pd.DataFrame:
    rows = []
    for window_name, (start, end, measurement_type) in STRESS_WINDOWS.items():
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        for name in nav_frame.columns:
            source = nav_frame[name]
            row_measurement_type = measurement_type
            if measurement_type == "proxy_em_momentum_only" and name.startswith("J002"):
                source = momentum_nav
            elif measurement_type == "proxy_em_momentum_only" and name == "P08_IEF30":
                source = p08_proxy_nav
                row_measurement_type = "proxy_p08_us_core"
            elif measurement_type == "proxy_em_momentum_only":
                row_measurement_type = "exact_or_proxy_registered_components"
            window = source.loc[source.index.to_series().between(start_date, end_date)].dropna()
            if window.empty:
                continue
            row = metrics_for_nav(name, window_name, window / window.iloc[0])
            row["measurement_type"] = row_measurement_type
            rows.append(row)
    return pd.DataFrame(rows)


def build_turnover_by_year(hold_history: pd.DataFrame) -> pd.DataFrame:
    data = hold_history.copy()
    data["year"] = pd.to_datetime(data["execution_date"]).dt.year
    rows = []
    for variant, sleeve_weight in {"J002-A": 0.29, "J002-B": 0.50, "J002-C": 1.00}.items():
        grouped = data.groupby("year", sort=True)["turnover_one_way"].agg(["mean", "sum", "count"]).reset_index()
        grouped["variant"] = variant
        grouped["em_sleeve_weight"] = sleeve_weight
        grouped["quarterly_avg_turnover"] = grouped["mean"] * sleeve_weight
        grouped["annual_turnover"] = grouped["sum"] * sleeve_weight
        grouped["rebalance_count"] = grouped["count"].astype(int)
        rows.append(
            grouped[
                ["variant", "year", "em_sleeve_weight", "rebalance_count", "quarterly_avg_turnover", "annual_turnover"]
            ]
        )
    return pd.concat(rows, ignore_index=True)


def build_delta_vs_comparators(full_metrics: pd.DataFrame, variant: str) -> pd.DataFrame:
    target = full_metrics.loc[full_metrics["variant"].eq(variant)].iloc[0]
    rows = []
    for comparator in COMPARATOR_WEIGHTS:
        base = full_metrics.loc[full_metrics["variant"].eq(comparator)].iloc[0]
        rows.append(
            {
                "variant": variant,
                "comparator": comparator,
                "delta_total_return_pp": (target["total_return"] - base["total_return"]) * 100.0,
                "delta_cagr_pp": (target["cagr"] - base["cagr"]) * 100.0,
                "delta_sharpe": target["sharpe"] - base["sharpe"],
                "delta_mdd_pp": (target["max_drawdown"] - base["max_drawdown"]) * 100.0,
                "variant_cagr": target["cagr"],
                "comparator_cagr": base["cagr"],
                "variant_sharpe": target["sharpe"],
                "comparator_sharpe": base["sharpe"],
                "variant_mdd": target["max_drawdown"],
                "comparator_mdd": base["max_drawdown"],
            }
        )
    return pd.DataFrame(rows)


def build_overall_score_ranking(stress: pd.DataFrame) -> pd.DataFrame:
    j002 = stress.loc[stress["variant"].str.startswith("J002")].copy()
    baseline = stress.loc[stress["variant"].eq("P08_IEF30"), ["period", "total_return", "max_drawdown"]].rename(
        columns={"total_return": "baseline_total_return", "max_drawdown": "baseline_max_drawdown"}
    )
    rows = j002.merge(baseline, on="period", how="left", validate="many_to_one")
    rows["delta_return_pp"] = (rows["total_return"] - rows["baseline_total_return"]) * 100.0
    rows["delta_mdd_pp"] = (rows["max_drawdown"] - rows["baseline_max_drawdown"]) * 100.0
    rows["return_improved"] = rows["delta_return_pp"] > TOLERANCE
    rows["mdd_improved"] = rows["delta_mdd_pp"] > TOLERANCE
    scores = score_rows(rows, family="J002")

    previous = []
    for path in [
        ROOT / "reports/experiments/N005_multi_stress_comparison/overall_score_ranking.csv",
        ROOT / "reports/experiments/K001_static_sector_diversifier/overall_score_ranking.csv",
        ROOT / "reports/experiments/K002_one_shot_sector_momentum/overall_score_ranking.csv",
    ]:
        if path.exists():
            data = pd.read_csv(path).drop(columns=["overall_rank"], errors="ignore")
            if "family" not in data.columns:
                data["family"] = "N-family"
            previous.append(data)
    combined = pd.concat([*previous, scores], ignore_index=True, sort=False)
    combined = combined.drop_duplicates(subset=["variant", "family"], keep="last")
    combined = combined.sort_values(
        ["mdd_score_pp", "return_score_pp", "balanced_score_pp", "variant"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    combined.insert(0, "overall_rank", range(1, len(combined) + 1))
    return combined


def evaluate_promotion(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
) -> dict[str, object]:
    full_pass = better_on_return_mdd_sharpe(full_metrics, "J002-A", "P08_IEF30")
    stress_pass = all_stress_improved(stress, "J002-A", "P08_IEF30")
    spike_pass = better_on_return_mdd_sharpe(spike, "J002-A", "P08_IEF30")
    subperiod_pass = all(
        better_on_return_mdd_sharpe(subperiod.loc[subperiod["period"].eq(period)], "J002-A", "P08_IEF30")
        for period in ("2010_2017", "2018_2026")
    )
    return {
        "return_mdd_sharpe_all_better_than_p08": full_pass,
        "four_stress_all_improved": stress_pass,
        "no_2025_spike_dependency": spike_pass,
        "subperiod_all_superior": subperiod_pass,
        "promotion_pass": bool(full_pass and stress_pass and spike_pass and subperiod_pass),
        "direct_promote_p08_ief30": False,
        "role": "backlog_candidate_library",
    }


def build_metrics_payload(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    turnover: pd.DataFrame,
    delta: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
    overall: pd.DataFrame,
    promotion: dict[str, object],
) -> dict[str, object]:
    return {
        "experiment": "J002_one_shot_em_momentum",
        "purpose": "one-shot EM momentum under strict budget",
        "guardrails": {
            "lookback_grid": False,
            "top_k_grid": False,
            "weighting_optimization": False,
            "additional_em_etfs": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "role": "backlog_candidate_library",
        },
        "rule": {
            "universe": EM_ETFS,
            "lookback_trading_days": LOOKBACK_DAYS,
            "top_k": TOP_K,
            "weighting": "equal weight within EM momentum sleeve",
            "rebalance": "quarter end plus one trading day",
        },
        "variants": J002_VARIANTS,
        "full_history": records_for_json(full_metrics),
        "stress_windows": records_for_json(stress),
        "turnover_by_year": records_for_json(turnover),
        "delta_vs_baseline": records_for_json(delta),
        "subperiod_split": records_for_json(subperiod),
        "spike_exclusion": records_for_json(spike),
        "overall_score_ranking": records_for_json(overall),
        "j003_promotion_rule": promotion,
    }


def write_config() -> None:
    lines = [
        "experiment: J002_one_shot_em_momentum",
        "status: generated",
        "candidate_status: backlog_candidate_library",
        "base_candidate: P08_IEF30",
        "direct_promote_p08_ief30: false",
        "mode: one_shot_em_momentum",
        "search: none",
        "nav_basis: gross",
        "tax_model: none",
        "currency: KRW",
        "fx_policy: USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "rule:",
        f"  universe: [{', '.join(EM_ETFS)}]",
        f"  lookback_trading_days: {LOOKBACK_DAYS}",
        "  ranking: 12_month_return_krw",
        f"  top_k: {TOP_K}",
        "  top_k_weight: equal",
        "  rebalance: quarter_end_plus_1_trading_day",
        "  partial_inception: rank only ETFs with valid 252 trading day history",
        "variants:",
    ]
    for variant, weights in J002_VARIANTS.items():
        lines.append(f"  {variant}:")
        lines.extend(f"    {ticker}: {weight:.10f}" for ticker, weight in weights.items())
    lines.extend(
        [
            "comparators:",
            *[f"  - {name}" for name in COMPARATOR_WEIGHTS],
            "notes:",
            "  - H001 plus EWY/MCHI/VWO momentum may create Korea/EM double exposure.",
            "prohibited:",
            "  lookback_grid: true",
            "  top_k_grid: true",
            "  weighting_optimization: true",
            "  additional_em_etfs: true",
            "  external_network: true",
            "  engine_modification: true",
            "sources:",
            f"  etf_dir: {ETF_DIR.relative_to(ROOT)}",
            f"  usdk_rw_file: {USDKRW_PATH.relative_to(ROOT)}",
            f"  h001_equity_curve: {H001_EQUITY_PATH.relative_to(ROOT)}",
            "",
        ]
    )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    turnover: pd.DataFrame,
    hold_history: pd.DataFrame,
    delta: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
    overall: pd.DataFrame,
    promotion: dict[str, object],
) -> None:
    p08_delta = delta.loc[delta["comparator"].eq("P08_IEF30")].iloc[0]
    spy_delta = delta.loc[delta["comparator"].eq("SPY_100")].iloc[0]
    pass_text = "통과" if promotion["promotion_pass"] else "미통과"
    lines = [
        "# J002 One-shot EM Momentum",
        "",
        "Status: GENERATED BY `src.audit.j002_one_shot_em_momentum`",
        "",
        "## Scope",
        "",
        "- 단 하나의 규칙만 실행했다: 252 거래일 KRW momentum / Top 2 equal weight / quarterly.",
        "- Lookback grid / Top-K grid / weighting optimization / 추가 EM ETF는 실행하지 않았다.",
        "- `P08_IEF30` 직접 promote X. J002 결과는 backlog candidate library 전용이다.",
        "- Gross NAV, 비용 X, 로컬 USDKRW 보간 KRW 환산 기준이다.",
        "- H001와 EWY/EM momentum의 한국 double exposure 가능성을 허용하고 명시한다.",
        "",
        "## 3 J002 Variant 종합 Metric",
        "",
        table_for_report(full_metrics.loc[full_metrics["variant"].str.startswith("J002")], ["variant", "total_return", "cagr", "sharpe", "max_drawdown", "start_date", "end_date"]),
        "",
        "## P08_IEF30 / SPY / QQQ / K001-B / N001-B / N002-B 대비",
        "",
        f"- J002-A vs P08_IEF30: CAGR {p08_delta['delta_cagr_pp']:.4f}pp, Sharpe {p08_delta['delta_sharpe']:.4f}, MDD {p08_delta['delta_mdd_pp']:.4f}pp.",
        f"- J002-A vs SPY 100%: CAGR {spy_delta['delta_cagr_pp']:.4f}pp, Sharpe {spy_delta['delta_sharpe']:.4f}, MDD {spy_delta['delta_mdd_pp']:.4f}pp.",
        "",
        table_for_report(delta, ["variant", "comparator", "delta_cagr_pp", "delta_sharpe", "delta_mdd_pp", "variant_cagr", "comparator_cagr", "variant_mdd", "comparator_mdd"]),
        "",
        "## 4 Stress 결과",
        "",
        table_for_report(stress, ["variant", "period", "measurement_type", "total_return", "sharpe", "max_drawdown"]),
        "",
        "## Subperiod / 2025 Spike",
        "",
        table_for_report(subperiod.loc[subperiod["variant"].isin(["J002-A", "P08_IEF30"])], ["variant", "period", "cagr", "sharpe", "max_drawdown"]),
        "",
        table_for_report(spike.loc[spike["variant"].isin(["J002-A", "P08_IEF30"])], ["variant", "period", "cagr", "sharpe", "max_drawdown"]),
        "",
        "## J-family + K-family + N-family Ranking",
        "",
        table_for_report(overall, ["overall_rank", "variant", "family", "return_score_pp", "mdd_score_pp", "balanced_score_pp", "return_improved_count", "mdd_improved_count"]),
        "",
        "## EM Hold History 요약",
        "",
        f"- 가장 자주 hold 된 ETF top 3: {', '.join(most_common_holds(hold_history))}.",
        "",
        table_for_report(turnover.groupby("variant", as_index=False).agg(quarterly_avg_turnover=("quarterly_avg_turnover", "mean"), annual_turnover=("annual_turnover", "mean")), ["variant", "quarterly_avg_turnover", "annual_turnover"]),
        "",
        "## J003 Promotion Rule 평가",
        "",
        f"- Return + MDD + Sharpe 모두 P08_IEF30보다 명확히 좋음: {'통과' if promotion['return_mdd_sharpe_all_better_than_p08'] else '미통과'}",
        f"- 4 stress 모두 개선: {'통과' if promotion['four_stress_all_improved'] else '미통과'}",
        f"- 2025 spike 의존도 증가 없음: {'통과' if promotion['no_2025_spike_dependency'] else '미통과'}",
        f"- Subperiod 모두 우수: {'통과' if promotion['subperiod_all_superior'] else '미통과'}",
        f"- J003 promotion: {pass_text}",
        "",
        "## Verdict",
        "",
        "- J-family 전체 = backlog only unless all J003 conditions pass.",
        f"- J003 result: {pass_text}.",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def most_common_holds(hold_history: pd.DataFrame) -> list[str]:
    counts = pd.concat([hold_history["rank_1"], hold_history["rank_2"]]).value_counts()
    return [f"{ticker} ({int(count)}회)" for ticker, count in counts.head(3).items()]


if __name__ == "__main__":
    main()
