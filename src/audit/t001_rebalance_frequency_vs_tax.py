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
OUTPUT_DIR = Path("reports/experiments/T001_rebalance_frequency_vs_tax")

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
class FrequencySpec:
    name: str
    label: str
    mode: str
    threshold_pp: float | None = None


FREQUENCIES = (
    FrequencySpec("monthly", "Monthly", "monthly"),
    FrequencySpec("quarterly", "Quarterly", "quarterly"),
    FrequencySpec("semiannual", "Semiannual", "semiannual"),
    FrequencySpec("annual", "Annual", "annual"),
    FrequencySpec("no_rebalance", "No-rebalance", "none"),
    FrequencySpec("threshold_5pp", "Threshold 5pp", "threshold", 0.05),
    FrequencySpec("threshold_10pp", "Threshold 10pp", "threshold", 0.10),
)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = load_price_panel()
    results = {spec.name: simulate_frequency(prices, spec, after_tax=True) for spec in FREQUENCIES}
    gross_results = {spec.name: simulate_frequency(prices, spec, after_tax=False) for spec in FREQUENCIES}

    frequency_metrics = build_frequency_metrics(results, gross_results)
    tax_paid = build_tax_paid_by_frequency(results)
    turnover = build_turnover_by_frequency(results)
    drift = build_tracking_drift_by_frequency(results)
    stress = build_stress_net_by_frequency(results)
    daily_nav = build_daily_nav_by_frequency(results, gross_results)

    frequency_metrics.to_csv(OUTPUT_DIR / "frequency_metrics.csv", index=False)
    tax_paid.to_csv(OUTPUT_DIR / "tax_paid_by_frequency.csv", index=False)
    turnover.to_csv(OUTPUT_DIR / "turnover_by_frequency.csv", index=False)
    drift.to_csv(OUTPUT_DIR / "tracking_drift_by_frequency.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_net_by_frequency.csv", index=False)
    daily_nav.to_csv(OUTPUT_DIR / "daily_nav_by_frequency.csv", index=False)
    write_report(frequency_metrics, tax_paid, turnover, drift, stress)


def load_price_panel() -> pd.DataFrame:
    fx = load_usdkrw()
    etfs = {ticker: load_etf_with_fx(ticker, fx) for ticker in US_ETFS}
    h001 = load_h001_curve()
    calendar = sorted(set(h001.index).union(*(set(data.index) for data in etfs.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    index = index[(index >= START_DATE) & (index <= END_DATE)]
    rows = pd.DataFrame(index=index)
    for ticker, data in etfs.items():
        aligned = data.reindex(index).ffill()
        if aligned[["close_usd", "usdkrw"]].isna().any().any():
            first_bad = aligned.loc[aligned[["close_usd", "usdkrw"]].isna().any(axis=1)].index.min().date()
            raise ValueError(f"{ticker} missing aligned price or FX on {first_bad}")
        rows[f"{ticker}_close_usd"] = aligned["close_usd"]
        rows[f"{ticker}_usdkrw"] = aligned["usdkrw"]
        rows[f"{ticker}_price_krw"] = aligned["close_usd"] * aligned["usdkrw"]
    h001_aligned = h001.reindex(index).ffill()
    if h001_aligned.isna().any():
        first_bad = h001_aligned.loc[h001_aligned.isna()].index.min().date()
        raise ValueError(f"H001 missing aligned NAV on {first_bad}")
    rows["H001_price_krw"] = h001_aligned / h001_aligned.iloc[0] * 10_000.0
    return rows.reset_index()


def load_usdkrw() -> pd.DataFrame:
    path = MACRO_DIR / "fred_dexkous_usdkrw.csv"
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})
    data["usdkrw"] = pd.to_numeric(data["usdkrw"], errors="coerce")
    return data.dropna(subset=["date", "usdkrw"]).sort_values("date").reset_index(drop=True)


def load_etf_with_fx(ticker: str, fx: pd.DataFrame) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}.csv"
    prices = pd.read_csv(path, parse_dates=["Date"])
    prices = prices.rename(columns={"Date": "date", "Close": "close_usd"})
    prices["close_usd"] = pd.to_numeric(prices["close_usd"], errors="coerce")
    prices = prices.dropna(subset=["date", "close_usd"]).sort_values("date")
    data = pd.merge_asof(prices, fx[["date", "usdkrw"]].sort_values("date"), on="date", direction="backward")
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", "close_usd", "usdkrw"]].copy()
    if data["usdkrw"].isna().any():
        first_bad = data.loc[data["usdkrw"].isna(), "date"].min().date()
        raise ValueError(f"{ticker} has no USDKRW observation on or before {first_bad}")
    return data.set_index("date").sort_index()


