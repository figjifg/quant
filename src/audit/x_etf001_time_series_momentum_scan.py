from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_PATH = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
P08_FULL_PATH = ROOT / "reports/experiments/I001_6_daily_nav_metrics/daily_nav_by_portfolio.csv"
OUTPUT_DIR = ROOT / "x_lab/x_etf/x_etf001_results"

PRIMARY_UNIVERSE = ["SPY", "QQQ", "IWM", "IEF", "TLT", "SHY", "GLD", "UUP", "DBC", "VWO", "EWY", "EWJ", "EWZ"]
SECONDARY_UNIVERSE = [*PRIMARY_UNIVERSE, "MCHI"]
SIGNALS = {
    "ret_3m": {"lookback": 63, "skip": 0},
    "ret_6m": {"lookback": 126, "skip": 0},
    "ret_12m": {"lookback": 252, "skip": 0},
    "ret_12m_skip_1m": {"lookback": 252, "skip": 21},
}
PORTFOLIOS = ["top1_ew", "top2_ew", "top3_ew", "positive_top3_shy_fallback", "all_positive_ew_shy_fallback"]
REBALANCE = ["monthly", "quarterly"]
SUBPERIODS = {
    "2011_2014": ("2011-01-01", "2014-12-31"),
    "2015_2019": ("2015-01-01", "2019-12-31"),
    "2020_2026": ("2020-01-01", "2026-12-31"),
}
STRESS_WINDOWS = {
    "covid_2020_02_03": ("2020-02-01", "2020-03-31"),
    "year_2022": ("2022-01-01", "2022-12-31"),
}
INITIAL_CAPITAL_KRW = 100_000_000.0
TURNOVER_COST_RATE = 0.0030
CAPITAL_GAINS_TAX_RATE = 0.22
ANNUAL_EXEMPTION_KRW = 2_500_000.0
RANDOM_TRIALS = 1_000
RANDOM_SEED = 20260520
P08_FULL_CARRIER = "P08_SPY40_QQQ30_H00120_IEF10"


