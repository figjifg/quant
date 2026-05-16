from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import BacktestResult, run_candidate_backtest
from src.data.equity_panel import load_equity_panel
from src.data.market_flow import load_market_flow
from src.data.universe import build_execution_universe
from src.features.flow_ratios import build_atr_pct, build_flow_ratios
from src.features.market_gate import build_kospi_proxy_close_series, build_market_gate_features
from src.features.relative_flow import cross_sectional_std_diagnostic
from src.data.kospi_proxy import load_kospi_proxy
from src.features.regime import regime_gate_on, regime_state_log
from src.reporting.metrics import metrics_is_oos
from src.reporting.report import write_report
from src.roles.exits import exit_signal_reversal, exit_time_cap, exit_volatility_stop_plus_cap
from src.strategies.b001_mcap_normalized import build_b001_mcap_normalized_candidates
from src.strategies.b002_signal_reversal import build_b002_candidates, build_b002_signal_exit_features
from src.strategies.b003_trigger_exploration import TRIGGER_CANDIDATES, build_b003_trigger_exploration
from src.strategies.b004_regime_gate import (
    VARIANTS as B004_VARIANTS,
    build_gate_only_equal_weight_candidates,
    run_b004_variants,
)
from src.strategies.b005_relative_flow import VARIANTS as B005_VARIANTS, run_b005_variants
from src.strategies.baselines import (
    run_b0_cash,
    run_b1_buy_and_hold,
    run_b2_universe_5d_rebalance,
    run_b3_price_momentum,
)
from src.strategies.a001_fixed_holding import build_e001_flow_filter_candidates
from src.strategies.a003_market_gate import build_e003_market_gated_candidates
from src.strategies.a004_strength_quintile import (
    build_e004_quintile_membership,
    build_e004_top_quintile_candidates,
)


EXPECTED_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_E002_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "exit",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_E003_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "market_flow",
    "periods",
    "universe",
    "strategy",
    "exit",
    "gate",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_E004_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "exit",
    "quintile",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B001_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "exit",
    "normalization",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B002_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "exit",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B003_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "exit",
    "trigger",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B004_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "market_flow_csv",
    "market_breadth_csv",
    "periods",
    "universe",
    "strategy",
    "regime",
    "exit",
    "trigger",
    "variants",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B005_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "trigger",
    "exit",
    "variants",
    "relative",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_PERIOD_KEYS = ("is", "oos")
EXPECTED_SPLIT_KEYS = ("start", "end")
EXPECTED_UNIVERSE_KEYS = (
    "require_dynamic_top100",
    "min_avg_traded_value_20d",
    "exclude_estimated_flag_rows",
)
EXPECTED_STRATEGY_KEYS = ("lookback", "holding", "max_positions")
EXPECTED_B002_STRATEGY_KEYS = ("lookback", "max_positions")
EXPECTED_EXIT_KEYS = ("vol_stop_k", "vol_stop_atr_window")
EXPECTED_B002_EXIT_KEYS = ("type",)
EXPECTED_B003_TRIGGER_KEYS = ("candidates",)
EXPECTED_B004_REGIME_KEYS = ("gate_type", "window")
EXPECTED_B004_TRIGGER_KEYS = ("type",)
EXPECTED_B005_RELATIVE_KEYS = ("cross_sectional_min_count",)
EXPECTED_MARKET_FLOW_KEYS = ("path",)
EXPECTED_GATE_KEYS = ("window", "threshold")
EXPECTED_QUINTILE_KEYS = ("value", "min_daily_universe_size")
EXPECTED_NORMALIZATION_KEYS = ("divisor",)
EXPECTED_COST_KEYS = ("commission_bps", "tax_bps_sell", "slippage_bps")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a configured backtest experiment.")
    parser.add_argument("--config", required=True, help="Path to a YAML experiment config.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = _load_config(config_path)
    experiment_id = config.get("experiment_id")
    if experiment_id == "E001":
        _validate_config_shape(config)
        run_experiment(config, config_path)
    elif experiment_id == "E002":
        _validate_e002_config_shape(config)
        run_e002_experiment(config, config_path)
    elif experiment_id == "E003":
        _validate_e003_config_shape(config)
        run_e003_experiment(config, config_path)
    elif experiment_id == "E004":
        _validate_e004_config_shape(config)
        run_e004_experiment(config, config_path)
    elif experiment_id == "B001":
        _validate_b001_config_shape(config)
        run_b001_experiment(config, config_path)
    elif experiment_id == "B002":
        _validate_b002_config_shape(config)
        run_b002_experiment(config, config_path)
    elif experiment_id == "B003":
        _validate_b003_config_shape(config)
        run_b003_experiment(config, config_path)
    elif experiment_id == "B004":
        _validate_b004_config_shape(config)
        run_b004_experiment(config, config_path)
    elif experiment_id == "B005":
        _validate_b005_config_shape(config)
        run_b005_experiment(config, config_path)
    else:
        raise ValueError(f"Unsupported experiment_id: {experiment_id!r}.")


def run_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    headline_candidates = build_e001_flow_filter_candidates(features, headline_universe)

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    holding = int(strategy["holding"])
    costs = _costs_from_config(config["costs"])

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            build_e001_flow_filter_candidates(features, diagnostic_universe),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=holding,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
    )


def run_e002_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    headline_candidates = build_e001_flow_filter_candidates(features, headline_universe)
    diagnostic_candidates = build_e001_flow_filter_candidates(features, diagnostic_universe)

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    holding_cap = int(strategy["holding"])
    costs = _costs_from_config(config["costs"])
    exit_config = config["exit"]
    atr_window = int(exit_config["vol_stop_atr_window"])
    vol_stop_k = float(exit_config["vol_stop_k"])
    atr_features = build_atr_pct(panel, calendar, window=atr_window)
    headline_exit = exit_volatility_stop_plus_cap(holding_cap, vol_stop_k, atr_window, atr_features)
    cap_only_exit = exit_time_cap(holding_cap)
    stop_only_exit = exit_volatility_stop_plus_cap(999, vol_stop_k, atr_window, atr_features)
    e001_replay_exit = exit_time_cap(5)

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **headline_exit,
        ),
        "cap_only": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **cap_only_exit,
        ),
        "stop_only": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **stop_only_exit,
        ),
        "E001_replay": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **e001_replay_exit,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **headline_exit,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _e002_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            candidates=headline_candidates,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            holding_cap=holding_cap,
            vol_stop_k=vol_stop_k,
            atr_window=atr_window,
            atr_features=atr_features,
        )
    )
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=holding_cap,
        vol_stop_k=vol_stop_k,
        vol_stop_atr_window=atr_window,
        atr_features=atr_features,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "cap_only": metrics["cap_only"],
            "stop_only": metrics["stop_only"],
            "E001_replay": metrics["E001_replay"],
            "cost_0_headline": metrics["cost_0_headline"],
            "cost_0_E001_replay": metrics["cost_0_E001_replay"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
    )


