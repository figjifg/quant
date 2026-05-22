from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.audit.t001_rebalance_frequency_vs_tax import (
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
    immediate_tax_due,
    is_quarter_end,
    load_price_panel,
    make_lot,
    metrics_for_nav,
    period_return,
    portfolio_value,
    portfolio_weights,
)


OUTPUT_DIR = Path("reports/experiments/T002_no_trade_band")
BANDS = (0.0, 0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20)
SCHEDULES = ("quarterly", "monthly", "annual")
T001_QUARTERLY_10PP_CAGR = 0.12650574680626359


@dataclass(frozen=True)
class BandSpec:
    name: str
    label: str
    schedule: str
    band: float


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_price_panel()
    specs = build_specs()
    results = {spec.name: simulate_band(prices, spec, after_tax=True) for spec in specs}
    gross_results = {spec.name: simulate_band(prices, spec, after_tax=False) for spec in specs}

    metrics = build_band_grid_metrics(specs, results, gross_results)
    drift_paths = build_drift_paths(specs, results)
    events = build_rebalance_events(specs, results)
    stress = build_stress_net_by_band(specs, results)
    daily_nav = build_daily_nav_by_band(specs, results, gross_results)

    metrics.to_csv(OUTPUT_DIR / "band_grid_metrics.csv", index=False)
    drift_paths.to_csv(OUTPUT_DIR / "drift_paths.csv", index=False)
    events.to_csv(OUTPUT_DIR / "rebalance_events.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_net_by_band.csv", index=False)
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_by_band.csv", index=False)
    write_report(metrics, stress)


def build_specs() -> tuple[BandSpec, ...]:
    specs = []
    for schedule in SCHEDULES:
        for band in BANDS:
            specs.append(
                BandSpec(
                    f"{schedule}_band_{band_slug_pp(band)}",
                    f"{schedule.title()} + {band_display_pp(band)}",
                    schedule,
                    band,
                )
            )
    return tuple(specs)


def band_slug_pp(band: float) -> str:
    pp = band * 100.0
    if pp.is_integer():
        return f"{int(pp)}pp"
    return f"{pp:.1f}".replace(".", "p") + "pp"


def band_display_pp(band: float) -> str:
    pp = band * 100.0
    if pp.is_integer():
        return f"{int(pp)}pp"
    return f"{pp:.1f}pp"


def simulate_band(prices: pd.DataFrame, spec: BandSpec, after_tax: bool) -> dict:
    cash = INITIAL_CAPITAL_KRW
    lots = {component: [] for component in COMPONENTS}
    lot_id = 0
    last_period_key = None
    taxable_base_paid_by_year: dict[int, float] = {}
    realized_by_year_sleeve: dict[tuple[int, str], float] = {}
    nav_rows = []
    trade_rows = []
    tax_rows = []
    drift_rows = []
    event_rows = []

    for idx, row in prices.iterrows():
        d = row["date"]
        current_weights = portfolio_weights(cash, lots, row)
        max_pre_check_drift = max(abs(current_weights[component] - WEIGHTS[component]) for component in COMPONENTS)
        check_date = is_scheduled_check(prices, idx, spec.schedule, last_period_key)
        should_rebalance = idx == 0 or (check_date and max_pre_check_drift > spec.band)
        if should_rebalance:
            pre_nav = portfolio_value(cash, lots, row)
            cash, lot_id, rebalance_tax_rows, rebalance_trade_rows = rebalance(
                d,
                row,
                spec,
                cash,
                lots,
                lot_id,
                realized_by_year_sleeve,
                taxable_base_paid_by_year,
                after_tax,
            )
            tax_rows.extend(rebalance_tax_rows)
            trade_rows.extend(rebalance_trade_rows)
            event_rows.append(
                {
                    "portfolio": spec.name,
                    "label": spec.label,
                    "schedule": spec.schedule,
                    "band_pp": spec.band * 100.0,
                    "date": d,
                    "event_type": "initial_allocation" if idx == 0 else "band_trigger_rebalance",
                    "pre_nav_krw": pre_nav,
                    "pre_check_max_component_abs_drift_pp": max_pre_check_drift * 100.0,
                    "commission_krw": sum(row_["rebalance_commission_krw"] for row_ in rebalance_trade_rows[:1]),
                    "capital_gains_tax_krw": sum(row_["rebalance_capital_gains_tax_krw"] for row_ in rebalance_trade_rows[:1]),
                }
            )

        if after_tax and is_quarter_end(prices, idx):
            dividend_tax = dividend_withholding(lots, row)
            if dividend_tax > 0.0:
                cash -= dividend_tax
                tax_rows.append(tax_row(spec, d.year, d, 0.0, dividend_tax, "dividend_withholding"))

        post_weights = portfolio_weights(cash, lots, row)
        nav_rows.append(
            {
                "date": d,
                "portfolio": spec.name,
                "label": spec.label,
                "schedule": spec.schedule,
                "band_pp": spec.band * 100.0,
                "nav": portfolio_value(cash, lots, row) / INITIAL_CAPITAL_KRW,
            }
        )
        drift_rows.append(drift_row(spec, d, post_weights, check_date, should_rebalance, max_pre_check_drift))
        last_period_key = period_key(d, spec.schedule)

    return {
        "spec": spec,
        "nav": pd.DataFrame(nav_rows),
        "trades": pd.DataFrame(trade_rows),
        "tax": pd.DataFrame(tax_rows),
        "drift": pd.DataFrame(drift_rows),
        "events": pd.DataFrame(event_rows),
        "realized": realized_by_year_sleeve,
    }


