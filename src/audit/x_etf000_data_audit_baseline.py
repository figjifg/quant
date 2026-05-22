from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_PATH = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
P08_IEF30_PATH = ROOT / "reports/experiments/I001_6_daily_nav_metrics/daily_nav_by_portfolio.csv"
OUTPUT_DIR = ROOT / "x_lab/x_etf/x_etf000_results"

UNIVERSE = ["SPY", "QQQ", "IWM", "IEF", "TLT", "SHY", "GLD", "UUP", "DBC", "VWO", "EWY", "EWJ", "EWZ", "MCHI"]
BENCHMARK_PORTFOLIOS: dict[str, dict[str, float]] = {
    "60_40_SPY_IEF": {"SPY": 0.60, "IEF": 0.40},
    "P08_PROXY_SPY29_QQQ21_IEF50": {"SPY": 0.29, "QQQ": 0.21, "IEF": 0.50},
}
STRESS_WINDOWS = {
    "gfc_proxy_2008_2009": ("2008-01-01", "2009-12-31"),
    "covid_2020_02_03": ("2020-02-01", "2020-03-31"),
    "year_2022": ("2022-01-01", "2022-12-31"),
}
COMPARISON_START = pd.Timestamp("2010-01-04")
COMPARISON_END = pd.Timestamp("2026-05-18")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    usdkrw = load_usdkrw()
    prices = {ticker: load_price(ticker) for ticker in UNIVERSE}
    availability = build_data_availability(prices)
    nav_usd = build_nav(prices, currency="USD")
    nav_krw = build_nav(prices, currency="KRW", usdkrw=usdkrw)

    buyhold = build_buyhold_metrics(nav_usd, nav_krw)
    benchmark_nav = build_benchmark_nav(nav_usd, nav_krw)
    benchmarks = build_benchmark_metrics(benchmark_nav)
    stress = build_stress_windows(nav_usd, nav_krw, benchmark_nav)
    verdict = build_verdict(availability, buyhold, benchmarks)

    availability.to_csv(OUTPUT_DIR / "data_availability.csv", index=False)
    buyhold.to_csv(OUTPUT_DIR / "buyhold_metrics.csv", index=False)
    benchmarks.to_csv(OUTPUT_DIR / "benchmark_portfolios.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    write_json(verdict, OUTPUT_DIR / "verdict.json")
    write_baseline_board(availability, buyhold, benchmarks, stress, verdict)


def load_price(ticker: str) -> pd.DataFrame:
    path = etf_path(ticker)
    if not path.exists():
        raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    price = pd.DataFrame(
        {
            "date": data["Date"],
            "close_usd": pd.to_numeric(data["Close"], errors="coerce"),
        }
    )
    return price.sort_values("date").reset_index(drop=True)


def etf_path(ticker: str) -> Path:
    if ticker in {"VWO", "EWY", "EWJ", "EWZ", "MCHI"}:
        return ETF_DIR / f"yf_em_{ticker}.csv"
    long_path = ETF_DIR / f"yf_{ticker}_long.csv"
    if long_path.exists():
        return long_path
    return ETF_DIR / f"yf_{ticker}.csv"


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_PATH, parse_dates=["observation_date"], na_values=["."])
    required = {"observation_date", "DEXKOUS"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{USDKRW_PATH} missing columns: {sorted(missing)}")
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return (
        data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})[["date", "usdkrw"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
        .reset_index(drop=True)
    )


def build_data_availability(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ticker, data in prices.items():
        valid = data.dropna(subset=["date", "close_usd"]).drop_duplicates(subset=["date"], keep="last")
        date_span = pd.date_range(valid["date"].min(), valid["date"].max(), freq="B") if not valid.empty else []
        missing_business_days = len(set(date_span).difference(set(valid["date"]))) if len(valid) else None
        rows.append(
            {
                "ticker": ticker,
                "source_file": str(etf_path(ticker).relative_to(ROOT)),
                "start_date": valid["date"].min().date().isoformat() if not valid.empty else "",
                "end_date": valid["date"].max().date().isoformat() if not valid.empty else "",
                "row_count": int(len(valid)),
                "duplicate_date_rows": int(data["date"].duplicated().sum()),
                "missing_close_rows": int(data["close_usd"].isna().sum()),
                "missing_business_days_between_start_end": missing_business_days,
                "adjusted_price_assumption": "Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption)",
                "status": "available" if not valid.empty and data["close_usd"].isna().sum() == 0 else "needs_review",
            }
        )
    return pd.DataFrame(rows)


def build_nav(
    prices: dict[str, pd.DataFrame],
    *,
    currency: str,
    usdkrw: pd.DataFrame | None = None,
) -> pd.DataFrame:
    series_by_ticker = {}
    for ticker, data in prices.items():
        valid = data.dropna(subset=["date", "close_usd"]).drop_duplicates(subset=["date"], keep="last")
        if currency == "KRW":
            if usdkrw is None:
                raise ValueError("USDKRW data is required for KRW NAV")
            valid = pd.merge_asof(valid.sort_values("date"), usdkrw.sort_values("date"), on="date", direction="backward")
            valid["close"] = valid["close_usd"] * valid["usdkrw"]
        elif currency == "USD":
            valid["close"] = valid["close_usd"]
        else:
            raise ValueError(f"Unsupported currency: {currency}")
        series_by_ticker[ticker] = (valid.set_index("date")["close"] / valid["close"].iloc[0]).rename(ticker)
    return pd.concat(series_by_ticker.values(), axis=1).sort_index()


def build_buyhold_metrics(nav_usd: pd.DataFrame, nav_krw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for currency, nav in [("USD", nav_usd), ("KRW", nav_krw)]:
        for ticker in UNIVERSE:
            rows.append(metrics_row(ticker, "ETF_BUYHOLD", currency, nav[ticker].dropna()))
            comparison = nav.loc[COMPARISON_START:COMPARISON_END, ticker].dropna()
            if not comparison.empty:
                rows.append(metrics_row(ticker, "ETF_BUYHOLD_2010_2026", currency, comparison))
    return pd.DataFrame(rows)


def build_benchmark_nav(nav_usd: pd.DataFrame, nav_krw: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    benchmark_nav = {}
    for currency, nav in [("USD", nav_usd), ("KRW", nav_krw)]:
        for portfolio, weights in BENCHMARK_PORTFOLIOS.items():
            common = nav[list(weights)].dropna()
            returns = common.pct_change().fillna(0.0)
            weighted_returns = sum(returns[ticker] * weight for ticker, weight in weights.items())
            benchmark_nav[(portfolio, currency)] = (1.0 + weighted_returns).cumprod()
    p08 = load_p08_ief30_nav()
    if p08 is not None:
        benchmark_nav[("P08_IEF30_AVAILABLE", "KRW")] = p08
    return benchmark_nav


def load_p08_ief30_nav() -> pd.Series | None:
    if not P08_IEF30_PATH.exists():
        return None
    data = pd.read_csv(P08_IEF30_PATH, parse_dates=["date"])
    required = {"date", "carrier", "net_value"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{P08_IEF30_PATH} missing columns: {sorted(missing)}")
    p08 = data.loc[data["carrier"] == "P08_SPY40_QQQ30_H00120_IEF10", ["date", "net_value"]].copy()
    if p08.empty:
        return None
    p08 = p08.dropna().sort_values("date").drop_duplicates(subset=["date"], keep="last")
    return (p08.set_index("date")["net_value"] / p08["net_value"].iloc[0]).rename("P08_IEF30_AVAILABLE")


def build_benchmark_metrics(benchmark_nav: dict[tuple[str, str], pd.Series]) -> pd.DataFrame:
    rows = []
    for (portfolio, currency), nav in benchmark_nav.items():
        rows.append(metrics_row(portfolio, "BENCHMARK_PORTFOLIO", currency, nav.dropna()))
        comparison = nav.loc[COMPARISON_START:COMPARISON_END].dropna()
        if not comparison.empty:
            rows.append(metrics_row(portfolio, "BENCHMARK_PORTFOLIO_2010_2026", currency, comparison))
    return pd.DataFrame(rows)


def build_stress_windows(
    nav_usd: pd.DataFrame,
    nav_krw: pd.DataFrame,
    benchmark_nav: dict[tuple[str, str], pd.Series],
) -> pd.DataFrame:
    rows = []
    for window, (start, end) in STRESS_WINDOWS.items():
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        for currency, nav_frame in [("USD", nav_usd), ("KRW", nav_krw)]:
            for ticker in UNIVERSE:
                rows.append(stress_row(window, ticker, "ETF_BUYHOLD", currency, nav_frame[ticker], start_date, end_date))
        for (portfolio, currency), nav in benchmark_nav.items():
            rows.append(stress_row(window, portfolio, "BENCHMARK_PORTFOLIO", currency, nav, start_date, end_date))
    return pd.DataFrame(rows)


def metrics_row(name: str, asset_type: str, currency: str, nav: pd.Series) -> dict:
    nav = nav.dropna()
    returns = nav.pct_change().fillna(0.0)
    return {
        "name": name,
        "asset_type": asset_type,
        "currency": currency,
        "start_date": nav.index.min().date().isoformat(),
        "end_date": nav.index.max().date().isoformat(),
        "trading_days": int(len(nav)),
        "total_return": float(nav.iloc[-1] / nav.iloc[0] - 1.0),
        "cagr": cagr(nav),
        "sharpe": sharpe(returns),
        "max_drawdown": max_drawdown(nav),
        "calmar": calmar(nav),
        "daily_volatility": float(returns.std()),
        "annualized_volatility": float(returns.std() * math.sqrt(252.0)),
    }


def stress_row(
    window: str,
    name: str,
    asset_type: str,
    currency: str,
    nav: pd.Series,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> dict:
    sliced = nav.loc[start_date:end_date].dropna()
    if sliced.empty:
        return {
            "stress_window": window,
            "name": name,
            "asset_type": asset_type,
            "currency": currency,
            "start_date": "",
            "end_date": "",
            "trading_days": 0,
            "total_return": None,
            "max_drawdown": None,
            "sharpe": None,
            "status": "unavailable",
        }
    norm = sliced / sliced.iloc[0]
    returns = norm.pct_change().fillna(0.0)
    return {
        "stress_window": window,
        "name": name,
        "asset_type": asset_type,
        "currency": currency,
        "start_date": norm.index.min().date().isoformat(),
        "end_date": norm.index.max().date().isoformat(),
        "trading_days": int(len(norm)),
        "total_return": float(norm.iloc[-1] / norm.iloc[0] - 1.0),
        "max_drawdown": max_drawdown(norm),
        "sharpe": sharpe(returns),
        "status": "measured",
    }


def cagr(nav: pd.Series) -> float:
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0.0:
        return 0.0
    return float((nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0)


def sharpe(returns: pd.Series) -> float | None:
    std = returns.std()
    if pd.isna(std) or std == 0.0:
        return None
    return float(returns.mean() / std * math.sqrt(252.0))


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def calmar(nav: pd.Series) -> float | None:
    mdd = abs(max_drawdown(nav))
    if mdd == 0.0:
        return None
    return float(cagr(nav) / mdd)


def build_verdict(availability: pd.DataFrame, buyhold: pd.DataFrame, benchmarks: pd.DataFrame) -> dict:
    unavailable = availability.loc[availability["status"] != "available", "ticker"].tolist()
    comparison_rows = buyhold.loc[
        (buyhold["asset_type"] == "ETF_BUYHOLD_2010_2026") & (buyhold["currency"] == "USD")
    ].copy()
    full_coverage = comparison_rows.loc[
        (comparison_rows["start_date"] <= COMPARISON_START.date().isoformat())
        & (comparison_rows["end_date"] >= COMPARISON_END.date().isoformat()),
        "name",
    ].tolist()
    missing_2010 = sorted(set(UNIVERSE).difference(full_coverage))
    status = "PASS" if not unavailable and not missing_2010 and not benchmarks.empty else "NEEDS_MORE_DATA"
    return {
        "experiment": "X-ETF000",
        "x_lab_quarantine": True,
        "status": status,
        "data_sufficient_for_x_etf001_004": status == "PASS",
        "universe": UNIVERSE,
        "unavailable_tickers": unavailable,
        "missing_2010_2026_coverage": missing_2010,
        "notes": [
            "Gross-only baseline; T-family taxable assumptions documented but not applied.",
            "No strategy optimization was run.",
            "P08_IEF30 comparison is included only when local daily NAV exists.",
        ],
    }


def write_baseline_board(
    availability: pd.DataFrame,
    buyhold: pd.DataFrame,
    benchmarks: pd.DataFrame,
    stress: pd.DataFrame,
    verdict: dict,
) -> None:
    usd_2010 = buyhold.loc[(buyhold["asset_type"] == "ETF_BUYHOLD_2010_2026") & (buyhold["currency"] == "USD")]
    krw_2010 = buyhold.loc[(buyhold["asset_type"] == "ETF_BUYHOLD_2010_2026") & (buyhold["currency"] == "KRW")]
    bench_2010 = benchmarks.loc[benchmarks["asset_type"] == "BENCHMARK_PORTFOLIO_2010_2026"]
    covid = stress.loc[(stress["stress_window"] == "covid_2020_02_03") & (stress["currency"] == "USD")]
    lines = [
        "# X-ETF000 Baseline Board",
        "",
        "X-Lab quarantine applies. This board is diagnostic only and does not affect `P08_IEF30`.",
        "",
        f"Verdict: `{verdict['status']}`",
        "",
        "## Data Availability",
        "",
        markdown_table(availability),
        "",
        "## Buy-and-Hold Metrics, USD 2010-2026",
        "",
        format_metric_table(usd_2010),
        "",
        "## Buy-and-Hold Metrics, KRW 2010-2026",
        "",
        format_metric_table(krw_2010),
        "",
        "## Benchmark Portfolios",
        "",
        format_metric_table(bench_2010),
        "",
        "## COVID Stress Window, USD",
        "",
        markdown_table(covid[["name", "asset_type", "total_return", "max_drawdown", "sharpe", "status"]]),
        "",
        "## Tax / Cost Note",
        "",
        "This baseline is gross only. Future taxable strategy tests should use the T-family default assumptions: HIFO, KRW 2.5M annual exemption, 22% capital-gains tax, 0.25% round-trip trading cost, 10 bps FX cost, and 15% dividend withholding.",
        "",
        "## Proceed Decision",
        "",
        "X-ETF001-004 may proceed only if the research director accepts this data audit and keeps all results inside X-Lab quarantine.",
    ]
    (OUTPUT_DIR / "baseline_board.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_metric_table(data: pd.DataFrame) -> str:
    if data.empty:
        return "No rows available."
    table = data[["name", "currency", "start_date", "end_date", "cagr", "sharpe", "max_drawdown", "calmar", "annualized_volatility"]].copy()
    for col in ["cagr", "sharpe", "max_drawdown", "calmar", "annualized_volatility"]:
        table[col] = table[col].map(lambda value: "" if pd.isna(value) else f"{float(value):.6f}")
    return markdown_table(table)


def markdown_table(data: pd.DataFrame) -> str:
    if data.empty:
        return "No rows available."
    text = data.copy()
    for column in text.columns:
        text[column] = text[column].map(format_markdown_cell)
    header = "| " + " | ".join(str(column) for column in text.columns) + " |"
    separator = "| " + " | ".join("---" for _ in text.columns) + " |"
    rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in text.itertuples(index=False, name=None)]
    return "\n".join([header, separator, *rows])


def format_markdown_cell(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value).replace("|", "\\|")


def write_json(payload: dict, path: Path) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
