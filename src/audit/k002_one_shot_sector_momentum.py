from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
MACRO_DIR = ROOT / "research_input_data/inputs/macro_features"
USDKRW_PATH = MACRO_DIR / "fred_dexkous_usdkrw.csv"
H001_EQUITY_PATH = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "reports/experiments/K002_one_shot_sector_momentum"

SECTORS = ["XLE", "XLF", "XLK", "XLV", "XLP", "XLU", "XLI", "XLY", "XLB", "XLRE", "XLC"]
LOOKBACK_DAYS = 252
TOP_K = 3
BASELINE_WEIGHTS = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
PRE_2010_P08_PROXY_WEIGHTS = {"SPY": 0.29 / 0.80, "QQQ": 0.21 / 0.80, "IEF": 0.30 / 0.80}
K002_VARIANTS = {
    "K002-A": {"QQQ": 0.21, "H001": 0.20, "IEF": 0.30, "SectorRotation": 0.29},
    "K002-B": {"H001": 0.20, "IEF": 0.30, "SectorRotation": 0.50},
    "K002-C": {"SectorRotation": 1.00},
}
COMPARATOR_WEIGHTS = {
    "P08_IEF30": BASELINE_WEIGHTS,
    "SPY_100": {"SPY": 1.00},
    "QQQ_100": {"QQQ": 1.00},
    "K001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "XLP": 0.10},
    "N002-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "cash": 0.10},
}
STRESS_WINDOWS = {
    "dot_com_proxy_2002_07_2003_12": ("2002-07-01", "2003-12-31", "proxy_sector_momentum_only"),
    "gfc_proxy_2008_2009": ("2008-01-01", "2009-12-31", "proxy_sector_momentum_only"),
    "covid_2020_02_2020_03": ("2020-02-01", "2020-03-31", "exact"),
    "rate_shock_2022": ("2022-01-01", "2022-12-31", "exact"),
}
TOLERANCE = 1e-12


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    usdk = load_usdkrw()
    etf_nav = load_etf_nav_krw(("SPY", "QQQ", "IEF", "XLP"), usdk)
    sector_prices = load_sector_prices_krw(usdk)
    rotation_nav, hold_history = build_sector_rotation_nav(sector_prices, etf_nav["SPY"])
    h001 = load_h001_nav()
    cash = build_kr_cash_nav(etf_nav.index.union(h001.index))
    p08_proxy_nav = build_rebalanced_nav(etf_nav, PRE_2010_P08_PROXY_WEIGHTS)

    components = (
        etf_nav.join(h001.rename("H001"), how="outer")
        .join(cash.rename("cash"), how="outer")
        .join(rotation_nav.rename("SectorRotation"), how="outer")
        .sort_index()
        .ffill()
    )
    variant_nav = build_variant_navs(components, K002_VARIANTS)
    comparator_nav = build_variant_navs(components, COMPARATOR_WEIGHTS)
    stress_nav = pd.concat([variant_nav, comparator_nav], axis=1)
    analysis_nav = rebase_frame(
        stress_nav.loc[stress_nav.index.to_series().between(pd.Timestamp("2010-01-01"), pd.Timestamp("2026-12-31"))]
    )

    full_metrics = build_metrics_table(analysis_nav, "full_history_2010_2026")
    stress = build_stress_windows(stress_nav, rotation_nav, p08_proxy_nav)
    turnover = build_turnover_by_year(hold_history)
    delta = build_delta_vs_comparators(full_metrics, "K002-A")
    subperiod = build_subperiod_split(analysis_nav)
    spike = build_spike_exclusion(analysis_nav)
    overall = build_overall_score_ranking(stress)
    promotion = evaluate_promotion(full_metrics, stress, subperiod, spike)
    metrics = build_metrics_payload(full_metrics, stress, turnover, delta, subperiod, spike, overall, promotion)

    analysis_nav[list(K002_VARIANTS)].reset_index(names="date").to_csv(OUTPUT_DIR / "daily_nav.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    turnover.to_csv(OUTPUT_DIR / "turnover_by_year.csv", index=False)
    hold_history.to_csv(OUTPUT_DIR / "sector_hold_history.csv", index=False)
    delta.to_csv(OUTPUT_DIR / "delta_vs_baseline.csv", index=False)
    subperiod.to_csv(OUTPUT_DIR / "subperiod_split.csv", index=False)
    spike.to_csv(OUTPUT_DIR / "2025_spike_exclusion.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "overall_score_ranking.csv", index=False)
    write_config()
    write_json(metrics, OUTPUT_DIR / "metrics.json")
    write_report(full_metrics, stress, turnover, hold_history, delta, subperiod, spike, overall, promotion)


def load_usdkrw() -> pd.DataFrame:
    data = pd.read_csv(USDKRW_PATH, parse_dates=["observation_date"], na_values=["."])
    data["DEXKOUS"] = pd.to_numeric(data["DEXKOUS"], errors="coerce")
    return (
        data.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]]
        .dropna()
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
    )