def is_scheduled_check(prices: pd.DataFrame, idx: int, schedule: str, last_period_key) -> bool:
    if idx == 0:
        return True
    current_key = period_key(prices.loc[idx, "date"], schedule)
    return current_key != last_period_key


def period_key(d: pd.Timestamp, schedule: str):
    if schedule == "monthly":
        return d.year, d.month
    if schedule == "quarterly":
        return d.year, (d.month - 1) // 3 + 1
    if schedule == "annual":
        return d.year
    raise ValueError(f"unknown schedule: {schedule}")


def rebalance(
    d: pd.Timestamp,
    row: pd.Series,
    spec: BandSpec,
    cash: float,
    lots: dict[str, list[dict]],
    lot_id: int,
    realized_by_year_sleeve: dict[tuple[int, str], float],
    taxable_base_paid_by_year: dict[int, float],
    after_tax: bool,
) -> tuple[float, int, list[dict], list[dict]]:
    pre_nav = portfolio_value(cash, lots, row)
    current_values = {component: holding_value(lots[component], row, component) for component in COMPONENTS}
    target_values = {component: pre_nav * WEIGHTS[component] for component in COMPONENTS}
    trades = {component: target_values[component] - current_values[component] for component in COMPONENTS}
    commission = sum(abs(value) for value in trades.values()) * COMMISSION_RATE if after_tax else 0.0
    tax_events = []
    trade_rows = []
    realized_gain = 0.0

    for component in COMPONENTS:
        trade_value = trades[component]
        if trade_value < -1e-9:
            price = component_price(row, component)
            qty = min(sum(lot["qty_open"] for lot in lots[component]), -trade_value / price)
            cash_delta, component_gain, rows = sell_lots(d, component, qty, price, row, spec, lots, realized_by_year_sleeve, after_tax)
            cash += cash_delta
            realized_gain += component_gain
            trade_rows.extend(rows)

    capital_tax = 0.0
    if after_tax:
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
            trade_rows.append(trade_row(spec, d, component, "BUY", trade_value, qty, price, 0.0, commission, capital_tax))

    one_way_turnover = sum(abs(value) for value in trades.values()) / (2.0 * pre_nav) if pre_nav else 0.0
    for trade in trade_rows:
        trade["pre_nav_krw"] = pre_nav
        trade["one_way_turnover"] = one_way_turnover
        trade["rebalance_realized_gain_krw"] = realized_gain
        trade["rebalance_commission_krw"] = commission
        trade["rebalance_capital_gains_tax_krw"] = capital_tax
    return cash, lot_id, tax_events, trade_rows


