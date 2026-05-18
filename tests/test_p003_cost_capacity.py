from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.strategies.p003_d013_cost_capacity import (
    add_capacity_impact,
    costs_with_slippage,
    multiply_costs,
    run_capacity_backtest,
)


def test_p003_cost_multiplier_scales_all_cost_components() -> None:
    costs = Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)

    stressed = multiply_costs(costs, 5.0)

    assert stressed.commission_bps == 7.5
    assert stressed.tax_bps_sell == 100.0
    assert stressed.slippage_bps == 25.0


def test_p003_slippage_stress_changes_only_slippage() -> None:
    costs = Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)

    stressed = costs_with_slippage(costs, 25.0)

    assert stressed.commission_bps == costs.commission_bps
    assert stressed.tax_bps_sell == costs.tax_bps_sell
    assert stressed.slippage_bps == 25.0


def test_capacity_impact_uses_signal_date_rolling_adv_without_future_rows() -> None:
    panel = _capacity_panel()
    candidates = pd.DataFrame(
        [
            {
                "signal_date": pd.Timestamp("2025-01-06"),
                "execution_date": pd.Timestamp("2025-01-07"),
                "종목코드": "000001",
                "rank": 1,
                "market_cap": 1_000.0,
            }
        ]
    )
    mutated = panel.copy()
    mutated.loc[mutated["날짜"].gt(pd.Timestamp("2025-01-06")), "거래대금추정"] = 1.0

    before = add_capacity_impact(panel=panel, candidates=candidates, aum_krw=500.0, max_positions=5)
    after = add_capacity_impact(panel=mutated, candidates=candidates, aum_krw=500.0, max_positions=5)

    assert before.loc[0, "avg_traded_value_60d"] == pytest.approx(after.loc[0, "avg_traded_value_60d"], abs=0.0)
    assert before.loc[0, "participation"] == pytest.approx(100.0 / 110.0)
    assert before.loc[0, "impact_bps"] == pytest.approx(10.0 * math.sqrt(100.0 / 110.0))


def test_capacity_backtest_adds_impact_to_trade_costs() -> None:
    panel = _capacity_panel()
    calendar = derive_trading_calendar(panel)
    candidates = pd.DataFrame(
        [
            {
                "signal_date": calendar.dates[2],
                "execution_date": calendar.dates[3],
                "종목코드": "000001",
                "rank": 1,
                "market_cap": 1_000.0,
                "participation": 0.25,
                "impact_bps": 5.0,
            }
        ]
    )

    result = run_capacity_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        base_costs=Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0),
        segments=((calendar.dates[0], calendar.dates[-1]),),
        rebalance_dates={calendar.dates[3]},
    ).result

    trade = result.trades.iloc[0]
    expected_buy_cost = trade["notional_at_entry"] * (1.5 + 5.0 + 5.0) / 1e4
    expected_sell_cost = trade["shares"] * trade["exit_price"] * (1.5 + 5.0 + 5.0 + 20.0) / 1e4
    assert trade["buy_cost"] == pytest.approx(expected_buy_cost)
    assert trade["sell_cost"] == pytest.approx(expected_sell_cost)
    assert trade["impact_bps"] == pytest.approx(5.0)
    assert trade["participation"] == pytest.approx(0.25)


def test_p003_configs_preserve_d013_carrier_definition() -> None:
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))
    for path in (
        "configs/backtests/p003_cost.yaml",
        "configs/backtests/p003_slippage.yaml",
        "configs/backtests/p003_capacity.yaml",
    ):
        config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        for key in ("panels", "panel_date_filters", "market_breadth_csv", "macro_data_dir", "period", "universe"):
            assert config[key] == d013[key]
        for key in ("strategy", "regime", "selection", "rebalance"):
            assert config[key] == d013[key]


def _capacity_panel() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=8, freq="B")
    traded_values = [100.0, 110.0, 120.0, 130.0, 10_000.0, 10_000.0, 10_000.0, 10_000.0]
    rows = []
    for date, traded_value in zip(dates, traded_values, strict=True):
        rows.append(
            {
                "날짜": date,
                "종목코드": "000001",
                "시가": 100.0,
                "KRX종가": 101.0,
                "거래대금추정": traded_value,
            }
        )
    return pd.DataFrame(rows)
