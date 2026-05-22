from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")

ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
I0035_DIR = Path("reports/experiments/I003_5_static_allocation_frontier")
OUTPUT_DIR = Path("reports/experiments/I005_production_cost_validation")

COMPONENTS = ("SPY", "QQQ", "H001", "IEF")
US_ETFS = ("SPY", "QQQ", "IEF")
WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
REFERENCE_CANDIDATE = "B04_SPY29_QQQ21_H00120_IEF30"
P07_CANDIDATE = "A03_P07_QQQ50_H00130_IEF20"
P08_CANDIDATE = "B02_P08_SPY40_QQQ30_H00120_IEF10"

INITIAL_CAPITAL_KRW = 100_000_000.0
ANNUAL_CAPITAL_GAIN_EXEMPTION_KRW = 2_500_000.0
ANNUAL_EXEMPTION_NAV = ANNUAL_CAPITAL_GAIN_EXEMPTION_KRW / INITIAL_CAPITAL_KRW
COMMISSION_RATE = 0.0025
CAPITAL_GAINS_TAX_RATE = 0.22
DIVIDEND_WITHHOLDING_RATE = 0.15
DIVIDEND_YIELDS = {"SPY": 0.013, "QQQ": 0.005, "IEF": 0.035}


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    fx_spread_bps: float
    dividend_withholding: bool
    annual_exemption: bool