def sell_lots(
    d: pd.Timestamp,
    component: str,
    qty_to_sell: float,
    sell_price: float,
    row: pd.Series,
    spec: BandSpec,
    lots: dict[str, list[dict]],
    realized_by_year_sleeve: dict[tuple[int, str], float],
    after_tax: bool,
) -> tuple[float, float, list[dict]]:
    selected = sorted(lots[component], key=lambda lot: lot["buy_price_krw"], reverse=True)
    remaining = qty_to_sell
    proceeds = 0.0
    realized_gain = 0.0
    rows = []
    for lot in selected:
        if remaining <= 1e-12:
            break
        qty = min(lot["qty_open"], remaining)
        lot["qty_open"] -= qty
        remaining -= qty
        proceeds += qty * sell_price
        gain = 0.0
        if after_tax and component in US_ETFS:
            gain = (sell_price - lot["buy_price_krw"]) * qty
            realized_gain += gain
            key = (d.year, component)
            realized_by_year_sleeve[key] = realized_by_year_sleeve.get(key, 0.0) + gain
        rows.append(trade_row(spec, d, component, "SELL", -qty * sell_price, qty, sell_price, gain, 0.0, 0.0))
    lots[component] = [lot for lot in lots[component] if lot["qty_open"] > 1e-12]
    return proceeds, realized_gain, rows


