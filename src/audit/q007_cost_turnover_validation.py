from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data" / "inputs" / "global_etf"
MACRO_DIR = ROOT / "research_input_data" / "inputs" / "macro_features"
Q002_DIR = ROOT / "reports" / "experiments" / "Q002_quality_only"
Q006_DIR = ROOT / "reports" / "experiments" / "Q006_qvsy_composite"
REPORT_DIR = ROOT / "reports" / "experiments" / "Q007_cost_turnover_validation"

START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")
INITIAL_CAPITAL_KRW = 100_000_000.0
ANNUAL_EXEMPTION_NAV = 2_500_000.0 / INITIAL_CAPITAL_KRW
COMMISSION_RATE = 0.0025
CAPITAL_GAINS_TAX_RATE = 0.22
DIVIDEND_WITHHOLDING_RATE = 0.15
FX_SPREAD_RATE = 10.0 / 10_000.0

FACTOR_ETFS = ("SCHD", "COWZ", "MTUM")
DIRECT_Q = {"Q002": Q002_DIR, "Q006": Q006_DIR}
DIVIDEND_YIELDS = {
    "SPY": 0.013,
    "QQQ": 0.005,
    "IEF": 0.035,
    "SCHD": 0.035,
    "COWZ": 0.018,
    "MTUM": 0.007,
    "Q002": 0.015,
    "Q006": 0.015,
}


@dataclass
class Lot:
    shares: float
    cost_basis: float


def main() -> int:
    parser = argparse.ArgumentParser(description="Q007 cost and turnover validation.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    run(args.report_dir)
    return 0


def run(report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)

    direct = build_direct_q_cost_table()
    etf = build_etf_proxy_cost_table()
    comparison = build_comparison_table(direct, etf)

    direct.to_csv(report_dir / "direct_q_cost.csv", index=False)
    etf.to_csv(report_dir / "etf_proxy_cost.csv", index=False)
    comparison.to_csv(report_dir / "comparison.csv", index=False)
    write_report(report_dir / "report.md", direct, etf, comparison)


def build_direct_q_cost_table() -> pd.DataFrame:
    rows = []
    for name, directory in DIRECT_Q.items():
        nav = load_nav(directory / "portfolio_daily_nav.csv")
        turnover = pd.read_csv(directory / "turnover_by_quarter.csv", parse_dates=["execution_date"])
        result = simulate_single_asset_turnover(
            name=name,
            nav=nav,
            turnover=turnover,
            dividend_yield=DIVIDEND_YIELDS[name],
        )
        rows.append(result)
    return pd.DataFrame(rows)


def build_etf_proxy_cost_table() -> pd.DataFrame:
    fx = load_usdkrw()
    rows = []
    for ticker in FACTOR_ETFS:
        curve = load_etf_krw_nav(ticker, fx)
        turnover = pd.DataFrame({"execution_date": [curve.index[0]], "turnover": [0.0]})
        result = simulate_single_asset_turnover(
            name=ticker,
            nav=curve,
            turnover=turnover,
            dividend_yield=DIVIDEND_YIELDS[ticker],
        )
        rows.append({**result, "turnover_policy": "buy_hold_proxy_near_zero"})
    return pd.DataFrame(rows)


def build_comparison_table(direct: pd.DataFrame, etf: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "sleeve",
        "sleeve_type",
        "start_date",
        "end_date",
        "gross_cagr",
        "net_cagr",
        "cagr_drag",
        "gross_sharpe",
        "net_sharpe",
        "gross_mdd",
        "net_mdd",
        "total_cost",
        "commission_cost",
        "capital_gains_tax",
        "fx_spread_cost",
        "dividend_withholding",
        "annual_one_way_turnover",
    ]
    out = pd.concat([direct, etf], ignore_index=True)
    out["cost_impact_rank"] = out["cagr_drag"].rank(method="first", ascending=True).astype(int)
    return out.sort_values(["cagr_drag", "sleeve"]).reset_index(drop=True)[["cost_impact_rank", *cols]]


def load_nav(path: Path) -> pd.Series:
    data = pd.read_csv(path, parse_dates=["date"])
    data["nav"] = pd.to_numeric(data["nav"], errors="coerce")
    data = data.dropna(subset=["date", "nav"]).sort_values("date")
    data = data.loc[data["date"].le(END_DATE)].copy()
    return pd.Series(data["nav"].to_numpy(), index=pd.DatetimeIndex(data["date"]), name=path.parent.name)


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(MACRO_DIR / "fred_dexkous_usdkrw.csv", parse_dates=["observation_date"], na_values=["."])
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})
    data["usdkrw"] = pd.to_numeric(data["usdkrw"], errors="coerce")
    return data.dropna(subset=["date", "usdkrw"]).sort_values("date").reset_index(drop=True)


