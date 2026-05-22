from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit.i003_5_static_allocation_frontier import (
    H001_DIR,
    H001_EQUITY_COL,
    build_portfolio_nav_and_contributions,
    load_reference_curve,
)
from src.audit.q002_quality_only import END_DATE, ETF_DIR, ROOT, nav_metrics, slice_nav


REPORT_DIR = ROOT / "reports" / "experiments" / "Q006_6_factor_etf_proxy_benchmark"
Q002_DIR = ROOT / "reports" / "experiments" / "Q002_quality_only"
Q006_DIR = ROOT / "reports" / "experiments" / "Q006_qvsy_composite"
FACTOR_ETFS = ("QUAL", "COWZ", "SCHD", "VLUE", "MTUM")
CORE_ETFS = ("SPY", "QQQ", "IEF")
P08_IEF30 = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}


def main() -> int:
    parser = argparse.ArgumentParser(description="Q006.6 factor ETF proxy benchmark.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    run(args.report_dir)
    return 0


def run(report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    etf_curves = {ticker: load_usd_curve(ticker) for ticker in (*CORE_ETFS, *FACTOR_ETFS)}
    standalone = build_standalone_metrics(etf_curves)
    q_compare = build_q_vs_etf_comparison(etf_curves)
    p08_preview = build_p08_plus_etf_preview(etf_curves)

    write_config(report_dir / "config.yaml", etf_curves)
    standalone.to_csv(report_dir / "etf_standalone_metrics.csv", index=False)
    q_compare.to_csv(report_dir / "q_vs_etf_comparison.csv", index=False)
    p08_preview.to_csv(report_dir / "p08_plus_etf_preview.csv", index=False)
    write_report(report_dir / "report.md", standalone, q_compare, p08_preview)


def load_usd_curve(ticker: str) -> pd.DataFrame:
    prefix = "yf_factor_" if ticker in FACTOR_ETFS else "yf_"
    path = ETF_DIR / f"{prefix}{ticker}.csv"
    if not path.exists() and ticker in {"SPY", "QQQ", "IEF"}:
        path = ETF_DIR / f"yf_{ticker}_long.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    data = data.rename(columns={"Date": "date", "Close": "close"})
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna(subset=["date", "close"]).sort_values("date")
    data = data.loc[data["date"].le(pd.Timestamp(END_DATE)), ["date", "close"]].copy()
    data["nav"] = data["close"] / data["close"].iloc[0]
    return data[["date", "nav"]].reset_index(drop=True)


def build_standalone_metrics(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    spy = curves["SPY"]
    for ticker, curve in curves.items():
        metrics = nav_metrics(curve)
        spy_slice = align_navs({"strategy": curve, "spy": spy})
        spy_metrics = nav_metrics(spy_slice[["date", "spy"]].rename(columns={"spy": "nav"}))
        rows.append(
            {
                "ticker": ticker,
                "start_date": curve["date"].iloc[0].date().isoformat(),
                "end_date": curve["date"].iloc[-1].date().isoformat(),
                **metrics,
                "excess_cagr_vs_spy_same_period": metrics["cagr"] - spy_metrics["cagr"],
            }
        )
    common_start = max(curve["date"].iloc[0] for curve in curves.values())
    common_end = min(curve["date"].iloc[-1] for curve in curves.values())
    for ticker, curve in curves.items():
        sliced = normalize_between(curve, common_start, common_end)
        metrics = nav_metrics(sliced)
        spy_metrics = nav_metrics(normalize_between(spy, common_start, common_end))
        rows.append(
            {
                "ticker": f"{ticker}_common_all_factor_etf",
                "start_date": common_start.date().isoformat(),
                "end_date": common_end.date().isoformat(),
                **metrics,
                "excess_cagr_vs_spy_same_period": metrics["cagr"] - spy_metrics["cagr"],
            }
        )
    return pd.DataFrame(rows)


def build_q_vs_etf_comparison(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    q_curves = {
        "Q002": pd.read_csv(Q002_DIR / "portfolio_daily_nav.csv", parse_dates=["date"]),
        "Q006": pd.read_csv(Q006_DIR / "portfolio_daily_nav.csv", parse_dates=["date"]),
    }
    rows = []
    common_factor_start = max(curves[ticker]["date"].iloc[0] for ticker in FACTOR_ETFS)
    common_factor_end = min(curves[ticker]["date"].iloc[-1] for ticker in FACTOR_ETFS)
    for q_name, q_curve in q_curves.items():
        for etf in FACTOR_ETFS:
            start = max(q_curve["date"].iloc[0], curves[etf]["date"].iloc[0])
            end = min(q_curve["date"].iloc[-1], curves[etf]["date"].iloc[-1])
            rows.append(compare_pair(q_name, q_curve, etf, curves[etf], start, end, "etf_specific_common"))
        for etf in FACTOR_ETFS:
            rows.append(compare_pair(q_name, q_curve, etf, curves[etf], common_factor_start, common_factor_end, "all_factor_etf_common"))
    return pd.DataFrame(rows)


def compare_pair(
    q_name: str,
    q_curve: pd.DataFrame,
    etf: str,
    etf_curve: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    comparison_window: str,
) -> dict[str, object]:
    q_nav = normalize_between(q_curve, start, end)
    e_nav = normalize_between(etf_curve, start, end)
    q_metrics = nav_metrics(q_nav)
    e_metrics = nav_metrics(e_nav)
    cagr_delta = q_metrics["cagr"] - e_metrics["cagr"]
    sharpe_delta = q_metrics["sharpe"] - e_metrics["sharpe"]
    if cagr_delta > 0.01 and sharpe_delta > 0:
        verdict = "direct_q_wins"
    elif cagr_delta < -0.01 or sharpe_delta < -0.10:
        verdict = "etf_proxy_prefer"
    else:
        verdict = "similar_etf_practical_prefer"
    return {
        "q_strategy": q_name,
        "etf": etf,
        "comparison_window": comparison_window,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "q_cagr": q_metrics["cagr"],
        "q_sharpe": q_metrics["sharpe"],
        "q_mdd": q_metrics["mdd"],
        "etf_cagr": e_metrics["cagr"],
        "etf_sharpe": e_metrics["sharpe"],
        "etf_mdd": e_metrics["mdd"],
        "q_minus_etf_cagr": cagr_delta,
        "q_minus_etf_sharpe": sharpe_delta,
        "verdict": verdict,
    }


def build_p08_plus_etf_preview(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    h001 = load_reference_curve(H001_DIR / "equity_curve.csv", H001_EQUITY_COL, "H001").rename(columns={"net_value": "nav"})
    components = {ticker: curves[ticker].rename(columns={"nav": "net_value"}) for ticker in CORE_ETFS}
    components["H001"] = h001.rename(columns={"nav": "net_value"})
    rows = []
    for sleeve in ("BASELINE", *FACTOR_ETFS, "Q002", "Q006"):
        if sleeve == "BASELINE":
            weights = P08_IEF30.copy()
            component_nav = align_components(components, pd.Timestamp("2017-01-03"), pd.Timestamp(END_DATE))
        elif sleeve in FACTOR_ETFS:
            weights = P08_IEF30.copy()
            weights["SPY"] -= 0.10
            weights[sleeve] = 0.10
            local_components = {**components, sleeve: curves[sleeve].rename(columns={"nav": "net_value"})}
            component_nav = align_components(local_components, max(pd.Timestamp("2017-01-03"), curves[sleeve]["date"].iloc[0]), pd.Timestamp(END_DATE))
        else:
            weights = P08_IEF30.copy()
            weights["SPY"] -= 0.10
            weights[sleeve] = 0.10
            q_dir = Q002_DIR if sleeve == "Q002" else Q006_DIR
            q_curve = pd.read_csv(q_dir / "portfolio_daily_nav.csv", parse_dates=["date"]).rename(columns={"nav": "net_value"})
            local_components = {**components, sleeve: q_curve}
            component_nav = align_components(local_components, max(pd.Timestamp("2017-01-03"), q_curve["date"].iloc[0]), pd.Timestamp(END_DATE))
        nav, _ = build_portfolio_nav_and_contributions(component_nav, {f"P08_IEF30_plus_{sleeve}": weights}, "quarterly")
        series = nav.iloc[:, 0]
        returns = series.pct_change().fillna(0.0)
        metrics = metrics_from_series(series, returns)
        rows.append({"sleeve": sleeve, "candidate": nav.columns[0], **metrics})
    out = pd.DataFrame(rows)
    baseline = out.loc[out["sleeve"].eq("BASELINE")].iloc[0]
    out["cagr_delta_vs_baseline"] = out["cagr"] - baseline["cagr"]
    out["sharpe_delta_vs_baseline"] = out["sharpe"] - baseline["sharpe"]
    out["mdd_delta_vs_baseline"] = out["mdd"] - baseline["mdd"]
    return out


def align_components(curves: dict[str, pd.DataFrame], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    calendar = sorted(set().union(*(set(curve["date"]) for curve in curves.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    index = index[(index >= start) & (index <= end)]
    aligned = {}
    for name, curve in curves.items():
        series = curve.set_index("date")["net_value"].reindex(index).ffill()
        if series.isna().any():
            index = index[index >= series.first_valid_index()]
            series = curve.set_index("date")["net_value"].reindex(index).ffill()
        aligned[name] = series / series.iloc[0]
    return pd.DataFrame(aligned, index=index).dropna()


def align_navs(named: dict[str, pd.DataFrame]) -> pd.DataFrame:
    start = max(df["date"].iloc[0] for df in named.values())
    end = min(df["date"].iloc[-1] for df in named.values())
    out = {"date": None}
    pieces = []
    for name, df in named.items():
        sliced = normalize_between(df, start, end).rename(columns={"nav": name})
        pieces.append(sliced)
    merged = pieces[0]
    for piece in pieces[1:]:
        merged = merged.merge(piece, on="date", how="inner")
    return merged


def normalize_between(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    work = df.loc[df["date"].between(start, end), ["date", "nav"]].copy()
    if work.empty:
        raise ValueError(f"no rows between {start.date()} and {end.date()}")
    work["nav"] = work["nav"] / work["nav"].iloc[0]
    return work.reset_index(drop=True)


def metrics_from_series(nav: pd.Series, returns: pd.Series) -> dict[str, object]:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    std = float(returns.std())
    drawdown = nav / nav.cummax() - 1.0
    return {
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "sharpe": math.sqrt(252.0) * float(returns.mean()) / std if std else np.nan,
        "mdd": float(drawdown.min()),
        "n_observations": int(nav.shape[0]),
    }


def write_config(path: Path, curves: dict[str, pd.DataFrame]) -> None:
    starts = {ticker: curves[ticker]["date"].iloc[0].date().isoformat() for ticker in curves}
    path.write_text(
        f"""experiment: Q006_6_factor_etf_proxy_benchmark
currency: USD for standalone and direct Q comparison; P08 preview uses existing H001 NAV plus USD ETF/Q curves as gross diagnostic
factor_etfs: {list(FACTOR_ETFS)}
core_etfs: {list(CORE_ETFS)}
etf_start_dates: {starts}
p08_ief30_baseline_weights:
  SPY: 0.29
  QQQ: 0.21
  H001: 0.20
  IEF: 0.30
replacement_rule: subtract 10pct from SPY and add 10pct factor ETF or direct Q sleeve
limitations:
  - COWZ starts after 2014, so all-factor-ETF common window starts at the latest ETF inception
  - direct Q-family remains survivor-universe diagnostic and production X
  - P08 preview is gross allocation math, not a strategy/engine modification
""",
        encoding="utf-8",
    )


def write_report(path: Path, standalone: pd.DataFrame, q_compare: pd.DataFrame, p08: pd.DataFrame) -> None:
    common = standalone.loc[standalone["ticker"].str.endswith("_common_all_factor_etf")].copy()
    common["base_ticker"] = common["ticker"].str.replace("_common_all_factor_etf", "", regex=False)
    factor_common = common.loc[common["base_ticker"].isin(FACTOR_ETFS)].copy()
    best_common = factor_common.sort_values(["sharpe", "cagr"], ascending=False).iloc[0]
    direct_wins = (q_compare["verdict"].eq("direct_q_wins")).sum()
    etf_pref = (q_compare["verdict"].ne("direct_q_wins")).sum()
    best_p08 = p08.sort_values(["sharpe", "cagr"], ascending=False).iloc[0]
    verdict = "ETF proxy production prefer"
    if direct_wins > etf_pref:
        verdict = "direct Q-family 우위 가능성은 있으나 survivor-safe universe 전 production 불가"
    report = f"""# Q006.6 Factor ETF Proxy Benchmark

## Verdict

{verdict}. Survivorship-safe universe가 없으면 direct Q-family는 research diagnostic이고, production path는 ETF proxy가 우선이다.

## ETF Standalone

전체 factor ETF 공통 기간의 factor ETF 최상위 Sharpe는 {best_common['base_ticker']} ({best_common['sharpe']:.2f}, CAGR {best_common['cagr']:.2%})이다. COWZ 상장일 때문에 모든 factor ETF 공통 비교는 2014가 아니라 {best_common['start_date']} 이후로 제한된다. SPY/QQQ는 같은 표에 비교 기준으로만 포함했다.

## Direct Q vs ETF

- 비교 row 수: {len(q_compare)}
- direct_q_wins: {direct_wins}
- ETF 또는 실용성 우선 판정: {etf_pref}

ETF가 비슷한 경우 운용 가능성, survivor-safe exposure, 낮은 implementation risk 때문에 ETF proxy를 우선한다.

## P08_IEF30 Preview

| Sleeve | CAGR | Sharpe | MDD | Sharpe delta |
| --- | ---: | ---: | ---: | ---: |
"""
    for _, row in p08.iterrows():
        report += f"| {row['sleeve']} | {row['cagr']:.2%} | {row['sharpe']:.2f} | {row['mdd']:.2%} | {row['sharpe_delta_vs_baseline']:.2f} |\n"
    report += f"""
Best preview by Sharpe: {best_p08['sleeve']} ({best_p08['sharpe']:.2f}).

## Production Gate

Direct Q-family production gate: closed. ETF proxy path: open for Q008 framework, subject to Q007-style cost/turnover validation where applicable.
"""
    path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
