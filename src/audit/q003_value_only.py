from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.audit.q000_us_fundamental_data_audit import CONCEPT_ALIASES
from src.audit.q002_quality_only import (
    END_DATE,
    ETF_DIR,
    FUNDAMENTAL_DIR,
    PIT_LAG_DAYS,
    PRICE_DIR,
    Q001_REPORT_DIR,
    ROOT,
    START_DATE,
    TOP_N,
    build_factor_metrics as q002_build_factor_metrics,
    build_portfolio_nav,
    build_spy_nav,
    build_subperiod_split as q002_build_subperiod_split,
    classify_verdict,
    information_ratio,
    load_prices,
    load_spy,
    load_universe,
    merge_navs,
    nav_metrics,
    normalize_flow_quarters,
    normalize_instants,
    sector_concentration,
)


REPORT_DIR = ROOT / "reports" / "experiments" / "Q003_value_only"
Q002_REPORT_DIR = ROOT / "reports" / "experiments" / "Q002_quality_only"

FLOW_CONCEPTS = {"NetIncome", "OperatingIncome", "Revenues", "CFO", "CapEx", "Buybacks", "Dividends"}
INSTANT_CONCEPTS = {"StockholdersEquity", "Assets", "LongTermDebt", "Shares"}
REQUIRED_FLOW_CONCEPTS = {"NetIncome", "OperatingIncome", "Revenues", "CFO", "CapEx"}
OPTIONAL_CASH_RETURN_CONCEPTS = {"Buybacks", "Dividends"}

Q_FAMILY_ALIASES: dict[str, list[str]] = {
    "NetIncome": CONCEPT_ALIASES["NetIncome"],
    "OperatingIncome": CONCEPT_ALIASES["OperatingIncome"],
    "Revenues": CONCEPT_ALIASES["Revenue"],
    "StockholdersEquity": CONCEPT_ALIASES["StockholdersEquity"],
    "Assets": CONCEPT_ALIASES["Assets"],
    "LongTermDebt": CONCEPT_ALIASES["LongTermDebt"],
    "CFO": CONCEPT_ALIASES["CFO"],
    "CapEx": CONCEPT_ALIASES["CapEx"],
    "Buybacks": [
        "PaymentsForRepurchaseOfCommonStock",
        "PaymentsForRepurchaseOfEquity",
        "PaymentsForRepurchaseOfCommonStocks",
        "StockRepurchasedDuringPeriodValue",
        "StockRepurchasedAndRetiredDuringPeriodValue",
    ],
    "Dividends": [
        "PaymentsOfDividends",
        "PaymentsOfDividendsCommonStock",
        "DividendsCommonStockCash",
        "PaymentsOfOrdinaryDividends",
    ],
    "Shares": [
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
    ],
}

CONCEPT_UNITS = {
    **{concept: {"USD"} for concept in FLOW_CONCEPTS | {"StockholdersEquity", "Assets", "LongTermDebt"}},
    "Shares": {"shares"},
}

