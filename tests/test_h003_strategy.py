from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.run_experiment import _d001_blocks_from_config
from src.strategies.h003_us_treasury_sleeve import (
    apply_us_treasury_off_sleeve,
    load_us_treasury_quarterly_returns,
    us_treasury_sleeve_drawdown,
)


def test_h003_config_freezes_d013_carrier_and_declares_us_treasury_sleeve() -> None:
    h003 = yaml.safe_load(Path("configs/backtests/h003.yaml").read_text(encoding="utf-8"))
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))

    assert h003["experiment_id"] == "H003"
    assert h003["carrier"] == "d013"
    for key in (
        "panels",
        "panel_date_filters",
        "market_breadth_csv",
        "macro_data_dir",
        "period",
        "universe",
        "strategy",
        "regime",
        "selection",
        "rebalance",
        "costs",
    ):
        assert h003[key] == d013[key]
    assert _d001_blocks_from_config(h003["regime"]["blocks"]) == _d001_blocks_from_config(d013["regime"]["blocks"])
    assert h003["off_sleeve"] == {
        "type": "us_10y_treasury_krw",
        "yield_source": "research_input_data/inputs/macro_features/fred_dgs10.csv",
        "yield_column": "DGS10",
        "fx_source": "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv",
        "fx_column": "DEXKOUS",
        "effective_duration": 7.0,
        "formula": "-delta_yield_decimal * 7 + start_yield_decimal / 4 + usdkrw_quarter_return",
    }


def test_us_treasury_quarter_return_uses_signal_date_and_next_signal_date(tmp_path: Path) -> None:
    dgs10 = tmp_path / "dgs10.csv"
    dgs10.write_text(
        "observation_date,DGS10\n"
        "2024-03-28,4.0\n"
        "2024-03-29,5.0\n"
        "2024-06-27,5.5\n"
        "2024-06-28,6.0\n"
        "2024-07-01,1.0\n",
        encoding="utf-8",
    )
    usdkrw = tmp_path / "usdkrw.csv"
    usdkrw.write_text(
        "observation_date,DEXKOUS\n"
        "2024-03-29,1300.0\n"
        "2024-06-28,1326.0\n"
        "2024-07-01,1400.0\n",
        encoding="utf-8",
    )

    returns = load_us_treasury_quarterly_returns(
        dgs10,
        usdkrw,
        pd.Series(pd.to_datetime(["2024-03-29", "2024-06-28"])),
    )

    assert returns["start_yield_observation_date"].iloc[0] == pd.Timestamp("2024-03-29")
    assert returns["end_yield_observation_date"].iloc[0] == pd.Timestamp("2024-06-28")
    assert returns["yield_change"].iloc[0] == pytest.approx(0.01)
    assert returns["duration_return"].iloc[0] == pytest.approx(-0.07)
    assert returns["carry_return"].iloc[0] == pytest.approx(0.0125)
    assert returns["fx_return"].iloc[0] == pytest.approx(0.02)
    assert returns["krw_treasury_return"].iloc[0] == pytest.approx(-0.0375)


def test_off_sleeve_applies_treasury_return_only_to_off_execution_window(tmp_path: Path) -> None:
    dgs10 = tmp_path / "dgs10.csv"
    dgs10.write_text(
        "observation_date,DGS10\n"
        "2024-03-29,4.0\n"
        "2024-06-28,3.0\n",
        encoding="utf-8",
    )
    usdkrw = tmp_path / "usdkrw.csv"
    usdkrw.write_text(
        "observation_date,DEXKOUS\n"
        "2024-03-29,1000.0\n"
        "2024-06-28,1010.0\n",
        encoding="utf-8",
    )
    dates = pd.to_datetime(["2024-03-29", "2024-04-01", "2024-04-02", "2024-06-28", "2024-07-01"])
    calendar = KRXTradingCalendar(tuple(dates))
    equity = pd.DataFrame(
        {
            "date": dates,
            "cash": [1.0] * len(dates),
            "mtm_value": [0.0] * len(dates),
            "gross_value": [1.0] * len(dates),
            "net_value": [1.0] * len(dates),
            "n_positions": [0] * len(dates),
        }
    )
    regime = pd.DataFrame(
        {
            "signal_date": pd.to_datetime(["2024-03-29", "2024-06-28"]),
            "regime_on": [False, True],
        }
    )

    sleeve, decomposition = apply_us_treasury_off_sleeve(
        BacktestResult(trades=pd.DataFrame(), equity_curve=equity),
        calendar=calendar,
        quarterly_regime=regime,
        dgs10_csv=dgs10,
        usdkrw_csv=usdkrw,
    )

    expected = 1.0 + 0.07 + 0.01 + 0.01
    assert decomposition["quarter_treasury_krw_return"].iloc[0] == pytest.approx(expected - 1.0)
    assert decomposition["cumulative_off_treasury"].iloc[-1] == pytest.approx(expected - 1.0)
    assert sleeve.equity_curve["net_value"].iloc[0] == pytest.approx(1.0)
    assert sleeve.equity_curve["net_value"].iloc[3] == pytest.approx(expected)
    assert sleeve.equity_curve["net_value"].iloc[4] == pytest.approx(expected)


def test_us_treasury_sleeve_drawdown_uses_off_quarter_sequence() -> None:
    decomposition = pd.DataFrame({"quarter_treasury_krw_return": [0.10, -0.12, 0.02]})

    assert us_treasury_sleeve_drawdown(decomposition) == pytest.approx(-0.12)
