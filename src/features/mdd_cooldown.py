from __future__ import annotations

import pandas as pd


def mdd_cooldown_scalars(
    equity_curve: pd.DataFrame,
    signal_dates: pd.Series | pd.Index | list[object],
    *,
    drawdown_lookback_days: int = 252,
    warning_threshold: float = -0.05,
    hard_threshold: float = -0.15,
    hard_scalar: float = 0.5,
) -> pd.DataFrame:
    """Return signal-date exposure scalars from trailing portfolio drawdown.

    The drawdown stamped on signal date T uses portfolio values through T only.
    Callers can apply the scalar to T+1 or later execution weights.
    """
    if drawdown_lookback_days <= 1:
        raise ValueError("drawdown_lookback_days must be greater than 1.")
    if not hard_threshold < warning_threshold < 0.0:
        raise ValueError("thresholds must satisfy hard_threshold < warning_threshold < 0.")
    if not 0.0 < hard_scalar <= 1.0:
        raise ValueError("hard_scalar must be in (0, 1].")
    _require_columns(equity_curve, ("date", "net_value"), "equity_curve")

    data = equity_curve.loc[:, ["date", "net_value"]].copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    data = data.sort_values("date").reset_index(drop=True)
    net = pd.to_numeric(data["net_value"], errors="raise")
    trailing_peak = net.rolling(window=drawdown_lookback_days, min_periods=1).max()
    data["portfolio_drawdown"] = net / trailing_peak - 1.0

    dates = pd.DataFrame({"signal_date": pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()})
    dates = dates.drop_duplicates().sort_values("signal_date").reset_index(drop=True)
    output = dates.merge(
        data.rename(columns={"date": "signal_date"}),
        on="signal_date",
        how="left",
        validate="one_to_one",
    )
    drawdown = pd.to_numeric(output["portfolio_drawdown"], errors="coerce")
    slope = (1.0 - hard_scalar) / (warning_threshold - hard_threshold)
    scalar = hard_scalar + (drawdown - hard_threshold) * slope
    scalar = scalar.where(drawdown.lt(warning_threshold), 1.0)
    scalar = scalar.where(drawdown.ge(hard_threshold), hard_scalar)
    output["drawdown_lookback_days"] = int(drawdown_lookback_days)
    output["warning_threshold"] = float(warning_threshold)
    output["hard_threshold"] = float(hard_threshold)
    output["hard_scalar"] = float(hard_scalar)
    output["exposure_scalar"] = scalar.clip(lower=hard_scalar, upper=1.0).fillna(1.0).astype("float64")
    return output.loc[
        :,
        [
            "signal_date",
            "net_value",
            "portfolio_drawdown",
            "drawdown_lookback_days",
            "warning_threshold",
            "hard_threshold",
            "hard_scalar",
            "exposure_scalar",
        ],
    ]


def apply_mdd_cooldown_to_weights(
    candidates: pd.DataFrame,
    scalars: pd.DataFrame,
    *,
    base_weight: float | None = None,
) -> pd.DataFrame:
    """Multiply candidate target weights by signal-date MDD cooldown scalar."""
    if candidates.empty:
        data = candidates.copy()
        if "target_weight_before_mdd" not in data.columns:
            data["target_weight_before_mdd"] = pd.Series(dtype="float64")
        data["target_weight"] = pd.Series(dtype="float64")
        data["portfolio_drawdown"] = pd.Series(dtype="float64")
        data["exposure_scalar"] = pd.Series(dtype="float64")
        return data
    _require_columns(candidates, ("signal_date",), "candidates")
    _require_columns(scalars, ("signal_date", "portfolio_drawdown", "exposure_scalar"), "scalars")

    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    if "target_weight" in data.columns:
        data["target_weight_before_mdd"] = pd.to_numeric(data["target_weight"], errors="raise")
    elif base_weight is not None:
        data["target_weight_before_mdd"] = float(base_weight)
    else:
        raise ValueError("candidates must contain target_weight unless base_weight is provided.")

    scalar_data = scalars.loc[:, ["signal_date", "portfolio_drawdown", "exposure_scalar"]].copy()
    scalar_data["signal_date"] = pd.to_datetime(scalar_data["signal_date"], errors="raise").dt.normalize()
    data = data.merge(scalar_data, on="signal_date", how="left", validate="many_to_one")
    data["exposure_scalar"] = pd.to_numeric(data["exposure_scalar"], errors="coerce").fillna(1.0)
    data["target_weight"] = data["target_weight_before_mdd"] * data["exposure_scalar"]
    return data


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
