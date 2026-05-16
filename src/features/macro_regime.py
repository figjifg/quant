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
KR10Y_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "regime_score",
    "regime_on",
)
KR_RATES_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "US3M_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "KR3M_yoy_change",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_KR3M",
    "regime_score",
    "regime_on",
)
CPI_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "regime_score",
    "regime_on",
)
PPI_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "US_PPI_yoy",
    "US_PPI_decel",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "favorable_US_PPI",
    "regime_score",
    "regime_on",
)
UNRATE_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "US_PPI_yoy",
    "US_PPI_decel",
    "US_UNRATE_yoy_change",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "favorable_US_PPI",
    "favorable_US_UNRATE",
    "regime_score",
    "regime_on",
)
KR_CPI_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "US_PPI_yoy",
    "US_PPI_decel",
    "KR_CPI_yoy",
    "KR_CPI_decel",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "favorable_US_PPI",
    "favorable_KR_CPI",
    "regime_score",
    "regime_on",
)
KR_EXPORTS_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "US_PPI_yoy",
    "US_PPI_decel",
    "KR_exports_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "favorable_US_PPI",
    "favorable_KR_exports",
    "regime_score",
    "regime_on",
)
US_M2_REGIME_COLUMNS = (
    "signal_date",
    "USDKRW_yoy",
    "VIX_60d_avg",
    "VIX_240d_avg",
    "DXY_yoy",
    "US_2_10_curve_spread",
    "US10Y_yoy_change",
    "Brent_yoy",
    "KR10Y_yoy_change",
    "US_CPI_yoy",
    "US_CPI_decel",
    "US_PPI_yoy",
    "US_PPI_decel",
    "US_M2_yoy",
    "favorable_USDKRW",
    "favorable_VIX",
    "favorable_DXY",
    "favorable_US_2_10_curve",
    "favorable_Brent",
    "favorable_KR10Y",
    "favorable_US_CPI",
    "favorable_US_PPI",
    "favorable_US_M2",
    "regime_score",
    "regime_on",
)
THREE_SIGNAL_NAMES = ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy")
FOUR_SIGNAL_NAMES = (*THREE_SIGNAL_NAMES, "us_2_10_curve")
FIVE_USDCNY_SIGNAL_NAMES = (*FOUR_SIGNAL_NAMES, "usdcny_yoy")
FIVE_BRENT_SIGNAL_NAMES = (*FOUR_SIGNAL_NAMES, "brent_yoy")
SIX_COPPER_SIGNAL_NAMES = (*FIVE_BRENT_SIGNAL_NAMES, "copper_yoy")
SIX_KR10Y_SIGNAL_NAMES = (*FIVE_BRENT_SIGNAL_NAMES, "kr10y_yoy_change")
SEVEN_KR_RATES_SIGNAL_NAMES = (*SIX_KR10Y_SIGNAL_NAMES, "kr3m_yoy_change")
SEVEN_CPI_SIGNAL_NAMES = (*SIX_KR10Y_SIGNAL_NAMES, "us_cpi_decel")
EIGHT_PPI_SIGNAL_NAMES = (*SEVEN_CPI_SIGNAL_NAMES, "us_ppi_decel")
NINE_UNRATE_SIGNAL_NAMES = (*EIGHT_PPI_SIGNAL_NAMES, "us_unrate_change")
NINE_KR_CPI_SIGNAL_NAMES = (*EIGHT_PPI_SIGNAL_NAMES, "kr_cpi_decel")
NINE_KR_EXPORTS_SIGNAL_NAMES = (*EIGHT_PPI_SIGNAL_NAMES, "kr_exports_yoy")
NINE_US_M2_SIGNAL_NAMES = (*EIGHT_PPI_SIGNAL_NAMES, "us_m2_yoy")
FIVE_SIGNAL_NAMES = FIVE_USDCNY_SIGNAL_NAMES
SIGNAL_VARIANTS = {
    THREE_SIGNAL_NAMES: (
        ["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy"],
        ["favorable_USDKRW", "favorable_VIX", "favorable_DXY"],
        REGIME_COLUMNS,
    ),
    FOUR_SIGNAL_NAMES: (
        ["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy", "US_2_10_curve_spread"],
        ["favorable_USDKRW", "favorable_VIX", "favorable_DXY", "favorable_US_2_10_curve"],
        CURVE_REGIME_COLUMNS,
    ),
    FIVE_USDCNY_SIGNAL_NAMES: (
        ["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy", "US_2_10_curve_spread", "USDCNY_yoy"],
        ["favorable_USDKRW", "favorable_VIX", "favorable_DXY", "favorable_US_2_10_curve", "favorable_USDCNY"],
        USDCNY_REGIME_COLUMNS,
    ),
    FIVE_BRENT_SIGNAL_NAMES: (
        ["USDKRW_yoy", "VIX_60d_avg", "VIX_240d_avg", "DXY_yoy", "US_2_10_curve_spread", "Brent_yoy"],
        ["favorable_USDKRW", "favorable_VIX", "favorable_DXY", "favorable_US_2_10_curve", "favorable_Brent"],
        BRENT_REGIME_COLUMNS,
    ),
    SIX_COPPER_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "Brent_yoy",
            "Copper_yoy",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_Copper",
        ],
        COPPER_REGIME_COLUMNS,
    ),
    SIX_KR10Y_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
        ],
        KR10Y_REGIME_COLUMNS,
    ),
    SEVEN_KR_RATES_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "US3M_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "KR3M_yoy_change",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_KR3M",
        ],
        KR_RATES_REGIME_COLUMNS,
    ),
    SEVEN_CPI_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
        ],
        CPI_REGIME_COLUMNS,
    ),
    EIGHT_PPI_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
            "US_PPI_decel",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
            "favorable_US_PPI",
        ],
        PPI_REGIME_COLUMNS,
    ),
    NINE_UNRATE_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
            "US_PPI_decel",
            "US_UNRATE_yoy_change",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
            "favorable_US_PPI",
            "favorable_US_UNRATE",
        ],
        UNRATE_REGIME_COLUMNS,
    ),
    NINE_KR_CPI_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
            "US_PPI_decel",
            "KR_CPI_decel",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
            "favorable_US_PPI",
            "favorable_KR_CPI",
        ],
        KR_CPI_REGIME_COLUMNS,
    ),
    NINE_KR_EXPORTS_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
            "US_PPI_decel",
            "KR_exports_yoy",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
            "favorable_US_PPI",
            "favorable_KR_exports",
        ],
        KR_EXPORTS_REGIME_COLUMNS,
    ),
    NINE_US_M2_SIGNAL_NAMES: (
        [
            "USDKRW_yoy",
            "VIX_60d_avg",
            "VIX_240d_avg",
            "DXY_yoy",
            "US_2_10_curve_spread",
            "US10Y_yoy_change",
            "Brent_yoy",
            "KR10Y_yoy_change",
            "US_CPI_decel",
            "US_PPI_decel",
            "US_M2_yoy",
        ],
        [
            "favorable_USDKRW",
            "favorable_VIX",
            "favorable_DXY",
            "favorable_US_2_10_curve",
            "favorable_Brent",
            "favorable_KR10Y",
            "favorable_US_CPI",
            "favorable_US_PPI",
            "favorable_US_M2",
        ],
        US_M2_REGIME_COLUMNS,
    ),
}


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
    six-signal Brent plus copper variant, C011 opts into a separate
    six-signal Brent plus KR 10y variant, C012 opts into a seven-signal
    KR 10y plus KR 3m variant, C013 opts into a seven-signal KR 10y
    plus US CPI deceleration variant, C014 opts into an eight-signal
    CPI plus PPI deceleration variant, C015 opts into a nine-signal
    CPI/PPI plus US unemployment-rate yoy-change variant, C016 opts
    into a different nine-signal variant that replaces UNRATE with Korean
    CPI deceleration, and C017 opts into a C014-plus-Korean-exports-yoy
    variant through ``macro_signals``, and C018 opts into a separate
    C014-plus-US-M2-yoy variant.
    """
    if yoy_lookback <= 0:
        raise ValueError("yoy_lookback must be positive.")
    if vix_short_window <= 0 or vix_long_window <= 0:
        raise ValueError("VIX windows must be positive.")
    if vix_short_window > vix_long_window:
        raise ValueError("vix_short_window cannot exceed vix_long_window.")
    signal_names = tuple(macro_signals)
    if signal_names not in SIGNAL_VARIANTS:
        raise ValueError(
            f"macro_signals must be one of {tuple(SIGNAL_VARIANTS)}; "
            f"got {signal_names}."
        )

    aligned = align_macro_factors_to_korean_signal_dates(trading_dates, macro_data_dir)
    aligned = aligned.sort_values("signal_date").reset_index(drop=True)

    usdkrw = pd.to_numeric(aligned["dexkous_usdkrw"], errors="coerce").ffill(limit=5)
    vix = pd.to_numeric(aligned["vix"], errors="coerce").ffill(limit=5)
    dxy = pd.to_numeric(aligned["dxy"], errors="coerce").ffill(limit=5)
    dgs2 = pd.to_numeric(aligned["dgs2"], errors="coerce").ffill(limit=5)
    dgs10 = pd.to_numeric(aligned["dgs10"], errors="coerce").ffill(limit=5)
    dgs3mo = pd.to_numeric(aligned["dgs3mo"], errors="coerce").ffill(limit=5)
    usdcny = pd.to_numeric(aligned["dexchus_usdcny"], errors="coerce").ffill(limit=5)
    brent = pd.to_numeric(aligned["brent"], errors="coerce").ffill(limit=5)
    copper = pd.to_numeric(aligned["copper"], errors="coerce").ffill()
    kr10y = pd.to_numeric(aligned["kr10y"], errors="coerce").ffill()
    kr3m = pd.to_numeric(aligned["kr3m"], errors="coerce").ffill()
    kr_cpi = pd.to_numeric(aligned["kr_cpi"], errors="coerce")

    result = pd.DataFrame({"signal_date": aligned["signal_date"]})
    result["USDKRW_yoy"] = usdkrw / usdkrw.shift(yoy_lookback) - 1.0
    result["VIX_60d_avg"] = vix.rolling(vix_short_window, min_periods=vix_short_window).mean()
    result["VIX_240d_avg"] = vix.rolling(vix_long_window, min_periods=vix_long_window).mean()
    result["DXY_yoy"] = dxy / dxy.shift(yoy_lookback) - 1.0
    result["US_2_10_curve_spread"] = dgs10 - dgs2
    result["US10Y_yoy_change"] = dgs10 - dgs10.shift(yoy_lookback)
    result["US3M_yoy_change"] = dgs3mo - dgs3mo.shift(yoy_lookback)
    result["USDCNY_yoy"] = usdcny / usdcny.shift(yoy_lookback) - 1.0
    result["Brent_yoy"] = brent / brent.shift(yoy_lookback) - 1.0
    result["Copper_yoy"] = copper / copper.shift(yoy_lookback) - 1.0
    result["KR10Y_yoy_change"] = _monthly_level_change(aligned, "kr10y", months=12)
    result["KR3M_yoy_change"] = _monthly_level_change(aligned, "kr3m", months=12)
    result["US_CPI_yoy"] = _monthly_yoy(aligned, "us_cpi", months=12)
    result["US_CPI_decel"] = _monthly_yoy_change(aligned, "us_cpi", months=12)
    result["US_PPI_yoy"] = _monthly_yoy(aligned, "us_ppi", months=12)
    result["US_PPI_decel"] = _monthly_yoy_change(aligned, "us_ppi", months=12)
    result["US_UNRATE_yoy_change"] = _monthly_level_change(aligned, "us_unrate", months=12)
    result["KR_CPI_yoy"] = kr_cpi
    result["KR_CPI_decel"] = _monthly_level_change(aligned, "kr_cpi", months=12)
    result["KR_exports_yoy"] = _monthly_yoy(aligned, "kr_exports", months=12)
    result["US_M2_yoy"] = _monthly_yoy(aligned, "us_m2", months=12)
    kr_cpi_stale = _monthly_source_age_days(aligned, "kr_cpi").gt(62)
    result.loc[kr_cpi_stale, ["KR_CPI_yoy", "KR_CPI_decel"]] = pd.NA

    result["favorable_USDKRW"] = result["USDKRW_yoy"].le(0.0)
    result["favorable_VIX"] = result["VIX_60d_avg"].le(result["VIX_240d_avg"])
    result["favorable_DXY"] = result["DXY_yoy"].le(0.0)
    result["favorable_US_2_10_curve"] = result["US_2_10_curve_spread"].gt(0.0)
    result["favorable_USDCNY"] = result["USDCNY_yoy"].le(0.0)
    result["favorable_Brent"] = result["Brent_yoy"].le(0.0)
    result["favorable_Copper"] = result["Copper_yoy"].gt(0.0)
    result["favorable_KR10Y"] = result["KR10Y_yoy_change"].le(0.0)
    result["favorable_KR3M"] = result["KR3M_yoy_change"].le(0.0)
    result["favorable_US_CPI"] = result["US_CPI_decel"].le(0.0)
    result["favorable_US_PPI"] = result["US_PPI_decel"].le(0.0)
    result["favorable_US_UNRATE"] = result["US_UNRATE_yoy_change"].ge(0.0)
    result["favorable_KR_CPI"] = result["KR_CPI_decel"].le(0.0).fillna(False)
    result["favorable_KR_exports"] = result["KR_exports_yoy"].ge(0.0)
    result["favorable_US_M2"] = result["US_M2_yoy"].ge(0.05)

    value_columns, favorable_columns, output_columns = SIGNAL_VARIANTS[signal_names]

    if signal_names == NINE_KR_CPI_SIGNAL_NAMES:
        non_kr_value_columns = [column for column in value_columns if column != "KR_CPI_decel"]
        complete = result[non_kr_value_columns].notna().all(axis=1)
    else:
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


def _monthly_level_change(aligned: pd.DataFrame, name: str, *, months: int) -> pd.Series:
    source_column = f"{name}_source_observation_date"
    _require_columns(aligned, (name, source_column), "aligned")
    data = aligned.loc[:, [source_column, name]].copy()
    data[source_column] = pd.to_datetime(data[source_column], errors="coerce")
    data[name] = pd.to_numeric(data[name], errors="coerce")
    monthly = (
        data.dropna(subset=[source_column])
        .drop_duplicates(subset=[source_column], keep="last")
        .sort_values(source_column)
        .reset_index(drop=True)
    )
    monthly = monthly.rename(columns={source_column: "base_source_observation_date", name: "base_value"})

    lookup = pd.DataFrame(
        {
            "row_order": range(len(aligned)),
            "lookup_date": pd.to_datetime(aligned[source_column], errors="coerce") - pd.DateOffset(months=months),
        }
    )
    valid_lookup = lookup.loc[lookup["lookup_date"].notna()].copy()
    output = pd.Series(pd.NA, index=range(len(aligned)), dtype="Float64")
    if valid_lookup.empty:
        return output
    matched = pd.merge_asof(
        valid_lookup.sort_values("lookup_date"),
        monthly,
        left_on="lookup_date",
        right_on="base_source_observation_date",
        direction="backward",
    ).sort_values("row_order")
    current = pd.to_numeric(aligned[name], errors="coerce").reset_index(drop=True)
    values = current.loc[matched["row_order"].to_numpy()].reset_index(drop=True) - matched["base_value"].reset_index(
        drop=True
    )
    output.loc[matched["row_order"].to_numpy()] = values.to_numpy()
    return output


def _monthly_source_age_days(aligned: pd.DataFrame, name: str) -> pd.Series:
    source_column = f"{name}_source_observation_date"
    _require_columns(aligned, ("signal_date", source_column), "aligned")
    signal_date = pd.to_datetime(aligned["signal_date"], errors="coerce")
    source_date = pd.to_datetime(aligned[source_column], errors="coerce")
    return (signal_date - source_date).dt.days.astype("Float64")


def _monthly_yoy(aligned: pd.DataFrame, name: str, *, months: int) -> pd.Series:
    source_column = f"{name}_source_observation_date"
    _require_columns(aligned, (name, source_column), "aligned")
    data = aligned.loc[:, [source_column, name]].copy()
    data[source_column] = pd.to_datetime(data[source_column], errors="coerce")
    data[name] = pd.to_numeric(data[name], errors="coerce")
    monthly = (
        data.dropna(subset=[source_column])
        .drop_duplicates(subset=[source_column], keep="last")
        .sort_values(source_column)
        .reset_index(drop=True)
    )
    monthly = monthly.rename(columns={source_column: "base_source_observation_date", name: "base_value"})

    lookup = pd.DataFrame(
        {
            "row_order": range(len(aligned)),
            "lookup_date": pd.to_datetime(aligned[source_column], errors="coerce") - pd.DateOffset(months=months),
        }
    )
    valid_lookup = lookup.loc[lookup["lookup_date"].notna()].copy()
    output = pd.Series(pd.NA, index=range(len(aligned)), dtype="Float64")
    if valid_lookup.empty:
        return output
    matched = pd.merge_asof(
        valid_lookup.sort_values("lookup_date"),
        monthly,
        left_on="lookup_date",
        right_on="base_source_observation_date",
        direction="backward",
    ).sort_values("row_order")
    current = pd.to_numeric(aligned[name], errors="coerce").reset_index(drop=True)
    values = current.loc[matched["row_order"].to_numpy()].reset_index(drop=True) / matched["base_value"].reset_index(
        drop=True
    ) - 1.0
    output.loc[matched["row_order"].to_numpy()] = values.to_numpy()
    return output


def _monthly_yoy_change(aligned: pd.DataFrame, name: str, *, months: int) -> pd.Series:
    source_column = f"{name}_source_observation_date"
    _require_columns(aligned, (name, source_column), "aligned")
    data = aligned.loc[:, [source_column, name]].copy()
    data[source_column] = pd.to_datetime(data[source_column], errors="coerce")
    data[name] = pd.to_numeric(data[name], errors="coerce")
    monthly = (
        data.dropna(subset=[source_column])
        .drop_duplicates(subset=[source_column], keep="last")
        .sort_values(source_column)
        .reset_index(drop=True)
    )
    monthly = monthly.rename(columns={source_column: "base_source_observation_date", name: "base_value"})
    lookup = pd.DataFrame(
        {
            "row_order": range(len(aligned)),
            "lookup_date": pd.to_datetime(aligned[source_column], errors="coerce") - pd.DateOffset(months=months),
            "prior_lookup_date": pd.to_datetime(aligned[source_column], errors="coerce")
            - pd.DateOffset(months=months * 2),
        }
    )
    valid_lookup = lookup.loc[lookup["lookup_date"].notna() & lookup["prior_lookup_date"].notna()].copy()
    output = pd.Series(pd.NA, index=range(len(aligned)), dtype="Float64")
    if valid_lookup.empty:
        return output
    current_base = pd.merge_asof(
        valid_lookup.sort_values("lookup_date"),
        monthly,
        left_on="lookup_date",
        right_on="base_source_observation_date",
        direction="backward",
    ).sort_values("row_order")
    prior_base = pd.merge_asof(
        valid_lookup.sort_values("prior_lookup_date"),
        monthly,
        left_on="prior_lookup_date",
        right_on="base_source_observation_date",
        direction="backward",
    ).sort_values("row_order")
    current = pd.to_numeric(aligned[name], errors="coerce").reset_index(drop=True)
    current_value = current.loc[current_base["row_order"].to_numpy()].reset_index(drop=True)
    current_base_value = current_base["base_value"].reset_index(drop=True)
    prior_base_value = prior_base["base_value"].reset_index(drop=True)
    current_yoy = current_value / current_base_value - 1.0
    prior_yoy = current_base_value / prior_base_value - 1.0
    output.loc[current_base["row_order"].to_numpy()] = (current_yoy - prior_yoy).to_numpy()
    return output
