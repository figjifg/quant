from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.audit.t001_rebalance_frequency_vs_tax import (
    COMMISSION_RATE,
    COMPONENTS,
    DIVIDEND_YIELDS,
    END_DATE,
    INITIAL_CAPITAL_KRW,
    START_DATE,
    US_ETFS,
    WEIGHTS,
    component_price,
    holding_value,
    is_quarter_end,
    load_price_panel,
    make_lot,
    metrics_for_nav,
    portfolio_value,
)


OUTPUT_DIR = Path("reports/experiments/T004_account_vehicle_study")

GROSS_I003_5_CAGR = 0.12738381267998689
T003_A_BASELINE_CAGR = 0.12462572401851557

OVERSEAS_CAPITAL_GAINS_TAX_RATE = 0.22
OVERSEAS_ANNUAL_EXEMPTION_KRW = 2_500_000.0
OVERSEAS_DIVIDEND_WITHHOLDING_RATE = 0.15

DOMESTIC_ETF_TAX_RATE = 0.154
ISA_ANNUAL_EXEMPTION_KRW = 2_000_000.0
ISA_SEPARATE_TAX_RATE = 0.099

PENSION_TAX_CREDIT_RATE = 0.132
PENSION_SAVINGS_ANNUAL_CREDIT_BASE_KRW = 6_000_000.0
IRP_ANNUAL_CREDIT_BASE_KRW = 3_000_000.0
PENSION_WITHDRAWAL_TAX_RATE = 0.055
EARLY_WITHDRAWAL_PENALTY_RATE = 0.165


@dataclass(frozen=True)
class VehicleSpec:
    vehicle: str
    label: str
    tax_model: str
    annual_tax_credit_base_krw: float = 0.0
    withdrawal_tax_rate: float = 0.0
    early_withdrawal_penalty_rate: float = 0.0
    irp_risky_asset_limit: float | None = None


@dataclass(frozen=True)
class PortfolioSpec:
    scenario: str
    label: str
    allocations: dict[str, float]


VEHICLES = (
    VehicleSpec("V1", "Overseas ETF direct taxable", "overseas_taxable"),
    VehicleSpec("V2", "Korean-listed US ETF taxable", "domestic_taxable"),
    VehicleSpec("V3", "Brokerage ISA", "isa"),
    VehicleSpec(
        "V4",
        "Pension savings",
        "pension",
        annual_tax_credit_base_krw=PENSION_SAVINGS_ANNUAL_CREDIT_BASE_KRW,
        withdrawal_tax_rate=PENSION_WITHDRAWAL_TAX_RATE,
        early_withdrawal_penalty_rate=EARLY_WITHDRAWAL_PENALTY_RATE,
    ),
    VehicleSpec(
        "V5",
        "IRP",
        "pension",
        annual_tax_credit_base_krw=IRP_ANNUAL_CREDIT_BASE_KRW,
        withdrawal_tax_rate=PENSION_WITHDRAWAL_TAX_RATE,
        early_withdrawal_penalty_rate=EARLY_WITHDRAWAL_PENALTY_RATE,
        irp_risky_asset_limit=0.70,
    ),
)

