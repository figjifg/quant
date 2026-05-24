"""Shared invalid-OHLCV-row quarantine utility.

Per `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`.
S1-S6 signatures. Fail-closed on missing required columns. No return / signal / NAV
computation. Measurement-layer infrastructure only.
"""
from __future__ import annotations

import datetime as _dt
from typing import Iterable

import numpy as np
import pandas as pd

# Reason code constants (S1-S6)
S1 = "S1_vendor_non_trading_forward"
S2 = "S2_nonpos_price"
S3 = "S3_ohlc_order_violation"
S4 = "S4_neg_volume_or_value"
S5 = "S5_tv_estimated_mismatch"
S6 = "S6_adj_missing"

INVALID_ROW_REASON_CODES = (S1, S2, S3, S4, S5, S6)

DEFAULT_PRICE_COLS = ("시가", "고가", "저가", "종가")
DEFAULT_ADJUSTED_PRICE_COLS = ("adj_open", "adj_high", "adj_low", "adj_close")
DEFAULT_VOLUME_COL = "거래량"
DEFAULT_ADJUSTED_VOLUME_COL = "adj_volume"
DEFAULT_VALUE_COL = "거래대금추정"
DEFAULT_VALUE_FLAG_COL = "거래대금추정여부"

ANNOTATION_VALID_MASK_COL = "valid_ohlcv_mask"
ANNOTATION_REASON_COL = "invalid_ohlcv_reason_codes"
ANNOTATION_RUN_COL = "ohlcv_quarantine_run_at"

_GUARD_ACK_LOG: list[tuple[str, str]] = []


class OhlcvQuarantineError(RuntimeError):
    """Raised on missing required columns or invalid-row policy violations."""


def _choose_price_cols(df: pd.DataFrame, price_cols: Iterable[str] | None) -> list[str]:
    if price_cols is not None:
        chosen = list(price_cols)
        missing = [c for c in chosen if c not in df.columns]
        if missing:
            raise OhlcvQuarantineError(
                f"requested price_cols missing from dataframe: {missing}"
            )
        return chosen
    raw_present = [c for c in DEFAULT_PRICE_COLS if c in df.columns]
    if len(raw_present) == 4:
        return raw_present
    adj_present = [c for c in DEFAULT_ADJUSTED_PRICE_COLS if c in df.columns]
    if len(adj_present) == 4:
        return adj_present
    raise OhlcvQuarantineError(
        "no full OHLC quartet found; expected either Korean raw columns "
        f"{DEFAULT_PRICE_COLS} or adjusted columns {DEFAULT_ADJUSTED_PRICE_COLS}"
    )


def _choose_volume_col(df: pd.DataFrame, volume_col: str | None) -> str | None:
    if volume_col is not None:
        if volume_col not in df.columns:
            raise OhlcvQuarantineError(
                f"requested volume_col '{volume_col}' missing from dataframe"
            )
        return volume_col
    for cand in (DEFAULT_VOLUME_COL, DEFAULT_ADJUSTED_VOLUME_COL):
        if cand in df.columns:
            return cand
    return None  # OK — volume check is optional


def _choose_value_col(df: pd.DataFrame, value_col: str | None) -> str | None:
    if value_col is not None:
        if value_col not in df.columns:
            raise OhlcvQuarantineError(
                f"requested value_col '{value_col}' missing from dataframe"
            )
        return value_col
    return DEFAULT_VALUE_COL if DEFAULT_VALUE_COL in df.columns else None


def _choose_value_flag_col(df: pd.DataFrame, value_flag_col: str | None) -> str | None:
    if value_flag_col is not None:
        if value_flag_col not in df.columns:
            raise OhlcvQuarantineError(
                f"requested value_flag_col '{value_flag_col}' missing from dataframe"
            )
        return value_flag_col
    return DEFAULT_VALUE_FLAG_COL if DEFAULT_VALUE_FLAG_COL in df.columns else None


