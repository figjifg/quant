from __future__ import annotations

import math

import pandas as pd


def realized_volatility_60d(
    equity_curve: pd.DataFrame,
    *,
    window: int = 60,
    annualization: int = 252,
) -> pd.DataFrame:
    """Compute trailing realized volatility from daily portfolio returns.

    The value stamped on date T uses returns through T only. A caller can use
    that value for a T+1 rebalance without look-ahead.
    """
    if window <= 1:
        raise ValueError("window must be greater than 1.")
    if annualization <= 0:
        raise ValueError("annualization must be positive.")
    _require_columns(equity_curve, ("date", "net_value"), "equity_curve")

    data = equity_curve.loc[:, ["date", "net_value"]].copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    data = data.sort_values("date").reset_index(drop=True)
    net = pd.to_numeric(data["net_value"], errors="raise")
    returns = net.pct_change()
    data["daily_return"] = returns
    data["realized_vol_60d"] = returns.rolling(window=window, min_periods=window).std(ddof=1) * math.sqrt(annualization)
    return data.loc[:, ["date", "daily_return", "realized_vol_60d"]]


def volatility_scalars(
    equity_curve: pd.DataFrame,
    signal_dates: pd.Series | pd.Index | list[object],
    *,
    target_vol: float = 0.20,
    window: int = 60,
    annualization: int = 252,
) -> pd.DataFrame:
    """Return vol_scalar values for signal dates using trailing realized vol."""
    if target_vol <= 0.0:
        raise ValueError("target_vol must be positive.")
    vol = realized_volatility_60d(equity_curve, window=window, annualization=annualization)
    dates = pd.DataFrame({"signal_date": pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()})
    dates = dates.drop_duplicates().sort_values("signal_date").reset_index(drop=True)
    data = dates.merge(
        vol.rename(columns={"date": "signal_date"}),
        on="signal_date",
        how="left",
        validate="one_to_one",
    )
    realized = pd.to_numeric(data["realized_vol_60d"], errors="coerce")
    scalar = target_vol / realized
    scalar = scalar.where(realized.gt(0.0), 1.0)
    scalar = scalar.clip(upper=1.0).fillna(1.0)
    data["target_vol"] = float(target_vol)
    data["vol_scalar"] = scalar.astype("float64")
    return data.loc[:, ["signal_date", "daily_return", "realized_vol_60d", "target_vol", "vol_scalar"]]


def apply_volatility_target_to_weights(
    candidates: pd.DataFrame,
    scalars: pd.DataFrame,
    *,
    base_weight: float | None = None,
) -> pd.DataFrame:
    """Multiply candidate target weights by the signal-date vol scalar."""
    if candidates.empty:
        data = candidates.copy()
        if "target_weight_before_vol" not in data.columns:
            data["target_weight_before_vol"] = pd.Series(dtype="float64")
        data["target_weight"] = pd.Series(dtype="float64")
        data["realized_vol_60d"] = pd.Series(dtype="float64")
        data["target_vol"] = pd.Series(dtype="float64")
        data["vol_scalar"] = pd.Series(dtype="float64")
        return data
    _require_columns(candidates, ("signal_date",), "candidates")
    _require_columns(scalars, ("signal_date", "realized_vol_60d", "target_vol", "vol_scalar"), "scalars")

    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    if "target_weight" in data.columns:
        data["target_weight_before_vol"] = pd.to_numeric(data["target_weight"], errors="raise")
    elif base_weight is not None:
        data["target_weight_before_vol"] = float(base_weight)
    else:
        raise ValueError("candidates must contain target_weight unless base_weight is provided.")

    scalar_data = scalars.loc[:, ["signal_date", "realized_vol_60d", "target_vol", "vol_scalar"]].copy()
    scalar_data["signal_date"] = pd.to_datetime(scalar_data["signal_date"], errors="raise").dt.normalize()
    data = data.merge(scalar_data, on="signal_date", how="left", validate="many_to_one")
    data["vol_scalar"] = pd.to_numeric(data["vol_scalar"], errors="coerce").fillna(1.0)
    data["target_weight"] = data["target_weight_before_vol"] * data["vol_scalar"]
    return data


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
