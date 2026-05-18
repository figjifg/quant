from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ETF_TICKERS = ("SPY", "QQQ", "IWM", "SHY", "IEF", "TLT", "GLD", "UUP", "DBC")

START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")

ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
OUTPUT_DIR = Path("reports/experiments/I001_etf_buyhold_baseline")

D013_METRIC_KEY = "factor_macro_gate_mcap"
H001_METRIC_KEY = "d013_kr_short_rate_sleeve"
D013_EQUITY_COL = "V1_factor_macro_gate_mcap_net_value"
H001_EQUITY_COL = "net_value"

METRIC_COLUMNS = [
    "carrier",
    "asset_type",
    "start_date",
    "end_date",
    "cumulative_net_total_return",
    "annualized_return",
    "annualized_volatility",
    "sharpe",
    "max_drawdown",
    "positive_years",
    "n_observations",
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fx = load_usdkrw()
    etf_curves = {ticker: build_etf_curve(ticker, fx) for ticker in ETF_TICKERS}
    d013_curve = load_reference_curve(D013_DIR / "equity_curve.csv", D013_EQUITY_COL, "D013")
    h001_curve = load_reference_curve(H001_DIR / "equity_curve.csv", H001_EQUITY_COL, "H001")

    all_curves = {**etf_curves, "D013": d013_curve, "H001": h001_curve}
    d013_metrics = load_json_metrics(D013_DIR / "metrics.json")[D013_METRIC_KEY]
    h001_metrics = load_json_metrics(H001_DIR / "metrics.json")[H001_METRIC_KEY]

    metrics = build_metrics_table(etf_curves, d013_metrics, h001_metrics)
    year_returns = build_year_returns(etf_curves, d013_metrics, h001_metrics)
    equity_curves = build_quarterly_equity_curves(all_curves)
    mdd = build_mdd_attribution(all_curves)

    metrics.to_csv(OUTPUT_DIR / "baseline_metrics.csv", index=False)
    equity_curves.to_csv(OUTPUT_DIR / "equity_curves.csv", index=False)
    mdd.to_csv(OUTPUT_DIR / "mdd_attribution.csv", index=False)
    year_returns.to_csv(OUTPUT_DIR / "year_returns.csv", index=False)
    write_report(metrics, mdd, year_returns, fx)
    write_questions_if_needed(fx)


def load_usdkrw() -> pd.DataFrame:
    path = MACRO_DIR / "fred_dexkous_usdkrw.csv"
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    required = {"observation_date", "DEXKOUS"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdk_rw"})
    data["usdk_rw"] = pd.to_numeric(data["usdk_rw"], errors="coerce")
    return data.dropna(subset=["date", "usdk_rw"]).sort_values("date").reset_index(drop=True)


def build_etf_curve(ticker: str, fx: pd.DataFrame) -> pd.DataFrame:
    prices = load_etf_prices(ticker)
    data = pd.merge_asof(
        prices.sort_values("date"),
        fx[["date", "usdk_rw"]].sort_values("date"),
        on="date",
        direction="backward",
    )
    data = data.loc[data["date"].between(START_DATE, END_DATE)].copy()
    if data.empty:
        raise ValueError(f"{ticker} has no data in {START_DATE.date()} to {END_DATE.date()}")
    if data["usdk_rw"].isna().any():
        first_bad = data.loc[data["usdk_rw"].isna(), "date"].min().date()
        raise ValueError(f"{ticker} has no USDKRW observation on or before {first_bad}")

    data["usd_return"] = data["close_usd"].pct_change().fillna(0.0)
    data["usdk_rw_return"] = data["usdk_rw"].pct_change().fillna(0.0)
    data["daily_return"] = (1.0 + data["usd_return"]) * (1.0 + data["usdk_rw_return"]) - 1.0
    data["net_value"] = (1.0 + data["daily_return"]).cumprod()
    data["carrier"] = ticker
    data["fx_observation_date"] = data["date"].where(data["date"].isin(set(fx["date"])))
    data["fx_observation_date"] = data["fx_observation_date"].ffill()
    return data[
        [
            "date",
            "carrier",
            "close_usd",
            "usdk_rw",
            "usd_return",
            "usdk_rw_return",
            "daily_return",
            "net_value",
            "fx_observation_date",
        ]
    ].reset_index(drop=True)


def load_etf_prices(ticker: str) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.rename(columns={"Date": "date", "Close": "close_usd"})
    data["close_usd"] = pd.to_numeric(data["close_usd"], errors="coerce")
    return data.dropna(subset=["date", "close_usd"]).sort_values("date").reset_index(drop=True)


def load_reference_curve(path: Path, value_col: str, carrier: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"])
    required = {"date", value_col}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", value_col]].copy()
    data["net_value"] = pd.to_numeric(data[value_col], errors="coerce")
    data["carrier"] = carrier
    data["daily_return"] = data["net_value"].pct_change().fillna(0.0)
    return data.dropna(subset=["net_value"])[["date", "carrier", "daily_return", "net_value"]].reset_index(drop=True)


def load_json_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_metrics_table(
    etf_curves: dict[str, pd.DataFrame],
    d013_metrics: dict,
    h001_metrics: dict,
) -> pd.DataFrame:
    rows = [metrics_for_curve(ticker, curve, "ETF buy-hold") for ticker, curve in etf_curves.items()]
    rows.append(metrics_from_reference("D013", d013_metrics, D013_DIR / "equity_curve.csv"))
    rows.append(metrics_from_reference("H001", h001_metrics, H001_DIR / "equity_curve.csv"))
    frame = pd.DataFrame(rows, columns=METRIC_COLUMNS)
    frame["carrier_order"] = frame["carrier"].map({ticker: idx for idx, ticker in enumerate(ETF_TICKERS)} | {"D013": 9, "H001": 10})
    return frame.sort_values("carrier_order").drop(columns=["carrier_order"]).reset_index(drop=True)


def metrics_for_curve(carrier: str, curve: pd.DataFrame, asset_type: str) -> dict:
    nav = curve["net_value"]
    returns = curve["daily_return"]
    yearly = yearly_returns_from_curve(curve)
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    annualized_vol = annualized_volatility(nav)
    annualized_ret = annualized_return(total_return, len(curve))
    return {
        "carrier": carrier,
        "asset_type": asset_type,
        "start_date": curve["date"].iloc[0].date().isoformat(),
        "end_date": curve["date"].iloc[-1].date().isoformat(),
        "cumulative_net_total_return": total_return,
        "annualized_return": annualized_ret,
        "annualized_volatility": annualized_vol,
        "sharpe": safe_divide(annualized_ret, annualized_vol),
        "max_drawdown": max_drawdown(nav),
        "positive_years": int(sum(value > 0.0 for value in yearly.values())),
        "n_observations": int(returns.shape[0]),
    }


def metrics_from_reference(carrier: str, metrics: dict, equity_path: Path) -> dict:
    curve = pd.read_csv(equity_path, parse_dates=["date"])
    curve = curve.loc[curve["date"].between(START_DATE, END_DATE)]
    return {
        "carrier": carrier,
        "asset_type": "Korea strategy",
        "start_date": curve["date"].min().date().isoformat(),
        "end_date": curve["date"].max().date().isoformat(),
        "cumulative_net_total_return": metrics["cumulative_net_total_return"],
        "annualized_return": metrics["annualized_return"],
        "annualized_volatility": metrics.get("annualized_volatility"),
        "sharpe": metrics["sharpe"],
        "max_drawdown": metrics["max_drawdown"],
        "positive_years": metrics["positive_years"],
        "n_observations": int(curve.shape[0]),
    }


def build_year_returns(
    etf_curves: dict[str, pd.DataFrame],
    d013_metrics: dict,
    h001_metrics: dict,
) -> pd.DataFrame:
    rows = []
    for ticker, curve in etf_curves.items():
        yearly = yearly_returns_from_curve(curve)
        for year, value in yearly.items():
            rows.append({"carrier": ticker, "year": year, "net_total_return": value})
    for carrier, metrics in [("D013", d013_metrics), ("H001", h001_metrics)]:
        for year, value in metrics["yearly_net_total_return"].items():
            rows.append({"carrier": carrier, "year": int(year), "net_total_return": value})
    return pd.DataFrame(rows).sort_values(["year", "carrier"]).reset_index(drop=True)


def yearly_returns_from_curve(curve: pd.DataFrame) -> dict[int, float]:
    work = curve[["date", "daily_return"]].copy()
    work["year"] = work["date"].dt.year
    grouped = work.groupby("year")["daily_return"].apply(lambda values: float((1.0 + values).prod() - 1.0))
    return {int(year): float(value) for year, value in grouped.items()}


def build_quarterly_equity_curves(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for carrier, curve in curves.items():
        work = curve[["date", "net_value"]].copy()
        work["quarter"] = work["date"].dt.to_period("Q").astype(str)
        quarter_end = work.sort_values("date").groupby("quarter", as_index=False).tail(1)
        for row in quarter_end.itertuples(index=False):
            rows.append(
                {
                    "quarter": row.quarter,
                    "date": row.date.date().isoformat(),
                    "carrier": carrier,
                    "net_value": row.net_value,
                    "cumulative_net_total_return": row.net_value - 1.0,
                }
            )
    return pd.DataFrame(rows).sort_values(["quarter", "carrier"]).reset_index(drop=True)


def build_mdd_attribution(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for carrier, curve in curves.items():
        nav = curve["net_value"]
        running_peak = nav.cummax()
        drawdown = nav / running_peak - 1.0
        trough_idx = drawdown.idxmin()
        peak_idx = nav.loc[:trough_idx].idxmax()
        recovery_date = pd.NaT
        recovered = nav.loc[trough_idx:]
        recovered = recovered.loc[recovered >= nav.loc[peak_idx]]
        if not recovered.empty:
            recovery_date = curve.loc[recovered.index[0], "date"]
        rows.append(
            {
                "carrier": carrier,
                "mdd_peak_date": curve.loc[peak_idx, "date"].date().isoformat(),
                "mdd_trough_date": curve.loc[trough_idx, "date"].date().isoformat(),
                "mdd_recovery_date": "" if pd.isna(recovery_date) else recovery_date.date().isoformat(),
                "max_drawdown": float(drawdown.loc[trough_idx]),
                "peak_net_value": float(nav.loc[peak_idx]),
                "trough_net_value": float(nav.loc[trough_idx]),
            }
        )
    return pd.DataFrame(rows).sort_values("max_drawdown").reset_index(drop=True)


def annualized_return(total_return: float, periods: int) -> float:
    if periods == 0 or pd.isna(total_return):
        return float("nan")
    return float((1.0 + total_return) ** (252.0 / periods) - 1.0)


def annualized_volatility(nav: pd.Series) -> float:
    daily_log_returns = (nav / nav.shift(1)).apply(math.log).dropna()
    if daily_log_returns.empty:
        return float("nan")
    return float(math.sqrt(252.0) * daily_log_returns.std())


def max_drawdown(nav: pd.Series) -> float:
    if nav.empty:
        return float("nan")
    return float((nav / nav.cummax() - 1.0).min())


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def write_report(metrics: pd.DataFrame, mdd: pd.DataFrame, year_returns: pd.DataFrame, fx: pd.DataFrame) -> None:
    etf_metrics = metrics.loc[metrics["asset_type"].eq("ETF buy-hold")].copy()
    top_sharpe = etf_metrics.sort_values(["sharpe", "carrier"], ascending=[False, True]).iloc[0]
    lowest_mdd = etf_metrics.sort_values(["max_drawdown", "carrier"], ascending=[False, True]).iloc[0]
    top_cumulative = etf_metrics.sort_values(["cumulative_net_total_return", "carrier"], ascending=[False, True]).iloc[0]

    lines = [
        "# I001 — ETF Buy-and-Hold KRW Baseline",
        "",
        "## Method",
        "",
        f"- Period: {START_DATE.date()} buy, {END_DATE.date()} hold mark.",
        "- ETF source: research_input_data/inputs/global_etf/yf_*.csv, Yahoo Finance auto-adjusted Close.",
        "- FX source: research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv.",
        "- KRW conversion: daily_return_krw = (1 + ETF_USD_return) * (1 + USDKRW_return) - 1.",
        "- Cost policy: ignored by ticket definition; this is a diagnostic buy-and-hold baseline.",
        f"- USDKRW latest observation: {fx['date'].max().date()} at {fx['usdk_rw'].iloc[-1]}. ETF dates after that use the last available USDKRW observation.",
        "- D013/H001 strategy code and backtest engine were not modified.",
        "",
        "## ETF Buy-and-Hold Metrics",
        "",
        markdown_table(
            etf_metrics.sort_values("cumulative_net_total_return", ascending=False),
            [
                "carrier",
                "cumulative_net_total_return",
                "annualized_return",
                "annualized_volatility",
                "sharpe",
                "max_drawdown",
                "positive_years",
            ],
        ),
        "",
        "## ETF Leaders",
        "",
        f"- 최고 Sharpe ETF: {top_sharpe['carrier']} ({top_sharpe['sharpe']:.6f})",
        f"- 최저 MDD ETF: {lowest_mdd['carrier']} ({lowest_mdd['max_drawdown']:.6f})",
        f"- 최고 누적 ETF: {top_cumulative['carrier']} ({top_cumulative['cumulative_net_total_return']:.6f})",
        "",
        "## D013 / H001 Comparison",
        "",
        markdown_table(
            metrics.sort_values("cumulative_net_total_return", ascending=False),
            [
                "carrier",
                "cumulative_net_total_return",
                "annualized_return",
                "sharpe",
                "max_drawdown",
                "positive_years",
            ],
        ),
        "",
        "## MDD Attribution",
        "",
        markdown_table(mdd, ["carrier", "mdd_peak_date", "mdd_trough_date", "mdd_recovery_date", "max_drawdown"]),
        "",
        "## Year Returns",
        "",
        markdown_table(year_returns.pivot(index="year", columns="carrier", values="net_total_return").reset_index(), ["year", *sorted(year_returns["carrier"].unique())]),
        "",
        "## I002 Recommendation",
        "",
        "- PROCEED: ETF별 KRW buy-and-hold baseline과 D013/H001 비교표가 생성되었다.",
        "- Macro gate 적용은 I001의 ETF 단독 buy-and-hold를 frozen baseline으로 두고, I002에서는 D013의 quarterly macro gate signal_date에 맞춰 ETF exposure ON/OFF 또는 cash/short-rate sleeve 대체를 비교하는 방식이 적절하다.",
        "- Gate 판단은 신호일 기준 사용 가능 macro 값만 쓰고, ETF 체결/노출 변경은 다음 거래 가능일 이후로 밀어 timing leakage를 피해야 한다.",
        "",
        "## Files",
        "",
        "- baseline_metrics.csv",
        "- equity_curves.csv",
        "- mdd_attribution.csv",
        "- year_returns.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if column == "year" and not pd.isna(value):
                values.append(str(int(value)))
            elif isinstance(value, float):
                values.append("" if math.isnan(value) else f"{value:.6f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_questions_if_needed(fx: pd.DataFrame) -> None:
    if fx["date"].max() >= END_DATE:
        return
    path = Path("I001_codex_questions.md")
    path.write_text(
        "\n".join(
            [
                "# I001 Codex Questions",
                "",
                "## USDKRW endpoint gap",
                "",
                f"- ETF files run through {END_DATE.date()}, but `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv` ends at {fx['date'].max().date()}.",
                "- I001 outputs were generated with USDKRW carried forward from the last available FRED observation for ETF rows after that date.",
                "- For final research interpretation, should I001 be frozen with this convention, truncated to the common ETF/FX endpoint, or regenerated after a newer approved USDKRW input is added?",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
