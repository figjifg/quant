from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PlaceboConfig:
    n_trials: int
    random_seed: int


def _rng(seed: int):
    import numpy as np

    return np.random.default_rng(seed)


def date_matched_random(signal_dates, n_per_date, universe: pd.DataFrame, seed: int = 0) -> pd.DataFrame:
    rng = _rng(seed)
    date_col = "date" if "date" in universe.columns else "날짜"
    ticker_col = "ticker" if "ticker" in universe.columns else "종목코드"
    data = universe[[date_col, ticker_col]].dropna().copy()
    data[date_col] = pd.to_datetime(data[date_col]).dt.normalize()
    rows = []
    counts = n_per_date if isinstance(n_per_date, dict) else {pd.Timestamp(d).normalize(): int(n_per_date) for d in signal_dates}
    for date, count in counts.items():
        date = pd.Timestamp(date).normalize()
        choices = data.loc[data[date_col].eq(date), ticker_col].astype(str).unique()
        if len(choices) == 0:
            continue
        picked = rng.choice(choices, size=min(int(count), len(choices)), replace=False)
        rows.extend({"signal_date": date, "ticker": ticker, "placebo_type": "date_matched"} for ticker in picked)
    return pd.DataFrame(rows)


def drop_bucket_matched_random(signal_events: pd.DataFrame, all_returns: pd.DataFrame, bucket_size: float = 0.01, seed: int = 0) -> pd.DataFrame:
    rng = _rng(seed)
    date_col = "date" if "date" in all_returns.columns else "날짜"
    ticker_col = "ticker" if "ticker" in all_returns.columns else "종목코드"
    ret_col = "ret_1d" if "ret_1d" in all_returns.columns else "return"
    pool = all_returns[[date_col, ticker_col, ret_col]].dropna().copy()
    pool["bucket"] = (pool[ret_col] / bucket_size).round().astype(int)
    event_ret_col = ret_col if ret_col in signal_events.columns else "signal_return"
    rows = []
    for event in signal_events.itertuples(index=False):
        event_return = float(getattr(event, event_ret_col))
        bucket = round(event_return / bucket_size)
        candidates = pool.loc[pool["bucket"].eq(bucket)]
        if candidates.empty:
            continue
        picked = candidates.iloc[int(rng.integers(0, len(candidates)))]
        rows.append({"signal_date": picked[date_col], "ticker": str(picked[ticker_col]), "placebo_type": "drop_bucket_matched", "bucket": bucket})
    return pd.DataFrame(rows)


def time_shift_placebo(signal_dates, shift_days: int, universe: pd.DataFrame) -> pd.DataFrame:
    date_col = "date" if "date" in universe.columns else "날짜"
    ticker_col = "ticker" if "ticker" in universe.columns else "종목코드"
    dates = sorted(pd.to_datetime(universe[date_col]).dropna().dt.normalize().unique())
    shifted = {}
    for date in pd.to_datetime(pd.Series(signal_dates)).dt.normalize().unique():
        if date not in dates:
            continue
        idx = dates.index(date) + shift_days
        if 0 <= idx < len(dates):
            shifted[pd.Timestamp(date)] = pd.Timestamp(dates[idx])
    rows = []
    data = universe[[date_col, ticker_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col]).dt.normalize()
    for original, new_date in shifted.items():
        for ticker in data.loc[data[date_col].eq(original), ticker_col].astype(str).unique():
            rows.append({"signal_date": new_date, "ticker": ticker, "placebo_type": "time_shift", "original_signal_date": original})
    return pd.DataFrame(rows)


def stock_matched_placebo(signal_events: pd.DataFrame, seed: int = 0) -> pd.DataFrame:
    rng = _rng(seed)
    date_col = "signal_date" if "signal_date" in signal_events.columns else ("date" if "date" in signal_events.columns else "날짜")
    ticker_col = "ticker" if "ticker" in signal_events.columns else "종목코드"
    rows = []
    for ticker, group in signal_events.groupby(ticker_col, sort=False):
        dates = pd.to_datetime(group[date_col]).dt.normalize().dropna().unique()
        if len(dates) == 0:
            continue
        sampled = rng.choice(dates, size=len(group), replace=True)
        rows.extend({"signal_date": pd.Timestamp(date), "ticker": str(ticker), "placebo_type": "stock_matched"} for date in sampled)
    return pd.DataFrame(rows)


def build_date_matched_placebos(signals: pd.DataFrame, tradable_universe: pd.DataFrame, config: PlaceboConfig) -> pd.DataFrame:
    date_col = "signal_date" if "signal_date" in signals.columns else "date"
    counts = pd.to_datetime(signals[date_col]).dt.normalize().value_counts().to_dict()
    frames = []
    for trial in range(config.n_trials):
        frame = date_matched_random(counts.keys(), counts, tradable_universe, config.random_seed + trial)
        frame["trial"] = trial
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def summarize_placebo_distribution(placebo_results: pd.DataFrame) -> pd.DataFrame:
    if placebo_results.empty:
        return pd.DataFrame(columns=["metric", "mean", "p05", "p50", "p95"])
    numeric = placebo_results.select_dtypes("number")
    rows = []
    for column in numeric.columns:
        rows.append(
            {
                "metric": column,
                "mean": float(numeric[column].mean()),
                "p05": float(numeric[column].quantile(0.05)),
                "p50": float(numeric[column].quantile(0.50)),
                "p95": float(numeric[column].quantile(0.95)),
            }
        )
    return pd.DataFrame(rows)
