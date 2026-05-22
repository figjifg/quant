from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit.q007_cost_turnover_validation import (
    CAPITAL_GAINS_TAX_RATE,
    COMMISSION_RATE,
    DIRECT_Q,
    DIVIDEND_WITHHOLDING_RATE,
    DIVIDEND_YIELDS,
    END_DATE,
    ETF_DIR,
    FACTOR_ETFS,
    FX_SPREAD_RATE,
    Lot,
    REPORT_DIR as Q007_REPORT_DIR,
    ROOT,
    START_DATE,
    load_etf_krw_nav,
    load_nav,
    load_usdkrw,
    metrics,
    sell_hifo,
    table_for_report,
    tax_due,
)


REPORT_DIR = ROOT / "reports" / "experiments" / "Q008_portfolio_combination"
H001_DIR = ROOT / "reports" / "experiments" / "H001_kr_short_rate_sleeve"
N001_DIR = ROOT / "reports" / "experiments" / "N001_gold_sleeve"
N002_DIR = ROOT / "reports" / "experiments" / "N002_cash_shy_sleeve"

BASELINE_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
CORE_ETFS = ("SPY", "QQQ", "IEF")
SLEEVES = ("SCHD", "COWZ", "MTUM", "Q002", "Q006")
TAXABLE_COMPONENTS = set(CORE_ETFS).union(SLEEVES)
STRESS_WINDOWS = {
    "dot_com_proxy_2002_07_2003_12": (pd.Timestamp("2002-07-01"), pd.Timestamp("2003-12-31")),
    "gfc_proxy_2008_2009": (pd.Timestamp("2008-01-01"), pd.Timestamp("2009-12-31")),
    "covid_2020_02_2020_03": (pd.Timestamp("2020-02-01"), pd.Timestamp("2020-03-31")),
    "rate_shock_2022": (pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Q008 P08_IEF30 + ETF proxy portfolio combination.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    run(args.report_dir)
    return 0


def run(report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    fx = load_usdkrw()
    components = load_components(fx)
    candidates = registered_candidates()

    baseline_result = simulate_portfolio("P08_IEF30_BASELINE", BASELINE_WEIGHTS, components)
    baseline_metrics = row_metrics("P08_IEF30_BASELINE", "baseline", "baseline", 0.0, baseline_result)

    rows = []
    navs = {"P08_IEF30_BASELINE": baseline_result["net_nav"]}
    for candidate in candidates:
        result = simulate_portfolio(candidate["candidate"], candidate["weights"], components)
        navs[candidate["candidate"]] = result["net_nav"]
        rows.append(row_metrics(**candidate, result=result))

    combination = pd.DataFrame(rows)
    for col in ["net_cagr", "net_sharpe", "net_mdd"]:
        combination[f"delta_{col}_vs_baseline"] = combination[col] - baseline_metrics[col]
    combination["excess_net_cagr_vs_baseline"] = combination["delta_net_cagr_vs_baseline"]
    combination = combination.sort_values(["method", "sleeve", "q_weight"]).reset_index(drop=True)

    stress = build_stress_windows(navs, candidates, components)
    deltas = build_delta_table(combination, baseline_metrics)
    top = combination.sort_values(
        ["net_sharpe", "net_mdd", "net_cagr", "candidate"],
        ascending=[False, False, False, True],
    ).head(10)

    write_config(report_dir / "config.yaml", candidates)
    combination.to_csv(report_dir / "combination_metrics.csv", index=False)
    stress.to_csv(report_dir / "stress_windows.csv", index=False)
    deltas.to_csv(report_dir / "delta_vs_p08_ief30.csv", index=False)
    top.to_csv(report_dir / "top_ranked_candidates.csv", index=False)
    write_report(report_dir / "report.md", baseline_metrics, combination, stress, top)
    write_q_family_final_summary(ROOT / "reports" / "experiments" / "Q_family_final_summary.md", combination, top)


def load_components(fx: pd.DataFrame) -> dict[str, pd.Series]:
    components = {ticker: load_etf_krw_nav(ticker, fx) for ticker in CORE_ETFS}
    h001 = pd.read_csv(H001_DIR / "equity_curve.csv", parse_dates=["date"])
    h001 = h001.loc[h001["date"].between(START_DATE, END_DATE), ["date", "net_value"]].copy()
    h001["net_value"] = pd.to_numeric(h001["net_value"], errors="coerce")
    h001 = h001.dropna(subset=["date", "net_value"]).sort_values("date")
    components["H001"] = pd.Series(
        h001["net_value"].to_numpy() / h001["net_value"].iloc[0],
        index=pd.DatetimeIndex(h001["date"]),
        name="H001",
    )
    spy = components["SPY"]
    for ticker in FACTOR_ETFS:
        components[ticker] = sleeve_with_spy_proxy(load_etf_krw_nav(ticker, fx), spy, ticker)
    for name, directory in DIRECT_Q.items():
        components[name] = sleeve_with_spy_proxy(load_nav(directory / "portfolio_daily_nav.csv"), spy, name)
    return components


def sleeve_with_spy_proxy(sleeve: pd.Series, spy: pd.Series, name: str) -> pd.Series:
    calendar = pd.DatetimeIndex(sorted(set(spy.index).union(set(sleeve.index))))
    calendar = calendar[(calendar >= START_DATE) & (calendar <= END_DATE)]
    spy_aligned = spy.reindex(calendar).ffill()
    sleeve_aligned = sleeve.reindex(calendar).ffill()
    first = sleeve.dropna().index[0]
    out = spy_aligned.copy()
    after = calendar >= first
    scale = spy_aligned.loc[first] / sleeve_aligned.loc[first] if first in sleeve_aligned.index else 1.0
    out.loc[after] = sleeve_aligned.loc[after] * scale
    out = out / out.iloc[0]
    out.name = name
    return out.dropna()


def registered_candidates() -> list[dict[str, object]]:
    rows = []
    for sleeve in SLEEVES:
        for q_weight in (0.10, 0.20):
            weights = {"SPY": 0.29 - q_weight, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30, sleeve: q_weight}
            rows.append(candidate_row("A", "SPY_replacement_primary", sleeve, q_weight, weights))
    for sleeve in SLEEVES:
        for q_weight in (0.10, 0.20):
            scale = (0.50 - q_weight) / 0.50
            weights = {"SPY": 0.29 * scale, "QQQ": 0.21 * scale, "H001": 0.20, "IEF": 0.30, sleeve: q_weight}
            rows.append(candidate_row("B", "US_equity_pro_rata_secondary", sleeve, q_weight, weights))
    for sleeve in SLEEVES:
        for q_weight in (0.10, 0.15):
            weights = {"SPY": 0.29, "QQQ": 0.21 - q_weight, "H001": 0.20, "IEF": 0.30, sleeve: q_weight}
            rows.append(candidate_row("C", "QQQ_replacement_diagnostic", sleeve, q_weight, weights))
    if len(rows) != 30:
        raise RuntimeError(f"Expected 30 pre-registered candidates, got {len(rows)}")
    return rows


def candidate_row(method: str, method_name: str, sleeve: str, q_weight: float, weights: dict[str, float]) -> dict[str, object]:
    total = sum(weights.values())
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"weights sum to {total}")
    weight_label = int(round(q_weight * 100))
    return {
        "candidate": f"Q008-{method}-{sleeve}-{weight_label:02d}",
        "method": f"Method {method}",
        "method_name": method_name,
        "sleeve": sleeve,
        "sleeve_type": "direct_q_diagnostic" if sleeve in DIRECT_Q else "etf_proxy",
        "q_weight": q_weight,
        "weights": weights,
    }


def simulate_portfolio(candidate: str, weights: dict[str, float], components: dict[str, pd.Series]) -> dict[str, object]:
    prices = align_prices({name: components[name] for name in weights})
    gross_nav = simulate_gross(prices, weights)
    net_nav, costs = simulate_net(candidate, prices, weights)
    return {"gross_nav": gross_nav, "net_nav": net_nav, "costs": costs}


def align_prices(curves: dict[str, pd.Series]) -> pd.DataFrame:
    calendar = pd.DatetimeIndex(sorted(set().union(*(set(curve.index) for curve in curves.values()))))
    calendar = calendar[(calendar >= START_DATE) & (calendar <= END_DATE)]
    aligned = {}
    for name, curve in curves.items():
        series = curve.reindex(calendar).ffill()
        if series.isna().any():
            first_bad = series.loc[series.isna()].index.min().date()
            raise ValueError(f"{name} has no NAV on or before {first_bad}")
        aligned[name] = series / series.iloc[0]
    return pd.DataFrame(aligned, index=calendar)


def simulate_gross(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    returns = prices.pct_change().fillna(0.0)
    values = []
    sleeve_values: dict[str, float] | None = None
    last_quarter = None
    for date, quarter in zip(returns.index, returns.index.to_period("Q"), strict=True):
        if sleeve_values is None:
            sleeve_values = weights.copy()
        elif quarter != last_quarter:
            nav = sum(sleeve_values.values())
            sleeve_values = {component: nav * weight for component, weight in weights.items()}
        for component in weights:
            sleeve_values[component] *= 1.0 + float(returns.loc[date, component])
        values.append(sum(sleeve_values.values()))
        last_quarter = quarter
    return pd.Series(values, index=returns.index, name="gross")


def simulate_net(candidate: str, prices: pd.DataFrame, weights: dict[str, float]) -> tuple[pd.Series, pd.DataFrame]:
    shares = {component: 0.0 for component in weights}
    lots = {component: [] for component in weights}
    cash = 1.0
    annual_net_realized: dict[int, float] = {}
    annual_taxable_paid: dict[int, float] = {}
    cost_rows = []
    values = []
    last_quarter = None
    for date, quarter in zip(prices.index, prices.index.to_period("Q"), strict=True):
        should_rebalance = last_quarter is None or quarter != last_quarter
        pre_nav = cash + sum(shares[c] * float(prices.loc[date, c]) for c in weights)
        if should_rebalance:
            costs = rebalance(candidate, date, pre_nav, prices.loc[date], weights, shares, lots, annual_net_realized, annual_taxable_paid)
            cash += costs["cash_delta"]
            cost_rows.append(costs["row"])
        if is_quarter_end(date, prices.index):
            component_values = {c: shares[c] * float(prices.loc[date, c]) for c in weights}
            dividend_cost = sum(
                component_values[c] * DIVIDEND_YIELDS.get(c, 0.0) / 4.0 * DIVIDEND_WITHHOLDING_RATE
                for c in weights
                if c in TAXABLE_COMPONENTS
            )
            cash -= dividend_cost
            if dividend_cost:
                cost_rows.append(
                    {
                        "candidate": candidate,
                        "date": date.date().isoformat(),
                        "event": "dividend_withholding",
                        "buy_amount": 0.0,
                        "sell_amount": 0.0,
                        "commission_cost": 0.0,
                        "capital_gains_tax": 0.0,
                        "fx_spread_cost": 0.0,
                        "dividend_withholding": dividend_cost,
                        "total_cost": dividend_cost,
                        "realized_gain": 0.0,
                    }
                )
        values.append(cash + sum(shares[c] * float(prices.loc[date, c]) for c in weights))
        last_quarter = quarter
    return pd.Series(values, index=prices.index, name=candidate), pd.DataFrame(cost_rows)


def rebalance(
    candidate: str,
    date: pd.Timestamp,
    pre_nav: float,
    price_row: pd.Series,
    weights: dict[str, float],
    shares: dict[str, float],
    lots: dict[str, list[Lot]],
    annual_net_realized: dict[int, float],
    annual_taxable_paid: dict[int, float],
) -> dict[str, object]:
    current_values = {component: shares[component] * float(price_row[component]) for component in weights}
    target_values = {component: pre_nav * weight for component, weight in weights.items()}
    trades = {component: target_values[component] - current_values[component] for component in weights}
    buy_amount = 0.0
    sell_amount = 0.0
    realized = 0.0
    tax = 0.0
    for component, trade_value in trades.items():
        price = float(price_row[component])
        if trade_value < -1e-15:
            value = min(-trade_value, shares[component] * price)
            sold_shares, gain = sell_hifo(lots[component], value, price)
            shares[component] -= sold_shares
            sell_amount += value
            if component in TAXABLE_COMPONENTS:
                realized += gain
        elif trade_value > 1e-15:
            buy_shares = trade_value / price
            shares[component] += buy_shares
            lots[component].append(Lot(shares=buy_shares, cost_basis=price))
            buy_amount += trade_value
    if realized:
        tax = tax_due(date.year, realized, annual_net_realized, annual_taxable_paid)
    taxable_trade = sum(abs(trades[c]) for c in weights if c in TAXABLE_COMPONENTS)
    commission = (buy_amount + sell_amount) * COMMISSION_RATE
    fx_cost = taxable_trade * FX_SPREAD_RATE
    total_cost = commission + tax + fx_cost
    return {
        "cash_delta": sell_amount - buy_amount - total_cost,
        "row": {
            "candidate": candidate,
            "date": date.date().isoformat(),
            "event": "rebalance",
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "commission_cost": commission,
            "capital_gains_tax": tax,
            "fx_spread_cost": fx_cost,
            "dividend_withholding": 0.0,
            "total_cost": total_cost,
            "realized_gain": realized,
        },
    }


def is_quarter_end(date: pd.Timestamp, index: pd.DatetimeIndex) -> bool:
    loc = index.get_loc(date)
    if not isinstance(loc, int):
        raise ValueError("duplicate dates are not supported")
    return loc == len(index) - 1 or index[loc + 1].to_period("Q") != date.to_period("Q")


def row_metrics(
    candidate: str,
    method: str,
    sleeve: str,
    q_weight: float,
    result: dict[str, object],
    method_name: str = "",
    sleeve_type: str = "",
    weights: dict[str, float] | None = None,
) -> dict[str, object]:
    gross_nav = result["gross_nav"]
    net_nav = result["net_nav"]
    costs = result["costs"]
    assert isinstance(gross_nav, pd.Series)
    assert isinstance(net_nav, pd.Series)
    assert isinstance(costs, pd.DataFrame)
    gross = metrics(gross_nav)
    net = metrics(net_nav)
    totals = costs[["commission_cost", "capital_gains_tax", "fx_spread_cost", "dividend_withholding", "total_cost"]].sum()
    return {
        "candidate": candidate,
        "method": method,
        "method_name": method_name,
        "sleeve": sleeve,
        "sleeve_type": sleeve_type,
        "q_weight": q_weight,
        "weights": weights_to_text(weights or BASELINE_WEIGHTS),
        "start_date": net_nav.index[0].date().isoformat(),
        "end_date": net_nav.index[-1].date().isoformat(),
        "gross_cagr": gross["cagr"],
        "net_cagr": net["cagr"],
        "net_sharpe": net["sharpe"],
        "net_mdd": net["mdd"],
        "gross_sharpe": gross["sharpe"],
        "gross_mdd": gross["mdd"],
        "cost_drag_cagr": net["cagr"] - gross["cagr"],
        "total_cost": float(totals["total_cost"]),
        "commission_cost": float(totals["commission_cost"]),
        "capital_gains_tax": float(totals["capital_gains_tax"]),
        "fx_spread_cost": float(totals["fx_spread_cost"]),
        "dividend_withholding": float(totals["dividend_withholding"]),
    }


def build_delta_table(combination: pd.DataFrame, baseline: dict[str, object]) -> pd.DataFrame:
    cols = [
        "candidate",
        "method",
        "sleeve",
        "sleeve_type",
        "q_weight",
        "net_cagr",
        "net_sharpe",
        "net_mdd",
        "delta_net_cagr_vs_baseline",
        "delta_net_sharpe_vs_baseline",
        "delta_net_mdd_vs_baseline",
    ]
    out = combination[cols].copy()
    out.insert(5, "baseline_net_cagr", baseline["net_cagr"])
    out.insert(7, "baseline_net_sharpe", baseline["net_sharpe"])
    out.insert(9, "baseline_net_mdd", baseline["net_mdd"])
    return out


def build_stress_windows(
    navs: dict[str, pd.Series],
    candidates: list[dict[str, object]],
    components: dict[str, pd.Series],
) -> pd.DataFrame:
    candidate_meta = {row["candidate"]: row for row in candidates}
    rows = []
    for candidate, nav in navs.items():
        meta = candidate_meta.get(candidate, {"method": "baseline", "sleeve": "baseline", "sleeve_type": "baseline", "q_weight": 0.0, "weights": BASELINE_WEIGHTS})
        for stress, (start, end) in STRESS_WINDOWS.items():
            if start >= START_DATE:
                value, mdd = stress_metrics(nav, start, end)
                measurement = "exact_net_2010_2026"
            else:
                value, mdd = proxy_long_history_stress(meta["weights"], components, start, end)
                measurement = "proxy_rescaled_missing_h001_sleeve_as_spy"
            base_value, base_mdd = (
                stress_metrics(navs["P08_IEF30_BASELINE"], start, end)
                if start >= START_DATE
                else proxy_long_history_stress(BASELINE_WEIGHTS, components, start, end)
            )
            rows.append(
                {
                    "candidate": candidate,
                    "method": meta["method"],
                    "sleeve": meta["sleeve"],
                    "sleeve_type": meta["sleeve_type"],
                    "q_weight": meta["q_weight"],
                    "stress_window": stress,
                    "measurement_type": measurement,
                    "total_return": value,
                    "baseline_total_return": base_value,
                    "delta_return": value - base_value,
                    "delta_return_pp": (value - base_value) * 100.0,
                    "daily_max_drawdown": mdd,
                    "baseline_daily_max_drawdown": base_mdd,
                    "delta_mdd": mdd - base_mdd,
                    "delta_mdd_pp": (mdd - base_mdd) * 100.0,
                }
            )
    return pd.DataFrame(rows)


def stress_metrics(nav: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> tuple[float, float]:
    window = nav.loc[nav.index.to_series().between(start, end)]
    if window.empty:
        return float("nan"), float("nan")
    total = float(window.iloc[-1] / window.iloc[0] - 1.0)
    mdd = float((window / window.cummax() - 1.0).min())
    return total, mdd


def proxy_long_history_stress(weights_obj: object, components: dict[str, pd.Series], start: pd.Timestamp, end: pd.Timestamp) -> tuple[float, float]:
    weights = weights_obj if isinstance(weights_obj, dict) else BASELINE_WEIGHTS
    fx = load_usdkrw()
    curves = {
        "SPY": load_etf_krw_nav("SPY", fx, long=True),
        "QQQ": load_etf_krw_nav("QQQ", fx, long=True),
        "IEF": load_etf_krw_nav("IEF", fx, long=True),
    }
    proxy_weights = {}
    for component, weight in weights.items():
        if component == "H001":
            continue
        if component in curves:
            proxy_weights[component] = proxy_weights.get(component, 0.0) + weight
        else:
            proxy_weights["SPY"] = proxy_weights.get("SPY", 0.0) + weight
    total_weight = sum(proxy_weights.values())
    proxy_weights = {component: weight / total_weight for component, weight in proxy_weights.items()}
    prices = align_long_prices({component: curves[component] for component in proxy_weights}, start, end)
    gross = simulate_gross(prices, proxy_weights)
    return stress_metrics(gross, start, end)


def align_long_prices(curves: dict[str, pd.Series], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    calendar = pd.DatetimeIndex(sorted(set().union(*(set(curve.index) for curve in curves.values()))))
    calendar = calendar[(calendar >= start) & (calendar <= end)]
    aligned = {}
    for name, curve in curves.items():
        series = curve.reindex(calendar).ffill()
        series = series.loc[series.first_valid_index():]
        aligned[name] = series / series.iloc[0]
    return pd.DataFrame(aligned).dropna()


def weights_to_text(weights: dict[str, float]) -> str:
    return ";".join(f"{k}:{v:.2f}" for k, v in sorted(weights.items()))


def write_config(path: Path, candidates: list[dict[str, object]]) -> None:
    lines = [
        "experiment: Q008_portfolio_combination",
        "baseline: P08_IEF30",
        "baseline_weights:",
        "  SPY: 0.29",
        "  QQQ: 0.21",
        "  H001: 0.20",
        "  IEF: 0.30",
        "cost_framework: T-family Scenario B / Korean resident V1",
        "candidate_count: 30",
        "candidates:",
    ]
    for row in candidates:
        lines.extend(
            [
                f"  - candidate: {row['candidate']}",
                f"    method: {row['method']}",
                f"    sleeve: {row['sleeve']}",
                f"    sleeve_type: {row['sleeve_type']}",
                f"    q_weight: {row['q_weight']}",
                f"    weights: {weights_to_text(row['weights'])}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def n_family_reference() -> pd.DataFrame:
    rows = []
    for label, path in {"N001-B": N001_DIR / "delta_vs_baseline.csv", "N002-B": N002_DIR / "delta_vs_baseline.csv"}.items():
        if not path.exists():
            continue
        data = pd.read_csv(path)
        sub = data.loc[data["variant"].eq(label)].copy()
        rows.append(
            {
                "variant": label,
                "mean_delta_return_pp": float(sub["delta_return_pp"].mean()) if not sub.empty else np.nan,
                "mean_delta_mdd_pp": float(sub["delta_mdd_pp"].mean()) if not sub.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def write_report(path: Path, baseline: dict[str, object], combination: pd.DataFrame, stress: pd.DataFrame, top: pd.DataFrame) -> None:
    method_summary = (
        combination.groupby("method", sort=False)
        .agg(
            best_net_sharpe=("net_sharpe", "max"),
            mean_delta_cagr=("delta_net_cagr_vs_baseline", "mean"),
            mean_delta_sharpe=("delta_net_sharpe_vs_baseline", "mean"),
            mean_delta_mdd=("delta_net_mdd_vs_baseline", "mean"),
        )
        .reset_index()
    )
    sleeve_summary = (
        combination.groupby(["sleeve_type", "sleeve"], sort=False)
        .agg(best_net_sharpe=("net_sharpe", "max"), best_delta_cagr=("delta_net_cagr_vs_baseline", "max"))
        .reset_index()
        .sort_values(["best_net_sharpe", "best_delta_cagr"], ascending=[False, False])
    )
    n_ref = n_family_reference()
    best = top.iloc[0]
    production_etf = combination.loc[combination["sleeve_type"].eq("etf_proxy")].sort_values(
        ["net_sharpe", "net_mdd", "net_cagr", "candidate"],
        ascending=[False, False, False, True],
    )
    best_etf = production_etf.iloc[0] if not production_etf.empty else best
    verdict = (
        "ETF sleeve production 후보 추가 보류"
        if float(best_etf["delta_net_sharpe_vs_baseline"]) <= 0.0
        else "ETF sleeve production 후보 추가 검토 가능"
    )
    lines = [
        "# Q008 P08_IEF30 + ETF Proxy Combination",
        "",
        "Status: GENERATED BY `src.audit.q008_portfolio_combination`",
        "",
        "## Baseline",
        "",
        f"- P08_IEF30 net CAGR: {baseline['net_cagr']:.4f}",
        f"- P08_IEF30 net Sharpe: {baseline['net_sharpe']:.4f}",
        f"- P08_IEF30 net MDD: {baseline['net_mdd']:.4f}",
        "",
        "## Best Candidate Ranking (Sharpe 우선)",
        "",
        table_for_report(
            top,
            [
                "candidate",
                "method",
                "sleeve",
                "sleeve_type",
                "q_weight",
                "net_cagr",
                "net_sharpe",
                "net_mdd",
                "delta_net_cagr_vs_baseline",
                "delta_net_sharpe_vs_baseline",
                "delta_net_mdd_vs_baseline",
            ],
        ),
        "",
        "## Method 비교",
        "",
        table_for_report(method_summary, ["method", "best_net_sharpe", "mean_delta_cagr", "mean_delta_sharpe", "mean_delta_mdd"]),
        "",
        "## ETF Proxy vs Direct Q",
        "",
        table_for_report(sleeve_summary, ["sleeve_type", "sleeve", "best_net_sharpe", "best_delta_cagr"]),
        "",
        "## N-family Defensive Shadow 비교",
        "",
        table_for_report(n_ref, ["variant", "mean_delta_return_pp", "mean_delta_mdd_pp"]) if not n_ref.empty else "N001-B / N002-B reference not found.",
        "",
        "## Stress Window Notes",
        "",
        "- COVID와 2022는 Q008 net NAV에서 직접 측정했다.",
        "- Dot-com/GFC는 2010-2026 NAV 범위 밖이므로 H001 제외, Q/sleeve는 SPY proxy로 rescale한 long-history proxy 진단이다.",
        "",
        "## Verdict",
        "",
        f"- 전체 Sharpe 1위는 `{best['candidate']}`이다.",
        f"- ETF proxy 중 Sharpe 1위는 `{best_etf['candidate']}`이다.",
        f"- 결론: {verdict}.",
        "- Direct Q002/Q006은 survivorship bias 때문에 production X, comparison diagnostic only다.",
        "- N002-B/N001-B 같은 defensive shadow는 stress 목적의 별도 후보군이며, Q008 ETF sleeve가 Sharpe를 개선하더라도 stress 개선은 `stress_windows.csv`와 함께 별도 판단해야 한다.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_q_family_final_summary(path: Path, combination: pd.DataFrame, top: pd.DataFrame) -> None:
    etf_top = combination.loc[combination["sleeve_type"].eq("etf_proxy")].sort_values(
        ["net_sharpe", "net_mdd", "net_cagr", "candidate"],
        ascending=[False, False, False, True],
    ).head(10)
    direct_top = top.loc[top["sleeve_type"].eq("direct_q_diagnostic")]
    lines = [
        "# Q-family Final Summary",
        "",
        "Status: GENERATED BY `src.audit.q008_portfolio_combination`",
        "",
        "## Q000-Q008 결과 요약",
        "",
        "- Q000-Q001: US fundamental data와 universe construction은 research diagnostic 기반을 제공했다.",
        "- Q002-Q006: direct Q-family factor sleeves는 결과 비교에는 유용하지만 survivor-universe bias 때문에 production 후보가 아니다.",
        "- Q006.5/Q006.6: bias benchmark와 factor ETF proxy benchmark는 direct Q 경로보다 ETF proxy 경로가 실전 검토에 더 적합하다는 감사 결론을 뒷받침한다.",
        "- Q007: T-family 비용 sanity를 direct Q와 ETF proxy에 적용했다.",
        "- Q008: P08_IEF30에 사전 등록된 30개 sleeve 결합을 적용했다.",
        "",
        "## ETF Proxy Path 의미",
        "",
        "- SCHD/COWZ/MTUM은 direct Q의 survivorship-bias 문제를 피하는 production 검토 경로다.",
        "- Missing sleeve history는 SPY proxy로 처리했으므로, 초기 구간 alpha claim은 금지한다.",
        "",
        "## Production Candidate Ranking",
        "",
        table_for_report(
            etf_top,
            ["candidate", "method", "sleeve", "q_weight", "net_cagr", "net_sharpe", "net_mdd", "delta_net_sharpe_vs_baseline"],
        )
        if not etf_top.empty
        else "ETF proxy top candidate 없음.",
        "",
        "## Direct Q-family Diagnostic",
        "",
        table_for_report(
            direct_top,
            ["candidate", "method", "sleeve", "q_weight", "net_cagr", "net_sharpe", "net_mdd", "delta_net_sharpe_vs_baseline"],
        )
        if not direct_top.empty
        else "Direct Q top diagnostic 없음.",
        "",
        "## Paper Tracking 가치",
        "",
        "- ETF proxy 후보는 live/paper tracking에서 세금 drag, 배당 원천징수, 분기 리밸런싱 turnover가 실제 계좌와 맞는지 확인할 가치가 있다.",
        "- Direct Q는 production 후보가 아니라 factor research와 ETF proxy 선택의 참고 자료로만 유지한다.",
        "",
        "## 다음 Family 권고",
        "",
        "- S-family: 단기 한국 주식 sleeve의 timing-safe production 후보 탐색.",
        "- R-family: 한국 자사주/주주환원 event sleeve 탐색.",
        "- N-family: defensive shadow 후보는 stress 목적의 비교축으로 유지.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
