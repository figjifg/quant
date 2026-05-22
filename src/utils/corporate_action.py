from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


DATE_COLS = ("date", "날짜")
TICKER_COLS = ("ticker", "종목코드")
OHLC_MAP = {
    "open": ("adjusted_open", "시가adj", "시가"),
    "high": ("adjusted_high", "고가adj", "고가"),
    "low": ("adjusted_low", "저가adj", "저가"),
    "close": ("adjusted_close", "종가adj", "KRX종가", "종가"),
}


@dataclass(frozen=True)
class CorporateActionPolicy:
    adjusted_close_column: str = "adjusted_close"
    raw_close_column: str = "KRX종가"
    max_abs_single_period_return: float = 0.50
    split_gap_threshold: float = 0.05


def _first(columns: pd.Index, candidates: tuple[str, ...]) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"missing required column; expected one of {candidates}")


def _date_col(panel: pd.DataFrame) -> str:
    return _first(panel.columns, DATE_COLS)


def _ticker_col(panel: pd.DataFrame) -> str:
    return _first(panel.columns, TICKER_COLS)


def _preferred_price_columns(panel: pd.DataFrame) -> dict[str, str]:
    return {field: _first(panel.columns, candidates) for field, candidates in OHLC_MAP.items() if any(c in panel.columns for c in candidates)}


