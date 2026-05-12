from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class KRXTradingCalendar:
    """KRX trading-day calendar derived from panel rows with non-null KRX close."""

    dates: tuple[pd.Timestamp, ...]

    def __post_init__(self) -> None:
        normalized = tuple(sorted({_to_timestamp(date) for date in self.dates}))
        if not normalized:
            raise ValueError("Trading calendar cannot be empty.")
        object.__setattr__(self, "dates", normalized)
        object.__setattr__(self, "_date_set", frozenset(normalized))

    @classmethod
    def from_panel(cls, panel: pd.DataFrame) -> KRXTradingCalendar:
        if "날짜" not in panel.columns or "KRX종가" not in panel.columns:
            raise ValueError("Panel must contain 날짜 and KRX종가 columns.")

        valid_dates = panel.loc[panel["KRX종가"].notna(), "날짜"]
        return cls(pd.to_datetime(valid_dates, errors="raise"))

    def next_trading_day(self, date: object) -> pd.Timestamp:
        target = _to_timestamp(date)
        index = self._first_index_after(target)
        if index >= len(self.dates):
            raise ValueError(f"No trading day after {target.date()} is in the calendar.")
        return self.dates[index]

    def add_trading_days(self, date: object, n: int) -> pd.Timestamp:
        if n < 0:
            raise ValueError("n must be non-negative.")

        target = _to_timestamp(date)
        if n == 0:
            if target not in self._date_set:
                raise ValueError(f"{target.date()} is not a trading day in the calendar.")
            return target

        index = self._first_index_after(target) + n - 1
        if index >= len(self.dates):
            raise ValueError(f"Cannot add {n} trading days after {target.date()}: out of range.")
        return self.dates[index]

    def _first_index_after(self, target: pd.Timestamp) -> int:
        return int(pd.Index(self.dates).searchsorted(target, side="right"))


def derive_trading_calendar(panel: pd.DataFrame) -> KRXTradingCalendar:
    return KRXTradingCalendar.from_panel(panel)


def _to_timestamp(date: object) -> pd.Timestamp:
    timestamp = pd.Timestamp(date)
    if timestamp.tz is not None:
        timestamp = timestamp.tz_localize(None)
    return timestamp.normalize()