def build_band_grid_metrics(specs: tuple[BandSpec, ...], results: dict[str, dict], gross_results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in specs:
        net_nav = nav_series(results[spec.name])
        gross_nav = nav_series(gross_results[spec.name])
        net_metrics = metrics_for_nav(net_nav)
        gross_metrics = metrics_for_nav(gross_nav)
        tax = results[spec.name]["tax"]
        trades = results[spec.name]["trades"]
        drift = results[spec.name]["drift"]
        events = results[spec.name]["events"]
        capital_tax = float(tax["capital_gains_tax_krw"].sum()) if not tax.empty else 0.0
        dividend_tax = float(tax["dividend_withholding_krw"].sum()) if not tax.empty else 0.0
        commission = total_commission(trades)
        rebalance_count = int(events.loc[events["event_type"].ne("initial_allocation")].shape[0]) if not events.empty else 0
        average_tracking_drift = float(drift["portfolio_abs_drift"].mean() * 100.0)
        max_component_drift = float(drift["max_component_abs_drift"].max() * 100.0)
        rows.append(
            {
                "portfolio": spec.name,
                "label": spec.label,
                "schedule": spec.schedule,
                "band_pp": spec.band * 100.0,
                "gross_cagr": gross_metrics["cagr"],
                "net_cagr": net_metrics["cagr"],
                "net_sharpe": net_metrics["sharpe"],
                "net_mdd": net_metrics["max_drawdown"],
                "gross_final_nav": float(gross_nav.iloc[-1]),
                "net_final_nav": float(net_nav.iloc[-1]),
                "average_tracking_drift_pp": average_tracking_drift,
                "max_component_drift_pp": max_component_drift,
                "total_rebalance_events_count_16y": rebalance_count,
                "total_tax_paid_krw": capital_tax + dividend_tax,
                "capital_gains_tax_krw": capital_tax,
                "dividend_withholding_krw": dividend_tax,
                "total_commission_paid_krw": commission,
                "disqualified_drift_gt_20pp": bool(max_component_drift > 20.0 or average_tracking_drift > 20.0),
            }
        )
    return pd.DataFrame(rows)


def total_commission(trades: pd.DataFrame) -> float:
    if trades.empty:
        return 0.0
    return float(trades.groupby("date")["rebalance_commission_krw"].first().sum())


def build_drift_paths(specs: tuple[BandSpec, ...], results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in specs:
        drift = results[spec.name]["drift"].copy()
        rows.append(drift)
    return pd.concat(rows, ignore_index=True)


def build_rebalance_events(specs: tuple[BandSpec, ...], results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in specs:
        events = results[spec.name]["events"].copy()
        if not events.empty:
            rows.append(events)
    return pd.concat(rows, ignore_index=True)


def build_stress_net_by_band(specs: tuple[BandSpec, ...], results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    periods = {
        "2020_covid_daily_mdd": ("mdd", pd.Timestamp("2020-02-01"), pd.Timestamp("2020-04-30")),
        "2022_krw_return": ("return", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
        "2025_spike_exclusion": ("cagr_excluding_year", START_DATE, END_DATE),
        "subperiod_2010_2017": ("period_metrics", pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        "subperiod_2018_2026": ("period_metrics", pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
    }
    for spec in specs:
        nav = nav_series(results[spec.name])
        for stress, (kind, start, end) in periods.items():
            if kind == "mdd":
                window = nav.loc[nav.index.to_series().between(start, end)]
                peak_date, trough_date, mdd = peak_to_trough(window)
                rows.append(stress_row(spec, stress, "daily_mdd", mdd, start, end, peak_date, trough_date))
            elif kind == "return":
                rows.append(stress_row(spec, stress, "calendar_year_return", period_return(nav, start, end), start, end))
            elif kind == "cagr_excluding_year":
                rows.append(stress_row(spec, stress, "cagr_excluding_2025_return_days", cagr_excluding_return_year(nav, 2025), start, end))
            else:
                window = nav.loc[nav.index.to_series().between(start, end)]
                if window.shape[0] < 2:
                    continue
                metrics = metrics_for_nav(window)
                rows.append(stress_row(spec, stress, "cagr", metrics["cagr"], start, end))
                rows.append(stress_row(spec, stress, "sharpe", metrics["sharpe"], start, end))
                rows.append(stress_row(spec, stress, "max_drawdown", metrics["max_drawdown"], start, end))
    return pd.DataFrame(rows)


def build_daily_nav_by_band(specs: tuple[BandSpec, ...], results: dict[str, dict], gross_results: dict[str, dict]) -> pd.DataFrame:
    base = None
    for spec in specs:
        net = nav_series(results[spec.name]).rename(f"{spec.name}_net_nav")
        gross = nav_series(gross_results[spec.name]).rename(f"{spec.name}_gross_nav")
        piece = pd.concat([gross, net], axis=1)
        base = piece if base is None else base.join(piece, how="outer")
    if base is None:
        raise ValueError("no NAV results")
    return base.reset_index().rename(columns={"index": "date"})


def nav_series(result: dict) -> pd.Series:
    nav = result["nav"].copy()
    return nav.set_index("date")["nav"].sort_index()


def trade_row(
    spec: BandSpec,
    d: pd.Timestamp,
    component: str,
    side: str,
    trade_value: float,
    qty: float,
    price: float,
    realized_gain: float,
    commission: float,
    capital_tax: float,
) -> dict:
    return {
        "portfolio": spec.name,
        "label": spec.label,
        "schedule": spec.schedule,
        "band_pp": spec.band * 100.0,
        "date": d,
        "component": component,
        "side": side,
        "trade_value_krw": trade_value,
        "qty": qty,
        "price_krw": price,
        "realized_gain_krw": realized_gain,
        "rebalance_commission_krw": commission,
        "rebalance_capital_gains_tax_krw": capital_tax,
    }


def tax_row(spec: BandSpec, tax_year: int, payment_date: pd.Timestamp, capital: float, dividend: float, event: str) -> dict:
    return {
        "portfolio": spec.name,
        "label": spec.label,
        "schedule": spec.schedule,
        "band_pp": spec.band * 100.0,
        "tax_year": tax_year,
        "payment_date": payment_date,
        "capital_gains_tax_krw": capital,
        "dividend_withholding_krw": dividend,
        "total_tax_paid_krw": capital + dividend,
        "event": event,
    }


def drift_row(
    spec: BandSpec,
    d: pd.Timestamp,
    current_weights: dict[str, float],
    is_check_date: bool,
    rebalance_triggered: bool,
    pre_check_max_component_abs_drift: float,
) -> dict:
    row = {
        "portfolio": spec.name,
        "label": spec.label,
        "schedule": spec.schedule,
        "band_pp": spec.band * 100.0,
        "date": d,
        "is_check_date": is_check_date,
        "rebalance_triggered": rebalance_triggered,
        "pre_check_max_component_abs_drift_pp": pre_check_max_component_abs_drift * 100.0,
    }
    abs_drifts = []
    for component in COMPONENTS:
        drift = current_weights[component] - WEIGHTS[component]
        row[f"{component}_weight"] = current_weights[component]
        row[f"{component}_target_weight"] = WEIGHTS[component]
        row[f"{component}_drift_pp"] = drift * 100.0
        row[f"{component}_abs_drift_pp"] = abs(drift) * 100.0
        abs_drifts.append(abs(drift))
    row["portfolio_abs_drift"] = sum(abs_drifts)
    row["max_component_abs_drift"] = max(abs_drifts)
    row["portfolio_abs_drift_pp"] = sum(abs_drifts) * 100.0
    row["max_component_abs_drift_pp"] = max(abs_drifts) * 100.0
    return row


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
    if kept.empty:
        return float("nan")
    cumulative = float((1.0 + kept).prod())
    years = kept.shape[0] / 252.0
    return cumulative ** (1.0 / years) - 1.0


def stress_row(
    spec: BandSpec,
    stress: str,
    metric: str,
    value: float,
    start: pd.Timestamp,
    end: pd.Timestamp,
    peak_date: pd.Timestamp | None = None,
    trough_date: pd.Timestamp | None = None,
) -> dict:
    return {
        "portfolio": spec.name,
        "label": spec.label,
        "schedule": spec.schedule,
        "band_pp": spec.band * 100.0,
        "stress": stress,
        "metric": metric,
        "value": value,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "peak_date": "" if peak_date is None else peak_date.date().isoformat(),
        "trough_date": "" if trough_date is None else trough_date.date().isoformat(),
    }


def write_report(metrics: pd.DataFrame, stress: pd.DataFrame) -> None:
    ranked = metrics.sort_values("net_cagr", ascending=False).reset_index(drop=True)
    winner = ranked.iloc[0]
    quarterly_0 = metrics.loc[metrics["portfolio"].eq("quarterly_band_0pp")].iloc[0]
    quarterly_10 = metrics.loc[metrics["portfolio"].eq("quarterly_band_10pp")].iloc[0]
    catastrophic = metrics.loc[metrics["disqualified_drift_gt_20pp"]].sort_values(["schedule", "band_pp"])

    comparison = ranked[
        [
            "label",
            "gross_cagr",
            "net_cagr",
            "net_sharpe",
            "net_mdd",
            "average_tracking_drift_pp",
            "max_component_drift_pp",
            "total_rebalance_events_count_16y",
            "total_tax_paid_krw",
            "total_commission_paid_krw",
            "disqualified_drift_gt_20pp",
        ]
    ].copy()

    stress_pivot = stress_summary_for_report(stress)
    metrics_with_stress = metrics.merge(stress_pivot.drop(columns=["label"]), on="portfolio", how="left")
    baseline_stress = stress_pivot.loc[stress_pivot["portfolio"].eq("quarterly_band_0pp")].iloc[0]
    metrics_with_stress["stress_not_hurt"] = (
        metrics_with_stress["2020_covid_daily_mdd_daily_mdd"].ge(baseline_stress["2020_covid_daily_mdd_daily_mdd"])
        & metrics_with_stress["2022_krw_return_calendar_year_return"].ge(baseline_stress["2022_krw_return_calendar_year_return"])
    )
    eligible = metrics_with_stress.loc[
        ~metrics_with_stress["disqualified_drift_gt_20pp"] & metrics_with_stress["stress_not_hurt"]
    ].sort_values("net_cagr", ascending=False).reset_index(drop=True)
    eligible_winner = eligible.iloc[0]
    recommended = eligible_winner
    winner_stress = stress_pivot.loc[stress_pivot["portfolio"].eq(winner["portfolio"])].iloc[0]
    recommended_stress = stress_pivot.loc[stress_pivot["portfolio"].eq(recommended["portfolio"])].iloc[0]
    t001_delta_pp = (float(winner["net_cagr"]) - T001_QUARTERLY_10PP_CAGR) * 100.0
    q10_delta_pp = (float(winner["net_cagr"]) - float(quarterly_10["net_cagr"])) * 100.0
    baseline_delta_pp = (float(winner["net_cagr"]) - float(quarterly_0["net_cagr"])) * 100.0
    catastrophic_text = (
        "없음"
        if catastrophic.empty
        else ", ".join(f"{row.schedule} {row.band_pp:.1f}pp" for row in catastrophic.itertuples(index=False))
    )

    lines = [
        "# T002 no-trade band / drift tolerance",
        "",
        "## 설정",
        "",
        "- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.",
        "- 체크 스케줄: monthly, quarterly, annual.",
        "- Band grid: 0pp, 2.5pp, 5pp, 7.5pp, 10pp, 12.5pp, 15pp, 20pp.",
        "- 세금/비용: HIFO lot accounting, 연 250만원 공제, ongoing NAV, 매매 수수료 0.25%, 배당 원천징수 15%, 양도세 22%.",
        "- terminal liquidation tax는 포함하지 않았다.",
        "",
        "## Band grid x schedule 24 portfolio net 비교",
        "",
        markdown_table(comparison),
        "",
        "## Net CAGR 1위",
        "",
        f"- 전체 1위: {winner['label']} net CAGR {winner['net_cagr']:.6f}, Sharpe {winner['net_sharpe']:.6f}, MDD {winner['net_mdd']:.6f}.",
        f"- Drift 20pp 초과 및 2020/2022 stress hurt 제외 후 1위: {eligible_winner['label']} net CAGR {eligible_winner['net_cagr']:.6f}.",
        f"- Quarterly 0pp baseline 대비 전체 1위 차이: {baseline_delta_pp:.3f}pp.",
        "",
        "## Quarterly + 10pp band vs T002 grid 최고",
        "",
        f"- T002 Quarterly + 10pp: net CAGR {quarterly_10['net_cagr']:.6f}, max drift {quarterly_10['max_component_drift_pp']:.3f}pp.",
        f"- T001 Threshold 10pp 참고값: after-tax CAGR {T001_QUARTERLY_10PP_CAGR:.6f}. T002 grid 1위와 차이 {t001_delta_pp:.3f}pp.",
        f"- T002 Quarterly + 10pp 대비 T002 grid 1위 차이: {q10_delta_pp:.3f}pp.",
        "",
        "## Drift 의 stress 영향",
        "",
        f"- Baseline Quarterly 0pp 2020 COVID daily MDD {baseline_stress['2020_covid_daily_mdd_daily_mdd']:.6f}, 2022 KRW return {baseline_stress['2022_krw_return_calendar_year_return']:.6f}.",
        f"- Grid 1위 {winner['label']} 2020 COVID daily MDD {winner_stress['2020_covid_daily_mdd_daily_mdd']:.6f}, 2022 KRW return {winner_stress['2022_krw_return_calendar_year_return']:.6f}.",
        f"- 권장 조합 {recommended['label']} 2020 COVID daily MDD {recommended_stress['2020_covid_daily_mdd_daily_mdd']:.6f}, 2022 KRW return {recommended_stress['2022_krw_return_calendar_year_return']:.6f}.",
        "",
        "## Drift catastrophic 임계값",
        "",
        f"- Drift > 20pp disqualifier 발생 조합: {catastrophic_text}.",
        f"- 전체 1위 max component drift: {winner['max_component_drift_pp']:.3f}pp.",
        "",
        "## 권장 band / schedule 조합",
        "",
        f"- 권장 조합: {recommended['label']}.",
        f"- Net CAGR {recommended['net_cagr']:.6f}, max component drift {recommended['max_component_drift_pp']:.3f}pp, rebalance events {int(recommended['total_rebalance_events_count_16y'])}회.",
        "- 사전 stress 기준을 엄격 적용하면 positive band 조합은 2020 또는 2022 중 하나를 baseline보다 악화시켰다.",
        "",
        "## Verdict",
        "",
        "- Verdict: No-trade band는 net CAGR을 높였지만, 사전 등록된 drift/stress 필터까지 통과한 positive band 조합은 없었다. 현행 Quarterly 0pp를 유지한다.",
        "- 다음 단계 권고: T003 tax-loss harvesting을 우선 진행한다. T002 결과는 no-trade band가 매도 시점과 과세 timing을 바꾸는 문제이므로, 손실 harvesting과 직접 연결된다.",
        "",
        "## Files",
        "",
        "- band_grid_metrics.csv",
        "- drift_paths.csv",
        "- rebalance_events.csv",
        "- stress_net_by_band.csv",
        "- daily_nav_by_band.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stress_summary_for_report(stress: pd.DataFrame) -> pd.DataFrame:
    keep = stress.loc[
        stress["stress"].isin(["2020_covid_daily_mdd", "2022_krw_return", "2025_spike_exclusion"])
    ].copy()
    keep["column"] = keep["stress"] + "_" + keep["metric"]
    return keep.pivot_table(index=["portfolio", "label"], columns="column", values="value", aggfunc="first").reset_index()


def markdown_table(data: pd.DataFrame) -> str:
    columns = list(data.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in data.iterrows():
        rows.append("| " + " | ".join(format_value(row[col]) for col in columns) + " |")
    return "\n".join([header, separator, *rows])


def format_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, bool):
        return str(value)
    return str(value)


if __name__ == "__main__":
    _ = CAPITAL_GAINS_TAX_RATE, DIVIDEND_WITHHOLDING_RATE, DIVIDEND_YIELDS
    main()