@dataclass(frozen=True)
class Variant:
    variant_id: str
    signal: str
    portfolio: str
    rebalance: str


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    variants = build_variants()
    prices = load_krw_prices(SECONDARY_UNIVERSE)
    primary_prices = prices[PRIMARY_UNIVERSE].dropna()
    secondary_prices = prices[SECONDARY_UNIVERSE].dropna()

    evaluation_start = first_signal_after_lookback(primary_prices, "monthly", 252)
    p08_proxy_nav = simulate_static_portfolio(
        primary_prices,
        {"SPY": 0.29, "QQQ": 0.21, "IEF": 0.50},
        evaluation_start,
        "quarterly",
        cost_rate=0.0,
    )
    p08_full_nav = load_p08_full_nav().loc[evaluation_start:]
    equal_weight_nav = simulate_static_portfolio(
        primary_prices,
        {ticker: 1.0 / len(PRIMARY_UNIVERSE) for ticker in PRIMARY_UNIVERSE},
        evaluation_start,
        "quarterly",
        cost_rate=TURNOVER_COST_RATE,
    )
    qqq_nav = normalize(primary_prices["QQQ"].loc[evaluation_start:])
    benchmark_metrics = {
        "p08_proxy": metrics(p08_proxy_nav),
        "p08_full": metrics(p08_full_nav),
        "equal_weight_13_after_cost": metrics(equal_weight_nav),
        "qqq": metrics(qqq_nav),
    }

    write_config(variants, evaluation_start, primary_prices, secondary_prices, benchmark_metrics)

    variant_rows = []
    subperiod_rows = []
    stress_rows = []
    random_rows = []
    exposure_rows = []
    ew_rows = []
    pass_rows = []
    secondary_rows = []
    nav_by_variant = {}
    random_cache = {}

    for variant in variants:
        target_weights = build_target_weights(primary_prices, variant, evaluation_start)
        layer_results = {
            "gross": simulate_targets(primary_prices, target_weights, cost_rate=0.0, tax=False),
            "after_cost": simulate_targets(primary_prices, target_weights, cost_rate=TURNOVER_COST_RATE, tax=False),
            "after_tax": simulate_targets(primary_prices, target_weights, cost_rate=TURNOVER_COST_RATE, tax=True),
        }
        nav_by_variant[variant.variant_id] = layer_results["after_cost"]["nav"]
        exposure = exposure_summary(primary_prices, target_weights, layer_results["after_cost"]["daily_contrib"])
        random = random_control(primary_prices, variant, target_weights, evaluation_start, random_cache)
        pass_eval = evaluate_pass_gate(
            variant,
            layer_results,
            random,
            benchmark_metrics,
            qqq_nav,
            p08_proxy_nav,
        )

        for layer, result in layer_results.items():
            row = {
                "variant_id": variant.variant_id,
                "signal": variant.signal,
                "portfolio": variant.portfolio,
                "rebalance": variant.rebalance,
                "cost_layer": layer,
                **metrics(result["nav"]),
                "total_turnover": result["total_turnover"],
                "annualized_turnover": annualized_turnover(result["turnover"], result["nav"]),
                "taxable_turnover": result["taxable_turnover"],
                "tax_paid_krw": result["tax_paid_krw"],
                "avg_asset_exposure": exposure["avg_asset_exposure"],
                "top_asset": exposure["top_asset"],
                "top_asset_contribution": exposure["top_asset_contribution"],
                "qqq_exposure": exposure["qqq_exposure"],
                "qqq_contribution": exposure["qqq_contribution"],
                "random_percentile": random["percentile"],
                "vs_equal_weight_sharpe": metrics(result["nav"])["sharpe"] - benchmark_metrics["equal_weight_13_after_cost"]["sharpe"],
            }
            variant_rows.append(row)
            for period, (start, end) in SUBPERIODS.items():
                subperiod_rows.append(
                    comparison_row(variant, layer, period, result["nav"], p08_proxy_nav, pd.Timestamp(start), pd.Timestamp(end))
                )
            for window, (start, end) in STRESS_WINDOWS.items():
                stress_rows.append(
                    comparison_row(variant, layer, window, result["nav"], p08_proxy_nav, pd.Timestamp(start), pd.Timestamp(end))
                )

        random_rows.append({"variant_id": variant.variant_id, **random})
        exposure_rows.append({"variant_id": variant.variant_id, **exposure, "qqq_return_correlation": qqq_correlation(layer_results["after_cost"]["nav"], qqq_nav)})
        ew_rows.append(equal_weight_comparison_row(variant, layer_results["after_cost"]["nav"], equal_weight_nav))
        pass_rows.append(pass_eval)

        secondary_targets = build_target_weights(secondary_prices, variant, first_signal_after_lookback(secondary_prices, variant.rebalance, 252))
        secondary_result = simulate_targets(secondary_prices, secondary_targets, cost_rate=TURNOVER_COST_RATE, tax=False)
        secondary_rows.append({"variant_id": variant.variant_id, **metrics(secondary_result["nav"])})

    variant_metrics = pd.DataFrame(variant_rows)
    subperiod_breakdown = pd.DataFrame(subperiod_rows)
    stress = pd.DataFrame(stress_rows)
    random_control_df = pd.DataFrame(random_rows)
    qqq_exposure = pd.DataFrame(exposure_rows)
    equal_weight_comparison = pd.DataFrame(ew_rows)
    pass_gate = pd.DataFrame(pass_rows)
    secondary = pd.DataFrame(secondary_rows)
    top_rankings = build_top_rankings(variant_metrics)

    variant_metrics.to_csv(OUTPUT_DIR / "variant_metrics.csv", index=False)
    top_rankings.to_csv(OUTPUT_DIR / "top_rankings.csv", index=False)
    subperiod_breakdown.to_csv(OUTPUT_DIR / "subperiod_breakdown.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    random_control_df.to_csv(OUTPUT_DIR / "random_control.csv", index=False)
    qqq_exposure.to_csv(OUTPUT_DIR / "qqq_exposure_test.csv", index=False)
    equal_weight_comparison.to_csv(OUTPUT_DIR / "equal_weight_comparison.csv", index=False)
    pass_gate.to_csv(OUTPUT_DIR / "pass_gate_evaluation.csv", index=False)
    secondary.to_csv(OUTPUT_DIR / "secondary_mchi_robustness.csv", index=False)
    write_report(variant_metrics, top_rankings, pass_gate, benchmark_metrics, evaluation_start)


def build_variants() -> list[Variant]:
    variants = []
    idx = 1
    for signal in SIGNALS:
        for portfolio in PORTFOLIOS:
            for rebalance in REBALANCE:
                variants.append(Variant(f"XETF001_V{idx:02d}", signal, portfolio, rebalance))
                idx += 1
    if len(variants) != 40:
        raise AssertionError(f"Expected 40 variants, got {len(variants)}")
    return variants


def load_krw_prices(universe: list[str]) -> pd.DataFrame:
    usdkrw = load_usdkrw()
    series = []
    for ticker in universe:
        data = pd.read_csv(etf_path(ticker), parse_dates=["Date"])
        data = data[["Date", "Close"]].rename(columns={"Date": "date", "Close": "close_usd"})
        data["close_usd"] = pd.to_numeric(data["close_usd"], errors="coerce")
        data = data.dropna().sort_values("date").drop_duplicates("date", keep="last")
        data = pd.merge_asof(data, usdkrw, on="date", direction="backward")
        series.append((data.set_index("date")["close_usd"] * data.set_index("date")["usdkrw"]).rename(ticker))
    return pd.concat(series, axis=1).sort_index()


def etf_path(ticker: str) -> Path:
    if ticker in {"VWO", "EWY", "EWJ", "EWZ", "MCHI"}:
        return ETF_DIR / f"yf_em_{ticker}.csv"
    long_path = ETF_DIR / f"yf_{ticker}_long.csv"
    if long_path.exists():
        return long_path
    return ETF_DIR / f"yf_{ticker}.csv"


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_PATH, parse_dates=["observation_date"], na_values=["."])
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return (
        data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})[["date", "usdkrw"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
    )


def first_signal_after_lookback(prices: pd.DataFrame, rebalance: str, lookback: int) -> pd.Timestamp:
    dates = rebalance_signal_dates(prices.index, rebalance)
    min_date = prices.index[lookback]
    eligible = [date for date in dates if date >= min_date]
    if not eligible:
        raise ValueError("No eligible rebalance date after lookback")
    return eligible[0]


def rebalance_signal_dates(index: pd.DatetimeIndex, rebalance: str) -> list[pd.Timestamp]:
    dates = pd.Series(index, index=index)
    if rebalance == "monthly":
        period_end = dates.groupby(index.to_period("M")).max().tolist()
    elif rebalance == "quarterly":
        period_end = dates.groupby(index.to_period("Q")).max().tolist()
    else:
        raise ValueError(f"Unsupported rebalance: {rebalance}")
    out = []
    locs = {date: pos for pos, date in enumerate(index)}
    for end in period_end:
        pos = locs[pd.Timestamp(end)] + 1
        if pos < len(index):
            out.append(index[pos])
    return out


def build_target_weights(prices: pd.DataFrame, variant: Variant, evaluation_start: pd.Timestamp) -> pd.DataFrame:
    signal_spec = SIGNALS[variant.signal]
    lookback = signal_spec["lookback"]
    skip = signal_spec["skip"]
    if skip:
        signal = prices.shift(skip) / prices.shift(lookback) - 1.0
    else:
        signal = prices / prices.shift(lookback) - 1.0
    target = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for signal_date in rebalance_signal_dates(prices.index, variant.rebalance):
        if signal_date < evaluation_start:
            continue
        loc = prices.index.get_loc(signal_date)
        if loc + 1 >= len(prices.index):
            continue
        trade_date = prices.index[loc + 1]
        scores = signal.loc[signal_date].dropna().sort_values(ascending=False)
        weights = choose_weights(scores, variant.portfolio, prices.columns)
        target.loc[trade_date] = pd.Series(weights)
    return target


def choose_weights(scores: pd.Series, portfolio: str, columns: pd.Index) -> dict[str, float]:
    weights = {ticker: 0.0 for ticker in columns}
    if portfolio.startswith("top") and portfolio.endswith("_ew"):
        k = int(portfolio[3])
        selected = scores.head(k).index.tolist()
        for ticker in selected:
            weights[ticker] = 1.0 / k
    elif portfolio == "positive_top3_shy_fallback":
        selected = scores.loc[scores > 0.0].head(3).index.tolist()
        slot = 1.0 / 3.0
        for ticker in selected:
            weights[ticker] += slot
        weights["SHY"] += slot * (3 - len(selected))
    elif portfolio == "all_positive_ew_shy_fallback":
        selected = scores.loc[scores > 0.0].index.tolist()
        if selected:
            for ticker in selected:
                weights[ticker] = 1.0 / len(selected)
        else:
            weights["SHY"] = 1.0
    else:
        raise ValueError(f"Unsupported portfolio: {portfolio}")
    total = sum(weights.values())
    if total > 1.0000001:
        raise AssertionError(f"Exposure exceeds 100%: {total}")
    return weights


def simulate_targets(prices: pd.DataFrame, target_weights: pd.DataFrame, *, cost_rate: float, tax: bool) -> dict:
    returns = prices.pct_change().fillna(0.0)
    start = first_nonzero_target_date(target_weights)
    idx = prices.index[prices.index >= start]
    target_weights = target_weights.loc[idx]
    returns = returns.loc[idx]
    prices = prices.loc[idx]
    weights = pd.Series(0.0, index=prices.columns)
    nav = []
    turnover = []
    taxable_turnover = 0.0
    tax_paid = 0.0
    lots = {ticker: [] for ticker in prices.columns}
    cash = INITIAL_CAPITAL_KRW
    shares = pd.Series(0.0, index=prices.columns)
    realized_by_year: dict[int, float] = {}
    paid_tax_years: set[int] = set()
    daily_contrib = []

    for pos, date in enumerate(idx):
        current_value = cash + float((shares * prices.loc[date]).sum())
        if current_value > 0.0:
            weights = (shares * prices.loc[date]) / current_value
        daily_contrib.append((weights * returns.loc[date]).rename(date))

        if target_weights.loc[date].sum() > 0.0:
            target = target_weights.loc[date]
            turn = float((target - weights).abs().sum())
            cost = turn * cost_rate
            taxable_turnover += float((target - weights).clip(upper=0).abs().sum())
            if tax:
                current_value = cash + float((shares * prices.loc[date]).sum())
                cash -= current_value * cost
                cash, paid = rebalance_lots(date, prices.loc[date], target, cash, shares, lots, realized_by_year, paid_tax_years)
                tax_paid += paid
                current_nav = cash + float((shares * prices.loc[date]).sum())
                weights = (shares * prices.loc[date]) / current_nav
            else:
                current_value = cash + float((shares * prices.loc[date]).sum())
                cash = current_value * max(0.0, 1.0 - cost)
                shares.loc[:] = 0.0
                for ticker, weight in target.items():
                    if weight > 0.0:
                        buy_value = cash * weight
                        shares[ticker] = buy_value / prices.loc[date, ticker]
                cash -= float((shares * prices.loc[date]).sum())
                current_nav = cash + float((shares * prices.loc[date]).sum())
                weights = (shares * prices.loc[date]) / current_nav if current_nav > 0 else weights
            turnover.append({"date": date, "turnover": turn})
        if tax and is_year_end_position(idx, pos) and date.year not in paid_tax_years:
            gain = realized_by_year.get(date.year, 0.0)
            taxable = max(0.0, gain - ANNUAL_EXEMPTION_KRW)
            paid = taxable * CAPITAL_GAINS_TAX_RATE
            cash -= paid
            tax_paid += paid
            paid_tax_years.add(date.year)
        value = cash + float((shares * prices.loc[date]).sum())
        nav.append({"date": date, "nav": value / INITIAL_CAPITAL_KRW})

    nav_series = pd.DataFrame(nav).set_index("date")["nav"]
    turnover_df = pd.DataFrame(turnover)
    return {
        "nav": nav_series,
        "turnover": turnover_df,
        "total_turnover": float(turnover_df["turnover"].sum()) if not turnover_df.empty else 0.0,
        "taxable_turnover": taxable_turnover,
        "tax_paid_krw": tax_paid,
        "daily_contrib": pd.DataFrame(daily_contrib),
    }


def rebalance_lots(date, price, target, cash, shares, lots, realized_by_year, paid_tax_years) -> tuple[float, float]:
    current_value = cash + float((shares * price).sum())
    current_values = shares * price
    target_values = target * current_value
    tax_paid = 0.0
    for ticker in price.index:
        delta_value = target_values[ticker] - current_values[ticker]
        if delta_value < -1e-9:
            sell_shares = abs(delta_value) / price[ticker]
            cash += sell_shares * price[ticker]
            shares[ticker] -= sell_shares
            gain = sell_hifo(lots[ticker], sell_shares, price[ticker])
            realized_by_year[date.year] = realized_by_year.get(date.year, 0.0) + gain
        elif delta_value > 1e-9:
            buy_shares = delta_value / price[ticker]
            cash -= buy_shares * price[ticker]
            shares[ticker] += buy_shares
            lots[ticker].append({"shares": buy_shares, "cost": price[ticker]})
    return cash, tax_paid


def sell_hifo(lots: list[dict], sell_shares: float, sale_price: float) -> float:
    lots.sort(key=lambda lot: lot["cost"], reverse=True)
    remaining = sell_shares
    gain = 0.0
    kept = []
    for lot in lots:
        if remaining <= 1e-10:
            kept.append(lot)
            continue
        used = min(lot["shares"], remaining)
        gain += used * (sale_price - lot["cost"])
        lot["shares"] -= used
        remaining -= used
        if lot["shares"] > 1e-10:
            kept.append(lot)
    lots[:] = kept
    return gain


def is_last_trading_day_of_year(date: pd.Timestamp) -> bool:
    return date.month == 12 and date.day >= 24


def is_year_end_position(index: pd.DatetimeIndex, pos: int) -> bool:
    return pos + 1 >= len(index) or index[pos + 1].year != index[pos].year


def first_nonzero_target_date(target_weights: pd.DataFrame) -> pd.Timestamp:
    rows = target_weights.sum(axis=1)
    nonzero = rows[rows > 0.0]
    if nonzero.empty:
        raise ValueError("No target weights available")
    return nonzero.index[0]


def simulate_static_portfolio(prices: pd.DataFrame, weights: dict[str, float], start: pd.Timestamp, rebalance: str, cost_rate: float) -> pd.Series:
    target = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for signal_date in rebalance_signal_dates(prices.index, rebalance):
        if signal_date < start:
            continue
        loc = prices.index.get_loc(signal_date)
        if loc + 1 < len(prices.index):
            target.loc[prices.index[loc + 1], list(weights)] = pd.Series(weights)
    return simulate_targets(prices, target, cost_rate=cost_rate, tax=False)["nav"]


def load_p08_full_nav() -> pd.Series:
    data = pd.read_csv(P08_FULL_PATH, parse_dates=["date"])
    p08 = data.loc[data["carrier"] == P08_FULL_CARRIER, ["date", "net_value"]].dropna()
    return normalize(p08.sort_values("date").drop_duplicates("date").set_index("date")["net_value"])


def random_control(prices: pd.DataFrame, variant: Variant, target_weights: pd.DataFrame, evaluation_start: pd.Timestamp, cache: dict) -> dict:
    rng = np.random.default_rng(RANDOM_SEED + int(variant.variant_id[-2:]))
    strategy_nav = simulate_targets(prices, target_weights, cost_rate=TURNOVER_COST_RATE, tax=False)["nav"]
    strategy_sharpe = metrics(strategy_nav)["sharpe"]
    trade_dates = target_weights.loc[target_weights.sum(axis=1) > 0.0].index
    random_start = trade_dates.min()
    returns = prices.pct_change().fillna(0.0).loc[random_start:].to_numpy()
    index = prices.loc[random_start:].index
    columns = prices.columns.to_numpy()
    trade_pos = [index.get_loc(date) for date in trade_dates if date in index]
    counts = [int((target_weights.loc[date] > 0.0).sum()) for date in trade_dates if date in index]
    cache_key = (tuple(trade_pos), tuple(counts), len(columns))
    if cache_key not in cache:
        cache[cache_key] = vectorized_random_sharpes(returns, len(columns), trade_pos, counts, rng)
    random_sharpes = cache[cache_key]
    arr = np.array(random_sharpes, dtype=float)
    percentile = float((arr <= strategy_sharpe).mean() * 100.0)
    return {
        "strategy_after_cost_sharpe": strategy_sharpe,
        "random_trials": RANDOM_TRIALS,
        "random_mean_sharpe": float(np.nanmean(arr)),
        "random_median_sharpe": float(np.nanmedian(arr)),
        "random_p90_sharpe": float(np.nanpercentile(arr, 90)),
        "random_p95_sharpe": float(np.nanpercentile(arr, 95)),
        "percentile": percentile,
    }


def vectorized_random_sharpes(
    returns: np.ndarray,
    asset_count: int,
    trade_pos: list[int],
    counts: list[int],
    rng: np.random.Generator,
) -> np.ndarray:
    weights = np.zeros((RANDOM_TRIALS, asset_count), dtype=float)
    nav = np.ones(RANDOM_TRIALS, dtype=float)
    daily_sum = np.zeros(RANDOM_TRIALS, dtype=float)
    daily_sumsq = np.zeros(RANDOM_TRIALS, dtype=float)
    trade_map = dict(zip(trade_pos, counts))
    trial_index = np.arange(RANDOM_TRIALS)
    for pos in range(len(returns)):
        daily_return = np.zeros(RANDOM_TRIALS, dtype=float)
        if pos > 0:
            growth = weights * (1.0 + returns[pos])
            gross = growth.sum(axis=1)
            daily_return += gross - 1.0
            nav *= gross
            valid = gross > 0.0
            weights[valid] = growth[valid] / gross[valid, None]
        if pos in trade_map:
            count = trade_map[pos]
            target = np.zeros_like(weights)
            picks = np.argsort(rng.random((RANDOM_TRIALS, asset_count)), axis=1)[:, :count]
            target[trial_index[:, None], picks] = 1.0 / count
            cost_return = -np.abs(target - weights).sum(axis=1) * TURNOVER_COST_RATE
            daily_return += cost_return
            nav *= 1.0 + cost_return
            weights = target
        daily_sum += daily_return
        daily_sumsq += daily_return * daily_return
    n = len(returns)
    mean = daily_sum / n
    variance = (daily_sumsq - n * mean * mean) / max(n - 1, 1)
    std = np.sqrt(np.maximum(variance, 0.0))
    out = np.full(RANDOM_TRIALS, np.nan)
    valid = std > 0.0
    out[valid] = mean[valid] / std[valid] * math.sqrt(252.0)
    return out


def fast_random_sharpe(
    returns: np.ndarray,
    asset_count: int,
    trade_pos: list[int],
    counts: list[int],
    rng: np.random.Generator,
) -> float | None:
    weights = np.zeros(asset_count)
    nav = np.ones(len(returns), dtype=float)
    trade_map = dict(zip(trade_pos, counts))
    for pos in range(len(returns)):
        if pos > 0:
            growth = weights * (1.0 + returns[pos])
            nav[pos] = nav[pos - 1] * growth.sum()
            weights = growth / growth.sum() if growth.sum() > 0 else weights
        if pos in trade_map:
            count = trade_map[pos]
            target = np.zeros(asset_count)
            selected = rng.choice(asset_count, size=count, replace=False)
            target[selected] = 1.0 / count
            turn = np.abs(target - weights).sum()
            nav[pos] *= max(0.0, 1.0 - turn * TURNOVER_COST_RATE)
            weights = target
        elif pos == 0:
            nav[pos] = 1.0
    if len(nav) < 2:
        return None
    daily = pd.Series(nav).pct_change().fillna(0.0)
    return sharpe(daily)


def exposure_summary(prices: pd.DataFrame, target_weights: pd.DataFrame, daily_contrib: pd.DataFrame) -> dict:
    active = target_weights.replace(0.0, np.nan).ffill().fillna(0.0)
    active = active.loc[daily_contrib.index.intersection(active.index)]
    avg = active.mean()
    contrib = daily_contrib.sum().sort_values(ascending=False)
    top_asset = contrib.index[0] if not contrib.empty else ""
    return {
        "avg_asset_exposure": float(avg[avg > 0].mean()) if (avg > 0).any() else 0.0,
        "top_asset": top_asset,
        "top_asset_contribution": float(contrib.iloc[0]) if not contrib.empty else 0.0,
        "qqq_exposure": float(avg.get("QQQ", 0.0)),
        "qqq_contribution": float(contrib.get("QQQ", 0.0)),
    }


def comparison_row(variant: Variant, layer: str, name: str, nav: pd.Series, benchmark: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    sliced = normalize(nav.loc[start:end].dropna())
    bench = normalize(benchmark.loc[start:end].dropna())
    strat_metrics = metrics(sliced) if not sliced.empty else empty_metrics()
    bench_metrics = metrics(bench) if not bench.empty else empty_metrics()
    return {
        "variant_id": variant.variant_id,
        "signal": variant.signal,
        "portfolio": variant.portfolio,
        "rebalance": variant.rebalance,
        "cost_layer": layer,
        "window": name,
        **{f"strategy_{key}": value for key, value in strat_metrics.items()},
        **{f"p08_proxy_{key}": value for key, value in bench_metrics.items()},
        "beats_p08_proxy_sharpe": strat_metrics["sharpe"] > bench_metrics["sharpe"] if strat_metrics["sharpe"] is not None and bench_metrics["sharpe"] is not None else False,
    }


def equal_weight_comparison_row(variant: Variant, nav: pd.Series, equal_weight_nav: pd.Series) -> dict:
    strat = metrics(nav)
    ew = metrics(equal_weight_nav)
    return {
        "variant_id": variant.variant_id,
        "strategy_after_cost_sharpe": strat["sharpe"],
        "equal_weight_13_sharpe": ew["sharpe"],
        "sharpe_diff": strat["sharpe"] - ew["sharpe"],
        "strategy_cagr": strat["cagr"],
        "equal_weight_13_cagr": ew["cagr"],
        "cagr_diff": strat["cagr"] - ew["cagr"],
    }


def evaluate_pass_gate(variant: Variant, layer_results: dict, random: dict, benchmarks: dict, qqq_nav: pd.Series, p08_proxy_nav: pd.Series) -> dict:
    after_cost = metrics(layer_results["after_cost"]["nav"])
    after_tax = metrics(layer_results["after_tax"]["nav"])
    p08 = benchmarks["p08_proxy"]
    p08_full = benchmarks["p08_full"]
    qqq = benchmarks["qqq"]
    subperiod_wins = 0
    for start, end in SUBPERIODS.values():
        s = metrics(normalize(layer_results["after_cost"]["nav"].loc[start:end].dropna()))
        b = metrics(normalize(p08_proxy_nav.loc[start:end].dropna()))
        if s["sharpe"] is not None and b["sharpe"] is not None and s["sharpe"] > b["sharpe"]:
            subperiod_wins += 1
    qqq_corr = qqq_correlation(layer_results["after_cost"]["nav"], qqq_nav)
    role_a = (
        after_cost["sharpe"] >= 1.15
        and after_cost["cagr"] >= p08["cagr"]
        and after_cost["max_drawdown"] >= -0.2343
        and random["percentile"] >= 95.0
    )
    role_b = (
        after_cost["max_drawdown"] >= p08["max_drawdown"] + 0.02
        and after_cost["cagr"] >= p08["cagr"] - 0.015
        and window_return(layer_results["after_cost"]["nav"], "2022-01-01", "2022-12-31") > window_return(p08_proxy_nav, "2022-01-01", "2022-12-31")
    )
    role_c = (
        after_cost["cagr"] >= 0.1643
        and after_cost["sharpe"] >= 1.017
        and after_cost["max_drawdown"] >= qqq["max_drawdown"] + 0.05
        and abs(qqq_corr) < 0.90
    )
    diagnostic = (
        after_cost["sharpe"] >= p08["sharpe"] + 0.10
        and (after_cost["cagr"] >= p08["cagr"] or role_b)
        and after_cost["max_drawdown"] >= qqq["max_drawdown"] + 0.05
        and random["percentile"] >= 90.0
        and subperiod_wins >= 2
        and abs(qqq_corr) < 0.90
    )
    close_reasons = []
    if after_cost["sharpe"] <= p08["sharpe"] + 0.05:
        close_reasons.append("after_cost_sharpe_not_above_p08_proxy_plus_0_05")
    if random["percentile"] < 90.0:
        close_reasons.append("not_different_from_random_topk")
    if subperiod_wins < 2:
        close_reasons.append("subperiod_wins_less_than_2")
    if abs(qqq_corr) >= 0.90:
        close_reasons.append("qqq_clone_risk")
    verdict = "CLOSE"
    if role_a or role_b or role_c:
        verdict = "DEEP_VALIDATION_CANDIDATE"
    elif diagnostic and not close_reasons:
        verdict = "DIAGNOSTIC_PASS"
    return {
        "variant_id": variant.variant_id,
        "signal": variant.signal,
        "portfolio": variant.portfolio,
        "rebalance": variant.rebalance,
        "verdict": verdict,
        "role_a_balanced": role_a,
        "role_b_defensive": role_b,
        "role_c_growth": role_c,
        "diagnostic_pass": diagnostic,
        "close_reasons": ";".join(close_reasons),
        "subperiod_wins_vs_p08_proxy": subperiod_wins,
        "qqq_return_correlation": qqq_corr,
        "after_cost_sharpe": after_cost["sharpe"],
        "after_tax_sharpe": after_tax["sharpe"],
        "p08_proxy_sharpe": p08["sharpe"],
        "p08_full_mdd": p08_full["max_drawdown"],
    }


def build_top_rankings(variant_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        ("top10_after_cost_sharpe", "after_cost", "sharpe", False),
        ("top10_after_tax_sharpe", "after_tax", "sharpe", False),
        ("top10_lowest_mdd", "after_cost", "max_drawdown", False),
    ]
    for ranking, layer, column, ascending in specs:
        data = variant_metrics.loc[variant_metrics["cost_layer"] == layer].sort_values(column, ascending=ascending).head(10)
        for rank, row in enumerate(data.itertuples(index=False), start=1):
            rows.append({"ranking": ranking, "rank": rank, "variant_id": row.variant_id, "cost_layer": layer, column: getattr(row, column)})
    for group_col in ["rebalance", "signal", "portfolio"]:
        grouped = variant_metrics.loc[variant_metrics["cost_layer"] == "after_cost"].groupby(group_col)["sharpe"].mean().reset_index()
        for row in grouped.itertuples(index=False):
            rows.append({"ranking": f"{group_col}_comparison", "rank": "", "variant_id": getattr(row, group_col), "cost_layer": "after_cost", "sharpe": row.sharpe})
    return pd.DataFrame(rows)


def metrics(nav: pd.Series) -> dict:
    nav = nav.dropna()
    if len(nav) < 2:
        return empty_metrics()
    returns = nav.pct_change().fillna(0.0)
    mdd = max_drawdown(nav)
    return {
        "start_date": nav.index.min().date().isoformat(),
        "end_date": nav.index.max().date().isoformat(),
        "trading_days": int(len(nav)),
        "total_return": float(nav.iloc[-1] / nav.iloc[0] - 1.0),
        "cagr": cagr(nav),
        "sharpe": sharpe(returns),
        "max_drawdown": mdd,
        "calmar": None if mdd == 0 else float(cagr(nav) / abs(mdd)),
        "volatility": float(returns.std() * math.sqrt(252.0)),
        "nav_final": float(nav.iloc[-1]),
    }


def empty_metrics() -> dict:
    return {
        "start_date": "",
        "end_date": "",
        "trading_days": 0,
        "total_return": None,
        "cagr": None,
        "sharpe": None,
        "max_drawdown": None,
        "calmar": None,
        "volatility": None,
        "nav_final": None,
    }


def cagr(nav: pd.Series) -> float:
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return float((nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0)


def sharpe(returns: pd.Series) -> float | None:
    std = returns.std()
    if pd.isna(std) or std == 0:
        return None
    return float(returns.mean() / std * math.sqrt(252.0))


def max_drawdown(nav: pd.Series) -> float:
    return float((nav / nav.cummax() - 1.0).min())


def normalize(series: pd.Series) -> pd.Series:
    series = series.dropna()
    if series.empty:
        return series
    return series / series.iloc[0]


def annualized_turnover(turnover: pd.DataFrame, nav: pd.Series) -> float:
    if turnover.empty or nav.empty:
        return 0.0
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    return float(turnover["turnover"].sum() / years) if years > 0 else 0.0


def qqq_correlation(nav: pd.Series, qqq_nav: pd.Series) -> float:
    data = pd.concat([nav.pct_change(), qqq_nav.pct_change()], axis=1).dropna()
    if data.empty:
        return 0.0
    return float(data.iloc[:, 0].corr(data.iloc[:, 1]))


def window_return(nav: pd.Series, start: str, end: str) -> float:
    sliced = nav.loc[start:end].dropna()
    if len(sliced) < 2:
        return 0.0
    return float(sliced.iloc[-1] / sliced.iloc[0] - 1.0)


def write_config(variants: list[Variant], evaluation_start: pd.Timestamp, primary_prices: pd.DataFrame, secondary_prices: pd.DataFrame, benchmark_metrics: dict) -> None:
    lines = [
        "experiment: X-ETF001",
        "status: pre_registered_scan",
        "currency: KRW_total_return_primary",
        f"evaluation_start: {evaluation_start.date().isoformat()}",
        f"evaluation_end: {primary_prices.index.max().date().isoformat()}",
        "primary_universe:",
        *[f"  - {ticker}" for ticker in PRIMARY_UNIVERSE],
        "secondary_universe:",
        *[f"  - {ticker}" for ticker in SECONDARY_UNIVERSE],
        f"secondary_common_start: {secondary_prices.index[252].date().isoformat()}",
        "cost_layers:",
        "  gross: no_cost_no_tax",
        "  after_cost: round_trip_30bps_on_turnover",
        "  after_tax: hifo_22pct_annual_2_5m_exemption",
        "random_control:",
        f"  trials: {RANDOM_TRIALS}",
        f"  seed: {RANDOM_SEED}",
        "benchmarks:",
        f"  p08_proxy_sharpe: {benchmark_metrics['p08_proxy']['sharpe']}",
        f"  p08_full_sharpe: {benchmark_metrics['p08_full']['sharpe']}",
        f"  equal_weight_13_after_cost_sharpe: {benchmark_metrics['equal_weight_13_after_cost']['sharpe']}",
        "variants:",
    ]
    for variant in variants:
        lines.extend(
            [
                f"  - variant_id: {variant.variant_id}",
                f"    signal: {variant.signal}",
                f"    portfolio: {variant.portfolio}",
                f"    rebalance: {variant.rebalance}",
            ]
        )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(variant_metrics: pd.DataFrame, top_rankings: pd.DataFrame, pass_gate: pd.DataFrame, benchmark_metrics: dict, evaluation_start: pd.Timestamp) -> None:
    best_after_cost = variant_metrics.loc[variant_metrics["cost_layer"] == "after_cost"].sort_values("sharpe", ascending=False).iloc[0]
    best_after_tax = variant_metrics.loc[variant_metrics["cost_layer"] == "after_tax"].sort_values("sharpe", ascending=False).iloc[0]
    verdict_counts = pass_gate["verdict"].value_counts().to_dict()
    lines = [
        "# X-ETF001 Time-Series Momentum Scan Report",
        "",
        "X-Lab 격리 산출물이다. D013, H001, P08_IEF30, engine.py, P08 paper tracking은 수정하지 않았다.",
        "",
        "## Verdict",
        "",
        f"사전 등록 40개 variant를 그대로 실행했다. Verdict 분포: `{json.dumps(verdict_counts, ensure_ascii=False)}`.",
        "",
        "## Benchmark",
        "",
        f"- Evaluation start: `{evaluation_start.date().isoformat()}`",
        f"- P08 proxy Sharpe: `{benchmark_metrics['p08_proxy']['sharpe']:.6f}`",
        f"- P08_IEF30 full Sharpe: `{benchmark_metrics['p08_full']['sharpe']:.6f}`",
        f"- Equal-weight 13 ETF after-cost Sharpe: `{benchmark_metrics['equal_weight_13_after_cost']['sharpe']:.6f}`",
        "",
        "## Best Variants",
        "",
        f"- Best after-cost Sharpe: `{best_after_cost.variant_id}` `{best_after_cost.sharpe:.6f}` CAGR `{best_after_cost.cagr:.6f}` MDD `{best_after_cost.max_drawdown:.6f}`",
        f"- Best after-tax Sharpe: `{best_after_tax.variant_id}` `{best_after_tax.sharpe:.6f}` CAGR `{best_after_tax.cagr:.6f}` MDD `{best_after_tax.max_drawdown:.6f}`",
        "",
        "## Caveats",
        "",
        "- Local Yahoo Finance `Close` is treated as adjusted total-return input following X-ETF000 convention.",
        "- Dividend withholding is documented as a taxable-account caveat; cash dividend streams are not separately available in local inputs.",
        "- After-tax NAV uses HIFO realized-gain accounting, 22% tax, and annual KRW 2.5M exemption on a KRW 100M normalized account.",
        "- Random TopK control uses deterministic local RNG seed and 1,000 trials per variant.",
        "",
        "## Output Files",
        "",
        "- `config.yaml`",
        "- `variant_metrics.csv`",
        "- `top_rankings.csv`",
        "- `subperiod_breakdown.csv`",
        "- `stress_windows.csv`",
        "- `random_control.csv`",
        "- `qqq_exposure_test.csv`",
        "- `equal_weight_comparison.csv`",
        "- `pass_gate_evaluation.csv`",
        "- `secondary_mchi_robustness.csv`",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
