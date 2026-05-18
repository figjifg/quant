from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.f002_stock_rs_d013_direct import build_f002_stock_rs_d013_direct_candidates
from src.strategies.f002_stock_rs_e014 import build_f002_stock_rs_e014_candidates


def test_f002_d013_direct_selects_universe_wide_stock_rs_top5() -> None:
    candidates = build_f002_stock_rs_d013_direct_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        stock_scores=_stock_scores(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
        top_n=5,
    )

    assert candidates["종목코드"].tolist() == ["000012", "000011", "000010", "000009", "000008"]
    assert candidates["execution_date"].eq(pd.Timestamp("2025-04-01")).all()
    assert candidates["stock_rs_score_universe"].is_monotonic_decreasing


def test_f002_e014_selects_stock_rs_within_selected_top4_sectors() -> None:
    candidates = build_f002_stock_rs_e014_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        combined_scores=_combined_scores(),
        stock_scores=_stock_scores(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    )

    assert candidates.groupby("sector_code").size().to_dict() == {"01": 2, "02": 1, "03": 1, "04": 1}
    assert candidates.loc[candidates["sector_code"].eq("01"), "종목코드"].tolist() == ["000003", "000002"]
    assert candidates["target_weight"].sum() == pytest.approx(1.0)


def _panel() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 13)]
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-03-31")] * len(tickers),
            "종목코드": tickers,
            "KRX종가": [100.0] * len(tickers),
            "상장주식수": list(range(1001, 1013)),
        }
    )


def _universe() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 13)]
    return pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-03-31")] * len(tickers),
            "execution_date": [pd.Timestamp("2025-04-01")] * len(tickers),
            "종목코드": tickers,
        }
    )


def _quarterly_regime() -> pd.DataFrame:
    return pd.DataFrame({"signal_date": [pd.Timestamp("2025-03-31")], "regime_on": [True]})


def _stock_scores() -> pd.DataFrame:
    rows = []
    for sector_index, sector_code in enumerate(("01", "02", "03", "04"), start=0):
        for offset in range(3):
            ticker_number = sector_index * 3 + offset + 1
            rows.append(
                {
                    "signal_date": pd.Timestamp("2025-03-31"),
                    "ticker": f"{ticker_number:06d}",
                    "sector_code": sector_code,
                    "sector_name": f"Sector {sector_code}",
                    "raw_stock_rs_score": float(ticker_number),
                    "stock_rs_score": float(offset),
                }
            )
    return pd.DataFrame(rows)


def _combined_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-03-31")] * 4,
            "sector_code": ["01", "02", "03", "04"],
            "sector_name": ["Sector 01", "Sector 02", "Sector 03", "Sector 04"],
            "flow_score": [0.0, 0.0, 0.0, 0.0],
            "rs_score": [4.0, 3.0, 2.0, 1.0],
            "breadth_score": [4.0, 3.0, 2.0, 1.0],
            "combined_score": [4.0, 3.0, 2.0, 1.0],
        }
    )
