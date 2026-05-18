from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.strategies.h001_kr_short_rate_sleeve import load_kr_short_rate_quarterly_carry
from src.strategies.h002_usdkrw_sleeve import load_usdkrw_quarterly_returns
from src.strategies.h003_us_treasury_sleeve import load_us_treasury_quarterly_returns


VARIANTS = ("d013_baseline", "d013_defensive_basket")
SLEEVE_WEIGHTS = ("kr_short_rate_carry", "usdkrw_cash", "us_10y_treasury_krw")


def load_defensive_basket_quarterly_returns(
    *,
    kr_short_rate_csv: str | Path,
    usdkrw_csv: str | Path,
    dgs10_csv: str | Path,
    signal_dates: pd.Series,
    weights: Mapping[str, float],
    effective_duration: float = 7.0,
) -> pd.DataFrame:
    """Build pre-registered quarterly OFF-basket returns from H001/H002/H003 sleeves."""
    _validate_weights(weights)
    carry = load_kr_short_rate_quarterly_carry(kr_short_rate_csv, signal_dates)
    fx = load_usdkrw_quarterly_returns(usdkrw_csv, signal_dates)
    treasury = load_us_treasury_quarterly_returns(
        dgs10_csv,
        usdkrw_csv,
        signal_dates,
        effective_duration=effective_duration,
    )
    data = (
        carry.merge(fx, on="signal_date", how="left")
        .merge(
            treasury.loc[
                :,
                [
                    "signal_date",
                    "start_yield_observation_date",
                    "start_yield",
                    "end_yield_observation_date",
                    "end_yield",
                    "yield_change",
                    "duration_return",
                    "carry_return",
                    "usd_treasury_return",
                    "fx_return",
                    "krw_treasury_return",
                    "effective_duration",
                ],
            ],
            on="signal_date",
            how="left",
        )
        .sort_values("signal_date")
        .reset_index(drop=True)
    )
    kr_weight = float(weights["kr_short_rate_carry"])
    usd_weight = float(weights["usdkrw_cash"])
    treasury_weight = float(weights["us_10y_treasury_krw"])
    data["kr_carry_contribution"] = kr_weight * pd.to_numeric(data["kr_short_quarter_carry"], errors="coerce")
    data["usdkrw_contribution"] = usd_weight * pd.to_numeric(data["usdkrw_quarter_return"], errors="coerce")
    data["treasury_contribution"] = treasury_weight * pd.to_numeric(data["krw_treasury_return"], errors="coerce")
    data["basket_quarter_return"] = (
        data["kr_carry_contribution"] + data["usdkrw_contribution"] + data["treasury_contribution"]
    )
    data["kr_short_rate_weight"] = kr_weight
    data["usdkrw_weight"] = usd_weight
    data["us_treasury_weight"] = treasury_weight
    return data


