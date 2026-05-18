from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult


VARIANTS = ("d013_baseline", "d013_usdkrw_sleeve")
USDKRW_COLUMN = "DEXKOUS"


def load_usdkrw_quarterly_returns(path: str | Path, signal_dates: pd.Series) -> pd.DataFrame:
    """Align USDKRW observations to quarter-end signal dates and compute T to T+1Q returns."""
    fx = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    fx.columns = [str(column).lstrip("\ufeff") for column in fx.columns]
    if USDKRW_COLUMN not in fx.columns:
        raise ValueError(f"{path} must contain {USDKRW_COLUMN}.")
    fx[USDKRW_COLUMN] = pd.to_numeric(fx[USDKRW_COLUMN], errors="coerce")
    fx = fx.dropna(subset=[USDKRW_COLUMN]).sort_values("observation_date")

    dates = pd.DataFrame({"signal_date": pd.to_datetime(signal_dates, errors="raise").dt.normalize()})
    aligned = pd.merge_asof(
        dates.sort_values("signal_date"),
        fx[["observation_date", USDKRW_COLUMN]],
        left_on="signal_date",
        right_on="observation_date",
        direction="backward",
    ).rename(columns={"observation_date": "start_observation_date", USDKRW_COLUMN: "start_usdkrw"})
    aligned["end_signal_date"] = aligned["signal_date"].shift(-1)

    end_dates = aligned.loc[aligned["end_signal_date"].notna(), ["end_signal_date"]].copy()
    end_dates = end_dates.rename(columns={"end_signal_date": "signal_date"})
    end_aligned = pd.merge_asof(
        end_dates.sort_values("signal_date"),
        fx[["observation_date", USDKRW_COLUMN]],
        left_on="signal_date",
        right_on="observation_date",
        direction="backward",
    ).rename(
        columns={
            "signal_date": "end_signal_date",
            "observation_date": "end_observation_date",
            USDKRW_COLUMN: "end_usdkrw",
        }
    )

    aligned = aligned.merge(end_aligned, on="end_signal_date", how="left")
    aligned["usdkrw_quarter_return"] = aligned["end_usdkrw"] / aligned["start_usdkrw"] - 1.0
    return aligned.loc[
        :,
        [
            "signal_date",
            "start_observation_date",
            "start_usdkrw",
            "end_signal_date",
            "end_observation_date",
            "end_usdkrw",
            "usdkrw_quarter_return",
        ],
    ]


def apply_usdkrw_off_sleeve(
    result: BacktestResult,
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    usdkrw_csv: str | Path,
) -> tuple[BacktestResult, pd.DataFrame]:
    """Replace D013 OFF cash return with USD cash marked in KRW by quarter FX change."""
    regime = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    regime["signal_date"] = pd.to_datetime(regime["signal_date"], errors="raise").dt.normalize()
    regime = regime.sort_values("signal_date").reset_index(drop=True)
    fx_returns = load_usdkrw_quarterly_returns(usdkrw_csv, regime["signal_date"])
    regime = regime.merge(fx_returns, on="signal_date", how="left")
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
            raise ValueError(f"Cannot compute full-quarter USDKRW return after final OFF signal_date {row.signal_date.date()}.")
        if pd.isna(row.usdkrw_quarter_return):
            raise ValueError(f"Missing USDKRW quarter return for signal_date {row.signal_date.date()}.")
        start = pd.Timestamp(row.execution_date).normalize()
        end = pd.Timestamp(row.next_execution_date).normalize()
        mask = (date_index >= start) & (date_index < end)
        n_days = int(mask.sum())
        quarter_return = float(row.usdkrw_quarter_return)
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
                "start_observation_date": row.start_observation_date,
                "end_observation_date": row.end_observation_date,
                "start_usdkrw": row.start_usdkrw,
                "end_usdkrw": row.end_usdkrw,
                "quarter_fx_return": quarter_return,
                "daily_fx_return": daily,
                "trading_days": n_days,
                "cumulative_off_fx": cumulative - 1.0,
            }
        )

    sleeve_factor = daily_multiplier.cumprod()
    adjusted = equity.copy()
    for column in ("cash", "mtm_value", "gross_value", "net_value"):
        if column in adjusted.columns:
            adjusted[column] = pd.to_numeric(adjusted[column], errors="raise") * sleeve_factor.to_numpy()

    trades = _scale_trades(result.trades, sleeve_factor)
    return BacktestResult(trades=trades, equity_curve=adjusted), pd.DataFrame(rows)


def usdkrw_sleeve_drawdown(off_fx: pd.DataFrame) -> float:
    if off_fx.empty:
        return 0.0
    values = (1.0 + pd.to_numeric(off_fx["quarter_fx_return"], errors="raise")).cumprod()
    drawdown = values / values.cummax() - 1.0
    return float(drawdown.min())


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