def _assert_krx_close(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    if "KRX종가" not in out.columns:
        if "종가" not in out.columns:
            raise ValueError("panel needs KRX종가 or 종가")
        out["KRX종가"] = out["종가"]
        out["krx_close_source"] = "synthesized_from_close"
    elif "종가" in out.columns:
        mismatch = out["KRX종가"].notna() & out["종가"].notna() & (pd.to_numeric(out["KRX종가"], errors="coerce") != pd.to_numeric(out["종가"], errors="coerce"))
        if mismatch.any():
            raise ValueError(f"종가 != KRX종가 rows: {int(mismatch.sum())}")
        out["krx_close_source"] = out.get("krx_close_source", "on_disk_krx_close")
    else:
        out["krx_close_source"] = out.get("krx_close_source", "on_disk_krx_close")
    return out


def detect_impossible_returns(panel: pd.DataFrame, threshold: float = 0.50) -> pd.DataFrame:
    date_col = _date_col(panel)
    ticker_col = _ticker_col(panel)
    close_col = _first(panel.columns, OHLC_MAP["close"])
    data = panel[[date_col, ticker_col, close_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[close_col] = pd.to_numeric(data[close_col], errors="coerce")
    data = data.sort_values([ticker_col, date_col])
    data["return"] = data.groupby(ticker_col, sort=False)[close_col].pct_change()
    bad = data.loc[data["return"].abs().gt(threshold).fillna(False), [ticker_col, date_col, "return"]].copy()
    bad.columns = ["ticker", "date", "return"]
    bad["flag"] = "ABS_DAILY_RETURN_GT_50PCT"
    return bad.reset_index(drop=True)


def adjust_for_corporate_actions(panel: pd.DataFrame, policy: CorporateActionPolicy | None = None) -> pd.DataFrame:
    """Add corporate-action audit metadata to a panel. **Does not actually adjust prices.**

    Function name is misleading and kept only for backward compatibility. Round 3
    Step 5 audit (KR-G5-ADJOHLC-CORPACT-AUDIT-001) confirmed that:

    - If panel has no adjusted_* columns, this function creates them as aliases
      pointing to the raw `시가`/`고가`/`저가`/`종가` values. **The values are
      identical to raw — no split / 증자 / 감자 factor is applied.**
    - `adjustment_factor` column carries reverse factors only for split-like
      rows (|daily return| > 50%); the factor is not applied to price values.
    - Downstream callers must not assume adjusted_close is a true adjusted
      price. Use `*_source` column or `adjusted_*_source == 'unadjusted_raw_alias'`
      check to detect this state.

    Defects registered in Round 3:
    - G5_000002 (adjusted_column_is_raw_alias, critical)
    - G5_000003 (metadata_only_no_actual_adjustment, high)

    Real adjustment requires:
    - S1 Adjusted OHLC source (vendor / KRX 공식 / 자체 계산)
    - S2 Corporate Action Event Log
    - W001 v2 new function `apply_corporate_action_adjustment(event_log, panel)`
      (per `docs/W001_v2_infrastructure_repair_plan.md` Component C1+C2+C3)

    See `docs/adjustment_engine_requirements.md` and
    `docs/W001_v2_infrastructure_repair_plan.md` for repair plan.

    Returns the panel with `adjusted_*` aliases, `corporate_action_candidate`
    flag (|return| > 5%), `impossible_return_flag` (|return| > 50%), and
    `adjustment_factor` metadata.
    """
    policy = policy or CorporateActionPolicy()
    out = _assert_krx_close(panel)
    date_col = _date_col(out)
    ticker_col = _ticker_col(out)
    price_cols = _preferred_price_columns(out)
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out.sort_values([ticker_col, date_col]).reset_index(drop=True)
    for field, source in price_cols.items():
        out[source] = pd.to_numeric(out[source], errors="coerce")
        out[f"adjusted_{field}"] = out[source]
        # NOTE: this is an alias to the raw column, NOT a real adjusted price.
        # The source value distinguishes it from a real adjustment that would
        # be marked with sources like 'vendor', 'krx_official', or
        # 'self_calculated' once W001 v2 lands.
        out[f"adjusted_{field}_source"] = "unadjusted_raw_alias"

    close = out["adjusted_close"]
    ret = close.groupby(out[ticker_col], sort=False).pct_change()
    out["corporate_action_candidate"] = ret.abs().gt(policy.split_gap_threshold).fillna(False)
    split_like = ret.abs().gt(policy.max_abs_single_period_return).fillna(False)
    out["impossible_return_flag"] = split_like
    out["adjustment_factor"] = 1.0
    if split_like.any():
        # Fail-soft adjustment metadata: leave prices intact for auditability,
        # expose split-like rows to the impossible-return checks. To actually
        # adjust prices, W001 v2 will introduce `apply_corporate_action_adjustment`
        # which takes an event log.
        out.loc[split_like, "adjustment_factor"] = 1.0 / (1.0 + ret.loc[split_like])
    return out


def validate_adjusted_prices(panel: pd.DataFrame, policy: CorporateActionPolicy) -> pd.DataFrame:
    adjusted = adjust_for_corporate_actions(panel, policy)
    close = pd.to_numeric(adjusted["adjusted_close"], errors="coerce")
    invalid = close.isna() | close.le(0)
    if invalid.any():
        raise ValueError(f"invalid adjusted close rows: {int(invalid.sum())}")
    return adjusted


def compute_adjusted_returns(panel: pd.DataFrame, policy: CorporateActionPolicy | None = None) -> pd.DataFrame:
    policy = policy or CorporateActionPolicy()
    adjusted = validate_adjusted_prices(panel, policy)
    ticker_col = _ticker_col(adjusted)
    adjusted["adjusted_return_1d"] = adjusted.groupby(ticker_col, sort=False)["adjusted_close"].pct_change()
    return adjusted


def detect_impossible_trade_returns(trades: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
    candidates = [column for column in ("gross_return", "net_return", "return") if column in trades.columns]
    if not candidates:
        return pd.DataFrame(columns=["ticker", "date", "return", "flag"])
    col = candidates[0]
    bad = trades.loc[pd.to_numeric(trades[col], errors="coerce").abs().gt(threshold).fillna(False)].copy()
    if bad.empty:
        return pd.DataFrame(columns=["ticker", "date", "return", "flag"])
    return pd.DataFrame(
        {
            "ticker": bad.get("ticker", bad.get("종목코드", "")),
            "date": bad.get("exit_date", bad.get("date", "")),
            "return": pd.to_numeric(bad[col], errors="coerce"),
            "flag": "ABS_TRADE_RETURN_GT_100PCT",
        }
    ).reset_index(drop=True)
