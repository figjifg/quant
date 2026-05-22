from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pandas as pd


DATE_COLUMNS = ("date", "날짜", "signal_date", "execution_date")
TICKER_COLUMNS = ("ticker", "종목코드")
TRADE_VALUE_COLUMNS = ("거래대금추정", "traded_value", "trade_value", "거래대금")
STATUS_COLUMNS = ("status", "상태", "종목상태")


def _normalize_date(value: object) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError("date is NaT")
    return ts.normalize()


def _date_column(columns: Iterable[str]) -> str:
    for column in DATE_COLUMNS:
        if column in columns:
            return column
    raise ValueError(f"no recognized date column; expected one of {DATE_COLUMNS}")


def _ticker_column(columns: Iterable[str]) -> str:
    for column in TICKER_COLUMNS:
        if column in columns:
            return column
    raise ValueError(f"no recognized ticker column; expected one of {TICKER_COLUMNS}")


def _read_panel_dates(path: Path) -> pd.Series:
    header = pd.read_csv(path, nrows=0, encoding="utf-8-sig")
    date_col = _date_column(header.columns)
    return pd.read_csv(path, encoding="utf-8-sig", usecols=[date_col], parse_dates=[date_col])[date_col]


def _is_suspended_rows(frame: pd.DataFrame) -> pd.Series:
    suspended = pd.Series(False, index=frame.index)
    for column in TRADE_VALUE_COLUMNS:
        if column in frame.columns:
            suspended |= pd.to_numeric(frame[column], errors="coerce").fillna(0).le(0)
            break
    for column in STATUS_COLUMNS:
        if column in frame.columns:
            status = frame[column].astype(str)
            suspended |= status.str.contains("정지|관리|halt|suspend", case=False, regex=True, na=False)
    return suspended


@dataclass(frozen=True)
class KoreanTradingCalendar:
    """KRX calendar derived only from local panel rows."""

    dates: tuple[pd.Timestamp, ...]
    tradable_dates_by_ticker: Mapping[str, tuple[pd.Timestamp, ...]] = field(default_factory=dict)

    @classmethod
    def load(cls, panels: Sequence[str | Path | pd.DataFrame]) -> "KoreanTradingCalendar":
        dates: list[pd.Timestamp] = []
        for panel in panels:
            if isinstance(panel, pd.DataFrame):
                date_col = _date_column(panel.columns)
                dates.extend(pd.to_datetime(panel[date_col], errors="coerce").dropna().dt.normalize().tolist())
            else:
                dates.extend(pd.to_datetime(_read_panel_dates(Path(panel)), errors="coerce").dropna().dt.normalize().tolist())
        return cls.from_dates(dates)

    @classmethod
    def from_panel(cls, panel: pd.DataFrame) -> "KoreanTradingCalendar":
        date_col = _date_column(panel.columns)
        if "KRX종가" in panel.columns:
            source = panel.loc[pd.to_numeric(panel["KRX종가"], errors="coerce").notna(), date_col]
        else:
            source = panel[date_col]
        return cls.from_dates(source)

    @classmethod
    def from_dates(cls, dates: Iterable[object]) -> "KoreanTradingCalendar":
        normalized = sorted({_normalize_date(date) for date in dates if pd.notna(date)})
        if not normalized:
            raise ValueError("calendar requires at least one trading day")
        return cls(tuple(normalized))

    def with_tradable_dates(self, panels: Sequence[str | Path | pd.DataFrame]) -> "KoreanTradingCalendar":
        return KoreanTradingCalendar(self.dates, load_tradable_dates(panels))

    def is_trading_day(self, date: object) -> bool:
        return _normalize_date(date) in set(self.dates)

    def next_trading_day(self, date: object) -> pd.Timestamp:
        target = _normalize_date(date)
        idx = bisect_right(self.dates, target)
        if idx >= len(self.dates):
            raise ValueError(f"no trading day after {target.date()}")
        return self.dates[idx]

    def prev_trading_day(self, date: object) -> pd.Timestamp:
        target = _normalize_date(date)
        idx = bisect_left(self.dates, target) - 1
        if idx < 0:
            raise ValueError(f"no trading day before {target.date()}")
        return self.dates[idx]

    def add_trading_days(self, start_date: object, n: int) -> pd.Timestamp:
        if n < 0:
            raise ValueError("n must be non-negative")
        current = _normalize_date(start_date)
        idx = bisect_right(self.dates, current) + n - 1
        if idx >= len(self.dates):
            raise ValueError(f"cannot advance {n} trading days from {current.date()}")
        return self.dates[idx]

    def n_trading_days_between(self, start: object, end: object) -> int:
        start_ts = _normalize_date(start)
        end_ts = _normalize_date(end)
        if end_ts < start_ts:
            return -self.n_trading_days_between(end_ts, start_ts)
        return bisect_right(self.dates, end_ts) - bisect_left(self.dates, start_ts)

    def trading_days_in_range(self, start: object, end: object) -> list[pd.Timestamp]:
        start_ts = _normalize_date(start)
        end_ts = _normalize_date(end)
        left = bisect_left(self.dates, start_ts)
        right = bisect_right(self.dates, end_ts)
        return list(self.dates[left:right])

    def is_tradable(self, ticker: str, date: object) -> bool:
        dates = self.tradable_dates_by_ticker.get(str(ticker), ())
        return _normalize_date(date) in set(dates)

    def next_tradable_date(self, ticker: str, date: object) -> pd.Timestamp:
        dates = self.tradable_dates_by_ticker.get(str(ticker), ())
        if not dates:
            raise ValueError(f"no tradable dates loaded for {ticker}")
        idx = bisect_right(dates, _normalize_date(date))
        if idx >= len(dates):
            raise ValueError(f"no tradable date for {ticker} after {pd.Timestamp(date).date()}")
        return dates[idx]


