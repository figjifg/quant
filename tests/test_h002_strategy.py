from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.run_experiment import _d001_blocks_from_config
from src.strategies.h002_usdkrw_sleeve import (
    apply_usdkrw_off_sleeve,
    load_usdkrw_quarterly_returns,
    usdkrw_sleeve_drawdown,
)


def test_h002_config_freezes_d013_carrier_and_declares_usdkrw_sleeve() -> None:
    h002 = yaml.safe_load(Path("configs/backtests/h002.yaml").read_text(encoding="utf-8"))
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))

    assert h002["experiment_id"] == "H002"
    assert h002["carrier"] == "d013"
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
        assert h002[key] == d013[key]
    assert _d001_blocks_from_config(h002["regime"]["blocks"]) == _d001_blocks_from_config(d013["regime"]["blocks"])
    assert h002["off_sleeve"] == {
        "type": "usdkrw_cash",
        "source": "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv",
        "rate_column": "DEXKOUS",
        "carry_assumption": 0,
        "formula": "end_usdkrw / start_usdkrw - 1",
    }


def test_usdkrw_quarter_return_uses_signal_date_and_next_signal_date(tmp_path: Path) -> None:
    path = tmp_path / "usdkrw.csv"
    path.write_text(
        "observation_date,DEXKOUS\n"
        "2024-03-28,1300.0\n"
        "2024-03-29,1310.0\n"
        "2024-06-27,1320.0\n"
        "2024-06-28,1336.2\n"
        "2024-07-01,1400.0\n",
        encoding="utf-8",
    )

    fx = load_usdkrw_quarterly_returns(path, pd.Series(pd.to_datetime(["2024-03-29", "2024-06-28"])))

    assert fx["start_observation_date"].iloc[0] == pd.Timestamp("2024-03-29")
    assert fx["end_observation_date"].iloc[0] == pd.Timestamp("2024-06-28")
    assert fx["usdkrw_quarter_return"].iloc[0] == pytest.approx(1336.2 / 1310.0 - 1.0)


def test_off_sleeve_applies_fx_only_to_off_execution_window(tmp_path: Path) -> None:
    path = tmp_path / "usdkrw.csv"
    path.write_text(
        "observation_date,DEXKOUS\n"
        "2024-03-29,1000.0\n"
        "2024-06-28,1100.0\n",
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

    sleeve, contribution = apply_usdkrw_off_sleeve(
        BacktestResult(trades=pd.DataFrame(), equity_curve=equity),
        calendar=calendar,
        quarterly_regime=regime,
        usdkrw_csv=path,
    )

    assert contribution["quarter_fx_return"].iloc[0] == pytest.approx(0.10)
    assert contribution["cumulative_off_fx"].iloc[-1] == pytest.approx(0.10)
    assert sleeve.equity_curve["net_value"].iloc[0] == pytest.approx(1.0)
    assert sleeve.equity_curve["net_value"].iloc[3] == pytest.approx(1.10)
    assert sleeve.equity_curve["net_value"].iloc[4] == pytest.approx(1.10)


def test_usdkrw_sleeve_drawdown_uses_off_quarter_fx_sequence() -> None:
    off_fx = pd.DataFrame({"quarter_fx_return": [0.10, -0.06, 0.02]})

    assert usdkrw_sleeve_drawdown(off_fx) == pytest.approx(-0.06)
