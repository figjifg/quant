from __future__ import annotations

import pandas as pd

from src.data.macro_factors import align_macro_factors_to_korean_signal_dates


def stress_filter_scalars(
    signal_dates: pd.Series | pd.Index | list[object],
    *,
    macro_data_dir: str,
    market_breadth: pd.DataFrame,
    trading_dates: pd.Series | pd.Index | list[object] | None = None,
    z_window: int = 60,
    usdkrw_yoy_lookback_days: int = 252,
    kospi_vol_window: int = 60,
) -> pd.DataFrame:
    """Return signal-date stress exposure scalars using data available through T.

    VIX uses the existing FRED after-U.S.-close alignment, so a Korean signal
    date T sees VIX observations from T-1 or earlier. USDKRW is aligned through
    Korean date T, and KOSPI realized vol uses cap_weighted_return through T.
    Callers apply the resulting scalar only to T+1 or later execution weights.
    """
    if z_window <= 1:
        raise ValueError("z_window must be greater than 1.")
    if usdkrw_yoy_lookback_days <= 0:
        raise ValueError("usdkrw_yoy_lookback_days must be positive.")
    if kospi_vol_window <= 1:
        raise ValueError("kospi_vol_window must be greater than 1.")
    _require_columns(market_breadth, ("date", "cap_weighted_return"), "market_breadth")

    dates = pd.DataFrame({"signal_date": pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()})
    dates = dates.drop_duplicates().sort_values("signal_date").reset_index(drop=True)
    if dates.empty:
        return _empty_scalars()
    if trading_dates is None:
        calculation_dates = dates.copy()
    else:
        calculation_dates = pd.DataFrame(
            {"signal_date": pd.to_datetime(pd.Series(trading_dates), errors="raise").dt.normalize()}
        )
        calculation_dates = calculation_dates.drop_duplicates().sort_values("signal_date").reset_index(drop=True)
        calculation_dates = calculation_dates.loc[
            calculation_dates["signal_date"].le(dates["signal_date"].max())
        ].reset_index(drop=True)

    aligned = align_macro_factors_to_korean_signal_dates(calculation_dates["signal_date"], input_dir=macro_data_dir)
    aligned = aligned.sort_values("signal_date").reset_index(drop=True)
    data = calculation_dates.merge(aligned.loc[:, ["signal_date", "vix", "dexkous_usdkrw"]], on="signal_date", how="left")
    data["vix"] = pd.to_numeric(data["vix"], errors="coerce").ffill(limit=5)
    data["usdkrw"] = pd.to_numeric(data["dexkous_usdkrw"], errors="coerce").ffill(limit=5)

    breadth = market_breadth.loc[:, ["date", "cap_weighted_return"]].copy()
    breadth["signal_date"] = pd.to_datetime(breadth["date"], errors="raise").dt.normalize()
    breadth = breadth.sort_values("signal_date").reset_index(drop=True)
    breadth["cap_weighted_return"] = pd.to_numeric(breadth["cap_weighted_return"], errors="coerce")
    breadth["KOSPI_realized_vol_60d"] = breadth["cap_weighted_return"].rolling(
        window=kospi_vol_window,
        min_periods=kospi_vol_window,
    ).std(ddof=1)

    data = data.merge(
        breadth.loc[:, ["signal_date", "KOSPI_realized_vol_60d"]],
        on="signal_date",
        how="left",
        validate="one_to_one",
    )
    data["USDKRW_yoy"] = data["usdkrw"] / data["usdkrw"].shift(usdkrw_yoy_lookback_days) - 1.0
    data["VIX_z"] = _rolling_zscore(data["vix"], z_window)
    data["USDKRW_z"] = _rolling_zscore(data["USDKRW_yoy"], z_window)
    data["KOSPI_vol_z"] = _rolling_zscore(data["KOSPI_realized_vol_60d"], z_window)
    data["stress_score"] = data.loc[:, ["VIX_z", "USDKRW_z", "KOSPI_vol_z"]].mean(axis=1, skipna=False)
    data["exposure_scalar"] = stress_exposure_scalar(data["stress_score"])
    data["z_window"] = int(z_window)
    data["usdkrw_yoy_lookback_days"] = int(usdkrw_yoy_lookback_days)
    data["kospi_vol_window"] = int(kospi_vol_window)
    data = dates.merge(data, on="signal_date", how="left", validate="one_to_one")
    return data.loc[
        :,
        [
            "signal_date",
            "vix",
            "usdkrw",
            "USDKRW_yoy",
            "KOSPI_realized_vol_60d",
            "VIX_z",
            "USDKRW_z",
            "KOSPI_vol_z",
            "stress_score",
            "z_window",
            "usdkrw_yoy_lookback_days",
            "kospi_vol_window",
            "exposure_scalar",
        ],
    ]


