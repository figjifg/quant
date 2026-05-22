from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
H001_EQUITY_PATH = Path("reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv")
N000_STRESS_PATH = Path("reports/experiments/N000_stress_diversifier_baseline/stress_windows.csv")

BASELINE_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
CORE_TICKERS = ("SPY", "QQQ", "IEF", "GLD", "SHY", "TLT", "DBC", "UUP")
RATE_COLUMN = "IR3TIB01KRM156N"

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


def run_experiment(
    *,
    experiment_id: str,
    slug: str,
    title: str,
    variants: dict[str, dict[str, float]],
    hypotheses: list[str],
    emphasis: list[str] | None = None,
) -> None:
    output_dir = Path(f"reports/experiments/{experiment_id}_{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)

    etf_nav = load_etf_nav(CORE_TICKERS)
    h001 = load_h001_nav()
    cash = build_kr_cash_nav(etf_nav.index.union(h001.index))
    components = etf_nav.join(h001.rename("H001"), how="outer").join(cash.rename("cash"), how="outer").ffill()

    daily_nav = {}
    stress_rows = []
    for variant, weights in variants.items():
        daily_nav[variant] = build_rebalanced_nav(components, weights)
        stress_rows.extend(build_variant_stress_rows(variant, weights, components))

    daily_nav_frame = pd.DataFrame(daily_nav).sort_index()
    stress = pd.DataFrame(stress_rows)
    baseline = load_n000_baseline()
    delta = build_delta_vs_baseline(stress, baseline)
    metrics = build_full_history_metrics(daily_nav_frame)

    daily_nav_frame.reset_index(names="date").to_csv(output_dir / "daily_nav.csv", index=False)
    stress.to_csv(output_dir / "stress_windows.csv", index=False)
    delta.to_csv(output_dir / "delta_vs_baseline.csv", index=False)
    write_config(output_dir, experiment_id, slug, variants, hypotheses)
    write_metrics_json(output_dir, experiment_id, variants, metrics, stress, delta)
    write_report(output_dir, title, experiment_id, variants, hypotheses, emphasis or [], metrics, stress, delta)


def load_etf_nav(tickers: tuple[str, ...]) -> pd.DataFrame:
    frames = {}
    for ticker in tickers:
        path = ETF_DIR / f"yf_{ticker}_long.csv"
        if not path.exists():
            path = ETF_DIR / f"yf_{ticker}.csv"
        if not path.exists():
            continue
        data = pd.read_csv(path, parse_dates=["Date"])
        required = {"Date", "Close"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
        close = pd.to_numeric(data["Close"], errors="coerce")
        frame = (
            pd.DataFrame({"date": data["Date"], ticker: close})
            .dropna(subset=["date", ticker])
            .sort_values("date")
            .drop_duplicates(subset=["date"], keep="last")
            .set_index("date")
        )
        frames[ticker] = frame[ticker] / frame[ticker].iloc[0]
    return pd.DataFrame(frames).sort_index()


def load_h001_nav() -> pd.Series:
    data = pd.read_csv(H001_EQUITY_PATH, parse_dates=["date"])
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


def build_full_history_metrics(daily_nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant, nav in daily_nav.items():
        nav = nav.dropna()
        rows.append(metrics_for_window("full_history_2010_2026", "exact", variant, {}, nav))
    return pd.DataFrame(rows)


def load_n000_baseline() -> pd.DataFrame:
    baseline = pd.read_csv(N000_STRESS_PATH)
    return baseline.loc[:, ["stress_window", "total_return", "daily_max_drawdown"]].rename(
        columns={
            "total_return": "baseline_total_return",
            "daily_max_drawdown": "baseline_daily_max_drawdown",
        }
    )


def build_delta_vs_baseline(stress: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    data = stress.merge(baseline, on="stress_window", how="left", validate="many_to_one")
    data["delta_total_return"] = data["total_return"] - data["baseline_total_return"]
    data["delta_daily_max_drawdown"] = data["daily_max_drawdown"] - data["baseline_daily_max_drawdown"]
    data["delta_return_pp"] = data["delta_total_return"] * 100.0
    data["delta_mdd_pp"] = data["delta_daily_max_drawdown"] * 100.0
    columns = [
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
    return data[columns]


def write_config(
    output_dir: Path,
    experiment_id: str,
    slug: str,
    variants: dict[str, dict[str, float]],
    hypotheses: list[str],
) -> None:
    lines = [
        f"experiment: {experiment_id}_{slug}",
        "status: generated",
        "mode: stress_response_only",
        "search: none",
        "promotion: none",
        "candidate_status: backlog_candidate_library",
        "rebalance: quarterly",
        "nav_basis: gross",
        "tax_model: none",
        "baseline: N000_stress_diversifier_baseline",
        "pre_2010_proxy:",
        "  rule: exclude H001 and sleeves without local observations in the stress window, then rescale remaining registered weights",
        "variants:",
    ]
    for variant, weights in variants.items():
        lines.append(f"  {variant}:")
        for ticker, weight in weights.items():
            lines.append(f"    {ticker}: {weight:.10f}")
    lines.extend(["hypotheses:"])
    lines.extend(f"  - {item}" for item in hypotheses)
    lines.extend(
        [
            "sources:",
            f"  etf_dir: {ETF_DIR}",
            f"  h001_equity_curve: {H001_EQUITY_PATH}",
            f"  kr_cash_rate: {MACRO_DIR / 'fred_kr_short_rate.csv'}",
            f"  n000_baseline: {N000_STRESS_PATH}",
            "guardrails:",
            "  best_sharpe_search: false",
            "  p08_ief30_modified: false",
            "  direct_promotion: false",
            "  n_family_role: backlog_candidate_library",
            "",
        ]
    )
    (output_dir / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_metrics_json(
    output_dir: Path,
    experiment_id: str,
    variants: dict[str, dict[str, float]],
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta: pd.DataFrame,
) -> None:
    payload = {
        "experiment": experiment_id,
        "purpose": "stress response measurement only",
        "guardrails": {
            "best_sharpe_search": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "n_family_role": "backlog_candidate_library",
        },
        "variants": variants,
        "full_history": records_for_json(full_metrics),
        "stress_windows": records_for_json(stress),
        "delta_vs_baseline": records_for_json(delta),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_report(
    output_dir: Path,
    title: str,
    experiment_id: str,
    variants: dict[str, dict[str, float]],
    hypotheses: list[str],
    emphasis: list[str],
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    delta: pd.DataFrame,
) -> None:
    best = delta.loc[delta["delta_daily_max_drawdown"].idxmax()]
    worst = delta.loc[delta["delta_daily_max_drawdown"].idxmin()]
    lines = [
        f"# {title}",
        "",
        f"Status: GENERATED BY `src.audit.{experiment_id.lower()}_*`",
        "",
        "## 범위",
        "",
        "- 사전 등록 weights만 실행했다.",
        "- 새 최고 Sharpe 검색은 수행하지 않았다.",
        "- `P08_IEF30` 직접 promote X: N-family 결과는 backlog candidate library 전용이다.",
        "- Gross NAV만 측정했다. HIFO / 250만 공제 / 양도세는 적용하지 않았다.",
        "- Quarterly rebalance를 사용했다.",
        "",
        "## 사전 등록 가설",
        "",
        *[f"- {item}" for item in hypotheses],
        "",
        "## Variants",
        "",
        table_for_weights(variants),
        "",
        "## Full History Metrics",
        "",
        table_for_report(full_metrics, ["variant", "start_date", "end_date", "total_return", "gross_sharpe", "daily_max_drawdown"]),
        "",
        "## Stress Windows",
        "",
        table_for_report(
            stress,
            [
                "variant",
                "stress_window",
                "measurement_type",
                "total_return",
                "gross_sharpe",
                "daily_max_drawdown",
                "proxy_excluded_sleeves",
            ],
        ),
        "",
        "## N000 대비 변화",
        "",
        table_for_report(
            delta,
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
        "## Stress 요약",
        "",
        f"- 최고 개선 stress: {best['variant']} / {best['stress_window']} / MDD {best['delta_mdd_pp']:.4f}pp, return {best['delta_return_pp']:.4f}pp.",
        f"- 최악 악화 stress: {worst['variant']} / {worst['stress_window']} / MDD {worst['delta_mdd_pp']:.4f}pp, return {worst['delta_return_pp']:.4f}pp.",
        *[f"- {item}" for item in emphasis],
        "",
        "## Proxy 주의",
        "",
        "- 2010 이전 stress는 proxy다. H001이 없고, 해당 window에 로컬 ETF 관측치가 없는 sleeve도 제외한 뒤 남은 등록 weights를 리스케일했다.",
        "- 따라서 proxy 행은 stress response 방향 비교용이며, 신규 sleeve의 실제 pre-inception 성과를 뜻하지 않는다.",
        "",
        "## 다음 단계",
        "",
        "- N005 multi-stress 종합 비교에서 N001-N004를 한 표로 비교할 것을 권고한다.",
        "",
    ]
    (output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def table_for_weights(variants: dict[str, dict[str, float]]) -> str:
    tickers = sorted({ticker for weights in variants.values() for ticker in weights})
    rows = []
    for variant, weights in variants.items():
        rows.append({"variant": variant, **{ticker: weights.get(ticker, 0.0) for ticker in tickers}})
    return table_for_report(pd.DataFrame(rows), ["variant", *tickers])


def table_for_report(data: pd.DataFrame, columns: list[str]) -> str:
    rows = data[columns].copy()
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


def weights_to_text(weights: dict[str, float]) -> str:
    return ";".join(f"{ticker}:{weight:.4f}" for ticker, weight in weights.items())


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0 or math.isnan(denominator):
        return None
    return numerator / denominator
