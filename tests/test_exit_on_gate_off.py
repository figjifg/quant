from __future__ import annotations

import pandas as pd

from src.roles.exits import exit_on_gate_off


def test_exit_on_gate_off_returns_engine_kwargs() -> None:
    kwargs = exit_on_gate_off({pd.Timestamp("2025-01-03 15:30")})

    assert kwargs == {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": None,
        "gate_exit_signal_dates": {pd.Timestamp("2025-01-03")},
    }
