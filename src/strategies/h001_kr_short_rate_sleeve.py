from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult


VARIANTS = ("d013_baseline", "d013_kr_short_rate_sleeve")
RATE_COLUMN = "IR3TIB01KRM156N"


def load_kr_short_rate_quarterly_carry(path: str | Path, signal_dates: pd.Series) -> pd.DataFrame:
    """Align KR 3M annual rates as-of signal dates and convert them to quarterly carry."""
    rates = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    if RATE_COLUMN not in rates.columns:
        raise ValueError(f"{path} must contain {RATE_COLUMN}.")
    rates[RATE_COLUMN] = pd.to_numeric(rates[RATE_COLUMN], errors="coerce")
    rates = rates.dropna(subset=[RATE_COLUMN]).sort_values("observation_date")

    dates = pd.DataFrame({"signal_date": pd.to_datetime(signal_dates, errors="raise").dt.normalize()})
    aligned = pd.merge_asof(
        dates.sort_values("signal_date"),
        rates[["observation_date", RATE_COLUMN]],
        left_on="signal_date",
        right_on="observation_date",
        direction="backward",
    )
    aligned["annual_rate"] = aligned[RATE_COLUMN] / 100.0
    aligned["kr_short_quarter_carry"] = (1.0 + aligned["annual_rate"] / 12.0) ** 3 - 1.0
    return aligned.loc[:, ["signal_date", "observation_date", "annual_rate", "kr_short_quarter_carry"]]


def apply_kr_short_rate_off_sleeve(
    result: BacktestResult,
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    kr_short_rate_csv: str | Path,
) -> tuple[BacktestResult, pd.DataFrame]:
    """Replace D013 OFF cash return with KR short-rate carry without changing D013 trades."""
    regime = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    regime["signal_date"] = pd.to_datetime(regime["signal_date"], errors="raise").dt.normalize()
    regime = regime.sort_values("signal_date").reset_index(drop=True)
    carry = load_kr_short_rate_quarterly_carry(kr_short_rate_csv, regime["signal_date"])
    regime = regime.merge(carry, on="signal_date", how="left")
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
        if pd.isna(row.kr_short_quarter_carry):
            raise ValueError(f"Missing KR short-rate carry for signal_date {row.signal_date.date()}.")
        start = pd.Timestamp(row.execution_date).normalize()
        end = (
            pd.Timestamp(row.next_execution_date).normalize()
            if not pd.isna(row.next_execution_date)
            else pd.Timestamp(equity["date"].iloc[-1]).normalize() + pd.Timedelta(days=1)
        )
        mask = (date_index >= start) & (date_index < end)
        n_days = int(mask.sum())
        quarter_carry = float(row.kr_short_quarter_carry)
        if n_days > 0:
            daily = (1.0 + quarter_carry) ** (1.0 / n_days) - 1.0
            daily_multiplier.loc[mask] = 1.0 + daily
            cumulative *= 1.0 + quarter_carry
        else:
            daily = float("nan")
        rows.append(
            {
                "signal_date": row.signal_date,
                "execution_date": start,
                "end_exclusive": end,
                "observation_date": row.observation_date,
                "annual_rate": row.annual_rate,
                "quarter_carry": quarter_carry,
                "daily_carry": daily,
                "trading_days": n_days,
                "cumulative_off_carry": cumulative - 1.0,
            }
        )

    sleeve_factor = daily_multiplier.cumprod()
    adjusted = equity.copy()
    for column in ("cash", "mtm_value", "gross_value", "net_value"):
        if column in adjusted.columns:
            adjusted[column] = pd.to_numeric(adjusted[column], errors="raise") * sleeve_factor.to_numpy()

    trades = _scale_trades(result.trades, sleeve_factor)
    return BacktestResult(trades=trades, equity_curve=adjusted), pd.DataFrame(rows)


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