EXPERIMENTS: dict[str, dict[str, Any]] = {
    "Q003": {
        "slug": "value_only",
        "report_dir": ROOT / "reports" / "experiments" / "Q003_value_only",
        "strategy": "Q003_value_top30",
        "title": "Q003 Value Only",
        "score_column": "value_score",
        "component_scores": ["value_score"],
        "z_inputs": ["fcf_yield", "earnings_yield"],
        "score_formula": "Value_Score = z(FCF_yield) + z(Earnings_yield)",
        "hypothesis": "FCF yield와 earnings yield가 높은 대형주는 다음 분기 보유 구간에서 SPY 100%보다 더 나은 성과를 낼 수 있다.",
    },
    "Q004": {
        "slug": "shareholder_yield_only",
        "report_dir": ROOT / "reports" / "experiments" / "Q004_shareholder_yield_only",
        "strategy": "Q004_shareholder_yield_top30",
        "title": "Q004 Shareholder Yield Only",
        "score_column": "sy_score",
        "component_scores": ["sy_score"],
        "z_inputs": ["buyback_yield", "dividend_yield", "dilution"],
        "score_formula": "SY_Score = z(Buyback_yield) + z(Dividend_yield) - z(Dilution)",
        "hypothesis": "Buyback yield와 dividend yield가 높고 dilution이 낮은 대형주는 다음 분기 보유 구간에서 SPY 100%보다 더 나은 성과를 낼 수 있다.",
    },
    "Q005": {
        "slug": "quality_value_composite",
        "report_dir": ROOT / "reports" / "experiments" / "Q005_quality_value_composite",
        "strategy": "Q005_quality_value_top30",
        "title": "Q005 Quality + Value Composite",
        "score_column": "qv_score",
        "component_scores": ["quality_score", "value_score"],
        "z_inputs": ["roic", "fcf_margin", "leverage", "fcf_yield", "earnings_yield"],
        "score_formula": "Score = Quality_Score(Q002) + Value_Score(Q003)",
        "hypothesis": "Quality와 Value가 동시에 높은 대형주는 단일 factor보다 안정적인 다음 분기 성과를 낼 수 있다.",
    },
    "Q006": {
        "slug": "qvsy_composite",
        "report_dir": ROOT / "reports" / "experiments" / "Q006_qvsy_composite",
        "strategy": "Q006_qvsy_top30",
        "title": "Q006 Quality + Value + Shareholder Yield Composite",
        "score_column": "qvsy_score",
        "component_scores": ["quality_score", "value_score", "sy_score"],
        "z_inputs": ["roic", "fcf_margin", "leverage", "fcf_yield", "earnings_yield", "buyback_yield", "dividend_yield", "dilution"],
        "score_formula": "Score = Quality_Score + Value_Score + SY_Score",
        "hypothesis": "Quality, Value, Shareholder Yield가 동시에 높은 대형주는 Q-family final candidate로 검증할 가치가 있다.",
    },
}


@dataclass(frozen=True)
class FactStore:
    flows: dict[str, pd.DataFrame]
    instants: dict[str, pd.DataFrame]


