from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.run_experiment import _validate_p002_config_shape
from src.strategies.p002_d013_execution import run_p002_execution_backtest


def test_p002_configs_are_d013_carrier_with_only_scenario_changed() -> None:
    scenarios = {
        "p002_a.yaml": "A_next_day_close",
        "p002_b.yaml": "B_1day_delay",
        "p002_c.yaml": "C_2day_delay",
        "p002_d.yaml": "D_unfavorable_fill",
        "p002_e.yaml": "E_partial_fill",
        "p002_f.yaml": "F_cash_fallback",
    }
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))
    for filename, scenario in scenarios.items():
        config = yaml.safe_load(Path("configs/backtests", filename).read_text(encoding="utf-8"))
        _validate_p002_config_shape(config)
        assert config["carrier"] == "d013"
        assert config["scenario"] == scenario
        for key in ("panels", "panel_date_filters", "period", "universe", "strategy", "regime", "selection", "rebalance", "costs"):
            assert config[key] == d013[key]


def test_p002_delay_shifts_execution_dates_without_same_day_signal_use() -> None:
    result = run_p002_execution_backtest(
        panel=_panel(),
        calendar=_calendar(),
        candidates=_candidates(),
        quarterly_regime=_quarterly_regime(),
        costs=_zero_costs(),
        segments=((pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-08")),),
        scenario="B_1day_delay",
    )

    assert result.candidates["execution_date"].unique().tolist() == [pd.Timestamp("2025-01-06")]
    assert (result.candidates["execution_date"] > result.candidates["signal_date"]).all()
    assert result.result.trades.loc[0, "entry_date"] == pd.Timestamp("2025-01-06")


def test_p002_next_day_close_uses_close_for_entry_and_rebalance_exit() -> None:
    result = run_p002_execution_backtest(
        panel=_panel(),
        calendar=_calendar(),
        candidates=_two_rebalance_candidates(),
        quarterly_regime=_two_rebalance_regime(),
        costs=_zero_costs(),
        segments=((pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-08")),),
        scenario="A_next_day_close",
    )

    trade = result.result.trades.iloc[0]
    assert trade["entry_date"] == pd.Timestamp("2025-01-03")
    assert trade["entry_price"] == pytest.approx(102.0)
    assert trade["exit_date"] == pd.Timestamp("2025-01-06")
    assert trade["exit_price"] == pytest.approx(103.0)


def test_p002_unfavorable_fill_uses_high_for_buy_low_for_sell() -> None:
    result = run_p002_execution_backtest(
        panel=_panel(),
        calendar=_calendar(),
        candidates=_two_rebalance_candidates(),
        quarterly_regime=_two_rebalance_regime(),
        costs=_zero_costs(),
        segments=((pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-08")),),
        scenario="D_unfavorable_fill",
    )

    trade = result.result.trades.iloc[0]
    assert trade["entry_price"] == pytest.approx(110.0)
    assert trade["exit_price"] == pytest.approx(95.0)


def test_p002_partial_fill_deploys_80_percent_and_leaves_cash() -> None:
    result = run_p002_execution_backtest(
        panel=_panel(),
        calendar=_calendar(),
        candidates=_candidates(),
        quarterly_regime=_quarterly_regime(),
        costs=_zero_costs(),
        segments=((pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-08")),),
        scenario="E_partial_fill",
    )

    first_live_row = result.result.equity_curve.loc[result.result.equity_curve["date"].eq(pd.Timestamp("2025-01-03"))].iloc[0]
    assert first_live_row["cash"] == pytest.approx(0.2)
    assert result.result.trades.loc[0, "notional_at_entry"] == pytest.approx(0.8)


def test_p002_cash_fallback_skips_status_ticker() -> None:
    panel = _panel()
    panel["거래정지여부"] = False
    panel.loc[panel["날짜"].eq(pd.Timestamp("2025-01-03")), "거래정지여부"] = True

    result = run_p002_execution_backtest(
        panel=panel,
        calendar=_calendar(),
        candidates=_candidates(),
        quarterly_regime=_quarterly_regime(),
        costs=_zero_costs(),
        segments=((pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-08")),),
        scenario="F_cash_fallback",
    )

    assert result.result.trades.empty
    assert len(result.fallback_events) == 1
    assert result.fallback_events.loc[0, "reason"] == "status_or_missing_row"
    assert result.result.equity_curve.loc[result.result.equity_curve["date"].eq(pd.Timestamp("2025-01-03")), "cash"].iloc[0] == pytest.approx(1.0)


def _calendar() -> KRXTradingCalendar:
    return KRXTradingCalendar(pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07", "2025-01-08"]))


def _panel() -> pd.DataFrame:
    rows = []
    for date, open_price, high, low, close in (
        ("2025-01-02", 100.0, 105.0, 95.0, 101.0),
        ("2025-01-03", 101.0, 110.0, 96.0, 102.0),
        ("2025-01-06", 102.0, 111.0, 95.0, 103.0),
        ("2025-01-07", 103.0, 112.0, 97.0, 104.0),
        ("2025-01-08", 104.0, 113.0, 98.0, 105.0),
    ):
        rows.append(
            {
                "날짜": pd.Timestamp(date),
                "종목코드": "000001",
                "시가": open_price,
                "고가": high,
                "저가": low,
                "KRX종가": close,
            }
        )
    return pd.DataFrame(rows)


def _candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_date": pd.Timestamp("2025-01-02"),
                "execution_date": pd.Timestamp("2025-01-03"),
                "종목코드": "000001",
                "market_cap": 1_000.0,
                "rank": 1,
            }
        ]
    )


def _two_rebalance_candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_date": pd.Timestamp("2025-01-02"),
                "execution_date": pd.Timestamp("2025-01-03"),
                "종목코드": "000001",
                "market_cap": 1_000.0,
                "rank": 1,
            },
            {
                "signal_date": pd.Timestamp("2025-01-03"),
                "execution_date": pd.Timestamp("2025-01-06"),
                "종목코드": "000001",
                "market_cap": 1_000.0,
                "rank": 1,
            },
        ]
    )


def _quarterly_regime() -> pd.DataFrame:
    return pd.DataFrame([{"signal_date": pd.Timestamp("2025-01-02"), "regime_on": True}])


def _two_rebalance_regime() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"signal_date": pd.Timestamp("2025-01-02"), "regime_on": True},
            {"signal_date": pd.Timestamp("2025-01-03"), "regime_on": True},
        ]
    )


def _zero_costs() -> Costs:
    return Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