def stress_exposure_scalar(stress_score: pd.Series) -> pd.Series:
    score = pd.to_numeric(stress_score, errors="coerce")
    scalar = 1.0 - 0.5 * (score - 1.0)
    scalar = scalar.where(score.gt(1.0), 1.0)
    scalar = scalar.where(score.lt(2.0), 0.5)
    scalar = scalar.where(score.notna(), 1.0)
    return scalar.clip(lower=0.5, upper=1.0).fillna(1.0).astype("float64")


def apply_stress_filter_to_weights(
    candidates: pd.DataFrame,
    scalars: pd.DataFrame,
    *,
    base_weight: float | None = None,
) -> pd.DataFrame:
    """Multiply candidate target weights by the signal-date stress scalar."""
    if candidates.empty:
        data = candidates.copy()
        if "target_weight_before_stress" not in data.columns:
            data["target_weight_before_stress"] = pd.Series(dtype="float64")
        data["target_weight"] = pd.Series(dtype="float64")
        data["stress_score"] = pd.Series(dtype="float64")
        data["exposure_scalar"] = pd.Series(dtype="float64")
        return data
    _require_columns(candidates, ("signal_date",), "candidates")
    _require_columns(scalars, ("signal_date", "stress_score", "exposure_scalar"), "scalars")

    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    if "target_weight" in data.columns:
        data["target_weight_before_stress"] = pd.to_numeric(data["target_weight"], errors="raise")
    elif base_weight is not None:
        data["target_weight_before_stress"] = float(base_weight)
    else:
        raise ValueError("candidates must contain target_weight unless base_weight is provided.")

    scalar_data = scalars.loc[:, ["signal_date", "stress_score", "exposure_scalar"]].copy()
    scalar_data["signal_date"] = pd.to_datetime(scalar_data["signal_date"], errors="raise").dt.normalize()
    data = data.merge(scalar_data, on="signal_date", how="left", validate="many_to_one")
    data["exposure_scalar"] = pd.to_numeric(data["exposure_scalar"], errors="coerce").fillna(1.0)
    data["target_weight"] = data["target_weight_before_stress"] * data["exposure_scalar"]
    return data


def _rolling_zscore(values: pd.Series, window: int) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    mean = numeric.rolling(window=window, min_periods=window).mean()
    std = numeric.rolling(window=window, min_periods=window).std(ddof=1)
    zscore = (numeric - mean) / std
    return zscore.where(std.gt(0.0))


def _empty_scalars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": pd.Series(dtype="datetime64[ns]"),
            "vix": pd.Series(dtype="float64"),
            "usdkrw": pd.Series(dtype="float64"),
            "USDKRW_yoy": pd.Series(dtype="float64"),
            "KOSPI_realized_vol_60d": pd.Series(dtype="float64"),
            "VIX_z": pd.Series(dtype="float64"),
            "USDKRW_z": pd.Series(dtype="float64"),
            "KOSPI_vol_z": pd.Series(dtype="float64"),
            "stress_score": pd.Series(dtype="float64"),
            "z_window": pd.Series(dtype="int64"),
            "usdkrw_yoy_lookback_days": pd.Series(dtype="int64"),
            "kospi_vol_window": pd.Series(dtype="int64"),
            "exposure_scalar": pd.Series(dtype="float64"),
        }
    )


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