def main() -> int:
    parser = argparse.ArgumentParser(description="Q003 pre-registered US value-only audit.")
    parser.add_argument("--fundamental-dir", type=Path, default=FUNDAMENTAL_DIR)
    parser.add_argument("--price-dir", type=Path, default=PRICE_DIR)
    parser.add_argument("--etf-dir", type=Path, default=ETF_DIR)
    parser.add_argument("--q001-report-dir", type=Path, default=Q001_REPORT_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()

    run_q_family(
        experiment_id="Q003",
        fundamental_dir=args.fundamental_dir,
        price_dir=args.price_dir,
        etf_dir=args.etf_dir,
        q001_report_dir=args.q001_report_dir,
        report_dir=args.report_dir,
    )
    return 0


def run_q_family(
    experiment_id: str,
    fundamental_dir: Path = FUNDAMENTAL_DIR,
    price_dir: Path = PRICE_DIR,
    etf_dir: Path = ETF_DIR,
    q001_report_dir: Path = Q001_REPORT_DIR,
    report_dir: Path | None = None,
) -> None:
    spec = EXPERIMENTS[experiment_id].copy()
    if report_dir is not None:
        spec["report_dir"] = report_dir
    spec["report_dir"].mkdir(parents=True, exist_ok=True)

    universe = load_universe(q001_report_dir)
    prices = load_prices(price_dir, universe["ticker"].tolist())
    spy = load_spy(etf_dir)
    calendar = sorted(spy.index)
    calendar = [d for d in calendar if pd.Timestamp(START_DATE) <= d <= pd.Timestamp(END_DATE)]
    if not calendar:
        raise RuntimeError(f"No common price calendar for {experiment_id}.")

    stores = {ticker: parse_companyfacts(fundamental_dir / f"{ticker}_facts.json") for ticker in universe["ticker"]}
    quarter_ends = pd.date_range(START_DATE, END_DATE, freq="QE")
    signal_rows = build_q_family_signals(quarter_ends, stores, universe, prices, calendar, spec)
    top_holdings = select_top_holdings(signal_rows, prices, spec)
    portfolio_nav, turnover = build_portfolio_nav(top_holdings, prices, calendar)
    spy_nav = build_spy_nav(spy, portfolio_nav["date"])
    factor_metrics = build_factor_metrics(portfolio_nav, spy_nav, top_holdings, spec)
    subperiod = build_subperiod_split(portfolio_nav, spy_nav, spec)
    quartiles = build_quartile_test(signal_rows, prices, calendar, spec)
    write_outputs(spec, signal_rows, top_holdings, portfolio_nav, spy_nav, factor_metrics, turnover, subperiod, quartiles)


def parse_companyfacts(path: Path) -> FactStore:
    if not path.exists():
        raise FileNotFoundError(path)
    facts = json.loads(path.read_text(encoding="utf-8")).get("facts", {}).get("us-gaap", {})
    raw: dict[str, pd.DataFrame] = {}
    for concept, aliases in Q_FAMILY_ALIASES.items():
        rows: list[dict[str, Any]] = []
        allowed_units = CONCEPT_UNITS[concept]
        for alias in aliases:
            payload = facts.get(alias)
            if not payload:
                continue
            for unit, entries in payload.get("units", {}).items():
                if unit not in allowed_units:
                    continue
                for entry in entries:
                    if entry.get("form") not in {"10-Q", "10-K"}:
                        continue
                    if not entry.get("end") or not entry.get("filed") or entry.get("val") is None:
                        continue
                    rows.append(
                        {
                            "concept": concept,
                            "alias": alias,
                            "start": entry.get("start"),
                            "end": entry["end"],
                            "filed": entry["filed"],
                            "fy": entry.get("fy"),
                            "fp": entry.get("fp"),
                            "form": entry.get("form"),
                            "value": entry.get("val"),
                        }
                    )
        raw[concept] = normalize_raw_rows(rows)

    flows = {concept: normalize_flow_quarters(raw[concept]) for concept in FLOW_CONCEPTS}
    instants = {concept: normalize_instants(raw[concept]) for concept in INSTANT_CONCEPTS}
    return FactStore(flows=flows, instants=instants)


def normalize_raw_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["start", "end", "filed", "value", "fy", "fp", "form", "alias"])
    df = pd.DataFrame(rows)
    df["end"] = pd.to_datetime(df["end"])
    df["filed"] = pd.to_datetime(df["filed"])
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["end", "filed", "value"]).sort_values(["filed", "end"])


