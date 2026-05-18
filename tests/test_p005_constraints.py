from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.strategies.p005_d013_with_constraints import (
    ProductionConstraints,
    apply_p005_constraints,
    binding_frequency,
)


def test_p005_config_preserves_d013_carrier_definition() -> None:
    d013 = yaml.safe_load(Path("configs/backtests/d013.yaml").read_text(encoding="utf-8"))
    p005 = yaml.safe_load(Path("configs/backtests/p005.yaml").read_text(encoding="utf-8"))

    for key in ("panels", "panel_date_filters", "market_breadth_csv", "macro_data_dir", "period", "universe"):
        assert p005[key] == d013[key]
    for key in ("strategy", "regime", "selection", "rebalance", "costs"):
        assert p005[key] == d013[key]


def test_p005_filters_liquidity_and_status_and_keeps_weight_caps() -> None:
    candidates = _candidates(["000001", "000002", "000003", "000004", "000005"])
    universe = _universe(
        {
            "000001": 6e9,
            "000002": 6e9,
            "000003": 6e9,
            "000004": 6e9,
            "000005": 1e9,
        }
    )
    panel = _panel(["000001", "000002", "000003", "000004", "000005"], halted={"000004"})

    constrained, log = apply_p005_constraints(
        candidates=candidates,
        panel=panel,
        universe=universe,
        constraints=ProductionConstraints(),
        max_positions=5,
    )

    assert constrained.empty
    assert log.loc[0, "liquidity_removed_count"] == 1
    assert log.loc[0, "status_removed_count"] == 1
    assert log.loc[0, "single_weight_bound"] == True
    assert log.loc[0, "top2_weight_bound"] == True


def test_p005_binding_frequency_counts_constraint_quarters() -> None:
    log = pd.DataFrame(
        [
            {
                "single_weight_bound": True,
                "top2_weight_bound": True,
                "liquidity_bound": False,
                "status_bound": False,
                "turnover_bound": False,
            },
            {
                "single_weight_bound": False,
                "top2_weight_bound": False,
                "liquidity_bound": True,
                "status_bound": False,
                "turnover_bound": False,
            },
        ]
    )

    frequency = binding_frequency(log).set_index("constraint")

    assert frequency.loc["single_weight_bound", "binding_frequency"] == 0.5
    assert frequency.loc["liquidity_bound", "binding_quarters"] == 1


def _candidates(tickers: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_date": "2026-03-31",
                "execution_date": "2026-04-01",
                "종목코드": ticker,
                "fnv_5": 0.0,
                "inv_5": 0.0,
                "combined_flow_5": 100.0 - rank,
                "market_cap": 100.0 - rank,
                "rank": rank,
            }
            for rank, ticker in enumerate(tickers, start=1)
        ]
    )


def _universe(liquidity_by_ticker: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_date": "2026-03-31",
                "execution_date": "2026-04-01",
                "종목코드": ticker,
                "avg_traded_value_20d": liquidity,
            }
            for ticker, liquidity in liquidity_by_ticker.items()
        ]
    )


def _panel(tickers: list[str], *, halted: set[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "날짜": "2026-03-31",
                "종목코드": ticker,
                "거래정지여부": ticker in halted,
            }
            for ticker in tickers
        ]
    )
