from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.audit.t001_rebalance_frequency_vs_tax import (
    ANNUAL_EXEMPTION_KRW,
    CAPITAL_GAINS_TAX_RATE,
    COMMISSION_RATE,
    COMPONENTS,
    DIVIDEND_WITHHOLDING_RATE,
    DIVIDEND_YIELDS,
    END_DATE,
    INITIAL_CAPITAL_KRW,
    START_DATE,
    US_ETFS,
    WEIGHTS,
    component_price,
    dividend_withholding,
    holding_value,
    is_quarter_end,
    load_price_panel,
    make_lot,
    metrics_for_nav,
    period_return,
    portfolio_value,
)


OUTPUT_DIR = Path("reports/experiments/T003_tax_loss_harvesting")
GROSS_I003_5_CAGR = 0.12738381267998689
T000_C_BASELINE_CAGR = 0.12462572401851557


@dataclass(frozen=True)
class TlhSpec:
    scenario: str
    label: str
    review_frequency: str
    threshold_return: float | None = None


SCENARIOS = (
    TlhSpec("T003-A", "No TLH", "none"),
    TlhSpec("T003-B", "Year-end TLH: all loss lots", "year_end"),
    TlhSpec("T003-C", "Quarter-end TLH: all loss lots", "quarter_end"),
    TlhSpec("T003-D", "Year-end TLH: loss <= -5%", "year_end", -0.05),
    TlhSpec("T003-E", "Year-end TLH: loss <= -10%", "year_end", -0.10),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_price_panel()
    results = {spec.scenario: simulate_tlh(prices, spec) for spec in SCENARIOS}

    scenarios = build_scenario_metrics(results)
    realized_loss = build_realized_loss_by_year(results)
    tax_savings = build_tax_savings_by_year(results)
    events = build_tlh_events(results)
    daily_nav = build_daily_nav(results)
    stress = build_stress(results)

    scenarios.to_csv(OUTPUT_DIR / "tlh_scenarios.csv", index=False)
    realized_loss.to_csv(OUTPUT_DIR / "realized_loss_by_year.csv", index=False)
    tax_savings.to_csv(OUTPUT_DIR / "tax_savings_by_year.csv", index=False)
    events.to_csv(OUTPUT_DIR / "tlh_events.csv", index=False)
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_by_tlh.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_net_by_tlh.csv", index=False)
    write_report(scenarios, realized_loss, tax_savings, events, stress)


def simulate_tlh(prices: pd.DataFrame, spec: TlhSpec) -> dict:
    cash = INITIAL_CAPITAL_KRW
    lots = {component: [] for component in COMPONENTS}
    lot_id = 0
    last_quarter = None
    taxable_base_paid_by_year: dict[int, float] = {}
    realized_by_year_sleeve: dict[tuple[int, str], float] = {}
    tax_rows = []
    nav_rows = []
    ordinary_trade_rows = []
    tlh_rows = []
    true_up_rows = []

    for idx, row in prices.iterrows():
        d = row["date"]
        quarter = (d.year, (d.month - 1) // 3 + 1)
        if last_quarter is None or quarter != last_quarter:
            cash, lot_id, rebalance_tax, rebalance_trades = rebalance_hifo(
                d,
                row,
                spec,
                cash,
                lots,
                lot_id,
                realized_by_year_sleeve,
                taxable_base_paid_by_year,
            )
            tax_rows.extend(rebalance_tax)
            ordinary_trade_rows.extend(rebalance_trades)

        if should_tlh_review(prices, idx, spec):
            cash, lot_id, rows = harvest_losses(d, row, spec, cash, lots, lot_id, realized_by_year_sleeve)
            tlh_rows.extend(rows)
            true_up = annual_tax_true_up(d, spec, realized_by_year_sleeve, taxable_base_paid_by_year)
            if true_up["tax_savings_krw"] > 0.0:
                cash += true_up["tax_savings_krw"]
                tax_rows.append(tax_row(spec, d.year, d, -true_up["tax_savings_krw"], 0.0, "tlh_annual_tax_true_up"))
                true_up_rows.append(true_up)

        if is_quarter_end(prices, idx):
            tax = dividend_withholding(lots, row)
            if tax > 0.0:
                tax_rows.append(tax_row(spec, d.year, d, 0.0, tax, "dividend_withholding_tracked_not_nav"))

        nav_rows.append(
            {
                "date": d,
                "scenario": spec.scenario,
                "label": spec.label,
                "nav": portfolio_value(cash, lots, row) / INITIAL_CAPITAL_KRW,
            }
        )
        last_quarter = quarter

    return {
        "spec": spec,
        "nav": pd.DataFrame(nav_rows),
        "tax": pd.DataFrame(tax_rows),
        "ordinary_trades": pd.DataFrame(ordinary_trade_rows),
        "tlh_events": pd.DataFrame(tlh_rows),
        "true_ups": pd.DataFrame(true_up_rows),
        "realized": realized_by_year_sleeve,
    }


def rebalance_hifo(
    d: pd.Timestamp,
    row: pd.Series,
    spec: TlhSpec,
    cash: float,
    lots: dict[str, list[dict]],
    lot_id: int,
    realized_by_year_sleeve: dict[tuple[int, str], float],
    taxable_base_paid_by_year: dict[int, float],
) -> tuple[float, int, list[dict], list[dict]]:
    pre_nav = portfolio_value(cash, lots, row)
    target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
    current_values = {component: holding_value(lots[component], row, component) for component in COMPONENTS}
    trades = {component: target_values[component] - current_values[component] for component in COMPONENTS}
    commission = sum(abs(value) for value in trades.values()) * COMMISSION_RATE
    tax_events = []
    trade_rows = []

    for component in COMPONENTS:
        trade_value = trades[component]
        if trade_value < -1e-9:
            price = component_price(row, component)
            qty = min(sum(lot["qty_open"] for lot in lots[component]), -trade_value / price)
            cash_delta, rows = sell_lots_hifo(d, component, qty, price, row, spec, lots, realized_by_year_sleeve, "rebalance")
            cash += cash_delta
            trade_rows.extend(rows)

    capital_tax = immediate_tax_due(realized_by_year_sleeve, d.year, taxable_base_paid_by_year)
    if capital_tax > 0.0:
        tax_events.append(tax_row(spec, d.year, d, capital_tax, 0.0, "immediate_capital_gains_tax"))
    cash -= commission + capital_tax

    for component in COMPONENTS:
        trade_value = trades[component]
        if trade_value > 1e-9:
            price = component_price(row, component)
            qty = trade_value / price
            lot_id += 1
            lot = make_lot(lot_id, d, component, qty, price, row)
            lots[component].append(lot)
            cash -= qty * price
            trade_rows.append(trade_row(spec, d, component, "BUY", "rebalance", qty, price, trade_value, 0.0, "", commission, capital_tax))
    return cash, lot_id, tax_events, trade_rows


def sell_lots_hifo(
    d: pd.Timestamp,
    component: str,
    qty_to_sell: float,
    sell_price: float,
    row: pd.Series,
    spec: TlhSpec,
    lots: dict[str, list[dict]],
    realized_by_year_sleeve: dict[tuple[int, str], float],
    event_type: str,
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
        gain = 0.0
        if component in US_ETFS:
            gain = (sell_price - lot["buy_price_krw"]) * qty
            realized_by_year_sleeve[(d.year, component)] = realized_by_year_sleeve.get((d.year, component), 0.0) + gain
        rows.append(
            trade_row(
                spec,
                d,
                component,
                "SELL",
                event_type,
                qty,
                sell_price,
                -qty * sell_price,
                gain,
                lot["lot_id"],
                0.0,
                0.0,
            )
        )
    lots[component] = [lot for lot in lots[component] if lot["qty_open"] > 1e-12]
    return proceeds, rows


def harvest_losses(
    d: pd.Timestamp,
    row: pd.Series,
    spec: TlhSpec,
    cash: float,
    lots: dict[str, list[dict]],
    lot_id: int,
    realized_by_year_sleeve: dict[tuple[int, str], float],
) -> tuple[float, int, list[dict]]:
    events = []
    for component in US_ETFS:
        price = component_price(row, component)
        candidates = [lot for lot in lots[component] if lot_is_harvestable(lot, price, spec.threshold_return)]
        for lot in sorted(candidates, key=lambda item: item["buy_price_krw"], reverse=True):
            if lot["qty_open"] <= 1e-12:
                continue
            qty = lot["qty_open"]
            original_lot_id = lot["lot_id"]
            buy_price = lot["buy_price_krw"]
            buy_date = lot["buy_date"]
            cash_delta, realized_loss = sell_specific_lot(d, component, original_lot_id, qty, price, lots, realized_by_year_sleeve)
            sell_commission = qty * price * COMMISSION_RATE
            buy_commission = qty * price * COMMISSION_RATE
            cash += cash_delta - sell_commission - buy_commission
            lot_id += 1
            new_lot = make_lot(lot_id, d, component, qty, price, row)
            lots[component].append(new_lot)
            cash -= qty * price
            realized_loss = (price - buy_price) * qty
            loss_return = price / buy_price - 1.0
            events.append(
                {
                    "scenario": spec.scenario,
                    "label": spec.label,
                    "date": d,
                    "tax_year": d.year,
                    "component": component,
                    "original_lot_id": original_lot_id,
                    "replacement_lot_id": lot_id,
                    "original_buy_date": buy_date,
                    "qty": qty,
                    "buy_price_krw": buy_price,
                    "sell_price_krw": price,
                    "unrealized_return": loss_return,
                    "realized_loss_krw": realized_loss,
                    "sell_commission_krw": sell_commission,
                    "buy_commission_krw": buy_commission,
                    "total_tlh_commission_krw": sell_commission + buy_commission,
                    "same_etf_immediate_repurchase": True,
                }
            )
    return cash, lot_id, normalize_tlh_rows(events)


def normalize_tlh_rows(rows: list[dict]) -> list[dict]:
    event_rows = [row for row in rows if "realized_loss_krw" in row]
    return event_rows


def sell_specific_lot(
    d: pd.Timestamp,
    component: str,
    lot_id: int,
    qty: float,
    sell_price: float,
    lots: dict[str, list[dict]],
    realized_by_year_sleeve: dict[tuple[int, str], float],
) -> tuple[float, float]:
    for lot in lots[component]:
        if lot["lot_id"] != lot_id:
            continue
        if qty - lot["qty_open"] > 1e-12:
            raise ValueError(f"TLH qty exceeds open qty for lot {lot_id}")
        lot["qty_open"] -= qty
        proceeds = qty * sell_price
        realized = (sell_price - lot["buy_price_krw"]) * qty
        realized_by_year_sleeve[(d.year, component)] = realized_by_year_sleeve.get((d.year, component), 0.0) + realized
        lots[component] = [item for item in lots[component] if item["qty_open"] > 1e-12]
        return proceeds, realized
    raise ValueError(f"lot {lot_id} not found for TLH")


def lot_is_harvestable(lot: dict, price: float, threshold_return: float | None) -> bool:
    lot_return = price / lot["buy_price_krw"] - 1.0
    if threshold_return is None:
        return lot_return < 0.0
    return lot_return <= threshold_return


def immediate_tax_due(realized_by_year_sleeve: dict[tuple[int, str], float], year: int, taxable_base_paid_by_year: dict[int, float]) -> float:
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    taxable_base = max(total - ANNUAL_EXEMPTION_KRW, 0.0)
    incremental = max(taxable_base - taxable_base_paid_by_year.get(year, 0.0), 0.0)
    taxable_base_paid_by_year[year] = taxable_base_paid_by_year.get(year, 0.0) + incremental
    return incremental * CAPITAL_GAINS_TAX_RATE


def annual_tax_true_up(
    d: pd.Timestamp,
    spec: TlhSpec,
    realized_by_year_sleeve: dict[tuple[int, str], float],
    taxable_base_paid_by_year: dict[int, float],
) -> dict:
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == d.year)
    correct_taxable_base = max(total - ANNUAL_EXEMPTION_KRW, 0.0)
    paid_taxable_base = taxable_base_paid_by_year.get(d.year, 0.0)
    overpaid_taxable_base = max(paid_taxable_base - correct_taxable_base, 0.0)
    tax_savings = overpaid_taxable_base * CAPITAL_GAINS_TAX_RATE
    if overpaid_taxable_base > 0.0:
        taxable_base_paid_by_year[d.year] = correct_taxable_base
    return {
        "scenario": spec.scenario,
        "label": spec.label,
        "tax_year": d.year,
        "payment_date": d,
        "realized_gain_after_tlh_krw": total,
        "paid_taxable_base_before_true_up_krw": paid_taxable_base,
        "correct_taxable_base_after_tlh_krw": correct_taxable_base,
        "tax_savings_krw": tax_savings,
    }


def should_tlh_review(prices: pd.DataFrame, idx: int, spec: TlhSpec) -> bool:
    if spec.review_frequency == "none":
        return False
    if spec.review_frequency == "quarter_end":
        return is_quarter_end(prices, idx)
    if spec.review_frequency == "year_end":
        if idx == len(prices) - 1:
            return True
        d = prices.loc[idx, "date"]
        next_d = prices.loc[idx + 1, "date"]
        return d.year != next_d.year
    raise ValueError(f"unknown TLH review frequency: {spec.review_frequency}")


def build_scenario_metrics(results: dict[str, dict]) -> pd.DataFrame:
    baseline_nav = nav_series(results["T003-A"])
    baseline_metrics = metrics_for_nav(baseline_nav)
    baseline_capital_tax = capital_tax_total(results["T003-A"])
    rows = []
    for spec in SCENARIOS:
        result = results[spec.scenario]
        nav = nav_series(result)
        metrics = metrics_for_nav(nav)
        tlh_events = result["tlh_events"]
        tlh_commission = float(tlh_events["total_tlh_commission_krw"].sum()) if not tlh_events.empty else 0.0
        realized_loss = float(tlh_events["realized_loss_krw"].sum()) if not tlh_events.empty else 0.0
        tax_savings = tax_savings_total(result)
        rows.append(
            {
                "scenario": spec.scenario,
                "label": spec.label,
                "gross_i003_5_cagr_reference": GROSS_I003_5_CAGR,
                "t000_c_baseline_cagr_reference": T000_C_BASELINE_CAGR,
                "net_cagr": metrics["cagr"],
                "net_cagr_delta_vs_t003_a_pp": (metrics["cagr"] - baseline_metrics["cagr"]) * 100.0,
                "net_sharpe": metrics["sharpe"],
                "net_sharpe_delta_vs_t003_a": metrics["sharpe"] - baseline_metrics["sharpe"],
                "net_mdd": metrics["max_drawdown"],
                "net_mdd_delta_vs_t003_a_pp": (metrics["max_drawdown"] - baseline_metrics["max_drawdown"]) * 100.0,
                "final_nav": float(nav.iloc[-1]),
                "realized_loss_krw_16y": realized_loss,
                "capital_gains_tax_paid_krw_16y": capital_tax_total(result),
                "capital_gains_tax_reduction_vs_t003_a_krw": baseline_capital_tax - capital_tax_total(result),
                "tlh_tax_savings_true_up_krw_16y": tax_savings,
                "tlh_commission_krw_16y": tlh_commission,
                "tlh_tax_savings_minus_commission_krw": tax_savings - tlh_commission,
                "tlh_event_count": int(tlh_events.shape[0]) if not tlh_events.empty else 0,
                "annual_exemption_utilization_ratio": annual_exemption_utilization_ratio(result),
                "passes_plus_0p1pp_net_cagr": bool((metrics["cagr"] - baseline_metrics["cagr"]) >= 0.001),
            }
        )
    return pd.DataFrame(rows)


def build_realized_loss_by_year(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in SCENARIOS:
        events = results[spec.scenario]["tlh_events"]
        if events.empty:
            grouped = pd.DataFrame({"tax_year": list(range(START_DATE.year, END_DATE.year + 1)), "realized_loss_krw": 0.0, "tlh_event_count": 0})
        else:
            grouped = events.groupby("tax_year", as_index=False).agg(
                realized_loss_krw=("realized_loss_krw", "sum"),
                tlh_event_count=("realized_loss_krw", "size"),
                tlh_commission_krw=("total_tlh_commission_krw", "sum"),
            )
        grouped["scenario"] = spec.scenario
        grouped["label"] = spec.label
        if "tlh_commission_krw" not in grouped.columns:
            grouped["tlh_commission_krw"] = 0.0
        rows.append(grouped[["scenario", "label", "tax_year", "realized_loss_krw", "tlh_event_count", "tlh_commission_krw"]])
    return pd.concat(rows, ignore_index=True)


def build_tax_savings_by_year(results: dict[str, dict]) -> pd.DataFrame:
    baseline = annual_capital_tax(results["T003-A"])
    rows = []
    for spec in SCENARIOS:
        current = annual_capital_tax(results[spec.scenario])
        years = sorted(set(baseline).union(current).union(range(START_DATE.year, END_DATE.year + 1)))
        for year in years:
            rows.append(
                {
                    "scenario": spec.scenario,
                    "label": spec.label,
                    "tax_year": year,
                    "baseline_capital_gains_tax_krw": baseline.get(year, 0.0),
                    "scenario_capital_gains_tax_krw": current.get(year, 0.0),
                    "capital_gains_tax_reduction_vs_t003_a_krw": baseline.get(year, 0.0) - current.get(year, 0.0),
                    "tlh_true_up_tax_savings_krw": annual_true_up_savings(results[spec.scenario]).get(year, 0.0),
                }
            )
    return pd.DataFrame(rows)


def build_tlh_events(results: dict[str, dict]) -> pd.DataFrame:
    frames = [results[spec.scenario]["tlh_events"] for spec in SCENARIOS if not results[spec.scenario]["tlh_events"].empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def build_daily_nav(results: dict[str, dict]) -> pd.DataFrame:
    base = None
    for spec in SCENARIOS:
        series = nav_series(results[spec.scenario]).rename(f"{spec.scenario}_net_nav")
        base = series.to_frame() if base is None else base.join(series, how="outer")
    return base.reset_index().rename(columns={"index": "date"})


def build_stress(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    periods = {
        "2020_covid_daily_mdd": ("mdd", pd.Timestamp("2020-02-01"), pd.Timestamp("2020-04-30")),
        "2022_krw_return": ("return", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
        "2025_spike_exclusion": ("cagr_excluding_year", START_DATE, END_DATE),
    }
    for spec in SCENARIOS:
        nav = nav_series(results[spec.scenario])
        for stress, (kind, start, end) in periods.items():
            if kind == "mdd":
                window = nav.loc[nav.index.to_series().between(start, end)]
                peak_date, trough_date, mdd = peak_to_trough(window)
                rows.append(stress_row(spec, stress, "daily_mdd", mdd, start, end, peak_date, trough_date))
            elif kind == "return":
                rows.append(stress_row(spec, stress, "calendar_year_return", period_return(nav, start, end), start, end))
            else:
                rows.append(stress_row(spec, stress, "cagr_excluding_2025_return_days", cagr_excluding_return_year(nav, 2025), start, end))
    return pd.DataFrame(rows)


def nav_series(result: dict) -> pd.Series:
    nav = result["nav"].copy()
    return nav.set_index("date")["nav"].sort_index()


def annual_capital_tax(result: dict) -> dict[int, float]:
    tax = result["tax"]
    if tax.empty:
        return {}
    capital = tax.groupby("tax_year")["capital_gains_tax_krw"].sum()
    return {int(year): float(value) for year, value in capital.items()}


def annual_true_up_savings(result: dict) -> dict[int, float]:
    true_ups = result["true_ups"]
    if true_ups.empty:
        return {}
    savings = true_ups.groupby("tax_year")["tax_savings_krw"].sum()
    return {int(year): float(value) for year, value in savings.items()}


def capital_tax_total(result: dict) -> float:
    return sum(annual_capital_tax(result).values())


def tax_savings_total(result: dict) -> float:
    return sum(annual_true_up_savings(result).values())


def annual_exemption_utilization_ratio(result: dict) -> float:
    used = 0.0
    years = range(START_DATE.year, END_DATE.year + 1)
    for year in years:
        realized = sum(gain for (gain_year, _), gain in result["realized"].items() if gain_year == year)
        used += min(max(realized, 0.0), ANNUAL_EXEMPTION_KRW)
    return used / (ANNUAL_EXEMPTION_KRW * len(list(years)))


def peak_to_trough(nav: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp, float]:
    if nav.empty:
        raise ValueError("empty stress window")
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return peak_date, trough_date, float(drawdown.loc[trough_date])


def cagr_excluding_return_year(nav: pd.Series, excluded_year: int) -> float:
    returns = nav.pct_change().fillna(0.0)
    kept = returns.loc[returns.index.year != excluded_year]
    cumulative = float((1.0 + kept).prod())
    years = kept.shape[0] / 252.0
    return cumulative ** (1.0 / years) - 1.0


def stress_row(
    spec: TlhSpec,
    stress: str,
    metric: str,
    value: float,
    start: pd.Timestamp,
    end: pd.Timestamp,
    peak_date: pd.Timestamp | None = None,
    trough_date: pd.Timestamp | None = None,
) -> dict:
    return {
        "scenario": spec.scenario,
        "label": spec.label,
        "stress": stress,
        "metric": metric,
        "value": value,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "peak_date": "" if peak_date is None else peak_date.date().isoformat(),
        "trough_date": "" if trough_date is None else trough_date.date().isoformat(),
    }


def trade_row(
    spec: TlhSpec,
    d: pd.Timestamp,
    component: str,
    side: str,
    event_type: str,
    qty: float,
    price: float,
    trade_value: float,
    realized_gain: float,
    lot_id,
    commission: float,
    capital_tax: float,
) -> dict:
    return {
        "scenario": spec.scenario,
        "label": spec.label,
        "date": d,
        "component": component,
        "side": side,
        "event_type": event_type,
        "lot_id": lot_id,
        "trade_value_krw": trade_value,
        "qty": qty,
        "price_krw": price,
        "realized_gain_krw": realized_gain,
        "rebalance_commission_krw": commission,
        "rebalance_capital_gains_tax_krw": capital_tax,
    }


def tax_row(spec: TlhSpec, tax_year: int, payment_date: pd.Timestamp, capital: float, dividend: float, event: str) -> dict:
    return {
        "scenario": spec.scenario,
        "label": spec.label,
        "tax_year": tax_year,
        "payment_date": payment_date,
        "capital_gains_tax_krw": capital,
        "dividend_withholding_krw": dividend,
        "total_tax_paid_krw": capital + dividend,
        "event": event,
    }


def write_report(
    scenarios: pd.DataFrame,
    realized_loss: pd.DataFrame,
    tax_savings: pd.DataFrame,
    events: pd.DataFrame,
    stress: pd.DataFrame,
) -> None:
    comparison = scenarios[
        [
            "scenario",
            "label",
            "net_cagr",
            "net_cagr_delta_vs_t003_a_pp",
            "net_sharpe",
            "net_mdd",
            "realized_loss_krw_16y",
            "tlh_tax_savings_true_up_krw_16y",
            "tlh_commission_krw_16y",
            "tlh_tax_savings_minus_commission_krw",
            "annual_exemption_utilization_ratio",
            "passes_plus_0p1pp_net_cagr",
        ]
    ].copy()
    baseline = scenarios.loc[scenarios["scenario"].eq("T003-A")].iloc[0]
    best = scenarios.loc[scenarios["scenario"].ne("T003-A")].sort_values("net_cagr", ascending=False).iloc[0]
    stress_pivot = stress.pivot_table(index=["scenario", "label"], columns=["stress", "metric"], values="value", aggfunc="first")
    stress_pivot.columns = [f"{a}_{b}" for a, b in stress_pivot.columns]
    stress_table = stress_pivot.reset_index()
    savings_summary = tax_savings.groupby("scenario", as_index=False)[
        ["capital_gains_tax_reduction_vs_t003_a_krw", "tlh_true_up_tax_savings_krw"]
    ].sum()
    loss_years = realized_loss.loc[realized_loss["realized_loss_krw"].lt(0.0)].sort_values("realized_loss_krw").head(10)
    event_count = 0 if events.empty else int(events.shape[0])
    pass_text = "통과" if bool(best["passes_plus_0p1pp_net_cagr"]) else "미통과"

    lines = [
        "# T003 tax-loss harvesting diagnostic",
        "",
        "## 설정",
        "",
        "- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.",
        "- Rebalance: quarterly + 0pp, HIFO lot accounting, ongoing NAV.",
        "- 세금/비용: 해외 ETF 양도세 22%, 연 250만원 공제, 매매 수수료 0.25%, 배당 원천징수 15%.",
        "- H001은 한국 주식 비대주주 가정으로 양도세/TLH를 적용하지 않았다.",
        "- 한국 세법 가정: 해외 ETF 손익통산 가능, 동일 ETF 즉시 재매수에 대한 wash sale rule 없음으로 단순화했다.",
        "- Diagnostic only: 실전 적용 전 세무 전문가 확인이 필요하다. Wash sale, 동일/유사 exposure 대체, broker reporting은 별도 검토 대상이다.",
        "- T003-A는 T000-C baseline reproduction이다. 배당 원천징수는 T000과 동일하게 세목 추적만 하고 NAV에서는 차감하지 않아 lot/tax timing 효과를 isolate했다.",
        "",
        "## 5 시나리오 net 비교",
        "",
        markdown_table(comparison),
        "",
        "## TLH 의 net CAGR 개선 효과",
        "",
        f"- Gross I003.5 참고 CAGR: {GROSS_I003_5_CAGR:.6f}.",
        f"- T000-C baseline 참고 CAGR: {T000_C_BASELINE_CAGR:.6f}.",
        f"- T003-A reproduction net CAGR: {baseline['net_cagr']:.6f}.",
        f"- TLH 최고 시나리오: {best['scenario']} {best['label']}, net CAGR {best['net_cagr']:.6f}, T003-A 대비 {best['net_cagr_delta_vs_t003_a_pp']:.3f}pp.",
        f"- 사전 기준(+0.1pp net CAGR): {pass_text}.",
        "",
        "## 가장 효과적 TLH 시나리오",
        "",
        f"- Net CAGR 기준 1위는 {best['scenario']} {best['label']}이다.",
        f"- 16년 누적 TLH tax true-up savings {best['tlh_tax_savings_true_up_krw_16y']:.0f} KRW, TLH 추가 수수료 {best['tlh_commission_krw_16y']:.0f} KRW, 순효과 {best['tlh_tax_savings_minus_commission_krw']:.0f} KRW.",
        "",
        "## 250만원 공제 활용 효율",
        "",
        f"- T003-A annual exemption utilization ratio: {baseline['annual_exemption_utilization_ratio']:.6f}.",
        f"- 최고 TLH annual exemption utilization ratio: {best['annual_exemption_utilization_ratio']:.6f}.",
        "- TLH는 손실을 같은 해 이익과 통산해 과세표준을 낮추는 구조이므로, 공제 활용률 상승 자체보다 과세표준 감소와 true-up savings가 핵심 측정치다.",
        "",
        "## 2020/2022 큰 loss 해와 2025 spike exclusion",
        "",
        markdown_table(stress_table),
        "",
        "## TLH 매매 수수료 vs 양도세 절감",
        "",
        markdown_table(savings_summary),
        "",
        "## Realized loss 발생 상위 연도",
        "",
        markdown_table(loss_years),
        "",
        "## Verdict",
        "",
        f"- Verdict: {best['scenario']}가 T003-A 대비 net CAGR을 {best['net_cagr_delta_vs_t003_a_pp']:.3f}pp 개선했다. 사전 기준은 {pass_text}.",
        "- TLH가 유효한 경우에도 결과는 한국 세법 단순화에 의존한다. 실전 적용 전 세무 전문가 확인이 필요하다.",
        "- T004 권고: account/vehicle study를 진행해 일반계좌, 연금/ISA 가능성, broker reporting, 실제 세금 납부 timing을 비교한다.",
        "",
        "## Files",
        "",
        "- tlh_scenarios.csv",
        "- realized_loss_by_year.csv",
        "- tax_savings_by_year.csv",
        "- tlh_events.csv",
        "- daily_nav_by_tlh.csv",
        "- stress_net_by_tlh.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(data: pd.DataFrame) -> str:
    if data.empty:
        return "(empty)"
    columns = list(data.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in data.iterrows():
        rows.append("| " + " | ".join(format_value(row[col]) for col in columns) + " |")
    return "\n".join([header, separator, *rows])


def format_value(value) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        return f"{value:.6f}"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    return str(value)


if __name__ == "__main__":
    _ = DIVIDEND_WITHHOLDING_RATE, DIVIDEND_YIELDS
    main()
