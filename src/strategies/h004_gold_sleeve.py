from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult


VARIANTS = ("d013_baseline", "d013_gold_sleeve")
GOLD_INCEPTION_DATE = pd.Timestamp("2010-10-01")
GOLD_TICKER = "132030"


def load_gold_quarterly_returns(
    path: str | Path,
    signal_dates: pd.Series,
    *,
    final_end_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Align KODEX 132030 closes to D013 quarter-end signal dates."""
    gold = pd.read_csv(path, parse_dates=["date"])
    gold.columns = [str(column).lstrip("\ufeff") for column in gold.columns]
    required = {"date", "close"}
    missing = required.difference(gold.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}.")
    gold["close"] = pd.to_numeric(gold["close"], errors="coerce")
    gold = gold.dropna(subset=["date", "close"]).sort_values("date")

    dates = pd.DataFrame({"signal_date": pd.to_datetime(signal_dates, errors="raise").dt.normalize()})
    dates = dates.sort_values("signal_date").reset_index(drop=True)
    dates["end_signal_date"] = dates["signal_date"].shift(-1)
    if final_end_date is not None and not dates.empty:
        dates.loc[dates["end_signal_date"].isna(), "end_signal_date"] = pd.Timestamp(final_end_date).normalize()

    start = _align_gold_close(dates[["signal_date"]], gold, "start")
    end_dates = dates.loc[dates["end_signal_date"].notna(), ["end_signal_date"]].rename(
        columns={"end_signal_date": "signal_date"}
    )
    end = _align_gold_close(end_dates, gold, "end").rename(
        columns={
            "signal_date": "end_signal_date",
            "end_observation_date": "end_observation_date",
            "end_close": "end_close",
        }
    )
    aligned = dates.merge(start, on="signal_date", how="left").merge(end, on="end_signal_date", how="left")
    aligned["inception_cash_fallback"] = aligned["signal_date"].lt(GOLD_INCEPTION_DATE) | aligned["start_close"].isna()
    aligned["gold_quarter_return"] = aligned["end_close"] / aligned["start_close"] - 1.0
    aligned.loc[aligned["inception_cash_fallback"], "gold_quarter_return"] = 0.0
    aligned["return_source"] = aligned["inception_cash_fallback"].map(
        {True: "cash_fallback_pre_inception", False: "kodex_132030_close_to_close"}
    )
    return aligned.loc[
        :,
        [
            "signal_date",
            "start_observation_date",
            "start_close",
            "end_signal_date",
            "end_observation_date",
            "end_close",
            "gold_quarter_return",
            "inception_cash_fallback",
            "return_source",
        ],
    ]


def apply_gold_off_sleeve(
    result: BacktestResult,
    *,
    calendar: KRXTradingCalendar,
    quarterly_regime: pd.DataFrame,
    gold_csv: str | Path,
) -> tuple[BacktestResult, pd.DataFrame]:
    """Replace D013 OFF cash return with KODEX 132030 close-to-close KRW returns."""
    regime = quarterly_regime.loc[:, ["signal_date", "regime_on"]].copy()
    regime["signal_date"] = pd.to_datetime(regime["signal_date"], errors="raise").dt.normalize()
    regime = regime.sort_values("signal_date").reset_index(drop=True)

    equity = result.equity_curve.copy()
    equity["date"] = pd.to_datetime(equity["date"], errors="raise").dt.normalize()
    final_end_date = pd.Timestamp(equity["date"].iloc[-1]).normalize()
    gold_returns = load_gold_quarterly_returns(gold_csv, regime["signal_date"], final_end_date=final_end_date)
    regime = regime.merge(gold_returns, on="signal_date", how="left")
    regime["execution_date"] = [calendar.next_trading_day(date) for date in regime["signal_date"]]
    regime["next_execution_date"] = regime["execution_date"].shift(-1)

    date_index = pd.Index(equity["date"])
    daily_multiplier = pd.Series(1.0, index=date_index, dtype="float64")
    rows: list[dict[str, object]] = []
    cumulative = 1.0

    for row in regime.itertuples(index=False):
        if bool(row.regime_on):
            continue
        start = pd.Timestamp(row.execution_date).normalize()
        end = (
            pd.Timestamp(row.next_execution_date).normalize()
            if not pd.isna(row.next_execution_date)
            else final_end_date + pd.Timedelta(days=1)
        )
        mask = (date_index >= start) & (date_index < end)
        n_days = int(mask.sum())
        quarter_return = float(row.gold_quarter_return)
        if pd.isna(quarter_return):
            raise ValueError(f"Missing KODEX 132030 quarter return for signal_date {row.signal_date.date()}.")
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
                "ticker": GOLD_TICKER,
                "start_observation_date": row.start_observation_date,
                "start_close": row.start_close,
                "end_observation_date": row.end_observation_date,
                "end_close": row.end_close,
                "gold_quarter_return": quarter_return,
                "daily_gold_return": daily,
                "trading_days": n_days,
                "inception_cash_fallback": bool(row.inception_cash_fallback),
                "return_source": row.return_source,
                "cumulative_off_gold": cumulative - 1.0,
            }
        )

    sleeve_factor = daily_multiplier.cumprod()
    adjusted = equity.copy()
    for column in ("cash", "mtm_value", "gross_value", "net_value"):
        if column in adjusted.columns:
            adjusted[column] = pd.to_numeric(adjusted[column], errors="raise") * sleeve_factor.to_numpy()

    trades = _scale_trades(result.trades, sleeve_factor)
    return BacktestResult(trades=trades, equity_curve=adjusted), pd.DataFrame(rows)


def gold_sleeve_drawdown(decomposition: pd.DataFrame) -> float:
    if decomposition.empty:
        return 0.0
    values = (1.0 + pd.to_numeric(decomposition["gold_quarter_return"], errors="raise")).cumprod()
    drawdown = values / values.cummax() - 1.0
    return float(drawdown.min())


def _align_gold_close(dates: pd.DataFrame, gold: pd.DataFrame, prefix: str) -> pd.DataFrame:
    aligned = pd.merge_asof(
        dates.sort_values("signal_date"),
        gold[["date", "close"]],
        left_on="signal_date",
        right_on="date",
        direction="backward",
    )
    return aligned.rename(
        columns={
            "date": f"{prefix}_observation_date",
            "close": f"{prefix}_close",
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
