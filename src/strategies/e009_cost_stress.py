from __future__ import annotations

from typing import Any

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.strategies.e007_flow_rs_breadth import build_e007_flow_rs_breadth_top_sector_candidates


COST_SCENARIOS: dict[str, dict[str, float]] = {
    "base": {"commission_bps": 1.5, "tax_bps_sell": 20.0, "slippage_bps": 5.0},
    "2x": {"commission_bps": 3.0, "tax_bps_sell": 40.0, "slippage_bps": 10.0},
    "3x": {"commission_bps": 4.5, "tax_bps_sell": 60.0, "slippage_bps": 15.0},
    "extra_slippage": {"commission_bps": 1.5, "tax_bps_sell": 20.0, "slippage_bps": 15.0},
}

SCENARIO_ORDER: tuple[str, ...] = ("base", "2x", "3x", "extra_slippage")


def build_e009_cost_stress_candidates(
    *,
    panel: pd.DataFrame,
    universe: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    combined_scores: pd.DataFrame,
    sector_mapping: pd.DataFrame,
    calendar: KRXTradingCalendar,
) -> pd.DataFrame:
    return build_e007_flow_rs_breadth_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_regime,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=(2, 2, 1),
    )


def validate_e009_cost_scenarios(cost_scenarios: dict[str, Any]) -> None:
    if tuple(cost_scenarios.keys()) != SCENARIO_ORDER:
        raise ValueError(f"E009 cost_scenarios must be exactly {list(SCENARIO_ORDER)} in order.")
    for scenario, expected in COST_SCENARIOS.items():
        actual = cost_scenarios[scenario]
        if tuple(actual.keys()) != ("commission_bps", "tax_bps_sell", "slippage_bps"):
            raise ValueError(f"E009 {scenario} cost keys must be commission_bps, tax_bps_sell, slippage_bps.")
        for key, expected_value in expected.items():
            if float(actual[key]) != expected_value:
                raise ValueError(f"E009 {scenario}.{key} must be {expected_value}.")