def load_h001_curve() -> pd.Series:
    path = H001_DIR / "equity_curve.csv"
    data = pd.read_csv(path, parse_dates=["date"])
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", "net_value"]].copy()
    data["net_value"] = pd.to_numeric(data["net_value"], errors="coerce")
    data = data.dropna(subset=["date", "net_value"]).sort_values("date")
    if data.empty:
        raise ValueError("H001 reference curve has no usable rows")
    return data.set_index("date")["net_value"]


def simulate_frequency(prices: pd.DataFrame, spec: FrequencySpec, after_tax: bool) -> dict:
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

    for idx, row in prices.iterrows():
        d = row["date"]
        pre_nav = portfolio_value(cash, lots, row)
        current_weights = portfolio_weights(cash, lots, row)
        should_rebalance = should_rebalance_on_row(prices, idx, spec, last_period_key, current_weights)
        if should_rebalance:
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

        if after_tax and is_quarter_end(prices, idx):
            dividend_tax = dividend_withholding(lots, row)
            if dividend_tax > 0.0:
                cash -= dividend_tax
                tax_rows.append(tax_row(spec, d.year, d, 0.0, dividend_tax, "dividend_withholding"))

        nav_rows.append(
            {
                "date": d,
                "frequency": spec.name,
                "label": spec.label,
                "nav": portfolio_value(cash, lots, row) / INITIAL_CAPITAL_KRW,
            }
        )
        drift_rows.append(drift_row(spec, d, portfolio_weights(cash, lots, row)))
        last_period_key = period_key(d, spec.mode)

    return {
        "spec": spec,
        "nav": pd.DataFrame(nav_rows),
        "trades": pd.DataFrame(trade_rows),
        "tax": pd.DataFrame(tax_rows),
        "drift": pd.DataFrame(drift_rows),
        "realized": realized_by_year_sleeve,
    }


def should_rebalance_on_row(
    prices: pd.DataFrame,
    idx: int,
    spec: FrequencySpec,
    last_period_key,
    current_weights: dict[str, float],
) -> bool:
    if idx == 0:
        return True
    if spec.mode == "none":
        return False
    if spec.mode == "threshold":
        threshold = spec.threshold_pp
        if threshold is None:
            raise ValueError(f"{spec.name} missing threshold")
        return max(abs(current_weights[component] - WEIGHTS[component]) for component in COMPONENTS) >= threshold
    return period_key(prices.loc[idx, "date"], spec.mode) != last_period_key


