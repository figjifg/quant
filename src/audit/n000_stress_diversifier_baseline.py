from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ETF_DIR = Path("research_input_data/inputs/global_etf")
H001_EQUITY_PATH = Path("reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv")
OUTPUT_DIR = Path("reports/experiments/N000_stress_diversifier_baseline")

P08_IEF30_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
PRE_2010_PROXY_WEIGHTS = {"SPY": 0.29 / 0.80, "QQQ": 0.21 / 0.80, "IEF": 0.30 / 0.80}

STRESS_WINDOWS = {
    "dot_com_proxy_2002_07_2003_12": {
        "start": "2002-07-01",
        "end": "2003-12-31",
        "series": "p08_ief30_pre2010_us_core_proxy",
        "label": "proxy",
    },
    "gfc_proxy_2008_2009": {
        "start": "2008-01-01",
        "end": "2009-12-31",
        "series": "p08_ief30_pre2010_us_core_proxy",
        "label": "proxy",
    },
    "covid_2020_02_2020_03": {
        "start": "2020-02-01",
        "end": "2020-03-31",
        "series": "p08_ief30_exact",
        "label": "exact",
    },
    "rate_shock_2022": {
        "start": "2022-01-01",
        "end": "2022-12-31",
        "series": "p08_ief30_exact",
        "label": "exact",
    },
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    etf_nav = load_etf_nav(("SPY", "QQQ", "IEF"))
    h001 = load_h001_nav()

    proxy_nav = build_rebalanced_nav(etf_nav, PRE_2010_PROXY_WEIGHTS)
    exact_components = etf_nav.join(h001.rename("H001"), how="outer").ffill()
    exact_nav = build_rebalanced_nav(exact_components, P08_IEF30_WEIGHTS)

    daily_nav = pd.DataFrame(
        {
            "p08_ief30_exact": exact_nav,
            "p08_ief30_pre2010_us_core_proxy": proxy_nav,
        }
    )
    stress = build_stress_metrics(daily_nav)

    daily_nav.reset_index().rename(columns={"index": "date"}).to_csv(
        OUTPUT_DIR / "daily_nav.csv", index=False
    )
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    write_config()
    write_metrics_json(stress)
    write_report(stress)


def load_etf_nav(tickers: tuple[str, ...]) -> pd.DataFrame:
    frames = {}
    for ticker in tickers:
        path = ETF_DIR / f"yf_{ticker}_long.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing local ETF file: {path}")
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
    if not H001_EQUITY_PATH.exists():
        raise FileNotFoundError(f"Missing H001 equity curve: {H001_EQUITY_PATH}")
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


def build_rebalanced_nav(component_nav: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    missing = sorted(set(weights).difference(component_nav.columns))
    if missing:
        raise ValueError(f"Missing components for portfolio: {missing}")
    components = component_nav[list(weights)].dropna(how="all").ffill()
    components = components.dropna(subset=list(weights))
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

        sleeve_values = {
            ticker: value * (1.0 + float(row[ticker]))
            for ticker, value in sleeve_values.items()
        }
        values.append((date, sum(sleeve_values.values())))
        last_quarter = quarter

    nav = pd.Series(dict(values), name="nav").sort_index()
    return nav / nav.iloc[0]


def build_stress_metrics(daily_nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stress_name, spec in STRESS_WINDOWS.items():
        series = daily_nav[spec["series"]].dropna()
        window = series.loc[
            series.index.to_series().between(pd.Timestamp(spec["start"]), pd.Timestamp(spec["end"]))
        ].dropna()
        if window.empty:
            raise ValueError(f"No observations for stress window: {stress_name}")
        rows.append(metrics_for_window(stress_name, spec, window))
    return pd.DataFrame(rows)


def metrics_for_window(stress_name: str, spec: dict[str, str], nav: pd.Series) -> dict[str, object]:
    returns = nav.pct_change().fillna(0.0)
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    peak_value = nav.loc[peak_date]
    recovery = nav.loc[trough_date:]
    recovered = recovery.loc[recovery >= peak_value]
    recovery_date = None if recovered.empty else recovered.index[0].date().isoformat()
    daily_std = float(returns.std())
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1.0 / 365.25)
    return {
        "stress_window": stress_name,
        "measurement_type": spec["label"],
        "portfolio_series": spec["series"],
        "weights": weights_to_text(
            P08_IEF30_WEIGHTS if spec["series"] == "p08_ief30_exact" else PRE_2010_PROXY_WEIGHTS
        ),
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
        "mdd_recovery_date": recovery_date,
    }


def write_config() -> None:
    lines = [
        "experiment: N000_stress_diversifier_baseline",
        "status: generated",
        "candidate: P08_IEF30",
        "candidate_status: frozen",
        "mode: stress_response_only",
        "search: none",
        "promotion: none",
        "weights:",
        "  SPY: 0.29",
        "  QQQ: 0.21",
        "  H001: 0.20",
        "  IEF: 0.30",
        "pre_2010_proxy:",
        "  reason: H001 unavailable before 2010",
        "  weights_rescaled_to_us_core:",
        "    SPY: 0.3625",
        "    QQQ: 0.2625",
        "    IEF: 0.3750",
        "sources:",
        f"  etf_dir: {ETF_DIR}",
        f"  h001_equity_curve: {H001_EQUITY_PATH}",
        "",
    ]
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_metrics_json(stress: pd.DataFrame) -> None:
    payload = {
        "experiment": "N000_stress_diversifier_baseline",
        "candidate": "P08_IEF30",
        "candidate_status": "frozen",
        "purpose": "stress response measurement only",
        "guardrails": {
            "best_sharpe_search": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "n_family_role": "backlog_candidate_library",
        },
        "stress_windows": records_for_json(stress),
    }
    (OUTPUT_DIR / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_report(stress: pd.DataFrame) -> None:
    lines = [
        "# N000 Stress Diversifier Baseline",
        "",
        "Status: GENERATED BY `src.audit.n000_stress_diversifier_baseline`",
        "",
        "## Scope",
        "",
        "- Frozen `P08_IEF30`: SPY 29 / QQQ 21 / H001 20 / IEF 30.",
        "- Stress response only.",
        "- No best-Sharpe search.",
        "- No direct `P08_IEF30` modification or promotion.",
        "- N-family output is backlog candidate library only.",
        "",
        "## H001 Availability",
        "",
        "- 2010 onward windows use exact `P08_IEF30` with H001.",
        "- Pre-2010 windows are labeled proxy because H001 is unavailable.",
        "- Proxy weights rescale the non-H001 sleeves to 100%: SPY 36.25 / QQQ 26.25 / IEF 37.50.",
        "",
        "## Stress Metrics",
        "",
        table_for_report(stress),
        "",
        "## Metadata",
        "",
        f"- ETF source directory: `{ETF_DIR}`",
        f"- H001 source: `{H001_EQUITY_PATH}`",
        "- Local data only; no network access.",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def table_for_report(data: pd.DataFrame) -> str:
    columns = [
        "stress_window",
        "measurement_type",
        "start_date",
        "end_date",
        "total_return",
        "gross_sharpe",
        "daily_max_drawdown",
        "mdd_peak_date",
        "mdd_trough_date",
        "mdd_recovery_date",
    ]
    rows = data[columns].copy()
    for column in ("total_return", "gross_sharpe", "daily_max_drawdown"):
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


if __name__ == "__main__":
    main()