def _signature_masks(
    df: pd.DataFrame,
    *,
    price_cols: list[str],
    volume_col: str | None,
    value_col: str | None,
    value_flag_col: str | None,
    require_adjusted: bool,
) -> dict[str, pd.Series]:
    """Return one boolean mask per signature."""
    # Convert price columns to float64 with NaN-safe semantics
    op = df[price_cols[0]].astype("float64")
    hi = df[price_cols[1]].astype("float64")
    lo = df[price_cols[2]].astype("float64")
    cl = df[price_cols[3]].astype("float64")

    # S1: OHL == 0 AND close > 0 (vendor non-trading forward)
    s1 = (op == 0) & (hi == 0) & (lo == 0) & (cl > 0)

    # S2: any price <= 0 OR any price is NaN (fail-closed for missing price data)
    s2 = (op <= 0) | (hi <= 0) | (lo <= 0) | (cl <= 0) | op.isna() | hi.isna() | lo.isna() | cl.isna()

    # S3: OHLC ordering violation (NaN-safe: NaN comparisons return False)
    s3 = (hi < lo) | (hi < op) | (hi < cl) | (lo > op) | (lo > cl)

    # S4: negative volume / value
    if volume_col is not None and value_col is not None:
        v = df[volume_col].astype("float64")
        tv = df[value_col].astype("float64")
        s4 = (v < 0) | (tv < 0)
    elif volume_col is not None:
        v = df[volume_col].astype("float64")
        s4 = v < 0
    elif value_col is not None:
        tv = df[value_col].astype("float64")
        s4 = tv < 0
    else:
        s4 = pd.Series(False, index=df.index)

    # S5: estimated trading-value mismatch (only when value_flag_col == True)
    if value_flag_col is not None and value_col is not None:
        flag = df[value_flag_col].astype("string").str.strip().eq("True")
        # Some panels may already be bool dtype; coerce safely
        if not flag.any():
            flag = df[value_flag_col].fillna(False).astype(bool)
        v = df[volume_col].astype("float64") if volume_col else pd.Series(np.nan, index=df.index)
        tv = df[value_col].astype("float64")
        expected = cl * v
        denom = expected.abs().replace(0, np.nan)
        rel_diff = (tv - expected).abs() / denom
        s5 = flag & (rel_diff > 1e-6) & rel_diff.notna()
    else:
        s5 = pd.Series(False, index=df.index)

    # S6: adjusted columns required but missing
    if require_adjusted:
        adj_present = all(c in df.columns for c in DEFAULT_ADJUSTED_PRICE_COLS)
        if not adj_present:
            s6 = pd.Series(True, index=df.index)
        else:
            adj_close = df["adj_close"].astype("float64")
            s6 = adj_close.isna() & cl.notna()
    else:
        s6 = pd.Series(False, index=df.index)

    return {S1: s1, S2: s2, S3: s3, S4: s4, S5: s5, S6: s6}


def invalid_ohlcv_mask(
    df: pd.DataFrame,
    *,
    price_cols: Iterable[str] | None = None,
    volume_col: str | None = None,
    value_col: str | None = None,
    value_flag_col: str | None = None,
    require_adjusted: bool = False,
    mode: str = "any",
) -> pd.Series:
    """Return a boolean Series; True means the row is INVALID per S1-S6.

    Fails closed on missing required columns.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if mode not in ("any", "all"):
        raise ValueError(f"mode must be 'any' or 'all', got {mode!r}")

    price_cols_resolved = _choose_price_cols(df, price_cols)
    volume_col_resolved = _choose_volume_col(df, volume_col)
    value_col_resolved = _choose_value_col(df, value_col)
    value_flag_col_resolved = _choose_value_flag_col(df, value_flag_col)

    sigs = _signature_masks(
        df,
        price_cols=price_cols_resolved,
        volume_col=volume_col_resolved,
        value_col=value_col_resolved,
        value_flag_col=value_flag_col_resolved,
        require_adjusted=require_adjusted,
    )

    if mode == "any":
        out = pd.Series(False, index=df.index)
        for m in sigs.values():
            out |= m
    else:  # "all"
        out = pd.Series(True, index=df.index)
        for m in sigs.values():
            out &= m
    return out


def _reason_codes_for_rows(sigs: dict[str, pd.Series]) -> pd.Series:
    """Pipe-joined reason-code strings per row; empty when row is valid."""
    # Stack signatures into a 2D mask
    code_names = list(sigs.keys())
    mat = pd.concat([sigs[c] for c in code_names], axis=1)
    mat.columns = code_names

    def join_codes(row: pd.Series) -> str:
        return "|".join([c for c, v in row.items() if bool(v)])

    return mat.apply(join_codes, axis=1)


def apply_ohlcv_quarantine(
    df: pd.DataFrame,
    *,
    mode: str = "filter",
    price_cols: Iterable[str] | None = None,
    volume_col: str | None = None,
    value_col: str | None = None,
    value_flag_col: str | None = None,
    require_adjusted: bool = False,
) -> pd.DataFrame:
    """Apply quarantine. `mode` in {"filter", "mask", "annotate"}."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if mode not in ("filter", "mask", "annotate"):
        raise ValueError(f"mode must be 'filter', 'mask', or 'annotate', got {mode!r}")

    price_cols_resolved = _choose_price_cols(df, price_cols)
    volume_col_resolved = _choose_volume_col(df, volume_col)
    value_col_resolved = _choose_value_col(df, value_col)
    value_flag_col_resolved = _choose_value_flag_col(df, value_flag_col)

    sigs = _signature_masks(
        df,
        price_cols=price_cols_resolved,
        volume_col=volume_col_resolved,
        value_col=value_col_resolved,
        value_flag_col=value_flag_col_resolved,
        require_adjusted=require_adjusted,
    )
    invalid = pd.Series(False, index=df.index)
    for m in sigs.values():
        invalid |= m

    if mode == "filter":
        return df.loc[~invalid].copy()

    if mode == "mask":
        out = df.copy()
        # NaN out price + volume + value columns on invalid rows
        cols_to_nan = list(price_cols_resolved)
        if volume_col_resolved is not None:
            cols_to_nan.append(volume_col_resolved)
        if value_col_resolved is not None:
            cols_to_nan.append(value_col_resolved)
        for c in cols_to_nan:
            out.loc[invalid, c] = np.nan
        return out

    # annotate
    out = df.copy()
    out[ANNOTATION_VALID_MASK_COL] = ~invalid
    out[ANNOTATION_REASON_COL] = _reason_codes_for_rows(sigs)
    out[ANNOTATION_RUN_COL] = _dt.datetime.now().isoformat(timespec="seconds")
    return out


