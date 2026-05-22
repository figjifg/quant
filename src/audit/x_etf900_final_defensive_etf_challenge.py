from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit import x_etf001_time_series_momentum_scan as base


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "x_lab/x_etf/x_etf900_results"

PRIMARY_UNIVERSE = ["SPY", "QQQ", "IWM", "IEF", "TLT", "SHY", "GLD", "UUP", "DBC", "VWO", "EWY", "EWJ", "EWZ"]
RISK_ASSETS = ["SPY", "QQQ", "IWM", "VWO", "EWY", "EWJ", "EWZ"]
DEFENSIVE_ASSETS_A = ["IEF", "TLT", "SHY", "GLD", "UUP"]
DEFENSIVE_ASSETS_B = ["IEF", "SHY", "GLD", "UUP", "DBC"]
SIGNALS = {
    "ret_6m": {"lookback": 126, "skip": 0},
    "ret_12m_skip_1m": {"lookback": 252, "skip": 21},
}
REBALANCE = ["monthly", "quarterly"]
SUBPERIODS = base.SUBPERIODS
STRESS_WINDOWS = base.STRESS_WINDOWS
TURNOVER_COST_RATE = base.TURNOVER_COST_RATE
RANDOM_TRIALS = base.RANDOM_TRIALS
RANDOM_SEED = base.RANDOM_SEED


