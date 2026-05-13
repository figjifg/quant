from __future__ import annotations

import pandas as pd


def trigger_immediate(filtered_features: pd.DataFrame) -> pd.DataFrame:
    """Return filtered rows unchanged; filter pass is the entry trigger."""
    return filtered_features


def trigger_freshness(filtered_features: pd.DataFrame, full_features: pd.DataFrame) -> pd.DataFrame:
    """Fire only when a ticker's positive-flow filter newly turns true."""
    _require_columns(filtered_features, ("종목코드", "signal_date"), "filtered_features")
    state = _filter_state(full_features)
    state["previous_filter_pass"] = (
        state.groupby("종목코드", sort=False)["filter_pass"].shift(1).fillna(False).astype(bool)
    )
    fired_keys = state.loc[state["filter_pass"] & state["previous_filter_pass"].eq(False), ["종목코드", "signal_date"]]
    return _semi_join_filtered(filtered_features, fired_keys)


def trigger_acceleration(filtered_features: pd.DataFrame, full_features: pd.DataFrame) -> pd.DataFrame:
    """Fire when one-day combined flow is stronger than the 5-day daily average."""
    _require_columns(filtered_features, ("종목코드", "signal_date", "combined_flow_5"), "filtered_features")
    _require_columns(full_features, ("종목코드", "combined_flow_1"), "full_features")
    context = _date_keyed(full_features).loc[:, ["종목코드", "signal_date", "combined_flow_1"]]
    triggered = filtered_features.merge(
        context,
        on=["종목코드", "signal_date"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_from_full"),
    )
    mask = triggered["combined_flow_1"].gt(triggered["combined_flow_5"] / 5.0)
    return triggered.loc[mask, filtered_features.columns].copy()


def trigger_persistence_3d(filtered_features: pd.DataFrame, full_features: pd.DataFrame) -> pd.DataFrame:
    """Fire on the third consecutive signal_date where the positive-flow filter passes."""
    _require_columns(filtered_features, ("종목코드", "signal_date"), "filtered_features")
    state = _filter_state(full_features)
    run_id = state.groupby("종목코드", sort=False)["filter_pass"].transform(lambda values: values.ne(values.shift()).cumsum())
    state["run_length"] = state.groupby(["종목코드", run_id], sort=False).cumcount() + 1
    fired_keys = state.loc[state["filter_pass"] & state["run_length"].eq(3), ["종목코드", "signal_date"]]
    return _semi_join_filtered(filtered_features, fired_keys)


def _filter_state(full_features: pd.DataFrame) -> pd.DataFrame:
    _require_columns(full_features, ("종목코드", "fnv_5", "inv_5"), "full_features")
    state = _date_keyed(full_features).loc[:, ["종목코드", "signal_date", "fnv_5", "inv_5"]].copy()
    state["filter_pass"] = state["fnv_5"].gt(0) & state["inv_5"].gt(0)
    return state.sort_values(["종목코드", "signal_date"]).reset_index(drop=True)


def _date_keyed(features: pd.DataFrame) -> pd.DataFrame:
    if "signal_date" in features.columns:
        result = features.copy()
        result["signal_date"] = pd.to_datetime(result["signal_date"], errors="raise").astype("datetime64[ns]")
        return result
    _require_columns(features, ("날짜",), "features")
    result = features.copy()
    result["signal_date"] = pd.to_datetime(result["날짜"], errors="raise").astype("datetime64[ns]")
    return result


def _semi_join_filtered(filtered_features: pd.DataFrame, fired_keys: pd.DataFrame) -> pd.DataFrame:
    filtered = filtered_features.copy()
    filtered["signal_date"] = pd.to_datetime(filtered["signal_date"], errors="raise").astype("datetime64[ns]")
    fired = fired_keys.drop_duplicates(["종목코드", "signal_date"])
    return filtered.merge(
        fired.assign(_trigger_fire=True),
        on=["종목코드", "signal_date"],
        how="inner",
        validate="many_to_one",
    ).drop(columns="_trigger_fire")


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
