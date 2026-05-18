from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import build_e007_flow_rs_breadth_top_sector_candidates
from src.strategies.e009_cost_stress import (
    COST_SCENARIOS,
    SCENARIO_ORDER,
    build_e009_cost_stress_candidates,
    validate_e009_cost_scenarios,
)


def _panel() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 10)]
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-03-31")] * len(tickers),
            "종목코드": tickers,
            "KRX종가": [100.0] * len(tickers),
            "상장주식수": list(range(1009, 1000, -1)),
        }
    )


def _universe() -> pd.DataFrame:
    tickers = [f"{value:06d}" for value in range(1, 10)]
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
    for sector_index, sector_code in enumerate(("01", "02", "03"), start=0):
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
            "signal_date": [pd.Timestamp("2025-03-31")] * 3,
            "sector_code": ["01", "02", "03"],
            "sector_name": ["Sector 01", "Sector 02", "Sector 03"],
            "flow_score": [3.0, 2.0, 1.0],
            "rs_score": [3.0, 2.0, 1.0],
            "breadth_score": [3.0, 2.0, 1.0],
            "combined_score": [3.0, 2.0, 1.0],
        }
    )


def test_e009_candidates_are_e007_top3_2_2_1_carrier() -> None:
    kwargs = {
        "panel": _panel(),
        "universe": _universe(),
        "quarterly_regime": _quarterly_regime(),
        "combined_scores": _combined_scores(),
        "sector_mapping": _mapping(),
        "calendar": KRXTradingCalendar([pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-01")]),
    }

    expected = build_e007_flow_rs_breadth_top_sector_candidates(**kwargs, top_sector_counts=(2, 2, 1))
    result = build_e009_cost_stress_candidates(**kwargs)

    pd.testing.assert_frame_equal(result, expected)
    assert result.groupby("sector_code").size().to_dict() == {"01": 2, "02": 2, "03": 1}
    assert result["target_weight"].sum() == pytest.approx(1.0)


def test_e009_cost_scenarios_match_d018_ticket_values() -> None:
    config = yaml.safe_load(Path("configs/backtests/e009.yaml").read_text(encoding="utf-8"))

    validate_e009_cost_scenarios(config["cost_scenarios"])
    assert tuple(config["cost_scenarios"].keys()) == SCENARIO_ORDER
    assert config["cost_scenarios"] == COST_SCENARIOS


def test_e009_rejects_unregistered_cost_scenario() -> None:
    scenarios = dict(COST_SCENARIOS)
    scenarios["one_day_delay"] = {"commission_bps": 1.5, "tax_bps_sell": 20.0, "slippage_bps": 5.0}

    with pytest.raises(ValueError, match="cost_scenarios"):
        validate_e009_cost_scenarios(scenarios)
