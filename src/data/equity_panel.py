from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from src.utils.ohlcv_quarantine import apply_ohlcv_quarantine


REQUIRED_COLUMNS = (
    "날짜",
    "종목코드",
    "시가",
    "KRX종가",
    "거래대금추정",
    "시가총액추정",
    "외국인순매수금액추정",
    "기관순매수금액추정",
    "수급금액추정여부",
    "거래대금추정여부",
    "동적유니버스포함",
)

RAW_CLOSE_COLUMN = "종가"
KRX_CLOSE_SOURCE_VALUES = ("native", "from_종가_fallback")
INTEGRATION_FLAG_COLUMNS = (
    "통합거래량반영여부",
    "통합종가반영여부",
    "통합종가제외여부",
    "가격범위후보정여부",
)
BOOL_COLUMNS = (
    "수급금액추정여부",
    "거래대금추정여부",
    "동적유니버스포함",
    *INTEGRATION_FLAG_COLUMNS,
)
NUMERIC_COLUMNS = (
    "시가",
    "KRX종가",
    "거래대금추정",
    "시가총액추정",
    "외국인순매수금액추정",
    "기관순매수금액추정",
)


def load_equity_panel(paths: Sequence[str | Path]) -> pd.DataFrame:
    """Load E001 equity panels and normalize the KRX close column."""
    if not paths:
        raise ValueError("At least one equity panel path is required.")

    frames = [_read_panel(Path(path)) for path in paths]
    panel = pd.concat(frames, ignore_index=True)

    _validate_required_columns(panel)
    panel = panel.assign(
        날짜=pd.to_datetime(panel["날짜"], errors="raise").astype("datetime64[ns]"),
        종목코드=panel["종목코드"].astype("string"),
    )

    for column in BOOL_COLUMNS:
        panel[column] = _coerce_bool_column(panel[column], column)

    for column in NUMERIC_COLUMNS:
        panel[column] = pd.to_numeric(panel[column], errors="raise")

    source_dtype = pd.CategoricalDtype(categories=KRX_CLOSE_SOURCE_VALUES)
    panel["krx_close_source"] = panel["krx_close_source"].astype(source_dtype)

    panel = panel.sort_values(["종목코드", "날짜"]).reset_index(drop=True)

    # Per `KR_OHLCV_QUARANTINE_PATCH_PHASE`: emit valid_ohlcv_mask + reason codes so
    # downstream code can filter invalid rows (S1-S6 signatures). Annotation mode
    # preserves row count; downstream consumers must apply the mask.
    panel = apply_ohlcv_quarantine(panel, mode="annotate")
    return panel


def _read_panel(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype={"종목코드": "string"})

    if RAW_CLOSE_COLUMN not in frame.columns:
        raise ValueError(f"{path} is missing required raw close column: {RAW_CLOSE_COLUMN}")

    if "KRX종가" in frame.columns:
        mismatch = frame[RAW_CLOSE_COLUMN].ne(frame["KRX종가"])
        mismatch = mismatch & ~(frame[RAW_CLOSE_COLUMN].isna() & frame["KRX종가"].isna())
        if bool(mismatch.any()):
            count = int(mismatch.sum())
            raise ValueError(f"{path} has {count} rows where 종가 != KRX종가")
        frame = frame.assign(krx_close_source="native")
    else:
        frame = frame.assign(KRX종가=frame[RAW_CLOSE_COLUMN], krx_close_source="from_종가_fallback")

    missing_integration_flags = [
        column for column in INTEGRATION_FLAG_COLUMNS if column not in frame.columns
    ]
    if missing_integration_flags:
        frame = frame.assign(**{column: False for column in missing_integration_flags})

    return frame


def _validate_required_columns(panel: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in panel.columns]
    if missing:
        raise ValueError(f"Missing required equity panel columns: {missing}")


def _coerce_bool_column(series: pd.Series, column: str) -> pd.Series:
    valid_strings = {"True": True, "False": False}

    def coerce_value(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value in valid_strings:
            return valid_strings[value]
        raise ValueError(f"{column} contains non-boolean value: {value!r}")

    return series.map(coerce_value).astype(bool)
