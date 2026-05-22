from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")

ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
OUTPUT_DIR = Path("reports/experiments/I003_p07_p08_robustness")

H001_EQUITY_COL = "net_value"
COMPONENTS = ("QQQ", "SPY", "H001", "IEF")

GRID_A: dict[str, dict[str, float]] = {
    "A01_QQQ70_H00130_IEF00": {"QQQ": 0.70, "H001": 0.30},
    "A02_QQQ60_H00130_IEF10": {"QQQ": 0.60, "H001": 0.30, "IEF": 0.10},
    "A03_P07_QQQ50_H00130_IEF20": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "A04_QQQ40_H00130_IEF30": {"QQQ": 0.40, "H001": 0.30, "IEF": 0.30},
}

GRID_B: dict[str, dict[str, float]] = {
    "B01_SPY46_QQQ34_H00120_IEF00": {"SPY": 0.46, "QQQ": 0.34, "H001": 0.20},
    "B02_P08_SPY40_QQQ30_H00120_IEF10": {"SPY": 0.40, "QQQ": 0.30, "H001": 0.20, "IEF": 0.10},
    "B03_SPY34_QQQ26_H00120_IEF20": {"SPY": 0.34, "QQQ": 0.26, "H001": 0.20, "IEF": 0.20},
    "B04_SPY29_QQQ21_H00120_IEF30": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30},
}

GRID_C: dict[str, dict[str, float]] = {
    "C01_P07_QQQ50_SPY00_H00130_IEF20": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "C02_QQQ40_SPY10_H00130_IEF20": {"QQQ": 0.40, "SPY": 0.10, "H001": 0.30, "IEF": 0.20},
    "C03_QQQ35_SPY15_H00130_IEF20": {"QQQ": 0.35, "SPY": 0.15, "H001": 0.30, "IEF": 0.20},
    "C04_QQQ30_SPY20_H00130_IEF20": {"QQQ": 0.30, "SPY": 0.20, "H001": 0.30, "IEF": 0.20},
    "C05_QQQ25_SPY25_H00130_IEF20": {"QQQ": 0.25, "SPY": 0.25, "H001": 0.30, "IEF": 0.20},
}

PORTFOLIOS = {**GRID_A, **GRID_B, **GRID_C}
CANONICAL = {
    "P07": "A03_P07_QQQ50_H00130_IEF20",
    "P08": "B02_P08_SPY40_QQQ30_H00120_IEF10",
}