@dataclass(frozen=True)
class Variant:
    variant_id: str
    module: str
    signal: str
    rebalance: str
    portfolio: str
    method: str = ""
    lookback: int = 0


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    variants = build_variants()
    prices = base.load_krw_prices(PRIMARY_UNIVERSE).dropna()
    evaluation_start = base.first_signal_after_lookback(prices, "monthly", 252)

    p08_proxy_nav = base.simulate_static_portfolio(
        prices,
        {"SPY": 0.29, "QQQ": 0.21, "IEF": 0.50},
        evaluation_start,
        "quarterly",
        cost_rate=0.0,
    )
    p08_full_nav = base.load_p08_full_nav().loc[evaluation_start:]
    ew13_nav = base.simulate_static_portfolio(
        prices,
        {ticker: 1.0 / len(PRIMARY_UNIVERSE) for ticker in PRIMARY_UNIVERSE},
        evaluation_start,
        "quarterly",
        cost_rate=TURNOVER_COST_RATE,
    )
    n001b_nav = load_external_nav("reports/experiments/N001_gold_sleeve/daily_nav.csv", "N001-B").loc[evaluation_start:]
    n002b_nav = load_external_nav("reports/experiments/N002_cash_shy_sleeve/daily_nav.csv", "N002-B").loc[evaluation_start:]
    benchmarks = {
        "p08_proxy": base.metrics(p08_proxy_nav),
        "p08_ief30_full": base.metrics(p08_full_nav),
        "ew13_after_cost": base.metrics(ew13_nav),
        "n001_b": base.metrics(n001b_nav),
        "n002_b": base.metrics(n002b_nav),
    }

    write_config(variants, prices, evaluation_start, benchmarks)

    variant_rows = []
    subperiod_rows = []
    stress_rows = []
    random_rows = []
    turnover_rows = []
    contribution_rows = []
    pass_rows = []
    nav_by_variant = {}
    random_cache = {}

    for variant in variants:
        targets = build_target_weights(prices, variant, evaluation_start)
        layer_results = {
            "gross": base.simulate_targets(prices, targets, cost_rate=0.0, tax=False),
            "after_cost": base.simulate_targets(prices, targets, cost_rate=TURNOVER_COST_RATE, tax=False),
            "after_tax": base.simulate_targets(prices, targets, cost_rate=TURNOVER_COST_RATE, tax=True),
        }
        nav_by_variant[variant.variant_id] = layer_results["after_cost"]["nav"]
        exposure = base.exposure_summary(prices, targets, layer_results["after_cost"]["daily_contrib"])
        random = base.random_control(prices, variant, targets, evaluation_start, random_cache)
        pass_eval = evaluate_pass_gate(
            variant,
            layer_results,
            random,
            targets,
            p08_proxy_nav,
            p08_full_nav,
            ew13_nav,
        )

        for layer, result in layer_results.items():
            metric = base.metrics(result["nav"])
            row = {
                "variant_id": variant.variant_id,
                "module": variant.module,
                "signal": variant.signal,
                "rebalance": variant.rebalance,
                "portfolio": variant.portfolio,
                "method": variant.method,
                "lookback": variant.lookback,
                "cost_layer": layer,
                **metric,
                "total_turnover": result["total_turnover"],
                "annualized_turnover": base.annualized_turnover(result["turnover"], result["nav"]),
                "taxable_turnover": result["taxable_turnover"],
                "tax_paid_krw": result["tax_paid_krw"],
                "tax_drag_sharpe": metric["sharpe"] - base.metrics(layer_results["gross"]["nav"])["sharpe"] if metric["sharpe"] is not None else None,
                "top_asset": exposure["top_asset"],
                "top_asset_contribution": exposure["top_asset_contribution"],
                "qqq_exposure": exposure["qqq_exposure"],
                "qqq_contribution": exposure["qqq_contribution"],
                "p08_proxy_sharpe_diff": metric["sharpe"] - benchmarks["p08_proxy"]["sharpe"] if metric["sharpe"] is not None else None,
                "p08_proxy_mdd_diff": metric["max_drawdown"] - benchmarks["p08_proxy"]["max_drawdown"] if metric["max_drawdown"] is not None else None,
                "ew13_sharpe_diff": metric["sharpe"] - benchmarks["ew13_after_cost"]["sharpe"] if metric["sharpe"] is not None else None,
                "n001_b_sharpe_diff": metric["sharpe"] - benchmarks["n001_b"]["sharpe"] if metric["sharpe"] is not None else None,
                "n002_b_sharpe_diff": metric["sharpe"] - benchmarks["n002_b"]["sharpe"] if metric["sharpe"] is not None else None,
                "random_percentile": random["percentile"],
            }
            variant_rows.append(row)
            for period, (start, end) in SUBPERIODS.items():
                subperiod_rows.append(window_comparison_row(variant, layer, period, result["nav"], p08_proxy_nav, start, end))
            for window, (start, end) in STRESS_WINDOWS.items():
                stress_rows.append(window_comparison_row(variant, layer, window, result["nav"], p08_proxy_nav, start, end))

        random_rows.append({"variant_id": variant.variant_id, "module": variant.module, **random})
        turnover_rows.append(turnover_tax_drag_row(variant, layer_results))
        contribution_rows.append({"variant_id": variant.variant_id, "module": variant.module, **exposure})
        pass_rows.append(pass_eval)

    variant_metrics = pd.DataFrame(variant_rows)
    subperiod_breakdown = pd.DataFrame(subperiod_rows)
    stress = pd.DataFrame(stress_rows)
    random_control = pd.DataFrame(random_rows)
    turnover_tax_drag = pd.DataFrame(turnover_rows)
    pass_gate = pd.DataFrame(pass_rows)
    combination = build_p08_combination_test(nav_by_variant, variant_metrics, p08_full_nav, p08_proxy_nav)

    variant_metrics.to_csv(OUTPUT_DIR / "variant_metrics.csv", index=False)
    variant_metrics.loc[variant_metrics["module"] == "A"].to_csv(OUTPUT_DIR / "module_a_dual_momentum.csv", index=False)
    variant_metrics.loc[variant_metrics["module"] == "B"].to_csv(OUTPUT_DIR / "module_b_defensive_rotation.csv", index=False)
    variant_metrics.loc[variant_metrics["module"] == "C"].to_csv(OUTPUT_DIR / "module_c_risk_budget.csv", index=False)
    subperiod_breakdown.to_csv(OUTPUT_DIR / "subperiod_breakdown.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    random_control.to_csv(OUTPUT_DIR / "random_control.csv", index=False)
    turnover_tax_drag.to_csv(OUTPUT_DIR / "turnover_tax_drag.csv", index=False)
    pass_gate.to_csv(OUTPUT_DIR / "pass_gate_evaluation.csv", index=False)
    combination.to_csv(OUTPUT_DIR / "p08_combination_test.csv", index=False)
    write_report(variant_metrics, pass_gate, combination, benchmarks, evaluation_start)


def build_variants() -> list[Variant]:
    variants: list[Variant] = []
    idx = 1
    for signal in SIGNALS:
        for rebalance in REBALANCE:
            for portfolio in ["risk_top2_def_top2", "risk_top3_def_top2"]:
                variants.append(Variant(f"XETF900_V{idx:02d}", "A", signal, rebalance, portfolio))
                idx += 1
    for signal in SIGNALS:
        for rebalance in REBALANCE:
            for portfolio in ["def_sleeve_top1", "def_sleeve_top2_ew"]:
                variants.append(Variant(f"XETF900_V{idx:02d}", "B", signal, rebalance, portfolio))
                idx += 1
    for method in ["inverse_vol", "erc"]:
        for lookback in [126, 252]:
            for rebalance in REBALANCE:
                variants.append(Variant(f"XETF900_V{idx:02d}", "C", "vol_budget", rebalance, "risk_budget", method, lookback))
                idx += 1
    if len(variants) != 24:
        raise AssertionError(f"Expected 24 variants, got {len(variants)}")
    return variants


def build_target_weights(prices: pd.DataFrame, variant: Variant, evaluation_start: pd.Timestamp) -> pd.DataFrame:
    if variant.module in {"A", "B"}:
        scores = momentum_scores(prices, variant.signal)
    else:
        scores = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    target = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for signal_date in base.rebalance_signal_dates(prices.index, variant.rebalance):
        if signal_date < evaluation_start:
            continue
        loc = prices.index.get_loc(signal_date)
        if loc + 1 >= len(prices.index):
            continue
        trade_date = prices.index[loc + 1]
        if variant.module == "A":
            weights = module_a_weights(scores.loc[signal_date], variant)
        elif variant.module == "B":
            weights = module_b_weights(scores.loc[signal_date], variant)
        elif variant.module == "C":
            weights = module_c_weights(prices.loc[:signal_date], variant)
        else:
            raise ValueError(f"Unsupported module: {variant.module}")
        target.loc[trade_date] = pd.Series(weights)
    return target


def momentum_scores(prices: pd.DataFrame, signal: str) -> pd.DataFrame:
    spec = SIGNALS[signal]
    lookback = spec["lookback"]
    skip = spec["skip"]
    if skip:
        return prices.shift(skip) / prices.shift(lookback) - 1.0
    return prices / prices.shift(lookback) - 1.0


def module_a_weights(scores: pd.Series, variant: Variant) -> dict[str, float]:
    weights = zero_weights()
    risk_scores = scores[RISK_ASSETS].dropna()
    def_scores = scores[DEFENSIVE_ASSETS_A].dropna()
    risk_on = (
        not risk_scores.empty
        and not def_scores.empty
        and risk_scores.median() > def_scores.median()
        and scores.get("SPY", np.nan) > 0.0
    )
    if risk_on:
        k = 2 if variant.portfolio == "risk_top2_def_top2" else 3
        selected = risk_scores.sort_values(ascending=False).head(k).index
    else:
        selected = def_scores.sort_values(ascending=False).head(2).index
        k = 2
    for ticker in selected:
        weights[ticker] = 1.0 / k
    return weights


def module_b_weights(scores: pd.Series, variant: Variant) -> dict[str, float]:
    weights = zero_weights()
    weights["SPY"] = 0.29
    weights["QQQ"] = 0.21
    k = 1 if variant.portfolio == "def_sleeve_top1" else 2
    selected = scores[DEFENSIVE_ASSETS_B].dropna().sort_values(ascending=False).head(k).index
    if len(selected) == 0:
        weights["SHY"] += 0.25
    else:
        for ticker in selected:
            weights[ticker] += 0.50 / len(selected)
    return weights


def module_c_weights(price_history: pd.DataFrame, variant: Variant) -> dict[str, float]:
    window = price_history[PRIMARY_UNIVERSE].dropna().tail(variant.lookback + 1)
    if len(window) < variant.lookback:
        weights = zero_weights()
        weights["SHY"] = 0.25
        return weights
    returns = window.pct_change().dropna()
    if variant.method == "inverse_vol":
        vol = returns.std().replace(0.0, np.nan).dropna()
        raw = 1.0 / vol
        weights = raw / raw.sum()
    elif variant.method == "erc":
        weights = erc_weights(returns.cov())
    else:
        raise ValueError(f"Unsupported method: {variant.method}")
    return capped_weight_dict(weights.reindex(PRIMARY_UNIVERSE).fillna(0.0))


def erc_weights(cov: pd.DataFrame) -> pd.Series:
    cov = cov.loc[PRIMARY_UNIVERSE, PRIMARY_UNIVERSE].fillna(0.0)
    diag = pd.Series(np.diag(cov), index=cov.index)
    valid = diag > 0.0
    if valid.sum() < 2:
        raw = pd.Series(0.0, index=PRIMARY_UNIVERSE)
        raw["SHY"] = 0.25
        return raw
    tickers = diag[valid].index
    matrix = cov.loc[tickers, tickers].to_numpy()
    weights = np.ones(len(tickers)) / len(tickers)
    target = 1.0 / len(tickers)
    for _ in range(500):
        marginal = matrix @ weights
        variance = float(weights @ marginal)
        if variance <= 0.0:
            break
        risk_contrib = weights * marginal / variance
        adjustment = np.divide(target, risk_contrib, out=np.ones_like(risk_contrib), where=risk_contrib > 1e-12)
        weights *= adjustment ** 0.25
        weights = np.maximum(weights, 0.0)
        total = weights.sum()
        if total <= 0.0:
            break
        weights /= total
        if np.max(np.abs(risk_contrib - target)) < 1e-6:
            break
    out = pd.Series(0.0, index=PRIMARY_UNIVERSE)
    out.loc[tickers] = weights
    if not np.isfinite(out).all() or out.sum() <= 0.0:
        vol = np.sqrt(diag[valid])
        inv = 1.0 / vol
        out.loc[inv.index] = inv / inv.sum()
    return out


def capped_weight_dict(weights: pd.Series, cap: float = 0.25) -> dict[str, float]:
    weights = weights.clip(lower=0.0)
    if weights.sum() <= 0.0:
        out = zero_weights()
        out["SHY"] = cap
        return out
    weights = weights / weights.sum()
    capped = pd.Series(0.0, index=weights.index)
    remaining = 1.0
    active = weights.copy()
    while not active.empty and remaining > 1e-12:
        scaled = active / active.sum() * remaining
        over = scaled > cap
        if not over.any():
            capped.loc[scaled.index] = scaled
            break
        capped.loc[scaled[over].index] = cap
        remaining -= float(cap * over.sum())
        active = active.loc[~over]
    return {ticker: float(capped.get(ticker, 0.0)) for ticker in PRIMARY_UNIVERSE}


def zero_weights() -> dict[str, float]:
    return {ticker: 0.0 for ticker in PRIMARY_UNIVERSE}


def load_external_nav(relative_path: str, column: str) -> pd.Series:
    data = pd.read_csv(ROOT / relative_path, parse_dates=["date"])
    return base.normalize(data.sort_values("date").drop_duplicates("date").set_index("date")[column])


def window_comparison_row(
    variant: Variant,
    layer: str,
    window: str,
    nav: pd.Series,
    benchmark: pd.Series,
    start: str,
    end: str,
) -> dict:
    strat = base.metrics(base.normalize(nav.loc[start:end].dropna()))
    bench = base.metrics(base.normalize(benchmark.loc[start:end].dropna()))
    return {
        "variant_id": variant.variant_id,
        "module": variant.module,
        "signal": variant.signal,
        "rebalance": variant.rebalance,
        "portfolio": variant.portfolio,
        "method": variant.method,
        "lookback": variant.lookback,
        "cost_layer": layer,
        "window": window,
        **{f"strategy_{key}": value for key, value in strat.items()},
        **{f"p08_proxy_{key}": value for key, value in bench.items()},
        "sharpe_diff": nullable_diff(strat["sharpe"], bench["sharpe"]),
        "mdd_diff": nullable_diff(strat["max_drawdown"], bench["max_drawdown"]),
        "return_diff": nullable_diff(strat["total_return"], bench["total_return"]),
    }


def turnover_tax_drag_row(variant: Variant, layer_results: dict) -> dict:
    gross = base.metrics(layer_results["gross"]["nav"])
    after_cost = base.metrics(layer_results["after_cost"]["nav"])
    after_tax = base.metrics(layer_results["after_tax"]["nav"])
    return {
        "variant_id": variant.variant_id,
        "module": variant.module,
        "annualized_turnover": base.annualized_turnover(layer_results["after_cost"]["turnover"], layer_results["after_cost"]["nav"]),
        "total_turnover": layer_results["after_cost"]["total_turnover"],
        "taxable_turnover": layer_results["after_tax"]["taxable_turnover"],
        "tax_paid_krw": layer_results["after_tax"]["tax_paid_krw"],
        "gross_sharpe": gross["sharpe"],
        "after_cost_sharpe": after_cost["sharpe"],
        "after_tax_sharpe": after_tax["sharpe"],
        "cost_sharpe_drag": nullable_diff(after_cost["sharpe"], gross["sharpe"]),
        "tax_sharpe_drag": nullable_diff(after_tax["sharpe"], after_cost["sharpe"]),
        "cost_cagr_drag": nullable_diff(after_cost["cagr"], gross["cagr"]),
        "tax_cagr_drag": nullable_diff(after_tax["cagr"], after_cost["cagr"]),
    }


def evaluate_pass_gate(
    variant: Variant,
    layer_results: dict,
    random: dict,
    targets: pd.DataFrame,
    p08_proxy_nav: pd.Series,
    p08_full_nav: pd.Series,
    ew13_nav: pd.Series,
) -> dict:
    after_cost = base.metrics(layer_results["after_cost"]["nav"])
    after_tax = base.metrics(layer_results["after_tax"]["nav"])
    p08 = base.metrics(p08_proxy_nav)
    year_2022 = window_comparison(layer_results["after_cost"]["nav"], p08_proxy_nav, "2022-01-01", "2022-12-31")
    subperiod_fail_count = 0
    for start, end in SUBPERIODS.values():
        comp = window_comparison(layer_results["after_cost"]["nav"], p08_proxy_nav, start, end)
        if comp["strategy_sharpe"] is None or comp["p08_sharpe"] is None or comp["strategy_sharpe"] < comp["p08_sharpe"]:
            subperiod_fail_count += 1
    ew13 = base.metrics(ew13_nav)
    annual_turnover = base.annualized_turnover(layer_results["after_cost"]["turnover"], layer_results["after_cost"]["nav"])
    mdd_improvement = after_cost["max_drawdown"] - p08["max_drawdown"]
    cagr_drag = p08["cagr"] - after_cost["cagr"]
    sharpe_edge = after_cost["sharpe"] - p08["sharpe"]
    tax_collapse = after_tax["sharpe"] is None or after_tax["sharpe"] < after_cost["sharpe"] - 0.10
    static_clone = static_defensive_clone(targets)
    ew_or_random_explains = after_cost["sharpe"] <= ew13["sharpe"] + 0.05 or random["percentile"] < 90.0

    close_criteria = {
        "no_sharpe_edge_vs_p08_plus_0_05": sharpe_edge < 0.05,
        "no_mdd_improvement_2pp": mdd_improvement < 0.02,
        "no_2022_stress_improvement": year_2022["strategy_total_return"] <= year_2022["p08_total_return"] and year_2022["strategy_mdd"] <= year_2022["p08_mdd"] + 0.01,
        "ew13_or_random_explains": ew_or_random_explains,
        "after_tax_collapses": tax_collapse,
        "turnover_higher_without_mdd_benefit": annual_turnover > 1.0 and mdd_improvement < 0.02,
        "static_defensive_clone": static_clone,
        "two_of_three_subperiods_fail": subperiod_fail_count >= 2,
    }
    diagnostic = (
        mdd_improvement >= 0.02
        and cagr_drag <= 0.015
        and sharpe_edge >= -0.05
        and year_2022["strategy_total_return"] > year_2022["p08_total_return"]
        and not ew_or_random_explains
        and annual_turnover <= 1.0
    )
    deep = (
        sharpe_edge >= 0.05
        or (mdd_improvement >= 0.03 and cagr_drag <= 0.01)
    ) and not tax_collapse and subperiod_fail_count < 2 and not static_clone

    verdict = "CLOSE"
    if deep:
        verdict = "DEEP_VALIDATION_CANDIDATE"
    elif diagnostic:
        verdict = "DIAGNOSTIC_PASS"
    return {
        "variant_id": variant.variant_id,
        "module": variant.module,
        "verdict": verdict,
        "diagnostic_pass": diagnostic,
        "deep_validation_candidate": deep,
        "close_all_criteria_met": all(close_criteria.values()),
        **close_criteria,
        "after_cost_sharpe": after_cost["sharpe"],
        "p08_proxy_sharpe": p08["sharpe"],
        "sharpe_edge": sharpe_edge,
        "after_cost_mdd": after_cost["max_drawdown"],
        "p08_proxy_mdd": p08["max_drawdown"],
        "mdd_improvement": mdd_improvement,
        "cagr_drag": cagr_drag,
        "after_tax_sharpe": after_tax["sharpe"],
        "random_percentile": random["percentile"],
        "annualized_turnover": annual_turnover,
        "subperiod_fail_count_vs_p08": subperiod_fail_count,
        "p08_full_mdd": base.metrics(p08_full_nav)["max_drawdown"],
    }


def window_comparison(nav: pd.Series, benchmark: pd.Series, start: str, end: str) -> dict:
    strat = base.metrics(base.normalize(nav.loc[start:end].dropna()))
    bench = base.metrics(base.normalize(benchmark.loc[start:end].dropna()))
    return {
        "strategy_total_return": strat["total_return"],
        "p08_total_return": bench["total_return"],
        "strategy_mdd": strat["max_drawdown"],
        "p08_mdd": bench["max_drawdown"],
        "strategy_sharpe": strat["sharpe"],
        "p08_sharpe": bench["sharpe"],
    }


def static_defensive_clone(targets: pd.DataFrame) -> bool:
    active = targets.replace(0.0, np.nan).ffill().fillna(0.0)
    if active.empty:
        return False
    avg = active.mean()
    defensive_weight = float(avg[["SHY", "IEF", "GLD"]].sum())
    return defensive_weight >= 0.90 and float(active.diff().abs().sum(axis=1).sum()) < 2.0


def build_p08_combination_test(
    nav_by_variant: dict[str, pd.Series],
    variant_metrics: pd.DataFrame,
    p08_full_nav: pd.Series,
    p08_proxy_nav: pd.Series,
) -> pd.DataFrame:
    best_id = (
        variant_metrics.loc[variant_metrics["cost_layer"] == "after_cost"]
        .sort_values(["sharpe", "max_drawdown"], ascending=[False, False])
        .iloc[0]["variant_id"]
    )
    x_nav = nav_by_variant[best_id]
    combined = combine_navs({"p08_ief30": p08_full_nav, best_id: x_nav}, {"p08_ief30": 0.90, best_id: 0.10})
    rows = []
    for name, nav in [("p08_proxy", p08_proxy_nav), ("p08_ief30_full", p08_full_nav), ("p08_ief30_90_xetf900_10", combined)]:
        metric = base.metrics(base.normalize(nav.dropna()))
        rows.append({"portfolio": name, "best_variant": best_id, **metric})
    p08 = rows[1]
    combo = rows[2]
    combo["mdd_improvement_vs_p08_ief30"] = combo["max_drawdown"] - p08["max_drawdown"]
    combo["cagr_drag_vs_p08_ief30"] = p08["cagr"] - combo["cagr"]
    combo["deep_gate_combo_candidate"] = combo["mdd_improvement_vs_p08_ief30"] >= 0.02 and combo["cagr_drag_vs_p08_ief30"] <= 0.01
    return pd.DataFrame(rows)


def combine_navs(nav_by_name: dict[str, pd.Series], weights: dict[str, float]) -> pd.Series:
    aligned = pd.concat(nav_by_name, axis=1).dropna()
    returns = aligned.pct_change().fillna(0.0)
    combined_return = sum(returns[name] * weight for name, weight in weights.items())
    return (1.0 + combined_return).cumprod()


def nullable_diff(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return float(left - right)


def write_config(variants: list[Variant], prices: pd.DataFrame, evaluation_start: pd.Timestamp, benchmarks: dict) -> None:
    lines = [
        "experiment: X-ETF900",
        "status: pre_registered_final_defensive_etf_challenge",
        "currency: KRW_total_return_primary",
        f"evaluation_start: {evaluation_start.date().isoformat()}",
        f"evaluation_end: {prices.index.max().date().isoformat()}",
        "variant_count: 24",
        "cost_layers:",
        "  gross: no_cost_no_tax",
        "  after_cost: round_trip_30bps_on_turnover",
        "  after_tax: hifo_22pct_annual_2_5m_exemption",
        "random_control:",
        f"  trials: {RANDOM_TRIALS}",
        f"  seed: {RANDOM_SEED}",
        "benchmarks:",
        f"  p08_proxy_sharpe: {benchmarks['p08_proxy']['sharpe']}",
        f"  p08_ief30_full_sharpe: {benchmarks['p08_ief30_full']['sharpe']}",
        f"  ew13_after_cost_sharpe: {benchmarks['ew13_after_cost']['sharpe']}",
        f"  n001_b_sharpe: {benchmarks['n001_b']['sharpe']}",
        f"  n002_b_sharpe: {benchmarks['n002_b']['sharpe']}",
        "variants:",
    ]
    for variant in variants:
        lines.extend(
            [
                f"  - variant_id: {variant.variant_id}",
                f"    module: {variant.module}",
                f"    signal: {variant.signal}",
                f"    rebalance: {variant.rebalance}",
                f"    portfolio: {variant.portfolio}",
                f"    method: {variant.method}",
                f"    lookback: {variant.lookback}",
            ]
        )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(
    variant_metrics: pd.DataFrame,
    pass_gate: pd.DataFrame,
    combination: pd.DataFrame,
    benchmarks: dict,
    evaluation_start: pd.Timestamp,
) -> None:
    after_cost = variant_metrics.loc[variant_metrics["cost_layer"] == "after_cost"]
    after_tax = variant_metrics.loc[variant_metrics["cost_layer"] == "after_tax"]
    best_cost = after_cost.sort_values(["sharpe", "max_drawdown"], ascending=[False, False]).iloc[0]
    best_tax = after_tax.sort_values(["sharpe", "max_drawdown"], ascending=[False, False]).iloc[0]
    verdict_counts = pass_gate["verdict"].value_counts().to_dict()
    track_fail = bool(pass_gate["close_all_criteria_met"].all())
    survivor_count = int((pass_gate["verdict"] != "CLOSE").sum())
    if track_fail:
        final_verdict = "FAIL_CLOSE_X_ETF_TRACK"
    elif survivor_count == 0:
        final_verdict = "ALL_VARIANTS_CLOSE_BUT_TRACK_FAIL_GATE_NOT_FULLY_TRIGGERED"
    else:
        final_verdict = "REVIEW_ROLE_BASED_SURVIVORS"
    combo = combination.loc[combination["portfolio"] == "p08_ief30_90_xetf900_10"].iloc[0]
    lines = [
        "# X-ETF900 Final Defensive ETF Challenge Report",
        "",
        "X-Lab 격리 산출물이다. D013, H001, P08_IEF30 strategy, engine.py, P08 paper tracking은 수정하지 않았다.",
        "",
        "## Verdict",
        "",
        f"- Final verdict: `{final_verdict}`",
        f"- Verdict distribution: `{json.dumps(verdict_counts, ensure_ascii=False)}`",
        f"- Non-close survivor count: `{survivor_count}`",
        f"- All close criteria met by every variant: `{track_fail}`",
        "",
        "## Benchmarks",
        "",
        f"- Evaluation start: `{evaluation_start.date().isoformat()}`",
        f"- P08 proxy Sharpe: `{benchmarks['p08_proxy']['sharpe']:.6f}` MDD `{benchmarks['p08_proxy']['max_drawdown']:.6f}`",
        f"- P08_IEF30 full Sharpe: `{benchmarks['p08_ief30_full']['sharpe']:.6f}` MDD `{benchmarks['p08_ief30_full']['max_drawdown']:.6f}`",
        f"- EW13 after-cost Sharpe: `{benchmarks['ew13_after_cost']['sharpe']:.6f}`",
        f"- N001-B Sharpe: `{benchmarks['n001_b']['sharpe']:.6f}`",
        f"- N002-B Sharpe: `{benchmarks['n002_b']['sharpe']:.6f}`",
        "",
        "## Best Variants",
        "",
        f"- Best after-cost: `{best_cost.variant_id}` module `{best_cost.module}` Sharpe `{best_cost.sharpe:.6f}` CAGR `{best_cost.cagr:.6f}` MDD `{best_cost.max_drawdown:.6f}` QQQ exposure `{best_cost.qqq_exposure:.6f}`",
        f"- Best after-tax: `{best_tax.variant_id}` module `{best_tax.module}` Sharpe `{best_tax.sharpe:.6f}` CAGR `{best_tax.cagr:.6f}` MDD `{best_tax.max_drawdown:.6f}`",
        "",
        "## P08 Combination Diagnostic",
        "",
        f"- 90% P08_IEF30 + 10% `{combo.best_variant}` CAGR `{combo.cagr:.6f}` MDD `{combo.max_drawdown:.6f}` Sharpe `{combo.sharpe:.6f}`",
        f"- MDD improvement vs P08_IEF30: `{combo.mdd_improvement_vs_p08_ief30:.6f}`",
        f"- CAGR drag vs P08_IEF30: `{combo.cagr_drag_vs_p08_ief30:.6f}`",
        f"- Deep combo gate candidate: `{combo.deep_gate_combo_candidate}`",
        "",
        "## Output Files",
        "",
        "- `config.yaml`",
        "- `variant_metrics.csv`",
        "- `module_a_dual_momentum.csv`",
        "- `module_b_defensive_rotation.csv`",
        "- `module_c_risk_budget.csv`",
        "- `subperiod_breakdown.csv`",
        "- `stress_windows.csv`",
        "- `random_control.csv`",
        "- `turnover_tax_drag.csv`",
        "- `pass_gate_evaluation.csv`",
        "- `p08_combination_test.csv`",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
