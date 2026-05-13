from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")
TARGET_COLUMNS = ("execution_date", "combined_flow_5", "종목코드")


def build_e004_top_quintile_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    quintile_value: int | str = 5,
    min_daily_universe_size: int = 20,
) -> pd.DataFrame:
    """Build E004 signal-strength candidates for the slot engine.

    Quintile membership is computed over each signal_date's universe-eligible
    tickers before the positive-component safety filter is applied.
    """
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")
    label_count, target_label = _target_label(quintile_value)
    if min_daily_universe_size <= 0:
        raise ValueError("min_daily_universe_size must be positive.")

    merged = universe.merge(
        flow_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )
    if merged.empty:
        return merged.loc[:, list(FEATURE_COLUMNS)].copy()

    frames = [
        _select_target_label(group, label_count, target_label, min_daily_universe_size)
        for _, group in merged.groupby("signal_date", sort=False)
    ]
    selected = pd.concat(frames, ignore_index=True) if frames else merged.iloc[0:0].copy()
    if selected.empty:
        return selected.loc[:, list(FEATURE_COLUMNS)].copy()

    candidates = selected.loc[selected["fnv_5"].gt(0) & selected["inv_5"].gt(0), list(FEATURE_COLUMNS)].copy()
    return candidates.sort_values(
        list(TARGET_COLUMNS),
        ascending=[True, False, True],
    ).reset_index(drop=True)


def build_e004_quintile_membership(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    *,
    bins: int = 5,
    min_daily_universe_size: int = 20,
) -> pd.DataFrame:
    """Return per-row E004 quantile labels for diagnostic inspection."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")
    if bins not in {5, 10}:
        raise ValueError("bins must be either 5 or 10.")
    if min_daily_universe_size <= 0:
        raise ValueError("min_daily_universe_size must be positive.")

    merged = universe.merge(
        flow_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )
    if merged.empty:
        return merged.assign(quantile_label=pd.Series(dtype="Int64"))

    frames = [
        _label_group(group, bins=bins, min_daily_universe_size=min_daily_universe_size)
        for _, group in merged.groupby("signal_date", sort=False)
    ]
    return pd.concat(frames, ignore_index=True)


def _select_target_label(
    group: pd.DataFrame,
    label_count: int,
    target_label: int,
    min_daily_universe_size: int,
) -> pd.DataFrame:
    labeled = _label_group(group, bins=label_count, min_daily_universe_size=min_daily_universe_size)
    return labeled.loc[labeled["quantile_label"].eq(target_label)].copy()


def _label_group(group: pd.DataFrame, *, bins: int, min_daily_universe_size: int) -> pd.DataFrame:
    clean = group.loc[group["combined_flow_5"].notna()].copy()
    if len(clean) < min_daily_universe_size:
        return group.iloc[0:0].assign(quantile_label=pd.Series(dtype="Int64"))

    ranks = clean["combined_flow_5"].rank(method="first")
    clean["quantile_label"] = pd.qcut(ranks, bins, labels=range(1, bins + 1)).astype("Int64")
    return clean


def _target_label(quintile_value: int | str) -> tuple[int, int]:
    if quintile_value == "top_decile":
        return 10, 10
    if quintile_value not in {1, 2, 3, 4, 5}:
        raise ValueError("quintile_value must be one of {1, 2, 3, 4, 5} or 'top_decile'.")
    return 5, int(quintile_value)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
