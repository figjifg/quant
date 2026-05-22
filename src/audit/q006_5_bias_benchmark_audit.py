from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit.q002_quality_only import (
    END_DATE,
    ETF_DIR,
    PRICE_DIR,
    Q001_REPORT_DIR,
    ROOT,
    TOP_N,
    build_portfolio_nav,
    build_spy_nav,
    load_prices,
    load_spy,
    load_universe,
    nav_metrics,
)


REPORT_DIR = ROOT / "reports" / "experiments" / "Q006_5_bias_benchmark_audit"
Q002_DIR = ROOT / "reports" / "experiments" / "Q002_quality_only"
Q006_DIR = ROOT / "reports" / "experiments" / "Q006_qvsy_composite"
RANDOM_SEED = 20260520
RANDOM_RUNS = 1000
MAG7 = {"AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Q006.5 survivor bias and benchmark audit.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    run(args.report_dir)
    return 0


def run(report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    universe = load_universe(Q001_REPORT_DIR)
    prices = load_prices(PRICE_DIR, universe["ticker"].tolist())
    spy = load_spy(ETF_DIR)
    calendar = [d for d in sorted(spy.index) if pd.Timestamp("2010-01-01") <= d <= pd.Timestamp(END_DATE)]
    q002 = load_q_result(Q002_DIR, "Q002", "quality_score")
    q006 = load_q_result(Q006_DIR, "Q006", "qvsy_score")
    execution_dates = sorted(pd.to_datetime(q006["holdings"]["execution_date"]).unique())

    spy_nav = build_spy_nav(spy, pd.Series([d.date().isoformat() for d in calendar if d >= execution_dates[0]]))
    universe_ew = build_static_selection_nav(universe["ticker"].tolist(), execution_dates, prices, calendar, "survivor_99_ew")
    universe_ew_vs_spy = compare_navs({"survivor_99_ew": universe_ew, "SPY_100": spy_nav})
    random30 = build_random30_distribution(universe["ticker"].tolist(), execution_dates, prices, calendar, spy_nav)
    market_cap_top30, market_cap_holdings = build_market_cap_top30(q006["signals"], execution_dates, prices, calendar, spy_nav)
    sector_exposure = build_sector_exposure(universe, market_cap_holdings, q002["holdings"], q006["holdings"])
    mag7 = build_mag7_exclusion(q002, q006, prices, calendar, spy_nav)
    contributors = build_top_contributors({"Q002": q002["holdings"], "Q006": q006["holdings"]}, prices, calendar)
    quartiles = build_quartile_vs_spy({"Q002": q002, "Q006": q006}, prices, calendar, spy)

    q_metrics = {
        "Q002": nav_metrics(q002["nav"]),
        "Q006": nav_metrics(q006["nav"]),
        "SPY": nav_metrics(spy_nav),
    }
    random30 = append_candidate_percentiles(random30, q_metrics)

    write_config(report_dir / "config.yaml")
    universe_ew_vs_spy.to_csv(report_dir / "universe_ew_vs_spy.csv", index=False)
    random30.to_csv(report_dir / "random30_distribution.csv", index=False)
    market_cap_top30.to_csv(report_dir / "market_cap_top30.csv", index=False)
    sector_exposure.to_csv(report_dir / "sector_exposure.csv", index=False)
    mag7.to_csv(report_dir / "mag7_exclusion.csv", index=False)
    contributors.to_csv(report_dir / "top_contributors.csv", index=False)
    quartiles.to_csv(report_dir / "quartile_vs_spy.csv", index=False)
    write_report(report_dir / "report.md", universe_ew_vs_spy, random30, market_cap_top30, sector_exposure, mag7, contributors, quartiles, q_metrics)


def load_q_result(report_dir: Path, label: str, score_col: str) -> dict[str, pd.DataFrame | str]:
    signals = pd.read_csv(report_dir / "quarterly_signals.csv")
    holdings = pd.read_csv(report_dir / "top30_holdings.csv")
    nav = pd.read_csv(report_dir / "portfolio_daily_nav.csv")
    return {"label": label, "score_col": score_col, "signals": signals, "holdings": holdings, "nav": nav}


def build_static_selection_nav(
    tickers: list[str],
    execution_dates: list[pd.Timestamp],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    label: str,
) -> pd.DataFrame:
    rows = []
    for execution in execution_dates:
        selected = [ticker for ticker in tickers if ticker in prices and execution in prices[ticker].index]
        if not selected:
            continue
        weight = 1.0 / len(selected)
        period = execution.to_period("Q").end_time.date().isoformat()
        for ticker in selected:
            rows.append(
                {
                    "rebalance_period_end": period,
                    "available_date": execution.date().isoformat(),
                    "execution_date": execution.date().isoformat(),
                    "ticker": ticker,
                    "sector": "",
                    "rank": 0,
                    "weight": weight,
                    "entry_close": float(prices[ticker].loc[execution, "close"]),
                }
            )
    nav, _ = build_portfolio_nav(pd.DataFrame(rows), prices, calendar)
    nav["strategy"] = label
    return nav


def compare_navs(nav_by_name: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, nav in nav_by_name.items():
        metrics = nav_metrics(nav)
        rows.append({"strategy": name, **metrics})
    out = pd.DataFrame(rows)
    spy_cagr = float(out.loc[out["strategy"].eq("SPY_100"), "cagr"].iloc[0])
    out["excess_cagr_vs_spy"] = out["cagr"] - spy_cagr
    return out


def build_random30_distribution(
    tickers: list[str],
    execution_dates: list[pd.Timestamp],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spy_nav: pd.DataFrame,
) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    spy_cagr = nav_metrics(spy_nav)["cagr"]
    calendar = [d for d in calendar if d >= execution_dates[0]]
    returns = pd.DataFrame(index=pd.DatetimeIndex(calendar))
    for ticker in tickers:
        if ticker in prices:
            returns[ticker] = prices[ticker]["close"].pct_change().reindex(calendar)
    returns = returns.fillna(0.0)
    rows = []
    for sim_id in range(RANDOM_RUNS):
        selected = sorted(rng.choice(tickers, size=TOP_N, replace=False).tolist())
        daily_returns = returns[selected]
        nav_values = []
        sleeve_values = np.repeat(1.0 / TOP_N, TOP_N)
        execution_set = set(execution_dates)
        for date, row in daily_returns.iterrows():
            if date in execution_set:
                sleeve_values = np.repeat(float(sleeve_values.sum()) / TOP_N, TOP_N)
            sleeve_values = sleeve_values * (1.0 + row.to_numpy(dtype=float))
            nav_values.append(float(sleeve_values.sum()))
        nav = pd.DataFrame({"date": daily_returns.index.date.astype(str), "nav": nav_values})
        metrics = nav_metrics(nav)
        rows.append(
            {
                "simulation_id": sim_id,
                "seed": RANDOM_SEED,
                "tickers": " ".join(selected),
                **metrics,
                "excess_cagr_vs_spy": metrics["cagr"] - spy_cagr,
            }
        )
    return pd.DataFrame(rows)


def append_candidate_percentiles(random30: pd.DataFrame, q_metrics: dict[str, dict[str, float]]) -> pd.DataFrame:
    spy_cagr = q_metrics["SPY"]["cagr"]
    rows = []
    for label in ("Q002", "Q006"):
        excess = q_metrics[label]["cagr"] - spy_cagr
        rows.append(
            {
                "simulation_id": f"{label}_candidate",
                "seed": RANDOM_SEED,
                "tickers": "",
                **q_metrics[label],
                "excess_cagr_vs_spy": excess,
                "cagr_percentile_vs_random30": percentile_rank(random30["cagr"], q_metrics[label]["cagr"]),
                "excess_cagr_percentile_vs_random30": percentile_rank(random30["excess_cagr_vs_spy"], excess),
                "sharpe_percentile_vs_random30": percentile_rank(random30["sharpe"], q_metrics[label]["sharpe"]),
            }
        )
    out = random30.copy()
    out["cagr_percentile_vs_random30"] = np.nan
    out["excess_cagr_percentile_vs_random30"] = np.nan
    out["sharpe_percentile_vs_random30"] = np.nan
    return pd.concat([out, pd.DataFrame(rows)], ignore_index=True)


def percentile_rank(series: pd.Series, value: float) -> float:
    valid = series.dropna()
    return float((valid <= value).mean()) if len(valid) else float("nan")


def build_market_cap_top30(
    signals: pd.DataFrame,
    execution_dates: list[pd.Timestamp],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spy_nav: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for _, group in signals.groupby("rebalance_period_end", sort=True):
        if "market_cap_estimate" not in group.columns:
            continue
        selected = group.dropna(subset=["market_cap_estimate"]).sort_values("market_cap_estimate", ascending=False).head(TOP_N)
        if len(selected) < TOP_N:
            continue
        weight = 1.0 / TOP_N
        for rank, (_, row) in enumerate(selected.iterrows(), start=1):
            execution = pd.Timestamp(row["execution_date"])
            if row["ticker"] not in prices or execution not in prices[row["ticker"]].index:
                continue
            rows.append(
                {
                    "rebalance_period_end": row["rebalance_period_end"],
                    "available_date": row["available_date"],
                    "execution_date": row["execution_date"],
                    "ticker": row["ticker"],
                    "sector": row["sector"],
                    "market_cap_estimate": row["market_cap_estimate"],
                    "rank": rank,
                    "weight": weight,
                    "entry_close": float(prices[row["ticker"]].loc[execution, "close"]),
                }
            )
    holdings = pd.DataFrame(rows)
    nav, _ = build_portfolio_nav(holdings, prices, calendar)
    comparison = compare_navs({"market_cap_top30": nav, "SPY_100": spy_nav})
    return comparison, holdings


def build_sector_exposure(
    universe: pd.DataFrame,
    market_cap_holdings: pd.DataFrame,
    q002_holdings: pd.DataFrame,
    q006_holdings: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    sector_map = universe.set_index("ticker")["sector"].to_dict()
    universe_dates = sorted(set(q006_holdings["execution_date"]))
    for execution_date in universe_dates:
        for sector, count in universe["sector"].value_counts().items():
            rows.append({"strategy": "survivor_99_ew_proxy", "execution_date": execution_date, "sector": sector, "weight": count / len(universe)})
    for strategy, holdings in [("market_cap_top30", market_cap_holdings), ("Q002", q002_holdings), ("Q006", q006_holdings)]:
        work = holdings.copy()
        if "sector" not in work.columns or work["sector"].isna().all():
            work["sector"] = work["ticker"].map(sector_map)
        grouped = work.groupby(["execution_date", "sector"], dropna=False)["weight"].sum().reset_index()
        grouped["strategy"] = strategy
        rows.extend(grouped[["strategy", "execution_date", "sector", "weight"]].to_dict("records"))
    return pd.DataFrame(rows).sort_values(["strategy", "execution_date", "weight"], ascending=[True, True, False])


def build_mag7_exclusion(
    q002: dict[str, pd.DataFrame | str],
    q006: dict[str, pd.DataFrame | str],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spy_nav: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for q in (q002, q006):
        label = str(q["label"])
        score_col = str(q["score_col"])
        full_nav = q["nav"]  # type: ignore[assignment]
        excluded_holdings = reselect_without_tickers(q["signals"], score_col, MAG7, prices, calendar)  # type: ignore[arg-type]
        excluded_nav, _ = build_portfolio_nav(excluded_holdings, prices, calendar)
        for name, nav in [(label, full_nav), (f"{label}_ex_mag7", excluded_nav)]:
            metrics = nav_metrics(nav)  # type: ignore[arg-type]
            rows.append({"strategy": name, **metrics, "excess_cagr_vs_spy": metrics["cagr"] - nav_metrics(spy_nav)["cagr"]})
        delta = rows[-1]["cagr"] - rows[-2]["cagr"]
        rows[-1]["cagr_delta_vs_full"] = delta
        rows[-2]["cagr_delta_vs_full"] = 0.0
    return pd.DataFrame(rows)


def reselect_without_tickers(
    signals: pd.DataFrame,
    score_col: str,
    exclude: set[str],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
) -> pd.DataFrame:
    rows = []
    cal = pd.Series(calendar)
    for _, group in signals.loc[~signals["ticker"].isin(exclude)].groupby("rebalance_period_end", sort=True):
        if "execution_date" in group.columns:
            execution_date = group["execution_date"].iloc[0]
        else:
            available = pd.Timestamp(group["available_date"].iloc[0])
            candidates = cal.loc[cal.gt(available)]
            if candidates.empty:
                continue
            execution_date = candidates.iloc[0].date().isoformat()
        selected = group.sort_values(score_col, ascending=False).head(TOP_N)
        if len(selected) < TOP_N:
            continue
        weight = 1.0 / TOP_N
        for rank, (_, row) in enumerate(selected.iterrows(), start=1):
            execution = pd.Timestamp(execution_date)
            if row["ticker"] not in prices or execution not in prices[row["ticker"]].index:
                continue
            rows.append(
                {
                    "rebalance_period_end": row["rebalance_period_end"],
                    "available_date": row["available_date"],
                    "execution_date": execution.date().isoformat(),
                    "ticker": row["ticker"],
                    "sector": row["sector"],
                    score_col: row[score_col],
                    "rank": rank,
                    "weight": weight,
                    "entry_close": float(prices[row["ticker"]].loc[execution, "close"]),
                }
            )
    return pd.DataFrame(rows)


def build_top_contributors(
    holdings_by_strategy: dict[str, pd.DataFrame],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
) -> pd.DataFrame:
    rows = []
    cal = pd.Series(calendar)
    for strategy, holdings in holdings_by_strategy.items():
        nav = 1.0
        for idx, execution_date in enumerate(sorted(pd.to_datetime(holdings["execution_date"]).unique())):
            next_execution = sorted(pd.to_datetime(holdings["execution_date"]).unique())[idx + 1] if idx + 1 < holdings["execution_date"].nunique() else cal.iloc[-1]
            group = holdings.loc[pd.to_datetime(holdings["execution_date"]).eq(execution_date)]
            period_total = 0.0
            contribs = []
            for _, row in group.iterrows():
                ticker = row["ticker"]
                if ticker not in prices or execution_date not in prices[ticker].index or next_execution not in prices[ticker].index:
                    continue
                ticker_return = prices[ticker].loc[next_execution, "close"] / prices[ticker].loc[execution_date, "close"] - 1.0
                contribution = nav * row["weight"] * ticker_return
                contribs.append((ticker, contribution))
                period_total += row["weight"] * ticker_return
            for ticker, contribution in contribs:
                rows.append(
                    {
                        "strategy": strategy,
                        "ticker": ticker,
                        "execution_date": execution_date.date().isoformat(),
                        "exit_date": next_execution.date().isoformat(),
                        "nav_contribution": contribution,
                        "period_bucket": "2020_2026" if execution_date >= pd.Timestamp("2020-01-01") else "2010_2019",
                    }
                )
            nav *= 1.0 + period_total
    detail = pd.DataFrame(rows)
    totals = detail.groupby(["strategy", "ticker"], as_index=False)["nav_contribution"].sum()
    concentration_rows = []
    for strategy, group in totals.groupby("strategy"):
        total_gain = group["nav_contribution"].sum()
        ranked = group.assign(abs_contribution=group["nav_contribution"].abs()).sort_values("abs_contribution", ascending=False)
        for n in (5, 10, 20):
            concentration_rows.append(
                {
                    "strategy": strategy,
                    "ticker": f"TOP_{n}_CONCENTRATION",
                    "nav_contribution": ranked.head(n)["nav_contribution"].sum(),
                    "share_of_total_gain": ranked.head(n)["nav_contribution"].sum() / total_gain if total_gain else np.nan,
                    "period_bucket": "all",
                }
            )
        by_period = detail.loc[detail["strategy"].eq(strategy)].groupby("period_bucket")["nav_contribution"].sum()
        for period, value in by_period.items():
            concentration_rows.append(
                {
                    "strategy": strategy,
                    "ticker": f"PERIOD_{period}",
                    "nav_contribution": value,
                    "share_of_total_gain": value / total_gain if total_gain else np.nan,
                    "period_bucket": period,
                }
            )
    totals["share_of_total_gain"] = totals.groupby("strategy")["nav_contribution"].transform(lambda s: s / s.sum())
    totals["period_bucket"] = "all"
    return pd.concat([totals, pd.DataFrame(concentration_rows)], ignore_index=True).sort_values(["strategy", "nav_contribution"], ascending=[True, False])


def build_quartile_vs_spy(
    q_results: dict[str, dict[str, pd.DataFrame | str]],
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spy: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    cal = pd.Series(calendar)
    for label, q in q_results.items():
        signals = q["signals"]  # type: ignore[assignment]
        score_col = str(q["score_col"])
        for idx, period_end in enumerate(list(signals.groupby("rebalance_period_end", sort=True).groups)):
            group = signals.loc[signals["rebalance_period_end"].eq(period_end)].copy()
            execution = signal_execution_date(group, cal)
            if execution is None:
                continue
            if idx + 1 < signals["rebalance_period_end"].nunique():
                next_period = list(signals.groupby("rebalance_period_end", sort=True).groups)[idx + 1]
                exit_date = signal_execution_date(signals.loc[signals["rebalance_period_end"].eq(next_period)], cal)
                if exit_date is None:
                    continue
            else:
                exit_date = cal.iloc[-1]
            if execution not in spy.index or exit_date not in spy.index:
                continue
            tradable = group.loc[group["ticker"].map(lambda t: t in prices and execution in prices[t].index and exit_date in prices[t].index)].copy()
            if len(tradable) < 20:
                continue
            tradable["quartile"] = pd.qcut(tradable[score_col].rank(method="first", ascending=False), 4, labels=["Q1", "Q2", "Q3", "Q4"])
            spy_return = spy.loc[exit_date, "close"] / spy.loc[execution, "close"] - 1.0
            for quartile, qgroup in tradable.groupby("quartile", observed=True):
                returns = [prices[t].loc[exit_date, "close"] / prices[t].loc[execution, "close"] - 1.0 for t in qgroup["ticker"]]
                bucket_return = float(np.mean(returns))
                rows.append(
                    {
                        "strategy": label,
                        "rebalance_period_end": period_end,
                        "execution_date": execution.date().isoformat(),
                        "exit_date": exit_date.date().isoformat(),
                        "bucket": str(quartile),
                        "holding_count": len(returns),
                        "period_return": bucket_return,
                        "spy_period_return": spy_return,
                        "excess_vs_spy": bucket_return - spy_return,
                    }
                )
    return pd.DataFrame(rows)


def signal_execution_date(group: pd.DataFrame, cal: pd.Series) -> pd.Timestamp | None:
    if "execution_date" in group.columns:
        return pd.Timestamp(group["execution_date"].iloc[0])
    available = pd.Timestamp(group["available_date"].iloc[0])
    candidates = cal.loc[cal.gt(available)]
    if candidates.empty:
        return None
    return pd.Timestamp(candidates.iloc[0])


def write_config(path: Path) -> None:
    path.write_text(
        f"""experiment: Q006_5_bias_benchmark_audit
random_seed: {RANDOM_SEED}
random_runs: {RANDOM_RUNS}
source_results:
  q002: reports/experiments/Q002_quality_only
  q006: reports/experiments/Q006_qvsy_composite
  universe: reports/experiments/Q001_universe_construction/universe_list.csv
  prices: research_input_data/inputs/us_equity_prices/*.csv
  benchmark: research_input_data/inputs/global_etf/yf_SPY.csv
limitations:
  - survivor universe audit only; not survivorship-free
  - SPY sector breakdown is approximated only by survivor universe and market-cap-top30 proxies
  - Q-family remains research diagnostic, production X
""",
        encoding="utf-8",
    )


def write_report(
    path: Path,
    universe_ew: pd.DataFrame,
    random30: pd.DataFrame,
    market_cap: pd.DataFrame,
    sector: pd.DataFrame,
    mag7: pd.DataFrame,
    contributors: pd.DataFrame,
    quartiles: pd.DataFrame,
    q_metrics: dict[str, dict[str, float]],
) -> None:
    ew = universe_ew.set_index("strategy")
    mc = market_cap.set_index("strategy")
    random_only = random30.loc[random30["simulation_id"].map(lambda x: str(x).isdigit())]
    q_rows = random30.loc[random30["simulation_id"].astype(str).str.contains("_candidate")]
    q4_excess = quartiles.loc[quartiles["bucket"].eq("Q4"), "excess_vs_spy"].mean()
    all_quartile_win_rate = quartiles.groupby("bucket")["excess_vs_spy"].mean()
    mag = mag7.set_index("strategy")
    top_conc = contributors.loc[contributors["ticker"].str.contains("TOP_", na=False)]
    verdict = "universe bias 비중이 크다"
    if ew.loc["survivor_99_ew", "excess_cagr_vs_spy"] < 0.01 and q4_excess < 0:
        verdict = "factor alpha 가능성은 남지만 survivor-safe 검증 전 production 불가"
    report = f"""# Q006.5 Bias & Benchmark Audit

## Verdict

{verdict}. Q-family 결과는 현재 99개 survivor universe diagnostic이며 production 후보가 아니다.

## Universe Bias

| Benchmark | CAGR | Sharpe | MDD | Excess CAGR vs SPY |
| --- | ---: | ---: | ---: | ---: |
| Survivor 99 EW | {ew.loc['survivor_99_ew', 'cagr']:.2%} | {ew.loc['survivor_99_ew', 'sharpe']:.2f} | {ew.loc['survivor_99_ew', 'mdd']:.2%} | {ew.loc['survivor_99_ew', 'excess_cagr_vs_spy']:.2%} |
| SPY | {ew.loc['SPY_100', 'cagr']:.2%} | {ew.loc['SPY_100', 'sharpe']:.2f} | {ew.loc['SPY_100', 'mdd']:.2%} | 0.00% |

## Random 30 Percentile

Random 30 median excess CAGR: {random_only['excess_cagr_vs_spy'].median():.2%}.

| Strategy | CAGR percentile | Excess CAGR percentile | Sharpe percentile |
| --- | ---: | ---: | ---: |
"""
    for _, row in q_rows.iterrows():
        report += f"| {row['simulation_id']} | {row['cagr_percentile_vs_random30']:.1%} | {row['excess_cagr_percentile_vs_random30']:.1%} | {row['sharpe_percentile_vs_random30']:.1%} |\n"
    report += f"""
## Mega-cap Benchmark

Market-cap top30 excess CAGR vs SPY: {mc.loc['market_cap_top30', 'excess_cagr_vs_spy']:.2%}. 이 값이 Q002/Q006와 가까우면 mega-cap concentration 설명력이 크다.

## Sector / Mag 7

- Sector exposure CSV는 Q002/Q006, survivor EW proxy, market-cap top30 proxy 분기 sector weight를 기록한다. 실제 SPY sector breakdown 파일은 없어서 외부 추정 없이 별도 산출하지 않았다.
- Q002 Mag7 제외 CAGR delta: {mag.loc['Q002_ex_mag7', 'cagr_delta_vs_full']:.2%}
- Q006 Mag7 제외 CAGR delta: {mag.loc['Q006_ex_mag7', 'cagr_delta_vs_full']:.2%}

## Contributor Concentration

| Strategy | Top bucket | Share of total gain |
| --- | --- | ---: |
"""
    for _, row in top_conc.iterrows():
        report += f"| {row['strategy']} | {row['ticker']} | {row['share_of_total_gain']:.2%} |\n"
    report += f"""
## Quartile vs SPY

평균 Q4 excess vs SPY: {q4_excess:.2%}. Bucket별 평균 excess: {', '.join(f'{idx}={value:.2%}' for idx, value in all_quartile_win_rate.items())}.

## Production Gate

Direct Q-family는 survivor-safe universe가 없으므로 production X. Q007/Q008 진행 여부는 Q006.6 ETF proxy 결과와 함께 판단한다.
"""
    path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
