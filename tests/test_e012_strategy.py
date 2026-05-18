from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e012_robustness_ablation import build_e012_score_ablation_candidates, build_e012_topk_grid_candidates


def test_e012_score_ablation_changes_ranking_without_new_feature_inputs() -> None:
    scores = _combined_scores()
    scores["rs_score"] = [1.0, 2.0, 3.0, 5.0, 4.0]
    scores["breadth_score"] = [5.0, 4.0, 3.0, 1.0, 2.0]
    result = build_e012_score_ablation_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        combined_scores=scores,
        sector_mapping=_mapping(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    )

    assert tuple(result) == ("rs_only", "rs_breadth", "flow_rs_breadth")
    assert result["rs_only"].groupby("sector_code").size().to_dict() == {"02": 1, "03": 1, "04": 2, "05": 1}
    assert result["flow_rs_breadth"].groupby("sector_code").size().to_dict() == {
        "01": 2,
        "02": 1,
        "03": 1,
        "04": 1,
    }


def test_e012_topk_grid_is_limited_to_pre_registered_k_3_4_5() -> None:
    result = build_e012_topk_grid_candidates(
        panel=_panel(),
        universe=_universe(),
        quarterly_regime=_quarterly_regime(),
        combined_scores=_combined_scores(),
        sector_mapping=_mapping(),
        calendar=KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    )

    assert tuple(result) == ("top_3", "top_4", "top_5")
    assert result["top_4"].groupby("sector_code").size().to_dict() == {"01": 2, "02": 1, "03": 1, "04": 1}


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
