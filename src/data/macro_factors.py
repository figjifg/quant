from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


MACRO_INPUT_DIR = Path("research_input_data/inputs/macro_features")


@dataclass(frozen=True)
class FredSeriesSpec:
    name: str
    fred_series: str
    filename: str
    timing: str
    frequency: str
    transform: str
    description: str


US_AFTER_CLOSE = "us_after_close"
KOREA_SAME_DAY = "korea_same_day"
US_MONTHLY_AFTER_MONTH_END_LAG = "us_monthly_after_month_end_lag"
KOREA_MONTHLY_AFTER_MONTH_END_LAG = "korea_monthly_after_month_end_lag"
OECD_CLI_AFTER_MONTH_END_LAG = "oecd_cli_after_month_end_lag"


FRED_SERIES: tuple[FredSeriesSpec, ...] = (
    FredSeriesSpec(
        name="vix",
        fred_series="VIXCLS",
        filename="fred_vix.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="pct_change",
        description="CBOE VIX close",
    ),
    FredSeriesSpec(
        name="dxy",
        fred_series="DTWEXBGS",
        filename="fred_dxy.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="pct_change",
        description="Nominal broad U.S. dollar index",
    ),
    FredSeriesSpec(
        name="usdjpy",
        fred_series="DEXJPUS",
        filename="fred_jpy.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="pct_change",
        description="Japanese yen to one U.S. dollar",
    ),
    FredSeriesSpec(
        name="dgs2",
        fred_series="DGS2",
        filename="fred_dgs2.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="diff",
        description="U.S. 2-year Treasury yield",
    ),
    FredSeriesSpec(
        name="dgs10",
        fred_series="DGS10",
        filename="fred_dgs10.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="diff",
        description="U.S. 10-year Treasury yield",
    ),
    FredSeriesSpec(
        name="dexchus_usdcny",
        fred_series="DEXCHUS",
        filename="fred_dexchus.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="pct_change",
        description="Chinese yuan to one U.S. dollar",
    ),
    FredSeriesSpec(
        name="baa10y_spread",
        fred_series="BAA10Y",
        filename="fred_baa10y_spread.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="diff",
        description="Moody's Baa corporate bond yield minus 10-year Treasury",
    ),
    FredSeriesSpec(
        name="us_10y_real",
        fred_series="DFII10",
        filename="fred_us_10y_real.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="level",
        description="Market yield on U.S. 10-year Treasury inflation-indexed security",
    ),
    FredSeriesSpec(
        name="us_breakeven_10y",
        fred_series="T10YIE",
        filename="fred_us_breakeven_10y.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="level",
        description="U.S. 10-year breakeven inflation rate",
    ),
    FredSeriesSpec(
        name="dgs3mo",
        fred_series="DGS3MO",
        filename="fred_dgs3mo.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="diff",
        description="U.S. 3-month Treasury yield",
    ),
    FredSeriesSpec(
        name="brent",
        fred_series="DCOILBRENTEU",
        filename="fred_brent.csv",
        timing=US_AFTER_CLOSE,
        frequency="daily",
        transform="pct_change",
        description="Crude Oil Prices: Brent Europe",
    ),
    FredSeriesSpec(
        name="copper",
        fred_series="PCOPPUSDM",
        filename="fred_copper.csv",
        timing=US_AFTER_CLOSE,
        frequency="monthly",
        transform="pct_change",
        description="Global price of copper, U.S. dollars per metric ton",
    ),
    FredSeriesSpec(
        name="kr10y",
        fred_series="IRLTLT01KRM156N",
        filename="fred_kr10y.csv",
        timing=US_AFTER_CLOSE,
        frequency="monthly",
        transform="diff",
        description="Long-term government bond yields, 10-year, Korea",
    ),
    FredSeriesSpec(
        name="jp10y",
        fred_series="IRLTLT01JPM156N",
        filename="fred_jp10y.csv",
        timing=US_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="diff",
        description="Long-term government bond yields, 10-year, Japan",
    ),
    FredSeriesSpec(
        name="kr3m",
        fred_series="IR3TIB01KRM156N",
        filename="fred_kr3m.csv",
        timing=US_AFTER_CLOSE,
        frequency="monthly",
        transform="diff",
        description="3-month interbank rate, Korea",
    ),
    FredSeriesSpec(
        name="us_cpi",
        fred_series="CPIAUCSL",
        filename="fred_us_cpi.csv",
        timing=US_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="pct_change",
        description="U.S. CPI All Urban Consumers, seasonally adjusted",
    ),
    FredSeriesSpec(
        name="us_ppi",
        fred_series="PPIACO",
        filename="fred_us_ppi.csv",
        timing=US_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="pct_change",
        description="U.S. Producer Price Index by Commodity: All Commodities",
    ),
    FredSeriesSpec(
        name="us_unrate",
        fred_series="UNRATE",
        filename="fred_us_unrate.csv",
        timing=US_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="diff",
        description="U.S. unemployment rate, seasonally adjusted",
    ),
    FredSeriesSpec(
        name="us_m2",
        fred_series="M2SL",
        filename="fred_us_m2.csv",
        timing=US_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="pct_change",
        description="U.S. M2 money stock, seasonally adjusted",
    ),
    FredSeriesSpec(
        name="kr_cpi",
        fred_series="KORCPALTT01CTGYM",
        filename="fred_kr_cpi.csv",
        timing=KOREA_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="diff",
        description="Korea CPI, total, yoy growth rate in percent",
    ),
    FredSeriesSpec(
        name="kr_exports",
        fred_series="XTEXVA01KRM664S",
        filename="fred_kr_exports.csv",
        timing=KOREA_MONTHLY_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="pct_change",
        description="Korea exports of goods, value",
    ),
    FredSeriesSpec(
        name="kr_cli",
        fred_series="KORLOLITOAASTSAM",
        filename="fred_kr_cli.csv",
        timing=OECD_CLI_AFTER_MONTH_END_LAG,
        frequency="monthly",
        transform="level",
        description="OECD Composite Leading Indicator, amplitude adjusted, Korea",
    ),
    FredSeriesSpec(
        name="dexkous_usdkrw",
        fred_series="DEXKOUS",
        filename="fred_dexkous_usdkrw.csv",
        timing=KOREA_SAME_DAY,
        frequency="daily",
        transform="pct_change",
        description="Korean won to one U.S. dollar",
    ),
)


