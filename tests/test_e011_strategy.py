from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e011_top4_champion import build_e011_top4_champion_candidates


def test_e011_top4_uses_e008_registered_distribution() -> None:
    candidates = build_e011_top4_champion_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        combined_scores=_combined_scores(),
        sector_mapping=_mapping(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    )

    assert len(candidates) == 5
    assert candidates.groupby("sector_code").size().to_dict() == {"01": 2, "02": 1, "03": 1, "04": 1}
    assert candidates["target_weight"].sum() == pytest.approx(1.0)
    assert candidates["execution_date"].eq(pd.Timestamp("2025-04-01")).all()


def _panel() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 16)]
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-03-31")] * len(tickers),
            "종목코드": tickers,
            "KRX종가": [100.0] * len(tickers),
            "상장주식수": list(range(1015, 1000, -1)),
        }
    )


def _universe() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 16)]
    return pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-03-31")] * len(tickers),
            "execution_date": [pd.Timestamp("2025-04-01")] * len(tickers),
            "종목코드": tickers,
        }
    )


def _quarterly_regime() -> pd.DataFrame:
    return pd.DataFrame({"signal_date": [pd.Timestamp("2025-03-31")], "regime_on": [True]})


def _mapping() -> pd.DataFrame:
    rows = []
    for sector_index, sector_code in enumerate(("01", "02", "03", "04", "05"), start=0):
        for offset in range(3):
            rows.append(
                {
                    "ticker": f"{sector_index * 3 + offset + 1:06d}",
                    "final_sector_code": sector_code,
                    "final_sector_name": f"Sector {sector_code}",
                }
            )
    return pd.DataFrame(rows)


def _combined_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-03-31")] * 5,
            "sector_code": ["01", "02", "03", "04", "05"],
            "sector_name": ["Sector 01", "Sector 02", "Sector 03", "Sector 04", "Sector 05"],
            "flow_score": [5.0, 4.0, 3.0, 2.0, 1.0],
            "rs_score": [5.0, 4.0, 3.0, 2.0, 1.0],
            "breadth_score": [5.0, 4.0, 3.0, 2.0, 1.0],
            "combined_score": [5.0, 4.0, 3.0, 2.0, 1.0],
        }
    )
