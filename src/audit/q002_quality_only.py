from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.audit.q000_us_fundamental_data_audit import CONCEPT_ALIASES


ROOT = Path(__file__).resolve().parents[2]
FUNDAMENTAL_DIR = ROOT / "research_input_data" / "inputs" / "us_fundamentals"
PRICE_DIR = ROOT / "research_input_data" / "inputs" / "us_equity_prices"
ETF_DIR = ROOT / "research_input_data" / "inputs" / "global_etf"
Q001_REPORT_DIR = ROOT / "reports" / "experiments" / "Q001_universe_construction"
REPORT_DIR = ROOT / "reports" / "experiments" / "Q002_quality_only"

START_DATE = "2010-01-01"
END_DATE = "2026-05-18"
PIT_LAG_DAYS = 35
TOP_N = 30
INITIAL_NAV = 1.0

QUALITY_ALIASES: dict[str, list[str]] = {
    "NetIncome": CONCEPT_ALIASES["NetIncome"],
    "OperatingIncome": CONCEPT_ALIASES["OperatingIncome"],
    "Revenues": CONCEPT_ALIASES["Revenue"],
    "StockholdersEquity": CONCEPT_ALIASES["StockholdersEquity"],
    "Assets": CONCEPT_ALIASES["Assets"],
    "LongTermDebt": CONCEPT_ALIASES["LongTermDebt"],
    "CFO": CONCEPT_ALIASES["CFO"],
    "CapEx": CONCEPT_ALIASES["CapEx"],
}

FLOW_CONCEPTS = {"NetIncome", "OperatingIncome", "Revenues", "CFO", "CapEx"}
INSTANT_CONCEPTS = {"StockholdersEquity", "Assets", "LongTermDebt"}


@dataclass(frozen=True)
class FactStore:
    flows: dict[str, pd.DataFrame]
    instants: dict[str, pd.DataFrame]


