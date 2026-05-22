from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import pandas as pd


START_DATE = pd.Timestamp("2010-01-04")
END_DATE = pd.Timestamp("2026-05-18")

ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
OUTPUT_DIR = Path("reports/experiments/I003_5_static_allocation_frontier")

H001_EQUITY_COL = "net_value"
COMPONENTS = ("QQQ", "SPY", "H001", "IEF")
LONG_TICKERS = ("QQQ", "SPY", "IEF", "TLT", "GLD")

Frequency = Literal["monthly", "quarterly", "semiannual", "annual"]

GRID_A: dict[str, dict[str, float]] = {
    "A01_QQQ70_H00130_IEF00": {"QQQ": 0.70, "H001": 0.30},
    "A02_QQQ60_H00130_IEF10": {"QQQ": 0.60, "H001": 0.30, "IEF": 0.10},
    "A03_P07_QQQ50_H00130_IEF20": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "A04_QQQ40_H00130_IEF30": {"QQQ": 0.40, "H001": 0.30, "IEF": 0.30},
    "A05_QQQ30_H00130_IEF40": {"QQQ": 0.30, "H001": 0.30, "IEF": 0.40},
    "A06_QQQ20_H00130_IEF50": {"QQQ": 0.20, "H001": 0.30, "IEF": 0.50},
}

GRID_B: dict[str, dict[str, float]] = {
    "B01_SPY46_QQQ34_H00120_IEF00": {"SPY": 0.46, "QQQ": 0.34, "H001": 0.20},
    "B02_P08_SPY40_QQQ30_H00120_IEF10": {"SPY": 0.40, "QQQ": 0.30, "H001": 0.20, "IEF": 0.10},
    "B03_SPY34_QQQ26_H00120_IEF20": {"SPY": 0.34, "QQQ": 0.26, "H001": 0.20, "IEF": 0.20},
    "B04_SPY29_QQQ21_H00120_IEF30": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30},
    "B05_SPY23_QQQ17_H00120_IEF40": {"SPY": 0.23, "QQQ": 0.17, "H001": 0.20, "IEF": 0.40},
}

PORTFOLIOS = {**GRID_A, **GRID_B}
FOCUS: dict[str, str] = {
    "P07": "A03_P07_QQQ50_H00130_IEF20",
    "P08": "B02_P08_SPY40_QQQ30_H00120_IEF10",
    "P07_IEF30": "A04_QQQ40_H00130_IEF30",
    "P08_IEF30": "B04_SPY29_QQQ21_H00120_IEF30",
}

