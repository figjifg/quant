from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.run_experiment import _d001_blocks_from_config
from src.strategies.h004_gold_sleeve import (
    apply_gold_off_sleeve,
    gold_sleeve_drawdown,
    load_gold_quarterly_returns,
)


def test_h004_config_freezes_d013_carrier_and_declares_gold_sleeve() -> None:
    h004 = yaml.safe_load(Path("configs/backtests/h004.yaml").read_text(encoding="utf-8"))
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))

    assert h004["experiment_id"] == "H004"
    assert h004["carrier"] == "d013"
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
        assert h004[key] == d013[key]
    assert _d001_blocks_from_config(h004["regime"]["blocks"]) == _d001_blocks_from_config(d013["regime"]["blocks"])
    assert h004["off_sleeve"] == {
        "type": "kodex_gold_132030",
        "source": "research_input_data/inputs/macro_features/krx_kodex_gold_132030.csv",
        "ticker": "132030",
        "currency": "KRW",
        "price_column": "close",
        "inception_date": "2010-10-01",
        "pre_inception_fallback": "cash_return_0",
        "formula": "end_close / start_close - 1",
    }


def test_gold_quarter_return_uses_signal_date_and_next_quarter_close(tmp_path: Path) -> None:
    path = tmp_path / "gold.csv"
    path.write_text(
        "date,nav,open,high,low,close,volume,traded_value,base_index\n"
        "2024-03-29,100,100,100,100,1000,1,1,1\n"
        "2024-06-28,110,110,110,110,1100,1,1,1\n"
        "2024-07-01,150,150,150,150,1500,1,1,1\n",
        encoding="utf-8",
    )

    returns = load_gold_quarterly_returns(path, pd.Series(pd.to_datetime(["2024-03-29", "2024-06-28"])))

    assert returns["start_observation_date"].iloc[0] == pd.Timestamp("2024-03-29")
    assert returns["end_observation_date"].iloc[0] == pd.Timestamp("2024-06-28")
    assert returns["gold_quarter_return"].iloc[0] == pytest.approx(0.10)


def test_gold_pre_inception_signal_dates_use_cash_fallback(tmp_path: Path) -> None:
    path = tmp_path / "gold.csv"
    path.write_text(
        "date,nav,open,high,low,close,volume,traded_value,base_index\n"
        "2010-10-01,100,100,100,100,1000,1,1,1\n"
        "2010-12-30,110,110,110,110,1100,1,1,1\n",
        encoding="utf-8",
    )

    returns = load_gold_quarterly_returns(
        path,
        pd.Series(pd.to_datetime(["2010-09-30", "2010-12-30"])),
        final_end_date=pd.Timestamp("2010-12-30"),
    )

    assert returns["inception_cash_fallback"].iloc[0]
    assert returns["gold_quarter_return"].iloc[0] == pytest.approx(0.0)
    assert returns["return_source"].iloc[0] == "cash_fallback_pre_inception"


def test_gold_sleeve_applies_only_to_off_execution_window(tmp_path: Path) -> None:
    path = tmp_path / "gold.csv"
    path.write_text(
        "date,nav,open,high,low,close,volume,traded_value,base_index\n"
        "2024-03-29,100,100,100,100,1000,1,1,1\n"
        "2024-06-28,110,110,110,110,1100,1,1,1\n",
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

    sleeve, decomposition = apply_gold_off_sleeve(
        BacktestResult(trades=pd.DataFrame(), equity_curve=equity),
        calendar=calendar,
        quarterly_regime=regime,
        gold_csv=path,
    )

    assert decomposition["gold_quarter_return"].iloc[0] == pytest.approx(0.10)
    assert decomposition["cumulative_off_gold"].iloc[-1] == pytest.approx(0.10)
    assert sleeve.equity_curve["net_value"].iloc[0] == pytest.approx(1.0)
    assert sleeve.equity_curve["net_value"].iloc[3] == pytest.approx(1.10)
    assert sleeve.equity_curve["net_value"].iloc[4] == pytest.approx(1.10)


def test_gold_sleeve_drawdown_uses_off_quarter_sequence() -> None:
    decomposition = pd.DataFrame({"gold_quarter_return": [0.10, -0.12, 0.02]})

    assert gold_sleeve_drawdown(decomposition) == pytest.approx(-0.12)