def load_etf_krw_nav(ticker: str, fx: pd.DataFrame, long: bool = False) -> pd.Series:
    prefix = "yf_factor_" if ticker in FACTOR_ETFS else "yf_"
    suffix = "_long" if long and ticker not in FACTOR_ETFS else ""
    path = ETF_DIR / f"{prefix}{ticker}{suffix}.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    data = data.rename(columns={"Date": "date", "Close": "close_usd"})
    data["close_usd"] = pd.to_numeric(data["close_usd"], errors="coerce")
    data = data.dropna(subset=["date", "close_usd"]).sort_values("date")
    data = pd.merge_asof(data, fx[["date", "usdkrw"]].sort_values("date"), on="date", direction="backward")
    if not long:
        data = data.loc[data["date"].between(START_DATE, END_DATE)].copy()
    data["nav"] = data["close_usd"] * data["usdkrw"]
    data["nav"] = data["nav"] / data["nav"].iloc[0]
    return pd.Series(data["nav"].to_numpy(), index=pd.DatetimeIndex(data["date"]), name=ticker)


def simulate_single_asset_turnover(
    name: str,
    nav: pd.Series,
    turnover: pd.DataFrame,
    dividend_yield: float,
) -> dict[str, object]:
    nav = nav.dropna().sort_index()
    prices = nav / nav.iloc[0]
    turnover_map = {
        pd.Timestamp(row.execution_date): float(row.turnover)
        for row in turnover.itertuples(index=False)
        if pd.Timestamp(row.execution_date) in prices.index
    }
    lots: list[Lot] = []
    shares = 0.0
    cash = 1.0
    annual_net_realized: dict[int, float] = {}
    annual_taxable_paid: dict[int, float] = {}
    cost_rows = []
    values = []

    for i, (date, price) in enumerate(prices.items()):
        if i == 0:
            trade_value = cash / (1.0 + COMMISSION_RATE + FX_SPREAD_RATE)
            shares += trade_value / price
            lots.append(Lot(shares=shares, cost_basis=price))
            commission = trade_value * COMMISSION_RATE
            fx_cost = trade_value * FX_SPREAD_RATE
            cash -= trade_value + commission + fx_cost
            cost_rows.append(cost_row(name, date, "initial_buy", trade_value, 0.0, commission, 0.0, fx_cost, 0.0, 0.0))
        elif date in turnover_map and turnover_map[date] > 0.0:
            pre_nav = cash + shares * price
            one_way = min(max(turnover_map[date], 0.0), 1.0)
            sell_value = min(shares * price, pre_nav * one_way)
            sold_shares, realized = sell_hifo(lots, sell_value, price)
            shares -= sold_shares
            cash += sell_value
            tax = tax_due(date.year, realized, annual_net_realized, annual_taxable_paid)
            buy_value = max(min(cash - tax, pre_nav * one_way), 0.0) / (1.0 + COMMISSION_RATE + FX_SPREAD_RATE)
            buy_shares = buy_value / price
            shares += buy_shares
            lots.append(Lot(shares=buy_shares, cost_basis=price))
            commission = (sell_value + buy_value) * COMMISSION_RATE
            fx_cost = (sell_value + buy_value) * FX_SPREAD_RATE
            cash += -tax - buy_value - commission - fx_cost
            cost_rows.append(cost_row(name, date, "turnover", buy_value, sell_value, commission, tax, fx_cost, 0.0, realized))

        if is_quarter_end(date, prices.index):
            value = cash + shares * price
            dividend_cost = value * dividend_yield / 4.0 * DIVIDEND_WITHHOLDING_RATE
            cash -= dividend_cost
            if dividend_cost:
                cost_rows.append(cost_row(name, date, "dividend_withholding", 0.0, 0.0, 0.0, 0.0, 0.0, dividend_cost, 0.0))
        values.append(cash + shares * price)

    gross_metrics = metrics(prices)
    net = pd.Series(values, index=prices.index, name=name)
    net_metrics = metrics(net)
    costs = pd.DataFrame(cost_rows)
    totals = costs[["commission_cost", "capital_gains_tax", "fx_spread_cost", "dividend_withholding", "total_cost"]].sum()
    return {
        "sleeve": name,
        "sleeve_type": "direct_q_diagnostic" if name in DIRECT_Q else "etf_proxy",
        "start_date": prices.index[0].date().isoformat(),
        "end_date": prices.index[-1].date().isoformat(),
        "gross_cagr": gross_metrics["cagr"],
        "net_cagr": net_metrics["cagr"],
        "cagr_drag": net_metrics["cagr"] - gross_metrics["cagr"],
        "gross_sharpe": gross_metrics["sharpe"],
        "net_sharpe": net_metrics["sharpe"],
        "gross_mdd": gross_metrics["mdd"],
        "net_mdd": net_metrics["mdd"],
        "total_cost": float(totals["total_cost"]),
        "commission_cost": float(totals["commission_cost"]),
        "capital_gains_tax": float(totals["capital_gains_tax"]),
        "fx_spread_cost": float(totals["fx_spread_cost"]),
        "dividend_withholding": float(totals["dividend_withholding"]),
        "annual_one_way_turnover": float(turnover["turnover"].sum() / max(years_between(prices.index[0], prices.index[-1]), 1e-12)),
    }


