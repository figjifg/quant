from __future__ import annotations

import pandas as pd

from src.features.regime import regime_gate_on


def test_regime_gate_crossings_up_and_down() -> None:
    dates = pd.date_range("2025-01-02", periods=5, freq="B")
    proxy = pd.DataFrame(
        {
            "kospi_proxy_level": [100.0, 101.0, 99.0, 103.0, 98.0],
            "kospi_proxy_sma_200": [pd.NA, 100.0, 100.0, 100.0, 100.0],
        },
        index=pd.Index(dates, name="date"),
    )

    gate = regime_gate_on(proxy)

    assert gate.tolist() == [False, True, False, True, False]