def load_fred_series(path: str | Path, spec: FredSeriesSpec) -> pd.DataFrame:
    """Load and validate one two-column FRED CSV."""
    frame = pd.read_csv(path, encoding="utf-8-sig")
    required = {"observation_date", spec.fred_series}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{path} is missing required FRED columns: {missing}")

    result = frame.loc[:, ["observation_date", spec.fred_series]].copy()
    result = result.rename(columns={"observation_date": "observation_date", spec.fred_series: spec.name})
    result["observation_date"] = pd.to_datetime(
        result["observation_date"], errors="raise"
    ).astype("datetime64[ns]")
    result[spec.name] = pd.to_numeric(result[spec.name].replace(".", pd.NA), errors="coerce")

    if result["observation_date"].duplicated().any():
        raise ValueError(f"{path} contains duplicate observation_date rows.")

    return result.sort_values("observation_date").reset_index(drop=True)


def load_all_fred_series(input_dir: str | Path = MACRO_INPUT_DIR) -> dict[str, pd.DataFrame]:
    """Load all registered C002 FRED series without changing their timing."""
    base = Path(input_dir)
    return {spec.name: load_fred_series(base / spec.filename, spec) for spec in FRED_SERIES}


def align_macro_factors_to_korean_signal_dates(
    signal_dates: pd.Series | pd.Index | list[pd.Timestamp] | list[str],
    input_dir: str | Path = MACRO_INPUT_DIR,
) -> pd.DataFrame:
    """Align FRED values to Korean signal dates using pre-registered timing rules.

    U.S. after-close series are available to Korean signal date T only from
    observations dated T-1 or earlier. USDKRW is treated as available through
    Korean signal date T per C002.
    """
    dates = pd.Series(pd.to_datetime(signal_dates, errors="raise").unique(), name="signal_date")
    dates = dates.sort_values().reset_index(drop=True)
    aligned = pd.DataFrame({"signal_date": dates})

    for spec in FRED_SERIES:
        raw = load_fred_series(Path(input_dir) / spec.filename, spec)
        shifted = _align_one_series(aligned["signal_date"], raw, spec)
        aligned = aligned.merge(shifted, on="signal_date", how="left", validate="one_to_one")

    return aligned


