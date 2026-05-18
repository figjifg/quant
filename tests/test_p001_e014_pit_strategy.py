from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.p001_e014_pit import build_p001_e014_pit_candidates


def test_p001_e014_pit_uses_signal_date_sector_mapping() -> None:
    candidates = build_p001_e014_pit_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=pd.DataFrame({"signal_date": [pd.Timestamp("2025-03-31")], "regime_on": [True]}),
        combined_scores=_combined_scores(),
        pit_sector_mapping=_pit_mapping(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    )

    assert len(candidates) == 5
    assert candidates.groupby("sector_code").size().to_dict() == {"01": 2, "02": 1, "03": 1, "04": 1}
    assert set(candidates.loc[candidates["sector_code"].eq("01"), "종목코드"]) == {"000001", "000002"}


def _panel() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 13)]
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-03-31")] * len(tickers),
            "종목코드": tickers,
            "KRX종가": [100.0] * len(tickers),
            "상장주식수": list(range(1012, 1000, -1)),
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


def _pit_mapping() -> pd.DataFrame:
    rows = []
    sectors = ["01", "01", "01", "02", "02", "02", "03", "03", "03", "04", "04", "04"]
    stale_sectors = ["04"] * 12
    for ticker, stale_sector, sector in zip([f"{value:06d}" for value in range(1, 13)], stale_sectors, sectors):
        rows.append(
            {
                "date": pd.Timestamp("2024-12-30"),
                "ticker": ticker,
                "final_sector_code": stale_sector,
                "final_sector_name": f"Sector {stale_sector}",
            }
        )
        rows.append(
            {
                "date": pd.Timestamp("2025-03-31"),
                "ticker": ticker,
                "final_sector_code": sector,
                "final_sector_name": f"Sector {sector}",
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