def assert_no_invalid_ohlcv(
    df: pd.DataFrame,
    *,
    context: str,
    price_cols: Iterable[str] | None = None,
    volume_col: str | None = None,
    value_col: str | None = None,
    value_flag_col: str | None = None,
    require_adjusted: bool = False,
) -> None:
    """Hard gate: raise OhlcvQuarantineError if any invalid row remains in df."""
    mask = invalid_ohlcv_mask(
        df,
        price_cols=price_cols,
        volume_col=volume_col,
        value_col=value_col,
        value_flag_col=value_flag_col,
        require_adjusted=require_adjusted,
    )
    if not mask.any():
        return
    bad_idx = df.index[mask][:10].tolist()
    raise OhlcvQuarantineError(
        f"assert_no_invalid_ohlcv failed at {context!r}: "
        f"{int(mask.sum())} invalid rows; first up to 10 index values = {bad_idx}"
    )


def assert_panel_has_valid_mask(df: pd.DataFrame, *, context: str) -> None:
    """Lightweight hard gate: panel must carry the loader-emitted valid_ohlcv_mask.

    Use at the entry of any function that consumes a Korean equity panel for value
    derivation. Distinct from `assert_no_invalid_ohlcv`, which also asserts that no
    invalid row remains; this function only asserts the annotation column is present.

    Per KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE, this is the canonical fail-closed
    helper for closed-strategy guard hardening: closed strategies remain closed, but
    if they were ever reactivated this raises immediately when the loader-side
    annotation is missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if ANNOTATION_VALID_MASK_COL not in df.columns:
        raise OhlcvQuarantineError(
            f"assert_panel_has_valid_mask failed at {context!r}: panel missing "
            f"`{ANNOTATION_VALID_MASK_COL}`; load via "
            "src.data.equity_panel.load_equity_panel which annotates it"
        )


def require_guarded_field_use(field_name: str, context: str) -> None:
    """Annotate that the caller is using an ALLOW_WITH_GUARD field and has applied a guard.

    No side effect on dataframes. Records the (field, context) pair in the in-memory
    `_GUARD_ACK_LOG` so audits / tests can verify the contract.
    """
    if not isinstance(field_name, str) or not field_name:
        raise TypeError("field_name must be a non-empty string")
    if not isinstance(context, str) or not context:
        raise TypeError("context must be a non-empty string")
    _GUARD_ACK_LOG.append((field_name, context))


def get_guard_ack_log() -> list[tuple[str, str]]:
    return list(_GUARD_ACK_LOG)


def clear_guard_ack_log() -> None:
    _GUARD_ACK_LOG.clear()
