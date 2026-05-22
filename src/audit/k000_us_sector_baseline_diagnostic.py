from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_CSV = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
OUTPUT_DIR = ROOT / "reports/experiments/K000_us_sector_baseline_diagnostic"

SECTORS = ["XLE", "XLF", "XLK", "XLV", "XLP", "XLU", "XLI", "XLY", "XLB", "XLRE", "XLC"]
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
    stress = build_stress_by_sector(daily)

    daily.to_csv(OUTPUT_DIR / "daily_nav_by_sector.csv", index=False)
    correlation.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    stress.to_csv(OUTPUT_DIR / "stress_by_sector.csv", index=False)
    write_config()
    write_metrics_json(metrics, stress)
    write_report(metrics, stress, correlation)


def build_daily_nav() -> pd.DataFrame:
    usdk = load_usdkrw()
    spy = load_price("SPY", ETF_DIR / "yf_SPY_long.csv")
    frames = []

    for sector in SECTORS:
        prices = load_price(sector, ETF_DIR / f"yf_sector_{sector}.csv")
        frame = (
            prices.merge(usdk, on="date", how="left")
            .merge(spy[["date", "close_usd"]].rename(columns={"close_usd": "spy_close_usd"}), on="date", how="left")
            .sort_values("date")
        )
        frame["USDKRW"] = frame["USDKRW"].ffill()
        frame["spy_close_usd"] = frame["spy_close_usd"].ffill()
        frame = frame.dropna(subset=["close_usd", "USDKRW", "spy_close_usd"]).copy()
        frame["close_krw"] = frame["close_usd"] * frame["USDKRW"]
        frame["nav"] = frame["close_krw"] / frame["close_krw"].iloc[0]
        frame["daily_return"] = frame["nav"].pct_change().fillna(0.0)
        frame["spy_close_krw"] = frame["spy_close_usd"] * frame["USDKRW"]
        frame["spy_nav_from_sector_start"] = frame["spy_close_krw"] / frame["spy_close_krw"].iloc[0]
        frame["spy_daily_return"] = frame["spy_nav_from_sector_start"].pct_change().fillna(0.0)
        frame.insert(1, "sector", sector)
        frames.append(
            frame[
                [
                    "date",
                    "sector",
                    "close_usd",
                    "USDKRW",
                    "close_krw",
                    "nav",
                    "daily_return",
                    "spy_nav_from_sector_start",
                    "spy_daily_return",
                ]
            ]
        )

    return pd.concat(frames, ignore_index=True)


def load_price(ticker: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
    data = pd.read_csv(path, parse_dates=["Date"])
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")
    return data.rename(columns={"Date": "date", "Close": "close_usd"})[["date", "close_usd"]].dropna()


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_CSV, parse_dates=["observation_date"], na_values=["."])
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return data.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]].dropna()


def build_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sector, group in daily.groupby("sector", sort=False):
        group = group.sort_values("date")
        sector_ret = group["daily_return"]
        spy_ret = group["spy_daily_return"]
        rows.append(
            {
                "sector": sector,
                "start_date": group["date"].iloc[0].strftime("%Y-%m-%d"),
                "end_date": group["date"].iloc[-1].strftime("%Y-%m-%d"),
                "trading_days": int(len(group)),
                "cagr": cagr(group["nav"]),
                "sharpe": sharpe(sector_ret),
                "daily_vol": float(sector_ret.std() * (252**0.5)),
                "max_drawdown": max_drawdown(group["nav"]),
                "spy_correlation": float(sector_ret.corr(spy_ret)),
                "spy_relative_cagr_pp": (cagr(group["nav"]) - cagr(group["spy_nav_from_sector_start"])) * 100.0,
                "spy_relative_mdd_pp": (max_drawdown(group["nav"]) - max_drawdown(group["spy_nav_from_sector_start"])) * 100.0,
            }
        )
    return pd.DataFrame(rows)


def build_correlation_matrix(daily: pd.DataFrame) -> pd.DataFrame:
    returns = daily.pivot(index="date", columns="sector", values="daily_return")
    return returns.loc[:, SECTORS].corr()


