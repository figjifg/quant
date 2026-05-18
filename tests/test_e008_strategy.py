from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e008_topk_grid import build_e008_topk_grid_candidates


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
            ticker = f"{sector_index * 3 + offset + 1:06d}"
            rows.append(
                {
                    "ticker": ticker,
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


def test_e008_topk_grid_applies_exact_sector_distributions() -> None:
    result = build_e008_topk_grid_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        combined_scores=_combined_scores(),
        sector_mapping=_mapping(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
        top_sector_counts_grid=((3, 2), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1)),
    )

    expected = {
        "top_2": {"01": 3, "02": 2},
        "top_3": {"01": 2, "02": 2, "03": 1},
        "top_4": {"01": 2, "02": 1, "03": 1, "04": 1},
        "top_5": {"01": 1, "02": 1, "03": 1, "04": 1, "05": 1},
    }
    for label, sector_counts in expected.items():
        candidates = result[label]
        assert len(candidates) == 5
        assert candidates.groupby("sector_code").size().to_dict() == sector_counts
        assert candidates["target_weight"].sum() == pytest.approx(1.0)
        assert candidates["execution_date"].eq(pd.Timestamp("2025-04-01")).all()


def test_e008_rejects_duplicate_k_grid_entries() -> None:
    with pytest.raises(ValueError, match="unique K"):
        build_e008_topk_grid_candidates(
            panel=_panel(),
            universe=_universe(),
            quarterly_regime=_quarterly_regime(),
            combined_scores=_combined_scores(),
            sector_mapping=_mapping(),
            calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
            top_sector_counts_grid=((3, 2), (4, 1)),
        )
