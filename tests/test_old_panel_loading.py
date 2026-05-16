from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.equity_panel import INTEGRATION_FLAG_COLUMNS, load_equity_panel


OLD_PANEL = Path(
    "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv"
)
MID_PANEL = Path("research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv")


def test_old_2010_2016_panel_loads_with_native_krx_close() -> None:
    panel = load_equity_panel([OLD_PANEL])

    assert len(panel) == 1_093_386
    assert panel["날짜"].min() == pd.Timestamp("2010-01-04")
    assert panel["날짜"].max() == pd.Timestamp("2016-12-29")
    assert set(panel["krx_close_source"]) == {"native"}
    for column in INTEGRATION_FLAG_COLUMNS:
        assert column in panel.columns
        assert panel[column].dtype == bool
        assert not panel[column].any()


def test_2017_2024_panel_defaults_integration_flags_and_krx_close() -> None:
    panel = load_equity_panel([MID_PANEL])

    assert len(panel) == 1_087_741
    assert panel["날짜"].min() == pd.Timestamp("2017-01-02")
    assert panel["날짜"].max() == pd.Timestamp("2024-12-30")
    assert set(panel["krx_close_source"]) == {"from_종가_fallback"}
    assert panel["KRX종가"].equals(panel["종가"])
    for column in INTEGRATION_FLAG_COLUMNS:
        assert column in panel.columns
        assert panel[column].dtype == bool
        assert not panel[column].any()
