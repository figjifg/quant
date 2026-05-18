from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import BacktestResult
from src.run_experiment import _d001_blocks_from_config
from src.strategies.h001_kr_short_rate_sleeve import (
    apply_kr_short_rate_off_sleeve,
    load_kr_short_rate_quarterly_carry,
)


def test_h001_config_freezes_d013_carrier_and_declares_kr_short_rate_sleeve() -> None:
    h001 = yaml.safe_load(Path("configs/backtests/h001.yaml").read_text(encoding="utf-8"))
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))

    assert h001["experiment_id"] == "H001"
    assert h001["carrier"] == "d013"
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
        assert h001[key] == d013[key]
    assert _d001_blocks_from_config(h001["regime"]["blocks"]) == _d001_blocks_from_config(d013["regime"]["blocks"])
    assert h001["off_sleeve"] == {
        "type": "kr_short_rate_carry",
        "source": "research_input_data/inputs/macro_features/fred_kr_short_rate.csv",
        "rate_column": "IR3TIB01KRM156N",
        "compounding": "monthly_3x",
        "formula": "(1 + annual_rate / 12)^3 - 1",
    }


def test_kr_short_rate_carry_uses_latest_observation_on_or_before_signal_date(tmp_path: Path) -> None:
    path = tmp_path / "rates.csv"
    path.write_text(
        "observation_date,IR3TIB01KRM156N\n"
        "2024-01-01,12.0\n"
        "2024-04-01,24.0\n",
        encoding="utf-8",
    )

    carry = load_kr_short_rate_quarterly_carry(path, pd.Series(pd.to_datetime(["2024-03-29"])))

    assert carry["observation_date"].iloc[0] == pd.Timestamp("2024-01-01")
    assert carry["annual_rate"].iloc[0] == pytest.approx(0.12)
    assert carry["kr_short_quarter_carry"].iloc[0] == pytest.approx((1.0 + 0.12 / 12.0) ** 3 - 1.0)


def test_off_sleeve_applies_carry_only_to_off_execution_window(tmp_path: Path) -> None:
    path = tmp_path / "rates.csv"
    path.write_text(
        "observation_date,IR3TIB01KRM156N\n"
        "2024-03-01,12.0\n"
        "2024-06-01,0.0\n",
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

    sleeve, contribution = apply_kr_short_rate_off_sleeve(
        BacktestResult(trades=pd.DataFrame(), equity_curve=equity),
        calendar=calendar,
        quarterly_regime=regime,
        kr_short_rate_csv=path,
    )

    expected = (1.0 + 0.12 / 12.0) ** 3
    assert contribution["cumulative_off_carry"].iloc[-1] == pytest.approx(expected - 1.0)
    assert sleeve.equity_curve["net_value"].iloc[0] == pytest.approx(1.0)
    assert sleeve.equity_curve["net_value"].iloc[3] == pytest.approx(expected)
    assert sleeve.equity_curve["net_value"].iloc[4] == pytest.approx(expected)