def build_q_family_signals(
    quarter_ends: pd.DatetimeIndex,
    stores: dict[str, FactStore],
    universe: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spec: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    cal = pd.Series(calendar)
    sector_map = universe.set_index("ticker")["sector"].to_dict()
    for quarter_end in quarter_ends:
        available_date = quarter_end + pd.Timedelta(days=PIT_LAG_DAYS)
        execution_candidates = cal.loc[cal.gt(available_date)]
        if execution_candidates.empty:
            continue
        execution_date = execution_candidates.iloc[0]
        for ticker, store in stores.items():
            if ticker not in prices or execution_date not in prices[ticker].index:
                continue
            price = float(prices[ticker].loc[execution_date, "close"])
            factors = calculate_factors(store, available_date, price)
            if factors is None:
                continue
            rows.append(
                {
                    "rebalance_period_end": quarter_end.date().isoformat(),
                    "available_date": available_date.date().isoformat(),
                    "execution_date": execution_date.date().isoformat(),
                    "ticker": ticker,
                    "sector": sector_map.get(ticker, "unknown"),
                    **factors,
                }
            )
    signals = pd.DataFrame(rows)
    if signals.empty:
        return signals
    scored = []
    for _, group in signals.groupby("rebalance_period_end", sort=True):
        group = group.copy()
        for col in ["roic", "fcf_margin", "leverage", "fcf_yield", "earnings_yield", "buyback_yield", "dividend_yield", "dilution"]:
            std = group[col].std(ddof=0)
            group[f"z_{col}"] = 0.0 if not np.isfinite(std) or std == 0 else (group[col] - group[col].mean()) / std
        group["quality_score"] = group["z_roic"] + group["z_fcf_margin"] - group["z_leverage"]
        group["value_score"] = group["z_fcf_yield"] + group["z_earnings_yield"]
        group["sy_score"] = group["z_buyback_yield"] + group["z_dividend_yield"] - group["z_dilution"]
        group[spec["score_column"]] = group[spec["component_scores"]].sum(axis=1)
        group["rank"] = group[spec["score_column"]].rank(ascending=False, method="first").astype(int)
        scored.append(group)
    return pd.concat(scored, ignore_index=True).sort_values(["rebalance_period_end", "rank", "ticker"])


def calculate_factors(store: FactStore, available_date: pd.Timestamp, rebalance_price: float) -> dict[str, float] | None:
    flow_values = {}
    for concept in REQUIRED_FLOW_CONCEPTS:
        value = trailing_4q_sum(store.flows[concept], available_date)
        if value is None:
            return None
        flow_values[concept] = value
    for concept in OPTIONAL_CASH_RETURN_CONCEPTS:
        flow_values[concept] = trailing_4q_sum(store.flows[concept], available_date, default_zero=True)

    instant_values = {}
    for concept in {"StockholdersEquity", "Assets", "LongTermDebt", "Shares"}:
        value = latest_instant(store.instants[concept], available_date)
        if value is None:
            return None
        instant_values[concept] = value
    shares_1y_ago = latest_instant(store.instants["Shares"], available_date - pd.Timedelta(days=365))
    if shares_1y_ago is None:
        return None

    shares = instant_values["Shares"]
    market_cap = shares * rebalance_price
    invested_capital = instant_values["StockholdersEquity"] + instant_values["LongTermDebt"]
    revenue = flow_values["Revenues"]
    equity = instant_values["StockholdersEquity"]
    if market_cap <= 0 or shares <= 0 or shares_1y_ago <= 0 or invested_capital <= 0 or revenue == 0 or equity <= 0:
        return None

    roic = flow_values["OperatingIncome"] / invested_capital
    fcf = flow_values["CFO"] - flow_values["CapEx"]
    fcf_margin = fcf / revenue
    leverage = instant_values["LongTermDebt"] / equity
    fcf_yield = fcf / market_cap
    earnings_yield = flow_values["NetIncome"] / market_cap
    buyback_yield = max(0.0, flow_values["Buybacks"]) / market_cap
    dividend_yield = max(0.0, flow_values["Dividends"]) / market_cap
    dilution = max(0.0, shares - shares_1y_ago) / shares_1y_ago
    values = [roic, fcf_margin, leverage, fcf_yield, earnings_yield, buyback_yield, dividend_yield, dilution]
    if not all(np.isfinite(values)):
        return None
    return {
        "trailing_4q_net_income": flow_values["NetIncome"],
        "trailing_4q_op_income": flow_values["OperatingIncome"],
        "trailing_4q_cfo": flow_values["CFO"],
        "trailing_4q_capex": flow_values["CapEx"],
        "trailing_4q_revenue": revenue,
        "trailing_4q_buybacks": flow_values["Buybacks"],
        "trailing_4q_dividends": flow_values["Dividends"],
        "latest_equity": equity,
        "latest_ltd": instant_values["LongTermDebt"],
        "latest_assets": instant_values["Assets"],
        "latest_shares": shares,
        "shares_1y_ago": shares_1y_ago,
        "rebalance_price": rebalance_price,
        "market_cap_estimate": market_cap,
        "dividend_missing_zero_fill": bool(flow_values["Dividends"] == 0.0),
        "roic": roic,
        "fcf_margin": fcf_margin,
        "leverage": leverage,
        "fcf_yield": fcf_yield,
        "earnings_yield": earnings_yield,
        "buyback_yield": buyback_yield,
        "dividend_yield": dividend_yield,
        "dilution": dilution,
    }


def trailing_4q_sum(rows: pd.DataFrame, available_date: pd.Timestamp, default_zero: bool = False) -> float | None:
    rows = rows.loc[rows["filed"].le(available_date)]
    if rows.empty:
        return 0.0 if default_zero else None
    latest_by_period = rows.sort_values(["period_end", "filed"]).groupby("period_end").tail(1)
    trailing = latest_by_period.sort_values("period_end").tail(4)
    if len(trailing) < 4:
        return 0.0 if default_zero else None
    return float(trailing["value"].sum())


def latest_instant(rows: pd.DataFrame, available_date: pd.Timestamp) -> float | None:
    rows = rows.loc[rows["filed"].le(available_date)]
    if rows.empty:
        return None
    return float(rows.sort_values(["period_end", "filed"]).iloc[-1]["value"])


def select_top_holdings(signals: pd.DataFrame, prices: dict[str, pd.DataFrame], spec: dict[str, Any]) -> pd.DataFrame:
    rows = []
    score_col = spec["score_column"]
    for _, group in signals.groupby("rebalance_period_end", sort=True):
        selected = group.sort_values("rank").head(TOP_N).copy()
        if len(selected) < TOP_N:
            continue
        weight = 1.0 / len(selected)
        for _, row in selected.iterrows():
            execution_date = pd.Timestamp(row["execution_date"])
            rows.append(
                {
                    "rebalance_period_end": row["rebalance_period_end"],
                    "available_date": row["available_date"],
                    "execution_date": row["execution_date"],
                    "ticker": row["ticker"],
                    "sector": row["sector"],
                    score_col: row[score_col],
                    "rank": int(row["rank"]),
                    "weight": weight,
                    "entry_close": float(prices[row["ticker"]].loc[execution_date, "close"]),
                }
            )
    return pd.DataFrame(rows).sort_values(["execution_date", "rank", "ticker"])


def build_factor_metrics(portfolio_nav: pd.DataFrame, spy_nav: pd.DataFrame, holdings: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    metrics = q002_build_factor_metrics(portfolio_nav, spy_nav, holdings)
    metrics.loc[0, "strategy"] = spec["strategy"]
    return metrics


def build_subperiod_split(portfolio_nav: pd.DataFrame, spy_nav: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    subperiod = q002_build_subperiod_split(portfolio_nav, spy_nav)
    subperiod.loc[subperiod["strategy"].eq("Q002_quality_top30"), "strategy"] = spec["strategy"]
    return subperiod


def build_quartile_test(
    signals: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
    spec: dict[str, Any],
) -> pd.DataFrame:
    cal = pd.Series(calendar)
    score_col = spec["score_column"]
    ordered_periods = list(signals.groupby("rebalance_period_end", sort=True).groups)
    rows = []
    for index, period_end in enumerate(ordered_periods):
        group = signals.loc[signals["rebalance_period_end"].eq(period_end)]
        execution = pd.Timestamp(group["execution_date"].iloc[0])
        if index + 1 < len(ordered_periods):
            next_group = signals.loc[signals["rebalance_period_end"].eq(ordered_periods[index + 1])]
            exit_date = pd.Timestamp(next_group["execution_date"].iloc[0])
        else:
            exit_date = cal.iloc[-1]
        tradable = group.loc[group["ticker"].map(lambda t: t in prices and execution in prices[t].index and exit_date in prices[t].index)].copy()
        if len(tradable) < 20:
            continue
        tradable["quartile"] = pd.qcut(tradable[score_col].rank(method="first", ascending=False), 4, labels=["Q1", "Q2", "Q3", "Q4"])
        period_returns = {}
        for quartile, qgroup in tradable.groupby("quartile", observed=True):
            ticker_returns = [prices[ticker].loc[exit_date, "close"] / prices[ticker].loc[execution, "close"] - 1.0 for ticker in qgroup["ticker"]]
            period_returns[str(quartile)] = float(np.mean(ticker_returns))
            rows.append(
                {
                    "rebalance_period_end": period_end,
                    "execution_date": execution.date().isoformat(),
                    "exit_date": exit_date.date().isoformat(),
                    "bucket": str(quartile),
                    "holding_count": len(ticker_returns),
                    "period_return": period_returns[str(quartile)],
                }
            )
        if "Q1" in period_returns and "Q4" in period_returns:
            rows.append(
                {
                    "rebalance_period_end": period_end,
                    "execution_date": execution.date().isoformat(),
                    "exit_date": exit_date.date().isoformat(),
                    "bucket": "Q1_minus_Q4",
                    "holding_count": 0,
                    "period_return": period_returns["Q1"] - period_returns["Q4"],
                }
            )
    return pd.DataFrame(rows)


def write_outputs(
    spec: dict[str, Any],
    signal_rows: pd.DataFrame,
    top_holdings: pd.DataFrame,
    portfolio_nav: pd.DataFrame,
    spy_nav: pd.DataFrame,
    factor_metrics: pd.DataFrame,
    turnover: pd.DataFrame,
    subperiod: pd.DataFrame,
    quartiles: pd.DataFrame,
) -> None:
    report_dir = spec["report_dir"]
    signal_rows.to_csv(report_dir / "quarterly_signals.csv", index=False)
    top_holdings.to_csv(report_dir / "top30_holdings.csv", index=False)
    portfolio_nav.to_csv(report_dir / "portfolio_daily_nav.csv", index=False)
    spy_nav.to_csv(report_dir / "spy_daily_nav.csv", index=False)
    factor_metrics.to_csv(report_dir / "factor_metrics.csv", index=False)
    turnover.to_csv(report_dir / "turnover_by_quarter.csv", index=False)
    subperiod.to_csv(report_dir / "subperiod_split.csv", index=False)
    quartiles.to_csv(report_dir / "quartile_long_short_test.csv", index=False)
    write_config(report_dir / "config.yaml", spec)
    write_report(report_dir / "report.md", spec, factor_metrics, turnover, subperiod, quartiles, top_holdings, signal_rows)


def write_config(path: Path, spec: dict[str, Any]) -> None:
    path.write_text(
        f"""experiment: {spec['title']}
universe: Q001 99 tickers, current S&P 100-like universe excluding MMC
fundamentals: research_input_data/inputs/us_fundamentals/*_facts.json
prices: research_input_data/inputs/us_equity_prices/*.csv
benchmark: research_input_data/inputs/global_etf/yf_SPY.csv
start_date: {START_DATE}
end_date: {END_DATE}
pit_policy:
  source_timestamp: SEC companyfacts filed
  conservative_lag_days_after_quarter_end: {PIT_LAG_DAYS}
  execution_rule: first SPY trading day after available_date
  market_cap_estimate: latest filed shares as of available_date * stock close on execution/rebalance date
signal:
  formula: {spec['score_formula']}
  quality_score: z_roic + z_fcf_margin - z_leverage
  value_score: z_fcf_yield + z_earnings_yield
  shareholder_yield_score: z_buyback_yield + z_dividend_yield - z_dilution
  fcf_yield: (trailing_4q_cfo - trailing_4q_capex) / market_cap_estimate
  earnings_yield: trailing_4q_net_income / market_cap_estimate
  buyback_yield: trailing_4q_buybacks / market_cap_estimate
  dividend_yield: trailing_4q_dividends / market_cap_estimate
  dilution: max(0, latest_shares - shares_1y_ago) / shares_1y_ago
portfolio:
  selection: top_{TOP_N}_{spec['score_column']}
  weighting: equal_weight
  rebalance: quarterly
  currency: USD
  costs_bps: 0
limitations:
  - current survivor universe; not survivorship-free
  - no factor grid; single pre-registered composite only
  - missing cash dividend concepts are zero-filled for Q004/Q006
""",
        encoding="utf-8",
    )


def write_report(
    path: Path,
    spec: dict[str, Any],
    metrics: pd.DataFrame,
    turnover: pd.DataFrame,
    subperiod: pd.DataFrame,
    quartiles: pd.DataFrame,
    holdings: pd.DataFrame,
    signals: pd.DataFrame,
) -> None:
    q = metrics.loc[metrics["strategy"].eq(spec["strategy"])].iloc[0]
    spy = metrics.loc[metrics["strategy"].eq("SPY_100")].iloc[0]
    ls = quartiles.loc[quartiles["bucket"].eq("Q1_minus_Q4"), "period_return"]
    ls_mean = float(ls.mean()) if not ls.empty else np.nan
    ls_positive = float((ls > 0).mean()) if not ls.empty else np.nan
    avg_turnover = float(turnover["turnover"].mean()) if not turnover.empty else np.nan
    verdict = classify_verdict(q, spy)
    period_lines = []
    for _, row in subperiod.loc[subperiod["strategy"].eq(spec["strategy"])].iterrows():
        period_lines.append(f"| {row['period']} | {row['cagr']:.2%} | {row['sharpe']:.2f} | {row['mdd']:.2%} | {row['excess_cagr_vs_spy']:.2%} |")
    missing_dividend_names = sorted(signals.loc[signals["dividend_missing_zero_fill"], "ticker"].unique())
    report = f"""# {spec['title']}

## Verdict

{verdict}. 이 실험은 사전 등록한 단일 score만 사용했다. 현재 survivor universe 한계가 있으므로 production promote 판단에는 쓰지 않는다.

## Hypothesis

{spec['hypothesis']}

## 사전 등록 구현

- Universe: Q001 99종목(S&P 100 유사 현재 universe, MMC 제외).
- Composite: `{spec['score_formula']}`.
- Market cap estimate: SEC `filed` 기준으로 사용 가능한 latest shares x rebalance/execution date 종가.
- Portfolio: 매 분기 Top 30 equal weight, 비용 0 gross only, USD NAV.
- Benchmark: SPY 100% buy-hold.
- PIT: SEC `filed` 날짜와 분기말 +35일 lag를 통과한 값만 사용했다. 실행일은 `available_date` 이후 첫 SPY 거래일이다.
- Factor grid: 없음. 사전 등록 factor 정의만 테스트했다.
- Dividend missing zero-fill: {len(missing_dividend_names)}개 종목이 최소 한 signal row에서 cash dividend concept 결측으로 0 처리됐다.

## 핵심 성과

| Strategy | Total return | CAGR | Sharpe | MDD | SPY excess CAGR | IR vs SPY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| {spec['strategy']} | {q['total_return']:.2%} | {q['cagr']:.2%} | {q['sharpe']:.2f} | {q['mdd']:.2%} | {q['excess_cagr_vs_spy']:.2%} | {q['information_ratio_vs_spy']:.2f} |
| SPY 100% | {spy['total_return']:.2%} | {spy['cagr']:.2%} | {spy['sharpe']:.2f} | {spy['mdd']:.2%} | 0.00% |  |

## Quartile Spread

- Q1-Q4 long-short 평균 분기 수익률: {ls_mean:.2%}
- Q1-Q4 양수 비율: {ls_positive:.1%}

## Turnover / Concentration

- 평균 분기 turnover: {avg_turnover:.2%}
- 평균 최대 sector weight: {q['avg_max_sector_weight']:.2%}
- 최대 sector weight: {q['max_sector_weight']:.2%} ({q['max_sector_name']})
- 보유 구간 수: {holdings['execution_date'].nunique()}
- signal row 수: {len(signals)}

## Subperiod

| Period | CAGR | Sharpe | MDD | Excess CAGR vs SPY |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(period_lines)}

## 한계

- 현재 universe는 살아남은 99종목이므로 survivorship bias가 있다.
- 비용은 0 gross only이며, 비용/세금 검증은 Q007에서 별도로 해야 한다.
- `P08_IEF30` 직접 promote가 아니라 Q-family 별도 sleeve 검증이다.
"""
    path.write_text(report, encoding="utf-8")


def build_comparison_report(path: Path = ROOT / "reports" / "experiments" / "Q_family_composite_comparison.md") -> None:
    rows = []
    subperiod_rows = []
    for experiment_id, title, report_dir in [
        ("Q002", "Quality only", Q002_REPORT_DIR),
        ("Q003", "Value only", EXPERIMENTS["Q003"]["report_dir"]),
        ("Q004", "Shareholder Yield only", EXPERIMENTS["Q004"]["report_dir"]),
        ("Q005", "Quality + Value", EXPERIMENTS["Q005"]["report_dir"]),
        ("Q006", "Quality + Value + Shareholder Yield", EXPERIMENTS["Q006"]["report_dir"]),
    ]:
        metrics = pd.read_csv(report_dir / "factor_metrics.csv")
        strategy_row = metrics.loc[metrics["strategy"].ne("SPY_100")].iloc[0]
        turnover = pd.read_csv(report_dir / "turnover_by_quarter.csv")
        quartiles = pd.read_csv(report_dir / "quartile_long_short_test.csv")
        ls = quartiles.loc[quartiles["bucket"].eq("Q1_minus_Q4"), "period_return"]
        rows.append(
            {
                "experiment": experiment_id,
                "title": title,
                "cagr": strategy_row["cagr"],
                "sharpe": strategy_row["sharpe"],
                "mdd": strategy_row["mdd"],
                "excess_cagr": strategy_row["excess_cagr_vs_spy"],
                "ir": strategy_row["information_ratio_vs_spy"],
                "turnover": turnover["turnover"].mean(),
                "long_short": ls.mean(),
            }
        )
        sub = pd.read_csv(report_dir / "subperiod_split.csv")
        strategy_sub = sub.loc[sub["strategy"].ne("SPY_100"), ["period", "cagr", "excess_cagr_vs_spy"]].copy()
        strategy_sub["experiment"] = experiment_id
        subperiod_rows.append(strategy_sub)

    summary = pd.DataFrame(rows)
    ranking = summary.sort_values(["excess_cagr", "sharpe", "ir"], ascending=False).reset_index(drop=True)
    subperiod = pd.concat(subperiod_rows, ignore_index=True)
    spy_cagr = pd.read_csv(Q002_REPORT_DIR / "factor_metrics.csv").loc[1, "cagr"]
    lines = [
        "# Q-family Composite Comparison",
        "",
        "## 종합 표",
        "",
        "| Experiment | Sleeve | CAGR | Sharpe | MDD | Excess CAGR vs SPY | IR | Top30 turnover | Q1-Q4 long-short |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['experiment']} | {row['title']} | {row['cagr']:.2%} | {row['sharpe']:.2f} | {row['mdd']:.2%} | {row['excess_cagr']:.2%} | {row['ir']:.2f} | {row['turnover']:.2%} | {row['long_short']:.2%} |"
        )
    lines.extend(
        [
            f"| SPY | Benchmark | {spy_cagr:.2%} |  |  | 0.00% |  |  |  |",
            "",
            "## Subperiod 일관성",
            "",
            "| Experiment | 2010_2015 excess | 2016_2020 excess | 2021_2026 excess | Positive subperiods |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for experiment_id, group in subperiod.groupby("experiment", sort=False):
        by_period = group.set_index("period")["excess_cagr_vs_spy"]
        positives = int((by_period > 0).sum())
        lines.append(
            f"| {experiment_id} | {by_period.get('2010_2015', np.nan):.2%} | {by_period.get('2016_2020', np.nan):.2%} | {by_period.get('2021_2026', np.nan):.2%} | {positives}/3 |"
        )
    lines.extend(["", "## Verdict ranking", ""])
    for idx, row in ranking.iterrows():
        lines.append(f"{idx + 1}. {row['experiment']} {row['title']}: Excess CAGR {row['excess_cagr']:.2%}, Sharpe {row['sharpe']:.2f}, IR {row['ir']:.2f}.")
    lines.extend(
        [
            "",
            "## 다음 step",
            "",
            "- Q007 cost validation으로 turnover, 세금, 수수료, 슬리피지를 별도 검증한다.",
            "- Q-family는 별도 US individual-stock fundamental sleeve이며 `P08_IEF30`을 직접 promote하지 않는다.",
            "- 모든 Q002-Q006 결과는 현재 survivor universe 기반이므로 survivorship bias 한계를 유지한다.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
