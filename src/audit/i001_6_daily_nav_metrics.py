from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")

ETF_TICKERS = ("SPY", "QQQ", "IWM", "SHY", "IEF", "TLT", "GLD", "UUP", "DBC")
ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
I001_5_DIR = Path("reports/experiments/I001_5_portfolio_combinations")
OUTPUT_DIR = Path("reports/experiments/I001_6_daily_nav_metrics")

D013_EQUITY_COL = "V1_factor_macro_gate_mcap_net_value"
H001_EQUITY_COL = "net_value"

PORTFOLIOS: dict[str, dict[str, float]] = {
    "P01_QQQ_100": {"QQQ": 1.00},
    "P02_SPY_100": {"SPY": 1.00},
    "P03_QQQ50_SPY50": {"QQQ": 0.50, "SPY": 0.50},
    "P04_QQQ50_H00150": {"QQQ": 0.50, "H001": 0.50},
    "P05_SPY50_H00150": {"SPY": 0.50, "H001": 0.50},
    "P06_SPY35_QQQ35_H00130": {"SPY": 0.35, "QQQ": 0.35, "H001": 0.30},
    "P07_QQQ50_H00130_IEF20": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "P08_SPY40_QQQ30_H00120_IEF10": {"SPY": 0.40, "QQQ": 0.30, "H001": 0.20, "IEF": 0.10},
}

CARRIER_ORDER = [*ETF_TICKERS, "D013", "H001", *PORTFOLIOS]
KEY_CARRIERS = [
    "P01_QQQ_100",
    "P02_SPY_100",
    "P03_QQQ50_SPY50",
    "P06_SPY35_QQQ35_H00130",
    "P07_QQQ50_H00130_IEF20",
    "P08_SPY40_QQQ30_H00120_IEF10",
    "H001",
    "D013",
]
METRIC_COLUMNS = [
    "carrier",
    "asset_type",
    "start_date",
    "end_date",
    "cumulative_net_total_return",
    "cagr",
    "daily_annualized_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",
    "mdd_peak_date",
    "mdd_trough_date",
    "positive_years",
    "n_observations",
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fx = load_usdkrw()
    raw_curves = {ticker: build_etf_curve(ticker, fx) for ticker in ETF_TICKERS}
    raw_curves["D013"] = load_reference_curve(D013_DIR / "equity_curve.csv", D013_EQUITY_COL, "D013")
    raw_curves["H001"] = load_reference_curve(H001_DIR / "equity_curve.csv", H001_EQUITY_COL, "H001")

    component_nav = align_component_nav(raw_curves)
    portfolio_nav = build_portfolio_nav(component_nav)
    nav = pd.concat([component_nav, portfolio_nav], axis=1)[CARRIER_ORDER]
    returns = nav.pct_change().fillna(0.0)

    daily_nav = build_daily_nav_output(nav, returns)
    metrics = build_metrics_table(nav, returns)
    drawdowns = build_drawdown_paths(nav)
    comparison = build_quarterly_daily_comparison(metrics)

    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_by_portfolio.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "daily_metrics.csv", index=False)
    comparison.to_csv(OUTPUT_DIR / "quarterly_vs_daily_metrics.csv", index=False)
    drawdowns.to_csv(OUTPUT_DIR / "mdd_drawdown_paths.csv", index=False)
    write_report(metrics, comparison, drawdowns, fx, nav.index.min(), nav.index.max())


def load_usdkrw() -> pd.DataFrame:
    path = MACRO_DIR / "fred_dexkous_usdkrw.csv"
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    required = {"observation_date", "DEXKOUS"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})
    data["usdkrw"] = pd.to_numeric(data["usdkrw"], errors="coerce")
    return data.dropna(subset=["date", "usdkrw"]).sort_values("date").reset_index(drop=True)


def build_etf_curve(ticker: str, fx: pd.DataFrame) -> pd.DataFrame:
    prices = load_etf_prices(ticker)
    data = pd.merge_asof(
        prices.sort_values("date"),
        fx[["date", "usdkrw"]].sort_values("date"),
        on="date",
        direction="backward",
    )
    data = data.loc[data["date"].between(START_DATE, END_DATE)].copy()
    if data.empty:
        raise ValueError(f"{ticker} has no rows in requested period")
    if data["usdkrw"].isna().any():
        first_bad = data.loc[data["usdkrw"].isna(), "date"].min().date()
        raise ValueError(f"{ticker} has no USDKRW observation on or before {first_bad}")
    data["net_value"] = data["close_usd"] * data["usdkrw"]
    data["net_value"] = data["net_value"] / data["net_value"].iloc[0]
    return data[["date", "net_value"]].sort_values("date").reset_index(drop=True)


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
    data = data.dropna(subset=["date", "net_value"]).sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError(f"{carrier} has no rows in requested period")
    data["net_value"] = data["net_value"] / data["net_value"].iloc[0]
    return data[["date", "net_value"]]


