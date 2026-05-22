from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.utils.korean_calendar import KoreanTradingCalendar


DATE_COLS = ("date", "날짜")
TICKER_COLS = ("ticker", "종목코드")
OPEN_COLS = ("adj_open", "adjusted_open", "시가adj", "시가")
HIGH_COLS = ("adj_high", "adjusted_high", "고가adj", "고가")
LOW_COLS = ("adj_low", "adjusted_low", "저가adj", "저가")
CLOSE_COLS = ("adj_close", "adjusted_close", "종가adj", "KRX종가", "종가")
TRADE_VALUE_COLS = ("거래대금추정", "traded_value", "trade_value", "거래대금")
STATUS_COLS = ("status", "상태", "종목상태")


@dataclass(frozen=True)
class TradabilityPolicy:
    require_dynamic_universe: bool = True
    exclude_estimated_traded_value: bool = True
    min_avg_traded_value_20d: float | None = None
    limit_threshold: float = 0.299


def _first(columns: pd.Index, candidates: tuple[str, ...], required: bool = True) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    if required:
        raise ValueError(f"missing required column; expected one of {candidates}")
    return None


def _date_col(panel: pd.DataFrame) -> str:
    return str(_first(panel.columns, DATE_COLS))


def _ticker_col(panel: pd.DataFrame) -> str:
    return str(_first(panel.columns, TICKER_COLS))


def tradable_mask(panel: pd.DataFrame, policy: TradabilityPolicy | None = None) -> pd.Series:
    policy = policy or TradabilityPolicy()
    ticker_col = _ticker_col(panel)
    open_col = _first(panel.columns, OPEN_COLS)
    high_col = _first(panel.columns, HIGH_COLS, required=False)
    low_col = _first(panel.columns, LOW_COLS, required=False)
    close_col = _first(panel.columns, CLOSE_COLS)
    value_col = _first(panel.columns, TRADE_VALUE_COLS, required=False)

    mask = pd.Series(True, index=panel.index)
    for column in [open_col, close_col, high_col, low_col]:
        if column is not None:
            values = pd.to_numeric(panel[column], errors="coerce")
            mask &= values.notna() & values.gt(0)
    if value_col is not None:
        value = pd.to_numeric(panel[value_col], errors="coerce")
        mask &= value.notna() & value.gt(0)
        if policy.min_avg_traded_value_20d is not None:
            avg20 = value.groupby(panel[ticker_col], sort=False).transform(lambda x: x.rolling(20, min_periods=10).mean())
            mask &= avg20.ge(policy.min_avg_traded_value_20d).fillna(False)
    if policy.exclude_estimated_traded_value and "거래대금추정여부" in panel.columns:
        mask &= ~panel["거래대금추정여부"].fillna(True).astype(bool)
    if policy.require_dynamic_universe and "동적유니버스포함" in panel.columns:
        mask &= panel["동적유니버스포함"].fillna(False).astype(bool)
    for column in STATUS_COLS:
        if column in panel.columns:
            status = panel[column].astype(str)
            mask &= ~status.str.contains("정지|관리|halt|suspend", case=False, regex=True, na=False)

    close = pd.to_numeric(panel[close_col], errors="coerce")
    prev_close = close.groupby(panel[ticker_col], sort=False).shift(1)
    open_px = pd.to_numeric(panel[open_col], errors="coerce")
    limit_open = (open_px / prev_close - 1.0).abs().ge(policy.limit_threshold).fillna(False)
    mask &= ~limit_open
    return mask.fillna(False)


def filter_tradable(panel: pd.DataFrame, policy: TradabilityPolicy | None = None) -> pd.DataFrame:
    return panel.loc[tradable_mask(panel, policy)].copy()


def mark_tradable_rows(panel: pd.DataFrame, policy: TradabilityPolicy | None = None) -> pd.DataFrame:
    out = panel.copy()
    out["tradable"] = tradable_mask(out, policy)
    return out