def run_e003_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    market_flow = load_market_flow(config["market_flow"]["path"], calendar)
    kospi_proxy_close = build_kospi_proxy_close_series(panel, calendar)
    market_gate_features = build_market_gate_features(market_flow, calendar, kospi_proxy_close)

    headline_candidates = build_e003_market_gated_candidates(
        features,
        headline_universe,
        market_gate_features,
        "market_gate_on",
    )
    cap_only_candidates = build_e001_flow_filter_candidates(features, headline_universe)
    diagnostic_candidates = build_e003_market_gated_candidates(
        features,
        diagnostic_universe,
        market_gate_features,
        "market_gate_on",
    )

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    holding_cap = int(strategy["holding"])
    costs = _costs_from_config(config["costs"])

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "cap_only": run_candidate_backtest(
            panel,
            calendar,
            cap_only_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "inverted_gate": run_candidate_backtest(
            panel,
            calendar,
            build_e003_market_gated_candidates(features, headline_universe, market_gate_features, "market_gate_off"),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "price_gate": run_candidate_backtest(
            panel,
            calendar,
            build_e003_market_gated_candidates(features, headline_universe, market_gate_features, "price_gate_on"),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "double_gate": run_candidate_backtest(
            panel,
            calendar,
            build_e003_market_gated_candidates(features, headline_universe, market_gate_features, "double_gate_on"),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _e003_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            headline_candidates=headline_candidates,
            cap_only_candidates=cap_only_candidates,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            holding_cap=holding_cap,
        )
    )
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "cap_only": metrics["cap_only"],
            "inverted_gate": metrics["inverted_gate"],
            "price_gate": metrics["price_gate"],
            "double_gate": metrics["double_gate"],
            "cost_0_headline": metrics["cost_0_headline"],
            "cost_0_cap_only": metrics["cost_0_cap_only"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
        market_gate_features=market_gate_features,
    )


def run_e004_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)

    quintile = config["quintile"]
    quintile_value = int(quintile["value"])
    min_daily_universe_size = int(quintile["min_daily_universe_size"])
    headline_candidates = build_e004_top_quintile_candidates(
        features,
        headline_universe,
        quintile_value=quintile_value,
        min_daily_universe_size=min_daily_universe_size,
    )
    cap_only_candidates = build_e001_flow_filter_candidates(features, headline_universe)
    diagnostic_candidates = build_e004_top_quintile_candidates(
        features,
        diagnostic_universe,
        quintile_value=quintile_value,
        min_daily_universe_size=min_daily_universe_size,
    )

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    holding_cap = int(strategy["holding"])
    costs = _costs_from_config(config["costs"])

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "cap_only": run_candidate_backtest(
            panel,
            calendar,
            cap_only_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "bottom_quintile": run_candidate_backtest(
            panel,
            calendar,
            build_e004_top_quintile_candidates(
                features,
                headline_universe,
                quintile_value=1,
                min_daily_universe_size=min_daily_universe_size,
            ),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "middle_quintile": run_candidate_backtest(
            panel,
            calendar,
            build_e004_top_quintile_candidates(
                features,
                headline_universe,
                quintile_value=3,
                min_daily_universe_size=min_daily_universe_size,
            ),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "top_decile": run_candidate_backtest(
            panel,
            calendar,
            build_e004_top_quintile_candidates(
                features,
                headline_universe,
                quintile_value="top_decile",
                min_daily_universe_size=min_daily_universe_size,
            ),
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _e003_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            headline_candidates=headline_candidates,
            cap_only_candidates=cap_only_candidates,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            holding_cap=holding_cap,
        )
    )
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    quintile_membership = build_e004_quintile_membership(
        features,
        headline_universe,
        bins=5,
        min_daily_universe_size=min_daily_universe_size,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "cap_only": metrics["cap_only"],
            "bottom_quintile": metrics["bottom_quintile"],
            "middle_quintile": metrics["middle_quintile"],
            "top_decile": metrics["top_decile"],
            "cost_0_headline": metrics["cost_0_headline"],
            "cost_0_cap_only": metrics["cost_0_cap_only"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
        quintile_membership=quintile_membership,
    )


def run_b001_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    headline_candidates = build_b001_mcap_normalized_candidates(features, headline_universe)
    a002_candidates = build_e001_flow_filter_candidates(features, headline_universe)
    diagnostic_candidates = build_b001_mcap_normalized_candidates(features, diagnostic_universe)

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    holding_cap = int(strategy["holding"])
    costs = _costs_from_config(config["costs"])

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "A002_replay": run_candidate_backtest(
            panel,
            calendar,
            a002_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b001_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            headline_candidates=headline_candidates,
            a002_candidates=a002_candidates,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            holding_cap=holding_cap,
        )
    )
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    trade_mcap_composition = _trade_mcap_composition(
        panel=panel,
        trades_by_run={
            "headline": runs["headline"].trades,
            "A002_replay": runs["A002_replay"].trades,
        },
        oos_start=oos_start,
        oos_end=oos_end,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "A002_replay": metrics["A002_replay"],
            "cost_0_headline": metrics["cost_0_headline"],
            "cost_0_A002_replay": metrics["cost_0_A002_replay"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
        trade_mcap_composition=trade_mcap_composition,
    )


def run_b002_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    headline_candidates = build_b002_candidates(features, headline_universe)
    a002_candidates = build_e001_flow_filter_candidates(features, headline_universe)
    diagnostic_candidates = build_b002_candidates(features, diagnostic_universe)
    signal_exit_features = build_b002_signal_exit_features(features)

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    costs = _costs_from_config(config["costs"])
    a002_holding_cap = 20
    signal_exit_kwargs = exit_signal_reversal(features)
    a002_exit_kwargs = exit_time_cap(a002_holding_cap)

    runs: dict[str, BacktestResult] = {
        "headline": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        ),
        "A002_replay": run_candidate_backtest(
            panel,
            calendar,
            a002_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **a002_exit_kwargs,
        ),
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b002_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            headline_candidates=headline_candidates,
            a002_candidates=a002_candidates,
            signal_exit_features=signal_exit_features,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            a002_holding_cap=a002_holding_cap,
        )
    )
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=headline_candidates,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=signal_exit_features,
    )
    split_dates = {"is": (is_start, is_end), "oos": (oos_start, oos_end)}
    exit_reason_breakdown = _exit_reason_breakdown(
        trades_by_run={
            "headline": runs["headline"].trades,
            "A002_replay": runs["A002_replay"].trades,
        },
        split_dates=split_dates,
    )
    holding_period_distribution = _holding_period_distribution(
        trades_by_run={
            "headline": runs["headline"].trades,
            "A002_replay": runs["A002_replay"].trades,
        },
        oos_start=oos_start,
        oos_end=oos_end,
        calendar=calendar,
    )
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=headline_candidates,
        headline_result=runs["headline"],
        metrics=metrics,
        report_metrics={
            "is": metrics["headline"]["is"],
            "oos": metrics["headline"]["oos"],
            "full": metrics["headline"]["full"],
            "A002_replay": metrics["A002_replay"],
            "cost_0_headline": metrics["cost_0_headline"],
            "cost_0_A002_replay": metrics["cost_0_A002_replay"],
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
        exit_reason_breakdown=exit_reason_breakdown,
        holding_period_distribution=holding_period_distribution,
    )


def run_b003_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, diagnostic_universe = _build_common_inputs(config)
    trigger_candidates, signal_exit_kwargs = build_b003_trigger_exploration(features, headline_universe)
    diagnostic_candidates, _ = build_b003_trigger_exploration(features, diagnostic_universe)

    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    strategy = config["strategy"]
    max_positions = int(strategy["max_positions"])
    costs = _costs_from_config(config["costs"])
    labels = {
        "immediate": "T1_immediate",
        "freshness": "T2_freshness",
        "acceleration": "T3_acceleration",
        "persistence_3d": "T4_persistence_3d",
    }

    trigger_runs = {
        labels[name]: run_candidate_backtest(
            panel,
            calendar,
            trigger_candidates[name],
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        )
        for name in TRIGGER_CANDIDATES
    }
    runs: dict[str, BacktestResult] = {
        **trigger_runs,
        "B0": run_b0_cash(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B1": run_b1_buy_and_hold(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B2": run_b2_universe_5d_rebalance(
            panel,
            calendar,
            features,
            diagnostic_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "B3": run_b3_price_momentum(
            panel,
            calendar,
            features,
            headline_universe,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
        ),
        "diagnostic_estimate_included": run_candidate_backtest(
            panel,
            calendar,
            diagnostic_candidates["immediate"],
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        ),
    }
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b003_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            candidates_by_label={labels[name]: trigger_candidates[name] for name in TRIGGER_CANDIDATES},
            signal_exit_features=signal_exit_kwargs["signal_exit_features"],
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
        )
    )

    best_label = max((labels[name] for name in TRIGGER_CANDIDATES), key=lambda label: metrics[label]["oos"]["total_return"])
    best_name = next(name for name, label in labels.items() if label == best_label)
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=trigger_candidates[best_name],
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=signal_exit_kwargs["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "run", best_label)
    split_dates = {"is": (is_start, is_end), "oos": (oos_start, oos_end)}
    exit_reason_breakdown = _exit_reason_breakdown(
        trades_by_run={label: trigger_runs[label].trades for label in labels.values()},
        split_dates=split_dates,
    )
    holding_period_distribution = _holding_period_distribution(
        trades_by_run={label: trigger_runs[label].trades for label in labels.values()},
        oos_start=oos_start,
        oos_end=oos_end,
        calendar=calendar,
    )
    trade_set_overlap = _trade_set_overlap_matrix(
        trades_by_run={label: trigger_runs[label].trades for label in labels.values()},
        oos_start=oos_start,
        oos_end=oos_end,
    )

    immediate_label = labels["immediate"]
    _write_outputs(
        config=config,
        config_path=config_path,
        panel=panel,
        calendar=calendar,
        headline_candidates=trigger_candidates["immediate"],
        headline_result=trigger_runs[immediate_label],
        metrics=metrics,
        report_metrics={
            label: metrics[label] for label in labels.values()
        }
        | {
            f"cost_0_{label}": metrics[f"cost_0_{label}"] for label in labels.values()
        }
        | {
            "diagnostic_estimate_included": metrics["diagnostic_estimate_included"],
        },
        baselines={
            "B0_cash": metrics["B0"],
            "B1_buy_and_hold": metrics["B1"],
            "B2_universe_5d_rebalance": metrics["B2"],
            "B3_price_momentum": metrics["B3"],
        },
        cost_sensitivity=cost_sensitivity,
        exit_reason_breakdown=exit_reason_breakdown,
        holding_period_distribution=holding_period_distribution,
    )
    output_dir = Path(config["output_dir"])
    for name in TRIGGER_CANDIDATES:
        label = labels[name]
        _write_ticker_safe_csv(trigger_runs[label].trades, output_dir / f"trades_{name}.csv")
        _write_ticker_safe_csv(_signals_frame(trigger_candidates[name]), output_dir / f"signals_{name}.csv")
        trigger_runs[label].equity_curve.to_csv(output_dir / f"equity_curve_{name}.csv", index=False)
    trade_set_overlap.to_csv(output_dir / "trade_set_overlap.csv", index=False)


def run_b004_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    costs = _costs_from_config(config["costs"])
    kospi_proxy = load_kospi_proxy(config["market_breadth_csv"], window=int(config["regime"]["window"]))

    runs, candidates, gate_frame = run_b004_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=headline_universe,
        kospi_proxy=kospi_proxy,
        costs=costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
    )
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b004_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            features=features,
            universe=headline_universe,
            kospi_proxy=kospi_proxy,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
        )
    )
    cost_sensitivity = _b004_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        features=features,
        universe=headline_universe,
        kospi_proxy=kospi_proxy,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
    )
    regime_log = regime_state_log(kospi_proxy)
    regime_year_breakdown = _b004_regime_year_breakdown(
        runs=runs,
        regime_log=regime_log,
        calendar=calendar,
        start=is_start,
        end=oos_end,
    )
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b004_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b004_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    regime_year_breakdown.to_csv(output_dir / "regime_year_breakdown.csv", index=False)
    regime_log.to_csv(output_dir / "regime_state_log.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b004_report(output_dir, config, metrics, regime_year_breakdown, cost_sensitivity)


def run_b005_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    min_count = int(config["relative"]["cross_sectional_min_count"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, exit_kwargs, relative_features = run_b005_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=headline_universe,
        costs=costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
        min_count=min_count,
    )
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b005_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            features=features,
            universe=headline_universe,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
            min_count=min_count,
        )
    )
    year_breakdown = _b005_year_breakdown(runs=runs, calendar=calendar, start=is_start, end=oos_end)
    overlap_matrix = _b005_trade_overlap_matrix(runs)
    std_diagnostic = cross_sectional_std_diagnostic(features, headline_universe)
    best_variant = max(B005_VARIANTS, key=lambda variant: metrics[variant]["oos"]["total_return"])
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=candidates[best_variant],
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=exit_kwargs[best_variant]["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "variant", best_variant)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b005_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b005_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b005_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "signal_redesign_year_breakdown.csv", index=False)
    std_diagnostic.to_csv(output_dir / "cross_sectional_std.csv", index=False)
    overlap_matrix.to_csv(output_dir / "trigger_overlap_matrix.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b005_report(output_dir, config, metrics, year_breakdown, overlap_matrix, cost_sensitivity)


def _build_common_inputs(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, object, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    panel = load_equity_panel(config["panels"])
    calendar = derive_trading_calendar(panel)
    features = build_flow_ratios(panel, calendar)
    headline_universe = build_execution_universe(
        panel,
        calendar,
        min_avg_traded_value_20d=float(config["universe"]["min_avg_traded_value_20d"]),
        exclude_estimated_flag_rows=bool(config["universe"]["exclude_estimated_flag_rows"]),
    )
    diagnostic_universe = build_execution_universe(
        panel,
        calendar,
        min_avg_traded_value_20d=float(config["universe"]["min_avg_traded_value_20d"]),
        exclude_estimated_flag_rows=False,
    )
    return panel, calendar, features, headline_universe, diagnostic_universe


def _metrics_for_runs(
    runs: dict[str, BacktestResult],
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    calendar: object,
) -> dict[str, dict[str, dict[str, float | int]]]:
    return {
        name: metrics_is_oos(result.equity_curve, result.trades, is_start, is_end, oos_start, oos_end, calendar)
        for name, result in runs.items()
    }


def _e002_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    holding_cap: int,
    vol_stop_k: float,
    atr_window: int,
    atr_features: pd.DataFrame,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    headline_exit = exit_volatility_stop_plus_cap(holding_cap, vol_stop_k, atr_window, atr_features)
    e001_replay_exit = exit_time_cap(5)
    cost_0_headline = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        **headline_exit,
    )
    cost_0_e001_replay = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        **e001_replay_exit,
    )
    return {
        "cost_0_headline": metrics_is_oos(
            cost_0_headline.equity_curve,
            cost_0_headline.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
        "cost_0_E001_replay": metrics_is_oos(
            cost_0_e001_replay.equity_curve,
            cost_0_e001_replay.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
    }


def _e003_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    headline_candidates: pd.DataFrame,
    cap_only_candidates: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    holding_cap: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    cost_0_headline = run_candidate_backtest(
        panel,
        calendar,
        headline_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    cost_0_cap_only = run_candidate_backtest(
        panel,
        calendar,
        cap_only_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    return {
        "cost_0_headline": metrics_is_oos(
            cost_0_headline.equity_curve,
            cost_0_headline.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
        "cost_0_cap_only": metrics_is_oos(
            cost_0_cap_only.equity_curve,
            cost_0_cap_only.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
    }


def _b001_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    headline_candidates: pd.DataFrame,
    a002_candidates: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    holding_cap: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    cost_0_headline = run_candidate_backtest(
        panel,
        calendar,
        headline_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    cost_0_a002_replay = run_candidate_backtest(
        panel,
        calendar,
        a002_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=holding_cap,
    )
    return {
        "cost_0_headline": metrics_is_oos(
            cost_0_headline.equity_curve,
            cost_0_headline.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
        "cost_0_A002_replay": metrics_is_oos(
            cost_0_a002_replay.equity_curve,
            cost_0_a002_replay.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
    }


def _b002_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    headline_candidates: pd.DataFrame,
    a002_candidates: pd.DataFrame,
    signal_exit_features: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    a002_holding_cap: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    signal_exit_kwargs = {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": signal_exit_features,
    }
    a002_exit_kwargs = exit_time_cap(a002_holding_cap)
    cost_0_headline = run_candidate_backtest(
        panel,
        calendar,
        headline_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        **signal_exit_kwargs,
    )
    cost_0_a002_replay = run_candidate_backtest(
        panel,
        calendar,
        a002_candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        **a002_exit_kwargs,
    )
    return {
        "cost_0_headline": metrics_is_oos(
            cost_0_headline.equity_curve,
            cost_0_headline.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
        "cost_0_A002_replay": metrics_is_oos(
            cost_0_a002_replay.equity_curve,
            cost_0_a002_replay.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        ),
    }


def _b003_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    candidates_by_label: dict[str, pd.DataFrame],
    signal_exit_features: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    signal_exit_kwargs = {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": signal_exit_features,
    }
    metrics: dict[str, dict[str, dict[str, float | int]]] = {}
    for label, candidates in candidates_by_label.items():
        result = run_candidate_backtest(
            panel,
            calendar,
            candidates,
            zero_costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            **signal_exit_kwargs,
        )
        metrics[f"cost_0_{label}"] = metrics_is_oos(
            result.equity_curve,
            result.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        )
    return metrics


def _b004_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    kospi_proxy: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    runs, _, _ = run_b004_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        kospi_proxy=kospi_proxy,
        costs=zero_costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
    )
    return {
        f"cost_0_{name}": metrics_is_oos(result.equity_curve, result.trades, is_start, is_end, oos_start, oos_end, calendar)
        for name, result in runs.items()
        if name != "cash"
    }


def _b004_cost_sensitivity(
    *,
    panel: pd.DataFrame,
    calendar: object,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    kospi_proxy: pd.DataFrame,
    base_costs: Costs,
    multipliers: list[float],
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for multiplier in multipliers:
        scaled_costs = Costs(
            commission_bps=base_costs.commission_bps * float(multiplier),
            tax_bps_sell=base_costs.tax_bps_sell * float(multiplier),
            slippage_bps=base_costs.slippage_bps * float(multiplier),
        )
        runs, _, _ = run_b004_variants(
            panel=panel,
            calendar=calendar,
            flow_features=features,
            universe=universe,
            kospi_proxy=kospi_proxy,
            costs=scaled_costs,
            period_start=is_start,
            period_end=oos_end,
            max_positions=max_positions,
        )
        for variant, result in runs.items():
            if variant == "cash":
                continue
            metric_block = metrics_is_oos(result.equity_curve, result.trades, is_start, is_end, oos_start, oos_end, calendar)
            rows.append(
                {
                    "variant": variant,
                    "multiplier": float(multiplier),
                    "is_total_return": metric_block["is"]["total_return"],
                    "oos_total_return": metric_block["oos"]["total_return"],
                    "full_total_return": metric_block["full"]["total_return"],
                    "cost_paid_total": metric_block["full"]["cost_paid_total"],
                }
            )
    return pd.DataFrame(rows)


def _write_outputs(
    *,
    config: dict[str, Any],
    config_path: Path,
    panel: pd.DataFrame,
    calendar: object,
    headline_candidates: pd.DataFrame,
    headline_result: BacktestResult,
    metrics: dict[str, Any],
    report_metrics: dict[str, Any],
    baselines: dict[str, dict[str, Any]],
    cost_sensitivity: pd.DataFrame,
    market_gate_features: pd.DataFrame | None = None,
    quintile_membership: pd.DataFrame | None = None,
    trade_mcap_composition: pd.DataFrame | None = None,
    exit_reason_breakdown: pd.DataFrame | None = None,
    holding_period_distribution: pd.DataFrame | None = None,
) -> None:
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(headline_result.trades, output_dir / "trades.csv")
    _write_ticker_safe_csv(
        _signals_frame(headline_candidates, include_signal_value=config.get("experiment_id") != "E001"),
        output_dir / "signals.csv",
    )
    headline_result.equity_curve.to_csv(output_dir / "equity_curve.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    if market_gate_features is not None:
        _market_gate_timeseries(market_gate_features).to_csv(output_dir / "market_gate_timeseries.csv", index=False)
    if quintile_membership is not None:
        _write_ticker_safe_csv(
            _quintile_membership_sample(quintile_membership),
            output_dir / "quintile_membership_sample.csv",
        )
    if trade_mcap_composition is not None:
        trade_mcap_composition.to_csv(output_dir / "trade_mcap_composition.csv", index=False)
    if exit_reason_breakdown is not None:
        exit_reason_breakdown.to_csv(output_dir / "exit_reason_breakdown.csv", index=False)
    if holding_period_distribution is not None:
        holding_period_distribution.to_csv(output_dir / "holding_period_distribution.csv", index=False)
    write_report(output_dir, _metadata(config, panel, calendar), report_metrics, baselines, cost_sensitivity)


def _run_cost_sensitivity(
    *,
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    base_costs: Costs,
    multipliers: list[float],
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    holding: int,
    vol_stop_k: float | None = None,
    vol_stop_atr_window: int = 20,
    atr_features: pd.DataFrame | None = None,
    signal_exit_features: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for multiplier in multipliers:
        scaled_costs = Costs(
            commission_bps=base_costs.commission_bps * float(multiplier),
            tax_bps_sell=base_costs.tax_bps_sell * float(multiplier),
            slippage_bps=base_costs.slippage_bps * float(multiplier),
        )
        result = run_candidate_backtest(
            panel,
            calendar,
            candidates,
            scaled_costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding,
            vol_stop_k=vol_stop_k,
            vol_stop_atr_window=vol_stop_atr_window,
            atr_features=atr_features,
            signal_exit_features=signal_exit_features,
        )
        metric_block = metrics_is_oos(
            result.equity_curve,
            result.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        )
        rows.append(
            {
                "multiplier": float(multiplier),
                "is_total_return": metric_block["is"]["total_return"],
                "oos_total_return": metric_block["oos"]["total_return"],
                "full_total_return": metric_block["full"]["total_return"],
                "cost_paid_total": metric_block["full"]["cost_paid_total"],
            }
        )
    return pd.DataFrame(rows)


def _combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B004_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b004_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B004_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _signal_included_in_trade(signals: pd.DataFrame, trades: pd.DataFrame) -> pd.Series:
    if signals.empty or trades.empty:
        return pd.Series(False, index=signals.index)
    trade_keys = {
        (pd.Timestamp(signal_date).normalize(), pd.Timestamp(entry_date).normalize(), str(ticker))
        for signal_date, entry_date, ticker in zip(
            trades["signal_date"],
            trades["entry_date"],
            trades["종목코드"],
            strict=False,
        )
    }
    return pd.Series(
        [
            (
                pd.Timestamp(signal_date).normalize(),
                pd.Timestamp(execution_date).normalize(),
                str(ticker),
            )
            in trade_keys
            for signal_date, execution_date, ticker in zip(
                signals["signal_date"],
                signals["execution_date"],
                signals["종목코드"],
                strict=False,
            )
        ],
        index=signals.index,
    )


def _b004_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["signal_plus_gate"].equity_curve["date"]})
    output["signal_plus_gate_value"] = runs["signal_plus_gate"].equity_curve["net_value"].to_numpy()
    output["signal_only_value"] = runs["signal_only"].equity_curve["net_value"].to_numpy()
    output["gate_only_value"] = runs["gate_only_equal_weight"].equity_curve["net_value"].to_numpy()
    output["cash_value"] = runs["cash"].equity_curve["net_value"].to_numpy()
    return output


def _b004_regime_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    regime_log: pd.DataFrame,
    calendar: object,
    start: object,
    end: object,
) -> pd.DataFrame:
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    years = range(start_ts.year, end_ts.year + 1)
    rows = []
    for year in years:
        year_start = max(pd.Timestamp(year=year, month=1, day=1), start_ts)
        year_end = min(pd.Timestamp(year=year, month=12, day=31), end_ts)
        row: dict[str, Any] = {"year": year}
        for variant in B004_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["delta_signal_plus_gate_minus_gate_only"] = (
            row["signal_plus_gate_net_total_return"] - row["gate_only_equal_weight_net_total_return"]
        )
        row["delta_signal_plus_gate_minus_signal_only"] = (
            row["signal_plus_gate_net_total_return"] - row["signal_only_net_total_return"]
        )
        year_regime = regime_log.loc[
            pd.to_datetime(regime_log["signal_date"], errors="raise").dt.year.eq(year)
        ]
        row["gate_on_days"] = int(year_regime["regime_gate_on"].sum())
        row["gate_off_days"] = int(len(year_regime) - row["gate_on_days"])
        rows.append(row)
    return pd.DataFrame(rows)


def _write_b004_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    regime_year_breakdown: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B004 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| is_start | {config['periods']['is']['start']} |",
            f"| is_end | {config['periods']['is']['end']} |",
            f"| oos_start | {config['periods']['oos']['start']} |",
            f"| oos_end | {config['periods']['oos']['end']} |",
            "| regime_gate | KOSPI proxy level > same-day 200-day SMA; entry-side only for signal variants; gate-off exit for gate-only variant |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            "",
        ]
    )
    lines.extend(_b004_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b004_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("Regime Year Breakdown", regime_year_breakdown))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b004_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B004_VARIANTS:
        block = metrics[variant][split]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    lines.append("")
    return lines


def _format_report_value(value: Any) -> str:
    if isinstance(value, float):
        return str(value)
    return str(value)


def _b004_dataframe_table(title: str, data: pd.DataFrame) -> list[str]:
    lines = [f"## {title}", ""]
    if data.empty:
        lines.extend(["| empty |", "| --- |", ""])
        return lines
    columns = [str(column) for column in data.columns]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for _, row in data.iterrows():
        lines.append("| " + " | ".join(_format_report_value(row[column]) for column in data.columns) + " |")
    lines.append("")
    return lines


def _b005_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
    min_count: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    runs, _, _, _ = run_b005_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=zero_costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
        min_count=min_count,
    )
    return {
        f"cost_0_{variant}": metrics_is_oos(
            result.equity_curve,
            result.trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        )
        for variant, result in runs.items()
    }


def _b005_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B005_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b005_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B005_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        if "rank_score" in candidates[variant].columns:
            signals["signal_value"] = candidates[variant]["rank_score"].to_numpy()
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b005_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["absolute_baseline"].equity_curve["date"]})
    for variant in B005_VARIANTS:
        output[f"{variant}_value"] = runs[variant].equity_curve["net_value"].to_numpy()
    return output


def _b005_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    start: object,
    end: object,
) -> pd.DataFrame:
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    rows = []
    for year in range(start_ts.year, end_ts.year + 1):
        year_start = max(pd.Timestamp(year=year, month=1, day=1), start_ts)
        year_end = min(pd.Timestamp(year=year, month=12, day=31), end_ts)
        row: dict[str, Any] = {
            "year": year,
            "is_h1_check_2020": year == 2020,
            "oos_h3_check_2025": year == 2025,
        }
        for variant in B005_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["relative_zscore_minus_absolute_baseline"] = (
            row["relative_zscore_net_total_return"] - row["absolute_baseline_net_total_return"]
        )
        row["relative_median_diff_minus_absolute_baseline"] = (
            row["relative_median_diff_net_total_return"] - row["absolute_baseline_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _b005_trade_overlap_matrix(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    trade_sets = {variant: _entry_ticker_set(runs[variant].trades) for variant in B005_VARIANTS}
    rows = []
    for left in B005_VARIANTS:
        row: dict[str, Any] = {"variant": left}
        for right in B005_VARIANTS:
            union = trade_sets[left].union(trade_sets[right])
            row[right] = 1.0 if not union else len(trade_sets[left].intersection(trade_sets[right])) / len(union)
        rows.append(row)
    return pd.DataFrame(rows)


def _entry_ticker_set(trades: pd.DataFrame) -> set[tuple[pd.Timestamp, str]]:
    if trades.empty:
        return set()
    return {
        (pd.Timestamp(entry_date).normalize(), str(ticker))
        for entry_date, ticker in zip(trades["entry_date"], trades["종목코드"], strict=False)
    }


def _write_b005_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    overlap_matrix: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B005 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| is_start | {config['periods']['is']['start']} |",
            f"| is_end | {config['periods']['is']['end']} |",
            f"| oos_start | {config['periods']['oos']['start']} |",
            f"| oos_end | {config['periods']['oos']['end']} |",
            "| strategy | B005 absolute baseline vs relative z-score vs relative median-diff alpha definitions |",
            "| trigger | trigger_immediate for all variants |",
            "| exit | signal reversal using each variant's own alpha columns; relative columns are renamed before engine handoff |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            "",
        ]
    )
    lines.extend(_b005_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b005_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("Signal Redesign Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Trade-Set Overlap", overlap_matrix))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b005_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B005_VARIANTS:
        block = metrics[variant][split]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    lines.append("")
    return lines


def _load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("Config must be a YAML mapping.")
    return loaded


def _validate_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_CONFIG_KEYS:
        raise ValueError(f"Config keys must be exactly {EXPECTED_CONFIG_KEYS}; got {keys}.")
    _validate_common_config_shape(config, "E001")


def _validate_e002_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E002_CONFIG_KEYS:
        raise ValueError(f"E002 config keys must be exactly {EXPECTED_E002_CONFIG_KEYS}; got {keys}.")
    _validate_common_config_shape(config, "E002")
    if tuple(config["exit"].keys()) != EXPECTED_EXIT_KEYS:
        raise ValueError(f"exit keys must be exactly {EXPECTED_EXIT_KEYS}.")
    if int(config["strategy"]["holding"]) != 20:
        raise ValueError("E002 requires strategy.holding: 20.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("E002 requires strategy.max_positions: 5.")
    if float(config["exit"]["vol_stop_k"]) != 2.0:
        raise ValueError("E002 requires exit.vol_stop_k: 2.0.")
    if int(config["exit"]["vol_stop_atr_window"]) != 20:
        raise ValueError("E002 requires exit.vol_stop_atr_window: 20.")


def _validate_e003_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E003_CONFIG_KEYS:
        raise ValueError(f"E003 config keys must be exactly {EXPECTED_E003_CONFIG_KEYS}; got {keys}.")
    _validate_common_config_shape(config, "E003")
    if tuple(config["market_flow"].keys()) != EXPECTED_MARKET_FLOW_KEYS:
        raise ValueError(f"market_flow keys must be exactly {EXPECTED_MARKET_FLOW_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_EXIT_KEYS:
        raise ValueError(f"exit keys must be exactly {EXPECTED_EXIT_KEYS}.")
    if tuple(config["gate"].keys()) != EXPECTED_GATE_KEYS:
        raise ValueError(f"gate keys must be exactly {EXPECTED_GATE_KEYS}.")
    if int(config["strategy"]["holding"]) != 20:
        raise ValueError("E003 requires strategy.holding: 20.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("E003 requires strategy.max_positions: 5.")
    if config["exit"]["vol_stop_k"] is not None:
        raise ValueError("E003 requires exit.vol_stop_k: null.")
    if int(config["exit"]["vol_stop_atr_window"]) != 20:
        raise ValueError("E003 requires exit.vol_stop_atr_window: 20.")
    if int(config["gate"]["window"]) != 5:
        raise ValueError("E003 requires gate.window: 5.")
    if float(config["gate"]["threshold"]) != 0.0:
        raise ValueError("E003 requires gate.threshold: 0.")


def _validate_e004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E004_CONFIG_KEYS:
        raise ValueError(f"E004 config keys must be exactly {EXPECTED_E004_CONFIG_KEYS}; got {keys}.")
    _validate_common_config_shape(config, "E004")
    if tuple(config["exit"].keys()) != EXPECTED_EXIT_KEYS:
        raise ValueError(f"exit keys must be exactly {EXPECTED_EXIT_KEYS}.")
    if tuple(config["quintile"].keys()) != EXPECTED_QUINTILE_KEYS:
        raise ValueError(f"quintile keys must be exactly {EXPECTED_QUINTILE_KEYS}.")
    if int(config["strategy"]["holding"]) != 20:
        raise ValueError("E004 requires strategy.holding: 20.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("E004 requires strategy.max_positions: 5.")
    if config["exit"]["vol_stop_k"] is not None:
        raise ValueError("E004 requires exit.vol_stop_k: null.")
    if int(config["exit"]["vol_stop_atr_window"]) != 20:
        raise ValueError("E004 requires exit.vol_stop_atr_window: 20.")
    if int(config["quintile"]["value"]) != 5:
        raise ValueError("E004 requires quintile.value: 5.")
    if int(config["quintile"]["min_daily_universe_size"]) != 20:
        raise ValueError("E004 requires quintile.min_daily_universe_size: 20.")


def _validate_b001_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B001_CONFIG_KEYS:
        raise ValueError(f"B001 config keys must be exactly {EXPECTED_B001_CONFIG_KEYS}; got {keys}.")
    _validate_common_config_shape(config, "B001")
    if tuple(config["exit"].keys()) != EXPECTED_EXIT_KEYS:
        raise ValueError(f"exit keys must be exactly {EXPECTED_EXIT_KEYS}.")
    if tuple(config["normalization"].keys()) != EXPECTED_NORMALIZATION_KEYS:
        raise ValueError(f"normalization keys must be exactly {EXPECTED_NORMALIZATION_KEYS}.")
    if int(config["strategy"]["holding"]) != 20:
        raise ValueError("B001 requires strategy.holding: 20.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B001 requires strategy.max_positions: 5.")
    if config["exit"]["vol_stop_k"] is not None:
        raise ValueError("B001 requires exit.vol_stop_k: null.")
    if int(config["exit"]["vol_stop_atr_window"]) != 20:
        raise ValueError("B001 requires exit.vol_stop_atr_window: 20.")
    if config["normalization"]["divisor"] != "시가총액":
        raise ValueError("B001 requires normalization.divisor: 시가총액.")


def _validate_b002_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B002_CONFIG_KEYS:
        raise ValueError(f"B002 config keys must be exactly {EXPECTED_B002_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError(f"B002 exit keys must be exactly {EXPECTED_B002_EXIT_KEYS}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B002 requires strategy.max_positions: 5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B002 requires exit.type: signal_reversal.")


def _validate_b003_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B003_CONFIG_KEYS:
        raise ValueError(f"B003 config keys must be exactly {EXPECTED_B003_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B003 exit keys must be exactly ('type',).")
    if tuple(config["trigger"].keys()) != EXPECTED_B003_TRIGGER_KEYS:
        raise ValueError(f"B003 trigger keys must be exactly {EXPECTED_B003_TRIGGER_KEYS}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B003 requires strategy.max_positions: 5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B003 requires exit.type: signal_reversal.")
    if tuple(config["trigger"]["candidates"]) != TRIGGER_CANDIDATES:
        raise ValueError(f"B003 trigger.candidates must be exactly {list(TRIGGER_CANDIDATES)}.")


def _validate_b004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B004_CONFIG_KEYS:
        raise ValueError(f"B004 config keys must be exactly {EXPECTED_B004_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["regime"].keys()) != EXPECTED_B004_REGIME_KEYS:
        raise ValueError(f"B004 regime keys must be exactly {EXPECTED_B004_REGIME_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B004 exit keys must be exactly ('type',).")
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B004 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["variants"]) != B004_VARIANTS:
        raise ValueError(f"B004 variants must be exactly {list(B004_VARIANTS)}.")
    if config["regime"]["gate_type"] != "kospi_sma":
        raise ValueError("B004 requires regime.gate_type: kospi_sma.")
    if int(config["regime"]["window"]) != 200:
        raise ValueError("B004 requires regime.window: 200.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B004 requires exit.type: signal_reversal.")
    if config["trigger"]["type"] != "immediate":
        raise ValueError("B004 requires trigger.type: immediate.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B004 requires strategy.max_positions: 5.")


def _validate_b005_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B005_CONFIG_KEYS:
        raise ValueError(f"B005 config keys must be exactly {EXPECTED_B005_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B005 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B005 exit keys must be exactly ('type',).")
    if tuple(config["relative"].keys()) != EXPECTED_B005_RELATIVE_KEYS:
        raise ValueError(f"B005 relative keys must be exactly {EXPECTED_B005_RELATIVE_KEYS}.")
    if tuple(config["variants"]) != B005_VARIANTS:
        raise ValueError(f"B005 variants must be exactly {list(B005_VARIANTS)}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B005 requires strategy.max_positions: 5.")
    if config["trigger"]["type"] != "immediate":
        raise ValueError("B005 requires trigger.type: immediate.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B005 requires exit.type: signal_reversal.")
    if int(config["relative"]["cross_sectional_min_count"]) != 30:
        raise ValueError("B005 requires relative.cross_sectional_min_count: 30.")


def _validate_common_config_shape(config: dict[str, Any], experiment_id: str) -> None:
    if tuple(config["periods"].keys()) != EXPECTED_PERIOD_KEYS:
        raise ValueError(f"periods keys must be exactly {EXPECTED_PERIOD_KEYS}.")
    for split in EXPECTED_PERIOD_KEYS:
        if tuple(config["periods"][split].keys()) != EXPECTED_SPLIT_KEYS:
            raise ValueError(f"periods.{split} keys must be exactly {EXPECTED_SPLIT_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_STRATEGY_KEYS:
        raise ValueError(f"strategy keys must be exactly {EXPECTED_STRATEGY_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError(f"{experiment_id} requires universe.require_dynamic_top100: true.")
    if int(config["strategy"]["lookback"]) != 5:
        raise ValueError(f"{experiment_id} requires strategy.lookback: 5.")


def _validate_b002_common_config_shape(config: dict[str, Any]) -> None:
    if tuple(config["periods"].keys()) != EXPECTED_PERIOD_KEYS:
        raise ValueError(f"periods keys must be exactly {EXPECTED_PERIOD_KEYS}.")
    for split in EXPECTED_PERIOD_KEYS:
        if tuple(config["periods"][split].keys()) != EXPECTED_SPLIT_KEYS:
            raise ValueError(f"periods.{split} keys must be exactly {EXPECTED_SPLIT_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_B002_STRATEGY_KEYS:
        raise ValueError(f"B002 strategy keys must be exactly {EXPECTED_B002_STRATEGY_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("B002 requires universe.require_dynamic_top100: true.")
    if int(config["strategy"]["lookback"]) != 5:
        raise ValueError("B002 requires strategy.lookback: 5.")


def _costs_from_config(costs: dict[str, Any]) -> Costs:
    return Costs(
        commission_bps=float(costs["commission_bps"]),
        tax_bps_sell=float(costs["tax_bps_sell"]),
        slippage_bps=float(costs["slippage_bps"]),
    )


def _signals_frame(candidates: pd.DataFrame, *, include_signal_value: bool = True) -> pd.DataFrame:
    columns = ["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"]
    if "combined_flow_5_mcap" in candidates.columns:
        columns.append("combined_flow_5_mcap")
    signals = candidates.loc[:, columns].copy()
    if include_signal_value:
        signals["signal_value"] = (
            signals["combined_flow_5_mcap"]
            if "combined_flow_5_mcap" in signals.columns
            else signals["combined_flow_5"]
        )
    signals["signal"] = True
    return signals


def _market_gate_timeseries(market_gate_features: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "signal_date",
        "execution_date",
        "kospi_combined_net_5",
        "market_gate_on",
        "kospi_5d_return",
        "price_gate_on",
        "double_gate_on",
    ]
    return market_gate_features.loc[:, columns].copy()


def _quintile_membership_sample(quintile_membership: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "signal_date",
        "execution_date",
        "eligible_universe_size",
        "target_quintile_min",
        "target_quintile_max",
        "종목코드",
        "combined_flow_5",
        "quantile_label",
        "selected_headline",
    ]
    if quintile_membership.empty:
        return pd.DataFrame(columns=columns)

    labeled = quintile_membership.copy()
    labeled["selected_headline"] = (
        labeled["quantile_label"].eq(5) & labeled["fnv_5"].gt(0) & labeled["inv_5"].gt(0)
    )
    labeled["eligible_universe_size"] = labeled.groupby("signal_date")["종목코드"].transform("size")
    target = labeled.loc[labeled["quantile_label"].eq(5)]
    bounds = target.groupby("signal_date")["combined_flow_5"].agg(
        target_quintile_min="min",
        target_quintile_max="max",
    )
    labeled = labeled.merge(bounds, on="signal_date", how="left", validate="many_to_one")
    dates = pd.Series(labeled["signal_date"].drop_duplicates().sort_values())
    sampled_dates = dates.sample(n=min(20, len(dates)), random_state=4).sort_values()
    sample = labeled.loc[labeled["signal_date"].isin(set(sampled_dates))]
    sample = sample.loc[sample["quantile_label"].eq(5)]
    return sample.loc[:, columns].sort_values(
        ["signal_date", "combined_flow_5", "종목코드"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def _trade_mcap_composition(
    *,
    panel: pd.DataFrame,
    trades_by_run: dict[str, pd.DataFrame],
    oos_start: object,
    oos_end: object,
) -> pd.DataFrame:
    mcap = panel.loc[:, ["날짜", "종목코드", "시가총액추정"]].copy()
    mcap["날짜"] = pd.to_datetime(mcap["날짜"], errors="raise").astype("datetime64[ns]")
    mcap["종목코드"] = mcap["종목코드"].astype("string")
    rows: list[pd.DataFrame] = []
    for run_name, trades in trades_by_run.items():
        if trades.empty:
            continue
        trade_mcaps = trades.loc[:, ["entry_date", "signal_date", "종목코드"]].copy()
        trade_mcaps["entry_date"] = pd.to_datetime(trade_mcaps["entry_date"], errors="raise").astype(
            "datetime64[ns]"
        )
        trade_mcaps["종목코드"] = trade_mcaps["종목코드"].astype("string")
        trade_mcaps = trade_mcaps.merge(
            mcap,
            left_on=["entry_date", "종목코드"],
            right_on=["날짜", "종목코드"],
            how="left",
            validate="many_to_one",
        )
        trade_mcaps["run"] = run_name
        trade_mcaps["year"] = trade_mcaps["entry_date"].dt.year
        rows.append(trade_mcaps)

    columns = ["run", "period", "year", "trade_count", "median_entry_mcap"]
    if not rows:
        return pd.DataFrame(columns=columns)

    combined = pd.concat(rows, ignore_index=True)
    oos_start_ts = pd.Timestamp(oos_start).normalize()
    oos_end_ts = pd.Timestamp(oos_end).normalize()
    combined["period"] = "is"
    combined.loc[combined["entry_date"].between(oos_start_ts, oos_end_ts), "period"] = "oos"
    by_year = (
        combined.groupby(["run", "period", "year"], dropna=False)["시가총액추정"]
        .agg(trade_count="size", median_entry_mcap="median")
        .reset_index()
    )
    overall = (
        combined.groupby(["run", "period"], dropna=False)["시가총액추정"]
        .agg(trade_count="size", median_entry_mcap="median")
        .reset_index()
    )
    overall["year"] = "ALL"
    summary = pd.concat([by_year, overall], ignore_index=True)
    summary["year"] = summary["year"].astype("string")
    return summary.loc[:, columns].sort_values(["run", "period", "year"]).reset_index(drop=True)


def _exit_reason_breakdown(
    *,
    trades_by_run: dict[str, pd.DataFrame],
    split_dates: dict[str, tuple[object, object]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run_name, trades in trades_by_run.items():
        if trades.empty:
            continue
        trade_data = trades.copy()
        trade_data["entry_date"] = pd.to_datetime(trade_data["entry_date"], errors="raise")
        for period, (start, end) in split_dates.items():
            start_ts = pd.Timestamp(start).normalize()
            end_ts = pd.Timestamp(end).normalize()
            period_trades = trade_data.loc[trade_data["entry_date"].between(start_ts, end_ts)]
            total = len(period_trades)
            counts = period_trades["exit_reason"].value_counts().sort_index()
            for exit_reason, count in counts.items():
                rows.append(
                    {
                        "run": run_name,
                        "period": period,
                        "exit_reason": exit_reason,
                        "count": int(count),
                        "pct": float(count / total) if total else 0.0,
                    }
                )
    return pd.DataFrame(rows, columns=["run", "period", "exit_reason", "count", "pct"])


def _trade_set_overlap_matrix(
    *,
    trades_by_run: dict[str, pd.DataFrame],
    oos_start: object,
    oos_end: object,
) -> pd.DataFrame:
    start_ts = pd.Timestamp(oos_start).normalize()
    end_ts = pd.Timestamp(oos_end).normalize()
    trade_sets: dict[str, set[tuple[pd.Timestamp, str]]] = {}
    for run_name, trades in trades_by_run.items():
        if trades.empty:
            trade_sets[run_name] = set()
            continue
        trade_data = trades.copy()
        trade_data["entry_date"] = pd.to_datetime(trade_data["entry_date"], errors="raise")
        trade_data["종목코드"] = trade_data["종목코드"].astype("string")
        trade_data = trade_data.loc[trade_data["entry_date"].between(start_ts, end_ts)]
        trade_sets[run_name] = {
            (pd.Timestamp(entry_date).normalize(), str(ticker))
            for entry_date, ticker in zip(trade_data["entry_date"], trade_data["종목코드"], strict=False)
        }

    rows: list[dict[str, Any]] = []
    for left_name, left_set in trade_sets.items():
        for right_name, right_set in trade_sets.items():
            union_count = len(left_set | right_set)
            overlap_count = len(left_set & right_set)
            rows.append(
                {
                    "left_run": left_name,
                    "right_run": right_name,
                    "left_count": len(left_set),
                    "right_count": len(right_set),
                    "overlap_count": overlap_count,
                    "left_only_count": len(left_set - right_set),
                    "right_only_count": len(right_set - left_set),
                    "jaccard_overlap": float(overlap_count / union_count) if union_count else float("nan"),
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "left_run",
            "right_run",
            "left_count",
            "right_count",
            "overlap_count",
            "left_only_count",
            "right_only_count",
            "jaccard_overlap",
        ],
    )


def _holding_period_distribution(
    *,
    trades_by_run: dict[str, pd.DataFrame],
    oos_start: object,
    oos_end: object,
    calendar: object,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run_name, trades in trades_by_run.items():
        holding_days = _trade_holding_days(trades, oos_start, oos_end, calendar)
        total = len(holding_days)
        if total == 0:
            rows.append(
                {
                    "run": run_name,
                    "period": "oos",
                    "row_type": "summary",
                    "holding_days": "",
                    "trade_count": 0,
                    "pct": float("nan"),
                    "metric": "no_trades",
                    "value": float("nan"),
                }
            )
            continue
        counts = holding_days.value_counts().sort_index()
        for holding_day, count in counts.items():
            rows.append(
                {
                    "run": run_name,
                    "period": "oos",
                    "row_type": "histogram",
                    "holding_days": int(holding_day),
                    "trade_count": int(count),
                    "pct": float(count / total),
                    "metric": "",
                    "value": float("nan"),
                }
            )
        summary = {
            "mean": holding_days.mean(),
            "median": holding_days.median(),
            "p05": holding_days.quantile(0.05),
            "p25": holding_days.quantile(0.25),
            "p75": holding_days.quantile(0.75),
            "p95": holding_days.quantile(0.95),
        }
        for metric, value in summary.items():
            rows.append(
                {
                    "run": run_name,
                    "period": "oos",
                    "row_type": "summary",
                    "holding_days": "",
                    "trade_count": total,
                    "pct": float("nan"),
                    "metric": metric,
                    "value": float(value),
                }
            )
    return pd.DataFrame(
        rows,
        columns=["run", "period", "row_type", "holding_days", "trade_count", "pct", "metric", "value"],
    )


def _trade_holding_days(
    trades: pd.DataFrame,
    start: object,
    end: object,
    calendar: object,
) -> pd.Series:
    if trades.empty:
        return pd.Series(dtype="int64")
    dates = getattr(calendar, "dates", calendar)
    index_by_date = {pd.Timestamp(date).normalize(): index for index, date in enumerate(dates)}
    trade_data = trades.copy()
    trade_data["entry_date"] = pd.to_datetime(trade_data["entry_date"], errors="raise")
    trade_data["exit_date"] = pd.to_datetime(trade_data["exit_date"], errors="raise")
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    trade_data = trade_data.loc[trade_data["entry_date"].between(start_ts, end_ts)]
    values = [
        index_by_date[pd.Timestamp(exit_date).normalize()] - index_by_date[pd.Timestamp(entry_date).normalize()]
        for entry_date, exit_date in zip(trade_data["entry_date"], trade_data["exit_date"], strict=False)
    ]
    return pd.Series(values, dtype="int64")


def _write_ticker_safe_csv(frame: pd.DataFrame, path: Path) -> None:
    output = frame.copy()
    if "종목코드" in output.columns:
        output["종목코드"] = output["종목코드"].map(_format_ticker_code).astype("string")
    output.to_csv(path, index=False)


def _format_ticker_code(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text.zfill(6) if text.isdigit() else text


def _metadata(config: dict[str, Any], panel: pd.DataFrame, calendar: object) -> dict[str, Any]:
    return {
        "panels_used": list(config["panels"]),
        "is_start": _date_string(config["periods"]["is"]["start"]),
        "is_end": _date_string(config["periods"]["is"]["end"]),
        "oos_start": _date_string(config["periods"]["oos"]["start"]),
        "oos_end": _date_string(config["periods"]["oos"]["end"]),
        "estimate_row_policy": "headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is universally True in the Kiwoom panel and is not used as a filter; diagnostic_estimate_included reincludes the 거래대금추정여부 rows",
        "integrated_column_policy": "KRX종가 preferred; 종가 only as pre-NXT fallback; E003 price_gate_on uses kospi_proxy_5d_return from dynamic-Top100 traded-value-weighted returns, not an official KOSPI close",
        "signal_exit_policy": _signal_exit_policy(config),
        "calendar_source": "derived from panel non-null KRX종가 rows",
        "krx_close_derivation_summary": {
            key: int(value) for key, value in panel["krx_close_source"].value_counts().sort_index().items()
        },
        "n_tickers": int(panel["종목코드"].nunique()),
        "n_trading_days": int(len(calendar.dates)),
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(_jsonable(data), ensure_ascii=False, allow_nan=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _signal_exit_policy(config: dict[str, Any]) -> str:
    if config.get("experiment_id") not in {"B002", "B003"}:
        return ""
    return "Signal-reversal exits at next trading-day open when fnv_5 <= 0 or inv_5 <= 0; NaN or missing signal components during hold are treated as <= 0 for conservative exit"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_jsonable(inner) for inner in value]
    if isinstance(value, tuple):
        return [_jsonable(inner) for inner in value]
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def _date_string(value: Any) -> str:
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


if __name__ == "__main__":
    main()
