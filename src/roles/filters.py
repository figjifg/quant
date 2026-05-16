from __future__ import annotations

import pandas as pd


def filter_flow_sign_both_positive(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Return rows where both 5-day foreign and institutional flows are positive."""
    _require_columns(flow_features, ("fnv_5", "inv_5"), "flow_features")
    return flow_features.loc[flow_features["fnv_5"].gt(0) & flow_features["inv_5"].gt(0)].copy()


def filter_relative_flow_sign_both_positive_z(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Return rows where both z-scored 5-day flow components are positive."""
    _require_columns(flow_features, ("fnv_5_z", "inv_5_z"), "flow_features")
    return flow_features.loc[flow_features["fnv_5_z"].gt(0) & flow_features["inv_5_z"].gt(0)].copy()


def filter_relative_flow_sign_both_positive(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Return rows where both median-relative 5-day flow components are positive."""
    _require_columns(flow_features, ("fnv_5_rel", "inv_5_rel"), "flow_features")
    return flow_features.loc[flow_features["fnv_5_rel"].gt(0) & flow_features["inv_5_rel"].gt(0)].copy()


def filter_relative_AND_absolute_positive(
    features: pd.DataFrame,
    relative_features: pd.DataFrame,
) -> pd.DataFrame:
    """Return rows where absolute and median-relative 5-day flow components are positive."""
    _require_columns(features, ("execution_date", "signal_date", "종목코드", "fnv_5", "inv_5"), "features")
    _require_columns(
        relative_features,
        ("execution_date", "signal_date", "종목코드", "fnv_5_rel", "inv_5_rel"),
        "relative_features",
    )
    merged = _date_keyed(features).merge(
        _date_keyed(relative_features).loc[
            :, ["execution_date", "signal_date", "종목코드", "fnv_5_rel", "inv_5_rel"]
        ],
        on=["execution_date", "signal_date", "종목코드"],
        how="left",
        validate="one_to_one",
    )
    mask = (
        merged["fnv_5"].gt(0)
        & merged["inv_5"].gt(0)
        & merged["fnv_5_rel"].gt(0)
        & merged["inv_5_rel"].gt(0)
    )
    return merged.loc[mask].copy()


def filter_persistence_4_of_5(
    features: pd.DataFrame,
    daily_flow_features: pd.DataFrame,
) -> pd.DataFrame:
    """Return F1 rows with at least four positive one-day combined-flow days in [T-4, T]."""
    _require_columns(features, ("signal_date", "종목코드", "fnv_5", "inv_5"), "features")
    _require_columns(daily_flow_features, ("signal_date", "종목코드", "combined_flow_1"), "daily_flow_features")

    base = filter_flow_sign_both_positive(features)
    persistence = _date_keyed(daily_flow_features).loc[:, ["signal_date", "종목코드", "combined_flow_1"]].copy()
    persistence = persistence.sort_values(["종목코드", "signal_date"]).reset_index(drop=True)
    positive_days = persistence["combined_flow_1"].gt(0).astype("int64")
    persistence["positive_combined_flow_1_count_5"] = (
        positive_days.groupby(persistence["종목코드"], sort=False)
        .rolling(5, min_periods=5)
        .sum()
        .reset_index(level=0, drop=True)
    )
    pass_keys = persistence.loc[
        persistence["positive_combined_flow_1_count_5"].ge(4),
        ["signal_date", "종목코드", "positive_combined_flow_1_count_5"],
    ]
    keyed = _date_keyed(base)
    return keyed.merge(pass_keys, on=["signal_date", "종목코드"], how="inner", validate="many_to_one")


def _date_keyed(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    result["signal_date"] = pd.to_datetime(result["signal_date"], errors="raise").astype("datetime64[ns]")
    if "execution_date" in result.columns:
        result["execution_date"] = pd.to_datetime(result["execution_date"], errors="raise").astype("datetime64[ns]")
    result["종목코드"] = result["종목코드"].astype("string")
    return result


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