def load_etf_nav_krw(tickers: tuple[str, ...], usdk: pd.DataFrame) -> pd.DataFrame:
    frames = {}
    for ticker in tickers:
        prices = load_price(ticker, etf_path(ticker))
        frame = prices.merge(usdk, on="date", how="left").sort_values("date")
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame["close_krw"] = frame["close_usd"] * frame["USDKRW"]
        series = frame.set_index("date")["close_krw"].dropna()
        frames[ticker] = series / series.iloc[0]
    return pd.DataFrame(frames).sort_index()


def load_sector_prices_krw(usdk: pd.DataFrame) -> pd.DataFrame:
    frames = {}
    for sector in SECTORS:
        prices = load_price(sector, ETF_DIR / f"yf_sector_{sector}.csv")
        frame = prices.merge(usdk, on="date", how="left").sort_values("date")
        frame["USDKRW"] = frame["USDKRW"].interpolate(method="linear").ffill()
        frame[sector] = frame["close_usd"] * frame["USDKRW"]
        frames[sector] = frame.set_index("date")[sector].dropna()
    return pd.DataFrame(frames).sort_index()


def load_price(ticker: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing local ETF file for {ticker}: {path}")
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Close"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    return (
        pd.DataFrame({"date": data["Date"], "close_usd": pd.to_numeric(data["Close"], errors="coerce")})
        .dropna(subset=["date", "close_usd"])
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
    )


def etf_path(ticker: str) -> Path:
    sector_path = ETF_DIR / f"yf_sector_{ticker}.csv"
    if sector_path.exists():
        return sector_path
    long_path = ETF_DIR / f"yf_{ticker}_long.csv"
    if long_path.exists():
        return long_path
    return ETF_DIR / f"yf_{ticker}.csv"


