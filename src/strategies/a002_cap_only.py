from __future__ import annotations

import pandas as pd

from src.roles.exits import exit_time_cap
from src.strategies.a001_fixed_holding import build_e001_flow_filter_candidates


def a002_cap_only_setup(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    *,
    holding_cap_days: int = 20,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Compose A002 cap-only replay candidates and fixed-cap exit kwargs."""
    return build_e001_flow_filter_candidates(flow_features, universe), exit_time_cap(holding_cap_days)
