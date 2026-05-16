from __future__ import annotations

import pandas as pd


BASE_COLUMNS = ("execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5")
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")
RELATIVE_COLUMNS = (
    "fnv_5_z",
    "inv_5_z",
    "combined_flow_5_z",
    "fnv_5_rel",
    "inv_5_rel",
    "combined_flow_5_rel",
)


def build_relative_flow_features(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    *,
    min_count: int = 30,
) -> pd.DataFrame:
    """Attach same-date cross-sectional relative flow features.

    Cross-sectional moments are computed only over rows present in the supplied
    execution universe for each signal_date. Rows outside that universe retain
    NaN relative features, making entry filters false and exits conservative.
    """
    if min_count <= 0:
        raise ValueError("min_count must be positive.")
    _require_columns(flow_features, BASE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    result = flow_features.copy()
    result["signal_date"] = pd.to_datetime(result["signal_date"], errors="raise").astype("datetime64[ns]")
    result["execution_date"] = pd.to_datetime(result["execution_date"], errors="raise").astype("datetime64[ns]")
    result["종목코드"] = result["종목코드"].astype("string")
    for column in RELATIVE_COLUMNS:
        result[column] = pd.NA

    eligible = _eligible_feature_rows(result, universe)
    if eligible.empty:
        return result

    relative = eligible.copy()
    for base_column in ("fnv_5", "inv_5", "combined_flow_5"):
        relative[f"{base_column}_z"] = _zscore_by_signal_date(relative, base_column, min_count)
        relative[f"{base_column}_rel"] = _median_diff_by_signal_date(relative, base_column, min_count)

    result = result.merge(
        relative.loc[:, [*UNIVERSE_COLUMNS, *RELATIVE_COLUMNS]],
        on=list(UNIVERSE_COLUMNS),
        how="left",
        validate="one_to_one",
        suffixes=("", "_computed"),
    )
    for column in RELATIVE_COLUMNS:
        result[column] = result[f"{column}_computed"]
        result = result.drop(columns=f"{column}_computed")
    return result


def cross_sectional_std_diagnostic(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> pd.DataFrame:
    """Return per-signal-date std diagnostics over the eligible universe."""
    _require_columns(flow_features, BASE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")
    eligible = _eligible_feature_rows(flow_features, universe)
    if eligible.empty:
        return pd.DataFrame(
            {
                "signal_date": pd.Series(dtype="datetime64[ns]"),
                "universe_count": pd.Series(dtype="int64"),
                "fnv_5_std": pd.Series(dtype="float64"),
                "inv_5_std": pd.Series(dtype="float64"),
            }
        )

    grouped = eligible.groupby("signal_date", sort=True)
    return (
        grouped.agg(
            universe_count=("종목코드", "size"),
            fnv_5_std=("fnv_5", lambda values: values.std(ddof=1)),
            inv_5_std=("inv_5", lambda values: values.std(ddof=1)),
        )
        .reset_index()
        .sort_values("signal_date")
        .reset_index(drop=True)
    )


def _eligible_feature_rows(flow_features: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    features = flow_features.loc[:, list(BASE_COLUMNS)].copy()
    features["signal_date"] = pd.to_datetime(features["signal_date"], errors="raise").astype("datetime64[ns]")
    features["execution_date"] = pd.to_datetime(features["execution_date"], errors="raise").astype("datetime64[ns]")
    features["종목코드"] = features["종목코드"].astype("string")

    universe_keys = universe.loc[:, list(UNIVERSE_COLUMNS)].copy()
    universe_keys["signal_date"] = pd.to_datetime(universe_keys["signal_date"], errors="raise").astype("datetime64[ns]")
    universe_keys["execution_date"] = pd.to_datetime(
        universe_keys["execution_date"],
        errors="raise",
    ).astype("datetime64[ns]")
    universe_keys["종목코드"] = universe_keys["종목코드"].astype("string")
    if universe_keys.duplicated(list(UNIVERSE_COLUMNS)).any():
        raise ValueError("universe contains duplicate rows for execution_date, signal_date, 종목코드.")

    return universe_keys.merge(features, on=list(UNIVERSE_COLUMNS), how="inner", validate="one_to_one")


def _zscore_by_signal_date(data: pd.DataFrame, column: str, min_count: int) -> pd.Series:
    grouped = data.groupby("signal_date", sort=False)[column]
    counts = grouped.transform("size")
    means = grouped.transform("mean")
    stds = grouped.transform(lambda values: values.std(ddof=1))
    valid = counts.ge(min_count) & stds.notna() & stds.ne(0)
    return ((data[column] - means) / stds).where(valid)


def _median_diff_by_signal_date(data: pd.DataFrame, column: str, min_count: int) -> pd.Series:
    grouped = data.groupby("signal_date", sort=False)[column]
    counts = grouped.transform("size")
    medians = grouped.transform("median")
    return (data[column] - medians).where(counts.ge(min_count))


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
