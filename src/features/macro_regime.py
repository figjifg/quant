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
CURVE_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "regime_score",
    "regime_on",
)
USDCNY_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "USDCNY_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_USDCNY",
    "regime_score",
    "regime_on",
)
BRENT_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "Brent_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "regime_score",
    "regime_on",
)
COPPER_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "Brent_yoy",
    "Copper_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_Copper",
    "regime_score",
    "regime_on",
)
THREE_SIGNAL_NAMES = ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy")
FOUR_SIGNAL_NAMES = (*THREE_SIGNAL_NAMES, "us_2_10_curve")
FIVE_USDCNY_SIGNAL_NAMES = (*FOUR_SIGNAL_NAMES, "usdcny_yoy")
FIVE_BRENT_SIGNAL_NAMES = (*FOUR_SIGNAL_NAMES, "brent_yoy")
SIX_COPPER_SIGNAL_NAMES = (*FIVE_BRENT_SIGNAL_NAMES, "copper_yoy")
FIVE_SIGNAL_NAMES = FIVE_USDCNY_SIGNAL_NAMES


def build_macro_regime_daily(
    trading_dates: pd.Series | pd.Index | list[pd.Timestamp] | list[str],
    *,
    macro_data_dir: str,
    yoy_lookback: int = 252,
    vix_short_window: int = 60,
    vix_long_window: int = 240,
    on_threshold: int = 2,
    macro_signals: tuple[str, ...] | list[str] = THREE_SIGNAL_NAMES,
) -> pd.DataFrame:
    """Build the macro regime on KRX trading dates.

    The default preserves C003/C004's three-signal regime. C005 opts into the
    fourth US 2-10y curve signal, C006 opts into a five-signal USDCNY variant,
    C008 opts into a different five-signal Brent variant, and C010 opts into
    a six-signal Brent plus copper variant through ``macro_signals``.
    """
    if yoy_lookback <= 0:
        raise ValueError("yoy_lookback must be positive.")
    if vix_short_window <= 0 or vix_long_window <= 0:
        raise ValueError("VIX windows must be positive.")
    if vix_short_window > vix_long_window:
        raise ValueError("vix_short_window cannot exceed vix_long_window.")
    signal_names = tuple(macro_signals)
    allowed_signals = (
        THREE_SIGNAL_NAMES,
        FOUR_SIGNAL_NAMES,
        FIVE_USDCNY_SIGNAL_NAMES,
        FIVE_BRENT_SIGNAL_NAMES,
        SIX_COPPER_SIGNAL_NAMES,
    )
    if signal_names not in allowed_signals:
        raise ValueError(
            f"macro_signals must be one of {allowed_signals}; "
            f"got {signal_names}."
        )

    aligned = align_macro_factors_to_korean_signal_dates(trading_dates, macro_data_dir)
    aligned = aligned.sort_values("signal_date").reset_index(drop=True)

    usdkrw = pd.to_numeric(aligned["dexkous_usdkrw"], errors="coerce").ffill(limit=5)
    vix = pd.to_numeric(aligned["vix"], errors="coerce").ffill(limit=5)
    dxy = pd.to_numeric(aligned["dxy"], errors="coerce").ffill(limit=5)
    dgs2 = pd.to_numeric(aligned["dgs2"], errors="coerce").ffill(limit=5)
    dgs10 = pd.to_numeric(aligned["dgs10"], errors="coerce").ffill(limit=5)
    usdcny = pd.to_numeric(aligned["dexchus_usdcny"], errors="coerce").ffill(limit=5)
    brent = pd.to_numeric(aligned["brent"], errors="coerce").ffill(limit=5)
    copper = pd.to_numeric(aligned["copper"], errors="coerce").ffill()

    result = pd.DataFrame({"signal_date": aligned["signal_date"]})
    result["USDKRW_yoy"] = usdkrw / usdkrw.shift(yoy_lookback) - 1.0
    result["VIX_60d_avg"] = vix.rolling(vix_short_window, min_periods=vix_short_window).mean()
    result["VIX_240d_avg"] = vix.rolling(vix_long_window, min_periods=vix_long_window).mean()
    result["DXY_yoy"] = dxy / dxy.shift(yoy_lookback) - 1.0
    result["US_2_10_curve_spread"] = dgs10 - dgs2
    result["USDCNY_yoy"] = usdcny / usdcny.shift(yoy_lookback) - 1.0
    result["Brent_yoy"] = brent / brent.shift(yoy_lookback) - 1.0
    result["Copper_yoy"] = copper / copper.shift(yoy_lookback) - 1.0

    result["favorable_USDKRW"] = result["USDKRW_yoy"].le(0.0)
    result["favorable_VIX"] = result["VIX_60d_avg"].le(result["VIX_240d_avg"])
    result["favorable_DXY"] = result["DXY_yoy"].le(0.0)
    result["favorable_US_2_10_curve"] = result["US_2_10_curve_spread"].gt(0.0)
    result["favorable_USDCNY"] = result["USDCNY_yoy"].le(0.0)
    result["favorable_Brent"] = result["Brent_yoy"].le(0.0)
    result["favorable_Copper"] = result["Copper_yoy"].gt(0.0)

    value_columns = ["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy"]
    favorable_columns = ["favorable_USDKRW", "favorable_VIX", "favorable_DXY"]
    output_columns = REGIME_COLUMNS
    if signal_names == FOUR_SIGNAL_NAMES:
        value_columns.append("US_2_10_curve_spread")
        favorable_columns.append("favorable_US_2_10_curve")
        output_columns = CURVE_REGIME_COLUMNS
    elif signal_names == FIVE_USDCNY_SIGNAL_NAMES:
        value_columns.extend(["US_2_10_curve_spread", "USDCNY_yoy"])
        favorable_columns.extend(["favorable_US_2_10_curve", "favorable_USDCNY"])
        output_columns = USDCNY_REGIME_COLUMNS
    elif signal_names == FIVE_BRENT_SIGNAL_NAMES:
        value_columns.extend(["US_2_10_curve_spread", "Brent_yoy"])
        favorable_columns.extend(["favorable_US_2_10_curve", "favorable_Brent"])
        output_columns = BRENT_REGIME_COLUMNS
    elif signal_names == SIX_COPPER_SIGNAL_NAMES:
        value_columns.extend(["US_2_10_curve_spread", "Brent_yoy", "Copper_yoy"])
        favorable_columns.extend(["favorable_US_2_10_curve", "favorable_Brent", "favorable_Copper"])
        output_columns = COPPER_REGIME_COLUMNS

    complete = result[value_columns].notna().all(axis=1)
    if signal_names == THREE_SIGNAL_NAMES:
        result.loc[~complete, favorable_columns] = False
    result["regime_score"] = result[favorable_columns].sum(axis=1).astype(int)
    result.loc[~complete, "regime_score"] = pd.NA
    result["regime_score"] = result["regime_score"].astype("Int64")
    result["regime_on"] = result["regime_score"].ge(on_threshold).fillna(False).astype(bool)

    return result.loc[:, list(output_columns)]


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