METRIC_COLUMNS = [
    "candidate",
    "grid",
    "weights",
    "start_date",
    "end_date",
    "cumulative_net_total_return",
    "cagr",
    "daily_annualized_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",
    "mdd_peak_date",
    "mdd_trough_date",
    "positive_years",
    "n_observations",
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fx = load_usdkrw()
    raw_curves = {
        "QQQ": build_etf_curve("QQQ", fx),
        "SPY": build_etf_curve("SPY", fx),
        "IEF": build_etf_curve("IEF", fx),
        "H001": load_reference_curve(H001_DIR / "equity_curve.csv", H001_EQUITY_COL, "H001"),
    }
    usd_curves = {ticker: load_etf_usd_curve(ticker) for ticker in ("QQQ", "SPY", "IEF")}

    component_nav = align_component_nav(raw_curves)
    component_returns = component_nav.pct_change().fillna(0.0)
    portfolio_nav, daily_contrib = build_portfolio_nav_and_contributions(component_nav, PORTFOLIOS)
    portfolio_returns = portfolio_nav.pct_change().fillna(0.0)

    metrics = build_metrics_table(portfolio_nav, portfolio_returns)
    grid_a = metrics_for_grid(metrics, GRID_A)
    grid_b = metrics_for_grid(metrics, GRID_B)
    grid_c = metrics_for_grid(metrics, GRID_C)
    covid = build_stress_table(portfolio_nav, daily_contrib, "2020_covid", "2020-02-01", "2020-04-30")
    rate = build_rate_shock_table(portfolio_nav, daily_contrib, component_nav, usd_curves)
    subperiod = build_subperiod_table(portfolio_nav, portfolio_returns)
    long_history = build_us_long_history_stress(usd_curves)
    p07_attr = build_contribution_attribution("P07", CANONICAL["P07"], PORTFOLIOS[CANONICAL["P07"]], portfolio_nav, daily_contrib, component_nav, usd_curves)
    p08_attr = build_contribution_attribution("P08", CANONICAL["P08"], PORTFOLIOS[CANONICAL["P08"]], portfolio_nav, daily_contrib, component_nav, usd_curves)

    grid_a.to_csv(OUTPUT_DIR / "grid_a_p07_style.csv", index=False)
    grid_b.to_csv(OUTPUT_DIR / "grid_b_p08_style.csv", index=False)
    grid_c.to_csv(OUTPUT_DIR / "grid_c_spy_inclusion.csv", index=False)
    covid.to_csv(OUTPUT_DIR / "covid_stress_2020.csv", index=False)
    rate.to_csv(OUTPUT_DIR / "rate_shock_stress_2022.csv", index=False)
    subperiod.to_csv(OUTPUT_DIR / "subperiod_split.csv", index=False)
    long_history.to_csv(OUTPUT_DIR / "us_long_history_stress.csv", index=False)
    p07_attr.to_csv(OUTPUT_DIR / "contribution_attribution_p07.csv", index=False)
    p08_attr.to_csv(OUTPUT_DIR / "contribution_attribution_p08.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "daily_metrics_all_candidates.csv", index=False)
    write_report(metrics, grid_a, grid_b, grid_c, covid, rate, subperiod, long_history, p07_attr, p08_attr, fx)


def load_usdkrw() -> pd.DataFrame:
    path = MACRO_DIR / "fred_dexkous_usdkrw.csv"
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    required = {"observation_date", "DEXKOUS"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.rename(columns={"observation_date": "date", "DEXKOUS": "usdkrw"})
    data["usdkrw"] = pd.to_numeric(data["usdkrw"], errors="coerce")
    return data.dropna(subset=["date", "usdkrw"]).sort_values("date").reset_index(drop=True)


def load_etf_prices(ticker: str) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
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


def load_etf_usd_curve(ticker: str) -> pd.DataFrame:
    data = load_etf_prices(ticker)
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", "close_usd"]].copy()
    data["net_value"] = data["close_usd"] / data["close_usd"].iloc[0]
    return data[["date", "net_value"]].reset_index(drop=True)


def load_reference_curve(path: Path, value_col: str, carrier: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"])
    required = {"date", value_col}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data = data.loc[data["date"].between(START_DATE, END_DATE), ["date", value_col]].copy()
    data["net_value"] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=["date", "net_value"]).sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError(f"{carrier} has no rows in requested period")
    data["net_value"] = data["net_value"] / data["net_value"].iloc[0]
    return data[["date", "net_value"]]


def align_component_nav(curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    calendar = sorted(set().union(*(set(curve["date"]) for curve in curves.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    index = index[(index >= START_DATE) & (index <= END_DATE)]
    aligned = {}
    for carrier, curve in curves.items():
        series = curve.set_index("date")["net_value"].reindex(index).ffill()
        if series.isna().any():
            first_bad = series.loc[series.isna()].index.min().date()
            raise ValueError(f"{carrier} has no NAV available on or before {first_bad}")
        aligned[carrier] = series / series.iloc[0]
    return pd.DataFrame(aligned, index=index)


def build_portfolio_nav_and_contributions(
    component_nav: pd.DataFrame,
    portfolios: dict[str, dict[str, float]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    component_returns = component_nav.pct_change().fillna(0.0)
    nav_values = {}
    contribution_rows = []
    quarters = component_returns.index.to_period("Q")
    for candidate, weights in portfolios.items():
        validate_weights(candidate, weights, component_nav.columns)
        values = []
        sleeve_values: dict[str, float] | None = None
        last_quarter = None
        for date, quarter in zip(component_returns.index, quarters, strict=True):
            rebalanced = False
            if sleeve_values is None:
                sleeve_values = {component: weight for component, weight in weights.items()}
                rebalanced = True
            elif quarter != last_quarter:
                portfolio_value = sum(sleeve_values.values())
                sleeve_values = {component: portfolio_value * weight for component, weight in weights.items()}
                rebalanced = True

            pre_nav = sum(sleeve_values.values())
            row = {
                "date": date,
                "candidate": candidate,
                "pre_nav": pre_nav,
                "rebalanced": rebalanced,
            }
            for component in COMPONENTS:
                row[f"{component}_contribution"] = 0.0
                row[f"{component}_weight_before_return"] = 0.0
            for component in weights:
                component_return = float(component_returns.loc[date, component])
                row[f"{component}_weight_before_return"] = sleeve_values[component] / pre_nav if pre_nav else 0.0
                row[f"{component}_contribution"] = sleeve_values[component] * component_return
                sleeve_values[component] *= 1.0 + component_return
            post_nav = sum(sleeve_values.values())
            row["daily_return"] = post_nav / pre_nav - 1.0 if pre_nav else 0.0
            row["net_value"] = post_nav
            contribution_rows.append(row)
            values.append(post_nav)
            last_quarter = quarter
        nav_values[candidate] = pd.Series(values, index=component_returns.index)
    return pd.DataFrame(nav_values, index=component_nav.index), pd.DataFrame(contribution_rows)


def validate_weights(candidate: str, weights: dict[str, float], available: pd.Index) -> None:
    total_weight = sum(weights.values())
    if not math.isclose(total_weight, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{candidate} weights sum to {total_weight}, expected 1.0")
    missing = sorted(set(weights).difference(available))
    if missing:
        raise ValueError(f"{candidate} missing component NAV: {missing}")


def build_metrics_table(nav: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = [metrics_for_candidate(candidate, nav[candidate], returns[candidate]) for candidate in nav.columns]
    metrics = pd.DataFrame(rows)
    metrics["candidate_order"] = metrics["candidate"].map({candidate: idx for idx, candidate in enumerate(nav.columns)})
    return metrics.sort_values("candidate_order")[METRIC_COLUMNS].reset_index(drop=True)


def metrics_for_candidate(candidate: str, nav: pd.Series, returns: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    daily_std = float(returns.std())
    downside = returns.loc[returns < 0.0]
    downside_std = float(downside.std()) if not downside.empty else float("nan")
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    yearly = returns.groupby(returns.index.year).apply(lambda values: float((1.0 + values).prod() - 1.0))
    return {
        "candidate": candidate,
        "grid": grid_for_candidate(candidate),
        "weights": weights_to_text(PORTFOLIOS[candidate]),
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "cumulative_net_total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "daily_annualized_volatility": daily_std * math.sqrt(252.0),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), daily_std),
        "sortino": safe_divide(float(returns.mean()) * math.sqrt(252.0), downside_std),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
        "positive_years": int((yearly > 0.0).sum()),
        "n_observations": int(returns.shape[0]),
    }


def metrics_for_grid(metrics: pd.DataFrame, grid: dict[str, dict[str, float]]) -> pd.DataFrame:
    return metrics.loc[metrics["candidate"].isin(grid)].copy().reset_index(drop=True)


def build_stress_table(
    nav: pd.DataFrame,
    daily_contrib: pd.DataFrame,
    stress_name: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    rows = []
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    for candidate in nav.columns:
        window = nav.loc[nav.index.to_series().between(start_ts, end_ts), candidate]
        peak_date, trough_date, mdd = peak_to_trough(window)
        recovery = recovery_date(nav[candidate], peak_date, trough_date)
        contrib = aggregate_contribution(daily_contrib, candidate, peak_date, trough_date)
        rows.append(
            {
                "stress": stress_name,
                "candidate": candidate,
                "grid": grid_for_candidate(candidate),
                "weights": weights_to_text(PORTFOLIOS[candidate]),
                "window_start": start,
                "window_end": end,
                "peak_date": peak_date.date().isoformat(),
                "trough_date": trough_date.date().isoformat(),
                "daily_mdd": mdd,
                "recovery_date": "" if recovery is None else recovery.date().isoformat(),
                "recovery_days": "" if recovery is None else int((recovery - trough_date).days),
                **contrib,
            }
        )
    return pd.DataFrame(rows)


def peak_to_trough(nav: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp, float]:
    if nav.empty:
        raise ValueError("empty stress window")
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return peak_date, trough_date, float(drawdown.loc[trough_date])


def recovery_date(nav: pd.Series, peak_date: pd.Timestamp, trough_date: pd.Timestamp) -> pd.Timestamp | None:
    peak_value = nav.loc[peak_date]
    recovered = nav.loc[trough_date:]
    recovered = recovered.loc[recovered >= peak_value]
    if recovered.empty:
        return None
    return recovered.index[0]


def aggregate_contribution(
    daily_contrib: pd.DataFrame,
    candidate: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> dict[str, float]:
    data = daily_contrib.loc[
        daily_contrib["candidate"].eq(candidate)
        & daily_contrib["date"].gt(start_date)
        & daily_contrib["date"].le(end_date)
    ]
    start_nav = float(data["pre_nav"].iloc[0]) if not data.empty else 1.0
    result = {}
    for component in COMPONENTS:
        result[f"{component}_return_contribution"] = float(data[f"{component}_contribution"].sum() / start_nav)
    result["total_return_contribution"] = float(sum(result[f"{component}_return_contribution"] for component in COMPONENTS))
    return result


def build_rate_shock_table(
    nav: pd.DataFrame,
    daily_contrib: pd.DataFrame,
    component_nav: pd.DataFrame,
    usd_curves: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    start = pd.Timestamp("2022-01-01")
    end = pd.Timestamp("2022-12-31")
    qqq_usd = period_return(align_single_curve(usd_curves["QQQ"], nav.index), start, end)
    ief_usd = period_return(align_single_curve(usd_curves["IEF"], nav.index), start, end)
    qqq_krw = period_return(component_nav["QQQ"], start, end)
    ief_krw = period_return(component_nav["IEF"], start, end)
    for candidate in nav.columns:
        candidate_return = period_return(nav[candidate], start, end)
        contrib = aggregate_contribution(daily_contrib, candidate, first_observation_on_or_after(nav.index, start), last_observation_on_or_before(nav.index, end))
        rows.append(
            {
                "candidate": candidate,
                "grid": grid_for_candidate(candidate),
                "weights": weights_to_text(PORTFOLIOS[candidate]),
                "calendar_year_return_krw": candidate_return,
                "QQQ_weight": PORTFOLIOS[candidate].get("QQQ", 0.0),
                "IEF_weight": PORTFOLIOS[candidate].get("IEF", 0.0),
                "QQQ_2022_return_usd": qqq_usd,
                "IEF_2022_return_usd": ief_usd,
                "QQQ_2022_return_krw": qqq_krw,
                "IEF_2022_return_krw": ief_krw,
                "QQQ_weighted_krw_impact": PORTFOLIOS[candidate].get("QQQ", 0.0) * qqq_krw,
                "IEF_weighted_krw_impact": PORTFOLIOS[candidate].get("IEF", 0.0) * ief_krw,
                **contrib,
            }
        )
    return pd.DataFrame(rows)


def build_subperiod_table(nav: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    periods = {
        "2010_2017": (pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        "2018_2026": (pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
        "2021_2022_drawdown": (pd.Timestamp("2021-01-01"), pd.Timestamp("2023-12-31")),
    }
    for candidate in nav.columns:
        for period, (start, end) in periods.items():
            n = nav.loc[nav.index.to_series().between(start, end), candidate]
            r = returns.loc[returns.index.to_series().between(start, end), candidate]
            if n.empty:
                continue
            metric = metrics_for_period(candidate, period, n, r)
            rows.append(metric)
    return pd.DataFrame(rows)


def metrics_for_period(candidate: str, period: str, nav: pd.Series, returns: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if period == "2021_2022_drawdown":
        peak_window = nav.loc[nav.index.year == 2021]
        peak_date = peak_window.idxmax()
        drawdown = nav.loc[peak_date:] / nav.loc[peak_date] - 1.0
        trough_date = drawdown.idxmin()
    else:
        drawdown = nav / nav.cummax() - 1.0
        trough_date = drawdown.idxmin()
        peak_date = nav.loc[:trough_date].idxmax()
    return {
        "candidate": candidate,
        "grid": grid_for_candidate(candidate),
        "period": period,
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0) if years > 0.0 else float("nan"),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), float(returns.std())),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
        "mdd_length_days": int((trough_date - peak_date).days),
    }


def build_us_long_history_stress(usd_curves: dict[str, pd.DataFrame]) -> pd.DataFrame:
    min_dates = {ticker: curve["date"].min().date().isoformat() for ticker, curve in usd_curves.items()}
    if any(pd.Timestamp(value) > pd.Timestamp("2000-01-01") for value in min_dates.values()):
        return pd.DataFrame(
            [
                {
                    "status": "skipped",
                    "reason": "local ETF files do not contain 2000-2002 history; network fetch is forbidden",
                    "QQQ_start": min_dates["QQQ"],
                    "SPY_start": min_dates["SPY"],
                    "IEF_start": min_dates["IEF"],
                }
            ]
        )
    return pd.DataFrame()


def build_contribution_attribution(
    label: str,
    candidate: str,
    weights: dict[str, float],
    nav: pd.DataFrame,
    daily_contrib: pd.DataFrame,
    component_nav: pd.DataFrame,
    usd_curves: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    data = daily_contrib.loc[daily_contrib["candidate"].eq(candidate)].copy()
    start = nav.index[0]
    end = nav.index[-1]
    total_return = float(nav.loc[end, candidate] / nav.loc[start, candidate] - 1.0)
    component_sum = {component: float(data[f"{component}_contribution"].sum()) for component in COMPONENTS}
    buy_hold_return = sum(weights.get(component, 0.0) * period_return(component_nav[component], start, end) for component in weights)
    rebalance_effect = total_return - buy_hold_return

    rows = []
    for component in COMPONENTS:
        krw_return = period_return(component_nav[component], start, end) if component in component_nav else 0.0
        usd_return = period_return(align_single_curve(usd_curves[component], nav.index), start, end) if component in usd_curves else 0.0
        fx_contribution = weights.get(component, 0.0) * (krw_return - usd_return) if component in usd_curves else 0.0
        rows.append(
            {
                "portfolio": label,
                "candidate": candidate,
                "component": component,
                "target_weight": weights.get(component, 0.0),
                "return_contribution": component_sum[component],
                "component_total_return_krw": krw_return,
                "component_total_return_usd": "" if component not in usd_curves else usd_return,
                "fx_contribution_estimate": fx_contribution,
            }
        )
    rows.append(
        {
            "portfolio": label,
            "candidate": candidate,
            "component": "rebalance_effect",
            "target_weight": "",
            "return_contribution": rebalance_effect,
            "component_total_return_krw": "",
            "component_total_return_usd": "",
            "fx_contribution_estimate": "",
        }
    )
    rows.append(
        {
            "portfolio": label,
            "candidate": candidate,
            "component": "total",
            "target_weight": 1.0,
            "return_contribution": total_return,
            "component_total_return_krw": total_return,
            "component_total_return_usd": "",
            "fx_contribution_estimate": sum(
                weights.get(component, 0.0)
                * (
                    period_return(component_nav[component], start, end)
                    - period_return(align_single_curve(usd_curves[component], nav.index), start, end)
                )
                for component in ("QQQ", "SPY", "IEF")
                if component in weights
            ),
        }
    )
    return pd.DataFrame(rows)


def period_return(series: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> float:
    start_date = first_observation_on_or_after(series.index, start)
    end_date = last_observation_on_or_before(series.index, end)
    if start_date is None or end_date is None or end_date < start_date:
        return float("nan")
    return float(series.loc[end_date] / series.loc[start_date] - 1.0)


def first_observation_on_or_after(index: pd.DatetimeIndex, start: pd.Timestamp) -> pd.Timestamp:
    values = index[index >= start]
    if values.empty:
        raise ValueError(f"no observation on or after {start.date()}")
    return values[0]


def last_observation_on_or_before(index: pd.DatetimeIndex, end: pd.Timestamp) -> pd.Timestamp:
    values = index[index <= end]
    if values.empty:
        raise ValueError(f"no observation on or before {end.date()}")
    return values[-1]


def align_single_curve(curve: pd.DataFrame, index: pd.DatetimeIndex) -> pd.Series:
    series = curve.set_index("date")["net_value"].reindex(index).ffill()
    if series.isna().any():
        series = series.bfill()
    return series / series.iloc[0]


def grid_for_candidate(candidate: str) -> str:
    if candidate in GRID_A:
        return "I003-A"
    if candidate in GRID_B:
        return "I003-B"
    if candidate in GRID_C:
        return "I003-C"
    return "unknown"


def weights_to_text(weights: dict[str, float]) -> str:
    return "/".join(f"{component}{int(round(weight * 100))}" for component, weight in weights.items())


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def verdict(metrics: pd.DataFrame, rate: pd.DataFrame, long_history: pd.DataFrame) -> str:
    p07 = metrics.set_index("candidate").loc[CANONICAL["P07"]]
    p08 = metrics.set_index("candidate").loc[CANONICAL["P08"]]
    rate_idx = rate.set_index("candidate")
    p07_2022 = float(rate_idx.loc[CANONICAL["P07"], "calendar_year_return_krw"])
    p08_2022 = float(rate_idx.loc[CANONICAL["P08"], "calendar_year_return_krw"])
    long_history_skipped = not long_history.empty and "skipped" in set(long_history.get("status", []))

    if p07["sharpe"] > p08["sharpe"] and p07_2022 >= p08_2022 and not long_history_skipped:
        return "P07 promote"
    if p07_2022 < p08_2022:
        return "P08 prefer"
    return "둘 다 후보 유지"


def write_report(
    metrics: pd.DataFrame,
    grid_a: pd.DataFrame,
    grid_b: pd.DataFrame,
    grid_c: pd.DataFrame,
    covid: pd.DataFrame,
    rate: pd.DataFrame,
    subperiod: pd.DataFrame,
    long_history: pd.DataFrame,
    p07_attr: pd.DataFrame,
    p08_attr: pd.DataFrame,
    fx: pd.DataFrame,
) -> None:
    p07_id = CANONICAL["P07"]
    p08_id = CANONICAL["P08"]
    metric_idx = metrics.set_index("candidate")
    p07 = metric_idx.loc[p07_id]
    p08 = metric_idx.loc[p08_id]
    covid_idx = covid.set_index("candidate")
    rate_idx = rate.set_index("candidate")
    final_verdict = verdict(metrics, rate, long_history)
    long_history_text = (
        str(long_history.iloc[0]["reason"])
        if not long_history.empty and "reason" in long_history.columns
        else "US long-history stress computed."
    )
    recommendation = (
        "I004 final candidate registration 전에 I002가 남아 있으면 I002를 먼저 진행하고, "
        "I002 완료 후 P07/P08 둘 다 후보 유지 상태로 final registration을 검토한다."
        if final_verdict == "둘 다 후보 유지"
        else "I004 final candidate registration으로 넘어가되, grid best가 아니라 사전 등록 후보만 등록한다."
    )

    lines = [
        "# I003 — P07/P08 Robustness",
        "",
        "## 방법",
        "",
        "- I001.6과 동일한 daily NAV 재구성: quarterly rebalance + daily mark-to-market.",
        "- 외부 network는 사용하지 않았다. D013/H001 strategy와 `engine.py`는 수정하지 않았다.",
        f"- 기간: {START_DATE.date()}부터 {END_DATE.date()}까지.",
        f"- USDKRW latest observation used: {fx['date'].max().date()} at {fx['usdkrw'].iloc[-1]}.",
        "- Grid는 plateau 확인용이며, 새 weight를 final 후보로 승격하지 않는다.",
        "",
        "## Grid plateau 확인",
        "",
        "### I003-A P07-style IEF grid",
        "",
        markdown_table(grid_a, ["candidate", "weights", "cagr", "sharpe", "sortino", "max_drawdown", "positive_years"]),
        "",
        "### I003-B P08-style IEF grid",
        "",
        markdown_table(grid_b, ["candidate", "weights", "cagr", "sharpe", "sortino", "max_drawdown", "positive_years"]),
        "",
        "### I003-C SPY inclusion test",
        "",
        markdown_table(grid_c, ["candidate", "weights", "cagr", "sharpe", "sortino", "max_drawdown", "positive_years"]),
        "",
        "## 2020 stress 결과",
        "",
        f"- P07 COVID MDD: {covid_idx.loc[p07_id, 'daily_mdd']:.6f}, recovery {covid_idx.loc[p07_id, 'recovery_date']}.",
        f"- P08 COVID MDD: {covid_idx.loc[p08_id, 'daily_mdd']:.6f}, recovery {covid_idx.loc[p08_id, 'recovery_date']}.",
        "",
        markdown_table(
            covid.loc[covid["candidate"].isin([p07_id, p08_id])],
            ["candidate", "daily_mdd", "recovery_date", "QQQ_return_contribution", "SPY_return_contribution", "H001_return_contribution", "IEF_return_contribution"],
        ),
        "",
        "## 2022 stress 결과",
        "",
        f"- P07 2022 KRW return: {rate_idx.loc[p07_id, 'calendar_year_return_krw']:.6f}; IEF weight 20%.",
        f"- P08 2022 KRW return: {rate_idx.loc[p08_id, 'calendar_year_return_krw']:.6f}; IEF weight 10%.",
        f"- Local data 기준 QQQ 2022 USD return {rate_idx.loc[p07_id, 'QQQ_2022_return_usd']:.6f}, IEF 2022 USD return {rate_idx.loc[p07_id, 'IEF_2022_return_usd']:.6f}.",
        "",
        markdown_table(
            rate.loc[rate["candidate"].isin([p07_id, p08_id])],
            ["candidate", "calendar_year_return_krw", "QQQ_weighted_krw_impact", "IEF_weighted_krw_impact", "QQQ_return_contribution", "IEF_return_contribution"],
        ),
        "",
        "## Long-history stress",
        "",
        f"- {long_history_text}",
        "- 2000-2002 dot-com 구간은 local QQQ/SPY/IEF 파일이 2010부터 시작하므로 산출하지 않았다. H001은 ticket대로 2010 이전 재현하지 않는다.",
        "",
        "## Subperiod 결과",
        "",
        markdown_table(
            subperiod.loc[subperiod["candidate"].isin([p07_id, p08_id])],
            ["candidate", "period", "cagr", "sharpe", "max_drawdown", "mdd_peak_date", "mdd_trough_date", "mdd_length_days"],
        ),
        "",
        "## Contribution attribution",
        "",
        "### P07",
        "",
        markdown_table(p07_attr, ["component", "target_weight", "return_contribution", "component_total_return_krw", "component_total_return_usd", "fx_contribution_estimate"]),
        "",
        "### P08",
        "",
        markdown_table(p08_attr, ["component", "target_weight", "return_contribution", "component_total_return_krw", "component_total_return_usd", "fx_contribution_estimate"]),
        "",
        "## 최종 verdict",
        "",
        f"- Verdict: {final_verdict}.",
        f"- P07: Sharpe {p07['sharpe']:.6f}, CAGR {p07['cagr']:.6f}, MDD {p07['max_drawdown']:.6f}.",
        f"- P08: Sharpe {p08['sharpe']:.6f}, CAGR {p08['cagr']:.6f}, MDD {p08['max_drawdown']:.6f}.",
        "- 사전 등록 rule에 따라 grid의 새 best weight는 final 승격하지 않는다.",
        f"- 진행 권고: {recommendation}",
        "",
        "## Files",
        "",
        "- grid_a_p07_style.csv",
        "- grid_b_p08_style.csv",
        "- grid_c_spy_inclusion.csv",
        "- covid_stress_2020.csv",
        "- rate_shock_stress_2022.csv",
        "- subperiod_split.csv",
        "- us_long_history_stress.csv",
        "- contribution_attribution_p07.csv",
        "- contribution_attribution_p08.csv",
        "- daily_metrics_all_candidates.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append("" if math.isnan(value) else f"{value:.6f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


if __name__ == "__main__":
    main()