# Tradable state categorical values (W001 v1.x partial). Values that need
# external sources (KRX suspension status S3, corporate-action event log S2)
# are reserved here for the W001 v2 implementation but cannot be set yet.
TRADABLE_STATES = (
    "executable",
    "not_in_dynamic_universe",  # renamed from `panel_absence` in W001 v2.1
    "data_missing",
    "limit_lock_candidate",
    "true_suspension",          # set when suspension_events is supplied (W001 v2)
    "delisting_transition",     # set when suspension_events is supplied (W001 v2)
    "corporate_action_day",     # requires S2 event log; unset until W001 v2 wires C3
)

# W001 v2.1: `panel_absence` was misleading because it can be confused with
# exchange non-tradability. The semantically correct name is
# `not_in_dynamic_universe` (the ticker is listed and tradable on KRX but
# simply not in the dynamic top-100 universe for that date). Code that still
# reads the old name must be updated, but the deprecated alias below keeps
# downstream lookups from crashing while we migrate.
_DEPRECATED_TRADABLE_STATE_ALIASES = {
    "panel_absence": "not_in_dynamic_universe",
}


def tradable_state(
    panel: pd.DataFrame,
    policy: TradabilityPolicy | None = None,
    *,
    suspension_events: pd.DataFrame | None = None,
) -> pd.Series:
    """Return a categorical tradable_state per (date, ticker).

    Round 3 Step 5 audit (KR-TRADABILITY-SEMANTICS-AUDIT-001) found that the
    legacy `tradable_mask()` collapses four real causes into a single binary
    flag. This function exposes a categorical decomposition.

    Cause priority (first match wins):

    1. `data_missing` — OHLC missing/<=0 or trading-value missing/<=0 or
       trading-value flagged as estimated (vendor-imputed).
    2. `delisting_transition` — ticker has a delisting event on or before the
       row date (requires `suspension_events`).
    3. `true_suspension` — ticker is in an active KRX suspension window
       (requires `suspension_events`).
    4. `limit_lock_candidate` — open/prev_close move >= limit_threshold.
       **Still overlaps with corporate_action_day** until S2 event log lands
       (Round 3 finding: 146 of 147 extreme-return events were flagged here).
    5. `not_in_dynamic_universe` — `동적유니버스포함 == False`, the dominant
       cause in the W001 v1 panel (~82% of rows). **This is NOT a
       non-tradability signal** — the ticker is listed and tradable on KRX
       but simply not in the dynamic top-100 universe for this date.
       Renamed from `panel_absence` in W001 v2.1 (Referee Round 4.1 lock)
       because the old name could be confused with exchange-status non-tradability.
    6. `executable` — none of the above.

    Reserved enum value:
    - `corporate_action_day` — requires S2 event log; the W001 v2 wiring will
      pull these rows out of `limit_lock_candidate`.

    `suspension_events` schema (one row per status event, sorted ascending by
    date per ticker; produced by `data/processed/w001_v2/listing_status_events.csv`):
    - `ticker` (str, zero-padded 6 digit)
    - `rcept_dt` (date)
    - `category` (str: `suspension` / `resumption` / `delisting` / `managed`
      / `investor_warning` / `other`)

    Backward compatibility: if `suspension_events` is None the function returns
    the same partial categorical that W001 v1.x emitted.
    """
    policy = policy or TradabilityPolicy()
    ticker_col = _ticker_col(panel)
    date_col = _date_col(panel)
    open_col = _first(panel.columns, OPEN_COLS)
    close_col = _first(panel.columns, CLOSE_COLS)
    value_col = _first(panel.columns, TRADE_VALUE_COLS, required=False)

    open_px = pd.to_numeric(panel[open_col], errors="coerce")
    close_px = pd.to_numeric(panel[close_col], errors="coerce")
    ohlc_bad = open_px.isna() | open_px.le(0) | close_px.isna() | close_px.le(0)

    tv_bad = pd.Series(False, index=panel.index)
    if value_col is not None:
        tv = pd.to_numeric(panel[value_col], errors="coerce")
        tv_bad = tv.isna() | tv.le(0)
    if "거래대금추정여부" in panel.columns:
        tv_bad = tv_bad | panel["거래대금추정여부"].fillna(False).astype(bool)
    data_missing = ohlc_bad | tv_bad

    prev_close = close_px.groupby(panel[ticker_col], sort=False).shift(1)
    limit_open = (open_px / prev_close - 1.0).abs().ge(policy.limit_threshold).fillna(False)

    in_universe = pd.Series(True, index=panel.index)
    if policy.require_dynamic_universe and "동적유니버스포함" in panel.columns:
        in_universe = panel["동적유니버스포함"].fillna(False).astype(bool)

    state = pd.Series("executable", index=panel.index, dtype="object")
    state = state.mask(limit_open, "limit_lock_candidate")

    if suspension_events is not None and len(suspension_events) > 0:
        ev = suspension_events.copy()
        ev["ticker"] = ev["ticker"].astype(str).str.zfill(6)
        ev["rcept_dt"] = pd.to_datetime(ev["rcept_dt"])
        ev = ev.sort_values(["ticker", "rcept_dt"])

        panel_dates = pd.to_datetime(panel[date_col])
        tickers_str = panel[ticker_col].astype(str).str.zfill(6)

        # Per-ticker: build suspended_intervals (suspension → next resumption)
        # and first_delisting_date.
        delisting_by_ticker = (
            ev[ev["category"] == "delisting"].groupby("ticker")["rcept_dt"].min()
        )
        delisted_mask = tickers_str.map(delisting_by_ticker)
        delisted_mask = panel_dates.ge(delisted_mask).fillna(False)
        state = state.mask(delisted_mask, "delisting_transition")

        # Suspension: for each ticker, build interval list and mark dates inside
        suspended_mask = pd.Series(False, index=panel.index)
        ticker_to_intervals: dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}
        for tk, grp in ev.groupby("ticker"):
            intervals = []
            current_start = None
            for _, row in grp.iterrows():
                cat = row["category"]
                if cat == "suspension" and current_start is None:
                    current_start = row["rcept_dt"]
                elif cat == "resumption" and current_start is not None:
                    intervals.append((current_start, row["rcept_dt"]))
                    current_start = None
            if current_start is not None:
                intervals.append((current_start, pd.Timestamp("2100-01-01")))
            if intervals:
                ticker_to_intervals[tk] = intervals

        for idx, (tk, dt) in enumerate(zip(tickers_str.values, panel_dates.values)):
            intervals = ticker_to_intervals.get(tk)
            if not intervals:
                continue
            dt_ts = pd.Timestamp(dt)
            for start, end in intervals:
                if start <= dt_ts < end:
                    suspended_mask.iat[idx] = True
                    break
        state = state.mask(suspended_mask & ~delisted_mask, "true_suspension")

    # data_missing only applies inside the dynamic universe; rows that are
    # zero or NaN because the ticker was outside the universe should be
    # classified as not_in_dynamic_universe, not as a missing-data defect.
    state = state.mask(data_missing & in_universe, "data_missing")
    state = state.mask(~in_universe, "not_in_dynamic_universe")
    return state


def next_executable_date(
    signal_date: pd.Timestamp,
    ticker: str,
    tradability: pd.DataFrame,
    calendar: KoreanTradingCalendar,
) -> pd.Timestamp:
    date_col = _date_col(tradability)
    ticker_col = _ticker_col(tradability)
    if "tradable" not in tradability.columns:
        tradability = mark_tradable_rows(tradability)
    next_krx = calendar.next_trading_day(signal_date)
    rows = tradability.loc[
        tradability[ticker_col].astype(str).eq(str(ticker))
        & pd.to_datetime(tradability[date_col]).dt.normalize().ge(next_krx)
        & tradability["tradable"].astype(bool),
        date_col,
    ]
    if rows.empty:
        raise ValueError(f"no tradable execution date for {ticker} after {pd.Timestamp(signal_date).date()}")
    return pd.to_datetime(rows).dt.normalize().min()
