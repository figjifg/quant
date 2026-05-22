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
OUTPUT_DIR = Path("reports/experiments/I001_5_portfolio_combinations")

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

METRIC_COLUMNS = [
    "carrier",
    "asset_type",
    "start_quarter",
    "end_quarter",
    "cumulative_net_total_return",
    "cagr",
    "quarterly_annualized_volatility",
    "sharpe",
    "max_drawdown",
    "positive_years",
    "n_quarters",
    "sharpe_rank",
    "mdd_rank",
    "cagr_rank",
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fx = load_usdkrw()
    etf_curves = {ticker: build_etf_curve(ticker, fx) for ticker in ETF_TICKERS}
    reference_curves = {
        "D013": load_reference_curve(D013_DIR / "equity_curve.csv", D013_EQUITY_COL, "D013"),
        "H001": load_reference_curve(H001_DIR / "equity_curve.csv", H001_EQUITY_COL, "H001"),
    }

    etf_returns = pd.concat([quarterly_returns(carrier, curve) for carrier, curve in etf_curves.items()], axis=1).sort_index()
    reference_returns = pd.concat(
        [quarterly_returns(carrier, curve) for carrier, curve in reference_curves.items()],
        axis=1,
    ).sort_index()
    reference_missing_quarters = missing_reference_quarters(etf_returns.index, reference_returns)
    reference_returns = reference_returns.reindex(etf_returns.index).fillna(0.0)
    component_returns = pd.concat([etf_returns, reference_returns], axis=1)

    portfolio_returns = build_portfolio_returns(component_returns)
    all_returns = pd.concat([component_returns, portfolio_returns], axis=1)
    all_curves = (1.0 + all_returns).cumprod()

    metrics = build_metrics_table(all_returns, all_curves)
    equity_curves = build_equity_curves_output(all_returns, all_curves)
    year_returns = build_year_returns(all_returns)
    correlation = all_returns[portfolio_returns.columns].corr()

    metrics.to_csv(OUTPUT_DIR / "portfolio_metrics.csv", index=False)
    equity_curves.to_csv(OUTPUT_DIR / "equity_curves_by_portfolio.csv", index=False)
    year_returns.to_csv(OUTPUT_DIR / "year_returns_by_portfolio.csv", index=False)
    correlation.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    write_report(
        metrics,
        year_returns,
        correlation,
        component_returns.index.min(),
        component_returns.index.max(),
        fx,
        reference_missing_quarters,
    )


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

    data["usd_return"] = data["close_usd"].pct_change().fillna(0.0)
    data["fx_return"] = data["usdkrw"].pct_change().fillna(0.0)
    data["daily_return"] = (1.0 + data["usd_return"]) * (1.0 + data["fx_return"]) - 1.0
    data["net_value"] = (1.0 + data["daily_return"]).cumprod()
    data["carrier"] = ticker
    return data[["date", "carrier", "daily_return", "net_value"]].reset_index(drop=True)


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
    data = data.dropna(subset=["net_value"]).sort_values("date").reset_index(drop=True)
    data["daily_return"] = data["net_value"].pct_change().fillna(0.0)
    data["carrier"] = carrier
    return data[["date", "carrier", "daily_return", "net_value"]]


def quarterly_returns(carrier: str, curve: pd.DataFrame) -> pd.Series:
    work = curve[["date", "daily_return"]].copy()
    work["quarter"] = work["date"].dt.to_period("Q").astype(str)
    returns = work.groupby("quarter")["daily_return"].apply(lambda values: float((1.0 + values).prod() - 1.0))
    returns.name = carrier
    return returns


def missing_reference_quarters(full_index: pd.Index, reference_returns: pd.DataFrame) -> dict[str, list[str]]:
    missing = {}
    for carrier in reference_returns.columns:
        carrier_missing = sorted(set(full_index).difference(reference_returns[carrier].dropna().index))
        missing[carrier] = carrier_missing
    return missing


def build_portfolio_returns(component_returns: pd.DataFrame) -> pd.DataFrame:
    rows: dict[str, pd.Series] = {}
    for portfolio, weights in PORTFOLIOS.items():
        total_weight = sum(weights.values())
        if not math.isclose(total_weight, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"{portfolio} weights sum to {total_weight}, expected 1.0")
        missing = sorted(set(weights).difference(component_returns.columns))
        if missing:
            raise ValueError(f"{portfolio} missing component returns: {missing}")
        weighted = sum(component_returns[component] * weight for component, weight in weights.items())
        rows[portfolio] = weighted.rename(portfolio)
    return pd.DataFrame(rows)


def build_metrics_table(returns: pd.DataFrame, curves: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for carrier in returns.columns:
        rows.append(metrics_for_carrier(carrier, returns[carrier], curves[carrier]))
    metrics = pd.DataFrame(rows)
    metrics["sharpe_rank"] = metrics["sharpe"].rank(method="min", ascending=False).astype(int)
    metrics["mdd_rank"] = metrics["max_drawdown"].rank(method="min", ascending=False).astype(int)
    metrics["cagr_rank"] = metrics["cagr"].rank(method="min", ascending=False).astype(int)
    order = {carrier: idx for idx, carrier in enumerate([*ETF_TICKERS, "D013", "H001", *PORTFOLIOS])}
    metrics["carrier_order"] = metrics["carrier"].map(order)
    return metrics.sort_values("carrier_order")[METRIC_COLUMNS].reset_index(drop=True)


def metrics_for_carrier(carrier: str, returns: pd.Series, nav: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] - 1.0)
    years = returns.index.to_series().str[:4].astype(int)
    yearly = returns.groupby(years).apply(lambda values: float((1.0 + values).prod() - 1.0))
    cagr = float((1.0 + total_return) ** (4.0 / len(returns)) - 1.0)
    volatility = float(math.sqrt(4.0) * returns.std())
    return {
        "carrier": carrier,
        "asset_type": asset_type_for(carrier),
        "start_quarter": str(returns.index[0]),
        "end_quarter": str(returns.index[-1]),
        "cumulative_net_total_return": total_return,
        "cagr": cagr,
        "quarterly_annualized_volatility": volatility,
        "sharpe": safe_divide(cagr, volatility),
        "max_drawdown": max_drawdown(nav),
        "positive_years": int((yearly > 0.0).sum()),
        "n_quarters": int(len(returns)),
    }


def asset_type_for(carrier: str) -> str:
    if carrier in ETF_TICKERS:
        return "ETF buy-hold"
    if carrier in {"D013", "H001"}:
        return "Korea strategy"
    return "Quarterly rebalanced portfolio"


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def build_equity_curves_output(returns: pd.DataFrame, curves: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for quarter in returns.index:
        for carrier in returns.columns:
            rows.append(
                {
                    "quarter": quarter,
                    "carrier": carrier,
                    "quarter_return": float(returns.loc[quarter, carrier]),
                    "net_value": float(curves.loc[quarter, carrier]),
                    "cumulative_net_total_return": float(curves.loc[quarter, carrier] - 1.0),
                }
            )
    return pd.DataFrame(rows)


def build_year_returns(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    years = returns.index.to_series().str[:4].astype(int)
    for carrier in returns.columns:
        grouped = returns[carrier].groupby(years).apply(lambda values: float((1.0 + values).prod() - 1.0))
        for year, value in grouped.items():
            rows.append({"carrier": carrier, "year": int(year), "net_total_return": value})
    return pd.DataFrame(rows).sort_values(["year", "carrier"]).reset_index(drop=True)


def write_report(
    metrics: pd.DataFrame,
    year_returns: pd.DataFrame,
    correlation: pd.DataFrame,
    start_quarter: str,
    end_quarter: str,
    fx: pd.DataFrame,
    reference_missing_quarters: dict[str, list[str]],
) -> None:
    portfolios = metrics.loc[metrics["asset_type"].eq("Quarterly rebalanced portfolio")].copy()
    comparison = comparison_summary(metrics)
    candidate = portfolios.sort_values(["sharpe", "max_drawdown", "cagr"], ascending=[False, False, False]).iloc[0]
    qqq = metrics.loc[metrics["carrier"].eq("P01_QQQ_100")].iloc[0]
    qqq_h001 = metrics.loc[metrics["carrier"].eq("P04_QQQ50_H00150")].iloc[0]
    spy = metrics.loc[metrics["carrier"].eq("P02_SPY_100")].iloc[0]
    spy_h001 = metrics.loc[metrics["carrier"].eq("P05_SPY50_H00150")].iloc[0]
    treasury_effect = treasury_summary(metrics)

    lines = [
        "# I001.5 — Portfolio Combination Baseline",
        "",
        "## Method",
        "",
        f"- Period: {start_quarter} to {end_quarter}; common quarterly return panel across ETFs, D013, and H001.",
        "- Rebalance: quarterly; portfolio quarter return is the pre-registered weighted sum of component KRW quarter returns.",
        "- ETF source: `research_input_data/inputs/global_etf/yf_*.csv`, KRW converted with `fred_dexkous_usdkrw.csv`.",
        "- H001 source: `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`.",
        "- D013 source: `reports/experiments/D013_d009_threshold_minus_0p2/equity_curve.csv`.",
        f"- Missing D013/H001 quarter policy: quarters with no source equity_curve rows are set to 0% return. Missing quarters: {format_missing_quarters(reference_missing_quarters)}.",
        f"- USDKRW latest observation used: {fx['date'].max().date()} at {fx['usdkrw'].iloc[-1]}.",
        "- D013/H001 strategy code and `engine.py` were not modified.",
        "",
        "## 8 Portfolio Metrics",
        "",
        markdown_table(
            portfolios,
            ["carrier", "cumulative_net_total_return", "cagr", "sharpe", "max_drawdown", "positive_years", "sharpe_rank", "mdd_rank", "cagr_rank"],
        ),
        "",
        "## 19-Row Ranking Table",
        "",
        markdown_table(
            metrics.sort_values(["sharpe_rank", "carrier"]),
            ["carrier", "asset_type", "cumulative_net_total_return", "cagr", "sharpe", "max_drawdown", "positive_years", "sharpe_rank", "mdd_rank", "cagr_rank"],
        ),
        "",
        "## H001 Addition Checks",
        "",
        markdown_table(comparison, ["comparison", "base", "with_h001", "base_sharpe", "with_h001_sharpe", "sharpe_delta", "base_mdd", "with_h001_mdd", "mdd_delta"]),
        "",
        "## QQQ vs QQQ + H001",
        "",
        f"- P01_QQQ_100: Sharpe {qqq['sharpe']:.6f}, MDD {qqq['max_drawdown']:.6f}, CAGR {qqq['cagr']:.6f}.",
        f"- P04_QQQ50_H00150: Sharpe {qqq_h001['sharpe']:.6f}, MDD {qqq_h001['max_drawdown']:.6f}, CAGR {qqq_h001['cagr']:.6f}.",
        f"- Delta: Sharpe {qqq_h001['sharpe'] - qqq['sharpe']:.6f}, MDD {qqq_h001['max_drawdown'] - qqq['max_drawdown']:.6f}.",
        "",
        "## SPY vs SPY + H001",
        "",
        f"- P02_SPY_100: Sharpe {spy['sharpe']:.6f}, MDD {spy['max_drawdown']:.6f}, CAGR {spy['cagr']:.6f}.",
        f"- P05_SPY50_H00150: Sharpe {spy_h001['sharpe']:.6f}, MDD {spy_h001['max_drawdown']:.6f}, CAGR {spy_h001['cagr']:.6f}.",
        f"- Delta: Sharpe {spy_h001['sharpe'] - spy['sharpe']:.6f}, MDD {spy_h001['max_drawdown'] - spy['max_drawdown']:.6f}.",
        "",
        "## Treasury Addition Effect",
        "",
        markdown_table(treasury_effect, ["comparison", "base", "with_ief", "base_sharpe", "with_ief_sharpe", "sharpe_delta", "base_mdd", "with_ief_mdd", "mdd_delta", "base_cagr", "with_ief_cagr", "cagr_delta"]),
        "",
        "## Verdict",
        "",
        f"- Best pre-registered portfolio by Sharpe: {candidate['carrier']} (Sharpe {candidate['sharpe']:.6f}, MDD {candidate['max_drawdown']:.6f}, CAGR {candidate['cagr']:.6f}).",
        f"- H001 effect on QQQ core: Sharpe delta {qqq_h001['sharpe'] - qqq['sharpe']:.6f}; MDD delta {qqq_h001['max_drawdown'] - qqq['max_drawdown']:.6f}.",
        f"- H001 effect on SPY core: Sharpe delta {spy_h001['sharpe'] - spy['sharpe']:.6f}; MDD delta {spy_h001['max_drawdown'] - spy['max_drawdown']:.6f}.",
        "- Recommendation: use the best Sharpe pre-registered combination as the final portfolio candidate for the next risk-controlled core step before adding a macro gate.",
        "- I002 recommendation: defer pure macro-gate work until I003-style risk-controlled core is frozen, because the I001.5 question is portfolio construction rather than signal timing.",
        "",
        "## Portfolio Correlation",
        "",
        markdown_table(correlation.reset_index().rename(columns={"index": "carrier"}), ["carrier", *correlation.columns.tolist()]),
        "",
        "## Year Returns",
        "",
        markdown_table(year_returns.pivot(index="year", columns="carrier", values="net_total_return").reset_index(), ["year", *sorted(year_returns["carrier"].unique())]),
        "",
        "## Files",
        "",
        "- portfolio_metrics.csv",
        "- equity_curves_by_portfolio.csv",
        "- year_returns_by_portfolio.csv",
        "- correlation_matrix.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def comparison_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("QQQ core", "P01_QQQ_100", "P04_QQQ50_H00150"),
        ("SPY core", "P02_SPY_100", "P05_SPY50_H00150"),
        ("QQQ/SPY core", "P03_QQQ50_SPY50", "P06_SPY35_QQQ35_H00130"),
    ]
    rows = []
    indexed = metrics.set_index("carrier")
    for label, base, with_h001 in pairs:
        base_row = indexed.loc[base]
        h001_row = indexed.loc[with_h001]
        rows.append(
            {
                "comparison": label,
                "base": base,
                "with_h001": with_h001,
                "base_sharpe": base_row["sharpe"],
                "with_h001_sharpe": h001_row["sharpe"],
                "sharpe_delta": h001_row["sharpe"] - base_row["sharpe"],
                "base_mdd": base_row["max_drawdown"],
                "with_h001_mdd": h001_row["max_drawdown"],
                "mdd_delta": h001_row["max_drawdown"] - base_row["max_drawdown"],
            }
        )
    return pd.DataFrame(rows)


def treasury_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("QQQ/H001 plus IEF", "P04_QQQ50_H00150", "P07_QQQ50_H00130_IEF20"),
        ("SPY/QQQ/H001 plus IEF", "P06_SPY35_QQQ35_H00130", "P08_SPY40_QQQ30_H00120_IEF10"),
    ]
    rows = []
    indexed = metrics.set_index("carrier")
    for label, base, with_ief in pairs:
        base_row = indexed.loc[base]
        ief_row = indexed.loc[with_ief]
        rows.append(
            {
                "comparison": label,
                "base": base,
                "with_ief": with_ief,
                "base_sharpe": base_row["sharpe"],
                "with_ief_sharpe": ief_row["sharpe"],
                "sharpe_delta": ief_row["sharpe"] - base_row["sharpe"],
                "base_mdd": base_row["max_drawdown"],
                "with_ief_mdd": ief_row["max_drawdown"],
                "mdd_delta": ief_row["max_drawdown"] - base_row["max_drawdown"],
                "base_cagr": base_row["cagr"],
                "with_ief_cagr": ief_row["cagr"],
                "cagr_delta": ief_row["cagr"] - base_row["cagr"],
            }
        )
    return pd.DataFrame(rows)


def format_missing_quarters(missing: dict[str, list[str]]) -> str:
    parts = []
    for carrier, quarters in missing.items():
        if quarters:
            parts.append(f"{carrier}={','.join(quarters)}")
        else:
            parts.append(f"{carrier}=none")
    return "; ".join(parts)


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


if __name__ == "__main__":
    main()