SCENARIOS = (
    Scenario("A_user", "0.25% commission + 22% tax, FX 0 bps, dividends ignored, no exemption", 0.0, False, False),
    Scenario("B_full", "0.25% commission + 22% tax, FX 10 bps, 15% dividend withholding, no exemption", 10.0, True, False),
    Scenario("C_worst", "0.25% commission + 22% tax, FX 20 bps, 15% dividend withholding, no exemption", 20.0, True, False),
    Scenario("D_best", "0.25% commission + 22% tax, FX 0 bps, dividends ignored, exemption applied", 0.0, False, True),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    component_nav = load_component_nav()
    gross_nav, gross_rebalance_rows = build_gross_nav_and_rebalance_log(component_nav)
    net_results = {scenario.name: simulate_net_nav(component_nav, scenario) for scenario in SCENARIOS}

    daily_nav = pd.DataFrame({"date": gross_nav.index, "gross": gross_nav.values})
    for scenario_name, result in net_results.items():
        daily_nav[scenario_name] = result["nav"].values
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_gross_vs_net.csv", index=False)

    turnover = build_quarterly_turnover(gross_rebalance_rows, net_results)
    turnover.to_csv(OUTPUT_DIR / "quarterly_turnover.csv", index=False)

    attribution = pd.concat([result["costs"] for result in net_results.values()], ignore_index=True)
    attribution.to_csv(OUTPUT_DIR / "cost_attribution.csv", index=False)

    scenario_metrics = build_cost_scenarios(gross_nav, net_results)
    scenario_metrics.to_csv(OUTPUT_DIR / "cost_scenarios.csv", index=False)

    stress = build_stress_net(gross_nav, net_results)
    stress.to_csv(OUTPUT_DIR / "stress_net.csv", index=False)

    write_report(scenario_metrics, turnover, attribution, stress)


def load_component_nav() -> pd.DataFrame:
    fx = load_usdkrw()
    curves = {
        "SPY": build_etf_curve("SPY", fx),
        "QQQ": build_etf_curve("QQQ", fx),
        "IEF": build_etf_curve("IEF", fx),
        "H001": load_h001_curve(),
    }
    calendar = sorted(set().union(*(set(curve["date"]) for curve in curves.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    index = index[(index >= START_DATE) & (index <= END_DATE)]
    aligned = {}
    for component, curve in curves.items():
        series = curve.set_index("date")["net_value"].reindex(index).ffill()
        if series.isna().any():
            first_bad = series.loc[series.isna()].index.min().date()
            raise ValueError(f"{component} has no NAV available on or before {first_bad}")
        aligned[component] = series / series.iloc[0]
    return pd.DataFrame(aligned, index=index)[list(COMPONENTS)]


def load_usdkrw() -> pd.DataFrame:
    path = MACRO_DIR / "fred_dexkous_usdkrw.csv"
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})
    data["usdkrw"] = pd.to_numeric(data["usdkrw"], errors="coerce")
    return data.dropna(subset=["date", "usdkrw"]).sort_values("date").reset_index(drop=True)


def load_etf_prices(ticker: str) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    data = data.rename(columns={"Date": "date", "Close": "close_usd"})
    data["close_usd"] = pd.to_numeric(data["close_usd"], errors="coerce")
    return data.dropna(subset=["date", "close_usd"]).sort_values("date").reset_index(drop=True)


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


def load_h001_curve() -> pd.DataFrame:
    path = H001_DIR / "equity_curve.csv"
    data = pd.read_csv(path, parse_dates=["date"])
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", "net_value"]].copy()
    data["net_value"] = pd.to_numeric(data["net_value"], errors="coerce")
    data = data.dropna(subset=["date", "net_value"]).sort_values("date").reset_index(drop=True)
    data["net_value"] = data["net_value"] / data["net_value"].iloc[0]
    return data


def build_gross_nav_and_rebalance_log(component_nav: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    returns = component_nav.pct_change().fillna(0.0)
    quarter_keys = returns.index.to_period("Q")
    sleeve_values: dict[str, float] | None = None
    last_quarter = None
    values = []
    rebalance_rows = []
    for date, quarter in zip(returns.index, quarter_keys, strict=True):
        if sleeve_values is None:
            sleeve_values = {component: WEIGHTS[component] for component in COMPONENTS}
            rebalance_rows.append(rebalance_row(date, quarter, 1.0, {component: 0.0 for component in COMPONENTS}, sleeve_values))
        elif quarter != last_quarter:
            pre_nav = sum(sleeve_values.values())
            current_weights = {component: sleeve_values[component] / pre_nav for component in COMPONENTS}
            target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
            trades = {component: target_values[component] - sleeve_values[component] for component in COMPONENTS}
            rebalance_rows.append(rebalance_row(date, quarter, pre_nav, trades, target_values, current_weights))
            sleeve_values = target_values
        for component in COMPONENTS:
            sleeve_values[component] *= 1.0 + float(returns.loc[date, component])
        values.append(sum(sleeve_values.values()))
        last_quarter = quarter
    return pd.Series(values, index=returns.index, name="gross"), pd.DataFrame(rebalance_rows)


def rebalance_row(
    date: pd.Timestamp,
    quarter: pd.Period,
    pre_nav: float,
    trades: dict[str, float],
    target_values: dict[str, float],
    current_weights: dict[str, float] | None = None,
) -> dict:
    buys = sum(max(value, 0.0) for value in trades.values())
    sells = sum(max(-value, 0.0) for value in trades.values())
    row = {
        "date": date,
        "quarter": str(quarter),
        "gross_pre_rebalance_nav": pre_nav,
        "one_way_turnover": sum(abs(value) for value in trades.values()) / (2.0 * pre_nav) if pre_nav else 0.0,
        "buy_amount": buys,
        "sell_amount": sells,
    }
    for component in COMPONENTS:
        row[f"{component}_weight_before_rebalance"] = (current_weights or WEIGHTS).get(component, WEIGHTS[component])
        row[f"{component}_target_weight"] = WEIGHTS[component]
        row[f"{component}_buy_amount"] = max(trades[component], 0.0)
        row[f"{component}_sell_amount"] = max(-trades[component], 0.0)
        row[f"{component}_target_value"] = target_values[component]
    return row


def simulate_net_nav(component_nav: pd.DataFrame, scenario: Scenario) -> dict[str, pd.DataFrame | pd.Series]:
    returns = component_nav.pct_change().fillna(0.0)
    quarter_keys = returns.index.to_period("Q")
    prices = component_nav
    shares = {component: 0.0 for component in COMPONENTS}
    avg_cost = {component: 0.0 for component in US_ETFS}
    cash = 0.0
    last_quarter = None
    used_exemption_by_year: dict[int, float] = {}
    values = []
    cost_rows = []

    for date, quarter in zip(returns.index, quarter_keys, strict=True):
        should_rebalance = last_quarter is None or quarter != last_quarter
        pre_nav = cash + sum(shares[component] * float(prices.loc[date, component]) for component in COMPONENTS)
        if should_rebalance:
            if last_quarter is None:
                pre_nav = 1.0
            costs = rebalance_net(date, quarter, scenario, prices.loc[date], pre_nav, shares, avg_cost, used_exemption_by_year)
            post_cost_nav = pre_nav - costs["total_cost"]
            if post_cost_nav <= 0.0:
                raise ValueError(f"{scenario.name} NAV depleted by costs on {date.date()}")
            scale = post_cost_nav / pre_nav
            for component in COMPONENTS:
                shares[component] *= scale
            cash = 0.0
            cost_rows.append(costs)
        if scenario.dividend_withholding and is_quarter_end(date, returns.index):
            nav_before_dividend_cost = cash + sum(
                shares[component] * float(prices.loc[date, component]) for component in COMPONENTS
            )
            dividend_cost = 0.0
            component_values = {component: shares[component] * float(prices.loc[date, component]) for component in COMPONENTS}
            for component in US_ETFS:
                dividend_cost += component_values[component] * DIVIDEND_YIELDS[component] / 4.0 * DIVIDEND_WITHHOLDING_RATE
            if dividend_cost:
                cash -= dividend_cost
                cost_rows.append(
                    {
                        "scenario": scenario.name,
                        "date": date,
                        "quarter": str(quarter),
                        "event": "dividend_withholding",
                        "pre_nav": nav_before_dividend_cost,
                        "one_way_turnover": 0.0,
                        "buy_amount": 0.0,
                        "sell_amount": 0.0,
                        "commission_cost": 0.0,
                        "capital_gains_tax": 0.0,
                        "fx_spread_cost": 0.0,
                        "dividend_withholding": dividend_cost,
                        "total_cost": dividend_cost,
                        "realized_gain": 0.0,
                        "taxable_gain": 0.0,
                        "annual_exemption_used": used_exemption_by_year.get(date.year, 0.0),
                    }
                )
        values.append(cash + sum(shares[component] * float(prices.loc[date, component]) for component in COMPONENTS))
        last_quarter = quarter
    return {"nav": pd.Series(values, index=returns.index, name=scenario.name), "costs": pd.DataFrame(cost_rows)}


def rebalance_net(
    date: pd.Timestamp,
    quarter: pd.Period,
    scenario: Scenario,
    price_row: pd.Series,
    pre_nav: float,
    shares: dict[str, float],
    avg_cost: dict[str, float],
    used_exemption_by_year: dict[int, float],
) -> dict:
    current_values = {component: shares[component] * float(price_row[component]) for component in COMPONENTS}
    target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
    trades = {component: target_values[component] - current_values[component] for component in COMPONENTS}
    buy_amount = sum(max(value, 0.0) for value in trades.values())
    sell_amount = sum(max(-value, 0.0) for value in trades.values())
    commission = (buy_amount + sell_amount) * COMMISSION_RATE
    fx_spread = scenario.fx_spread_bps / 10_000.0
    fx_cost = sum(abs(trades[component]) for component in US_ETFS) * fx_spread
    realized_gain = 0.0
    taxable_gain = 0.0

    for component in COMPONENTS:
        price = float(price_row[component])
        trade_value = trades[component]
        if trade_value < 0.0:
            sell_shares = min(shares[component], -trade_value / price)
            if component in US_ETFS:
                gain = max((price - avg_cost[component]) * sell_shares, 0.0)
                realized_gain += gain
                taxable_part = taxable_gain_after_exemption(gain, date.year, scenario, used_exemption_by_year)
                taxable_gain += taxable_part
            shares[component] -= sell_shares
        elif trade_value > 0.0:
            buy_shares = trade_value / price
            if component in US_ETFS:
                old_shares = shares[component]
                avg_cost[component] = (
                    (avg_cost[component] * old_shares + trade_value) / (old_shares + buy_shares)
                    if old_shares + buy_shares > 0.0
                    else price
                )
            shares[component] += buy_shares

    tax = taxable_gain * CAPITAL_GAINS_TAX_RATE
    return {
        "scenario": scenario.name,
        "date": date,
        "quarter": str(quarter),
        "event": "rebalance",
        "pre_nav": pre_nav,
        "one_way_turnover": sum(abs(value) for value in trades.values()) / (2.0 * pre_nav) if pre_nav else 0.0,
        "buy_amount": buy_amount,
        "sell_amount": sell_amount,
        "commission_cost": commission,
        "capital_gains_tax": tax,
        "fx_spread_cost": fx_cost,
        "dividend_withholding": 0.0,
        "total_cost": commission + tax + fx_cost,
        "realized_gain": realized_gain,
        "taxable_gain": taxable_gain,
        "annual_exemption_used": used_exemption_by_year.get(date.year, 0.0),
    }


def taxable_gain_after_exemption(
    gain: float,
    year: int,
    scenario: Scenario,
    used_exemption_by_year: dict[int, float],
) -> float:
    if gain <= 0.0:
        return 0.0
    if not scenario.annual_exemption:
        return gain
    used = used_exemption_by_year.get(year, 0.0)
    remaining = max(ANNUAL_EXEMPTION_NAV - used, 0.0)
    exempted = min(gain, remaining)
    used_exemption_by_year[year] = used + exempted
    return gain - exempted


def is_quarter_end(date: pd.Timestamp, index: pd.DatetimeIndex) -> bool:
    position = index.get_loc(date)
    if not isinstance(position, int):
        raise ValueError("duplicate date index")
    if position == len(index) - 1:
        return True
    return index[position + 1].to_period("Q") != date.to_period("Q")


def build_quarterly_turnover(gross_rebalance_rows: pd.DataFrame, net_results: dict[str, dict[str, pd.DataFrame | pd.Series]]) -> pd.DataFrame:
    rows = gross_rebalance_rows.copy()
    rows = rows.loc[rows["buy_amount"].gt(0.0) | rows["sell_amount"].gt(0.0)].reset_index(drop=True)
    for scenario, result in net_results.items():
        costs = result["costs"]
        assert isinstance(costs, pd.DataFrame)
        rebalance_costs = costs.loc[costs["event"].eq("rebalance"), ["date", "total_cost"]].rename(
            columns={"total_cost": f"{scenario}_rebalance_cost"}
        )
        rows = rows.merge(rebalance_costs, on="date", how="left")
    return rows


def build_cost_scenarios(gross_nav: pd.Series, net_results: dict[str, dict[str, pd.DataFrame | pd.Series]]) -> pd.DataFrame:
    rows = []
    gross_metrics = metrics_for_nav("Gross_I003_5", gross_nav)
    rows.append(
        {
            "scenario": "Gross_I003_5",
            "description": "I003.5 gross reference, no production cost overlay",
            **gross_metrics,
            "sharpe_delta_vs_gross": 0.0,
            "cagr_delta_vs_gross": 0.0,
            "mdd_delta_vs_gross_pp": 0.0,
            "total_cost": 0.0,
            "commission_cost": 0.0,
            "capital_gains_tax": 0.0,
            "fx_spread_cost": 0.0,
            "dividend_withholding": 0.0,
            "tax_share_of_gross_profit": 0.0,
            "pass_net_sharpe": True,
            "pass_net_cagr": True,
            "pass_mdd_degradation": True,
            "kill_net_sharpe": False,
            "kill_net_cagr": False,
            "kill_tax_over_50pct_profit": False,
        }
    )
    for scenario in SCENARIOS:
        result = net_results[scenario.name]
        nav = result["nav"]
        costs = result["costs"]
        assert isinstance(nav, pd.Series)
        assert isinstance(costs, pd.DataFrame)
        metrics = metrics_for_nav(scenario.name, nav)
        totals = costs[["commission_cost", "capital_gains_tax", "fx_spread_cost", "dividend_withholding", "total_cost"]].sum()
        tax_share = float(totals["capital_gains_tax"] / max(gross_nav.iloc[-1] - gross_nav.iloc[0], 1e-12))
        rows.append(
            {
                "scenario": scenario.name,
                "description": scenario.description,
                **metrics,
                "sharpe_delta_vs_gross": metrics["sharpe"] - gross_metrics["sharpe"],
                "cagr_delta_vs_gross": metrics["cagr"] - gross_metrics["cagr"],
                "mdd_delta_vs_gross_pp": (metrics["max_drawdown"] - gross_metrics["max_drawdown"]) * 100.0,
                "total_cost": float(totals["total_cost"]),
                "commission_cost": float(totals["commission_cost"]),
                "capital_gains_tax": float(totals["capital_gains_tax"]),
                "fx_spread_cost": float(totals["fx_spread_cost"]),
                "dividend_withholding": float(totals["dividend_withholding"]),
                "tax_share_of_gross_profit": tax_share,
                "pass_net_sharpe": metrics["sharpe"] >= 1.0,
                "pass_net_cagr": metrics["cagr"] >= 0.10,
                "pass_mdd_degradation": (metrics["max_drawdown"] - gross_metrics["max_drawdown"]) >= -0.03,
                "kill_net_sharpe": metrics["sharpe"] < 0.90,
                "kill_net_cagr": metrics["cagr"] < 0.08,
                "kill_tax_over_50pct_profit": tax_share >= 0.50,
            }
        )
    return pd.DataFrame(rows)


def metrics_for_nav(name: str, nav: pd.Series) -> dict:
    returns = nav.pct_change().fillna(0.0)
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return {
        "candidate": "P08_IEF30",
        "metric_source": name,
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "cumulative_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "daily_annualized_volatility": float(returns.std()) * math.sqrt(252.0),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), float(returns.std())),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
    }


def build_stress_net(gross_nav: pd.Series, net_results: dict[str, dict[str, pd.DataFrame | pd.Series]]) -> pd.DataFrame:
    rows = []
    reference = load_i0035_references()
    navs = {"Gross_I003_5": gross_nav}
    for scenario, result in net_results.items():
        nav = result["nav"]
        assert isinstance(nav, pd.Series)
        navs[scenario] = nav
    for scenario, nav in navs.items():
        rows.append(stress_covid_row(scenario, nav))
        rows.append(stress_2022_row(scenario, nav))
        rows.append(stress_spike_exclusion_row(scenario, nav))
        rows.extend(stress_subperiod_rows(scenario, nav))
    for key, row in reference.items():
        rows.append(row)
    return pd.DataFrame(rows)


def load_i0035_references() -> dict[str, dict]:
    refs: dict[str, dict] = {}
    covid = pd.read_csv(I0035_DIR / "stress_2020_covid.csv")
    rate = pd.read_csv(I0035_DIR / "stress_2022_rate_shock.csv")
    for label, candidate in (("P07_gross_reference", P07_CANDIDATE), ("P08_gross_reference", P08_CANDIDATE)):
        c = covid.loc[covid["candidate"].eq(candidate)].iloc[0]
        r = rate.loc[rate["candidate"].eq(candidate)].iloc[0]
        refs[f"{label}_covid"] = {
            "scenario": label,
            "stress": "2020_covid",
            "metric": "daily_mdd",
            "value": float(c["daily_mdd"]),
            "start_date": c["window_start"],
            "end_date": c["window_end"],
            "peak_date": c["peak_date"],
            "trough_date": c["trough_date"],
        }
        refs[f"{label}_2022"] = {
            "scenario": label,
            "stress": "2022",
            "metric": "calendar_year_return",
            "value": float(r["calendar_year_return_krw"]),
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "peak_date": "",
            "trough_date": "",
        }
    return refs


def stress_covid_row(scenario: str, nav: pd.Series) -> dict:
    start = pd.Timestamp("2020-02-01")
    end = pd.Timestamp("2020-04-30")
    window = nav.loc[nav.index.to_series().between(start, end)]
    peak_date, trough_date, mdd = peak_to_trough(window)
    return {
        "scenario": scenario,
        "stress": "2020_covid",
        "metric": "daily_mdd",
        "value": mdd,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "peak_date": peak_date.date().isoformat(),
        "trough_date": trough_date.date().isoformat(),
    }


def stress_2022_row(scenario: str, nav: pd.Series) -> dict:
    start = pd.Timestamp("2022-01-01")
    end = pd.Timestamp("2022-12-31")
    return {
        "scenario": scenario,
        "stress": "2022",
        "metric": "calendar_year_return",
        "value": period_return(nav, start, end),
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "peak_date": "",
        "trough_date": "",
    }


def stress_spike_exclusion_row(scenario: str, nav: pd.Series) -> dict:
    filtered = nav.loc[nav.index.year != 2025]
    return {
        "scenario": scenario,
        "stress": "2025_spike_exclusion",
        "metric": "sharpe",
        "value": metrics_for_nav(scenario, filtered)["sharpe"],
        "start_date": filtered.index[0].date().isoformat(),
        "end_date": filtered.index[-1].date().isoformat(),
        "peak_date": "",
        "trough_date": "",
    }


def stress_subperiod_rows(scenario: str, nav: pd.Series) -> list[dict]:
    rows = []
    for period, start, end in (
        ("2010_2017", pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        ("2018_2026", pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
    ):
        window = nav.loc[nav.index.to_series().between(start, end)]
        metric = metrics_for_nav(scenario, window)
        rows.append(
            {
                "scenario": scenario,
                "stress": period,
                "metric": "sharpe",
                "value": metric["sharpe"],
                "start_date": window.index[0].date().isoformat(),
                "end_date": window.index[-1].date().isoformat(),
                "peak_date": "",
                "trough_date": "",
            }
        )
        rows.append(
            {
                "scenario": scenario,
                "stress": period,
                "metric": "cagr",
                "value": metric["cagr"],
                "start_date": window.index[0].date().isoformat(),
                "end_date": window.index[-1].date().isoformat(),
                "peak_date": "",
                "trough_date": "",
            }
        )
    return rows


def peak_to_trough(nav: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp, float]:
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return peak_date, trough_date, float(drawdown.loc[trough_date])


def period_return(nav: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> float:
    window = nav.loc[nav.index.to_series().between(start, end)]
    if window.empty:
        raise ValueError(f"no NAV rows from {start.date()} to {end.date()}")
    return float(window.iloc[-1] / window.iloc[0] - 1.0)


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or math.isnan(denominator):
        return float("nan")
    return numerator / denominator


def write_report(
    scenarios: pd.DataFrame,
    turnover: pd.DataFrame,
    attribution: pd.DataFrame,
    stress: pd.DataFrame,
) -> None:
    net = scenarios.loc[scenarios["scenario"].ne("Gross_I003_5")].copy()
    gross = scenarios.loc[scenarios["scenario"].eq("Gross_I003_5")].iloc[0]
    attr_totals = attribution.groupby("scenario")[
        ["commission_cost", "capital_gains_tax", "fx_spread_cost", "dividend_withholding", "total_cost"]
    ].sum()
    worst = scenarios.loc[scenarios["scenario"].eq("C_worst")].iloc[0]
    full = scenarios.loc[scenarios["scenario"].eq("B_full")].iloc[0]
    stress_superior = net_stress_superior_to_references(stress)
    pass_all_core = bool(
        net["pass_net_sharpe"].all()
        and net["pass_net_cagr"].all()
        and net["pass_mdd_degradation"].all()
        and stress_superior
        and not net[["kill_net_sharpe", "kill_net_cagr", "kill_tax_over_50pct_profit"]].any().any()
    )
    verdict = "production-ready 유지" if pass_all_core else "production-ready 보류"
    recommendation = "I004 candidate 유지" if pass_all_core else "I004 candidate revise 검토"

    lines = [
        "# I005 production cost validation",
        "",
        "## 방법",
        "",
        "- P08_IEF30만 재계산했다: SPY 29% / QQQ 21% / H001 20% / IEF 30%, quarterly rebalance.",
        "- D013, H001 strategy, `engine.py`, 기존 I000-I004 산출물은 수정하지 않았다.",
        f"- 초기자본 가정: {INITIAL_CAPITAL_KRW:,.0f} KRW. 연 양도소득세 공제 {ANNUAL_CAPITAL_GAIN_EXEMPTION_KRW:,.0f} KRW는 normalized NAV {ANNUAL_EXEMPTION_NAV:.6f}로 적용했다.",
        "- US ETF 가격은 기존 I003.5와 같은 KRW 환산 total-return proxy를 사용하고, 배당 원천징수 sensitivity는 별도 비용 차감으로 단순화했다.",
        "",
        "## 분기 turnover 분석",
        "",
        f"- 평균 one-way turnover: {turnover['one_way_turnover'].mean():.6f}",
        f"- 최대 one-way turnover: {turnover['one_way_turnover'].max():.6f}",
        f"- 관측 rebalance 수: {len(turnover)}",
        "",
        markdown_table(turnover[["date", "quarter", "one_way_turnover", "buy_amount", "sell_amount"]].head(10)),
        "",
        "## 비용 attribution",
        "",
        markdown_table(attr_totals.reset_index()),
        "",
        "## 4 scenario 비교",
        "",
        markdown_table(
            scenarios[
                [
                    "scenario",
                    "cagr",
                    "sharpe",
                    "max_drawdown",
                    "cagr_delta_vs_gross",
                    "sharpe_delta_vs_gross",
                    "mdd_delta_vs_gross_pp",
                    "total_cost",
                    "tax_share_of_gross_profit",
                ]
            ]
        ),
        "",
        "## Stress 재검증",
        "",
        markdown_table(
            stress.loc[
                stress["stress"].isin(["2020_covid", "2022", "2025_spike_exclusion"]),
                ["scenario", "stress", "metric", "value", "start_date", "end_date", "peak_date", "trough_date"],
            ]
        ),
        "",
        "## Subperiod 재검증",
        "",
        markdown_table(
            stress.loc[
                stress["stress"].isin(["2010_2017", "2018_2026"]),
                ["scenario", "stress", "metric", "value", "start_date", "end_date"],
            ]
        ),
        "",
        "## Multi-metric framework 재평가",
        "",
        f"- Gross reference: CAGR {gross['cagr']:.6f}, Sharpe {gross['sharpe']:.6f}, MDD {gross['max_drawdown']:.6f}.",
        f"- Full cost Scenario B: CAGR {full['cagr']:.6f}, Sharpe {full['sharpe']:.6f}, MDD {full['max_drawdown']:.6f}.",
        f"- Worst Scenario C: CAGR {worst['cagr']:.6f}, Sharpe {worst['sharpe']:.6f}, MDD {worst['max_drawdown']:.6f}.",
        f"- Net stress가 P07/P08 gross reference보다 우수: {stress_superior}.",
        f"- Core pass criteria all scenarios pass: {pass_all_core}.",
        f"- Kill criteria triggered in any scenario: {bool(net[['kill_net_sharpe', 'kill_net_cagr', 'kill_tax_over_50pct_profit']].any().any())}.",
        "",
        "## Verdict",
        "",
        f"- Verdict: P08_IEF30 {verdict}.",
        f"- 진행 권고: {recommendation}.",
        "- I003.6 long-history host 복귀 대기는 별도 long-history 검증 이슈로 남긴다.",
        "",
        "## Files",
        "",
        "- cost_scenarios.csv",
        "- quarterly_turnover.csv",
        "- cost_attribution.csv",
        "- daily_nav_gross_vs_net.csv",
        "- stress_net.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def net_stress_superior_to_references(stress: pd.DataFrame) -> bool:
    net_scenarios = {scenario.name for scenario in SCENARIOS}
    for stress_name in ("2020_covid", "2022"):
        ref_values = stress.loc[
            stress["scenario"].isin(["P07_gross_reference", "P08_gross_reference"])
            & stress["stress"].eq(stress_name),
            "value",
        ]
        net_values = stress.loc[stress["scenario"].isin(net_scenarios) & stress["stress"].eq(stress_name), "value"]
        if ref_values.empty or net_values.empty:
            return False
        if not (net_values > ref_values.max()).all():
            return False
    return True


def markdown_table(data: pd.DataFrame) -> str:
    if data.empty:
        return "_empty_"
    columns = list(data.columns)
    rows = []
    for _, row in data.iterrows():
        rows.append([format_markdown_value(row[column]) for column in columns])
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def format_markdown_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


if __name__ == "__main__":
    main()