LONG_PORTFOLIOS: dict[str, dict[str, float]] = {
    "L01_QQQ100": {"QQQ": 1.00},
    "L02_SPY100": {"SPY": 1.00},
    "L03_QQQ50_SPY50": {"QQQ": 0.50, "SPY": 0.50},
    "L04_QQQ50_IEF50": {"QQQ": 0.50, "IEF": 0.50},
    "L05_QQQ40_SPY10_IEF50": {"QQQ": 0.40, "SPY": 0.10, "IEF": 0.50},
    "L06_SPY40_QQQ30_IEF30_P08_PROXY": {"SPY": 0.40, "QQQ": 0.30, "IEF": 0.30},
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

    component_nav = align_component_nav(raw_curves, START_DATE, END_DATE)
    portfolio_nav, daily_contrib = build_portfolio_nav_and_contributions(component_nav, PORTFOLIOS, "quarterly")
    portfolio_returns = portfolio_nav.pct_change().fillna(0.0)

    metrics = build_metrics_table(portfolio_nav, portfolio_returns, PORTFOLIOS)
    frontier_a = metrics_for_grid(metrics, GRID_A)
    frontier_b = metrics_for_grid(metrics, GRID_B)
    rebalance_frequency = build_rebalance_frequency_table(component_nav)
    stress_2020 = build_stress_table(portfolio_nav, daily_contrib, "2020_covid", "2020-02-01", "2020-04-30")
    stress_2022 = build_rate_shock_table(portfolio_nav, daily_contrib, component_nav, usd_curves)
    stress_2021_2022 = build_2021_2022_drawdown_table(portfolio_nav)
    spike_exclusion = build_spike_exclusion_table(portfolio_nav)
    subperiod = build_subperiod_table(portfolio_nav, portfolio_returns)
    long_history = build_us_long_history_stress()
    contribution = build_contribution_attribution_table(portfolio_nav, daily_contrib, component_nav, usd_curves)
    scorecard = build_scorecard(metrics, stress_2022, stress_2020, long_history, rebalance_frequency)

    frontier_a.to_csv(OUTPUT_DIR / "frontier_a_p07_style.csv", index=False)
    frontier_b.to_csv(OUTPUT_DIR / "frontier_b_p08_style.csv", index=False)
    rebalance_frequency.to_csv(OUTPUT_DIR / "rebalance_frequency.csv", index=False)
    stress_2020.to_csv(OUTPUT_DIR / "stress_2020_covid.csv", index=False)
    stress_2022.to_csv(OUTPUT_DIR / "stress_2022_rate_shock.csv", index=False)
    stress_2021_2022.to_csv(OUTPUT_DIR / "stress_2021_2022_drawdown.csv", index=False)
    spike_exclusion.to_csv(OUTPUT_DIR / "spike_exclusion_2025.csv", index=False)
    subperiod.to_csv(OUTPUT_DIR / "subperiod_split.csv", index=False)
    long_history.to_csv(OUTPUT_DIR / "long_history_us_core.csv", index=False)
    contribution.to_csv(OUTPUT_DIR / "contribution_attribution.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "daily_metrics_all_candidates.csv", index=False)
    write_report(
        metrics=metrics,
        frontier_a=frontier_a,
        frontier_b=frontier_b,
        rebalance_frequency=rebalance_frequency,
        stress_2020=stress_2020,
        stress_2022=stress_2022,
        stress_2021_2022=stress_2021_2022,
        spike_exclusion=spike_exclusion,
        subperiod=subperiod,
        long_history=long_history,
        contribution=contribution,
        scorecard=scorecard,
        fx=fx,
    )


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


def load_etf_prices(ticker: str, long: bool = False) -> pd.DataFrame:
    suffix = "_long" if long else ""
    path = ETF_DIR / f"yf_{ticker}{suffix}.csv"
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


def load_etf_usd_curve(ticker: str, long: bool = False) -> pd.DataFrame:
    data = load_etf_prices(ticker, long=long)
    if not long:
        data = data.loc[data["date"].between(START_DATE, END_DATE)].copy()
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


def align_component_nav(
    curves: dict[str, pd.DataFrame],
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> pd.DataFrame:
    calendar = sorted(set().union(*(set(curve["date"]) for curve in curves.values())))
    index = pd.DatetimeIndex(calendar, name="date")
    if start is not None:
        index = index[index >= start]
    if end is not None:
        index = index[index <= end]
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
    frequency: Frequency,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    component_returns = component_nav.pct_change().fillna(0.0)
    period_keys = rebalance_keys(component_returns.index, frequency)
    nav_values = {}
    contribution_rows = []
    for candidate, weights in portfolios.items():
        validate_weights(candidate, weights, component_nav.columns)
        values = []
        sleeve_values: dict[str, float] | None = None
        last_key = None
        for date, period_key in zip(component_returns.index, period_keys, strict=True):
            rebalanced = False
            if sleeve_values is None:
                sleeve_values = {component: weight for component, weight in weights.items()}
                rebalanced = True
            elif period_key != last_key:
                portfolio_value = sum(sleeve_values.values())
                sleeve_values = {component: portfolio_value * weight for component, weight in weights.items()}
                rebalanced = True

            pre_nav = sum(sleeve_values.values())
            row = {"date": date, "candidate": candidate, "pre_nav": pre_nav, "rebalanced": rebalanced}
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
            last_key = period_key
        nav_values[candidate] = pd.Series(values, index=component_returns.index)
    return pd.DataFrame(nav_values, index=component_nav.index), pd.DataFrame(contribution_rows)


def rebalance_keys(index: pd.DatetimeIndex, frequency: Frequency) -> list[tuple[int, int] | int]:
    if frequency == "monthly":
        return [(date.year, date.month) for date in index]
    if frequency == "quarterly":
        return [(date.year, (date.month - 1) // 3 + 1) for date in index]
    if frequency == "semiannual":
        return [(date.year, 1 if date.month <= 6 else 2) for date in index]
    if frequency == "annual":
        return [date.year for date in index]
    raise ValueError(f"unknown rebalance frequency: {frequency}")


def validate_weights(candidate: str, weights: dict[str, float], available: pd.Index) -> None:
    total_weight = sum(weights.values())
    if not math.isclose(total_weight, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{candidate} weights sum to {total_weight}, expected 1.0")
    missing = sorted(set(weights).difference(available))
    if missing:
        raise ValueError(f"{candidate} missing component NAV: {missing}")


def build_metrics_table(
    nav: pd.DataFrame,
    returns: pd.DataFrame,
    portfolios: dict[str, dict[str, float]],
) -> pd.DataFrame:
    rows = [metrics_for_candidate(candidate, nav[candidate], returns[candidate], portfolios) for candidate in nav.columns]
    metrics = pd.DataFrame(rows)
    metrics["candidate_order"] = metrics["candidate"].map({candidate: idx for idx, candidate in enumerate(nav.columns)})
    return metrics.sort_values("candidate_order")[METRIC_COLUMNS].reset_index(drop=True)


def metrics_for_candidate(
    candidate: str,
    nav: pd.Series,
    returns: pd.Series,
    portfolios: dict[str, dict[str, float]],
) -> dict:
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
        "weights": weights_to_text(portfolios[candidate]),
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


def build_rebalance_frequency_table(component_nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    focus_portfolios = {candidate: PORTFOLIOS[candidate] for candidate in FOCUS.values()}
    for frequency in ("monthly", "quarterly", "semiannual", "annual"):
        nav, _ = build_portfolio_nav_and_contributions(component_nav, focus_portfolios, frequency)  # type: ignore[arg-type]
        returns = nav.pct_change().fillna(0.0)
        metrics = build_metrics_table(nav, returns, focus_portfolios)
        for _, row in metrics.iterrows():
            rows.append(
                {
                    "portfolio": label_for_candidate(row["candidate"]),
                    "candidate": row["candidate"],
                    "frequency": frequency,
                    "cagr": row["cagr"],
                    "sharpe": row["sharpe"],
                    "max_drawdown": row["max_drawdown"],
                    "mdd_peak_date": row["mdd_peak_date"],
                    "mdd_trough_date": row["mdd_trough_date"],
                }
            )
    return pd.DataFrame(rows)


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
    component_returns_krw = {
        component: period_return(component_nav[component], start, end)
        for component in COMPONENTS
        if component in component_nav
    }
    component_returns_usd = {
        component: period_return(align_single_curve(usd_curves[component], nav.index), start, end)
        for component in ("QQQ", "SPY", "IEF")
    }
    for candidate in nav.columns:
        candidate_return = period_return(nav[candidate], start, end)
        contrib = aggregate_contribution(
            daily_contrib,
            candidate,
            first_observation_on_or_after(nav.index, start),
            last_observation_on_or_before(nav.index, end),
        )
        row = {
            "candidate": candidate,
            "grid": grid_for_candidate(candidate),
            "weights": weights_to_text(PORTFOLIOS[candidate]),
            "calendar_year_return_krw": candidate_return,
        }
        for component in COMPONENTS:
            weight = PORTFOLIOS[candidate].get(component, 0.0)
            row[f"{component}_weight"] = weight
            row[f"{component}_2022_return_krw"] = component_returns_krw.get(component, float("nan"))
            row[f"{component}_weighted_krw_impact"] = weight * component_returns_krw.get(component, 0.0)
            if component in component_returns_usd:
                row[f"{component}_2022_return_usd"] = component_returns_usd[component]
        rows.append({**row, **contrib})
    return pd.DataFrame(rows)


def build_2021_2022_drawdown_table(nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    start = pd.Timestamp("2021-01-01")
    end = pd.Timestamp("2022-12-31")
    for label, candidate in FOCUS.items():
        window = nav.loc[nav.index.to_series().between(start, end), candidate]
        peak_window = window.loc[window.index.year == 2021]
        peak_date = peak_window.idxmax()
        drawdown = window.loc[peak_date:] / window.loc[peak_date] - 1.0
        trough_date = drawdown.idxmin()
        recovery = recovery_date(nav[candidate], peak_date, trough_date)
        rows.append(
            {
                "portfolio": label,
                "candidate": candidate,
                "weights": weights_to_text(PORTFOLIOS[candidate]),
                "window_start": start.date().isoformat(),
                "window_end": end.date().isoformat(),
                "peak_date": peak_date.date().isoformat(),
                "trough_date": trough_date.date().isoformat(),
                "peak_to_trough_mdd": float(drawdown.loc[trough_date]),
                "drawdown_length_days": int((trough_date - peak_date).days),
                "recovery_date": "" if recovery is None else recovery.date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_spike_exclusion_table(nav: pd.DataFrame) -> pd.DataFrame:
    rows = []
    mask = nav.index.year != 2025
    filtered = nav.loc[mask].copy()
    returns = filtered.pct_change().fillna(0.0)
    for candidate in filtered.columns:
        metric = metrics_for_period(candidate, "exclude_2025_calendar_year", filtered[candidate], returns[candidate])
        metric["grid"] = grid_for_candidate(candidate)
        metric["weights"] = weights_to_text(PORTFOLIOS[candidate])
        rows.append(metric)
    return pd.DataFrame(rows)


def build_subperiod_table(nav: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    periods = {
        "2010_2017": (pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        "2018_2026": (pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
    }
    for candidate in nav.columns:
        for period, (start, end) in periods.items():
            n = nav.loc[nav.index.to_series().between(start, end), candidate]
            r = returns.loc[returns.index.to_series().between(start, end), candidate]
            if n.empty:
                continue
            metric = metrics_for_period(candidate, period, n, r)
            metric["grid"] = grid_for_candidate(candidate)
            metric["weights"] = weights_to_text(PORTFOLIOS[candidate])
            rows.append(metric)
    return pd.DataFrame(rows)


def metrics_for_period(candidate: str, period: str, nav: pd.Series, returns: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    return {
        "candidate": candidate,
        "period": period,
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "cumulative_net_total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0) if years > 0.0 else float("nan"),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), float(returns.std())),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
        "mdd_length_days": int((trough_date - peak_date).days),
    }


def build_us_long_history_stress() -> pd.DataFrame:
    download_status = ensure_long_history_files()
    missing = [ticker for ticker in ("QQQ", "SPY", "IEF") if not (ETF_DIR / f"yf_{ticker}_long.csv").exists()]
    if missing:
        return pd.DataFrame(
            [
                {
                    "status": "skipped",
                    "reason": f"long-history files missing after yfinance attempt: {', '.join(missing)}",
                    "download_status": download_status,
                }
            ]
        )

    curves = {ticker: load_etf_usd_curve(ticker, long=True) for ticker in ("QQQ", "SPY", "IEF")}
    rows = []
    periods = {
        "dot_com_2000_2002": (pd.Timestamp("2000-01-01"), pd.Timestamp("2002-12-31")),
        "gfc_2008": (pd.Timestamp("2008-01-01"), pd.Timestamp("2009-03-31")),
        "full_common_history": (pd.Timestamp("1999-03-10"), pd.Timestamp("2026-12-31")),
    }
    for portfolio, weights in LONG_PORTFOLIOS.items():
        available_curves = {component: curves[component] for component in weights}
        common_start = max(curve["date"].min() for curve in available_curves.values())
        common_end = min(curve["date"].max() for curve in available_curves.values())
        component_nav = align_component_nav(available_curves, common_start, common_end)
        nav, _ = build_long_portfolio_nav(component_nav, {portfolio: weights}, "quarterly")
        returns = nav.pct_change().fillna(0.0)
        for period, (start, end) in periods.items():
            n = nav.loc[nav.index.to_series().between(start, end), portfolio]
            r = returns.loc[returns.index.to_series().between(start, end), portfolio]
            if n.empty or n.index.min() > start + pd.Timedelta(days=31):
                rows.append(
                    {
                        "status": "skipped",
                        "portfolio": portfolio,
                        "weights": weights_to_text(weights),
                        "period": period,
                        "reason": f"common history starts {common_start.date()}, after required period start",
                        "start_date": "",
                        "end_date": "",
                        "cagr": float("nan"),
                        "sharpe": float("nan"),
                        "max_drawdown": float("nan"),
                    }
                )
                continue
            metric = metrics_for_period(portfolio, period, n, r)
            rows.append(
                {
                    "status": "computed",
                    "portfolio": portfolio,
                    "weights": weights_to_text(weights),
                    "period": period,
                    "reason": "",
                    **metric,
                }
            )
    return pd.DataFrame(rows)


def ensure_long_history_files() -> str:
    needed = [ticker for ticker in LONG_TICKERS if not (ETF_DIR / f"yf_{ticker}_long.csv").exists()]
    if not needed:
        return "existing long-history files used"
    try:
        import yfinance as yf  # type: ignore[import-not-found]
    except Exception as exc:
        return f"skipped: yfinance import failed: {exc}"

    statuses = []
    for ticker in needed:
        path = ETF_DIR / f"yf_{ticker}_long.csv"
        try:
            data = yf.download(ticker, start="1993-01-01", end="2026-05-19", auto_adjust=True, progress=False, timeout=20)
            if data.empty:
                statuses.append(f"{ticker}: empty download")
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [column[0] if isinstance(column, tuple) else column for column in data.columns]
            data = data.reset_index()
            if "Date" not in data.columns or "Close" not in data.columns:
                statuses.append(f"{ticker}: missing Date/Close columns")
                continue
            output = data[["Date", "Close", "High", "Low", "Open", "Volume"]].copy()
            output.to_csv(path, index=False)
            statuses.append(f"{ticker}: downloaded {len(output)} rows")
        except Exception as exc:
            statuses.append(f"{ticker}: failed: {exc}")
    if statuses and all("empty download" in status for status in statuses):
        return "network/DNS blocked or Yahoo returned empty downloads; " + "; ".join(statuses)
    return "; ".join(statuses)


def build_long_portfolio_nav(
    component_nav: pd.DataFrame,
    portfolios: dict[str, dict[str, float]],
    frequency: Frequency,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    original_components = globals()["COMPONENTS"]
    try:
        globals()["COMPONENTS"] = tuple(component_nav.columns)  # type: ignore[assignment]
        return build_portfolio_nav_and_contributions(component_nav, portfolios, frequency)
    finally:
        globals()["COMPONENTS"] = original_components  # type: ignore[assignment]


def build_contribution_attribution_table(
    nav: pd.DataFrame,
    daily_contrib: pd.DataFrame,
    component_nav: pd.DataFrame,
    usd_curves: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    periods = {
        "2010_2017": (pd.Timestamp("2010-01-01"), pd.Timestamp("2017-12-31")),
        "2018_2026": (pd.Timestamp("2018-01-01"), pd.Timestamp("2026-12-31")),
    }
    for label, candidate in FOCUS.items():
        weights = PORTFOLIOS[candidate]
        for period, (start_bound, end_bound) in periods.items():
            start = first_observation_on_or_after(nav.index, start_bound)
            end = last_observation_on_or_before(nav.index, end_bound)
            data = daily_contrib.loc[
                daily_contrib["candidate"].eq(candidate)
                & daily_contrib["date"].gt(start)
                & daily_contrib["date"].le(end)
            ]
            total_return = period_return(nav[candidate], start, end)
            buy_hold_return = sum(
                weights.get(component, 0.0) * period_return(component_nav[component], start, end)
                for component in weights
            )
            rebalance_effect = total_return - buy_hold_return
            fx_estimate = 0.0
            for component in ("QQQ", "SPY", "IEF"):
                if component in weights:
                    krw_return = period_return(component_nav[component], start, end)
                    usd_return = period_return(align_single_curve(usd_curves[component], nav.index), start, end)
                    fx_estimate += weights[component] * (krw_return - usd_return)
            for component in COMPONENTS:
                component_sum = float(data[f"{component}_contribution"].sum()) if not data.empty else 0.0
                start_nav = float(data["pre_nav"].iloc[0]) if not data.empty else 1.0
                krw_return = period_return(component_nav[component], start, end)
                usd_return = (
                    period_return(align_single_curve(usd_curves[component], nav.index), start, end)
                    if component in usd_curves
                    else float("nan")
                )
                rows.append(
                    {
                        "portfolio": label,
                        "candidate": candidate,
                        "period": period,
                        "component": component,
                        "target_weight": weights.get(component, 0.0),
                        "return_contribution": component_sum / start_nav,
                        "component_total_return_krw": krw_return,
                        "component_total_return_usd": "" if component not in usd_curves else usd_return,
                        "fx_contribution_estimate": weights.get(component, 0.0) * (krw_return - usd_return)
                        if component in usd_curves
                        else 0.0,
                    }
                )
            rows.append(
                {
                    "portfolio": label,
                    "candidate": candidate,
                    "period": period,
                    "component": "FX_estimate_total",
                    "target_weight": "",
                    "return_contribution": fx_estimate,
                    "component_total_return_krw": "",
                    "component_total_return_usd": "",
                    "fx_contribution_estimate": fx_estimate,
                }
            )
            rows.append(
                {
                    "portfolio": label,
                    "candidate": candidate,
                    "period": period,
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
                    "period": period,
                    "component": "total",
                    "target_weight": 1.0,
                    "return_contribution": total_return,
                    "component_total_return_krw": total_return,
                    "component_total_return_usd": "",
                    "fx_contribution_estimate": fx_estimate,
                }
            )
    return pd.DataFrame(rows)


def build_scorecard(
    metrics: pd.DataFrame,
    stress_2022: pd.DataFrame,
    stress_2020: pd.DataFrame,
    long_history: pd.DataFrame,
    rebalance_frequency: pd.DataFrame,
) -> pd.DataFrame:
    metric_idx = metrics.set_index("candidate")
    stress_2022_idx = stress_2022.set_index("candidate")
    stress_2020_idx = stress_2020.set_index("candidate")
    qqq_catastrophic = long_history_catastrophic(long_history)
    rows = []
    for label, candidate in FOCUS.items():
        score = 0
        reasons = []
        sharpe = float(metric_idx.loc[candidate, "sharpe"])
        cagr = float(metric_idx.loc[candidate, "cagr"])
        mdd = float(metric_idx.loc[candidate, "max_drawdown"])
        return_2022 = float(stress_2022_idx.loc[candidate, "calendar_year_return_krw"])
        covid_mdd = float(stress_2020_idx.loc[candidate, "daily_mdd"])
        freq_slice = rebalance_frequency.loc[rebalance_frequency["candidate"].eq(candidate)]
        freq_sharpe_range = float(freq_slice["sharpe"].max() - freq_slice["sharpe"].min())

        if sharpe >= 1.15:
            score += 2
            reasons.append("Sharpe>=1.15")
        if cagr >= 0.12:
            score += 2
            reasons.append("CAGR>=12%")
        else:
            score -= 2
            reasons.append("defensive(CAGR<12%)")
        if mdd <= -0.25:
            score -= 2
            reasons.append("MDD warning")
        else:
            score += 1
            reasons.append("MDD within warning line")
        if return_2022 <= -0.20:
            score -= 2
            reasons.append("2022 stress penalty")
        elif return_2022 <= -0.15:
            score -= 1
            reasons.append("2022 mild penalty")
        else:
            score += 1
            reasons.append("2022 resilient")
        if covid_mdd <= -0.25:
            score -= 1
            reasons.append("COVID MDD penalty")
        if freq_sharpe_range <= 0.04:
            score += 1
            reasons.append("frequency robust")
        if qqq_catastrophic and PORTFOLIOS[candidate].get("SPY", 0.0) > 0.0:
            score += 1
            reasons.append("SPY included under long-history penalty")
        elif qqq_catastrophic and PORTFOLIOS[candidate].get("SPY", 0.0) == 0.0:
            score -= 1
            reasons.append("QQQ-heavy long-history penalty")
        rows.append(
            {
                "portfolio": label,
                "candidate": candidate,
                "weights": weights_to_text(PORTFOLIOS[candidate]),
                "score": score,
                "sharpe": sharpe,
                "cagr": cagr,
                "max_drawdown": mdd,
                "return_2022": return_2022,
                "covid_mdd": covid_mdd,
                "frequency_sharpe_range": freq_sharpe_range,
                "reasons": "; ".join(reasons),
            }
        )
    return pd.DataFrame(rows).sort_values(["score", "sharpe"], ascending=[False, False]).reset_index(drop=True)


def long_history_catastrophic(long_history: pd.DataFrame) -> bool:
    required = {"status", "portfolio", "period", "max_drawdown"}
    if long_history.empty or not required.issubset(long_history.columns):
        return False
    computed = long_history.loc[
        long_history["status"].eq("computed")
        & long_history["portfolio"].isin(["L01_QQQ100", "L03_QQQ50_SPY50"])
        & long_history["period"].isin(["dot_com_2000_2002", "gfc_2008"])
    ]
    if computed.empty:
        return False
    return bool((computed["max_drawdown"] <= -0.45).any())


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
        return "I003.5-A"
    if candidate in GRID_B:
        return "I003.5-B"
    return "unknown"


def label_for_candidate(candidate: str) -> str:
    for label, value in FOCUS.items():
        if value == candidate:
            return label
    return candidate


def weights_to_text(weights: dict[str, float]) -> str:
    return "/".join(f"{component}{int(round(weight * 100))}" for component, weight in weights.items())


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0.0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def frontier_shape(frontier: pd.DataFrame) -> str:
    sharpe = frontier["sharpe"].tolist()
    cagr = frontier["cagr"].tolist()
    mdd = frontier["max_drawdown"].tolist()
    sharpe_non_decreasing = all(right >= left for left, right in zip(sharpe, sharpe[1:], strict=False))
    cagr_non_increasing = all(right <= left for left, right in zip(cagr, cagr[1:], strict=False))
    mdd_improves = all(right >= left for left, right in zip(mdd, mdd[1:], strict=False))
    if sharpe_non_decreasing and cagr_non_increasing and mdd_improves:
        return "단조 frontier: IEF 증가에 따라 Sharpe/MDD는 개선되고 CAGR은 하락"
    return "plateau/비단조 frontier: 일부 구간에서 Sharpe 또는 MDD 개선이 둔화"


def verdict(scorecard: pd.DataFrame, stress_2022: pd.DataFrame, long_history: pd.DataFrame) -> tuple[str, str]:
    best = scorecard.iloc[0]
    p07 = stress_2022.set_index("candidate").loc[FOCUS["P07"], "calendar_year_return_krw"]
    p08 = stress_2022.set_index("candidate").loc[FOCUS["P08"], "calendar_year_return_krw"]
    significant_2022 = abs(float(p07) - float(p08)) >= 0.05
    long_skipped = not long_history.empty and set(long_history.get("status", [])) == {"skipped"}
    if long_skipped:
        next_step = "I003.6에서 long-history만 별도 재시도 후 I004 등록"
    else:
        next_step = "I004 final candidate registration 진행"
    note = "2022 P07/P08 차이는 significant" if significant_2022 else "2022 P07/P08 차이는 5pp 미만"
    if "IEF30" in str(best["portfolio"]):
        recommendation = (
            f"{best['portfolio']}는 stress-balance 진단 leader이나 final promote 금지; "
            "P07/P08 anchor를 유지"
        )
    else:
        recommendation = f"{best['portfolio']}를 I004 후보 anchor로 우선 검토 ({best['candidate']})"
    return f"{recommendation}; {note}", next_step


def write_report(
    metrics: pd.DataFrame,
    frontier_a: pd.DataFrame,
    frontier_b: pd.DataFrame,
    rebalance_frequency: pd.DataFrame,
    stress_2020: pd.DataFrame,
    stress_2022: pd.DataFrame,
    stress_2021_2022: pd.DataFrame,
    spike_exclusion: pd.DataFrame,
    subperiod: pd.DataFrame,
    long_history: pd.DataFrame,
    contribution: pd.DataFrame,
    scorecard: pd.DataFrame,
    fx: pd.DataFrame,
) -> None:
    rec, next_step = verdict(scorecard, stress_2022, long_history)
    focus_candidates = list(FOCUS.values())
    p07_return_2022 = float(stress_2022.set_index("candidate").loc[FOCUS["P07"], "calendar_year_return_krw"])
    p08_return_2022 = float(stress_2022.set_index("candidate").loc[FOCUS["P08"], "calendar_year_return_krw"])
    long_history_text = summarize_long_history(long_history)

    lines = [
        "# I003.5 — Static Allocation Frontier",
        "",
        "## 방법",
        "",
        "- I001.6/I003과 동일한 daily NAV 재구성: quarterly rebalance + daily mark-to-market.",
        "- D013/H001 strategy와 `engine.py`는 수정하지 않았다.",
        "- Grid의 새 best 후보는 final 승격하지 않고 multi-metric balance만 평가한다.",
        "- 2022 stress는 binary pass/fail이 아니라 penalty로 반영했다.",
        f"- 기간: {START_DATE.date()}부터 {END_DATE.date()}까지.",
        f"- USDKRW latest observation used: {fx['date'].max().date()} at {fx['usdkrw'].iloc[-1]}.",
        "",
        "## Frontier shape (단조 vs plateau)",
        "",
        f"- A frontier: {frontier_shape(frontier_a)}.",
        f"- B frontier: {frontier_shape(frontier_b)}.",
        "",
        "### I003.5-A P07-style IEF frontier",
        "",
        markdown_table(frontier_a, ["candidate", "weights", "cagr", "sharpe", "max_drawdown", "positive_years"]),
        "",
        "### I003.5-B P08-style IEF frontier",
        "",
        markdown_table(frontier_b, ["candidate", "weights", "cagr", "sharpe", "max_drawdown", "positive_years"]),
        "",
        "## Rebalance frequency 효과",
        "",
        "- 아래 4 후보 모두 monthly/quarterly/semiannual/annual로 재계산했다.",
        "- P07의 성과가 특정 rebalance 주기 artifact인지 확인하는 진단이다.",
        "",
        markdown_table(rebalance_frequency, ["portfolio", "frequency", "cagr", "sharpe", "max_drawdown"]),
        "",
        "## 2022 vs COVID stress trade-off",
        "",
        f"- P07 2022 KRW return: {p07_return_2022:.6f}.",
        f"- P08 2022 KRW return: {p08_return_2022:.6f}.",
        f"- P07/P08 2022 차이: {p08_return_2022 - p07_return_2022:.6f}.",
        "",
        "### 2020 COVID",
        "",
        markdown_table(
            stress_2020.loc[stress_2020["candidate"].isin(focus_candidates)],
            ["candidate", "daily_mdd", "recovery_date", "QQQ_return_contribution", "SPY_return_contribution", "H001_return_contribution", "IEF_return_contribution"],
        ),
        "",
        "### 2022 rate shock",
        "",
        markdown_table(
            stress_2022.loc[stress_2022["candidate"].isin(focus_candidates)],
            ["candidate", "calendar_year_return_krw", "QQQ_return_contribution", "SPY_return_contribution", "H001_return_contribution", "IEF_return_contribution"],
        ),
        "",
        "### 2021-2022 drawdown",
        "",
        markdown_table(
            stress_2021_2022,
            ["portfolio", "peak_date", "trough_date", "peak_to_trough_mdd", "drawdown_length_days", "recovery_date"],
        ),
        "",
        "## Long-history 결과",
        "",
        f"- {long_history_text}",
        "",
        markdown_table(
            long_history.head(18),
            [column for column in ["status", "portfolio", "period", "cagr", "sharpe", "max_drawdown", "reason"] if column in long_history.columns],
        ),
        "",
        "## 2025 spike exclusion",
        "",
        markdown_table(
            spike_exclusion.loc[spike_exclusion["candidate"].isin(focus_candidates)],
            ["candidate", "cagr", "sharpe", "max_drawdown", "mdd_peak_date", "mdd_trough_date"],
        ),
        "",
        "## Subperiod split",
        "",
        markdown_table(
            subperiod.loc[subperiod["candidate"].isin(focus_candidates)],
            ["candidate", "period", "cagr", "sharpe", "max_drawdown", "mdd_length_days"],
        ),
        "",
        "## Contribution attribution",
        "",
        markdown_table(
            contribution.loc[contribution["component"].isin(["QQQ", "SPY", "H001", "IEF", "FX_estimate_total", "rebalance_effect", "total"])],
            ["portfolio", "period", "component", "target_weight", "return_contribution", "fx_contribution_estimate"],
        ),
        "",
        "## Multi-metric 최종 후보 선정",
        "",
        "- Highest Sharpe 자동 선택은 하지 않았다.",
        "- CAGR < 12%는 defensive portfolio로 분류한다.",
        "- MDD가 -25% 이하이면 warning으로 표시한다.",
        "- Daily Sharpe >= 1.15, 2022 stress, long-history, frequency robustness, explainability를 함께 점수화했다.",
        "",
        markdown_table(scorecard, ["portfolio", "score", "sharpe", "cagr", "max_drawdown", "return_2022", "covid_mdd", "reasons"]),
        "",
        "## Champion candidate 추천 + 근거",
        "",
        f"- Verdict: {rec}.",
        "- 이 추천은 grid best 승격이 아니며, IEF30 후보는 diagnostic leader여도 final promote하지 않는다.",
        f"- 진행 권고: {next_step}.",
        "",
        "## Files",
        "",
        "- frontier_a_p07_style.csv",
        "- frontier_b_p08_style.csv",
        "- rebalance_frequency.csv",
        "- stress_2020_covid.csv",
        "- stress_2022_rate_shock.csv",
        "- stress_2021_2022_drawdown.csv",
        "- spike_exclusion_2025.csv",
        "- subperiod_split.csv",
        "- long_history_us_core.csv",
        "- contribution_attribution.csv",
        "- daily_metrics_all_candidates.csv",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_long_history(long_history: pd.DataFrame) -> str:
    if long_history.empty:
        return "long-history 결과 없음"
    if "status" in long_history.columns and set(long_history["status"]) == {"skipped"}:
        return str(long_history.iloc[0].get("reason", "long-history skipped"))
    computed = long_history.loc[long_history.get("status", pd.Series(dtype=str)).eq("computed")]
    if computed.empty:
        return "long-history 계산 가능한 구간이 제한되어 대부분 skip됨"
    worst = computed.sort_values("max_drawdown").iloc[0]
    return (
        f"computed; worst drawdown은 {worst['portfolio']} / {worst['period']} "
        f"MDD {worst['max_drawdown']:.6f}"
    )


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if not columns:
        return ""
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