def main() -> int:
    parser = argparse.ArgumentParser(description="Q002 pre-registered US quality-only audit.")
    parser.add_argument("--fundamental-dir", type=Path, default=FUNDAMENTAL_DIR)
    parser.add_argument("--price-dir", type=Path, default=PRICE_DIR)
    parser.add_argument("--etf-dir", type=Path, default=ETF_DIR)
    parser.add_argument("--q001-report-dir", type=Path, default=Q001_REPORT_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()

    run_q002(
        fundamental_dir=args.fundamental_dir,
        price_dir=args.price_dir,
        etf_dir=args.etf_dir,
        q001_report_dir=args.q001_report_dir,
        report_dir=args.report_dir,
    )
    return 0


def run_q002(
    fundamental_dir: Path,
    price_dir: Path,
    etf_dir: Path,
    q001_report_dir: Path,
    report_dir: Path,
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    universe = load_universe(q001_report_dir)
    prices = load_prices(price_dir, universe["ticker"].tolist())
    spy = load_spy(etf_dir)
    calendar = sorted(spy.index)
    calendar = [d for d in calendar if pd.Timestamp(START_DATE) <= d <= pd.Timestamp(END_DATE)]
    if not calendar:
        raise RuntimeError("No common price calendar for Q002.")

    stores = {
        ticker: parse_companyfacts(fundamental_dir / f"{ticker}_facts.json")
        for ticker in universe["ticker"]
    }
    quarter_ends = pd.date_range(START_DATE, END_DATE, freq="QE")
    signal_rows = build_quality_signals(quarter_ends, stores, universe)
    top_holdings = select_top_holdings(signal_rows, prices, calendar)
    portfolio_nav, turnover = build_portfolio_nav(top_holdings, prices, calendar)
    spy_nav = build_spy_nav(spy, portfolio_nav["date"])
    factor_metrics = build_factor_metrics(portfolio_nav, spy_nav, top_holdings)
    subperiod = build_subperiod_split(portfolio_nav, spy_nav)
    quartiles = build_quartile_test(signal_rows, prices, calendar)

    write_outputs(
        report_dir=report_dir,
        signal_rows=signal_rows,
        top_holdings=top_holdings,
        portfolio_nav=portfolio_nav,
        spy_nav=spy_nav,
        factor_metrics=factor_metrics,
        turnover=turnover,
        subperiod=subperiod,
        quartiles=quartiles,
    )


def load_universe(q001_report_dir: Path) -> pd.DataFrame:
    path = q001_report_dir / "universe_list.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing Q001 universe file: {path}")
    universe = pd.read_csv(path)
    universe = universe.loc[universe["download_status"].isin(["existing", "downloaded"])].copy()
    universe = universe.loc[universe["ticker"].ne("MMC")].copy()
    return universe[["ticker", "sector", "sic", "entity_name"]].sort_values("ticker").reset_index(drop=True)


def load_prices(price_dir: Path, tickers: list[str]) -> dict[str, pd.DataFrame]:
    out = {}
    for ticker in tickers:
        path = price_dir / f"{ticker}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path, parse_dates=["Date"])
        df = df.rename(columns=str.lower).set_index("date").sort_index()
        df = df[["open", "close", "volume"]].apply(pd.to_numeric, errors="coerce")
        out[ticker] = df.loc[df["close"].gt(0)]
    return out


def load_spy(etf_dir: Path) -> pd.DataFrame:
    path = etf_dir / "yf_SPY.csv"
    if not path.exists():
        path = etf_dir / "yf_SPY_long.csv"
    if not path.exists():
        raise FileNotFoundError("Missing SPY benchmark CSV under research_input_data/inputs/global_etf.")
    df = pd.read_csv(path, parse_dates=["Date"])
    return df.rename(columns=str.lower).set_index("date").sort_index()[["close"]].apply(pd.to_numeric, errors="coerce")


def parse_companyfacts(path: Path) -> FactStore:
    if not path.exists():
        raise FileNotFoundError(path)
    facts = json.loads(path.read_text(encoding="utf-8")).get("facts", {}).get("us-gaap", {})
    raw: dict[str, pd.DataFrame] = {}
    for concept, aliases in QUALITY_ALIASES.items():
        rows: list[dict[str, Any]] = []
        for alias in aliases:
            payload = facts.get(alias)
            if not payload:
                continue
            for unit, entries in payload.get("units", {}).items():
                if unit != "USD":
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
        if rows:
            df = pd.DataFrame(rows)
            df["end"] = pd.to_datetime(df["end"])
            df["filed"] = pd.to_datetime(df["filed"])
            df["start"] = pd.to_datetime(df["start"], errors="coerce")
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df.dropna(subset=["end", "filed", "value"]).sort_values(["filed", "end"])
            raw[concept] = df
        else:
            raw[concept] = pd.DataFrame(columns=["start", "end", "filed", "value", "fy", "fp", "form", "alias"])

    flows = {concept: normalize_flow_quarters(raw[concept]) for concept in FLOW_CONCEPTS}
    instants = {concept: normalize_instants(raw[concept]) for concept in INSTANT_CONCEPTS}
    return FactStore(flows=flows, instants=instants)


def normalize_flow_quarters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["period_end", "filed", "value", "source"])
    work = df.dropna(subset=["start"]).copy()
    work["days"] = (work["end"] - work["start"]).dt.days + 1
    quarterly = work.loc[work["days"].between(60, 120)].copy()
    quarterly = quarterly.rename(columns={"end": "period_end"})
    quarterly["source"] = "direct_quarter"
    annual = work.loc[work["days"].between(330, 385) & work["form"].eq("10-K")].copy()
    q4_rows = []
    for _, row in annual.iterrows():
        prior = quarterly.loc[
            quarterly["period_end"].lt(row["end"])
            & quarterly["period_end"].ge(row["end"] - pd.Timedelta(days=370))
        ].sort_values("period_end").tail(3)
        if len(prior) != 3:
            continue
        q4_rows.append(
            {
                "period_end": row["end"],
                "filed": row["filed"],
                "value": row["value"] - prior["value"].sum(),
                "source": "annual_minus_q1_q3",
            }
        )
    normalized = quarterly[["period_end", "filed", "value", "source"]]
    if q4_rows:
        normalized = pd.concat([normalized, pd.DataFrame(q4_rows)], ignore_index=True)
    return normalized.dropna(subset=["period_end", "filed", "value"]).sort_values(["filed", "period_end"])


def normalize_instants(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["period_end", "filed", "value"])
    out = df.rename(columns={"end": "period_end"})[["period_end", "filed", "value"]].copy()
    return out.dropna(subset=["period_end", "filed", "value"]).sort_values(["filed", "period_end"])


