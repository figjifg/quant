from __future__ import annotations

import pandas as pd

from src.strategies.e013_subperiod_spike import e013_segments_for_trading_window


def test_e013_restricts_trading_window_without_changing_warmup_segments() -> None:
    segments = ((pd.Timestamp("2010-01-04"), pd.Timestamp("2026-05-04")),)

    restricted = e013_segments_for_trading_window(
        segments=segments,
        trading_start=pd.Timestamp("2021-01-01"),
        trading_end=pd.Timestamp("2026-05-04"),
    )

    assert restricted == ((pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-04")),)