def rebalance(
    d: pd.Timestamp,
    row: pd.Series,
    spec: FrequencySpec,
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
    spec: FrequencySpec,
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


def immediate_tax_due(realized_by_year_sleeve: dict[tuple[int, str], float], year: int, taxable_base_paid_by_year: dict[int, float]) -> float:
    total = sum(gain for (gain_year, _), gain in realized_by_year_sleeve.items() if gain_year == year)
    taxable_base = max(total - ANNUAL_EXEMPTION_KRW, 0.0)
    incremental = max(taxable_base - taxable_base_paid_by_year.get(year, 0.0), 0.0)
    taxable_base_paid_by_year[year] = taxable_base_paid_by_year.get(year, 0.0) + incremental
    return incremental * CAPITAL_GAINS_TAX_RATE


def build_frequency_metrics(results: dict[str, dict], gross_results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in FREQUENCIES:
        net_nav = nav_series(results[spec.name])
        gross_nav = nav_series(gross_results[spec.name])
        net_metrics = metrics_for_nav(net_nav)
        gross_metrics = metrics_for_nav(gross_nav)
        tax = results[spec.name]["tax"]
        trades = results[spec.name]["trades"]
        drift = results[spec.name]["drift"]
        capital_tax = float(tax["capital_gains_tax_krw"].sum()) if not tax.empty else 0.0
        dividend_tax = float(tax["dividend_withholding_krw"].sum()) if not tax.empty else 0.0
        realized = total_realized_gain(results[spec.name]["realized"])
        rows.append(
            {
                "frequency": spec.name,
                "label": spec.label,
                "gross_cagr": gross_metrics["cagr"],
                "after_tax_cagr": net_metrics["cagr"],
                "after_tax_sharpe": net_metrics["sharpe"],
                "after_tax_mdd": net_metrics["max_drawdown"],
                "gross_final_nav": float(gross_nav.iloc[-1]),
                "after_tax_final_nav": float(net_nav.iloc[-1]),
                "realized_gains_krw_16y": realized,
                "capital_gains_tax_krw_16y": capital_tax,
                "dividend_withholding_krw_16y": dividend_tax,
                "total_tax_paid_krw_16y": capital_tax + dividend_tax,
                "average_annual_tax_paid_krw": average_annual_tax(tax),
                "max_annual_tax_paid_krw": max_annual_tax(tax),
                "average_quarterly_turnover": average_period_turnover(trades, "Q"),
                "average_annual_turnover": average_period_turnover(trades, "Y"),
                "average_tracking_drift_pp": float(drift["portfolio_abs_drift"].mean() * 100.0),
                "max_tracking_drift_pp": float(drift["max_component_abs_drift"].max() * 100.0),
            }
        )
    return pd.DataFrame(rows)


def build_tax_paid_by_frequency(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in FREQUENCIES:
        tax = results[spec.name]["tax"]
        if tax.empty:
            years = range(START_DATE.year, END_DATE.year + 1)
            grouped = pd.DataFrame({"tax_year": list(years), "capital_gains_tax_krw": 0.0, "dividend_withholding_krw": 0.0})
        else:
            grouped = tax.groupby("tax_year", as_index=False)[["capital_gains_tax_krw", "dividend_withholding_krw"]].sum()
        grouped["frequency"] = spec.name
        grouped["label"] = spec.label
        grouped["total_tax_paid_krw"] = grouped["capital_gains_tax_krw"] + grouped["dividend_withholding_krw"]
        rows.append(grouped[["frequency", "label", "tax_year", "capital_gains_tax_krw", "dividend_withholding_krw", "total_tax_paid_krw"]])
    data = pd.concat(rows, ignore_index=True)
    summary = data.groupby("frequency")["total_tax_paid_krw"].agg(average_year="mean", max_year="max").reset_index()
    return data.merge(summary, on="frequency", how="left")


def build_turnover_by_frequency(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in FREQUENCIES:
        trades = results[spec.name]["trades"]
        if trades.empty:
            continue
        rebalances = trades.groupby("date", as_index=False).agg(
            one_way_turnover=("one_way_turnover", "first"),
            buy_amount_krw=("trade_value_krw", lambda values: float(values[values > 0.0].sum())),
            sell_amount_krw=("trade_value_krw", lambda values: float(-values[values < 0.0].sum())),
            commission_krw=("rebalance_commission_krw", "first"),
            capital_gains_tax_krw=("rebalance_capital_gains_tax_krw", "first"),
        )
        rebalances = rebalances.loc[pd.to_datetime(rebalances["date"]) > START_DATE].copy()
        if rebalances.empty:
            continue
        rebalances["frequency"] = spec.name
        rebalances["label"] = spec.label
        rebalances["quarter"] = pd.to_datetime(rebalances["date"]).dt.to_period("Q").astype(str)
        rebalances["year"] = pd.to_datetime(rebalances["date"]).dt.year
        rebalances["average_quarterly_turnover"] = rebalances.groupby("frequency")["one_way_turnover"].transform("mean")
        rebalances["annual_turnover"] = rebalances.groupby(["frequency", "year"])["one_way_turnover"].transform("sum")
        rebalances["average_annual_turnover"] = rebalances.groupby("frequency")["annual_turnover"].transform("mean")
        rows.append(rebalances)
    return pd.concat(rows, ignore_index=True)


def build_tracking_drift_by_frequency(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for spec in FREQUENCIES:
        drift = results[spec.name]["drift"].copy()
        summary = {
            "frequency": spec.name,
            "label": spec.label,
            "average_portfolio_abs_drift_pp": float(drift["portfolio_abs_drift"].mean() * 100.0),
            "max_component_abs_drift_pp": float(drift["max_component_abs_drift"].max() * 100.0),
        }
        for component in COMPONENTS:
            summary[f"{component}_average_abs_drift_pp"] = float(drift[f"{component}_abs_drift"].mean() * 100.0)
            summary[f"{component}_max_abs_drift_pp"] = float(drift[f"{component}_abs_drift"].max() * 100.0)
        rows.append(summary)
    return pd.DataFrame(rows)


def build_stress_net_by_frequency(results: dict[str, dict]) -> pd.DataFrame:
    rows = []
    periods = {
        "2020_covid_daily_mdd": ("mdd", pd.Timestamp("2020-02-01"), pd.Timestamp("2020-04-30")),
        "2022_krw_return": ("return", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
        "2025_spike_exclusion": ("cagr_excluding_year", START_DATE, END_DATE),
        "subperiod_2010_2017": ("period_metrics", pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        "subperiod_2018_2026": ("period_metrics", pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
    }
    for spec in FREQUENCIES:
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


def build_daily_nav_by_frequency(results: dict[str, dict], gross_results: dict[str, dict]) -> pd.DataFrame:
    base = None
    for spec in FREQUENCIES:
        net = nav_series(results[spec.name]).rename(f"{spec.name}_after_tax_nav")
        gross = nav_series(gross_results[spec.name]).rename(f"{spec.name}_gross_nav")
        piece = pd.concat([gross, net], axis=1)
        base = piece if base is None else base.join(piece, how="outer")
    if base is None:
        raise ValueError("no NAV results")
    return base.reset_index().rename(columns={"index": "date"})


def metrics_for_nav(nav: pd.Series) -> dict[str, float]:
    returns = nav.pct_change().fillna(0.0)
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    drawdown = nav / nav.cummax() - 1.0
    return {
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), float(returns.std())),
        "max_drawdown": float(drawdown.min()),
    }


def nav_series(result: dict) -> pd.Series:
    nav = result["nav"].copy()
    return nav.set_index("date")["nav"].sort_index()


def portfolio_value(cash: float, lots: dict[str, list[dict]], row: pd.Series) -> float:
    return cash + sum(holding_value(lots[component], row, component) for component in COMPONENTS)


def holding_value(component_lots: list[dict], row: pd.Series, component: str) -> float:
    return sum(lot["qty_open"] for lot in component_lots) * component_price(row, component)


def portfolio_weights(cash: float, lots: dict[str, list[dict]], row: pd.Series) -> dict[str, float]:
    nav = portfolio_value(cash, lots, row)
    if nav <= 0.0:
        return {component: 0.0 for component in COMPONENTS}
    return {component: holding_value(lots[component], row, component) / nav for component in COMPONENTS}


def component_price(row: pd.Series, component: str) -> float:
    return float(row[f"{component}_price_krw"])


def dividend_withholding(lots: dict[str, list[dict]], row: pd.Series) -> float:
    return sum(holding_value(lots[component], row, component) * DIVIDEND_YIELDS[component] / 4.0 * DIVIDEND_WITHHOLDING_RATE for component in US_ETFS)


def period_key(d: pd.Timestamp, mode: str):
    if mode == "monthly":
        return d.year, d.month
    if mode == "quarterly":
        return d.year, (d.month - 1) // 3 + 1
    if mode == "semiannual":
        return d.year, 1 if d.month <= 6 else 2
    if mode == "annual":
        return d.year
    if mode in {"none", "threshold"}:
        return None
    raise ValueError(f"unknown mode: {mode}")


def is_quarter_end(prices: pd.DataFrame, idx: int) -> bool:
    if idx == len(prices) - 1:
        return True
    d = prices.loc[idx, "date"]
    next_d = prices.loc[idx + 1, "date"]
    return (d.year, (d.month - 1) // 3) != (next_d.year, (next_d.month - 1) // 3)


def make_lot(lot_id: int, d: pd.Timestamp, component: str, qty: float, price: float, row: pd.Series) -> dict:
    return {
        "lot_id": lot_id,
        "component": component,
        "buy_date": d,
        "qty_open": qty,
        "buy_price_krw": price,
        "buy_price_usd": row.get(f"{component}_close_usd", ""),
        "buy_usdkrw": row.get(f"{component}_usdkrw", ""),
    }


def trade_row(
    spec: FrequencySpec,
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
        "frequency": spec.name,
        "label": spec.label,
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


def tax_row(spec: FrequencySpec, tax_year: int, payment_date: pd.Timestamp, capital: float, dividend: float, event: str) -> dict:
    return {
        "frequency": spec.name,
        "label": spec.label,
        "tax_year": tax_year,
        "payment_date": payment_date,
        "capital_gains_tax_krw": capital,
        "dividend_withholding_krw": dividend,
        "total_tax_paid_krw": capital + dividend,
        "event": event,
    }


def drift_row(spec: FrequencySpec, d: pd.Timestamp, current_weights: dict[str, float]) -> dict:
    row = {"frequency": spec.name, "label": spec.label, "date": d}
    abs_drifts = []
    for component in COMPONENTS:
        drift = current_weights[component] - WEIGHTS[component]
        row[f"{component}_weight"] = current_weights[component]
        row[f"{component}_target_weight"] = WEIGHTS[component]
        row[f"{component}_drift"] = drift
        row[f"{component}_abs_drift"] = abs(drift)
        abs_drifts.append(abs(drift))
    row["portfolio_abs_drift"] = sum(abs_drifts)
    row["max_component_abs_drift"] = max(abs_drifts)
    return row


def total_realized_gain(realized_by_year_sleeve: dict[tuple[int, str], float]) -> float:
    return float(sum(realized_by_year_sleeve.values()))


def average_annual_tax(tax: pd.DataFrame) -> float:
    if tax.empty:
        return 0.0
    return float(tax.groupby("tax_year")["total_tax_paid_krw"].sum().mean())


def max_annual_tax(tax: pd.DataFrame) -> float:
    if tax.empty:
        return 0.0
    return float(tax.groupby("tax_year")["total_tax_paid_krw"].sum().max())


def average_period_turnover(trades: pd.DataFrame, freq: str) -> float:
    if trades.empty:
        return 0.0
    rebalances = trades.groupby("date", as_index=False)["one_way_turnover"].first()
    rebalances = rebalances.loc[pd.to_datetime(rebalances["date"]) > START_DATE].copy()
    if rebalances.empty:
        return 0.0
    rebalances["period"] = pd.to_datetime(rebalances["date"]).dt.to_period(freq)
    return float(rebalances.groupby("period")["one_way_turnover"].sum().mean())


def peak_to_trough(nav: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp, float]:
    if nav.empty:
        raise ValueError("empty stress window")
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return peak_date, trough_date, float(drawdown.loc[trough_date])


def period_return(nav: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> float:
    window = nav.loc[nav.index.to_series().between(start, end)]
    if window.shape[0] < 2:
        return float("nan")
    return float(window.iloc[-1] / window.iloc[0] - 1.0)


def cagr_excluding_return_year(nav: pd.Series, excluded_year: int) -> float:
    returns = nav.pct_change().fillna(0.0)
    kept = returns.loc[returns.index.year != excluded_year]
    if kept.empty:
        return float("nan")
    cumulative = float((1.0 + kept).prod())
    years = kept.shape[0] / 252.0
    return cumulative ** (1.0 / years) - 1.0


def stress_row(
    spec: FrequencySpec,
    stress: str,
    metric: str,
    value: float,
    start: pd.Timestamp,
    end: pd.Timestamp,
    peak_date: pd.Timestamp | None = None,
    trough_date: pd.Timestamp | None = None,
) -> dict:
    return {
        "frequency": spec.name,
        "label": spec.label,
        "stress": stress,
        "metric": metric,
        "value": value,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "peak_date": "" if peak_date is None else peak_date.date().isoformat(),
        "trough_date": "" if trough_date is None else trough_date.date().isoformat(),
    }


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator and not math.isnan(denominator) else float("nan")


def write_report(
    metrics: pd.DataFrame,
    tax_paid: pd.DataFrame,
    turnover: pd.DataFrame,
    drift: pd.DataFrame,
    stress: pd.DataFrame,
) -> None:
    ranked = metrics.sort_values("after_tax_cagr", ascending=False).reset_index(drop=True)
    winner = ranked.iloc[0]
    quarterly = metrics.loc[metrics["frequency"].eq("quarterly")].iloc[0]
    annual = metrics.loc[metrics["frequency"].eq("annual")].iloc[0]
    no_rebalance = metrics.loc[metrics["frequency"].eq("no_rebalance")].iloc[0]
    threshold = metrics.loc[metrics["frequency"].isin(["threshold_5pp", "threshold_10pp"])].copy()
    equivalent = abs(float(winner["after_tax_cagr"]) - float(quarterly["after_tax_cagr"])) < 0.005
    verdict_frequency = "quarterly" if equivalent else str(winner["frequency"])
    verdict_label = "Quarterly" if equivalent else str(winner["label"])
    q_minus_a = float(quarterly["after_tax_cagr"] - annual["after_tax_cagr"])

    comparison = metrics[
        [
            "label",
            "gross_cagr",
            "after_tax_cagr",
            "after_tax_sharpe",
            "after_tax_mdd",
            "realized_gains_krw_16y",
            "total_tax_paid_krw_16y",
            "average_annual_turnover",
            "average_tracking_drift_pp",
        ]
    ].copy()
    comparison = comparison.sort_values("after_tax_cagr", ascending=False)

    lines = [
        "# T001 rebalance frequency vs tax",
        "",
        "## 설정",
        "",
        "- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.",
        "- 세금/비용: HIFO lot accounting, 연 250만원 공제, ongoing NAV, 매매 수수료 0.25% 양방향, 배당 원천징수 15%, 양도세 22%, FX spread 0bps.",
        "- terminal liquidation tax는 포함하지 않았다.",
        "",
        "## 7 frequency gross vs after-tax 비교",
        "",
        markdown_table(comparison),
        "",
        "## Net CAGR 1위",
        "",
        f"- 1위: {winner['label']} after-tax CAGR {winner['after_tax_cagr']:.6f}, Sharpe {winner['after_tax_sharpe']:.6f}, MDD {winner['after_tax_mdd']:.6f}.",
        f"- Quarterly와 1위 차이: {(float(winner['after_tax_cagr']) - float(quarterly['after_tax_cagr'])) * 100.0:.3f}pp.",
        "- 사전 기준상 차이가 0.5pp 미만이면 equivalent로 보고 현행 quarterly를 유지한다.",
        "",
        "## Quarterly vs annual",
        "",
        f"- Quarterly after-tax CAGR {quarterly['after_tax_cagr']:.6f}, Annual {annual['after_tax_cagr']:.6f}, delta {q_minus_a * 100.0:.3f}pp.",
        f"- Quarterly 총 세금 {quarterly['total_tax_paid_krw_16y']:,.0f} KRW, Annual 총 세금 {annual['total_tax_paid_krw_16y']:,.0f} KRW.",
        f"- Quarterly 평균 연 turnover {quarterly['average_annual_turnover']:.6f}, Annual 평균 연 turnover {annual['average_annual_turnover']:.6f}.",
        "",
        "## Threshold rebalance 효과",
        "",
    ]
    for _, row in threshold.iterrows():
        lines.append(
            f"- {row['label']}: after-tax CAGR {row['after_tax_cagr']:.6f}, 총 세금 {row['total_tax_paid_krw_16y']:,.0f} KRW, 평균 drift {row['average_tracking_drift_pp']:.3f}pp."
        )
    lines.extend(
        [
            "",
            "## No-rebalance 효과",
            "",
            f"- No-rebalance after-tax CAGR {no_rebalance['after_tax_cagr']:.6f}, Sharpe {no_rebalance['after_tax_sharpe']:.6f}, MDD {no_rebalance['after_tax_mdd']:.6f}.",
            f"- 총 세금 {no_rebalance['total_tax_paid_krw_16y']:,.0f} KRW, 평균 tracking drift {no_rebalance['average_tracking_drift_pp']:.3f}pp, 최대 component drift {no_rebalance['max_tracking_drift_pp']:.3f}pp.",
            "",
            "## Stress 재검증",
            "",
            markdown_table(stress_pivot_for_report(stress)),
            "",
            "## Verdict",
            "",
            f"- 권장 rebalance frequency: {verdict_label}.",
            f"- 사전 기준 적용 결과: {'Quarterly와 1위가 equivalent이므로 현행 quarterly 유지' if equivalent else '1위 frequency가 quarterly 대비 0.5pp 이상 우위'}."
            f"",
            "- T002 no-trade band 진행 권고: threshold 결과가 세금 절감과 drift 비용의 trade-off를 직접 보여주므로, quarterly schedule 위에 no-trade band를 얹는 후속 실험이 필요하다.",
            "",
            "## Files",
            "",
            "- frequency_metrics.csv",
            "- tax_paid_by_frequency.csv",
            "- turnover_by_frequency.csv",
            "- tracking_drift_by_frequency.csv",
            "- stress_net_by_frequency.csv",
            "- daily_nav_by_frequency.csv",
        ]
    )
    _ = tax_paid, turnover, drift
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stress_pivot_for_report(stress: pd.DataFrame) -> pd.DataFrame:
    keep = stress.loc[
        stress["stress"].isin(["2020_covid_daily_mdd", "2022_krw_return", "2025_spike_exclusion"])
    ].copy()
    keep["column"] = keep["stress"] + "_" + keep["metric"]
    pivot = keep.pivot_table(index="label", columns="column", values="value", aggfunc="first").reset_index()
    return pivot


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
    return str(value)


if __name__ == "__main__":
    main()
