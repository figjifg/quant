from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult


VARIANTS = ("d013_baseline", "d013_us_treasury_sleeve")
DGS10_COLUMN = "DGS10"
USDKRW_COLUMN = "DEXKOUS"


def load_us_treasury_quarterly_returns(
    dgs10_csv: str | Path,
    usdkrw_csv: str | Path,
    signal_dates: pd.Series,
    *,
    effective_duration: float = 7.0,
) -> pd.DataFrame:
    """Align US 10Y yield and USDKRW to signal dates and compute simple KRW quarterly returns."""
    yields = _load_series(dgs10_csv, DGS10_COLUMN)
    fx = _load_series(usdkrw_csv, USDKRW_COLUMN)
    dates = pd.DataFrame({"signal_date": pd.to_datetime(signal_dates, errors="raise").dt.normalize()})
    dates = dates.sort_values("signal_date").reset_index(drop=True)
    dates["end_signal_date"] = dates["signal_date"].shift(-1)

    start_yield = _align_asof(dates[["signal_date"]], yields, DGS10_COLUMN, "start_yield")
    start_fx = _align_asof(dates[["signal_date"]], fx, USDKRW_COLUMN, "start_usdkrw")
    aligned = dates.merge(start_yield, on="signal_date", how="left").merge(start_fx, on="signal_date", how="left")

    end_dates = dates.loc[dates["end_signal_date"].notna(), ["end_signal_date"]].rename(
        columns={"end_signal_date": "signal_date"}
    )
    end_yield = _align_asof(end_dates, yields, DGS10_COLUMN, "end_yield").rename(
        columns={"signal_date": "end_signal_date", "observation_date": "end_yield_observation_date"}
    )
    end_fx = _align_asof(end_dates, fx, USDKRW_COLUMN, "end_usdkrw").rename(
        columns={"signal_date": "end_signal_date", "observation_date": "end_usdkrw_observation_date"}
    )
    aligned = aligned.merge(end_yield, on="end_signal_date", how="left").merge(end_fx, on="end_signal_date", how="left")

    start_yield_decimal = pd.to_numeric(aligned["start_yield"], errors="coerce") / 100.0
    end_yield_decimal = pd.to_numeric(aligned["end_yield"], errors="coerce") / 100.0
    aligned["yield_change"] = end_yield_decimal - start_yield_decimal
    aligned["duration_return"] = -float(effective_duration) * aligned["yield_change"]
    aligned["carry_return"] = start_yield_decimal / 4.0
    aligned["usd_treasury_return"] = aligned["duration_return"] + aligned["carry_return"]
    aligned["fx_return"] = pd.to_numeric(aligned["end_usdkrw"], errors="coerce") / pd.to_numeric(
        aligned["start_usdkrw"], errors="coerce"
    ) - 1.0
    aligned["krw_treasury_return"] = aligned["usd_treasury_return"] + aligned["fx_return"]
    aligned["effective_duration"] = float(effective_duration)

    return aligned.loc[
        :,
        [
            "signal_date",
            "start_yield_observation_date",
            "start_yield",
            "end_signal_date",
            "end_yield_observation_date",
            "end_yield",
            "yield_change",
            "duration_return",
            "carry_return",
            "usd_treasury_return",
            "start_usdkrw_observation_date",
            "start_usdkrw",
            "end_usdkrw_observation_date",
            "end_usdkrw",
            "fx_return",
            "krw_treasury_return",
            "effective_duration",
        ],
    ]


def apply_us_treasury_off_sleeve(
    result: BacktestResult,
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    dgs10_csv: str | Path,
    usdkrw_csv: str | Path,
    effective_duration: float = 7.0,
) -> tuple[BacktestResult, pd.DataFrame]:
    """Replace D013 OFF cash return with simple US 10Y Treasury return translated to KRW."""
    regime = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    regime["signal_date"] = pd.to_datetime(regime["signal_date"], errors="raise").dt.normalize()
    regime = regime.sort_values("signal_date").reset_index(drop=True)
    treasury_returns = load_us_treasury_quarterly_returns(
        dgs10_csv,
        usdkrw_csv,
        regime["signal_date"],
        effective_duration=effective_duration,
    )
    regime = regime.merge(treasury_returns, on="signal_date", how="left")
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
            raise ValueError(
                f"Cannot compute full-quarter US Treasury return after final OFF signal_date {row.signal_date.date()}."
            )
        if pd.isna(row.krw_treasury_return):
            raise ValueError(f"Missing US Treasury return for signal_date {row.signal_date.date()}.")
        start = pd.Timestamp(row.execution_date).normalize()
        end = pd.Timestamp(row.next_execution_date).normalize()
        mask = (date_index >= start) & (date_index < end)
        n_days = int(mask.sum())
        quarter_return = float(row.krw_treasury_return)
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
                "start_yield_observation_date": row.start_yield_observation_date,
                "start_yield": row.start_yield,
                "end_yield_observation_date": row.end_yield_observation_date,
                "end_yield": row.end_yield,
                "yield_change": row.yield_change,
                "duration_return": row.duration_return,
                "carry_return": row.carry_return,
                "usd_treasury_return": row.usd_treasury_return,
                "start_usdkrw_observation_date": row.start_usdkrw_observation_date,
                "start_usdkrw": row.start_usdkrw,
                "end_usdkrw_observation_date": row.end_usdkrw_observation_date,
                "end_usdkrw": row.end_usdkrw,
                "fx_return": row.fx_return,
                "quarter_treasury_krw_return": quarter_return,
                "daily_treasury_krw_return": daily,
                "trading_days": n_days,
                "effective_duration": row.effective_duration,
                "cumulative_off_treasury": cumulative - 1.0,
            }
        )

    sleeve_factor = daily_multiplier.cumprod()
    adjusted = equity.copy()
    for column in ("cash", "mtm_value", "gross_value", "net_value"):
        if column in adjusted.columns:
            adjusted[column] = pd.to_numeric(adjusted[column], errors="raise") * sleeve_factor.to_numpy()

    trades = _scale_trades(result.trades, sleeve_factor)
    return BacktestResult(trades=trades, equity_curve=adjusted), pd.DataFrame(rows)


def us_treasury_sleeve_drawdown(off_treasury: pd.DataFrame) -> float:
    if off_treasury.empty:
        return 0.0
    values = (1.0 + pd.to_numeric(off_treasury["quarter_treasury_krw_return"], errors="raise")).cumprod()
    drawdown = values / values.cummax() - 1.0
    return float(drawdown.min())


def _load_series(path: str | Path, value_column: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["observation_date"], na_values=["."])
    data.columns = [str(column).lstrip("\ufeff") for column in data.columns]
    if value_column not in data.columns:
        raise ValueError(f"{path} must contain {value_column}.")
    data[value_column] = pd.to_numeric(data[value_column], errors="coerce")
    return data.dropna(subset=[value_column]).sort_values("observation_date")


def _align_asof(dates: pd.DataFrame, series: pd.DataFrame, value_column: str, output_column: str) -> pd.DataFrame:
    aligned = pd.merge_asof(
        dates.sort_values("signal_date"),
        series[["observation_date", value_column]],
        left_on="signal_date",
        right_on="observation_date",
        direction="backward",
    )
    return aligned.rename(
        columns={
            "observation_date": f"{output_column}_observation_date",
            value_column: output_column,
        }
    )


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
