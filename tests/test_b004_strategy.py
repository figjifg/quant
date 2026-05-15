from __future__ import annotations

import pandas as pd

from src.strategies.b004_regime_gate import build_gate_only_equal_weight_candidates


def test_gate_only_candidates_use_top_five_market_cap_with_lexical_tiebreak() -> None:
    signal_date = pd.Timestamp("2025-01-02")
    execution_date = pd.Timestamp("2025-01-03")
    tickers = ["000006", "000005", "000004", "000003", "000002", "000001"]
    panel = pd.DataFrame(
        [
            {
                "날짜": signal_date,
                "종목코드": ticker,
                "KRX종가": 10.0,
                "상장주식수": shares,
            }
            for ticker, shares in zip(tickers, [10, 20, 30, 40, 50, 50], strict=False)
        ]
    )
    universe = pd.DataFrame(
        {
            "execution_date": [execution_date] * len(tickers),
            "signal_date": [signal_date] * len(tickers),
            "종목코드": tickers,
        }
    )
    gate = pd.Series([True], index=pd.Index([signal_date], name="date"))

    candidates = build_gate_only_equal_weight_candidates(panel, universe, gate, max_positions=5)

    assert candidates["종목코드"].tolist() == ["000001", "000002", "000003", "000004", "000005"]
    assert candidates["rank"].tolist() == [1, 2, 3, 4, 5]
    assert candidates["combined_flow_5"].tolist() == [500.0, 500.0, 400.0, 300.0, 200.0]


def test_gate_only_candidates_skip_gate_off_dates() -> None:
    signal_date = pd.Timestamp("2025-01-02")
    panel = pd.DataFrame(
        [{"날짜": signal_date, "종목코드": "000001", "KRX종가": 10.0, "상장주식수": 10}]
    )
    universe = pd.DataFrame(
        {
            "execution_date": [pd.Timestamp("2025-01-03")],
            "signal_date": [signal_date],
            "종목코드": ["000001"],
        }
    )
    gate = pd.Series([False], index=pd.Index([signal_date], name="date"))

    candidates = build_gate_only_equal_weight_candidates(panel, universe, gate, max_positions=5)

    assert candidates.empty