PORTFOLIOS = (
    PortfolioSpec("T004-V1", "100% V1", {"V1": 1.0}),
    PortfolioSpec("T004-V2", "100% V2", {"V2": 1.0}),
    PortfolioSpec("T004-V3", "100% V3", {"V3": 1.0}),
    PortfolioSpec("T004-V4", "100% V4", {"V4": 1.0}),
    PortfolioSpec("T004-V5", "100% V5", {"V5": 1.0}),
    PortfolioSpec("T004-MIX1", "50% V1 + 30% ISA + 20% pension", {"V1": 0.50, "V3": 0.30, "V4": 0.20}),
    PortfolioSpec("T004-MIX2", "30% V1 + 30% ISA + 20% pension + 20% IRP", {"V1": 0.30, "V3": 0.30, "V4": 0.20, "V5": 0.20}),
    PortfolioSpec("T004-MIX3", "60% V2 + 20% pension + 20% IRP", {"V2": 0.60, "V4": 0.20, "V5": 0.20}),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_price_panel()
    vehicle_results = {spec.vehicle: simulate_vehicle(prices, spec, INITIAL_CAPITAL_KRW) for spec in VEHICLES}

    scenarios = build_vehicle_scenarios(vehicle_results)
    assert_v1_reproduces_t003_a(scenarios)
    tax_by_vehicle = build_tax_by_vehicle(vehicle_results)
    lock_up = build_lock_up_analysis(vehicle_results)
    daily_nav = build_daily_nav_by_vehicle(vehicle_results)
    attribution = build_vehicle_attribution(vehicle_results)

    scenarios.to_csv(OUTPUT_DIR / "vehicle_scenarios.csv", index=False)
    tax_by_vehicle.to_csv(OUTPUT_DIR / "tax_by_vehicle.csv", index=False)
    attribution.to_csv(OUTPUT_DIR / "vehicle_attribution.csv", index=False)
    lock_up.to_csv(OUTPUT_DIR / "lock_up_analysis.csv", index=False)
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_by_vehicle.csv", index=False)
    write_report(scenarios, tax_by_vehicle, attribution, lock_up)


def simulate_vehicle(prices: pd.DataFrame, spec: VehicleSpec, initial_capital: float) -> dict:
    if spec.irp_risky_asset_limit is not None:
        risky_weight = WEIGHTS["SPY"] + WEIGHTS["QQQ"] + WEIGHTS["H001"]
        if risky_weight - spec.irp_risky_asset_limit > 1e-12:
            raise ValueError(f"{spec.vehicle} violates IRP risky asset limit")

    cash = initial_capital
    lots = {component: [] for component in COMPONENTS}
    lot_id = 0
    last_quarter = None
    realized_by_year_sleeve: dict[tuple[int, str], float] = {}
    taxable_base_paid_by_year: dict[int, float] = {}
    pension_credit_years: set[int] = set()
    tax_rows = []
    nav_rows = []
    trade_rows = []

    for idx, row in prices.iterrows():
        d = row["date"]
        quarter = (d.year, (d.month - 1) // 3 + 1)

        if spec.tax_model == "pension" and d.year not in pension_credit_years:
            credit = spec.annual_tax_credit_base_krw * PENSION_TAX_CREDIT_RATE
            cash += credit
            pension_credit_years.add(d.year)
            tax_rows.append(tax_row(spec, d.year, d, 0.0, 0.0, 0.0, -credit, "pension_tax_credit_reinvested"))

        if last_quarter is None or quarter != last_quarter:
            cash, lot_id, rows = rebalance_vehicle(d, row, spec, cash, lots, lot_id, realized_by_year_sleeve, taxable_base_paid_by_year)
            tax_rows.extend(rows["tax"])
            trade_rows.extend(rows["trades"])

        if is_quarter_end(prices, idx):
            cash, dividend_tax_row = apply_quarterly_dividend_tax(d, row, spec, cash, lots, realized_by_year_sleeve, taxable_base_paid_by_year)
            if dividend_tax_row is not None:
                tax_rows.append(dividend_tax_row)

        nav_rows.append(
            {
                "date": d,
                "vehicle": spec.vehicle,
                "label": spec.label,
                "nav": portfolio_value(cash, lots, row) / initial_capital,
            }
        )
        last_quarter = quarter

    final_nav_krw = nav_rows[-1]["nav"] * initial_capital
    withdrawal_tax = 0.0
    early_withdrawal_penalty = 0.0
    if spec.tax_model == "pension":
        withdrawal_tax = final_nav_krw * spec.withdrawal_tax_rate
        early_withdrawal_penalty = final_nav_krw * spec.early_withdrawal_penalty_rate

    return {
        "spec": spec,
        "nav": pd.DataFrame(nav_rows),
        "tax": pd.DataFrame(tax_rows),
        "trades": pd.DataFrame(trade_rows),
        "realized": realized_by_year_sleeve,
        "final_nav_krw": final_nav_krw,
        "withdrawal_tax_krw": withdrawal_tax,
        "early_withdrawal_penalty_krw": early_withdrawal_penalty,
    }


def rebalance_vehicle(
    d: pd.Timestamp,
    row: pd.Series,
    spec: VehicleSpec,
    cash: float,
    lots: dict[str, list[dict]],
    lot_id: int,
    realized_by_year_sleeve: dict[tuple[int, str], float],
    taxable_base_paid_by_year: dict[int, float],
) -> tuple[float, int, dict[str, list[dict]]]:
    pre_nav = portfolio_value(cash, lots, row)
    target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
    current_values = {component: holding_value(lots[component], row, component) for component in COMPONENTS}
    trades = {component: target_values[component] - current_values[component] for component in COMPONENTS}
    commission = sum(abs(value) for value in trades.values()) * COMMISSION_RATE
    tax_rows = []
    trade_rows = []

    for component, trade_value in trades.items():
        if trade_value < -1e-9:
            price = component_price(row, component)
            qty = min(sum(lot["qty_open"] for lot in lots[component]), -trade_value / price)
            cash_delta, rows = sell_lots_hifo(d, component, qty, price, row, spec, lots, realized_by_year_sleeve)
            cash += cash_delta
            trade_rows.extend(rows)

    tax_due = immediate_tax_due(spec, realized_by_year_sleeve, d.year, taxable_base_paid_by_year)
    if tax_due > 0.0:
        tax_rows.append(tax_row_for_model(spec, d.year, d, tax_due, "rebalance_realized_gain_tax"))
    cash -= commission + tax_due

    for component, trade_value in trades.items():
        if trade_value > 1e-9:
            price = component_price(row, component)
            qty = trade_value / price
            lot_id += 1
            lots[component].append(make_lot(lot_id, d, component, qty, price, row))
            cash -= qty * price
            trade_rows.append(
                {
                    "vehicle": spec.vehicle,
                    "label": spec.label,
                    "date": d,
                    "component": component,
                    "side": "BUY",
                    "qty": qty,
                    "price_krw": price,
                    "trade_value_krw": trade_value,
                    "realized_gain_krw": 0.0,
                    "commission_krw": commission,
                    "tax_paid_krw": tax_due,
                }
            )

    return cash, lot_id, {"tax": tax_rows, "trades": trade_rows}


def sell_lots_hifo(
    d: pd.Timestamp,
    component: str,
    qty_to_sell: float,
    sell_price: float,
    row: pd.Series,
    spec: VehicleSpec,
    lots: dict[str, list[dict]],
    realized_by_year_sleeve: dict[tuple[int, str], float],
) -> tuple[float, list[dict]]:
    selected = sorted(lots[component], key=lambda lot: lot["buy_price_krw"], reverse=True)
    remaining = qty_to_sell
    proceeds = 0.0
    rows = []
    for lot in selected:
        if remaining <= 1e-12:
            break
        qty = min(lot["qty_open"], remaining)
        lot["qty_open"] -= qty
        remaining -= qty
        proceeds += qty * sell_price
        gain = taxable_realized_gain(spec, component, sell_price, lot["buy_price_krw"], qty)
        if gain != 0.0:
            realized_by_year_sleeve[(d.year, component)] = realized_by_year_sleeve.get((d.year, component), 0.0) + gain
        rows.append(
            {
                "vehicle": spec.vehicle,
                "label": spec.label,
                "date": d,
                "component": component,
                "side": "SELL",
                "qty": qty,
                "price_krw": sell_price,
                "trade_value_krw": -qty * sell_price,
                "realized_gain_krw": gain,
                "commission_krw": 0.0,
                "tax_paid_krw": 0.0,
            }
        )
    lots[component] = [lot for lot in lots[component] if lot["qty_open"] > 1e-12]
    return proceeds, rows


def taxable_realized_gain(spec: VehicleSpec, component: str, sell_price: float, buy_price: float, qty: float) -> float:
    if component not in US_ETFS:
        return 0.0
    if spec.tax_model in {"overseas_taxable", "domestic_taxable", "isa"}:
        return (sell_price - buy_price) * qty
    return 0.0


def immediate_tax_due(
    spec: VehicleSpec,
    realized_by_year_sleeve: dict[tuple[int, str], float],
    year: int,
    taxable_base_paid_by_year: dict[int, float],
) -> float:
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    if spec.tax_model == "overseas_taxable":
        taxable_base = max(total - OVERSEAS_ANNUAL_EXEMPTION_KRW, 0.0)
        rate = OVERSEAS_CAPITAL_GAINS_TAX_RATE
    elif spec.tax_model == "domestic_taxable":
        taxable_base = max(total, 0.0)
        rate = DOMESTIC_ETF_TAX_RATE
    elif spec.tax_model == "isa":
        taxable_base = max(total - ISA_ANNUAL_EXEMPTION_KRW, 0.0)
        rate = ISA_SEPARATE_TAX_RATE
    else:
        return 0.0
    incremental = max(taxable_base - taxable_base_paid_by_year.get(year, 0.0), 0.0)
    taxable_base_paid_by_year[year] = taxable_base_paid_by_year.get(year, 0.0) + incremental
    return incremental * rate


def apply_quarterly_dividend_tax(
    d: pd.Timestamp,
    row: pd.Series,
    spec: VehicleSpec,
    cash: float,
    lots: dict[str, list[dict]],
    realized_by_year_sleeve: dict[tuple[int, str], float],
    taxable_base_paid_by_year: dict[int, float],
) -> tuple[float, dict | None]:
    dividend_income = sum(holding_value(lots[component], row, component) * DIVIDEND_YIELDS[component] / 4.0 for component in US_ETFS)
    if dividend_income <= 0.0:
        return cash, None
    if spec.tax_model == "overseas_taxable":
        tax = dividend_income * OVERSEAS_DIVIDEND_WITHHOLDING_RATE
        return cash, tax_row(spec, d.year, d, 0.0, tax, 0.0, 0.0, "dividend_withholding")
    if spec.tax_model == "domestic_taxable":
        tax = dividend_income * DOMESTIC_ETF_TAX_RATE
        return cash, tax_row(spec, d.year, d, 0.0, tax, 0.0, 0.0, "domestic_etf_distribution_tax")
    if spec.tax_model == "isa":
        realized_by_year_sleeve[(d.year, "dividend")] = realized_by_year_sleeve.get((d.year, "dividend"), 0.0) + dividend_income
        tax = immediate_tax_due(spec, realized_by_year_sleeve, d.year, taxable_base_paid_by_year)
        if tax <= 0.0:
            return cash, tax_row(spec, d.year, d, 0.0, 0.0, 0.0, 0.0, "isa_dividend_within_annual_exemption")
        cash -= tax
        return cash, tax_row(spec, d.year, d, 0.0, 0.0, 0.0, tax, "isa_separate_tax_on_dividend_or_gain")
    return cash, None


def build_vehicle_scenarios(vehicle_results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    nav_by_vehicle = {vehicle: nav_series(result) for vehicle, result in vehicle_results.items()}
    baseline_nav = nav_by_vehicle["V1"]
    baseline_metrics = metrics_for_nav(baseline_nav)

    for portfolio in PORTFOLIOS:
        nav = combine_nav(nav_by_vehicle, portfolio.allocations)
        metrics = metrics_for_nav(nav)
        tax = combine_tax_totals(vehicle_results, portfolio.allocations)
        rows.append(
            {
                "scenario": portfolio.scenario,
                "label": portfolio.label,
                "allocations": format_allocations(portfolio.allocations),
                "gross_i003_5_cagr_reference": GROSS_I003_5_CAGR,
                "t003_a_baseline_cagr_reference": T003_A_BASELINE_CAGR,
                "net_cagr": metrics["cagr"],
                "net_cagr_delta_vs_t003_a_pp": (metrics["cagr"] - baseline_metrics["cagr"]) * 100.0,
                "net_sharpe": metrics["sharpe"],
                "net_mdd": metrics["max_drawdown"],
                "final_nav": float(nav.iloc[-1]),
                "capital_gains_tax_krw_16y": tax["capital_gains_tax_krw"],
                "domestic_distribution_tax_krw_16y": tax["domestic_distribution_tax_krw"],
                "dividend_withholding_krw_16y": tax["dividend_withholding_krw"],
                "isa_separate_tax_krw_16y": tax["isa_separate_tax_krw"],
                "pension_tax_credit_krw_16y": tax["pension_tax_credit_krw"],
                "withdrawal_tax_krw": tax["withdrawal_tax_krw"],
                "net_cagr_after_pension_withdrawal_tax": cagr_from_final_nav(nav, tax["withdrawal_tax_krw"] / INITIAL_CAPITAL_KRW),
                "total_tax_or_credit_krw_16y": tax["total_tax_or_credit_krw"],
            }
        )
    return pd.DataFrame(rows)


def assert_v1_reproduces_t003_a(scenarios: pd.DataFrame) -> None:
    v1 = scenarios.loc[scenarios["scenario"] == "T004-V1"].iloc[0]
    if abs(float(v1["net_cagr"]) - T003_A_BASELINE_CAGR) > 1e-12:
        raise AssertionError("T004-V1 must reproduce T003-A / T000-C baseline CAGR")


def build_tax_by_vehicle(vehicle_results: dict[str, dict]) -> pd.DataFrame:
    frames = []
    years = list(range(START_DATE.year, END_DATE.year + 1))
    for spec in VEHICLES:
        tax = vehicle_results[spec.vehicle]["tax"]
        if tax.empty:
            grouped = pd.DataFrame({"tax_year": years})
        else:
            grouped = tax.groupby("tax_year", as_index=False)[
                [
                    "capital_gains_tax_krw",
                    "dividend_withholding_krw",
                    "domestic_distribution_tax_krw",
                    "isa_separate_tax_krw",
                    "pension_tax_credit_krw",
                ]
            ].sum()
        grouped = pd.DataFrame({"tax_year": years}).merge(grouped, on="tax_year", how="left").fillna(0.0)
        grouped["vehicle"] = spec.vehicle
        grouped["label"] = spec.label
        grouped["total_tax_or_credit_krw"] = (
            grouped["capital_gains_tax_krw"]
            + grouped["dividend_withholding_krw"]
            + grouped["domestic_distribution_tax_krw"]
            + grouped["isa_separate_tax_krw"]
            + grouped["pension_tax_credit_krw"]
        )
        frames.append(
            grouped[
                [
                    "vehicle",
                    "label",
                    "tax_year",
                    "capital_gains_tax_krw",
                    "dividend_withholding_krw",
                    "domestic_distribution_tax_krw",
                    "isa_separate_tax_krw",
                    "pension_tax_credit_krw",
                    "total_tax_or_credit_krw",
                ]
            ]
        )
    return pd.concat(frames, ignore_index=True)


def build_vehicle_attribution(vehicle_results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    v1_cagr = metrics_for_nav(nav_series(vehicle_results["V1"]))["cagr"]
    for spec in VEHICLES:
        result = vehicle_results[spec.vehicle]
        nav = nav_series(result)
        metrics = metrics_for_nav(nav)
        tax = tax_totals(result)
        rows.append(
            {
                "vehicle": spec.vehicle,
                "label": spec.label,
                "net_cagr": metrics["cagr"],
                "net_cagr_delta_vs_v1_pp": (metrics["cagr"] - v1_cagr) * 100.0,
                "final_nav": float(nav.iloc[-1]),
                "capital_gains_tax_krw_16y": tax["capital_gains_tax_krw"],
                "distribution_or_dividend_tax_krw_16y": tax["dividend_withholding_krw"] + tax["domestic_distribution_tax_krw"],
                "isa_separate_tax_krw_16y": tax["isa_separate_tax_krw"],
                "pension_tax_credit_krw_16y": tax["pension_tax_credit_krw"],
                "withdrawal_tax_krw": result["withdrawal_tax_krw"],
                "after_withdrawal_final_nav": float(nav.iloc[-1]) - result["withdrawal_tax_krw"] / INITIAL_CAPITAL_KRW,
                "net_cagr_after_withdrawal_tax": cagr_from_final_nav(nav, result["withdrawal_tax_krw"] / INITIAL_CAPITAL_KRW),
            }
        )
    return pd.DataFrame(rows)


def build_lock_up_analysis(vehicle_results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for vehicle in ("V4", "V5"):
        result = vehicle_results[vehicle]
        spec = result["spec"]
        nav = nav_series(result)
        rows.append(
            {
                "vehicle": spec.vehicle,
                "label": spec.label,
                "paper_final_nav_krw": result["final_nav_krw"],
                "paper_cagr_before_withdrawal_tax": metrics_for_nav(nav)["cagr"],
                "pension_withdrawal_tax_rate": spec.withdrawal_tax_rate,
                "pension_withdrawal_tax_krw": result["withdrawal_tax_krw"],
                "final_nav_after_pension_withdrawal_tax_krw": result["final_nav_krw"] - result["withdrawal_tax_krw"],
                "cagr_after_pension_withdrawal_tax": cagr_from_final_nav(nav, result["withdrawal_tax_krw"] / INITIAL_CAPITAL_KRW),
                "early_withdrawal_penalty_rate_diagnostic": spec.early_withdrawal_penalty_rate,
                "early_withdrawal_penalty_krw_diagnostic": result["early_withdrawal_penalty_krw"],
                "lock_up_assumption": "16-year lock-up; no early withdrawal in headline",
            }
        )
    return pd.DataFrame(rows)


def build_daily_nav_by_vehicle(vehicle_results: dict[str, dict]) -> pd.DataFrame:
    base = None
    nav_by_vehicle = {vehicle: nav_series(result) for vehicle, result in vehicle_results.items()}
    for vehicle, nav in nav_by_vehicle.items():
        base = nav.rename(f"{vehicle}_net_nav").to_frame() if base is None else base.join(nav.rename(f"{vehicle}_net_nav"), how="outer")
    for portfolio in PORTFOLIOS:
        combined = combine_nav(nav_by_vehicle, portfolio.allocations)
        base = base.join(combined.rename(f"{portfolio.scenario}_net_nav"), how="outer")
    return base.reset_index().rename(columns={"index": "date"})


def combine_tax_totals(vehicle_results: dict[str, dict], allocations: dict[str, float]) -> dict[str, float]:
    keys = [
        "capital_gains_tax_krw",
        "dividend_withholding_krw",
        "domestic_distribution_tax_krw",
        "isa_separate_tax_krw",
        "pension_tax_credit_krw",
    ]
    totals = {key: 0.0 for key in keys}
    withdrawal_tax = 0.0
    for vehicle, weight in allocations.items():
        vehicle_tax = tax_totals(vehicle_results[vehicle])
        for key in keys:
            totals[key] += vehicle_tax[key] * weight
        withdrawal_tax += vehicle_results[vehicle]["withdrawal_tax_krw"] * weight
    totals["withdrawal_tax_krw"] = withdrawal_tax
    totals["total_tax_or_credit_krw"] = sum(totals[key] for key in keys)
    return totals


def tax_totals(result: dict) -> dict[str, float]:
    tax = result["tax"]
    keys = [
        "capital_gains_tax_krw",
        "dividend_withholding_krw",
        "domestic_distribution_tax_krw",
        "isa_separate_tax_krw",
        "pension_tax_credit_krw",
    ]
    if tax.empty:
        return {key: 0.0 for key in keys}
    return {key: float(tax[key].sum()) for key in keys}


def combine_nav(nav_by_vehicle: dict[str, pd.Series], allocations: dict[str, float]) -> pd.Series:
    out = None
    for vehicle, weight in allocations.items():
        weighted = nav_by_vehicle[vehicle] * weight
        out = weighted if out is None else out.add(weighted, fill_value=0.0)
    if out is None:
        raise ValueError("empty portfolio allocation")
    return out.sort_index()


def nav_series(result: dict) -> pd.Series:
    return result["nav"].set_index("date")["nav"].sort_index()


def cagr_from_final_nav(nav: pd.Series, terminal_tax_nav_units: float) -> float:
    adjusted_final = float(nav.iloc[-1] - terminal_tax_nav_units)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total_return = adjusted_final / float(nav.iloc[0]) - 1.0
    return float((1.0 + total_return) ** (1.0 / years) - 1.0)


def format_allocations(allocations: dict[str, float]) -> str:
    return "/".join(f"{vehicle}{weight:.0%}" for vehicle, weight in allocations.items())


def tax_row_for_model(spec: VehicleSpec, tax_year: int, payment_date: pd.Timestamp, amount: float, event: str) -> dict:
    if spec.tax_model == "overseas_taxable":
        return tax_row(spec, tax_year, payment_date, amount, 0.0, 0.0, 0.0, event)
    if spec.tax_model == "domestic_taxable":
        return tax_row(spec, tax_year, payment_date, 0.0, 0.0, amount, 0.0, event)
    if spec.tax_model == "isa":
        return tax_row(spec, tax_year, payment_date, 0.0, 0.0, 0.0, amount, event)
    raise ValueError(f"{spec.vehicle} has no immediate tax model")


def tax_row(
    spec: VehicleSpec,
    tax_year: int,
    payment_date: pd.Timestamp,
    capital_gains_tax: float,
    dividend_withholding: float,
    domestic_distribution_tax: float,
    pension_or_isa: float,
    event: str,
) -> dict:
    return {
        "vehicle": spec.vehicle,
        "label": spec.label,
        "tax_year": tax_year,
        "payment_date": payment_date,
        "capital_gains_tax_krw": capital_gains_tax,
        "dividend_withholding_krw": dividend_withholding,
        "domestic_distribution_tax_krw": domestic_distribution_tax,
        "isa_separate_tax_krw": pension_or_isa if spec.tax_model == "isa" else 0.0,
        "pension_tax_credit_krw": pension_or_isa if spec.tax_model == "pension" else 0.0,
        "event": event,
    }


def markdown_table(data: pd.DataFrame) -> str:
    if data.empty:
        return "(empty)"
    rows = [list(data.columns)]
    for _, row in data.iterrows():
        rows.append([format_markdown_cell(row[column]) for column in data.columns])
    widths = [max(len(str(row[idx])) for row in rows) for idx in range(len(rows[0]))]
    header = "| " + " | ".join(str(value).ljust(widths[idx]) for idx, value in enumerate(rows[0])) + " |"
    sep = "| " + " | ".join("---".ljust(widths[idx]) for idx in range(len(widths))) + " |"
    body = ["| " + " | ".join(str(value).ljust(widths[idx]) for idx, value in enumerate(row)) + " |" for row in rows[1:]]
    return "\n".join([header, sep, *body])


def format_markdown_cell(value) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6f}"
    return str(value)


def krw(value: float) -> str:
    return f"{value:,.0f} KRW"


def write_report(
    scenarios: pd.DataFrame,
    tax_by_vehicle: pd.DataFrame,
    attribution: pd.DataFrame,
    lock_up: pd.DataFrame,
) -> None:
    vehicle_rows = scenarios.loc[scenarios["scenario"].isin([f"T004-V{i}" for i in range(1, 6)])].copy()
    mix_rows = scenarios.loc[scenarios["scenario"].str.contains("MIX")].copy()
    best_vehicle = vehicle_rows.sort_values("net_cagr_after_pension_withdrawal_tax", ascending=False).iloc[0]
    best_mix = mix_rows.sort_values("net_cagr_after_pension_withdrawal_tax", ascending=False).iloc[0]
    v1 = attribution.loc[attribution["vehicle"] == "V1"].iloc[0]
    v2 = attribution.loc[attribution["vehicle"] == "V2"].iloc[0]
    v3 = attribution.loc[attribution["vehicle"] == "V3"].iloc[0]
    v4 = attribution.loc[attribution["vehicle"] == "V4"].iloc[0]
    v5 = attribution.loc[attribution["vehicle"] == "V5"].iloc[0]

    vehicle_table = vehicle_rows[
        [
            "scenario",
            "label",
            "net_cagr",
            "net_cagr_after_pension_withdrawal_tax",
            "net_cagr_delta_vs_t003_a_pp",
            "final_nav",
            "total_tax_or_credit_krw_16y",
            "withdrawal_tax_krw",
        ]
    ]
    mix_table = mix_rows[
        [
            "scenario",
            "label",
            "net_cagr",
            "net_cagr_after_pension_withdrawal_tax",
            "net_cagr_delta_vs_t003_a_pp",
            "final_nav",
            "total_tax_or_credit_krw_16y",
            "withdrawal_tax_krw",
        ]
    ]
    tax_summary = tax_by_vehicle.groupby(["vehicle", "label"], as_index=False)[
        [
            "capital_gains_tax_krw",
            "dividend_withholding_krw",
            "domestic_distribution_tax_krw",
            "isa_separate_tax_krw",
            "pension_tax_credit_krw",
            "total_tax_or_credit_krw",
        ]
    ].sum()

    text = f"""# T004 account / vehicle study

## 설정

- 대상: `P08_IEF30` = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- 기간: {START_DATE.date()} ~ {END_DATE.date()}, 초기자본 {krw(INITIAL_CAPITAL_KRW)}.
- Rebalance: quarterly, HIFO lot accounting where taxable, ongoing NAV, 매매 수수료 0.25%.
- T000/T003 baseline 호환을 위해 V1/V2의 배당 원천징수/분배금세는 세목으로 추적하되 NAV에서는 차감하지 않았다. 매매차익 관련 세금과 ISA 분리과세, 연금 세액공제는 NAV에 반영했다.
- Gross I003.5 참고 CAGR: {GROSS_I003_5_CAGR:.6f}.
- T003-A / T000-C baseline 참고 CAGR: {T003_A_BASELINE_CAGR:.6f}.
- 국내 상장 ETF proxy는 tracking error 0으로 단순화했다.
- Diagnostic only: 한국 세법 2026 기준 단순화이며 실전 적용 전 세무 전문가 확인이 필요하다.

## 5 vehicle net 비교

{markdown_table(vehicle_table)}

## 3 mix net 비교

{markdown_table(mix_table)}

## 가장 효율적 vehicle / mix

- Vehicle 기준 1위: {best_vehicle['scenario']} {best_vehicle['label']}, withdrawal tax 반영 CAGR {best_vehicle['net_cagr_after_pension_withdrawal_tax']:.6f}.
- Mix 기준 1위: {best_mix['scenario']} {best_mix['label']}, withdrawal tax 반영 CAGR {best_mix['net_cagr_after_pension_withdrawal_tax']:.6f}.

## 양도세 22% vs 배당소득세 15.4% 영향

- V1 해외 ETF 직접: net CAGR {v1['net_cagr']:.6f}, 16년 capital gains tax {krw(v1['capital_gains_tax_krw_16y'])}, dividend withholding {krw(v1['distribution_or_dividend_tax_krw_16y'])}.
- V2 국내 상장 미국 ETF proxy: net CAGR {v2['net_cagr']:.6f}, 16년 국내 ETF 과세/분배금세 {krw(v2['capital_gains_tax_krw_16y'] + v2['distribution_or_dividend_tax_krw_16y'])}.
- V2 - V1 net CAGR 차이: {(v2['net_cagr'] - v1['net_cagr']) * 100.0:.3f}pp.
- 이 차이는 22% 양도세와 250만원 공제 조합을 15.4% 배당소득세형 과세로 바꾼 단순화 효과다. 금융소득 종합과세는 모델링하지 않았다.

## ISA 비과세 200만원 효과

- V3 ISA net CAGR: {v3['net_cagr']:.6f}.
- V3 ISA separate tax 16년 합계: {krw(v3['isa_separate_tax_krw_16y'])}.
- V3 - V2 net CAGR 차이: {(v3['net_cagr'] - v2['net_cagr']) * 100.0:.3f}pp.
- ISA는 연 200만원 비과세 후 초과분 9.9% 분리과세로 모델링했다. 초기 1억원 전체가 단순화된 ISA lifetime cap 안에 있다고 가정했다.

## 연금저축/IRP 세액공제와 lock-up

- V4 연금저축 paper CAGR: {v4['net_cagr']:.6f}, withdrawal tax 반영 CAGR {v4['net_cagr_after_withdrawal_tax']:.6f}, 16년 세액공제 {krw(v4['pension_tax_credit_krw_16y'])}.
- V5 IRP paper CAGR: {v5['net_cagr']:.6f}, withdrawal tax 반영 CAGR {v5['net_cagr_after_withdrawal_tax']:.6f}, 16년 세액공제 {krw(v5['pension_tax_credit_krw_16y'])}.
- V4/V5는 55세 이후 연금 인출세 5.5%를 terminal tax로 별도 반영했다. 조기인출 16.5% 기타소득세는 diagnostic으로만 `lock_up_analysis.csv`에 기록했다.

{markdown_table(lock_up)}

## 세금 종류별 요약

{markdown_table(tax_summary)}

## 한국 세법 가정

- 기준: 2026년 현재 한국 거주자 기준 단순화.
- V1: 해외 상장 ETF 직접 보유, 양도세 22%, 연 250만원 공제, 배당 원천징수 15%.
- V2: 국내 상장 해외 ETF proxy, 매매차익과 분배금을 배당소득세 15.4%로 단순화, 250만원 공제 없음.
- V3: ISA 일반형, 연 200만원 비과세, 초과분 9.9% 분리과세, 국내 상장 ETF만 허용.
- V4: 연금저축, 연 600만원 세액공제 대상, 13.2% 세액공제, 연금 인출세 5.5%.
- V5: IRP, 연 300만원 세액공제 대상, 13.2% 세액공제, 연금 인출세 5.5%, 위험자산 70% 제한 통과.
- 금융소득 종합과세, 실제 ETF 과표기준가, 환헤지/환노출 상품 차이, broker별 원천징수/신고 처리, 세액공제 자격 제한은 모델링하지 않았다.

## Verdict

- Verdict: diagnostic 기준으로 production 운용의 우선 검토 조합은 {best_mix['scenario']}이다.
- 단일 vehicle로는 {best_vehicle['scenario']}이 가장 높지만, 연금/IRP 결과는 장기 lock-up과 인출세 가정에 의존한다.
- T-family 종합 결론: T000 HIFO+250만원 공제는 약 +0.45pp 개선, T001/T002/T003은 효과가 미미했다. T004에서는 vehicle/account 선택이 가장 큰 잠재 source로 나타났다.
- 이 결론은 세무 자문 전까지 실행 권고가 아니라 account/vehicle 설계 후보를 좁히는 diagnostic 결과다.

## Files

- vehicle_scenarios.csv
- tax_by_vehicle.csv
- vehicle_attribution.csv
- lock_up_analysis.csv
- daily_nav_by_vehicle.csv
"""
    (OUTPUT_DIR / "report.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