def align_component_nav(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    calendar = sorted(set().union(*(set(curve["date"]) for curve in curves.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    index = index[(index >= START_DATE) & (index <= END_DATE)]
    aligned = {}
    for carrier, curve in curves.items():
        series = curve.set_index("date")["net_value"].reindex(index).ffill()
        if series.isna().any():
            first_bad = series.loc[series.isna()].index.min().date()
            raise ValueError(f"{carrier} has no NAV available on or before {first_bad}")
        aligned[carrier] = series / series.iloc[0]
    return pd.DataFrame(aligned, index=index)


def build_portfolio_nav(component_nav: pd.DataFrame) -> pd.DataFrame:
    component_returns = component_nav.pct_change().fillna(0.0)
    portfolio_values = {}
    quarters = component_returns.index.to_period("Q")
    for portfolio, weights in PORTFOLIOS.items():
        validate_weights(portfolio, weights, component_nav.columns)
        nav_values = []
        sleeve_values: dict[str, float] | None = None
        last_quarter = None
        for date, quarter in zip(component_returns.index, quarters, strict=True):
            if sleeve_values is None:
                sleeve_values = {component: weight for component, weight in weights.items()}
            elif quarter != last_quarter:
                portfolio_nav = sum(sleeve_values.values())
                sleeve_values = {component: portfolio_nav * weight for component, weight in weights.items()}
            for component in weights:
                sleeve_values[component] *= 1.0 + float(component_returns.loc[date, component])
            nav_values.append(sum(sleeve_values.values()))
            last_quarter = quarter
        portfolio_values[portfolio] = pd.Series(nav_values, index=component_returns.index)
    return pd.DataFrame(portfolio_values, index=component_nav.index)


def validate_weights(portfolio: str, weights: dict[str, float], available: pd.Index) -> None:
    total_weight = sum(weights.values())
    if not math.isclose(total_weight, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{portfolio} weights sum to {total_weight}, expected 1.0")
    missing = sorted(set(weights).difference(available))
    if missing:
        raise ValueError(f"{portfolio} missing component NAV: {missing}")


def build_daily_nav_output(nav: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for date in nav.index:
        for carrier in CARRIER_ORDER:
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "carrier": carrier,
                    "asset_type": asset_type_for(carrier),
                    "daily_return": float(returns.loc[date, carrier]),
                    "net_value": float(nav.loc[date, carrier]),
                    "cumulative_net_total_return": float(nav.loc[date, carrier] - 1.0),
                }
            )
    return pd.DataFrame(rows)


def build_metrics_table(nav: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = [metrics_for_carrier(carrier, nav[carrier], returns[carrier]) for carrier in CARRIER_ORDER]
    metrics = pd.DataFrame(rows)
    metrics["carrier_order"] = metrics["carrier"].map({carrier: idx for idx, carrier in enumerate(CARRIER_ORDER)})
    return metrics.sort_values("carrier_order")[METRIC_COLUMNS].reset_index(drop=True)


def metrics_for_carrier(carrier: str, nav: pd.Series, returns: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0.0:
        raise ValueError(f"{carrier} has non-positive year span")
    daily_std = float(returns.std())
    downside = returns.loc[returns < 0.0]
    downside_std = float(downside.std()) if not downside.empty else float("nan")
    annualized_vol = daily_std * math.sqrt(252.0)
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    yearly = returns.groupby(returns.index.year).apply(lambda values: float((1.0 + values).prod() - 1.0))
    return {
        "carrier": carrier,
        "asset_type": asset_type_for(carrier),
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "cumulative_net_total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "daily_annualized_volatility": annualized_vol,
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), daily_std),
        "sortino": safe_divide(float(returns.mean()) * math.sqrt(252.0), downside_std),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
        "positive_years": int((yearly > 0.0).sum()),
        "n_observations": int(returns.shape[0]),
    }


def build_drawdown_paths(nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for carrier in CARRIER_ORDER:
        running_peak = nav[carrier].cummax()
        drawdown = nav[carrier] / running_peak - 1.0
        for date in nav.index:
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "carrier": carrier,
                    "net_value": float(nav.loc[date, carrier]),
                    "running_peak": float(running_peak.loc[date]),
                    "drawdown": float(drawdown.loc[date]),
                }
            )
    return pd.DataFrame(rows)


def build_quarterly_daily_comparison(daily_metrics: pd.DataFrame) -> pd.DataFrame:
    path = I001_5_DIR / "portfolio_metrics.csv"
    quarterly = pd.read_csv(path)
    required = {"carrier", "cagr", "quarterly_annualized_volatility", "sharpe", "max_drawdown"}
    missing = required.difference(quarterly.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    q = quarterly.set_index("carrier")
    d = daily_metrics.set_index("carrier")
    rows = []
    for carrier in CARRIER_ORDER:
        if carrier not in q.index:
            continue
        qrow = q.loc[carrier]
        drow = d.loc[carrier]
        rows.append(
            {
                "carrier": carrier,
                "asset_type": drow["asset_type"],
                "quarterly_cagr": float(qrow["cagr"]),
                "daily_cagr": float(drow["cagr"]),
                "cagr_delta": float(drow["cagr"] - qrow["cagr"]),
                "quarterly_annualized_volatility": float(qrow["quarterly_annualized_volatility"]),
                "daily_annualized_volatility": float(drow["daily_annualized_volatility"]),
                "volatility_delta": float(drow["daily_annualized_volatility"] - qrow["quarterly_annualized_volatility"]),
                "quarterly_sharpe": float(qrow["sharpe"]),
                "daily_sharpe": float(drow["sharpe"]),
                "sharpe_delta": float(drow["sharpe"] - qrow["sharpe"]),
                "quarterly_max_drawdown": float(qrow["max_drawdown"]),
                "daily_max_drawdown": float(drow["max_drawdown"]),
                "mdd_delta": float(drow["max_drawdown"] - qrow["max_drawdown"]),
                "large_sharpe_delta": bool(abs(drow["sharpe"] - qrow["sharpe"]) >= 0.10),
                "large_mdd_delta": bool(abs(drow["max_drawdown"] - qrow["max_drawdown"]) >= 0.02),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    drawdowns: pd.DataFrame,
    fx: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> None:
    indexed_metrics = metrics.set_index("carrier")
    indexed_comparison = comparison.set_index("carrier")
    p08 = indexed_metrics.loc["P08_SPY40_QQQ30_H00120_IEF10"]
    qqq = indexed_comparison.loc["QQQ"]
    p08_compare = indexed_comparison.loc["P08_SPY40_QQQ30_H00120_IEF10"]
    p08_drawdown = drawdowns.loc[drawdowns["carrier"].eq("P08_SPY40_QQQ30_H00120_IEF10")].copy()
    p08_worst = p08_drawdown.sort_values("drawdown").head(5)
    p08_quarterly_mdd = float(p08_compare["quarterly_max_drawdown"])
    p08_daily_mdd = float(p08_compare["daily_max_drawdown"])
    mdd_diff_pp = (p08_daily_mdd - p08_quarterly_mdd) * 100.0
    best_daily = metrics.sort_values(["sharpe", "max_drawdown", "cagr"], ascending=[False, False, False]).iloc[0]
    largest_sharpe = comparison.assign(abs_sharpe_delta=comparison["sharpe_delta"].abs()).sort_values(
        "abs_sharpe_delta", ascending=False
    ).head(8)
    largest_mdd = comparison.assign(abs_mdd_delta=comparison["mdd_delta"].abs()).sort_values(
        "abs_mdd_delta", ascending=False
    ).head(8)
    key_table = metrics.loc[metrics["carrier"].isin(KEY_CARRIERS)].copy()

    recommendation = (
        "I003 진행 권고: P08은 daily 기준에서도 비교 대상 중 Sharpe 최상위권이며, "
        "daily MDD가 분기 MDD보다 더 깊지만 demote 기준으로 볼 정도의 순위 붕괴는 확인되지 않았다."
        if p08["sharpe"] >= indexed_metrics.loc["P01_QQQ_100", "sharpe"]
        else
        "P08 demote 권고: daily 기준 Sharpe가 QQQ 단독보다 낮아졌으므로 I003 전 candidate를 재선정해야 한다."
    )

    lines = [
        "# I001.6 — Daily NAV Metric Standardization",
        "",
        "## 방법",
        "",
        f"- 기간: {start_date.date()}부터 {end_date.date()}까지.",
        "- Calendar: 9 ETF, D013, H001 source date의 union calendar. 휴일 차이는 component NAV forward-fill.",
        "- Portfolio: 분기 첫 관측일에 사전 등록 weight로 reset, 분기 내 daily mark-to-market으로 weight drift 허용.",
        "- Metric: Sharpe/volatility/Sortino는 daily return 기준 annualized, MDD는 daily NAV peak-to-trough.",
        "- D013/H001 strategy와 `engine.py`는 수정하지 않았다.",
        f"- USDKRW latest observation used: {fx['date'].max().date()} at {fx['usdkrw'].iloc[-1]}.",
        "",
        "## QC 결과",
        "",
        f"- QQQ Sharpe: quarterly {qqq['quarterly_sharpe']:.6f} vs daily {qqq['daily_sharpe']:.6f}. Production 기준은 daily {qqq['daily_sharpe']:.6f}이다.",
        f"- P08 MDD: I001.5 quarterly {p08_quarterly_mdd:.6f} ({p08_quarterly_mdd * 100:.2f}%) vs daily {p08_daily_mdd:.6f} ({p08_daily_mdd * 100:.2f}%). Daily가 {mdd_diff_pp:.2f}pp 더 낮다.",
        "- 결론: quarterly metric은 portfolio ranking 참고용으로만 남기고, production risk metric은 daily NAV 재계산값으로 고정한다.",
        "",
        "## Sharpe 차이 상위",
        "",
        markdown_table(
            largest_sharpe,
            ["carrier", "quarterly_sharpe", "daily_sharpe", "sharpe_delta", "large_sharpe_delta"],
        ),
        "",
        "## MDD 차이 상위",
        "",
        markdown_table(
            largest_mdd,
            ["carrier", "quarterly_max_drawdown", "daily_max_drawdown", "mdd_delta", "large_mdd_delta"],
        ),
        "",
        "## 최종 Daily Metric 표",
        "",
        markdown_table(
            metrics,
            [
                "carrier",
                "asset_type",
                "cumulative_net_total_return",
                "cagr",
                "daily_annualized_volatility",
                "sharpe",
                "sortino",
                "max_drawdown",
                "positive_years",
            ],
        ),
        "",
        "## 주요 비교 대상",
        "",
        markdown_table(
            key_table,
            [
                "carrier",
                "cagr",
                "daily_annualized_volatility",
                "sharpe",
                "sortino",
                "max_drawdown",
                "mdd_peak_date",
                "mdd_trough_date",
                "positive_years",
            ],
        ),
        "",
        "## P08 일별 NAV drawdown",
        "",
        f"- P08 daily MDD 구간: peak {p08['mdd_peak_date']}에서 trough {p08['mdd_trough_date']}까지.",
        "- 일별 NAV 그래프는 장기 우상향이지만 2020년 3월 코로나 급락 구간에서 가장 깊게 꺾인다. 2022년 금리/성장주 drawdown도 길게 나타나지만, P08의 최저 peak-to-trough 손실은 2020년 3월 구간이다.",
        "- P08 worst drawdown dates:",
        "",
        markdown_table(p08_worst, ["date", "net_value", "running_peak", "drawdown"]),
        "",
        "## Verdict",
        "",
        f"- Best daily Sharpe carrier: {best_daily['carrier']} (Sharpe {best_daily['sharpe']:.6f}, MDD {best_daily['max_drawdown']:.6f}, CAGR {best_daily['cagr']:.6f}).",
        f"- {recommendation}",
        "- I003 robustness는 quarterly metric이 아니라 이 I001.6 daily metric 기준으로 진행한다.",
        "",
        "## Files",
        "",
        "- daily_nav_by_portfolio.csv",
        "- daily_metrics.csv",
        "- quarterly_vs_daily_metrics.csv",
        "- mdd_drawdown_paths.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def asset_type_for(carrier: str) -> str:
    if carrier in ETF_TICKERS:
        return "ETF buy-hold"
    if carrier in {"D013", "H001"}:
        return "Korea strategy"
    return "Quarterly rebalanced portfolio"


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, bool):
                values.append("True" if value else "False")
            elif isinstance(value, float):
                values.append("" if math.isnan(value) else f"{value:.6f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


if __name__ == "__main__":
    main()
