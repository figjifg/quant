from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import mean, stdev


START_DATE = date(2010, 1, 4)
END_DATE = date(2026, 5, 18)
ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
I005_DIR = Path("reports/experiments/I005_production_cost_validation")
OUTPUT_DIR = Path("reports/experiments/T000_tax_engine_audit")

INITIAL_CAPITAL_KRW = 100_000_000.0
CAPITAL_GAINS_TAX_RATE = 0.22
ANNUAL_EXEMPTION_KRW = 2_500_000.0
COMMISSION_RATE = 0.0025
DIVIDEND_WITHHOLDING_RATE = 0.15
DIVIDEND_YIELDS = {"SPY": 0.013, "QQQ": 0.005, "IEF": 0.035}
COMPONENTS = ("SPY", "QQQ", "H001", "IEF")
US_ETFS = ("SPY", "QQQ", "IEF")
WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    lot_method: str
    annual_exemption: bool
    tax_timing: str
    terminal_liquidation: bool = False


SCENARIOS = (
    Scenario("T000-B", "FIFO + 250만원 공제, immediate tax, ongoing NAV", "FIFO", True, "immediate"),
    Scenario("T000-C", "HIFO + 250만원 공제, immediate tax, ongoing NAV", "HIFO", True, "immediate"),
    Scenario("T000-D", "FIFO + 250만원 공제, terminal liquidation tax 포함", "FIFO", True, "immediate", True),
    Scenario("T000-E", "FIFO + 250만원 공제, 다음 해 5월 납부", "FIFO", True, "annual_may"),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_price_panel()
    i005_nav = read_csv_rows(I005_DIR / "daily_nav_gross_vs_net.csv")
    i005_costs = read_csv_rows(I005_DIR / "cost_scenarios.csv")
    results = {scenario.name: simulate_lot_scenario(prices, scenario) for scenario in SCENARIOS}

    tax_scenarios = build_tax_scenarios(i005_nav, i005_costs, results)
    write_csv(OUTPUT_DIR / "tax_scenarios.csv", tax_scenarios)
    write_csv(OUTPUT_DIR / "lot_ledger.csv", concat_results(results, "lot_ledger"))
    realized = concat_results(results, "realized_by_year")
    unrealized = concat_results(results, "unrealized_by_year")
    taxes = concat_results(results, "tax_paid_by_year")
    write_csv(OUTPUT_DIR / "realized_gain_by_year.csv", realized)
    write_csv(OUTPUT_DIR / "unrealized_gain_by_year.csv", unrealized)
    write_csv(OUTPUT_DIR / "tax_paid_by_year.csv", taxes)
    cross_check = build_i005_cross_check(i005_costs, tax_scenarios, taxes)
    write_csv(OUTPUT_DIR / "i005_cross_check.csv", cross_check)
    write_report(tax_scenarios, cross_check, taxes)


def load_price_panel() -> list[dict]:
    fx = [(parse_date(row["observation_date"]), to_float(row["DEXKOUS"])) for row in read_csv_rows(MACRO_DIR / "fred_dexkous_usdkrw.csv")]
    fx = [(d, v) for d, v in fx if v is not None]
    etf_data = {ticker: load_etf_with_fx(ticker, fx) for ticker in US_ETFS}
    h001 = {parse_date(row["date"]): to_float(row["net_value"]) for row in read_csv_rows(H001_DIR / "equity_curve.csv")}
    calendar = sorted(set(h001).union(*(set(data) for data in etf_data.values())))
    calendar = [d for d in calendar if START_DATE <= d <= END_DATE]
    h001_aligned = ffill_series(calendar, h001)
    first_h001 = h001_aligned[calendar[0]]

    rows = []
    aligned_etfs = {ticker: ffill_series(calendar, etf_data[ticker]) for ticker in US_ETFS}
    for d in calendar:
        row = {"date": d}
        ok = True
        for ticker in US_ETFS:
            value = aligned_etfs[ticker].get(d)
            if value is None:
                ok = False
                break
            row[f"{ticker}_close_usd"] = value["close_usd"]
            row[f"{ticker}_usdkrw"] = value["usdkrw"]
            row[f"{ticker}_price_krw"] = value["close_usd"] * value["usdkrw"]
        if not ok or h001_aligned.get(d) is None:
            continue
        row["H001_price_krw"] = h001_aligned[d] / first_h001 * 10_000.0
        rows.append(row)
    return rows


def load_etf_with_fx(ticker: str, fx: list[tuple[date, float]]) -> dict[date, dict]:
    prices = []
    for row in read_csv_rows(ETF_DIR / f"yf_{ticker}.csv"):
        close = to_float(row["Close"])
        if close is not None:
            prices.append((parse_date(row["Date"]), close))
    prices.sort()
    fx.sort()
    out = {}
    fx_pos = 0
    last_fx = None
    for d, close in prices:
        while fx_pos < len(fx) and fx[fx_pos][0] <= d:
            last_fx = fx[fx_pos][1]
            fx_pos += 1
        if last_fx is not None and START_DATE <= d <= END_DATE:
            out[d] = {"close_usd": close, "usdkrw": last_fx}
    return out


def simulate_lot_scenario(prices: list[dict], scenario: Scenario) -> dict:
    cash = INITIAL_CAPITAL_KRW
    lots = {component: [] for component in COMPONENTS}
    lot_id = 0
    last_quarter = None
    nav = []
    ledger = []
    realized_by_year_sleeve = {}
    taxable_base_paid_by_year = {}
    annual_tax_liability = {}
    paid_annual_years = set()
    tax_events = []

    for idx, row in enumerate(prices):
        d = row["date"]
        quarter = quarter_key(d)
        if scenario.tax_timing == "annual_may":
            cash -= pay_due_annual_tax(d, annual_tax_liability, paid_annual_years, tax_events, scenario.name)
            if idx > 0 and d.year != prices[idx - 1]["date"].year:
                previous_year = d.year - 1
                annual_tax_liability[previous_year] = annual_tax_due(realized_by_year_sleeve, previous_year, scenario.annual_exemption)

        if last_quarter is None or quarter != last_quarter:
            cash, lot_id = rebalance(
                d,
                row,
                scenario,
                cash,
                lots,
                lot_id,
                ledger,
                realized_by_year_sleeve,
                taxable_base_paid_by_year,
                tax_events,
            )

        if is_quarter_end(prices, idx):
            tax = dividend_withholding(lots, row)
            tax_events.append(tax_event(scenario.name, d.year, d, 0.0, tax, "dividend_withholding"))

        nav.append({"date": d, "nav": portfolio_value(cash, lots, row) / INITIAL_CAPITAL_KRW})
        last_quarter = quarter

    if scenario.tax_timing == "annual_may":
        for year in sorted({year for year, _ in realized_by_year_sleeve}):
            annual_tax_liability.setdefault(year, annual_tax_due(realized_by_year_sleeve, year, scenario.annual_exemption))
        for year, tax in annual_tax_liability.items():
            if year not in paid_annual_years and tax > 0:
                cash -= tax
                tax_events.append(tax_event(scenario.name, year, prices[-1]["date"], tax, 0.0, "annual_tax_forced_final_payment"))
        nav[-1]["nav"] = portfolio_value(cash, lots, prices[-1]) / INITIAL_CAPITAL_KRW

    if scenario.terminal_liquidation:
        tax = terminal_liquidation_tax(
            lots,
            prices[-1],
            prices[-1]["date"].year,
            realized_by_year_sleeve,
            taxable_base_paid_by_year,
            scenario.annual_exemption,
        )
        nav[-1]["nav"] -= tax / INITIAL_CAPITAL_KRW
        tax_events.append(tax_event(scenario.name, prices[-1]["date"].year, prices[-1]["date"], tax, 0.0, "terminal_liquidation_tax"))

    return {
        "nav": nav,
        "lot_ledger": ledger,
        "realized_by_year": summarize_realized(scenario.name, realized_by_year_sleeve),
        "unrealized_by_year": summarize_unrealized(scenario.name, lots, prices),
        "tax_paid_by_year": summarize_tax_paid(scenario.name, tax_events),
    }


def rebalance(d, row, scenario, cash, lots, lot_id, ledger, realized_by_year_sleeve, taxable_base_paid_by_year, tax_events):
    pre_nav = portfolio_value(cash, lots, row)
    current_values = {component: holding_value(lots[component], row, component) for component in COMPONENTS}
    target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
    trades = {component: target_values[component] - current_values[component] for component in COMPONENTS}
    commission = sum(abs(value) for value in trades.values()) * COMMISSION_RATE

    for component in COMPONENTS:
        trade_value = trades[component]
        price = component_price(row, component)
        if trade_value < -1e-9:
            qty = min(sum(lot["qty_open"] for lot in lots[component]), -trade_value / price)
            cash += sell_lots(d, component, qty, price, row, scenario, lots, ledger, realized_by_year_sleeve)

    capital_tax = 0.0
    if scenario.tax_timing == "immediate":
        capital_tax = immediate_tax_due(realized_by_year_sleeve, d.year, taxable_base_paid_by_year, scenario.annual_exemption)
        if capital_tax:
            tax_events.append(tax_event(scenario.name, d.year, d, capital_tax, 0.0, "immediate_capital_gains_tax"))
    cash -= commission + capital_tax

    for component in COMPONENTS:
        trade_value = trades[component]
        price = component_price(row, component)
        if trade_value > 1e-9:
            qty = trade_value / price
            lot_id += 1
            lot = make_lot(lot_id, d, component, qty, price, row)
            lots[component].append(lot)
            cash -= qty * price
            ledger.append(ledger_row(scenario.name, "BUY", lot, d, qty, price, row, 0.0))
    return cash, lot_id


def sell_lots(d, component, qty_to_sell, sell_price, row, scenario, lots, ledger, realized_by_year_sleeve):
    selected = sorted(lots[component], key=lambda lot: lot["buy_price_krw"], reverse=True) if scenario.lot_method == "HIFO" else sorted(lots[component], key=lambda lot: lot["buy_date"])
    remaining = qty_to_sell
    proceeds = 0.0
    for lot in selected:
        if remaining <= 1e-12:
            break
        qty = min(lot["qty_open"], remaining)
        lot["qty_open"] -= qty
        remaining -= qty
        proceeds += qty * sell_price
        gain = 0.0
        if component in US_ETFS:
            gain = (sell_price - lot["buy_price_krw"]) * qty
            key = (d.year, component)
            realized_by_year_sleeve[key] = realized_by_year_sleeve.get(key, 0.0) + gain
        ledger.append(ledger_row(scenario.name, "SELL", lot, d, qty, sell_price, row, gain))
    lots[component] = [lot for lot in lots[component] if lot["qty_open"] > 1e-12]
    return proceeds


def immediate_tax_due(realized_by_year_sleeve, year, taxable_base_paid_by_year, annual_exemption):
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    taxable_base = max(total - (ANNUAL_EXEMPTION_KRW if annual_exemption else 0.0), 0.0)
    incremental = max(taxable_base - taxable_base_paid_by_year.get(year, 0.0), 0.0)
    taxable_base_paid_by_year[year] = taxable_base_paid_by_year.get(year, 0.0) + incremental
    return incremental * CAPITAL_GAINS_TAX_RATE


def annual_tax_due(realized_by_year_sleeve, year, annual_exemption):
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    return max(total - (ANNUAL_EXEMPTION_KRW if annual_exemption else 0.0), 0.0) * CAPITAL_GAINS_TAX_RATE


def pay_due_annual_tax(d, annual_tax_liability, paid_annual_years, tax_events, scenario):
    due_year = d.year - 1
    if d.month < 5 or due_year in paid_annual_years:
        return 0.0
    tax = annual_tax_liability.get(due_year, 0.0)
    paid_annual_years.add(due_year)
    if tax > 0:
        tax_events.append(tax_event(scenario, due_year, d, tax, 0.0, "annual_may_capital_gains_tax"))
    return tax


def terminal_liquidation_tax(lots, row, year, realized_by_year_sleeve, taxable_base_paid_by_year, annual_exemption):
    unrealized = 0.0
    for component in US_ETFS:
        price = component_price(row, component)
        for lot in lots[component]:
            unrealized += (price - lot["buy_price_krw"]) * lot["qty_open"]
    realized_this_year = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    total_base = max(realized_this_year + unrealized - (ANNUAL_EXEMPTION_KRW if annual_exemption else 0.0), 0.0)
    unpaid_base = max(total_base - taxable_base_paid_by_year.get(year, 0.0), 0.0)
    return unpaid_base * CAPITAL_GAINS_TAX_RATE


def summarize_realized(scenario, realized_by_year_sleeve):
    rows = []
    for year in sorted({year for year, _ in realized_by_year_sleeve}):
        row = {"scenario": scenario, "year": year}
        total = 0.0
        for sleeve in US_ETFS:
            value = realized_by_year_sleeve.get((year, sleeve), 0.0)
            row[f"{sleeve}_realized_gain_krw"] = value
            total += value
        row["us_etf_net_realized_gain_krw"] = total
        row["H001_taxable_realized_gain_krw"] = 0.0
        rows.append(row)
    return rows


def summarize_unrealized(scenario, lots, prices):
    rows = []
    for idx, row in enumerate(prices):
        if idx + 1 < len(prices) and prices[idx + 1]["date"].year == row["date"].year:
            continue
        out = {"scenario": scenario, "year": row["date"].year, "date": row["date"].isoformat()}
        total = 0.0
        for component in US_ETFS:
            value = 0.0
            price = component_price(row, component)
            for lot in lots[component]:
                if lot["buy_date"] <= row["date"]:
                    value += (price - lot["buy_price_krw"]) * lot["qty_open"]
            out[f"{component}_unrealized_gain_krw"] = value
            total += value
        out["us_etf_unrealized_gain_krw"] = total
        rows.append(out)
    return rows


def summarize_tax_paid(scenario, tax_events):
    grouped = {}
    for event in tax_events:
        key = event["tax_year"]
        grouped.setdefault(key, {"scenario": scenario, "tax_year": key, "capital_gains_tax_krw": 0.0, "dividend_withholding_krw": 0.0, "total_tax_paid_krw": 0.0})
        for col in ("capital_gains_tax_krw", "dividend_withholding_krw", "total_tax_paid_krw"):
            grouped[key][col] += event[col]
    return [grouped[key] for key in sorted(grouped)]


def build_tax_scenarios(i005_nav, i005_costs, results):
    nav_dates = [parse_date(row["date"]) for row in i005_nav]
    gross = [{"date": d, "nav": to_float(row["gross"])} for d, row in zip(nav_dates, i005_nav, strict=True)]
    a_user = [{"date": d, "nav": to_float(row["A_user"])} for d, row in zip(nav_dates, i005_nav, strict=True)]
    rows = [
        {"scenario": "Gross_I003_5", "description": "I003.5 gross reference", **metrics_for_nav(gross)},
        {"scenario": "I005_Scenario_A", "description": "I005 reported Scenario A", **i005_metric_row(i005_costs, "A_user")},
        {"scenario": "T000-A", "description": "I005 reproduction from saved daily NAV", **metrics_for_nav(a_user)},
    ]
    for scenario in SCENARIOS:
        rows.append({"scenario": scenario.name, "description": scenario.description, **metrics_for_nav(results[scenario.name]["nav"])})
    gross_row = rows[0]
    for row in rows:
        row["cagr_delta_vs_gross"] = row["cagr"] - gross_row["cagr"]
        row["sharpe_delta_vs_gross"] = row["sharpe"] - gross_row["sharpe"]
        row["mdd_delta_vs_gross_pp"] = (row["max_drawdown"] - gross_row["max_drawdown"]) * 100.0
    return rows


def i005_metric_row(rows, scenario):
    row = next(row for row in rows if row["scenario"] == scenario)
    return {
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "cumulative_return": to_float(row["cumulative_return"]),
        "cagr": to_float(row["cagr"]),
        "daily_annualized_volatility": to_float(row["daily_annualized_volatility"]),
        "sharpe": to_float(row["sharpe"]),
        "max_drawdown": to_float(row["max_drawdown"]),
    }


def metrics_for_nav(nav):
    values = [row["nav"] for row in nav]
    dates = [row["date"] for row in nav]
    returns = [0.0] + [values[i] / values[i - 1] - 1.0 for i in range(1, len(values))]
    total_return = values[-1] / values[0] - 1.0
    years = (dates[-1] - dates[0]).days / 365.25
    running_max = values[0]
    drawdowns = []
    for value in values:
        running_max = max(running_max, value)
        drawdowns.append(value / running_max - 1.0)
    sd = stdev(returns) if len(returns) > 1 else 0.0
    return {
        "start_date": dates[0].isoformat(),
        "end_date": dates[-1].isoformat(),
        "cumulative_return": total_return,
        "cagr": (1.0 + total_return) ** (1.0 / years) - 1.0,
        "daily_annualized_volatility": sd * math.sqrt(252.0),
        "sharpe": (mean(returns) * math.sqrt(252.0) / sd) if sd else math.nan,
        "max_drawdown": min(drawdowns),
    }


def build_i005_cross_check(i005_costs, tax_scenarios, taxes):
    i005_a = next(row for row in i005_costs if row["scenario"] == "A_user")
    t000_a = next(row for row in tax_scenarios if row["scenario"] == "T000-A")
    totals = {}
    for row in taxes:
        totals[row["scenario"]] = totals.get(row["scenario"], 0.0) + row["capital_gains_tax_krw"]
    return [
        {
            "check": "T000-A vs I005 Scenario A",
            "i005_cagr": to_float(i005_a["cagr"]),
            "t000_cagr": t000_a["cagr"],
            "cagr_diff": t000_a["cagr"] - to_float(i005_a["cagr"]),
            "i005_sharpe": to_float(i005_a["sharpe"]),
            "t000_sharpe": t000_a["sharpe"],
            "sharpe_diff": t000_a["sharpe"] - to_float(i005_a["sharpe"]),
            "i005_capital_gains_tax_krw": to_float(i005_a["capital_gains_tax"]) * INITIAL_CAPITAL_KRW,
            "t000_b_capital_gains_tax_krw": totals.get("T000-B", 0.0),
            "finding": "T000-A is sourced from I005 daily NAV; FIFO/HIFO lot scenarios are separate audit extensions.",
        }
    ]


def write_report(scenarios, cross_check, taxes):
    by_scenario = {row["scenario"]: row for row in scenarios}
    tax_totals = {}
    for row in taxes:
        tax_totals.setdefault(row["scenario"], {"scenario": row["scenario"], "capital_gains_tax_krw": 0.0, "dividend_withholding_krw": 0.0, "total_tax_paid_krw": 0.0})
        for col in ("capital_gains_tax_krw", "dividend_withholding_krw", "total_tax_paid_krw"):
            tax_totals[row["scenario"]][col] += row[col]
    hifo_delta = tax_totals["T000-C"]["capital_gains_tax_krw"] - tax_totals["T000-B"]["capital_gains_tax_krw"]
    a, b, c, d, e = (by_scenario[key] for key in ("T000-A", "T000-B", "T000-C", "T000-D", "T000-E"))
    check = cross_check[0]
    lines = [
        "# T000 tax engine audit",
        "",
        "## I005 세금 모델 audit 결과",
        "",
        "- 판정: 보완 필요.",
        "- I005 Scenario A는 22% 해외 ETF 양도세를 적용하고, H001에는 양도세를 적용하지 않는다.",
        f"- T000-A sanity check CAGR diff {check['cagr_diff']:.12f}, Sharpe diff {check['sharpe_diff']:.12f}.",
        "- I005 누락/단순화 항목: FIFO/HIFO lot accounting 명시 없음, 연간 손익통산 사후 정산 없음, terminal liquidation tax 없음, Scenario A 배당 원천징수 제외.",
        "- FX taxable gain은 원화 매수가/매도가 기준으로 계산되어 USD 가격 변동과 USDKRW 환차익이 과세 base에 함께 포함된다.",
        "",
        "## Scenario 비교",
        "",
        markdown_table(scenarios, ["scenario", "cagr", "sharpe", "max_drawdown", "cagr_delta_vs_gross", "sharpe_delta_vs_gross", "mdd_delta_vs_gross_pp"]),
        "",
        "## 250만원 공제 효과",
        "",
        f"- T000-A CAGR {a['cagr']:.6f} vs T000-B CAGR {b['cagr']:.6f}; delta {b['cagr'] - a['cagr']:.6f}.",
        f"- T000-A final NAV {1.0 + a['cumulative_return']:.6f} vs T000-B final NAV {1.0 + b['cumulative_return']:.6f}.",
        "",
        "## Lot accounting 효과",
        "",
        f"- FIFO T000-B CAGR {b['cagr']:.6f}, HIFO T000-C CAGR {c['cagr']:.6f}, delta {c['cagr'] - b['cagr']:.6f}.",
        f"- HIFO capital gains tax delta vs FIFO: {hifo_delta:,.0f} KRW.",
        "",
        "## Terminal liquidation 효과",
        "",
        f"- Ongoing FIFO T000-B final NAV {1.0 + b['cumulative_return']:.6f}.",
        f"- Liquidation T000-D final NAV {1.0 + d['cumulative_return']:.6f}; delta {d['cumulative_return'] - b['cumulative_return']:.6f}.",
        "",
        "## Tax timing 효과",
        "",
        f"- Immediate T000-B CAGR {b['cagr']:.6f}, annual May T000-E CAGR {e['cagr']:.6f}, delta {e['cagr'] - b['cagr']:.6f}.",
        "",
        "## 세금/손익 추적",
        "",
        markdown_table(list(tax_totals.values()), ["scenario", "capital_gains_tax_krw", "dividend_withholding_krw", "total_tax_paid_krw"]),
        "",
        "## Audit 발견 사항",
        "",
        "- I005의 250만원 공제: Scenario A는 미적용, Scenario D_best는 적용.",
        "- 손익통산: T000은 SPY/QQQ/IEF 연도별 net realized gain을 별도 산출한다.",
        "- Terminal tax: I005에는 없음. T000-D에서 별도 측정.",
        "- Lot accounting: I005는 average-cost 단순 모델이며 FIFO/HIFO 선택이 명시되어 있지 않다.",
        "- 배당: T000은 배당 원천징수를 별도 세목으로 추적하고 양도세 base에는 포함하지 않는다. A/B/C/D/E NAV 비교는 250만원 공제, lot accounting, terminal tax, tax timing 효과를 isolate하기 위해 배당세를 NAV에서 차감하지 않았다.",
        "",
        "## Verdict",
        "",
        "- Verdict: I005 모델 보완 필요.",
        "- I005의 30.5pp 양도세 차감은 Scenario A 정의 안에서는 재현되지만, 한국 거주자 일반계좌 세무 모델로는 lot accounting, 연간 손익통산, terminal liquidation, 납부시점 구분이 보완되어야 한다.",
        "- T001 진행 권고: rebalance frequency vs tax.",
        "",
        "## Files",
        "",
        "- tax_scenarios.csv",
        "- lot_ledger.csv",
        "- realized_gain_by_year.csv",
        "- unrealized_gain_by_year.csv",
        "- tax_paid_by_year.csv",
        "- i005_cross_check.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_lot(lot_id, d, component, qty, price, row):
    return {
        "lot_id": lot_id,
        "component": component,
        "buy_date": d,
        "qty_bought": qty,
        "qty_open": qty,
        "buy_price_krw": price,
        "buy_price_usd": row.get(f"{component}_close_usd", ""),
        "buy_usdkrw": row.get(f"{component}_usdkrw", ""),
    }


def ledger_row(scenario, event, lot, d, qty, price, row, realized_gain):
    component = lot["component"]
    return {
        "scenario": scenario,
        "event": event,
        "lot_id": lot["lot_id"],
        "sleeve": component,
        "buy_date": lot["buy_date"].isoformat(),
        "event_date": d.isoformat(),
        "qty": qty,
        "qty_open_after_event": lot["qty_open"],
        "buy_price_usd": lot["buy_price_usd"],
        "buy_price_krw": lot["buy_price_krw"],
        "event_price_usd": row.get(f"{component}_close_usd", ""),
        "event_price_krw": price,
        "realized_gain_krw": realized_gain,
    }


def tax_event(scenario, tax_year, payment_date, capital, dividend, event):
    return {
        "scenario": scenario,
        "tax_year": tax_year,
        "payment_date": payment_date.isoformat(),
        "capital_gains_tax_krw": capital,
        "dividend_withholding_krw": dividend,
        "total_tax_paid_krw": capital + dividend,
        "event": event,
    }


def portfolio_value(cash, lots, row):
    return cash + sum(holding_value(lots[component], row, component) for component in COMPONENTS)


def holding_value(component_lots, row, component):
    return sum(lot["qty_open"] for lot in component_lots) * component_price(row, component)


def component_price(row, component):
    return row[f"{component}_price_krw"]


def dividend_withholding(lots, row):
    return sum(holding_value(lots[component], row, component) * DIVIDEND_YIELDS[component] / 4.0 * DIVIDEND_WITHHOLDING_RATE for component in US_ETFS)


def quarter_key(d):
    return (d.year, (d.month - 1) // 3 + 1)


def is_quarter_end(prices, idx):
    return idx == len(prices) - 1 or quarter_key(prices[idx + 1]["date"]) != quarter_key(prices[idx]["date"])


def ffill_series(calendar, series):
    out = {}
    last = None
    for d in calendar:
        if d in series:
            last = series[d]
        out[d] = last
    return out


def concat_results(results, key):
    rows = []
    for result in results.values():
        rows.extend(result[key])
    return rows


def read_csv_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows, columns):
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(format_value(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, separator, *body])


def format_value(value):
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def to_float(value):
    if value in ("", None):
        return None
    return float(value)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


if __name__ == "__main__":
    main()