def load_tradable_dates(panels: Sequence[str | Path | pd.DataFrame]) -> dict[str, tuple[pd.Timestamp, ...]]:
    by_ticker: dict[str, set[pd.Timestamp]] = {}
    for panel in panels:
        if isinstance(panel, pd.DataFrame):
            frame = panel
        else:
            path = Path(panel)
            header = pd.read_csv(path, nrows=0, encoding="utf-8-sig")
            date_col = _date_column(header.columns)
            ticker_col = _ticker_column(header.columns)
            usecols = [date_col, ticker_col]
            usecols.extend([column for column in (*TRADE_VALUE_COLUMNS, *STATUS_COLUMNS) if column in header.columns])
            frame = pd.read_csv(path, encoding="utf-8-sig", usecols=sorted(set(usecols)), parse_dates=[date_col], dtype={ticker_col: str})
        date_col = _date_column(frame.columns)
        ticker_col = _ticker_column(frame.columns)
        ok = ~_is_suspended_rows(frame)
        subset = frame.loc[ok, [date_col, ticker_col]].dropna()
        subset[date_col] = pd.to_datetime(subset[date_col], errors="coerce").dt.normalize()
        for ticker, dates in subset.dropna().groupby(ticker_col)[date_col]:
            by_ticker.setdefault(str(ticker), set()).update(dates.tolist())
    return {ticker: tuple(sorted(dates)) for ticker, dates in by_ticker.items()}


def trading_day_coverage(panel: pd.DataFrame, calendar: KoreanTradingCalendar) -> float:
    """Share of panel dates that are present in the KRX calendar."""
    date_col = _date_column(panel.columns)
    dates = pd.to_datetime(panel[date_col], errors="coerce").dropna().dt.normalize()
    if dates.empty:
        return 0.0
    calendar_dates = set(calendar.dates)
    return float(dates.isin(calendar_dates).mean())