def build_macro_factor_changes(aligned: pd.DataFrame) -> pd.DataFrame:
    """Convert aligned macro levels into daily changes for decomposition."""
    required = {"signal_date", *(spec.name for spec in FRED_SERIES)}
    missing = sorted(required.difference(aligned.columns))
    if missing:
        raise ValueError(f"aligned macro factors missing columns: {missing}")

    result = aligned.loc[:, ["signal_date"]].copy()
    for spec in FRED_SERIES:
        values = pd.to_numeric(aligned[spec.name], errors="coerce")
        if spec.transform == "pct_change":
            result[f"{spec.name}_ret"] = values.pct_change(fill_method=None)
        elif spec.transform == "diff":
            result[f"{spec.name}_diff"] = values.diff()
        elif spec.transform == "level":
            result[f"{spec.name}_level"] = values
        else:
            raise ValueError(f"Unsupported transform for {spec.name}: {spec.transform}")
    return result


def _align_one_series(
    signal_dates: pd.Series,
    raw: pd.DataFrame,
    spec: FredSeriesSpec,
) -> pd.DataFrame:
    targets = pd.DataFrame({"signal_date": signal_dates})
    if spec.timing == US_AFTER_CLOSE:
        targets["lookup_date"] = targets["signal_date"] - pd.Timedelta(days=1)
    elif spec.timing == KOREA_SAME_DAY:
        targets["lookup_date"] = targets["signal_date"]
    elif spec.timing in (
        US_MONTHLY_AFTER_MONTH_END_LAG,
        KOREA_MONTHLY_AFTER_MONTH_END_LAG,
        OECD_CLI_AFTER_MONTH_END_LAG,
    ):
        targets["lookup_date"] = targets["signal_date"]
    else:
        raise ValueError(f"Unsupported timing policy for {spec.name}: {spec.timing}")
    targets["lookup_date"] = targets["lookup_date"].astype("datetime64[ns]")

    source = raw.rename(columns={"observation_date": "source_observation_date"})
    source["source_observation_date"] = source["source_observation_date"].astype("datetime64[ns]")
    if spec.timing in (
        US_MONTHLY_AFTER_MONTH_END_LAG,
        KOREA_MONTHLY_AFTER_MONTH_END_LAG,
        OECD_CLI_AFTER_MONTH_END_LAG,
    ):
        lag_days = 75 if spec.timing == OECD_CLI_AFTER_MONTH_END_LAG else 14
        # OECD Korea CLI is published with roughly a two-month delay
        # (for example, January observations around late March), so use a
        # conservative month-end +75 calendar-day availability rule. Other
        # monthly series keep the pre-registered month-end +14 day lag.
        source["availability_date"] = (
            source["source_observation_date"] + pd.offsets.MonthEnd(0) + pd.Timedelta(days=lag_days)
        ).astype("datetime64[ns]")
        right_on = "availability_date"
    else:
        right_on = "source_observation_date"
    merged = pd.merge_asof(
        targets.sort_values("lookup_date"),
        source.sort_values(right_on),
        left_on="lookup_date",
        right_on=right_on,
        direction="backward",
    )
    merged = merged.sort_values("signal_date").reset_index(drop=True)
    return merged.loc[:, ["signal_date", spec.name, "source_observation_date"]].rename(
        columns={"source_observation_date": f"{spec.name}_source_observation_date"}
    )
