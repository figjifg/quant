from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


SIGNAL_RECORD_KEYS = (
    "quarter",
    "signal_date",
    "execution_date",
    "regime_on",
    "composite",
    "tickers",
    "intended_weights",
)


def quarter_label(date: object) -> str:
    timestamp = pd.Timestamp(date).normalize()
    return f"{timestamp.year}-Q{timestamp.quarter}"


def signal_row_for_quarter(quarterly_regime: pd.DataFrame, quarter: str | None = None) -> pd.Series:
    if quarterly_regime.empty:
        raise ValueError("quarterly_regime is empty.")
    required = {"signal_date", "regime_on", "composite"}
    missing = sorted(required - set(quarterly_regime.columns))
    if missing:
        raise ValueError(f"quarterly_regime is missing required columns: {missing}")

    data = quarterly_regime.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["quarter"] = data["signal_date"].map(quarter_label)
    if quarter is not None:
        data = data.loc[data["quarter"].eq(quarter)]
        if data.empty:
            raise ValueError(f"No D013 quarterly regime row for {quarter}.")
    return data.sort_values("signal_date").iloc[-1]


def build_signal_record(
    *,
    quarterly_regime: pd.DataFrame,
    candidates: pd.DataFrame,
    quarter: str | None = None,
    max_positions: int = 5,
) -> dict[str, Any]:
    row = signal_row_for_quarter(quarterly_regime, quarter)
    signal_date = pd.Timestamp(row["signal_date"]).normalize()
    target_quarter = str(row["quarter"])
    regime_on = bool(row["regime_on"])

    selected = _selected_candidates(candidates, signal_date, max_positions=max_positions) if regime_on else pd.DataFrame()
    tickers = selected["종목코드"].astype(str).str.zfill(6).tolist() if not selected.empty else []
    weight = 1.0 / len(tickers) if tickers else 0.0
    execution_date = _execution_date(selected)

    return {
        "quarter": target_quarter,
        "signal_date": signal_date.date().isoformat(),
        "execution_date": execution_date,
        "regime_on": regime_on,
        "composite": _json_float(row["composite"]),
        "tickers": tickers,
        "intended_weights": {ticker: weight for ticker in tickers},
    }


def write_signal_record(record: dict[str, Any], output_root: str | Path) -> Path:
    _validate_signal_record(record)
    path = Path(output_root) / "signals" / f"{record['quarter']}.json"
    _write_json(path, record)
    return path


def build_execution_record(
    *,
    signal_record: dict[str, Any],
    fills: pd.DataFrame,
    portfolio_value: float,
) -> dict[str, Any]:
    _validate_signal_record(signal_record)
    required = {"ticker", "intended_price", "actual_price"}
    missing = sorted(required - set(fills.columns))
    if missing:
        raise ValueError(f"fills is missing required columns: {missing}")

    rows = []
    data = fills.copy()
    data["ticker"] = data["ticker"].astype(str).str.zfill(6)
    for _, row in data.iterrows():
        intended = float(row["intended_price"])
        actual = float(row["actual_price"])
        slippage_bps = (actual / intended - 1.0) * 1e4 if intended > 0.0 else float("nan")
        rows.append(
            {
                "ticker": str(row["ticker"]),
                "intended_price": intended,
                "actual_price": actual,
                "slippage_bps": _json_float(slippage_bps),
            }
        )

    return {
        "quarter": signal_record["quarter"],
        "signal_date": signal_record["signal_date"],
        "execution_date": signal_record["execution_date"],
        "portfolio_value": float(portfolio_value),
        "fills": rows,
    }


def write_execution_record(record: dict[str, Any], output_root: str | Path) -> Path:
    quarter = str(record["quarter"])
    path = Path(output_root) / "executions" / f"{quarter}.json"
    _write_json(path, record)
    return path


def completed_execution_quarters(output_root: str | Path) -> list[str]:
    path = Path(output_root) / "executions"
    if not path.exists():
        return []
    return sorted(file.stem for file in path.glob("*.json"))


def ready_for_four_quarter_review(output_root: str | Path) -> bool:
    return len(completed_execution_quarters(output_root)) >= 4


def _selected_candidates(candidates: pd.DataFrame, signal_date: pd.Timestamp, *, max_positions: int) -> pd.DataFrame:
    required = {"signal_date", "execution_date", "종목코드", "rank"}
    missing = sorted(required - set(candidates.columns))
    if missing:
        raise ValueError(f"candidates is missing required columns: {missing}")
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    selected = data.loc[data["signal_date"].eq(signal_date)].copy()
    return selected.sort_values(["rank", "종목코드"]).head(max_positions)


def _execution_date(selected: pd.DataFrame) -> str | None:
    if selected.empty:
        return None
    dates = pd.to_datetime(selected["execution_date"], errors="raise").dt.normalize().drop_duplicates()
    if len(dates) != 1:
        raise ValueError("selected candidates must have exactly one execution_date.")
    return dates.iloc[0].date().isoformat()


def _validate_signal_record(record: dict[str, Any]) -> None:
    missing = [key for key in SIGNAL_RECORD_KEYS if key not in record]
    if missing:
        raise ValueError(f"signal record is missing keys: {missing}")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_float(value: object) -> float | None:
    if pd.isna(value):
        return None
    return float(value)
