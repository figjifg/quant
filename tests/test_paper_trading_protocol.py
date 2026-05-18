from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.audit.paper_trading_protocol import (
    build_execution_record,
    build_signal_record,
    ready_for_four_quarter_review,
    write_execution_record,
    write_signal_record,
)


def test_build_signal_record_outputs_top5_equal_weight_when_regime_on(tmp_path: Path) -> None:
    quarterly = pd.DataFrame(
        [
            {"signal_date": "2026-03-31", "regime_on": True, "composite": 0.2},
        ]
    )
    candidates = pd.DataFrame(
        [
            {"signal_date": "2026-03-31", "execution_date": "2026-04-01", "종목코드": f"{i:06d}", "rank": i}
            for i in range(1, 7)
        ]
    )

    record = build_signal_record(quarterly_regime=quarterly, candidates=candidates, quarter="2026-Q1")
    path = write_signal_record(record, tmp_path)

    assert record["signal_date"] == "2026-03-31"
    assert record["execution_date"] == "2026-04-01"
    assert record["regime_on"] is True
    assert record["tickers"] == ["000001", "000002", "000003", "000004", "000005"]
    assert set(record["intended_weights"].values()) == {0.2}
    assert json.loads(path.read_text(encoding="utf-8"))["quarter"] == "2026-Q1"


def test_build_signal_record_outputs_cash_when_regime_off() -> None:
    quarterly = pd.DataFrame([{"signal_date": "2026-06-30", "regime_on": False, "composite": -0.4}])
    candidates = pd.DataFrame(
        [{"signal_date": "2026-06-30", "execution_date": "2026-07-01", "종목코드": "005930", "rank": 1}]
    )

    record = build_signal_record(quarterly_regime=quarterly, candidates=candidates, quarter="2026-Q2")

    assert record["execution_date"] is None
    assert record["tickers"] == []
    assert record["intended_weights"] == {}


def test_execution_record_tracks_slippage_and_four_quarter_readiness(tmp_path: Path) -> None:
    signal = {
        "quarter": "2026-Q1",
        "signal_date": "2026-03-31",
        "execution_date": "2026-04-01",
        "regime_on": True,
        "composite": 0.1,
        "tickers": ["005930"],
        "intended_weights": {"005930": 1.0},
    }
    fills = pd.DataFrame([{"ticker": "5930", "intended_price": 100.0, "actual_price": 101.0}])

    record = build_execution_record(signal_record=signal, fills=fills, portfolio_value=1.02)
    write_execution_record(record, tmp_path)
    for quarter in ("2026-Q2", "2026-Q3", "2026-Q4"):
        write_execution_record({**record, "quarter": quarter}, tmp_path)

    assert record["fills"][0]["ticker"] == "005930"
    assert record["fills"][0]["slippage_bps"] == pytest.approx(100.0)
    assert ready_for_four_quarter_review(tmp_path) is True