def apply_defensive_basket_off_sleeve(
    result: BacktestResult,
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    kr_short_rate_csv: str | Path,
    usdkrw_csv: str | Path,
    dgs10_csv: str | Path,
    weights: Mapping[str, float],
    effective_duration: float = 7.0,
) -> tuple[BacktestResult, pd.DataFrame]:
    """Replace D013 OFF cash return with a fixed-weight defensive basket."""
    regime = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    regime["signal_date"] = pd.to_datetime(regime["signal_date"], errors="raise").dt.normalize()
    regime = regime.sort_values("signal_date").reset_index(drop=True)
    basket = load_defensive_basket_quarterly_returns(
        kr_short_rate_csv=kr_short_rate_csv,
        usdkrw_csv=usdkrw_csv,
        dgs10_csv=dgs10_csv,
        signal_dates=regime["signal_date"],
        weights=weights,
        effective_duration=effective_duration,
    )
    regime = regime.merge(basket, on="signal_date", how="left")
    regime["execution_date"] = [calendar.next_trading_day(date) for date in regime["signal_date"]]
    regime["next_execution_date"] = regime["execution_date"].shift(-1)

    equity = result.equity_curve.copy()
    equity["date"] = pd.to_datetime(equity["date"], errors="raise").dt.normalize()
    date_index = pd.Index(equity["date"])
    daily_multiplier = pd.Series(1.0, index=date_index, dtype="float64")
    rows: list[dict[str, object]] = []
    cumulative = 1.0

    for row in regime.itertuples(index=False):
        if bool(row.regime_on):
            continue
        if pd.isna(row.next_execution_date):
            raise ValueError(f"Cannot compute full-quarter basket return after final OFF signal_date {row.signal_date.date()}.")
        if pd.isna(row.basket_quarter_return):
            raise ValueError(f"Missing defensive basket return for signal_date {row.signal_date.date()}.")
        start = pd.Timestamp(row.execution_date).normalize()
        end = pd.Timestamp(row.next_execution_date).normalize()
        mask = (date_index >= start) & (date_index < end)
        n_days = int(mask.sum())
        quarter_return = float(row.basket_quarter_return)
        if n_days > 0:
            daily = (1.0 + quarter_return) ** (1.0 / n_days) - 1.0
            daily_multiplier.loc[mask] = 1.0 + daily
            cumulative *= 1.0 + quarter_return
        else:
            daily = float("nan")
        rows.append(
            {
                "signal_date": row.signal_date,
                "execution_date": start,
                "end_signal_date": row.end_signal_date,
                "end_exclusive": end,
                "kr_short_rate_weight": row.kr_short_rate_weight,
                "usdkrw_weight": row.usdkrw_weight,
                "us_treasury_weight": row.us_treasury_weight,
                "kr_short_quarter_carry": row.kr_short_quarter_carry,
                "usdkrw_quarter_return": row.usdkrw_quarter_return,
                "quarter_treasury_krw_return": row.krw_treasury_return,
                "kr_carry_contribution": row.kr_carry_contribution,
                "usdkrw_contribution": row.usdkrw_contribution,
                "treasury_contribution": row.treasury_contribution,
                "basket_quarter_return": quarter_return,
                "daily_basket_return": daily,
                "trading_days": n_days,
                "cumulative_off_basket": cumulative - 1.0,
                "yield_change": row.yield_change,
                "fx_return": row.usdkrw_quarter_return,
            }
        )

    sleeve_factor = daily_multiplier.cumprod()
    adjusted = equity.copy()
    for column in ("cash", "mtm_value", "gross_value", "net_value"):
        if column in adjusted.columns:
            adjusted[column] = pd.to_numeric(adjusted[column], errors="raise") * sleeve_factor.to_numpy()

    trades = _scale_trades(result.trades, sleeve_factor)
    return BacktestResult(trades=trades, equity_curve=adjusted), pd.DataFrame(rows)


def defensive_basket_drawdown(decomposition: pd.DataFrame) -> float:
    if decomposition.empty:
        return 0.0
    values = (1.0 + pd.to_numeric(decomposition["basket_quarter_return"], errors="raise")).cumprod()
    drawdown = values / values.cummax() - 1.0
    return float(drawdown.min())


def _validate_weights(weights: Mapping[str, float]) -> None:
    if tuple(weights.keys()) != SLEEVE_WEIGHTS:
        raise ValueError(f"Basket weights must be exactly {list(SLEEVE_WEIGHTS)}.")
    total = sum(float(weights[name]) for name in SLEEVE_WEIGHTS)
    if abs(total - 1.0) > 1e-12:
        raise ValueError("Basket weights must sum to 1.0.")
    if any(float(weights[name]) < 0.0 for name in SLEEVE_WEIGHTS):
        raise ValueError("Basket weights must be non-negative.")


def _scale_trades(trades: pd.DataFrame, sleeve_factor: pd.Series) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    scaled = trades.copy()
    by_date = sleeve_factor.groupby(level=0).last()
    entry_scale = pd.to_datetime(scaled["entry_date"], errors="raise").dt.normalize().map(by_date).fillna(1.0)
    exit_scale = pd.to_datetime(scaled["exit_date"], errors="raise").dt.normalize().map(by_date).fillna(entry_scale)
    for column in ("shares", "notional_at_entry", "buy_cost"):
        if column in scaled.columns:
            scaled[column] = pd.to_numeric(scaled[column], errors="raise") * entry_scale.to_numpy()
    if "sell_cost" in scaled.columns:
        scaled["sell_cost"] = pd.to_numeric(scaled["sell_cost"], errors="raise") * exit_scale.to_numpy()
    return scaled
