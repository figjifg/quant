from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ETF_DIR = Path("research_input_data/inputs/global_etf")
OUTPUT_DIR = Path("reports/experiments/I003_6_long_history")
REQUIRED_TICKERS = ("QQQ", "SPY", "IEF", "TLT", "GLD")

PORTFOLIOS: dict[str, dict[str, float]] = {
    "QQQ_buy_hold": {"QQQ": 1.0},
    "SPY_buy_hold": {"SPY": 1.0},
    "IEF_buy_hold": {"IEF": 1.0},
    "SPY50_QQQ50": {"SPY": 0.50, "QQQ": 0.50},
    "SPY40_QQQ30_IEF30_P08_IEF30_PROXY": {"SPY": 0.40, "QQQ": 0.30, "IEF": 0.30},
}

STRESS_WINDOWS = {
    "dot_com_2000_2002": ("2000-03-01", "2002-12-31"),
    "gfc_2008_2009": ("2008-01-01", "2009-12-31"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31"),
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_required_prices()
    component_nav = align_component_nav(prices)
    portfolio_nav = build_portfolio_nav(component_nav, PORTFOLIOS)
    returns = portfolio_nav.pct_change().fillna(0.0)

    metrics = build_metrics(portfolio_nav, returns, PORTFOLIOS)
    stress = build_stress_table(portfolio_nav)
    component_stress = build_component_stress(component_nav)

    portfolio_nav.reset_index().rename(columns={"index": "date"}).to_csv(
        OUTPUT_DIR / "portfolio_nav.csv", index=False
    )
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    component_stress.to_csv(OUTPUT_DIR / "component_stress_windows.csv", index=False)
    write_metrics_json(metrics, stress)
    write_report(metrics, stress, component_stress)


def load_required_prices() -> dict[str, pd.DataFrame]:
    missing = [ticker for ticker in REQUIRED_TICKERS if not (ETF_DIR / f"yf_{ticker}_long.csv").exists()]
    if missing:
        expected = [str(ETF_DIR / f"yf_{ticker}_long.csv") for ticker in missing]
        raise FileNotFoundError(
            "I003.6 long-history data is missing. Run scripts/host_data_collection.py on the host first. "
            f"Missing files: {expected}"
        )
    return {ticker: load_etf_prices(ticker) for ticker in REQUIRED_TICKERS}


def load_etf_prices(ticker: str) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}_long.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.rename(columns={"Date": "date", "Close": "close"})
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError(f"{path} has no valid rows")
    return data[["date", "close"]]


def align_component_nav(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    calendar = sorted(set().union(*(set(frame["date"]) for frame in prices.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    aligned = {}
    for ticker, frame in prices.items():
        series = frame.set_index("date")["close"].reindex(index).ffill()
        first_valid = series.first_valid_index()
        if first_valid is None:
            raise ValueError(f"{ticker} has no valid close observations")
        series = series.loc[first_valid:]
        aligned[ticker] = series / series.iloc[0]
    return pd.DataFrame(aligned).dropna(how="all")


def build_portfolio_nav(component_nav: pd.DataFrame, portfolios: dict[str, dict[str, float]]) -> pd.DataFrame:
    returns = component_nav.pct_change().fillna(0.0)
    nav = {}
    for name, weights in portfolios.items():
        missing = sorted(set(weights).difference(component_nav.columns))
        if missing:
            raise ValueError(f"{name} missing component NAV: {missing}")
        portfolio_returns = sum(returns[ticker].fillna(0.0) * weight for ticker, weight in weights.items())
        valid = component_nav[list(weights)].dropna().index
        series = (1.0 + portfolio_returns.loc[valid]).cumprod()
        nav[name] = series / series.iloc[0]
    return pd.DataFrame(nav)


def build_metrics(
    nav: pd.DataFrame,
    returns: pd.DataFrame,
    portfolios: dict[str, dict[str, float]],
) -> pd.DataFrame:
    rows = []
    for name in nav.columns:
        series = nav[name].dropna()
        candidate_returns = returns[name].reindex(series.index).fillna(0.0)
        rows.append(metrics_for_series(name, "full_history", series, candidate_returns, portfolios[name]))
    return pd.DataFrame(rows)


def build_stress_table(nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in nav.columns:
        series = nav[name].dropna()
        returns = series.pct_change().fillna(0.0)
        for stress_name, (start, end) in STRESS_WINDOWS.items():
            window_nav = series.loc[series.index.to_series().between(pd.Timestamp(start), pd.Timestamp(end))]
            if window_nav.empty:
                continue
            window_returns = returns.reindex(window_nav.index).fillna(0.0)
            rows.append(metrics_for_series(name, stress_name, window_nav, window_returns, PORTFOLIOS[name]))
    return pd.DataFrame(rows)


def build_component_stress(component_nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker in component_nav.columns:
        series = component_nav[ticker].dropna()
        returns = series.pct_change().fillna(0.0)
        for stress_name, (start, end) in STRESS_WINDOWS.items():
            window_nav = series.loc[series.index.to_series().between(pd.Timestamp(start), pd.Timestamp(end))]
            if window_nav.empty:
                continue
            window_returns = returns.reindex(window_nav.index).fillna(0.0)
            rows.append(metrics_for_series(ticker, stress_name, window_nav, window_returns, {ticker: 1.0}))
    return pd.DataFrame(rows)


def metrics_for_series(
    candidate: str,
    period: str,
    nav: pd.Series,
    returns: pd.Series,
    weights: dict[str, float],
) -> dict[str, object]:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1.0 / 365.25)
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    daily_std = float(returns.std())
    return {
        "candidate": candidate,
        "period": period,
        "weights": weights_to_text(weights),
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "n_observations": int(nav.shape[0]),
        "total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "annualized_volatility": daily_std * math.sqrt(252.0),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), daily_std),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
    }


def write_metrics_json(metrics: pd.DataFrame, stress: pd.DataFrame) -> None:
    payload = {
        "label": "US-core stress approximation; NOT full P08_IEF30 replication before H001 availability",
        "full_history": records_for_json(metrics),
        "stress_windows": records_for_json(stress),
    }
    (OUTPUT_DIR / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_report(metrics: pd.DataFrame, stress: pd.DataFrame, component_stress: pd.DataFrame) -> None:
    lines = [
        "# I003.6 Long-history Stress",
        "",
        "Status: GENERATED BY `src.audit.i003_6_long_history`",
        "",
        "## Label",
        "",
        "- Pre-2010 result = NOT full P08_IEF30 replication.",
        "- US-core stress approximation only; H001 is not reconstructed before 2010.",
        "",
        "## Full-history portfolios",
        "",
        table_for_report(metrics),
        "",
        "## Stress windows",
        "",
        table_for_report(stress),
        "",
        "## Component stress",
        "",
        table_for_report(component_stress),
        "",
        "## Metadata",
        "",
        f"- Source directory: `{ETF_DIR}`",
        "- Source files: `yf_QQQ_long.csv`, `yf_SPY_long.csv`, `yf_IEF_long.csv`, `yf_TLT_long.csv`, `yf_GLD_long.csv`",
        "- yfinance files are expected to use `auto_adjust=True`.",
        "- No strategy promotion or result interpretation is made by this audit.",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def table_for_report(data: pd.DataFrame) -> str:
    if data.empty:
        return "_No rows._"
    columns = [
        "candidate",
        "period",
        "start_date",
        "end_date",
        "cagr",
        "sharpe",
        "max_drawdown",
        "mdd_peak_date",
        "mdd_trough_date",
    ]
    available = [column for column in columns if column in data.columns]
    rows = data[available].copy()
    for column in ("cagr", "sharpe", "max_drawdown"):
        if column in rows.columns:
            rows[column] = rows[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.6f}")
    header = "| " + " | ".join(available) + " |"
    separator = "| " + " | ".join("---" for _ in available) + " |"
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
            if pd.isna(value):
                clean[key] = None
            else:
                clean[key] = value
        records.append(clean)
    return records


def weights_to_text(weights: dict[str, float]) -> str:
    return ";".join(f"{ticker}:{weight:.2f}" for ticker, weight in weights.items())


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0 or math.isnan(denominator):
        return None
    return numerator / denominator


if __name__ == "__main__":
    main()
