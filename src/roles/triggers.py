from __future__ import annotations

import pandas as pd


def trigger_immediate(filtered_features: pd.DataFrame) -> pd.DataFrame:
    """Return filtered rows unchanged; filter pass is the entry trigger."""
    return filtered_features