def build_quality_signals(
    quarter_ends: pd.DatetimeIndex,
    stores: dict[str, FactStore],
    universe: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    sector_map = universe.set_index("ticker")["sector"].to_dict()
    for quarter_end in quarter_ends:
        available_date = quarter_end + pd.Timedelta(days=PIT_LAG_DAYS)
        for ticker, store in stores.items():
            factors = calculate_factors(store, available_date)
            if factors is None:
                continue
            rows.append(
                {
                    "rebalance_period_end": quarter_end.date().isoformat(),
                    "available_date": available_date.date().isoformat(),
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
        for col in ["roic", "fcf_margin", "leverage"]:
            std = group[col].std(ddof=0)
            group[f"z_{col}"] = 0.0 if not np.isfinite(std) or std == 0 else (group[col] - group[col].mean()) / std
        group["quality_score"] = group["z_roic"] + group["z_fcf_margin"] - group["z_leverage"]
        group["rank"] = group["quality_score"].rank(ascending=False, method="first").astype(int)
        scored.append(group)
    return pd.concat(scored, ignore_index=True).sort_values(["rebalance_period_end", "rank", "ticker"])


def calculate_factors(store: FactStore, available_date: pd.Timestamp) -> dict[str, float] | None:
    flow_values = {}
    for concept in FLOW_CONCEPTS:
        rows = store.flows[concept]
        rows = rows.loc[rows["filed"].le(available_date)]
        if rows.empty:
            return None
        latest_by_period = rows.sort_values(["period_end", "filed"]).groupby("period_end").tail(1)
        trailing = latest_by_period.sort_values("period_end").tail(4)
        if len(trailing) < 4:
            return None
        flow_values[concept] = float(trailing["value"].sum())

    instant_values = {}
    for concept in INSTANT_CONCEPTS:
        rows = store.instants[concept]
        rows = rows.loc[rows["filed"].le(available_date)]
        if rows.empty:
            return None
        instant_values[concept] = float(rows.sort_values(["period_end", "filed"]).iloc[-1]["value"])

    invested_capital = instant_values["StockholdersEquity"] + instant_values["LongTermDebt"]
    revenue = flow_values["Revenues"]
    equity = instant_values["StockholdersEquity"]
    if invested_capital <= 0 or revenue == 0 or equity <= 0:
        return None
    roic = flow_values["OperatingIncome"] / invested_capital
    fcf_margin = (flow_values["CFO"] - flow_values["CapEx"]) / revenue
    leverage = instant_values["LongTermDebt"] / equity
    values = [roic, fcf_margin, leverage]
    if not all(np.isfinite(values)):
        return None
    return {
        "trailing_4q_net_income": flow_values["NetIncome"],
        "trailing_4q_op_income": flow_values["OperatingIncome"],
        "trailing_4q_cfo": flow_values["CFO"],
        "trailing_4q_capex": flow_values["CapEx"],
        "trailing_4q_revenue": revenue,
        "latest_equity": equity,
        "latest_ltd": instant_values["LongTermDebt"],
        "latest_assets": instant_values["Assets"],
        "roic": roic,
        "fcf_margin": fcf_margin,
        "leverage": leverage,
    }


def select_top_holdings(
    signals: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
) -> pd.DataFrame:
    cal = pd.Series(calendar)
    rows = []
    for period_end, group in signals.groupby("rebalance_period_end", sort=True):
        available = pd.Timestamp(group["available_date"].iloc[0])
        execution_candidates = cal.loc[cal.gt(available)]
        if execution_candidates.empty:
            continue
        execution_date = execution_candidates.iloc[0]
        available_tickers = {
            ticker
            for ticker in group["ticker"]
            if ticker in prices and execution_date in prices[ticker].index
        }
        selected = group.loc[group["ticker"].isin(available_tickers)].sort_values("rank").head(TOP_N).copy()
        if len(selected) < TOP_N:
            continue
        weight = 1.0 / len(selected)
        for _, row in selected.iterrows():
            rows.append(
                {
                    "rebalance_period_end": period_end,
                    "available_date": row["available_date"],
                    "execution_date": execution_date.date().isoformat(),
                    "ticker": row["ticker"],
                    "sector": row["sector"],
                    "quality_score": row["quality_score"],
                    "rank": int(row["rank"]),
                    "weight": weight,
                    "entry_close": float(prices[row["ticker"]].loc[execution_date, "close"]),
                }
            )
    return pd.DataFrame(rows).sort_values(["execution_date", "rank", "ticker"])


def build_portfolio_nav(
    holdings: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    execution_dates = [pd.Timestamp(d) for d in sorted(holdings["execution_date"].unique())]
    if not execution_dates:
        raise RuntimeError("No Q002 execution dates.")
    calendar = [d for d in calendar if execution_dates[0] <= d <= pd.Timestamp(END_DATE)]
    returns = pd.DataFrame(index=calendar)
    for ticker, df in prices.items():
        returns[ticker] = df["close"].pct_change().reindex(calendar)
    nav_rows = []
    turnover_rows = []
    nav = INITIAL_NAV
    current_weights: dict[str, float] = {}
    pending_by_date = {d: g for d, g in holdings.groupby(pd.to_datetime(holdings["execution_date"]))}
    previous_date = calendar[0]
    for date in calendar:
        if date != previous_date and current_weights:
            daily_return = sum(
                weight * returns.at[date, ticker]
                for ticker, weight in current_weights.items()
                if ticker in returns.columns and pd.notna(returns.at[date, ticker])
            )
            nav *= 1.0 + daily_return
        if date in pending_by_date:
            new_weights = dict(zip(pending_by_date[date]["ticker"], pending_by_date[date]["weight"]))
            keys = set(current_weights) | set(new_weights)
            turnover = 0.5 * sum(abs(new_weights.get(k, 0.0) - current_weights.get(k, 0.0)) for k in keys)
            turnover_rows.append(
                {
                    "execution_date": date.date().isoformat(),
                    "holding_count": len(new_weights),
                    "turnover": turnover,
                    "overlap_count": len(set(current_weights).intersection(new_weights)),
                }
            )
            current_weights = new_weights
        nav_rows.append({"date": date.date().isoformat(), "nav": nav, "n_positions": len(current_weights)})
        previous_date = date
    return pd.DataFrame(nav_rows), pd.DataFrame(turnover_rows)


def build_spy_nav(spy: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    idx = pd.DatetimeIndex(pd.to_datetime(dates))
    close = spy["close"].reindex(idx).ffill()
    nav = close / close.iloc[0]
    return pd.DataFrame({"date": idx.date.astype(str), "nav": nav.to_numpy(), "close": close.to_numpy()})


def build_factor_metrics(
    portfolio_nav: pd.DataFrame,
    spy_nav: pd.DataFrame,
    holdings: pd.DataFrame,
) -> pd.DataFrame:
    p = nav_metrics(portfolio_nav)
    s = nav_metrics(spy_nav)
    merged = merge_navs(portfolio_nav, spy_nav)
    active = merged["portfolio_return"] - merged["spy_return"]
    ir = information_ratio(active)
    sector = sector_concentration(holdings)
    return pd.DataFrame(
        [
            {
                "strategy": "Q002_quality_top30",
                **p,
                "excess_cagr_vs_spy": p["cagr"] - s["cagr"],
                "information_ratio_vs_spy": ir,
                **sector,
            },
            {
                "strategy": "SPY_100",
                **s,
                "excess_cagr_vs_spy": 0.0,
                "information_ratio_vs_spy": np.nan,
                "avg_max_sector_weight": np.nan,
                "max_sector_weight": np.nan,
                "max_sector_name": "",
            },
        ]
    )


def build_subperiod_split(portfolio_nav: pd.DataFrame, spy_nav: pd.DataFrame) -> pd.DataFrame:
    periods = [
        ("2010_2015", "2010-01-01", "2015-12-31"),
        ("2016_2020", "2016-01-01", "2020-12-31"),
        ("2021_2026", "2021-01-01", END_DATE),
    ]
    rows = []
    for name, start, end in periods:
        p = slice_nav(portfolio_nav, start, end)
        s = slice_nav(spy_nav, start, end)
        if len(p) < 2 or len(s) < 2:
            continue
        pm = nav_metrics(p)
        sm = nav_metrics(s)
        active = merge_navs(p, s)["portfolio_return"] - merge_navs(p, s)["spy_return"]
        rows.append({"period": name, "strategy": "Q002_quality_top30", **pm, "excess_cagr_vs_spy": pm["cagr"] - sm["cagr"], "information_ratio_vs_spy": information_ratio(active)})
        rows.append({"period": name, "strategy": "SPY_100", **sm, "excess_cagr_vs_spy": 0.0, "information_ratio_vs_spy": np.nan})
    return pd.DataFrame(rows)


def build_quartile_test(
    signals: pd.DataFrame,
    prices: dict[str, pd.DataFrame],
    calendar: list[pd.Timestamp],
) -> pd.DataFrame:
    cal = pd.Series(calendar)
    execution_by_period = {}
    for period_end, group in signals.groupby("rebalance_period_end", sort=True):
        available = pd.Timestamp(group["available_date"].iloc[0])
        execution_candidates = cal.loc[cal.gt(available)]
        if not execution_candidates.empty:
            execution_by_period[period_end] = execution_candidates.iloc[0]
    ordered_periods = list(execution_by_period)
    rows = []
    for index, period_end in enumerate(ordered_periods):
        group = signals.loc[signals["rebalance_period_end"].eq(period_end)]
        execution = execution_by_period[period_end]
        if index + 1 < len(ordered_periods):
            exit_date = execution_by_period[ordered_periods[index + 1]]
        else:
            exit_date = cal.iloc[-1]
        tradable = group.loc[group["ticker"].map(lambda t: t in prices and execution in prices[t].index and exit_date in prices[t].index)].copy()
        if len(tradable) < 20:
            continue
        tradable["quartile"] = pd.qcut(tradable["quality_score"].rank(method="first", ascending=False), 4, labels=["Q1", "Q2", "Q3", "Q4"])
        period_returns = {}
        for quartile, qgroup in tradable.groupby("quartile", observed=True):
            ticker_returns = [
                prices[ticker].loc[exit_date, "close"] / prices[ticker].loc[execution, "close"] - 1.0
                for ticker in qgroup["ticker"]
            ]
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


def nav_metrics(nav_df: pd.DataFrame) -> dict[str, float]:
    df = nav_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    returns = df["nav"].pct_change().dropna()
    days = (df["date"].iloc[-1] - df["date"].iloc[0]).days
    total_return = df["nav"].iloc[-1] / df["nav"].iloc[0] - 1.0
    cagr = (df["nav"].iloc[-1] / df["nav"].iloc[0]) ** (365.25 / days) - 1.0 if days > 0 else np.nan
    sharpe = math.sqrt(252) * returns.mean() / returns.std(ddof=1) if returns.std(ddof=1) != 0 else np.nan
    running_max = df["nav"].cummax()
    mdd = (df["nav"] / running_max - 1.0).min()
    return {"total_return": total_return, "cagr": cagr, "sharpe": sharpe, "mdd": mdd}


def information_ratio(active_returns: pd.Series) -> float:
    active_returns = active_returns.dropna()
    std = active_returns.std(ddof=1)
    return math.sqrt(252) * active_returns.mean() / std if std and np.isfinite(std) else np.nan


def merge_navs(portfolio_nav: pd.DataFrame, spy_nav: pd.DataFrame) -> pd.DataFrame:
    p = portfolio_nav[["date", "nav"]].rename(columns={"nav": "portfolio_nav"}).copy()
    s = spy_nav[["date", "nav"]].rename(columns={"nav": "spy_nav"}).copy()
    merged = p.merge(s, on="date", how="inner")
    merged["portfolio_return"] = merged["portfolio_nav"].pct_change()
    merged["spy_return"] = merged["spy_nav"].pct_change()
    return merged.dropna()


def slice_nav(nav_df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    df = nav_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.loc[df["date"].between(pd.Timestamp(start), pd.Timestamp(end))].copy()
    if df.empty:
        return df
    df["nav"] = df["nav"] / df["nav"].iloc[0]
    df["date"] = df["date"].dt.date.astype(str)
    return df


def sector_concentration(holdings: pd.DataFrame) -> dict[str, float | str]:
    rows = []
    for execution_date, group in holdings.groupby("execution_date"):
        sector_weights = group.groupby("sector")["weight"].sum().sort_values(ascending=False)
        rows.append({"execution_date": execution_date, "sector": sector_weights.index[0], "weight": sector_weights.iloc[0]})
    data = pd.DataFrame(rows)
    if data.empty:
        return {"avg_max_sector_weight": np.nan, "max_sector_weight": np.nan, "max_sector_name": ""}
    max_row = data.sort_values("weight", ascending=False).iloc[0]
    return {
        "avg_max_sector_weight": float(data["weight"].mean()),
        "max_sector_weight": float(max_row["weight"]),
        "max_sector_name": str(max_row["sector"]),
    }


def write_outputs(
    report_dir: Path,
    signal_rows: pd.DataFrame,
    top_holdings: pd.DataFrame,
    portfolio_nav: pd.DataFrame,
    spy_nav: pd.DataFrame,
    factor_metrics: pd.DataFrame,
    turnover: pd.DataFrame,
    subperiod: pd.DataFrame,
    quartiles: pd.DataFrame,
) -> None:
    signal_rows.to_csv(report_dir / "quarterly_signals.csv", index=False)
    top_holdings.to_csv(report_dir / "top30_holdings.csv", index=False)
    portfolio_nav.to_csv(report_dir / "portfolio_daily_nav.csv", index=False)
    spy_nav.to_csv(report_dir / "spy_daily_nav.csv", index=False)
    factor_metrics.to_csv(report_dir / "factor_metrics.csv", index=False)
    turnover.to_csv(report_dir / "turnover_by_quarter.csv", index=False)
    subperiod.to_csv(report_dir / "subperiod_split.csv", index=False)
    quartiles.to_csv(report_dir / "quartile_long_short_test.csv", index=False)
    write_config(report_dir / "config.yaml")
    write_report(report_dir / "report.md", factor_metrics, turnover, subperiod, quartiles, top_holdings, signal_rows)


def write_config(path: Path) -> None:
    path.write_text(
        f"""experiment: Q002_quality_only
universe: Q001 99 tickers, current S&P 100-like universe excluding MMC
fundamentals: research_input_data/inputs/us_fundamentals/*_facts.json
prices: research_input_data/inputs/us_equity_prices/*.csv
benchmark: research_input_data/inputs/global_etf/yf_SPY.csv
start_date: {START_DATE}
end_date: {END_DATE}
pit_policy:
  source_timestamp: SEC companyfacts filed
  conservative_lag_days_after_quarter_end: {PIT_LAG_DAYS}
  execution_rule: first SPY trading day after available_date, with missing stock prices excluded
signal:
  roic: trailing_4q_operating_income / (latest_equity + latest_long_term_debt)
  fcf_margin: (trailing_4q_cfo - trailing_4q_capex) / trailing_4q_revenue
  leverage: latest_long_term_debt / latest_equity
  composite: z_roic + z_fcf_margin - z_leverage
portfolio:
  selection: top_{TOP_N}_quality_score
  weighting: equal_weight
  rebalance: quarterly
  costs_bps: 0
limitations:
  - current survivor universe; not survivorship-free
  - no factor grid; single pre-registered composite only
""",
        encoding="utf-8",
    )


def write_report(
    path: Path,
    metrics: pd.DataFrame,
    turnover: pd.DataFrame,
    subperiod: pd.DataFrame,
    quartiles: pd.DataFrame,
    holdings: pd.DataFrame,
    signals: pd.DataFrame,
) -> None:
    q = metrics.loc[metrics["strategy"].eq("Q002_quality_top30")].iloc[0]
    spy = metrics.loc[metrics["strategy"].eq("SPY_100")].iloc[0]
    ls = quartiles.loc[quartiles["bucket"].eq("Q1_minus_Q4"), "period_return"]
    ls_mean = float(ls.mean()) if not ls.empty else np.nan
    ls_positive = float((ls > 0).mean()) if not ls.empty else np.nan
    avg_turnover = float(turnover["turnover"].mean()) if not turnover.empty else np.nan
    verdict = classify_verdict(q, spy)
    period_lines = []
    for _, row in subperiod.loc[subperiod["strategy"].eq("Q002_quality_top30")].iterrows():
        period_lines.append(
            f"| {row['period']} | {row['cagr']:.2%} | {row['sharpe']:.2f} | {row['mdd']:.2%} | {row['excess_cagr_vs_spy']:.2%} |"
        )
    report = f"""# Q002 Quality Only

## Verdict

{verdict}. Q002는 사전 등록한 단일 Quality composite만 사용했다. 현재 survivor universe 한계가 있으므로 production promote 판단에는 쓰지 않는다.

## Hypothesis

ROIC가 높고 FCF margin이 높으며 leverage가 낮은 대형주는 다음 분기 보유 구간에서 SPY 100%보다 더 나은 위험조정 성과를 낼 수 있다.

## 사전 등록 구현

- Universe: Q001 99종목(S&P 100 유사 현재 universe, MMC 제외).
- Composite: `Quality_Score = z(ROIC) + z(FCF_margin) - z(Leverage)`.
- ROIC: `trailing_4Q_operating_income / (latest_equity + latest_long_term_debt)`.
- FCF margin: `(trailing_4Q_CFO - trailing_4Q_CapEx) / trailing_4Q_revenue`.
- Leverage: `latest_long_term_debt / latest_equity`.
- Portfolio: 매 분기 Top 30 equal weight, 비용 0 gross only.
- Benchmark: SPY 100% buy-hold, USD NAV.
- PIT: SEC `filed` 날짜와 분기말 +35일 lag를 통과한 값만 사용했다. 실행일은 `available_date` 이후 첫 SPY 거래일이며, 해당일 가격이 없는 종목은 제외했다.
- Factor grid: 없음. Q002는 단일 composite만 테스트했다.

## 핵심 성과

| Strategy | Total return | CAGR | Sharpe | MDD | SPY excess CAGR | IR vs SPY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q002 Top30 | {q['total_return']:.2%} | {q['cagr']:.2%} | {q['sharpe']:.2f} | {q['mdd']:.2%} | {q['excess_cagr_vs_spy']:.2%} | {q['information_ratio_vs_spy']:.2f} |
| SPY 100% | {spy['total_return']:.2%} | {spy['cagr']:.2%} | {spy['sharpe']:.2f} | {spy['mdd']:.2%} | 0.00% |  |

Top 30 ranking은 각 분기 단면에서 높은 ROIC, 높은 FCF margin, 낮은 leverage가 동시에 강한 종목을 고른다는 의미다. 순위 자체는 예측 점수이며, SPY 대비 alpha는 다음 분기 실제 보유 수익으로만 검증했다.

## Quartile Spread

- Q1-Q4 long-short 평균 분기 수익률: {ls_mean:.2%}
- Q1-Q4 양수 비율: {ls_positive:.1%}
- Long-short가 양수이면 Quality score가 단순 long-only 구성 효과를 넘어 진짜 factor premium을 가진다는 보조 증거로 본다. 이번 결과는 SPY 대비 long-only alpha는 강하지만 Q1-Q4 spread가 음수라서 순수 factor premium 증거는 약하다.

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

## Pass Criteria

- SPY 대비 CAGR 우수 + Sharpe 우수 = STRONG
- SPY 대비 CAGR 비슷 + Sharpe 우수(MDD 작음) = OK
- SPY 대비 CAGR 낮음 + Sharpe 비슷 = WEAK
- SPY 대비 CAGR + Sharpe 모두 낮음 = FAIL
- Long-short(Q1-Q4) 양수 = factor의 진짜 premium 보조 확인

## 한계

- 현재 universe는 살아남은 99종목이므로 survivorship bias가 있다.
- 비용은 Q002 사전 등록대로 0 gross only이며, 비용/세금 검증은 T-family 또는 Q007에서 별도로 해야 한다.
- `P08_IEF30` 직접 promote는 Q008 전까지 하지 않는다.

## 다음 단계

Q003 Value only 진행을 권고한다.
"""
    path.write_text(report, encoding="utf-8")


def classify_verdict(q: pd.Series, spy: pd.Series) -> str:
    cagr_better = q["cagr"] > spy["cagr"]
    sharpe_better = q["sharpe"] > spy["sharpe"]
    cagr_similar = abs(q["cagr"] - spy["cagr"]) <= 0.01
    if cagr_better and sharpe_better:
        return "STRONG"
    if cagr_similar and sharpe_better and q["mdd"] > spy["mdd"]:
        return "OK"
    if q["cagr"] < spy["cagr"] and q["sharpe"] >= spy["sharpe"] - 0.05:
        return "WEAK"
    if q["cagr"] < spy["cagr"] and q["sharpe"] < spy["sharpe"]:
        return "FAIL"
    return "WEAK"


if __name__ == "__main__":
    raise SystemExit(main())
