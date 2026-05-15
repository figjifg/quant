from __future__ import annotations

import pandas as pd

from src.data.kospi_proxy import build_kospi_proxy
from src.features.regime import regime_gate_on


def test_proxy_level_cumulates_cap_weighted_returns() -> None:
    source = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-02", periods=3, freq="B"),
            "cap_weighted_return": [0.10, -0.10, 0.20],
        }
    )

    proxy = build_kospi_proxy(source, window=2)

    assert proxy["kospi_proxy_level"].tolist() == [1.1, 0.9900000000000001, 1.1880000000000002]


def test_sma_uses_levels_through_same_signal_date_only() -> None:
    source = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-02", periods=4, freq="B"),
            "cap_weighted_return": [0.0, 1.0, 0.0, 9.0],
        }
    )

    proxy = build_kospi_proxy(source, window=3)

    assert pd.isna(proxy.iloc[1]["kospi_proxy_sma_200"])
    assert proxy.iloc[2]["kospi_proxy_sma_200"] == (1.0 + 2.0 + 2.0) / 3.0
    assert proxy.iloc[2]["kospi_proxy_sma_200"] != (2.0 + 2.0 + 20.0) / 3.0


def test_warmup_period_gate_is_off() -> None:
    source = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-02", periods=3, freq="B"),
            "cap_weighted_return": [0.0, 0.5, 0.5],
        }
    )

    proxy = build_kospi_proxy(source, window=4)
    gate = regime_gate_on(proxy)

    assert gate.tolist() == [False, False, False]
