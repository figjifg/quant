from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.run_experiment import _d001_blocks_from_config
from src.strategies.h005_defensive_basket import (
    apply_defensive_basket_off_sleeve,
    defensive_basket_drawdown,
    load_defensive_basket_quarterly_returns,
)


def test_h005_config_freezes_d013_carrier_and_declares_option_a_basket() -> None:
    h005 = yaml.safe_load(Path("configs/backtests/h005.yaml").read_text(encoding="utf-8"))
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))

    assert h005["experiment_id"] == "H005"
    assert h005["carrier"] == "d013"
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
        assert h005[key] == d013[key]
    assert _d001_blocks_from_config(h005["regime"]["blocks"]) == _d001_blocks_from_config(d013["regime"]["blocks"])
    assert h005["off_sleeve"]["type"] == "defensive_basket"
    assert h005["off_sleeve"]["option"] == "A"
    assert h005["off_sleeve"]["weights"] == {
        "kr_short_rate_carry": 0.50,
        "usdkrw_cash": 0.25,
        "us_10y_treasury_krw": 0.25,
    }
    assert h005["verdict"] == {
        "d013_baseline_cumulative_threshold": 2.54,
        "sharpe_min": 0.65,
        "basket_sleeve_max_drawdown_min": -0.08,
    }


def test_defensive_basket_return_uses_pre_registered_weights(tmp_path: Path) -> None:
    kr_rate, usdkrw, dgs10 = _write_component_csvs(tmp_path)

    returns = load_defensive_basket_quarterly_returns(
        kr_short_rate_csv=kr_rate,
        usdkrw_csv=usdkrw,
        dgs10_csv=dgs10,
        signal_dates=pd.Series(pd.to_datetime(["2024-03-29", "2024-06-28"])),
        weights={
            "kr_short_rate_carry": 0.50,
            "usdkrw_cash": 0.25,
            "us_10y_treasury_krw": 0.25,
        },
    )

    kr_carry = (1.0 + 0.12 / 12.0) ** 3 - 1.0
    usd_return = 0.10
    treasury_return = 0.07 + 0.01 + 0.10
    assert returns["kr_carry_contribution"].iloc[0] == pytest.approx(0.50 * kr_carry)
    assert returns["usdkrw_contribution"].iloc[0] == pytest.approx(0.25 * usd_return)
    assert returns["treasury_contribution"].iloc[0] == pytest.approx(0.25 * treasury_return)
    assert returns["basket_quarter_return"].iloc[0] == pytest.approx(
        0.50 * kr_carry + 0.25 * usd_return + 0.25 * treasury_return
    )


def test_basket_sleeve_applies_only_to_off_execution_window(tmp_path: Path) -> None:
    kr_rate, usdkrw, dgs10 = _write_component_csvs(tmp_path)
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

    sleeve, decomposition = apply_defensive_basket_off_sleeve(
        BacktestResult(trades=pd.DataFrame(), equity_curve=equity),
        calendar=calendar,
        quarterly_regime=regime,
        kr_short_rate_csv=kr_rate,
        usdkrw_csv=usdkrw,
        dgs10_csv=dgs10,
        weights={
            "kr_short_rate_carry": 0.50,
            "usdkrw_cash": 0.25,
            "us_10y_treasury_krw": 0.25,
        },
    )

    expected = 1.0 + decomposition["basket_quarter_return"].iloc[0]
    assert sleeve.equity_curve["net_value"].iloc[0] == pytest.approx(1.0)
    assert sleeve.equity_curve["net_value"].iloc[3] == pytest.approx(expected)
    assert sleeve.equity_curve["net_value"].iloc[4] == pytest.approx(expected)


def test_defensive_basket_drawdown_uses_basket_quarter_sequence() -> None:
    decomposition = pd.DataFrame({"basket_quarter_return": [0.05, -0.04, 0.01]})

    assert defensive_basket_drawdown(decomposition) == pytest.approx(-0.04)


def _write_component_csvs(tmp_path: Path) -> tuple[Path, Path, Path]:
    kr_rate = tmp_path / "kr_rate.csv"
    kr_rate.write_text(
        "observation_date,IR3TIB01KRM156N\n"
        "2024-03-29,12.0\n"
        "2024-06-28,0.0\n",
        encoding="utf-8",
    )
    usdkrw = tmp_path / "usdkrw.csv"
    usdkrw.write_text(
        "observation_date,DEXKOUS\n"
        "2024-03-29,1000.0\n"
        "2024-06-28,1100.0\n",
        encoding="utf-8",
    )
    dgs10 = tmp_path / "dgs10.csv"
    dgs10.write_text(
        "observation_date,DGS10\n"
        "2024-03-29,4.0\n"
        "2024-06-28,3.0\n",
        encoding="utf-8",
    )
    return kr_rate, usdkrw, dgs10
