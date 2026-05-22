from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_PATH = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
OUTPUT_DIR = ROOT / "reports/experiments/J000_em_equity_baseline_diagnostic"

EM_ETFS = ["VWO", "EWY", "EWJ", "EWZ", "MCHI"]
SPY = "SPY"
STRESS_WINDOWS = {
    "dot_com_2000_2002": ("2000-01-01", "2002-12-31"),
    "gfc_2008_2009": ("2008-01-01", "2009-12-31"),
    "covid_2020_02_2020_03": ("2020-02-01", "2020-03-31"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31"),
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    daily = build_daily_nav()
    metrics = build_metrics(daily)
    correlation = build_correlation_matrix(daily)
    stress = build_stress_by_etf(daily)

    daily.to_csv(OUTPUT_DIR / "daily_nav_by_etf.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "metrics_by_etf.csv", index=False)
    correlation.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    stress.to_csv(OUTPUT_DIR / "stress_by_etf.csv", index=False)
    write_config()
    write_json(
        {
            "experiment": "J000_em_equity_baseline_diagnostic",
            "status": "generated",
            "role": "backlog_candidate_library",
            "universe": EM_ETFS,
            "metrics_by_etf": records_for_json(metrics),
            "stress_by_etf": records_for_json(stress),
        },
        OUTPUT_DIR / "metrics.json",
    )
    write_report(metrics, stress, correlation)


def build_daily_nav() -> pd.DataFrame:
    usdk = load_usdkrw()
    spy = load_price(SPY)
    frames = []
    for ticker in EM_ETFS:
        prices = load_price(ticker)
        frame = (
            prices.merge(usdk, on="date", how="left")
            .merge(spy.rename(columns={"close_usd": "spy_close_usd"}), on="date", how="left")
            .sort_values("date")
        )
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame["spy_close_usd"] = frame["spy_close_usd"].ffill()
        frame = frame.dropna(subset=["close_usd", "USDKRW", "spy_close_usd"]).copy()
        frame["close_krw"] = frame["close_usd"] * frame["USDKRW"]
        frame["nav"] = frame["close_krw"] / frame["close_krw"].iloc[0]
        frame["daily_return"] = frame["nav"].pct_change().fillna(0.0)
        frame["spy_close_krw"] = frame["spy_close_usd"] * frame["USDKRW"]
        frame["spy_nav_from_etf_start"] = frame["spy_close_krw"] / frame["spy_close_krw"].iloc[0]
        frame["spy_daily_return"] = frame["spy_nav_from_etf_start"].pct_change().fillna(0.0)
        frame.insert(1, "ticker", ticker)
        frames.append(
            frame[
                [
                    "date",
                    "ticker",
                    "close_usd",
                    "USDKRW",
                    "close_krw",
                    "nav",
                    "daily_return",
                    "spy_nav_from_etf_start",
                    "spy_daily_return",
                ]
            ]
        )
    return pd.concat(frames, ignore_index=True)


def load_price(ticker: str) -> pd.DataFrame:
    path = etf_path(ticker)
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
    if ticker in EM_ETFS:
        return ETF_DIR / f"yf_em_{ticker}.csv"
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


def build_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker, group in daily.groupby("ticker", sort=False):
        group = group.sort_values("date")
        rows.append(
            {
                "ticker": ticker,
                "start_date": group["date"].iloc[0].date().isoformat(),
                "end_date": group["date"].iloc[-1].date().isoformat(),
                "trading_days": int(len(group)),
                "cagr": cagr(group["nav"]),
                "sharpe": sharpe(group["daily_return"]),
                "annualized_volatility": float(group["daily_return"].std() * math.sqrt(252.0)),
                "max_drawdown": max_drawdown(group["nav"]),
                "spy_correlation": float(group["daily_return"].corr(group["spy_daily_return"])),
                "spy_relative_cagr_pp": (cagr(group["nav"]) - cagr(group["spy_nav_from_etf_start"])) * 100.0,
                "spy_relative_mdd_pp": (
                    max_drawdown(group["nav"]) - max_drawdown(group["spy_nav_from_etf_start"])
                )
                * 100.0,
            }
        )
    return pd.DataFrame(rows)


def build_correlation_matrix(daily: pd.DataFrame) -> pd.DataFrame:
    returns = daily.pivot(index="date", columns="ticker", values="daily_return")
    return returns.loc[:, EM_ETFS].corr()


def build_stress_by_etf(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stress_name, (start, end) in STRESS_WINDOWS.items():
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        for ticker, group in daily.groupby("ticker", sort=False):
            window = group.loc[group["date"].between(start_date, end_date)].sort_values("date")
            if window.empty:
                rows.append(
                    {
                        "stress_window": stress_name,
                        "ticker": ticker,
                        "start_date": "",
                        "end_date": "",
                        "trading_days": 0,
                        "total_return": None,
                        "max_drawdown": None,
                        "sharpe": None,
                        "status": "unavailable",
                    }
                )
                continue
            nav = window["nav"] / window["nav"].iloc[0]
            rows.append(
                {
                    "stress_window": stress_name,
                    "ticker": ticker,
                    "start_date": window["date"].iloc[0].date().isoformat(),
                    "end_date": window["date"].iloc[-1].date().isoformat(),
                    "trading_days": int(len(window)),
                    "total_return": float(nav.iloc[-1] / nav.iloc[0] - 1.0),
                    "max_drawdown": max_drawdown(nav),
                    "sharpe": sharpe(window["daily_return"]),
                    "status": "measured",
                }
            )
    return pd.DataFrame(rows)


def cagr(nav: pd.Series) -> float:
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1.0 / 365.25) if isinstance(nav.index, pd.DatetimeIndex) else len(nav) / 252.0
    return float(nav.iloc[-1] ** (1.0 / years) - 1.0)


def sharpe(daily_return: pd.Series) -> float | None:
    std = daily_return.std()
    if pd.isna(std) or std == 0.0:
        return None
    return float(daily_return.mean() / std * math.sqrt(252.0))


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def write_config() -> None:
    lines = [
        "experiment: J000_em_equity_baseline_diagnostic",
        "status: generated",
        "candidate_status: backlog_candidate_library",
        "mode: buy_hold_baseline_diagnostic",
        "currency: KRW",
        "fx_policy: USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "search: none",
        "direct_promote_p08_ief30: false",
        "universe:",
        *[f"  - {ticker}" for ticker in EM_ETFS],
        "stress_windows:",
        *[f"  {name}: {{start: {start}, end: {end}}}" for name, (start, end) in STRESS_WINDOWS.items()],
        "sources:",
        f"  etf_dir: {ETF_DIR.relative_to(ROOT)}",
        f"  usdk_rw_file: {USDKRW_PATH.relative_to(ROOT)}",
        "prohibited:",
        "  external_network: true",
        "  ranking_timing: true",
        "  parameter_grid: true",
        "",
    ]
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_report(metrics: pd.DataFrame, stress: pd.DataFrame, correlation: pd.DataFrame) -> None:
    best_cagr = metrics.sort_values("cagr", ascending=False).iloc[0]
    best_mdd = metrics.sort_values("max_drawdown", ascending=False).iloc[0]
    corr = correlation.copy()
    for ticker in corr.index:
        corr.loc[ticker, ticker] = pd.NA
    lines = [
        "# J000 EM Equity Baseline Diagnostic",
        "",
        "Status: GENERATED BY `src.audit.j000_em_equity_baseline_diagnostic`",
        "",
        "## Scope",
        "",
        "- Local ETF files only; no network refresh.",
        "- KRW buy-and-hold NAV uses local USDKRW interpolation.",
        "- Diagnostic only: no timing, ranking, or parameter grid.",
        "- J-family is a backlog candidate library and does not directly promote `P08_IEF30`.",
        "",
        "## Metrics Summary",
        "",
        f"- Highest full-sample CAGR: {best_cagr['ticker']} ({best_cagr['cagr']:.6f}).",
        f"- Lowest full-sample drawdown: {best_mdd['ticker']} ({best_mdd['max_drawdown']:.6f}).",
        f"- Average pairwise EM ETF daily-return correlation: {corr.stack().mean():.6f}.",
        "",
        table_for_report(metrics, ["ticker", "start_date", "end_date", "cagr", "sharpe", "max_drawdown", "spy_correlation"]),
        "",
        "## Stress Windows",
        "",
        table_for_report(stress, ["stress_window", "ticker", "start_date", "end_date", "trading_days", "total_return", "max_drawdown", "sharpe", "status"]),
        "",
        "## Notes",
        "",
        "- Dot-com rows are availability-dependent because several EM ETFs did not exist for the full 2000-2002 window.",
        "- EM is treated as a risk-asset sleeve, not a stress hedge.",
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


def records_for_json(data: pd.DataFrame) -> list[dict[str, object]]:
    records = []
    for record in data.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if pd.isna(value):
                clean[key] = None
            elif hasattr(value, "item"):
                clean[key] = value.item()
            else:
                clean[key] = value
        records.append(clean)
    return records


def write_json(payload: dict[str, object], path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