def sell_hifo(lots: list[Lot], sell_value: float, price: float) -> tuple[float, float]:
    shares_to_sell = sell_value / price if price > 0.0 else 0.0
    realized = 0.0
    sold = 0.0
    lots.sort(key=lambda lot: lot.cost_basis, reverse=True)
    remaining = shares_to_sell
    for lot in list(lots):
        if remaining <= 1e-15:
            break
        take = min(lot.shares, remaining)
        lot.shares -= take
        remaining -= take
        sold += take
        realized += (price - lot.cost_basis) * take
    lots[:] = [lot for lot in lots if lot.shares > 1e-15]
    return sold, realized


def tax_due(
    year: int,
    realized_gain: float,
    annual_net_realized: dict[int, float],
    annual_taxable_paid: dict[int, float],
) -> float:
    annual_net_realized[year] = annual_net_realized.get(year, 0.0) + realized_gain
    taxable_total = max(annual_net_realized[year] - ANNUAL_EXEMPTION_NAV, 0.0)
    previously_taxed = annual_taxable_paid.get(year, 0.0)
    incremental_taxable = max(taxable_total - previously_taxed, 0.0)
    annual_taxable_paid[year] = previously_taxed + incremental_taxable
    return incremental_taxable * CAPITAL_GAINS_TAX_RATE


def cost_row(
    sleeve: str,
    date: pd.Timestamp,
    event: str,
    buy_amount: float,
    sell_amount: float,
    commission: float,
    tax: float,
    fx: float,
    dividend: float,
    realized_gain: float,
) -> dict[str, object]:
    return {
        "sleeve": sleeve,
        "date": date.date().isoformat(),
        "event": event,
        "buy_amount": buy_amount,
        "sell_amount": sell_amount,
        "commission_cost": commission,
        "capital_gains_tax": tax,
        "fx_spread_cost": fx,
        "dividend_withholding": dividend,
        "total_cost": commission + tax + fx + dividend,
        "realized_gain": realized_gain,
    }


def is_quarter_end(date: pd.Timestamp, index: pd.DatetimeIndex) -> bool:
    loc = index.get_loc(date)
    if not isinstance(loc, int):
        raise ValueError("duplicate dates are not supported")
    return loc == len(index) - 1 or index[loc + 1].to_period("Q") != date.to_period("Q")