def load_h001_nav() -> pd.Series:
    data = pd.read_csv(H001_EQUITY_PATH, parse_dates=["date"])
    required = {"date", "net_value"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{H001_EQUITY_PATH} missing columns: {sorted(missing)}")
    series = (
        pd.DataFrame({"date": data["date"], "H001": pd.to_numeric(data["net_value"], errors="coerce")})
        .dropna(subset=["date", "H001"])
        .sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
        .set_index("date")["H001"]
    )
    return series / series.iloc[0]


def build_kr_cash_nav(dates: pd.Index) -> pd.Series:
    rates = pd.read_csv(MACRO_DIR / "fred_kr_short_rate.csv", parse_dates=["observation_date"], na_values=["."])
    column = "IR3TIB01KRM156N"
    rates[column] = pd.to_numeric(rates[column], errors="coerce")
    rates = rates.dropna(subset=[column]).sort_values("observation_date")
    frame = pd.DataFrame({"date": pd.DatetimeIndex(dates).sort_values().unique()})
    aligned = pd.merge_asof(
        frame,
        rates[["observation_date", column]],
        left_on="date",
        right_on="observation_date",
        direction="backward",
    )
    daily_return = (1.0 + aligned[column] / 100.0 / 12.0) ** (12.0 / 252.0) - 1.0
    nav = (1.0 + daily_return.fillna(0.0)).cumprod()
    nav.index = aligned["date"]
    return nav / nav.iloc[0]


def build_sector_rotation_nav(
    sector_prices: pd.DataFrame,
    warmup_nav: pd.Series,
) -> tuple[pd.Series, pd.DataFrame]:
    prices = sector_prices.sort_index()
    returns = prices.pct_change(fill_method=None)
    calendar = prices.index
    rebalance_dates = first_trading_days_by_quarter(calendar)
    warmup_returns = warmup_nav.reindex(calendar).ffill().pct_change().fillna(0.0)

    current_weights: dict[str, float] = {}
    previous_target: dict[str, float] = {}
    value = 1.0
    rows = []
    hold_rows = []

    for date in calendar:
        if date in rebalance_dates:
            signal_date = previous_trading_day(calendar, date)
            if signal_date is not None:
                ranked = rank_sectors(prices, signal_date)
                if len(ranked) >= TOP_K:
                    top = ranked[:TOP_K]
                    current_weights = {sector: 1.0 / TOP_K for sector in top}
                    turnover = one_way_turnover(previous_target, current_weights)
                    hold_rows.append(
                        {
                            "execution_date": date.date().isoformat(),
                            "signal_date": signal_date.date().isoformat(),
                            "quarter": date.to_period("Q").strftime("Q%q-%Y"),
                            "available_sector_count": int(len(ranked)),
                            "rank_1": top[0],
                            "rank_2": top[1],
                            "rank_3": top[2],
                            "rank_1_return_252d": float(momentum_return(prices[top[0]], signal_date)),
                            "rank_2_return_252d": float(momentum_return(prices[top[1]], signal_date)),
                            "rank_3_return_252d": float(momentum_return(prices[top[2]], signal_date)),
                            "turnover_one_way": turnover,
                        }
                    )
                    previous_target = current_weights.copy()
        if current_weights:
            daily_return = sum(float(returns.at[date, sector]) * weight for sector, weight in current_weights.items())
            if math.isnan(daily_return):
                daily_return = 0.0
        else:
            daily_return = float(warmup_returns.loc[date])
        value *= 1.0 + daily_return
        rows.append((date, value))

    nav = pd.Series(dict(rows), name="SectorRotation").sort_index()
    nav = nav / nav.iloc[0]
    hold_history = pd.DataFrame(hold_rows)
    return nav, hold_history


def first_trading_days_by_quarter(calendar: pd.DatetimeIndex) -> set[pd.Timestamp]:
    data = pd.Series(calendar, index=calendar)
    quarter = data.index.to_period("Q")
    first_by_quarter = data.groupby(quarter).min()
    return set(first_by_quarter.iloc[1:])


def previous_trading_day(calendar: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | None:
    loc = calendar.get_loc(date)
    if isinstance(loc, slice) or isinstance(loc, pd.Series):
        raise ValueError("Calendar index must be unique")
    if loc == 0:
        return None
    return calendar[loc - 1]


def rank_sectors(prices: pd.DataFrame, signal_date: pd.Timestamp) -> list[str]:
    values = []
    for sector in SECTORS:
        value = momentum_return(prices[sector], signal_date)
        if not pd.isna(value):
            values.append((sector, float(value)))
    values.sort(key=lambda item: (-item[1], item[0]))
    return [sector for sector, _ in values]


def momentum_return(series: pd.Series, signal_date: pd.Timestamp) -> float:
    history = series.loc[:signal_date].dropna()
    if len(history) <= LOOKBACK_DAYS:
        return float("nan")
    return float(history.iloc[-1] / history.iloc[-1 - LOOKBACK_DAYS] - 1.0)


def one_way_turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    keys = sorted(set(previous).union(current))
    if not previous:
        return 1.0
    return 0.5 * sum(abs(previous.get(key, 0.0) - current.get(key, 0.0)) for key in keys)


def build_variant_navs(components: pd.DataFrame, variants: dict[str, dict[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        {variant: build_rebalanced_nav(components, weights) for variant, weights in variants.items()}
    ).sort_index()


def build_rebalanced_nav(component_nav: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    missing = sorted(set(weights).difference(component_nav.columns))
    if missing:
        raise ValueError(f"Missing components for portfolio: {missing}")
    components = component_nav[list(weights)].dropna(how="all").ffill().dropna(subset=list(weights))
    returns = components.pct_change().fillna(0.0)
    values = []
    sleeve_values: dict[str, float] | None = None
    rebalance_dates = first_trading_days_by_quarter(pd.DatetimeIndex(returns.index))

    for date, row in returns.iterrows():
        if sleeve_values is None:
            sleeve_values = weights.copy()
        elif date in rebalance_dates:
            portfolio_value = sum(sleeve_values.values())
            sleeve_values = {ticker: portfolio_value * weight for ticker, weight in weights.items()}
        sleeve_values = {ticker: value * (1.0 + float(row[ticker])) for ticker, value in sleeve_values.items()}
        values.append((date, sum(sleeve_values.values())))

    nav = pd.Series(dict(values), name="nav").sort_index()
    return nav / nav.iloc[0]


def build_metrics_table(nav_frame: pd.DataFrame, period: str) -> pd.DataFrame:
    rows = []
    for name, nav in nav_frame.items():
        rows.append(metrics_for_nav(name, period, nav.dropna()))
    return pd.DataFrame(rows)


def rebase_frame(nav_frame: pd.DataFrame) -> pd.DataFrame:
    data = nav_frame.sort_index().copy()
    rebased = {}
    for column in data.columns:
        series = data[column].dropna()
        if series.empty:
            rebased[column] = data[column]
        else:
            rebased[column] = data[column] / series.iloc[0]
    return pd.DataFrame(rebased, index=data.index)


def build_stress_windows(nav_frame: pd.DataFrame, rotation_nav: pd.Series, p08_proxy_nav: pd.Series) -> pd.DataFrame:
    rows = []
    for window_name, (start, end, measurement_type) in STRESS_WINDOWS.items():
        start_date = pd.Timestamp(start)
        end_date = pd.Timestamp(end)
        for name in nav_frame.columns:
            source = nav_frame[name]
            row_measurement_type = measurement_type
            if measurement_type == "proxy_sector_momentum_only" and name.startswith("K002"):
                source = rotation_nav
            elif measurement_type == "proxy_sector_momentum_only" and name == "P08_IEF30":
                source = p08_proxy_nav
                row_measurement_type = "proxy_p08_us_core"
            elif measurement_type == "proxy_sector_momentum_only":
                row_measurement_type = "exact_us_etf"
            window = source.loc[source.index.to_series().between(start_date, end_date)].dropna()
            if window.empty:
                continue
            row = metrics_for_nav(name, window_name, window / window.iloc[0])
            row["measurement_type"] = row_measurement_type
            rows.append(row)
    return pd.DataFrame(rows)


def metrics_for_nav(name: str, period: str, nav: pd.Series) -> dict[str, object]:
    returns = nav.pct_change().fillna(0.0)
    drawdown = nav / nav.cummax() - 1.0
    trough_date = drawdown.idxmin()
    peak_date = nav.loc[:trough_date].idxmax()
    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1.0 / 365.25)
    return {
        "variant": name,
        "period": period,
        "start_date": nav.index[0].date().isoformat(),
        "end_date": nav.index[-1].date().isoformat(),
        "n_observations": int(nav.shape[0]),
        "total_return": total_return,
        "cagr": float((1.0 + total_return) ** (1.0 / years) - 1.0),
        "sharpe": safe_divide(float(returns.mean()) * math.sqrt(252.0), float(returns.std())),
        "annualized_volatility": float(returns.std()) * math.sqrt(252.0),
        "max_drawdown": float(drawdown.min()),
        "mdd_peak_date": peak_date.date().isoformat(),
        "mdd_trough_date": trough_date.date().isoformat(),
    }


def build_turnover_by_year(hold_history: pd.DataFrame) -> pd.DataFrame:
    data = hold_history.copy()
    data["year"] = pd.to_datetime(data["execution_date"]).dt.year
    rows = []
    for variant, sleeve_weight in {"K002-A": 0.29, "K002-B": 0.50, "K002-C": 1.00}.items():
        grouped = data.groupby("year", sort=True)["turnover_one_way"].agg(["mean", "sum", "count"]).reset_index()
        grouped["variant"] = variant
        grouped["sector_sleeve_weight"] = sleeve_weight
        grouped["quarterly_avg_turnover"] = grouped["mean"] * sleeve_weight
        grouped["annual_turnover"] = grouped["sum"] * sleeve_weight
        grouped["rebalance_count"] = grouped["count"].astype(int)
        rows.append(grouped[["variant", "year", "sector_sleeve_weight", "rebalance_count", "quarterly_avg_turnover", "annual_turnover"]])
    return pd.concat(rows, ignore_index=True)


def build_delta_vs_comparators(full_metrics: pd.DataFrame, variant: str) -> pd.DataFrame:
    target = full_metrics.loc[full_metrics["variant"].eq(variant)].iloc[0]
    rows = []
    for comparator in COMPARATOR_WEIGHTS:
        base = full_metrics.loc[full_metrics["variant"].eq(comparator)].iloc[0]
        rows.append(
            {
                "variant": variant,
                "comparator": comparator,
                "delta_total_return_pp": (target["total_return"] - base["total_return"]) * 100.0,
                "delta_cagr_pp": (target["cagr"] - base["cagr"]) * 100.0,
                "delta_sharpe": target["sharpe"] - base["sharpe"],
                "delta_mdd_pp": (target["max_drawdown"] - base["max_drawdown"]) * 100.0,
                "variant_cagr": target["cagr"],
                "comparator_cagr": base["cagr"],
                "variant_sharpe": target["sharpe"],
                "comparator_sharpe": base["sharpe"],
                "variant_mdd": target["max_drawdown"],
                "comparator_mdd": base["max_drawdown"],
            }
        )
    return pd.DataFrame(rows)


def build_subperiod_split(nav_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    periods = {
        "2010_2017": ("2010-01-01", "2017-12-31"),
        "2018_2026": ("2018-01-01", "2026-12-31"),
    }
    for period, (start, end) in periods.items():
        sliced = nav_frame.loc[nav_frame.index.to_series().between(pd.Timestamp(start), pd.Timestamp(end))]
        rows.extend(build_metrics_table(rebase_frame(sliced), period).to_dict(orient="records"))
    return pd.DataFrame(rows)


def build_spike_exclusion(nav_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in nav_frame.columns:
        nav = nav_frame[column].dropna()
        returns = nav.pct_change().fillna(0.0)
        returns = returns.loc[returns.index.year != 2025]
        synthetic = (1.0 + returns).cumprod()
        synthetic = synthetic / synthetic.iloc[0]
        rows.append(metrics_for_nav(column, "exclude_2025_daily_returns", synthetic))
    return pd.DataFrame(rows)


def build_overall_score_ranking(stress: pd.DataFrame) -> pd.DataFrame:
    k002 = stress.loc[stress["variant"].str.startswith("K002")].copy()
    baseline = stress.loc[stress["variant"].eq("P08_IEF30"), ["period", "total_return", "max_drawdown"]].rename(
        columns={"total_return": "baseline_total_return", "max_drawdown": "baseline_max_drawdown"}
    )
    rows = k002.merge(baseline, on="period", how="left", validate="many_to_one")
    rows["delta_return_pp"] = (rows["total_return"] - rows["baseline_total_return"]) * 100.0
    rows["delta_mdd_pp"] = (rows["max_drawdown"] - rows["baseline_max_drawdown"]) * 100.0
    rows["return_improved"] = rows["delta_return_pp"] > TOLERANCE
    rows["mdd_improved"] = rows["delta_mdd_pp"] > TOLERANCE
    scores = score_rows(rows, family="K002")

    previous = []
    for path in [
        ROOT / "reports/experiments/N005_multi_stress_comparison/overall_score_ranking.csv",
        ROOT / "reports/experiments/K001_static_sector_diversifier/overall_score_ranking.csv",
    ]:
        if path.exists():
            data = pd.read_csv(path)
            if "family" not in data.columns:
                data["family"] = "N-family"
            if path.name == "overall_score_ranking.csv" and "K001_static_sector_diversifier" in str(path):
                data = data.loc[data["family"].eq("K001")]
            previous.append(data.drop(columns=["overall_rank"], errors="ignore"))
    combined = pd.concat([*previous, scores], ignore_index=True, sort=False)
    combined = combined.sort_values(
        ["mdd_score_pp", "return_score_pp", "balanced_score_pp", "variant"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    combined.insert(0, "overall_rank", range(1, len(combined) + 1))
    return combined


def score_rows(rows: pd.DataFrame, family: str) -> pd.DataFrame:
    rows["return_worsened"] = rows["delta_return_pp"] < -TOLERANCE
    rows["mdd_worsened"] = rows["delta_mdd_pp"] < -TOLERANCE
    scores = (
        rows.groupby("variant", sort=False)
        .agg(
            return_score_pp=("delta_return_pp", "mean"),
            mdd_score_pp=("delta_mdd_pp", "mean"),
            stress_count=("period", "count"),
            return_improved_count=("return_improved", "sum"),
            mdd_improved_count=("mdd_improved", "sum"),
            return_worsened_count=("return_worsened", "sum"),
            mdd_worsened_count=("mdd_worsened", "sum"),
        )
        .reset_index()
    )
    scores["balanced_score_pp"] = (scores["return_score_pp"] + scores["mdd_score_pp"]) / 2.0
    scores["family"] = family
    return scores


def evaluate_promotion(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
) -> dict[str, object]:
    full_pass = better_on_return_mdd_sharpe(full_metrics, "K002-A", "P08_IEF30")
    stress_pass = all_stress_improved(stress, "K002-A", "P08_IEF30")
    spike_pass = better_on_return_mdd_sharpe(spike, "K002-A", "P08_IEF30")
    subperiod_pass = all(
        better_on_return_mdd_sharpe(subperiod.loc[subperiod["period"].eq(period)], "K002-A", "P08_IEF30")
        for period in ("2010_2017", "2018_2026")
    )
    return {
        "return_mdd_sharpe_all_better_than_p08": full_pass,
        "four_stress_all_improved": stress_pass,
        "no_2025_spike_dependency": spike_pass,
        "subperiod_all_superior": subperiod_pass,
        "promotion_pass": bool(full_pass and stress_pass and spike_pass and subperiod_pass),
        "direct_promote_p08_ief30": False,
        "role": "backlog_candidate_library",
    }


def better_on_return_mdd_sharpe(metrics: pd.DataFrame, variant: str, comparator: str) -> bool:
    left = metrics.loc[metrics["variant"].eq(variant)].iloc[0]
    right = metrics.loc[metrics["variant"].eq(comparator)].iloc[0]
    return bool(
        left["cagr"] > right["cagr"] + TOLERANCE
        and left["max_drawdown"] > right["max_drawdown"] + TOLERANCE
        and left["sharpe"] > right["sharpe"] + TOLERANCE
    )


def all_stress_improved(stress: pd.DataFrame, variant: str, comparator: str) -> bool:
    left = stress.loc[stress["variant"].eq(variant), ["period", "total_return", "max_drawdown"]]
    right = stress.loc[stress["variant"].eq(comparator), ["period", "total_return", "max_drawdown"]].rename(
        columns={"total_return": "base_return", "max_drawdown": "base_mdd"}
    )
    merged = left.merge(right, on="period", how="inner", validate="one_to_one")
    return bool(((merged["total_return"] > merged["base_return"] + TOLERANCE) & (merged["max_drawdown"] > merged["base_mdd"] + TOLERANCE)).all())


def build_metrics_payload(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    turnover: pd.DataFrame,
    delta: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
    overall: pd.DataFrame,
    promotion: dict[str, object],
) -> dict[str, object]:
    return {
        "experiment": "K002_one_shot_sector_momentum",
        "purpose": "one-shot sector momentum under strict budget",
        "guardrails": {
            "lookback_grid": False,
            "top_k_grid": False,
            "weighting_optimization": False,
            "sector_risk_filter": False,
            "sector_universe_selection": False,
            "p08_ief30_modified": False,
            "direct_promotion": False,
            "role": "backlog_candidate_library",
        },
        "rule": {
            "universe": SECTORS,
            "lookback_trading_days": LOOKBACK_DAYS,
            "ranking": "12 month KRW return",
            "top_k": TOP_K,
            "weighting": "equal weight within sector rotation sleeve",
            "rebalance": "quarter end plus one trading day",
            "warmup": "SPY held until first valid 252 trading day signal",
        },
        "variants": K002_VARIANTS,
        "full_history": records_for_json(full_metrics),
        "stress_windows": records_for_json(stress),
        "turnover_by_year": records_for_json(turnover),
        "delta_vs_baseline": records_for_json(delta),
        "subperiod_split": records_for_json(subperiod),
        "spike_exclusion": records_for_json(spike),
        "overall_score_ranking": records_for_json(overall),
        "k003_promotion_rule": promotion,
    }


def write_config() -> None:
    lines = [
        "experiment: K002_one_shot_sector_momentum",
        "status: generated",
        "candidate_status: backlog_candidate_library",
        "base_candidate: P08_IEF30",
        "direct_promote_p08_ief30: false",
        "mode: one_shot_sector_momentum",
        "search: none",
        "nav_basis: gross",
        "tax_model: none",
        "currency: KRW",
        "fx_policy: USDKRW linear interpolation on ETF trading dates, then forward-fill",
        "rule:",
        f"  universe: [{', '.join(SECTORS)}]",
        f"  lookback_trading_days: {LOOKBACK_DAYS}",
        "  ranking: 12_month_return_krw",
        f"  top_k: {TOP_K}",
        "  top_k_weight: equal",
        "  rebalance: quarter_end_plus_1_trading_day",
        "  partial_inception: rank only sectors with valid 252 trading day history",
        "  warmup: SPY held until first valid signal",
        "  reversal: false",
        "  risk_filter: false",
        "variants:",
    ]
    for variant, weights in K002_VARIANTS.items():
        lines.append(f"  {variant}:")
        lines.extend(f"    {ticker}: {weight:.10f}" for ticker, weight in weights.items())
    lines.extend(
        [
            "comparators:",
            "  - P08_IEF30",
            "  - SPY_100",
            "  - QQQ_100",
            "  - K001-B",
            "  - N002-B",
            "prohibited:",
            "  lookback_grid: true",
            "  top_k_grid: true",
            "  weighting_optimization: true",
            "  sector_risk_filter: true",
            "  external_network: true",
            "  engine_modification: true",
            "sources:",
            f"  etf_dir: {ETF_DIR.relative_to(ROOT)}",
            f"  usdk_rw_file: {USDKRW_PATH.relative_to(ROOT)}",
            f"  h001_equity_curve: {H001_EQUITY_PATH.relative_to(ROOT)}",
            "",
        ]
    )
    (OUTPUT_DIR / "config.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    full_metrics: pd.DataFrame,
    stress: pd.DataFrame,
    turnover: pd.DataFrame,
    hold_history: pd.DataFrame,
    delta: pd.DataFrame,
    subperiod: pd.DataFrame,
    spike: pd.DataFrame,
    overall: pd.DataFrame,
    promotion: dict[str, object],
) -> None:
    top_holds = most_common_holds(hold_history)
    p08_delta = delta.loc[delta["comparator"].eq("P08_IEF30")].iloc[0]
    spy_delta = delta.loc[delta["comparator"].eq("SPY_100")].iloc[0]
    pass_text = "통과" if promotion["promotion_pass"] else "미통과"
    lines = [
        "# K002 One-shot Sector Momentum",
        "",
        "Status: GENERATED BY `src.audit.k002_one_shot_sector_momentum`",
        "",
        "## 범위",
        "",
        "- K002는 단 하나의 규칙만 실행했다: 252 거래일 KRW momentum / Top 3 equal weight / quarterly.",
        "- Lookback grid / Top-K grid / weighting optimization / sector risk filter / sector universe 선택은 실행하지 않았다.",
        "- `P08_IEF30` 직접 promote X. K002 결과는 backlog candidate library 전용이다.",
        "- Gross NAV, 비용 X, 로컬 USDKRW 보간 KRW 환산 기준이다.",
        "",
        "## 3 K002 Variant 종합 Metric",
        "",
        table_for_report(full_metrics.loc[full_metrics["variant"].str.startswith("K002")], ["variant", "total_return", "cagr", "sharpe", "max_drawdown", "start_date", "end_date"]),
        "",
        "## P08_IEF30 / SPY / QQQ / K001-B / N002-B 대비",
        "",
        f"- K002-A vs P08_IEF30: CAGR {p08_delta['delta_cagr_pp']:.4f}pp, Sharpe {p08_delta['delta_sharpe']:.4f}, MDD {p08_delta['delta_mdd_pp']:.4f}pp.",
        f"- K002-A vs SPY 100%: CAGR {spy_delta['delta_cagr_pp']:.4f}pp, Sharpe {spy_delta['delta_sharpe']:.4f}, MDD {spy_delta['delta_mdd_pp']:.4f}pp.",
        "",
        table_for_report(delta, ["variant", "comparator", "delta_cagr_pp", "delta_sharpe", "delta_mdd_pp", "variant_cagr", "comparator_cagr", "variant_mdd", "comparator_mdd"]),
        "",
        "## 4 Stress 결과",
        "",
        table_for_report(stress.loc[stress["variant"].isin(["K002-A", "K002-B", "K002-C", "P08_IEF30", "SPY_100", "QQQ_100", "K001-B", "N002-B"])], ["variant", "period", "measurement_type", "total_return", "sharpe", "max_drawdown"]),
        "",
        "## Subperiod / 2025 Spike",
        "",
        table_for_report(subperiod.loc[subperiod["variant"].isin(["K002-A", "P08_IEF30"])], ["variant", "period", "cagr", "sharpe", "max_drawdown"]),
        "",
        table_for_report(spike.loc[spike["variant"].isin(["K002-A", "P08_IEF30"])], ["variant", "period", "cagr", "sharpe", "max_drawdown"]),
        "",
        "## K-family + N-family 종합 Ranking",
        "",
        table_for_report(overall, ["overall_rank", "variant", "family", "return_score_pp", "mdd_score_pp", "balanced_score_pp", "return_improved_count", "mdd_improved_count"]),
        "",
        "## Sector Hold History 요약",
        "",
        f"- 가장 자주 hold 된 sector top 3: {', '.join(top_holds)}.",
        "",
        table_for_report(turnover.groupby("variant", as_index=False).agg(quarterly_avg_turnover=("quarterly_avg_turnover", "mean"), annual_turnover=("annual_turnover", "mean")), ["variant", "quarterly_avg_turnover", "annual_turnover"]),
        "",
        "## K003 Promotion Rule 평가",
        "",
        f"- Return + MDD + Sharpe 모두 P08_IEF30보다 명확히 좋음: {'통과' if promotion['return_mdd_sharpe_all_better_than_p08'] else '미통과'}",
        f"- 4 stress 모두 개선: {'통과' if promotion['four_stress_all_improved'] else '미통과'}",
        f"- 2025 spike 의존도 증가 없음: {'통과' if promotion['no_2025_spike_dependency'] else '미통과'}",
        f"- Subperiod 모두 우수: {'통과' if promotion['subperiod_all_superior'] else '미통과'}",
        f"- K003 promotion: {pass_text}",
        "",
        "## Verdict",
        "",
        f"- K002가 SPY 100%보다 명확히 우수한가: {'예' if spy_delta['delta_cagr_pp'] > 0 and spy_delta['delta_sharpe'] > 0 and spy_delta['delta_mdd_pp'] > 0 else '아니오'}.",
        f"- P08_IEF30 + K002가 P08_IEF30보다 우수한가: {'예' if p08_delta['delta_cagr_pp'] > 0 and p08_delta['delta_sharpe'] > 0 and p08_delta['delta_mdd_pp'] > 0 else '아니오'}.",
        "- K-family 전체 = backlog only (지피티 결정).",
        f"- 다음 진행: {'J-family (EM) 진행 권고' if not promotion['promotion_pass'] else 'K002는 backlog 후보로만 보관하고 J-family 진행 전 별도 승인 필요'}.",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def most_common_holds(hold_history: pd.DataFrame) -> list[str]:
    counts = pd.concat([hold_history["rank_1"], hold_history["rank_2"], hold_history["rank_3"]]).value_counts()
    return [f"{sector} ({int(count)}회)" for sector, count in counts.head(3).items()]


def table_for_report(data: pd.DataFrame, columns: list[str]) -> str:
    rows = data.loc[:, columns].copy()
    for column in rows.columns:
        if pd.api.types.is_float_dtype(rows[column]):
            rows[column] = rows[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.6f}")
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join("" if pd.isna(value) else str(value) for value in row) + " |"
        for row in rows.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


def records_for_json(data: pd.DataFrame) -> list[dict[str, object]]:
    records = []
    for record in data.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if pd.isna(value):
                clean[key] = None
            elif hasattr(value, "item"):
                clean[key] = value.item()
            else:
                clean[key] = value
        records.append(clean)
    return records


def write_json(payload: dict[str, object], path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0 or math.isnan(denominator):
        return None
    return numerator / denominator


if __name__ == "__main__":
    main()