def build_stress_by_sector(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stress_name, (start, end) in STRESS_WINDOWS.items():
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        for sector, group in daily.groupby("sector", sort=False):
            window = group.loc[group["date"].between(start_date, end_date)].sort_values("date")
            if window.empty:
                rows.append(
                    {
                        "stress_window": stress_name,
                        "sector": sector,
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
            rows.append(
                {
                    "stress_window": stress_name,
                    "sector": sector,
                    "start_date": window["date"].iloc[0].strftime("%Y-%m-%d"),
                    "end_date": window["date"].iloc[-1].strftime("%Y-%m-%d"),
                    "trading_days": int(len(window)),
                    "total_return": float(window["nav"].iloc[-1] / window["nav"].iloc[0] - 1.0),
                    "max_drawdown": max_drawdown(window["nav"] / window["nav"].iloc[0]),
                    "sharpe": sharpe(window["daily_return"]),
                    "status": "measured",
                }
            )
    return pd.DataFrame(rows)


def cagr(nav: pd.Series) -> float:
    years = len(nav) / 252.0
    if years <= 0:
        return float("nan")
    return float(nav.iloc[-1] ** (1.0 / years) - 1.0)


def sharpe(daily_return: pd.Series) -> float:
    std = daily_return.std()
    if pd.isna(std) or std == 0:
        return float("nan")
    return float(daily_return.mean() / std * (252**0.5))


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def write_config() -> None:
    sector_lines = "\n".join(f"  - {sector}" for sector in SECTORS)
    stress_lines = "\n".join(
        f"  {name}: {{start: {start}, end: {end}}}" for name, (start, end) in STRESS_WINDOWS.items()
    )
    text = f"""experiment: K000_us_sector_baseline_diagnostic
status: generated
data_sources:
  sector_etf_dir: research_input_data/inputs/global_etf
  spy_file: research_input_data/inputs/global_etf/yf_SPY_long.csv
  usdk_rw_file: research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv
currency: KRW
fx_policy: local USDKRW forward-fill on ETF trading dates
universe:
{sector_lines}
stress_windows:
{stress_lines}
prohibited:
  - rotation_timing
  - momentum_ranking
  - parameter_grid
"""
    (OUTPUT_DIR / "config.yaml").write_text(text, encoding="utf-8")


def write_metrics_json(metrics: pd.DataFrame, stress: pd.DataFrame) -> None:
    payload = {
        "experiment": "K000_us_sector_baseline_diagnostic",
        "status": "generated",
        "universe": SECTORS,
        "metrics_by_sector": metrics.to_dict(orient="records"),
        "stress_by_sector": stress.to_dict(orient="records"),
    }
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_report(metrics: pd.DataFrame, stress: pd.DataFrame, correlation: pd.DataFrame) -> None:
    best_cagr = metrics.sort_values("cagr", ascending=False).iloc[0]
    lowest_mdd = metrics.sort_values("max_drawdown", ascending=False).iloc[0]
    off_diagonal = correlation.copy()
    for sector in off_diagonal.index:
        off_diagonal.loc[sector, sector] = pd.NA
    avg_corr = off_diagonal.stack()
    lines = [
        "# K000 US Sector Baseline Diagnostic",
        "",
        "Status: GENERATED BY `src.audit.k000_us_sector_baseline_diagnostic`",
        "",
        "## Scope",
        "",
        "- Local data only; no network refresh.",
        "- KRW conversion uses local USDKRW forward-fill on ETF trading dates.",
        "- Diagnostic only: no rotation timing, momentum ranking, or parameter grid.",
        "",
        "## Metrics Summary",
        "",
        f"- Highest full-sample CAGR: {best_cagr['sector']} ({best_cagr['cagr']:.6f}).",
        f"- Lowest full-sample drawdown: {lowest_mdd['sector']} ({lowest_mdd['max_drawdown']:.6f}).",
        f"- Average pairwise sector daily-return correlation: {avg_corr.mean():.6f}.",
        "",
        to_markdown_table(metrics),
        "",
        "## Stress Summary",
        "",
        to_markdown_table(stress),
        "",
        "## Outputs",
        "",
        "- config.yaml",
        "- daily_nav_by_sector.csv",
        "- correlation_matrix.csv",
        "- stress_by_sector.csv",
        "- metrics.json",
        "- report.md",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def to_markdown_table(frame: pd.DataFrame) -> str:
    headers = [str(column) for column in frame.columns]
    rows = [headers, ["---"] * len(headers)]
    for record in frame.to_dict(orient="records"):
        row = []
        for column in frame.columns:
            value = record[column]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, float):
                row.append(f"{value:.6f}")
            else:
                row.append(str(value))
        rows.append(row)
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


if __name__ == "__main__":
    main()
