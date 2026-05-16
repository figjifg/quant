from __future__ import annotations

import pandas as pd

from src.data.macro_factors import align_macro_factors_to_korean_signal_dates


REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "regime_score",
    "regime_on",
)


def build_macro_regime_daily(
    trading_dates: pd.Series | pd.Index | list[pd.Timestamp] | list[str],
    *,
    macro_data_dir: str,
    yoy_lookback: int = 252,
    vix_short_window: int = 60,
    vix_long_window: int = 240,
    on_threshold: int = 2,
) -> pd.DataFrame:
    """Build the C003 three-signal macro regime on KRX trading dates."""
    if yoy_lookback <= 0:
        raise ValueError("yoy_lookback must be positive.")
    if vix_short_window <= 0 or vix_long_window <= 0:
        raise ValueError("VIX windows must be positive.")
    if vix_short_window > vix_long_window:
        raise ValueError("vix_short_window cannot exceed vix_long_window.")

    aligned = align_macro_factors_to_korean_signal_dates(trading_dates, macro_data_dir)
    aligned = aligned.sort_values("signal_date").reset_index(drop=True)

    usdkrw = pd.to_numeric(aligned["dexkous_usdkrw"], errors="coerce").ffill(limit=5)
    vix = pd.to_numeric(aligned["vix"], errors="coerce").ffill(limit=5)
    dxy = pd.to_numeric(aligned["dxy"], errors="coerce").ffill(limit=5)

    result = pd.DataFrame({"signal_date": aligned["signal_date"]})
    result["USDKRW_yoy"] = usdkrw / usdkrw.shift(yoy_lookback) - 1.0
    result["VIX_60d_avg"] = vix.rolling(vix_short_window, min_periods=vix_short_window).mean()
    result["VIX_240d_avg"] = vix.rolling(vix_long_window, min_periods=vix_long_window).mean()
    result["DXY_yoy"] = dxy / dxy.shift(yoy_lookback) - 1.0

    result["favorable_USDKRW"] = result["USDKRW_yoy"].le(0.0)
    result["favorable_VIX"] = result["VIX_60d_avg"].le(result["VIX_240d_avg"])
    result["favorable_DXY"] = result["DXY_yoy"].le(0.0)

    complete = result[["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy"]].notna().all(axis=1)
    result.loc[~complete, ["favorable_USDKRW", "favorable_VIX", "favorable_DXY"]] = False
    result["regime_score"] = result[["favorable_USDKRW", "favorable_VIX", "favorable_DXY"]].sum(axis=1).astype(int)
    result.loc[~complete, "regime_score"] = pd.NA
    result["regime_score"] = result["regime_score"].astype("Int64")
    result["regime_on"] = result["regime_score"].ge(on_threshold).fillna(False).astype(bool)

    return result.loc[:, list(REGIME_COLUMNS)]


def monthly_regime_log(daily_regime: pd.DataFrame) -> pd.DataFrame:
    """Select the last available KRX trading date in each calendar month."""
    _require_columns(daily_regime, ("signal_date",), "daily_regime")
    data = daily_regime.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data = data.sort_values("signal_date").reset_index(drop=True)
    month_key = data["signal_date"].dt.to_period("M")
    return data.loc[data.groupby(month_key)["signal_date"].idxmax()].reset_index(drop=True)


def quarterly_regime_log(daily_regime: pd.DataFrame) -> pd.DataFrame:
    """Select the last available KRX trading date in completed calendar quarters."""
    _require_columns(daily_regime, ("signal_date",), "daily_regime")
    data = daily_regime.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data = data.loc[data["signal_date"].dt.month.isin((3, 6, 9, 12))].copy()
    data = data.sort_values("signal_date").reset_index(drop=True)
    quarter_key = data["signal_date"].dt.to_period("Q")
    return data.loc[data.groupby(quarter_key)["signal_date"].idxmax()].reset_index(drop=True)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