def metrics(nav: pd.Series) -> dict[str, float]:
    returns = nav.pct_change().fillna(0.0)
    total = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = years_between(nav.index[0], nav.index[-1])
    drawdown = nav / nav.cummax() - 1.0
    std = float(returns.std())
    return {
        "cagr": float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0.0 else float("nan"),
        "sharpe": math.sqrt(252.0) * float(returns.mean()) / std if std > 0.0 else float("nan"),
        "mdd": float(drawdown.min()),
    }


def years_between(start: pd.Timestamp, end: pd.Timestamp) -> float:
    return max((end - start).days / 365.25, 1e-12)


def table_for_report(df: pd.DataFrame, columns: list[str]) -> str:
    work = df.loc[:, columns].copy()
    rendered = []
    for _, row in work.iterrows():
        rendered.append([format_cell(row[col]) for col in columns])
    widths = [
        max(len(str(col)), *(len(row[idx]) for row in rendered)) if rendered else len(str(col))
        for idx, col in enumerate(columns)
    ]
    header = "| " + " | ".join(str(col).ljust(widths[idx]) for idx, col in enumerate(columns)) + " |"
    sep = "| " + " | ".join("-" * widths[idx] for idx in range(len(columns))) + " |"
    body = ["| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(columns))) + " |" for row in rendered]
    return "\n".join([header, sep, *body])


def format_cell(value: object) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        return f"{value:.4f}"
    if isinstance(value, (np.floating,)):
        value = float(value)
        return "nan" if math.isnan(value) else f"{value:.4f}"
    return str(value)


def write_report(path: Path, direct: pd.DataFrame, etf: pd.DataFrame, comparison: pd.DataFrame) -> None:
    best = comparison.sort_values("cagr_drag", ascending=False).iloc[0]
    worst = comparison.sort_values("cagr_drag").iloc[0]
    lines = [
        "# Q007 Cost / Turnover Validation",
        "",
        "Status: GENERATED BY `src.audit.q007_cost_turnover_validation`",
        "",
        "## 범위",
        "",
        "- 목적은 Q008 결합 framework의 cost sanity 확인이다.",
        "- Direct Q002/Q006은 production 검증이 아니라 diagnostic only다.",
        "- 비용 가정은 T-family Scenario B: HIFO, 연 250만 공제, 양도세 22%, 배당 원천징수 15%, FX 10bps, 매매 수수료 0.25% 양방향이다.",
        "- ETF proxy는 standalone buy-hold 진단이며, 실제 Q008에서는 P08_IEF30 분기 리밸런싱 때만 거래한다.",
        "",
        "## Direct Q 진단",
        "",
        table_for_report(
            direct,
            [
                "sleeve",
                "gross_cagr",
                "net_cagr",
                "cagr_drag",
                "gross_sharpe",
                "net_sharpe",
                "annual_one_way_turnover",
                "total_cost",
            ],
        ),
        "",
        "## ETF Proxy 비용 진단",
        "",
        table_for_report(
            etf,
            [
                "sleeve",
                "gross_cagr",
                "net_cagr",
                "cagr_drag",
                "gross_sharpe",
                "net_sharpe",
                "annual_one_way_turnover",
                "total_cost",
            ],
        ),
        "",
        "## Cost 영향 Ranking",
        "",
        table_for_report(
            comparison,
            [
                "cost_impact_rank",
                "sleeve",
                "sleeve_type",
                "gross_cagr",
                "net_cagr",
                "cagr_drag",
                "commission_cost",
                "capital_gains_tax",
                "fx_spread_cost",
                "dividend_withholding",
            ],
        ),
        "",
        "## Verdict",
        "",
        f"- 비용 drag가 가장 작은 후보는 `{best['sleeve']}`이고, 가장 큰 후보는 `{worst['sleeve']}`이다.",
        "- Direct Q002/Q006은 turnover와 survivorship-bias 문제 때문에 production 후보로 승격하지 않는다.",
        "- Q008에서는 ETF proxy 중심으로 결합 후보를 판단하고, direct Q002/Q006은 비교 diagnostic으로만 유지한다.",
        "",
        "## Assumptions",
        "",
        "- Direct Q의 배당 원천징수는 개별 종목 배당 로그가 없어서 연 1.5% proxy yield를 적용했다.",
        "- ETF proxy 배당률은 고정 연율 proxy다. 실제 분배금 재투자 로그가 아니라 cost sanity 목적의 Scenario B 근사다.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
