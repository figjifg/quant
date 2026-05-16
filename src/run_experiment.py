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
from src.features.macro_regime import build_macro_regime_daily, monthly_regime_log, quarterly_regime_log
from src.features.regime import regime_gate_on, regime_state_log
from src.reporting.metrics import compute_metrics, metrics_is_oos
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
from src.strategies.b006_t3_promote import VARIANTS as B006_VARIANTS, run_b006_variants
from src.strategies.b007_filter_exploration import (
    FILTER_CANDIDATES as B007_FILTER_CANDIDATES,
    VARIANTS as B007_VARIANTS,
    run_b007_variants,
)
from src.strategies.b008_f2_promote import VARIANTS as B008_VARIANTS, run_b008_variants
from src.strategies.b009_f3_promote import VARIANTS as B009_VARIANTS, run_b009_variants
from src.strategies.b010_old_data_verification import VARIANTS as B010_VARIANTS, run_b010_variants
from src.strategies.b011_gate_only_full_timeline import VARIANTS as B011_VARIANTS, run_b011_variants
from src.strategies.c003_monthly_macro_gate import (
    VARIANTS as C003_VARIANTS,
    monthly_execution_dates,
    run_c003_variants,
    run_monthly_mcap_backtest,
)
from src.strategies.c004_quarterly_macro_gate import (
    VARIANTS as C004_VARIANTS,
    quarterly_execution_dates,
    run_c004_variants,
    run_quarterly_mcap_backtest,
)
from src.strategies.c005_quarterly_macro_v4 import VARIANTS as C005_VARIANTS, run_c005_variants
from src.strategies.c006_quarterly_macro_v5 import VARIANTS as C006_VARIANTS, run_c006_variants
from src.strategies.c007_top20_mcap import VARIANTS as C007_VARIANTS, run_c007_variants
from src.strategies.c008_quarterly_macro_v6 import VARIANTS as C008_VARIANTS, run_c008_variants
from src.strategies.c010_quarterly_macro_v7 import VARIANTS as C010_VARIANTS, run_c010_variants
from src.strategies.c011_quarterly_macro_v8 import VARIANTS as C011_VARIANTS, run_c011_variants
from src.strategies.c012_quarterly_macro_v9 import VARIANTS as C012_VARIANTS, run_c012_variants
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
EXPECTED_B006_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "filter",
    "ranking",
    "exit",
    "variants",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B007_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "trigger",
    "ranking",
    "exit",
    "filter",
    "relative",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B008_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "trigger",
    "ranking",
    "exit",
    "variants",
    "relative",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B009_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "universe",
    "strategy",
    "trigger",
    "ranking",
    "exit",
    "variants",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B010_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "periods",
    "excluded_years",
    "candidate_years",
    "survival_comparison",
    "universe",
    "strategy",
    "trigger",
    "ranking",
    "exit",
    "variants",
    "costs",
    "cost_sensitivity_multipliers",
    "output_dir",
)
EXPECTED_B011_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "panel_date_filters",
    "market_breadth_csv",
    "period",
    "universe",
    "regime",
    "selection",
    "costs",
    "variants",
    "output_dir",
)
EXPECTED_C003_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "panel_date_filters",
    "market_breadth_csv",
    "macro_data_dir",
    "period",
    "universe",
    "regime",
    "selection",
    "costs",
    "rebalance",
    "variants",
    "output_dir",
)
EXPECTED_C004_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C005_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C006_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C007_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C008_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C010_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C011_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C012_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_B010_SURVIVAL_KEYS = ("b009_metrics_path",)
EXPECTED_B011_PERIOD_KEYS = ("start", "end", "exclude_calendar_years")
EXPECTED_B011_SELECTION_KEYS = ("type", "n")
EXPECTED_C003_REGIME_KEYS = ("macro_signals", "composite_rule", "on_threshold")
EXPECTED_C003_REBALANCE_KEYS = ("frequency", "anchor")
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
EXPECTED_B006_ROLE_KEYS = ("type",)
EXPECTED_B007_FILTER_KEYS = ("candidates",)
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
    elif experiment_id == "B006":
        _validate_b006_config_shape(config)
        run_b006_experiment(config, config_path)
    elif experiment_id == "B007":
        _validate_b007_config_shape(config)
        run_b007_experiment(config, config_path)
    elif experiment_id == "B008":
        _validate_b008_config_shape(config)
        run_b008_experiment(config, config_path)
    elif experiment_id == "B009":
        _validate_b009_config_shape(config)
        run_b009_experiment(config, config_path)
    elif experiment_id == "B010":
        _validate_b010_config_shape(config)
        run_b010_experiment(config, config_path)
    elif experiment_id == "B011":
        _validate_b011_config_shape(config)
        run_b011_experiment(config, config_path)
    elif experiment_id == "C003":
        _validate_c003_config_shape(config)
        run_c003_experiment(config, config_path)
    elif experiment_id == "C004":
        _validate_c004_config_shape(config)
        run_c004_experiment(config, config_path)
    elif experiment_id == "C005":
        _validate_c005_config_shape(config)
        run_c005_experiment(config, config_path)
    elif experiment_id == "C006":
        _validate_c006_config_shape(config)
        run_c006_experiment(config, config_path)
    elif experiment_id == "C007":
        _validate_c007_config_shape(config)
        run_c007_experiment(config, config_path)
    elif experiment_id == "C008":
        _validate_c008_config_shape(config)
        run_c008_experiment(config, config_path)
    elif experiment_id == "C010":
        _validate_c010_config_shape(config)
        run_c010_experiment(config, config_path)
    elif experiment_id == "C011":
        _validate_c011_config_shape(config)
        run_c011_experiment(config, config_path)
    elif experiment_id == "C012":
        _validate_c012_config_shape(config)
        run_c012_experiment(config, config_path)
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


def run_b006_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, exit_kwargs = run_b006_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=headline_universe,
        costs=costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
    )
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b006_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            features=features,
            universe=headline_universe,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
        )
    )
    year_breakdown = _b006_year_breakdown(runs=runs, calendar=calendar, start=is_start, end=oos_end)
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=candidates["t3_acceleration"],
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=exit_kwargs["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "variant", "t3_acceleration")

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b006_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b006_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b006_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "t3_promote_year_breakdown.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b006_report(output_dir, config, metrics, year_breakdown, cost_sensitivity)


def run_b007_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    min_count = int(config["relative"]["cross_sectional_min_count"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, exit_kwargs, _relative_features = run_b007_variants(
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
        _b007_cost_0_metrics(
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
    year_breakdown = _b007_year_breakdown(runs=runs, calendar=calendar, start=is_start, end=oos_end)
    overlap_matrix = _b007_trade_overlap_matrix(runs)
    best_variant = max(B007_VARIANTS, key=lambda variant: metrics[variant]["oos"]["total_return"])
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
        signal_exit_features=exit_kwargs["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "variant", best_variant)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b007_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b007_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b007_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "filter_exploration_year_breakdown.csv", index=False)
    overlap_matrix.to_csv(output_dir / "filter_overlap_matrix.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b007_report(output_dir, config, metrics, year_breakdown, overlap_matrix, cost_sensitivity)


def run_b008_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    min_count = int(config["relative"]["cross_sectional_min_count"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, exit_kwargs, _relative_features = run_b008_variants(
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
        _b008_cost_0_metrics(
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
    year_breakdown = _b008_year_breakdown(runs=runs, calendar=calendar, start=is_start, end=oos_end)
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=candidates["f2_promote"],
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=exit_kwargs["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "variant", "f2_promote")

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b008_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b008_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b008_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "f2_promote_year_breakdown.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b008_report(output_dir, config, metrics, year_breakdown, cost_sensitivity)


def run_b009_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe, _diagnostic_universe = _build_common_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    max_positions = int(config["strategy"]["max_positions"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, exit_kwargs = run_b009_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=headline_universe,
        costs=costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
    )
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b009_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            features=features,
            universe=headline_universe,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
        )
    )
    year_breakdown = _b009_year_breakdown(runs=runs, calendar=calendar, start=is_start, end=oos_end)
    cost_sensitivity = _run_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        candidates=candidates["f3_promote"],
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
        holding=5,
        signal_exit_features=exit_kwargs["signal_exit_features"],
    )
    cost_sensitivity.insert(0, "variant", "f3_promote")

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b009_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b009_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b009_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "f3_promote_year_breakdown.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b009_report(output_dir, config, metrics, year_breakdown, cost_sensitivity)


def run_b010_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, features, headline_universe = _build_b010_inputs(config)
    periods = config["periods"]
    is_start = periods["is"]["start"]
    is_end = periods["is"]["end"]
    oos_start = periods["oos"]["start"]
    oos_end = periods["oos"]["end"]
    segments = ((is_start, is_end), (oos_start, oos_end))
    max_positions = int(config["strategy"]["max_positions"])
    costs = _costs_from_config(config["costs"])

    runs, candidates, _exit_kwargs = run_b010_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=headline_universe,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    metrics = _metrics_for_runs(runs, is_start, is_end, oos_start, oos_end, calendar)
    metrics.update(
        _b010_cost_0_metrics(
            panel=panel,
            calendar=calendar,
            features=features,
            universe=headline_universe,
            segments=segments,
            is_start=is_start,
            is_end=is_end,
            oos_start=oos_start,
            oos_end=oos_end,
            max_positions=max_positions,
        )
    )
    year_breakdown = _b010_year_breakdown(
        runs=runs,
        calendar=calendar,
        candidate_years=tuple(int(year) for year in config["candidate_years"]),
    )
    diagnostic = _b010_verification_diagnostic(config, metrics, year_breakdown)
    cost_sensitivity = _b010_cost_sensitivity(
        panel=panel,
        calendar=calendar,
        features=features,
        universe=headline_universe,
        base_costs=costs,
        multipliers=config["cost_sensitivity_multipliers"],
        segments=segments,
        is_start=is_start,
        is_end=is_end,
        oos_start=oos_start,
        oos_end=oos_end,
        max_positions=max_positions,
    )

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b010_combined_trades(runs), output_dir / "trades.csv")
    _write_ticker_safe_csv(_b010_combined_signals(candidates, runs), output_dir / "signals.csv")
    _b010_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "old_data_year_breakdown.csv", index=False)
    diagnostic.to_csv(output_dir / "verification_diagnostic.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
    _write_b010_report(output_dir, config, metrics, year_breakdown, diagnostic, cost_sensitivity)


def run_b011_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    kospi_proxy = load_kospi_proxy(config["market_breadth_csv"], window=int(config["regime"]["window"]))
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates, gate = run_b011_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        kospi_proxy=kospi_proxy,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _b011_metrics(runs, calendar, candidate_years)
    year_breakdown = _b011_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    drawdown = _b011_drawdown(runs)
    summary = _b011_summary(metrics, year_breakdown)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["gate_only_mcap"], calendar), output_dir / "trades.csv")
    _b011_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "gate_only_year_breakdown.csv", index=False)
    drawdown.to_csv(output_dir / "gate_only_drawdown.csv", index=False)
    summary.to_csv(output_dir / "gate_only_summary.csv", index=False)
    _write_b011_report(output_dir, config, metrics, year_breakdown, summary, gate)


def run_c003_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
    )
    monthly_log = monthly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c003_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        monthly_regime=monthly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c003_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        monthly_regime=monthly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c003_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c003_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _c003_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "monthly_year_breakdown.csv", index=False)
    monthly_log.to_csv(output_dir / "monthly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c003_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c004_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c004_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c004_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c004_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c004_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _c004_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c004_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c005_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c005_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c005_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c005_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c005_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _c005_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c005_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c006_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c006_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c006_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c006_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c006_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _c006_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c006_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c007_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c007_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c007_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c007_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c007_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _c007_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c007_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c008_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c008_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics = _c008_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c008_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    verdict = _c008_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c008_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c008_report(output_dir, config, metrics, year_breakdown, verdict)


def run_c010_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c010_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics, cost_0_result = _c010_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c010_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c010_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c010_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c010_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c011_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c011_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics, cost_0_result = _c011_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c011_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c011_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c011_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c011_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c012_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=int(config["regime"]["on_threshold"]),
        macro_signals=tuple(config["regime"]["macro_signals"]),
    )
    quarterly_log = quarterly_regime_log(daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_c012_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        quarterly_regime=quarterly_log,
        market_breadth=market_breadth,
        costs=costs,
        segments=segments,
        max_positions=max_positions,
    )
    candidate_years = _b011_candidate_years(config)
    metrics, cost_0_result = _c012_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c012_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c012_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c012_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c012_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


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


def _build_b010_inputs(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, object, pd.DataFrame, pd.DataFrame]:
    panel = load_equity_panel(config["panels"])
    excluded_years = {int(year) for year in config["excluded_years"]}
    if excluded_years:
        panel = panel.loc[~panel["날짜"].dt.year.isin(excluded_years)].copy()
    calendar = derive_trading_calendar(panel)
    features = build_flow_ratios(panel, calendar)
    universe = build_execution_universe(
        panel,
        calendar,
        min_avg_traded_value_20d=float(config["universe"]["min_avg_traded_value_20d"]),
        exclude_estimated_flag_rows=bool(config["universe"]["exclude_estimated_flag_rows"]),
    )
    candidate_years = {int(year) for year in config["candidate_years"]}
    features = _filter_signal_execution_years(features, candidate_years)
    universe = _filter_signal_execution_years(universe, candidate_years)
    return panel, calendar, features, universe


def _build_b011_inputs(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, object, pd.DataFrame]:
    frames = []
    filters = config.get("panel_date_filters", {})
    for path in config["panels"]:
        frame = load_equity_panel([path])
        date_filter = filters.get(path, {})
        if "start" in date_filter:
            frame = frame.loc[frame["날짜"].ge(pd.Timestamp(date_filter["start"]).normalize())].copy()
        if "end" in date_filter:
            frame = frame.loc[frame["날짜"].le(pd.Timestamp(date_filter["end"]).normalize())].copy()
        frames.append(frame)
    panel = pd.concat(frames, ignore_index=True)
    excluded_years = {int(year) for year in config["period"]["exclude_calendar_years"]}
    if excluded_years:
        panel = panel.loc[~panel["날짜"].dt.year.isin(excluded_years)].copy()
    start = pd.Timestamp(config["period"]["start"]).normalize()
    end = pd.Timestamp(config["period"]["end"]).normalize()
    panel = panel.loc[panel["날짜"].between(start, end)].copy()
    calendar = derive_trading_calendar(panel)
    universe = build_execution_universe(
        panel,
        calendar,
        min_avg_traded_value_20d=float(config["universe"]["min_avg_traded_value_20d"]),
        exclude_estimated_flag_rows=bool(config["universe"]["exclude_estimated_flag_rows"]),
    )
    years = set(_b011_candidate_years(config))
    universe = _filter_signal_execution_years(universe, years)
    return panel, calendar, universe


def _filter_signal_execution_years(frame: pd.DataFrame, years: set[int]) -> pd.DataFrame:
    signal_dates = pd.to_datetime(frame["signal_date"], errors="raise")
    execution_dates = pd.to_datetime(frame["execution_date"], errors="raise")
    signal_year = signal_dates.dt.year
    execution_year = execution_dates.dt.year
    adjacent_execution = (execution_dates - signal_dates).dt.days.le(10)
    return frame.loc[signal_year.isin(years) & execution_year.isin(years) & adjacent_execution].copy()


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


def _b006_cost_0_metrics(
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
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    runs, _, _ = run_b006_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=zero_costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
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


def _b006_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B006_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b006_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B006_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b006_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["t1_baseline"].equity_curve["date"]})
    output["t1_baseline_value"] = runs["t1_baseline"].equity_curve["net_value"].to_numpy()
    output["t3_acceleration_value"] = runs["t3_acceleration"].equity_curve["net_value"].to_numpy()
    return output


def _b006_year_breakdown(
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
            "period": "is" if year <= 2022 else "oos",
        }
        for variant in B006_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["t3_minus_t1_net_total_return"] = (
            row["t3_acceleration_net_total_return"] - row["t1_baseline_net_total_return"]
        )
        row["t3_wins"] = bool(row["t3_minus_t1_net_total_return"] > 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def _write_b006_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B006 Metrics Summary", ""]
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
            "| filter | filter_flow_sign_both_positive |",
            "| trigger_baseline | trigger_immediate |",
            "| trigger_candidate | trigger_acceleration |",
            "| ranking | rank_by_combined_flow_5 |",
            "| exit | exit_signal_reversal |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            "",
        ]
    )
    lines.extend(_b006_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b006_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("T3 Promote Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b006_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B006_VARIANTS:
        block = metrics[variant][split]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    for variant in B006_VARIANTS:
        block = metrics[f"cost_0_{variant}"][split]
        lines.append(
            "| cost_0_"
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    lines.append("")
    return lines


def _b007_cost_0_metrics(
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
    runs, _, _, _ = run_b007_variants(
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


def _b007_variant_label(variant: str) -> str:
    return {
        "f1_baseline": "F1",
        "f2_relative_and_absolute": "F2",
        "f3_persistence_4_of_5": "F3",
    }[variant]


def _b007_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B007_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", _b007_variant_label(variant))
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b007_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B007_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", _b007_variant_label(variant))
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b007_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["f1_baseline"].equity_curve["date"]})
    for variant in B007_VARIANTS:
        output[f"{_b007_variant_label(variant)}_value"] = runs[variant].equity_curve["net_value"].to_numpy()
    return output


def _b007_year_breakdown(
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
            "period": "is" if year <= 2022 else "oos",
            "is_v_recovery_diagnostic_2020": year == 2020,
            "oos_spike_capture_diagnostic_2025": year == 2025,
        }
        for variant in B007_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["f2_minus_f1_net_total_return"] = (
            row["f2_relative_and_absolute_net_total_return"] - row["f1_baseline_net_total_return"]
        )
        row["f3_minus_f1_net_total_return"] = (
            row["f3_persistence_4_of_5_net_total_return"] - row["f1_baseline_net_total_return"]
        )
        row["f2_wins_f1"] = bool(row["f2_minus_f1_net_total_return"] > 0.0)
        row["f3_wins_f1"] = bool(row["f3_minus_f1_net_total_return"] > 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def _b007_trade_overlap_matrix(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    trade_sets = {variant: _entry_ticker_set(runs[variant].trades) for variant in B007_VARIANTS}
    rows = []
    for left in B007_VARIANTS:
        row: dict[str, Any] = {"variant": _b007_variant_label(left)}
        for right in B007_VARIANTS:
            union = trade_sets[left].union(trade_sets[right])
            row[_b007_variant_label(right)] = 1.0 if not union else len(trade_sets[left].intersection(trade_sets[right])) / len(union)
        rows.append(row)
    return pd.DataFrame(rows)


def _write_b007_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    overlap_matrix: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B007 Metrics Summary", ""]
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
            "| filter_candidates | F1 flow_sign_both_positive; F2 relative_AND_absolute_positive; F3 persistence_4_of_5 |",
            "| trigger | trigger_acceleration |",
            "| ranking | rank_by_combined_flow_5 |",
            "| exit | exit_signal_reversal on absolute fnv_5/inv_5 |",
            "| relative_feature_policy | median-difference relative flow, cross-sectional moments by signal_date over eligible execution universe |",
            "| persistence_policy | per-ticker right-labeled rolling 5-row count of combined_flow_1 > 0 using signal dates through T only |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            "",
        ]
    )
    lines.extend(_b007_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b007_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("Filter Exploration Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Trade-Set Overlap", overlap_matrix))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b007_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B007_VARIANTS:
        block = metrics[variant][split]
        lines.append(
            "| "
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    for variant in B007_VARIANTS:
        block = metrics[f"cost_0_{variant}"][split]
        lines.append(
            "| cost_0_"
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    lines.append("")
    return lines


def _b008_cost_0_metrics(
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
    runs, _, _, _ = run_b008_variants(
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


def _b008_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B008_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b008_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B008_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b008_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["f1_baseline"].equity_curve["date"]})
    output["f1_baseline_value"] = runs["f1_baseline"].equity_curve["net_value"].to_numpy()
    output["f2_promote_value"] = runs["f2_promote"].equity_curve["net_value"].to_numpy()
    return output


def _b008_year_breakdown(
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
            "period": "is" if year <= 2022 else "oos",
        }
        for variant in B008_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["f2_minus_f1_net_total_return"] = row["f2_promote_net_total_return"] - row["f1_baseline_net_total_return"]
        row["f2_wins_f1"] = bool(row["f2_minus_f1_net_total_return"] > 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def _write_b008_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B008 Metrics Summary", ""]
    oos_rows = year_breakdown.loc[year_breakdown["period"].eq("oos")]
    oos_year_wins = int(oos_rows["f2_wins_f1"].sum())
    oos_delta_ex_2025 = float(
        oos_rows.loc[oos_rows["year"].isin([2023, 2024, 2026]), "f2_minus_f1_net_total_return"].sum()
    )
    delta_2025 = float(oos_rows.loc[oos_rows["year"].eq(2025), "f2_minus_f1_net_total_return"].sum())
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
            "| filter_baseline | filter_flow_sign_both_positive |",
            "| filter_candidate | filter_relative_AND_absolute_positive |",
            "| trigger | trigger_acceleration |",
            "| ranking | rank_by_combined_flow_5 |",
            "| exit | exit_signal_reversal on absolute fnv_5/inv_5 |",
            "| relative_feature_policy | median-difference relative flow, cross-sectional moments by signal_date over eligible execution universe |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            f"| oos_year_wins_f2_gt_f1 | {oos_year_wins} of 4 |",
            f"| oos_delta_excluding_2025 | {_format_report_value(oos_delta_ex_2025)} |",
            f"| oos_delta_2025 | {_format_report_value(delta_2025)} |",
            "",
        ]
    )
    lines.extend(_b008_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b008_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("F2 Promote Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b008_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B008_VARIANTS:
        block = metrics[variant][split]
        lines.append(
            "| "
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    for variant in B008_VARIANTS:
        block = metrics[f"cost_0_{variant}"][split]
        lines.append(
            "| cost_0_"
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    lines.append("")
    return lines


def _b009_cost_0_metrics(
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
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    runs, _, _ = run_b009_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=zero_costs,
        period_start=is_start,
        period_end=oos_end,
        max_positions=max_positions,
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


def _b009_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B009_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b009_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B009_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b009_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["f1_baseline"].equity_curve["date"]})
    output["f1_baseline_value"] = runs["f1_baseline"].equity_curve["net_value"].to_numpy()
    output["f3_promote_value"] = runs["f3_promote"].equity_curve["net_value"].to_numpy()
    return output


def _b009_year_breakdown(
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
            "period": "is" if year <= 2022 else "oos",
        }
        for variant in B009_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
        row["f3_minus_f1_net_total_return"] = row["f3_promote_net_total_return"] - row["f1_baseline_net_total_return"]
        row["f3_wins_f1"] = bool(row["f3_minus_f1_net_total_return"] > 0.0)
        rows.append(row)
    return pd.DataFrame(rows)


def _write_b009_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B009 Metrics Summary", ""]
    oos_rows = year_breakdown.loc[year_breakdown["period"].eq("oos")]
    oos_year_wins = int(oos_rows["f3_wins_f1"].sum())
    oos_delta_ex_2025 = float(
        oos_rows.loc[oos_rows["year"].isin([2023, 2024, 2026]), "f3_minus_f1_net_total_return"].sum()
    )
    delta_2025 = float(oos_rows.loc[oos_rows["year"].eq(2025), "f3_minus_f1_net_total_return"].sum())
    oos_delta_ex_2025_2026 = float(
        oos_rows.loc[oos_rows["year"].isin([2023, 2024]), "f3_minus_f1_net_total_return"].sum()
    )
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
            "| filter_baseline | filter_flow_sign_both_positive |",
            "| filter_candidate | filter_persistence_4_of_5 |",
            "| trigger | trigger_acceleration |",
            "| ranking | rank_by_combined_flow_5 |",
            "| exit | exit_signal_reversal on absolute fnv_5/inv_5 |",
            "| persistence_policy | per-ticker right-labeled rolling 5-row count of combined_flow_1 > 0 using signal dates through T only |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |",
            "| calendar_source | derived from panel non-null KRX종가 rows |",
            f"| oos_year_wins_f3_gt_f1 | {oos_year_wins} of 4 |",
            f"| oos_delta_excluding_2025 | {_format_report_value(oos_delta_ex_2025)} |",
            f"| oos_delta_2025 | {_format_report_value(delta_2025)} |",
            f"| oos_delta_excluding_2025_and_2026 | {_format_report_value(oos_delta_ex_2025_2026)} |",
            "",
        ]
    )
    lines.extend(_b009_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b009_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b004_dataframe_table("F3 Promote Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b009_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B009_VARIANTS:
        block = metrics[variant][split]
        lines.append(
            "| "
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    for variant in B009_VARIANTS:
        block = metrics[f"cost_0_{variant}"][split]
        lines.append(
            "| cost_0_"
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    lines.append("")
    return lines


def _b010_cost_0_metrics(
    *,
    panel: pd.DataFrame,
    calendar: object,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    max_positions: int,
) -> dict[str, dict[str, dict[str, float | int]]]:
    zero_costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)
    runs, _, _ = run_b010_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=zero_costs,
        segments=segments,
        max_positions=max_positions,
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


def _b010_cost_sensitivity(
    *,
    panel: pd.DataFrame,
    calendar: object,
    features: pd.DataFrame,
    universe: pd.DataFrame,
    base_costs: Costs,
    multipliers: list[float],
    segments: tuple[tuple[object, object], ...],
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
        runs, _, _ = run_b010_variants(
            panel=panel,
            calendar=calendar,
            flow_features=features,
            universe=universe,
            costs=scaled_costs,
            segments=segments,
            max_positions=max_positions,
        )
        metric_block = metrics_is_oos(
            runs["carrier_t3_f3"].equity_curve,
            runs["carrier_t3_f3"].trades,
            is_start,
            is_end,
            oos_start,
            oos_end,
            calendar,
        )
        rows.append(
            {
                "variant": "carrier_t3_f3",
                "multiplier": float(multiplier),
                "is_total_return": metric_block["is"]["total_return"],
                "oos_total_return": metric_block["oos"]["total_return"],
                "full_total_return": metric_block["full"]["total_return"],
                "cost_paid_total": metric_block["full"]["cost_paid_total"],
            }
        )
    return pd.DataFrame(rows)


def _b010_combined_trades(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    frames = []
    for variant in B010_VARIANTS:
        trades = runs[variant].trades.copy()
        trades.insert(0, "variant", variant)
        frames.append(trades)
    return pd.concat(frames, ignore_index=True)


def _b010_combined_signals(
    candidates: dict[str, pd.DataFrame],
    runs: dict[str, BacktestResult],
) -> pd.DataFrame:
    frames = []
    for variant in B010_VARIANTS:
        signals = _signals_frame(candidates[variant], include_signal_value=True)
        signals.insert(0, "variant", variant)
        signals["included_in_trade"] = _signal_included_in_trade(signals, runs[variant].trades)
        frames.append(signals)
    return pd.concat(frames, ignore_index=True)


def _b010_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    output = pd.DataFrame({"date": runs["carrier_t3_f3"].equity_curve["date"]})
    for variant in B010_VARIANTS:
        output[f"{variant}_value"] = runs[variant].equity_curve["net_value"].to_numpy()
    return output


def _b010_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    rows = []
    for year in candidate_years:
        year_start = pd.Timestamp(year=year, month=1, day=1)
        year_end = pd.Timestamp(year=year, month=12, day=31)
        row: dict[str, Any] = {"year": year}
        for variant in B010_VARIANTS:
            row[f"{variant}_net_total_return"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["total_return"]
            row[f"{variant}_hit_rate"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["hit_rate"]
            row[f"{variant}_trade_count"] = metrics_is_oos(
                runs[variant].equity_curve,
                runs[variant].trades,
                year_start,
                year_end,
                year_start,
                year_end,
                calendar,
            )["is"]["trade_count"]
        row["v1_minus_v2_net_total_return"] = (
            row["carrier_t3_f3_net_total_return"] - row["t3_f1_baseline_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _b010_verification_diagnostic(
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
) -> pd.DataFrame:
    v1_year_returns = pd.to_numeric(year_breakdown["carrier_t3_f3_net_total_return"], errors="raise")
    positive_years = int(v1_year_returns.gt(0.0).sum())
    positive_returns = v1_year_returns.loc[v1_year_returns.gt(0.0)]
    total_positive = float(positive_returns.sum())
    h4_fraction = float(positive_returns.max() / total_positive) if total_positive > 0.0 else float("nan")
    v1_full = metrics["carrier_t3_f3"]["full"]["total_return"]
    v1_cost_0_full = metrics["cost_0_carrier_t3_f3"]["full"]["total_return"]
    v2_full = metrics["t3_f1_baseline"]["full"]["total_return"]
    b009_cost_0_oos = _b010_b009_cost_0_oos(config)
    rows = [
        {"diagnostic": "h1_v1_cost_0_net_gt_0", "value": v1_cost_0_full, "threshold": 0.0, "passes": bool(v1_cost_0_full > 0.0)},
        {"diagnostic": "h2_v1_net_total_return_ge_-0.20", "value": v1_full, "threshold": -0.20, "passes": bool(v1_full >= -0.20)},
        {"diagnostic": "h3_v1_positive_years_ge_4_of_7", "value": positive_years, "threshold": 4, "passes": bool(positive_years >= 4)},
        {"diagnostic": "h4_largest_positive_year_fraction_le_80pct", "value": h4_fraction, "threshold": 0.80, "passes": bool(h4_fraction <= 0.80) if total_positive > 0.0 else False},
        {"diagnostic": "h4_total_positive_year_return", "value": total_positive, "threshold": "", "passes": ""},
        {"diagnostic": "h5_v1_minus_v2_net_total_return", "value": float(v1_full - v2_full), "threshold": "", "passes": ""},
        {"diagnostic": "survival_2010_2017_v1_cost_0_full", "value": v1_cost_0_full, "threshold": "", "passes": ""},
        {"diagnostic": "survival_2018_2026_v1_cost_0_oos_from_b009", "value": b009_cost_0_oos, "threshold": "", "passes": ""},
    ]
    return pd.DataFrame(rows)


def _b010_b009_cost_0_oos(config: dict[str, Any]) -> float:
    path = Path(config["survival_comparison"]["b009_metrics_path"])
    metrics = json.loads(path.read_text(encoding="utf-8"))
    return float(metrics["cost_0_f3_promote"]["oos"]["total_return"])


def _write_b010_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, Any],
    year_breakdown: pd.DataFrame,
    diagnostic: pd.DataFrame,
    cost_sensitivity: pd.DataFrame,
) -> None:
    lines = ["# B010 Metrics Summary", ""]
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
            f"| excluded_years | {json.dumps(config['excluded_years'])} |",
            f"| candidate_years | {json.dumps(config['candidate_years'])} |",
            "| filter_candidate | filter_persistence_4_of_5 |",
            "| filter_baseline | filter_flow_sign_both_positive |",
            "| trigger | trigger_acceleration |",
            "| ranking | rank_by_combined_flow_5 |",
            "| exit | exit_signal_reversal on absolute fnv_5/inv_5 |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b010_variant_metric_table("IS Variant Metrics", metrics, "is"))
    lines.extend(_b010_variant_metric_table("OOS Variant Metrics", metrics, "oos"))
    lines.extend(_b010_variant_metric_table("Full Verification Metrics", metrics, "full"))
    lines.extend(_b004_dataframe_table("Old Data Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verification Diagnostic", diagnostic))
    lines.extend(_b004_dataframe_table("Cost Sensitivity", cost_sensitivity))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _b010_variant_metric_table(title: str, metrics: dict[str, Any], split: str) -> list[str]:
    columns = ("total_return", "hit_rate", "trade_count", "return_before_cost")
    lines = [
        f"## {title}",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B010_VARIANTS:
        block = metrics[variant][split]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    for variant in B010_VARIANTS:
        block = metrics[f"cost_0_{variant}"][split]
        lines.append(
            "| cost_0_"
            + variant
            + " | "
            + " | ".join(_format_report_value(block[column]) for column in columns)
            + " |"
        )
    lines.append("")
    return lines


def _b011_segments(config: dict[str, Any]) -> tuple[tuple[pd.Timestamp, pd.Timestamp], ...]:
    start = pd.Timestamp(config["period"]["start"]).normalize()
    end = pd.Timestamp(config["period"]["end"]).normalize()
    excluded_years = {int(year) for year in config["period"]["exclude_calendar_years"]}
    segments: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    segment_start = start
    for year in range(start.year, end.year + 1):
        if year not in excluded_years:
            continue
        segment_end = min(pd.Timestamp(year=year - 1, month=12, day=31), end)
        if segment_start <= segment_end:
            segments.append((segment_start, segment_end))
        segment_start = max(pd.Timestamp(year=year + 1, month=1, day=1), start)
    if segment_start <= end:
        segments.append((segment_start, end))
    return tuple(segments)


def _b011_candidate_years(config: dict[str, Any]) -> tuple[int, ...]:
    start_year = pd.Timestamp(config["period"]["start"]).year
    end_year = pd.Timestamp(config["period"]["end"]).year
    excluded = {int(year) for year in config["period"]["exclude_calendar_years"]}
    return tuple(year for year in range(start_year, end_year + 1) if year not in excluded)


def _b011_metrics(
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in B011_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block
    return metrics


def _b011_year_returns(
    result: BacktestResult,
    calendar: object,
    candidate_years: tuple[int, ...],
) -> dict[int, float]:
    yearly: dict[int, float] = {}
    for year in candidate_years:
        year_start = pd.Timestamp(year=year, month=1, day=1)
        year_end = pd.Timestamp(year=year, month=12, day=31)
        yearly[year] = metrics_is_oos(
            result.equity_curve,
            result.trades,
            year_start,
            year_end,
            year_start,
            year_end,
            calendar,
        )["is"]["total_return"]
    return yearly


def _b011_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in B011_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        rows.append(row)
    return pd.DataFrame(rows)


def _b011_drawdown(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    base = pd.DataFrame({"date": runs["gate_only_mcap"].equity_curve["date"]})
    for variant in ("gate_only_mcap", "kospi_buy_and_hold"):
        nav = pd.to_numeric(runs[variant].equity_curve["net_value"], errors="raise")
        base[f"{variant}_drawdown"] = (nav / nav.cummax() - 1.0).to_numpy()
    return base


def _b011_summary(metrics: dict[str, dict[str, Any]], year_breakdown: pd.DataFrame) -> pd.DataFrame:
    v1 = metrics["gate_only_mcap"]
    v2 = metrics["kospi_buy_and_hold"]
    v1_return = float(v1["cumulative_net_total_return"])
    v2_return = float(v2["cumulative_net_total_return"])
    v1_mdd = float(v1["max_drawdown"])
    v2_mdd = float(v2["max_drawdown"])
    v1_positive_years = int(v1["positive_years"])
    yearly = v1["yearly_net_total_return"]
    h3 = all(float(yearly[str(year)]) > 0.0 for year in (2010, 2025, 2026))
    row = {
        "h1_cumulative_survival_pass": bool(v1_return > 0.0),
        "h1_v1_cumulative_net_total_return": v1_return,
        "h2_vs_kospi_pass": bool(v1_return >= v2_return - 0.10),
        "h2_v1_minus_v2_cumulative_delta": v1_return - v2_return,
        "h3_spike_capture_pass": bool(h3),
        "h3_v1_2010_net": float(yearly["2010"]),
        "h3_v1_2025_net": float(yearly["2025"]),
        "h3_v1_2026_net": float(yearly["2026"]),
        "h4_drawdown_protection_pass": bool(v1_mdd < v2_mdd - 0.05),
        "h4_v1_max_drawdown": v1_mdd,
        "h4_v2_max_drawdown": v2_mdd,
        "h5_positive_years_pass": bool(v1_positive_years >= 8),
        "h5_v1_positive_years": v1_positive_years,
        "candidate_year_count": int(len(year_breakdown)),
    }
    row["hypotheses_passed"] = int(
        sum(
            bool(row[column])
            for column in (
                "h1_cumulative_survival_pass",
                "h2_vs_kospi_pass",
                "h3_spike_capture_pass",
                "h4_drawdown_protection_pass",
                "h5_positive_years_pass",
            )
        )
    )
    return pd.DataFrame([row])


def _b011_trades(result: BacktestResult, calendar: object) -> pd.DataFrame:
    trades = result.trades.copy()
    if trades.empty:
        trades["cost_paid"] = pd.Series(dtype="float64")
        trades["holding_days"] = pd.Series(dtype="int64")
        return trades
    trades["cost_paid"] = pd.to_numeric(trades["buy_cost"], errors="raise") + pd.to_numeric(
        trades["sell_cost"], errors="raise"
    )
    index_by_date = {pd.Timestamp(date).normalize(): index for index, date in enumerate(calendar.dates)}
    trades["holding_days"] = [
        index_by_date[pd.Timestamp(exit_date).normalize()] - index_by_date[pd.Timestamp(entry_date).normalize()]
        for entry_date, exit_date in zip(trades["entry_date"], trades["exit_date"], strict=False)
    ]
    return trades


def _b011_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["gate_only_mcap"].equity_curve["date"],
            "V1_value": runs["gate_only_mcap"].equity_curve["net_value"],
            "V2_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c003_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    monthly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C003_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _c003_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_monthly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=monthly_execution_dates(calendar, monthly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(monthly_regime["regime_on"].mean()) if not monthly_regime.empty else float("nan")
    complete_months = monthly_regime.loc[monthly_regime["regime_score"].notna()]
    v1["regime_on_share_complete_months"] = (
        float(complete_months["regime_on"].mean()) if not complete_months.empty else float("nan")
    )
    return metrics


def _c003_year_returns(
    result: BacktestResult,
    calendar: object,
    candidate_years: tuple[int, ...],
) -> dict[int, float]:
    return _b011_year_returns(result, calendar, candidate_years)


def _c003_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C003_VARIANTS:
            row[f"{variant}_net_total_return"] = _c003_year_returns(runs[variant], calendar, (year,))[year]
        rows.append(row)
    return pd.DataFrame(rows)


def _c003_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    v1 = metrics["macro_gate_mcap"]
    v2 = metrics["kospi_buy_and_hold"]
    yearly = v1["yearly_net_total_return"]
    spike_positive = sum(float(yearly[str(year)]) > 0.0 for year in (2010, 2025, 2026))
    rows = [
        {
            "hypothesis": "H1",
            "description": "V1 cumulative net total return > 0",
            "value": float(v1["cumulative_net_total_return"]),
            "threshold": 0.0,
            "passes": bool(float(v1["cumulative_net_total_return"]) > 0.0),
        },
        {
            "hypothesis": "H2",
            "description": "V1 cumulative net >= V2 cumulative net - 30pp",
            "value": float(v1["cumulative_net_total_return"]) - float(v2["cumulative_net_total_return"]),
            "threshold": -0.30,
            "passes": bool(float(v1["cumulative_net_total_return"]) >= float(v2["cumulative_net_total_return"]) - 0.30),
        },
        {
            "hypothesis": "H3",
            "description": "V1 positive in at least 2 of 2010, 2025, 2026",
            "value": int(spike_positive),
            "threshold": 2,
            "passes": bool(spike_positive >= 2),
        },
        {
            "hypothesis": "H4",
            "description": "V1 max drawdown improves on V2 by at least 5pp",
            "value": float(v1["max_drawdown"]) - float(v2["max_drawdown"]),
            "threshold": -0.05,
            "passes": bool(float(v1["max_drawdown"]) <= float(v2["max_drawdown"]) - 0.05),
        },
        {
            "hypothesis": "H5",
            "description": "V1 positive in >= 8 of 16 years",
            "value": int(v1["positive_years"]),
            "threshold": 8,
            "passes": bool(int(v1["positive_years"]) >= 8),
        },
        {
            "hypothesis": "H6",
            "description": "V1 net / V1 cost-0 >= 0.7",
            "value": float(v1["net_to_cost_0_ratio"]),
            "threshold": 0.7,
            "passes": bool(float(v1["net_to_cost_0_ratio"]) >= 0.7),
        },
    ]
    return pd.DataFrame(rows)


def _c003_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


C003_MONTHLY_OUTPUT_DIR = Path("reports/experiments/C003_monthly_macro_gated_strategy")
C003_MONTHLY_CUMULATIVE_NET = -0.5417073809779971
C004_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C004_quarterly_macro_gated_strategy")
C004_QUARTERLY_CUMULATIVE_NET = -0.22013309027255956
C005_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C005_macro_v4_yield_curve")
C005_QUARTERLY_CUMULATIVE_NET = -0.08478285179122336
C005_QUARTERLY_COST_0_CUMULATIVE_NET = 0.03671567736697412
C008_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C008_macro_v6_brent")
C008_QUARTERLY_CUMULATIVE_NET = 0.3697554631843185
C008_QUARTERLY_COST_0_CUMULATIVE_NET = 0.5982253500065959
C011_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C011_macro_v8_kr10y")
C011_QUARTERLY_CUMULATIVE_NET = 0.5500320799221281
C011_QUARTERLY_COST_0_CUMULATIVE_NET = 0.8334534338807984


def _c004_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C004_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c003_monthly_cumulative_net_total_return"] = C003_MONTHLY_CUMULATIVE_NET
    v1["quarterly_minus_monthly_cumulative_net_pp"] = v1_return - C003_MONTHLY_CUMULATIVE_NET
    v1["c003_monthly_trade_count_reference"] = _c003_monthly_trade_count_reference()
    return metrics


def _c004_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c003_monthly = _c003_monthly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C004_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c003_monthly_macro_gate_mcap_net_total_return"] = c003_monthly.get(year, float("nan"))
        row["quarterly_minus_monthly_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c003_monthly_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c004_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["quarterly_minus_monthly_cumulative_net_pp"])
    h7 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 quarterly cumulative net improves on C003 monthly by >= 10pp",
                "value": delta,
                "threshold": 0.10,
                "passes": bool(delta >= 0.10),
            }
        ]
    )
    return pd.concat([base, h7], ignore_index=True)


def _c004_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c005_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C005_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c004_v3_cumulative_net_total_return"] = C004_QUARTERLY_CUMULATIVE_NET
    v1["v4_minus_v3_cumulative_net_pp"] = v1_return - C004_QUARTERLY_CUMULATIVE_NET
    v1["yield_curve_favorable_quarters"] = int(quarterly_regime["favorable_US_2_10_curve"].sum())
    v1["yield_curve_total_quarters"] = int(len(quarterly_regime))
    v1["yield_curve_complete_quarters"] = int(complete_quarters["favorable_US_2_10_curve"].notna().sum())
    return metrics


def _c005_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c004_quarterly = _c004_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C005_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c004_v3_macro_gate_mcap_net_total_return"] = c004_quarterly.get(year, float("nan"))
        row["v4_minus_v3_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c004_v3_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c005_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v4_minus_v3_cumulative_net_pp"])
    h7 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v4 cumulative net improves on C004 v3 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            }
        ]
    )
    return pd.concat([base, h7], ignore_index=True)


def _c005_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c006_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C006_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    usdcny_usdkrw = quarterly_regime.loc[:, ["USDCNY_yoy", "USDKRW_yoy"]].dropna()
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c005_v4_cumulative_net_total_return"] = C005_QUARTERLY_CUMULATIVE_NET
    v1["c005_v4_cost_0_cumulative_net_total_return"] = C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v5_minus_v4_cumulative_net_pp"] = v1_return - C005_QUARTERLY_CUMULATIVE_NET
    v1["v5_minus_v4_cost_0_cumulative_net_pp"] = cost_0_return - C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["usdcny_favorable_quarters"] = int(complete_quarters["favorable_USDCNY"].sum())
    v1["usdcny_total_quarters"] = int(len(complete_quarters))
    v1["usdcny_yoy_usdkrw_yoy_correlation"] = (
        float(usdcny_usdkrw["USDCNY_yoy"].corr(usdcny_usdkrw["USDKRW_yoy"]))
        if len(usdcny_usdkrw) >= 2
        else float("nan")
    )
    return metrics


def _c006_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c005_quarterly = _c005_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C006_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c005_v4_macro_gate_mcap_net_total_return"] = c005_quarterly.get(year, float("nan"))
        row["v5_minus_v4_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c005_v4_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c006_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v5_minus_v4_cumulative_net_pp"])
    h7_h8 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v5 cumulative net improves on C005 v4 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "USDCNY yoy and USDKRW yoy correlation, descriptive only",
                "value": float(v1["usdcny_yoy_usdkrw_yoy_correlation"]),
                "threshold": float("nan"),
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h8], ignore_index=True)


def _c006_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c007_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C007_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c005_n5_cumulative_net_total_return"] = C005_QUARTERLY_CUMULATIVE_NET
    v1["c005_n5_cost_0_cumulative_net_total_return"] = C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["n20_minus_n5_cumulative_net_pp"] = v1_return - C005_QUARTERLY_CUMULATIVE_NET
    v1["n20_minus_n5_cost_0_cumulative_net_pp"] = cost_0_return - C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["c005_n5_trade_count_reference"] = _c005_trade_count_reference()
    return metrics


def _c007_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c005_quarterly = _c005_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C007_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c005_n5_macro_gate_mcap_net_total_return"] = c005_quarterly.get(year, float("nan"))
        row["n20_minus_n5_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c005_n5_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c007_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["n20_minus_n5_cumulative_net_pp"])
    h8_value = float(v1["yearly_net_total_return"].get("2018", float("nan")))
    h7_h8 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 N=20 cumulative net improves on C005 N=5 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "V1 N=20 2018 net total return, descriptive concentration check",
                "value": h8_value,
                "threshold": float("nan"),
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h8], ignore_index=True)


def _c007_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c008_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C008_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    brent_usdkrw = quarterly_regime.loc[:, ["Brent_yoy", "USDKRW_yoy"]].dropna()
    brent_vix = quarterly_regime.loc[:, ["Brent_yoy", "VIX_60d_avg"]].dropna()
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c005_v4_cumulative_net_total_return"] = C005_QUARTERLY_CUMULATIVE_NET
    v1["c005_v4_cost_0_cumulative_net_total_return"] = C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v6_minus_v4_cumulative_net_pp"] = v1_return - C005_QUARTERLY_CUMULATIVE_NET
    v1["v6_minus_v4_cost_0_cumulative_net_pp"] = cost_0_return - C005_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["brent_favorable_quarters"] = int(complete_quarters["favorable_Brent"].sum())
    v1["brent_total_quarters"] = int(len(complete_quarters))
    v1["brent_yoy_usdkrw_yoy_correlation"] = (
        float(brent_usdkrw["Brent_yoy"].corr(brent_usdkrw["USDKRW_yoy"])) if len(brent_usdkrw) >= 2 else float("nan")
    )
    v1["brent_yoy_vix_60d_avg_correlation"] = (
        float(brent_vix["Brent_yoy"].corr(brent_vix["VIX_60d_avg"])) if len(brent_vix) >= 2 else float("nan")
    )
    return metrics


def _c008_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c005_quarterly = _c005_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C008_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c005_v4_macro_gate_mcap_net_total_return"] = c005_quarterly.get(year, float("nan"))
        row["v6_minus_v4_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c005_v4_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c008_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v6_minus_v4_cumulative_net_pp"])
    h7_h8 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v6 cumulative net improves on C005 v4 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "Brent yoy and USDKRW yoy correlation, descriptive only",
                "value": float(v1["brent_yoy_usdkrw_yoy_correlation"]),
                "threshold": float("nan"),
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h8], ignore_index=True)


def _c008_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c008_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "market_cap"]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals["market_cap"], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _c010_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> tuple[dict[str, dict[str, Any]], BacktestResult]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C010_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    copper_brent = quarterly_regime.loc[:, ["Copper_yoy", "Brent_yoy"]].dropna()
    copper_usdkrw = quarterly_regime.loc[:, ["Copper_yoy", "USDKRW_yoy"]].dropna()
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c008_v6_cumulative_net_total_return"] = C008_QUARTERLY_CUMULATIVE_NET
    v1["c008_v6_cost_0_cumulative_net_total_return"] = C008_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v7_minus_v6_cumulative_net_pp"] = v1_return - C008_QUARTERLY_CUMULATIVE_NET
    v1["v7_minus_v6_cost_0_cumulative_net_pp"] = cost_0_return - C008_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["copper_favorable_quarters"] = int(complete_quarters["favorable_Copper"].sum())
    v1["copper_total_quarters"] = int(len(complete_quarters))
    v1["copper_yoy_brent_yoy_correlation"] = (
        float(copper_brent["Copper_yoy"].corr(copper_brent["Brent_yoy"])) if len(copper_brent) >= 2 else float("nan")
    )
    v1["copper_yoy_usdkrw_yoy_correlation"] = (
        float(copper_usdkrw["Copper_yoy"].corr(copper_usdkrw["USDKRW_yoy"]))
        if len(copper_usdkrw) >= 2
        else float("nan")
    )
    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c010_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c008_quarterly = _c008_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C010_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c008_v6_macro_gate_mcap_net_total_return"] = c008_quarterly.get(year, float("nan"))
        row["v7_minus_v6_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c008_v6_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c010_subperiod_breakdown(
    net_result: BacktestResult,
    cost_0_result: BacktestResult,
    calendar: object,
) -> pd.DataFrame:
    rows = []
    periods = (
        ("2010-2017", pd.Timestamp("2010-01-04"), pd.Timestamp("2017-12-31")),
        ("2018-2026", pd.Timestamp("2018-01-01"), pd.Timestamp("2026-05-04")),
    )
    for label, start, end in periods:
        net = metrics_is_oos(
            net_result.equity_curve,
            net_result.trades,
            start,
            end,
            start,
            end,
            calendar,
        )["is"]
        cost_0 = metrics_is_oos(
            cost_0_result.equity_curve,
            cost_0_result.trades,
            start,
            end,
            start,
            end,
            calendar,
        )["is"]
        rows.append(
            {
                "period": label,
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "v1_net_total_return": net["total_return"],
                "v1_cost_0_total_return": cost_0["total_return"],
                "v1_annualized_return": net["annualized_return"],
                "v1_cost_0_annualized_return": cost_0["annualized_return"],
                "v1_max_drawdown": net["max_drawdown"],
                "v1_cost_0_max_drawdown": cost_0["max_drawdown"],
                "v1_trade_count": net["trade_count"],
                "v1_cost_0_trade_count": cost_0["trade_count"],
            }
        )
    return pd.DataFrame(rows)


def _c010_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v7_minus_v6_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v7 cumulative net improves on C008 v6 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "Both C010 V1 subperiod cumulative net returns are >= 0, descriptive robustness check",
                "value": min(
                    float(v1["subperiod_2010_2017_net_total_return"]),
                    float(v1["subperiod_2018_2026_net_total_return"]),
                ),
                "threshold": 0.0,
                "passes": bool(
                    float(v1["subperiod_2010_2017_net_total_return"]) >= 0.0
                    and float(v1["subperiod_2018_2026_net_total_return"]) >= 0.0
                ),
            },
            {
                "hypothesis": "H9",
                "description": "Copper yoy and Brent yoy correlation, descriptive only",
                "value": float(v1["copper_yoy_brent_yoy_correlation"]),
                "threshold": float("nan"),
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c010_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c011_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> tuple[dict[str, dict[str, Any]], BacktestResult]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C011_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    kr10y_us10y = quarterly_regime.loc[:, ["KR10Y_yoy_change", "US10Y_yoy_change"]].dropna()
    kr10y_usdkrw = quarterly_regime.loc[:, ["KR10Y_yoy_change", "USDKRW_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c008_v6_cumulative_net_total_return"] = C008_QUARTERLY_CUMULATIVE_NET
    v1["c008_v6_cost_0_cumulative_net_total_return"] = C008_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v8_minus_v6_cumulative_net_pp"] = v1_return - C008_QUARTERLY_CUMULATIVE_NET
    v1["v8_minus_v6_cost_0_cumulative_net_pp"] = cost_0_return - C008_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["kr10y_favorable_quarters"] = int(complete_quarters["favorable_KR10Y"].sum())
    v1["kr10y_total_quarters"] = int(len(complete_quarters))
    v1["kr10y_yoy_change_us10y_yoy_change_correlation"] = (
        float(kr10y_us10y["KR10Y_yoy_change"].corr(kr10y_us10y["US10Y_yoy_change"]))
        if len(kr10y_us10y) >= 2
        else float("nan")
    )
    v1["kr10y_yoy_change_usdkrw_yoy_correlation"] = (
        float(kr10y_usdkrw["KR10Y_yoy_change"].corr(kr10y_usdkrw["USDKRW_yoy"]))
        if len(kr10y_usdkrw) >= 2
        else float("nan")
    )
    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c011_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c008_quarterly = _c008_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C011_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c008_v6_macro_gate_mcap_net_total_return"] = c008_quarterly.get(year, float("nan"))
        row["v8_minus_v6_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c008_v6_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c011_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v8_minus_v6_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v8 cumulative net improves on C008 v6 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "Both C011 V1 subperiod cumulative net returns are >= 0, descriptive robustness check",
                "value": min(
                    float(v1["subperiod_2010_2017_net_total_return"]),
                    float(v1["subperiod_2018_2026_net_total_return"]),
                ),
                "threshold": 0.0,
                "passes": bool(
                    float(v1["subperiod_2010_2017_net_total_return"]) >= 0.0
                    and float(v1["subperiod_2018_2026_net_total_return"]) >= 0.0
                ),
            },
            {
                "hypothesis": "H9",
                "description": "KR10y yoy change and US 10y yoy change correlation, descriptive only",
                "value": float(v1["kr10y_yoy_change_us10y_yoy_change_correlation"]),
                "threshold": float("nan"),
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c012_metrics(
    *,
    runs: dict[str, BacktestResult],
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> tuple[dict[str, dict[str, Any]], BacktestResult]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in C012_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_macro_gate_mcap"] = cost_0

    v1 = metrics["macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["regime_score"].notna()]
    kr3m_kr10y = quarterly_regime.loc[:, ["KR3M_yoy_change", "KR10Y_yoy_change"]].dropna()
    kr3m_us3m = quarterly_regime.loc[:, ["KR3M_yoy_change", "US3M_yoy_change"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c011_v8_cumulative_net_total_return"] = C011_QUARTERLY_CUMULATIVE_NET
    v1["c011_v8_cost_0_cumulative_net_total_return"] = C011_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v9_minus_v8_cumulative_net_pp"] = v1_return - C011_QUARTERLY_CUMULATIVE_NET
    v1["v9_minus_v8_cost_0_cumulative_net_pp"] = cost_0_return - C011_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["kr3m_favorable_quarters"] = int(complete_quarters["favorable_KR3M"].sum())
    v1["kr3m_total_quarters"] = int(len(complete_quarters))
    v1["kr3m_yoy_change_kr10y_yoy_change_correlation"] = (
        float(kr3m_kr10y["KR3M_yoy_change"].corr(kr3m_kr10y["KR10Y_yoy_change"]))
        if len(kr3m_kr10y) >= 2
        else float("nan")
    )
    v1["kr3m_yoy_change_us3m_yoy_change_correlation"] = (
        float(kr3m_us3m["KR3M_yoy_change"].corr(kr3m_us3m["US3M_yoy_change"]))
        if len(kr3m_us3m) >= 2
        else float("nan")
    )
    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c012_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c011_quarterly = _c011_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C012_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c011_v8_macro_gate_mcap_net_total_return"] = c011_quarterly.get(year, float("nan"))
        row["v9_minus_v8_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c011_v8_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c012_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v9_minus_v8_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v9 cumulative net improves on C011 v8 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C012 V1 subperiod cumulative net improves pre-2018 and remains >= 0 in 2018-2026",
                "value": float(v1["subperiod_2010_2017_net_total_return"]),
                "threshold": -0.21476707289130448,
                "passes": bool(
                    float(v1["subperiod_2010_2017_net_total_return"]) > -0.21476707289130448
                    and float(v1["subperiod_2018_2026_net_total_return"]) >= 0.0
                ),
            },
            {
                "hypothesis": "H9",
                "description": "KR3m yoy change correlations with KR10y and US 3m changes are descriptive redundancy checks",
                "value": max(
                    abs(float(v1["kr3m_yoy_change_kr10y_yoy_change_correlation"])),
                    abs(float(v1["kr3m_yoy_change_us3m_yoy_change_correlation"])),
                ),
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c011_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["macro_gate_mcap"].equity_curve["date"],
            "V1_macro_gate_mcap_net_value": runs["macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _c012_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c005_quarterly_year_reference() -> dict[int, float]:
    path = C005_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c004_quarterly_year_reference() -> dict[int, float]:
    path = C004_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c008_quarterly_year_reference() -> dict[int, float]:
    path = C008_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c011_quarterly_year_reference() -> dict[int, float]:
    path = C011_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c003_monthly_year_reference() -> dict[int, float]:
    path = C003_MONTHLY_OUTPUT_DIR / "monthly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c003_monthly_trade_count_reference() -> int | float:
    path = C003_MONTHLY_OUTPUT_DIR / "metrics.json"
    if not path.exists():
        return float("nan")
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return int(data["macro_gate_mcap"]["trade_count"])


def _c005_trade_count_reference() -> int | float:
    path = C005_QUARTERLY_OUTPUT_DIR / "metrics.json"
    if not path.exists():
        return float("nan")
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return int(data["macro_gate_mcap"]["trade_count"])


def _write_b011_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    summary: pd.DataFrame,
    gate: pd.Series,
) -> None:
    del gate
    lines = ["# B011 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| regime_gate | KOSPI proxy level > 200-day SMA; B004(c) frozen gate window |",
            "| selection | top 5 by prior-day market cap, equal weight when gate ON |",
            "| exit | exit_on_gate_off plus universe exit when name leaves eligibility |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b011_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Gate Only Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Gate Only Summary", summary))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c003_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    del year_breakdown
    lines = ["# C003 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of each month; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c003_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c004_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C004 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c003_monthly_reference | C003 monthly cumulative net -54.17%; monthly columns read from C003 output files |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c004_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c005_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C005 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c004_v3_reference | C004 v3 quarterly cumulative net -22.01%; yearly columns read from C004 output files |",
            "| yield_curve_timing | DGS2 and DGS10 use the aligned FRED observations available to the Korean signal date under src.data.macro_factors timing rules |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c005_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c006_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C006 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, USDCNY yoy <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c005_v4_reference | C005 v4 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |",
            "| usdcny_timing | DEXCHUS uses the aligned FRED observation available to the Korean signal date under src.data.macro_factors timing rules |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c006_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c007_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C007 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 20 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c005_n5_reference | C005 v4 N=5 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c007_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c008_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C008 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c005_v4_reference | C005 v4 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |",
            "| brent_timing | DCOILBRENTEU uses the aligned FRED observation available to the Korean signal date under src.data.macro_factors timing rules |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c008_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c010_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C010 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, Copper yoy > 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c008_v6_reference | C008 v6 quarterly cumulative net +36.98%; cost-0 +59.82%; yearly columns read from C008 output files |",
            "| copper_timing | PCOPPUSDM is monthly; each KRX signal date uses the latest FRED observation at or before the aligned lookup date, so quarter-end signals and the 252-trading-day YoY base use no future monthly value |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c010_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c011_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C011 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c008_v6_reference | C008 v6 quarterly cumulative net +36.98%; cost-0 +59.82%; yearly columns read from C008 output files |",
            "| kr10y_timing | IRLTLT01KRM156N is monthly; each KRX signal date uses the latest FRED observation at or before the aligned lookup date, so quarter-end signals and the 252-trading-day YoY change base use no future monthly value |",
            "| kr10y_formula | KR10y yoy is a percentage-point yield change, KR10Y(T) - KR10Y(T-12 months), not a return ratio |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c011_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c012_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C012 Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| panels_used | {json.dumps(config['panels'], ensure_ascii=False)} |",
            f"| period_start | {config['period']['start']} |",
            f"| period_end | {config['period']['end']} |",
            f"| excluded_years | {json.dumps(config['period']['exclude_calendar_years'])} |",
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, KR3m yoy change <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c011_v8_reference | C011 v8 quarterly cumulative net +55.00%; cost-0 +83.35%; yearly columns read from C011 output files |",
            "| kr_rates_timing | IRLTLT01KRM156N and IR3TIB01KRM156N are monthly; each KRX signal date uses the latest FRED observation at or before the aligned lookup date, so quarter-end signals and the 12-month change base use no future monthly value |",
            "| kr3m_formula | KR3m yoy is a percentage-point rate change, KR3M(T) - KR3M(T-12 months), not a return ratio |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c012_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _c003_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C003_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    lines.append("")
    return lines


def _c004_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C004_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C003 Monthly Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c003_monthly_cumulative_net_total_return | {_format_report_value(C003_MONTHLY_CUMULATIVE_NET)} |",
            f"| quarterly_minus_monthly_cumulative_net_pp | {_format_report_value(v1['quarterly_minus_monthly_cumulative_net_pp'])} |",
            f"| c003_monthly_trade_count_reference | {_format_report_value(v1['c003_monthly_trade_count_reference'])} |",
            "",
        ]
    )
    return lines


def _c005_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C005_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C004 V3 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c004_v3_cumulative_net_total_return | {_format_report_value(C004_QUARTERLY_CUMULATIVE_NET)} |",
            f"| v4_minus_v3_cumulative_net_pp | {_format_report_value(v1['v4_minus_v3_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| yield_curve_favorable_quarters | {_format_report_value(v1['yield_curve_favorable_quarters'])} |",
            f"| yield_curve_total_quarters | {_format_report_value(v1['yield_curve_total_quarters'])} |",
            "",
        ]
    )
    return lines


def _c006_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C006_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C005 V4 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c005_v4_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c005_v4_cost_0_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v5_minus_v4_cumulative_net_pp | {_format_report_value(v1['v5_minus_v4_cumulative_net_pp'])} |",
            f"| v5_minus_v4_cost_0_cumulative_net_pp | {_format_report_value(v1['v5_minus_v4_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| usdcny_favorable_quarters | {_format_report_value(v1['usdcny_favorable_quarters'])} |",
            f"| usdcny_total_quarters | {_format_report_value(v1['usdcny_total_quarters'])} |",
            f"| usdcny_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['usdcny_yoy_usdkrw_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c007_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C007_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C005 N5 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c005_n5_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c005_n5_cost_0_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| n20_minus_n5_cumulative_net_pp | {_format_report_value(v1['n20_minus_n5_cumulative_net_pp'])} |",
            f"| n20_minus_n5_cost_0_cumulative_net_pp | {_format_report_value(v1['n20_minus_n5_cost_0_cumulative_net_pp'])} |",
            f"| c005_n5_trade_count_reference | {_format_report_value(v1['c005_n5_trade_count_reference'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            "",
        ]
    )
    return lines


def _c008_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C008_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C005 V4 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c005_v4_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c005_v4_cost_0_cumulative_net_total_return | {_format_report_value(C005_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v6_minus_v4_cumulative_net_pp | {_format_report_value(v1['v6_minus_v4_cumulative_net_pp'])} |",
            f"| v6_minus_v4_cost_0_cumulative_net_pp | {_format_report_value(v1['v6_minus_v4_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| brent_favorable_quarters | {_format_report_value(v1['brent_favorable_quarters'])} |",
            f"| brent_total_quarters | {_format_report_value(v1['brent_total_quarters'])} |",
            f"| brent_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['brent_yoy_usdkrw_yoy_correlation'])} |",
            f"| brent_yoy_vix_60d_avg_correlation | {_format_report_value(v1['brent_yoy_vix_60d_avg_correlation'])} |",
            "",
        ]
    )
    return lines


def _c010_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C010_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C008 V6 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c008_v6_cumulative_net_total_return | {_format_report_value(C008_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c008_v6_cost_0_cumulative_net_total_return | {_format_report_value(C008_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v7_minus_v6_cumulative_net_pp | {_format_report_value(v1['v7_minus_v6_cumulative_net_pp'])} |",
            f"| v7_minus_v6_cost_0_cumulative_net_pp | {_format_report_value(v1['v7_minus_v6_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| copper_favorable_quarters | {_format_report_value(v1['copper_favorable_quarters'])} |",
            f"| copper_total_quarters | {_format_report_value(v1['copper_total_quarters'])} |",
            f"| copper_yoy_brent_yoy_correlation | {_format_report_value(v1['copper_yoy_brent_yoy_correlation'])} |",
            f"| copper_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['copper_yoy_usdkrw_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c011_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C011_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C008 V6 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c008_v6_cumulative_net_total_return | {_format_report_value(C008_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c008_v6_cost_0_cumulative_net_total_return | {_format_report_value(C008_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v8_minus_v6_cumulative_net_pp | {_format_report_value(v1['v8_minus_v6_cumulative_net_pp'])} |",
            f"| v8_minus_v6_cost_0_cumulative_net_pp | {_format_report_value(v1['v8_minus_v6_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| kr10y_favorable_quarters | {_format_report_value(v1['kr10y_favorable_quarters'])} |",
            f"| kr10y_total_quarters | {_format_report_value(v1['kr10y_total_quarters'])} |",
            f"| kr10y_yoy_change_us10y_yoy_change_correlation | {_format_report_value(v1['kr10y_yoy_change_us10y_yoy_change_correlation'])} |",
            f"| kr10y_yoy_change_usdkrw_yoy_correlation | {_format_report_value(v1['kr10y_yoy_change_usdkrw_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c012_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in C012_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C011 V8 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c011_v8_cumulative_net_total_return | {_format_report_value(C011_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c011_v8_cost_0_cumulative_net_total_return | {_format_report_value(C011_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v9_minus_v8_cumulative_net_pp | {_format_report_value(v1['v9_minus_v8_cumulative_net_pp'])} |",
            f"| v9_minus_v8_cost_0_cumulative_net_pp | {_format_report_value(v1['v9_minus_v8_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| kr3m_favorable_quarters | {_format_report_value(v1['kr3m_favorable_quarters'])} |",
            f"| kr3m_total_quarters | {_format_report_value(v1['kr3m_total_quarters'])} |",
            f"| kr3m_yoy_change_kr10y_yoy_change_correlation | {_format_report_value(v1['kr3m_yoy_change_kr10y_yoy_change_correlation'])} |",
            f"| kr3m_yoy_change_us3m_yoy_change_correlation | {_format_report_value(v1['kr3m_yoy_change_us3m_yoy_change_correlation'])} |",
            "",
        ]
    )
    return lines


def _b011_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    columns = (
        "cumulative_net_total_return",
        "max_drawdown",
        "positive_years",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "trade_count",
        "hit_rate",
        "cost_paid_total",
    )
    lines = [
        "## Variant Metrics",
        "",
        "| variant | " + " | ".join(columns) + " |",
        "| --- | " + " | ".join("---:" for _ in columns) + " |",
    ]
    for variant in B011_VARIANTS:
        block = metrics[variant]
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


def _validate_b006_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B006_CONFIG_KEYS:
        raise ValueError(f"B006 config keys must be exactly {EXPECTED_B006_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["filter"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B006 filter keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["ranking"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B006 ranking keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B006 exit keys must be exactly ('type',).")
    if tuple(config["variants"]) != B006_VARIANTS:
        raise ValueError(f"B006 variants must be exactly {list(B006_VARIANTS)}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B006 requires strategy.max_positions: 5.")
    if config["filter"]["type"] != "flow_sign_both_positive":
        raise ValueError("B006 requires filter.type: flow_sign_both_positive.")
    if config["ranking"]["type"] != "combined_flow_5":
        raise ValueError("B006 requires ranking.type: combined_flow_5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B006 requires exit.type: signal_reversal.")


def _validate_b007_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B007_CONFIG_KEYS:
        raise ValueError(f"B007 config keys must be exactly {EXPECTED_B007_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B007 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["ranking"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B007 ranking keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B007 exit keys must be exactly ('type',).")
    if tuple(config["filter"].keys()) != EXPECTED_B007_FILTER_KEYS:
        raise ValueError(f"B007 filter keys must be exactly {EXPECTED_B007_FILTER_KEYS}.")
    if tuple(config["relative"].keys()) != EXPECTED_B005_RELATIVE_KEYS:
        raise ValueError(f"B007 relative keys must be exactly {EXPECTED_B005_RELATIVE_KEYS}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B007 requires strategy.max_positions: 5.")
    if config["trigger"]["type"] != "acceleration":
        raise ValueError("B007 requires trigger.type: acceleration.")
    if config["ranking"]["type"] != "combined_flow_5":
        raise ValueError("B007 requires ranking.type: combined_flow_5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B007 requires exit.type: signal_reversal.")
    if tuple(config["filter"]["candidates"]) != B007_FILTER_CANDIDATES:
        raise ValueError(f"B007 filter.candidates must be exactly {list(B007_FILTER_CANDIDATES)}.")
    if int(config["relative"]["cross_sectional_min_count"]) != 30:
        raise ValueError("B007 requires relative.cross_sectional_min_count: 30.")


def _validate_b008_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B008_CONFIG_KEYS:
        raise ValueError(f"B008 config keys must be exactly {EXPECTED_B008_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B008 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["ranking"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B008 ranking keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B008 exit keys must be exactly ('type',).")
    if tuple(config["relative"].keys()) != EXPECTED_B005_RELATIVE_KEYS:
        raise ValueError(f"B008 relative keys must be exactly {EXPECTED_B005_RELATIVE_KEYS}.")
    if tuple(config["variants"]) != B008_VARIANTS:
        raise ValueError(f"B008 variants must be exactly {list(B008_VARIANTS)}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B008 requires strategy.max_positions: 5.")
    if config["trigger"]["type"] != "acceleration":
        raise ValueError("B008 requires trigger.type: acceleration.")
    if config["ranking"]["type"] != "combined_flow_5":
        raise ValueError("B008 requires ranking.type: combined_flow_5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B008 requires exit.type: signal_reversal.")
    if int(config["relative"]["cross_sectional_min_count"]) != 30:
        raise ValueError("B008 requires relative.cross_sectional_min_count: 30.")


def _validate_b009_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B009_CONFIG_KEYS:
        raise ValueError(f"B009 config keys must be exactly {EXPECTED_B009_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B009 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["ranking"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B009 ranking keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B009 exit keys must be exactly ('type',).")
    if tuple(config["variants"]) != B009_VARIANTS:
        raise ValueError(f"B009 variants must be exactly {list(B009_VARIANTS)}.")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B009 requires strategy.max_positions: 5.")
    if config["trigger"]["type"] != "acceleration":
        raise ValueError("B009 requires trigger.type: acceleration.")
    if config["ranking"]["type"] != "combined_flow_5":
        raise ValueError("B009 requires ranking.type: combined_flow_5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B009 requires exit.type: signal_reversal.")


def _validate_b010_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B010_CONFIG_KEYS:
        raise ValueError(f"B010 config keys must be exactly {EXPECTED_B010_CONFIG_KEYS}; got {keys}.")
    _validate_b002_common_config_shape(config)
    if tuple(config["trigger"].keys()) != EXPECTED_B004_TRIGGER_KEYS:
        raise ValueError(f"B010 trigger keys must be exactly {EXPECTED_B004_TRIGGER_KEYS}.")
    if tuple(config["ranking"].keys()) != EXPECTED_B006_ROLE_KEYS:
        raise ValueError(f"B010 ranking keys must be exactly {EXPECTED_B006_ROLE_KEYS}.")
    if tuple(config["exit"].keys()) != EXPECTED_B002_EXIT_KEYS:
        raise ValueError("B010 exit keys must be exactly ('type',).")
    if tuple(config["survival_comparison"].keys()) != EXPECTED_B010_SURVIVAL_KEYS:
        raise ValueError(f"B010 survival_comparison keys must be exactly {EXPECTED_B010_SURVIVAL_KEYS}.")
    if tuple(config["variants"]) != B010_VARIANTS:
        raise ValueError(f"B010 variants must be exactly {list(B010_VARIANTS)}.")
    if tuple(int(year) for year in config["excluded_years"]) != (2016,):
        raise ValueError("B010 requires excluded_years: [2016].")
    if tuple(int(year) for year in config["candidate_years"]) != (2010, 2011, 2012, 2013, 2014, 2015, 2017):
        raise ValueError("B010 candidate_years must be exactly [2010, 2011, 2012, 2013, 2014, 2015, 2017].")
    if int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("B010 requires strategy.max_positions: 5.")
    if config["trigger"]["type"] != "acceleration":
        raise ValueError("B010 requires trigger.type: acceleration.")
    if config["ranking"]["type"] != "combined_flow_5":
        raise ValueError("B010 requires ranking.type: combined_flow_5.")
    if config["exit"]["type"] != "signal_reversal":
        raise ValueError("B010 requires exit.type: signal_reversal.")


def _validate_b011_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_B011_CONFIG_KEYS:
        raise ValueError(f"B011 config keys must be exactly {EXPECTED_B011_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"B011 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"B011 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_B004_REGIME_KEYS:
        raise ValueError(f"B011 regime keys must be exactly {EXPECTED_B004_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"B011 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"B011 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != B011_VARIANTS:
        raise ValueError(f"B011 variants must be exactly {list(B011_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("B011 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("B011 requires period.exclude_calendar_years: [2016].")
    if config["regime"]["gate_type"] != "kospi_sma":
        raise ValueError("B011 requires regime.gate_type: kospi_sma.")
    if int(config["regime"]["window"]) != 200:
        raise ValueError("B011 requires regime.window: 200.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("B011 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("B011 requires selection.n: 5.")


def _validate_c003_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C003_CONFIG_KEYS:
        raise ValueError(f"C003 config keys must be exactly {EXPECTED_C003_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C003 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C003 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C003 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C003 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C003 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C003 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C003_VARIANTS:
        raise ValueError(f"C003 variants must be exactly {list(C003_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C003 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C003 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy"):
        raise ValueError("C003 macro_signals are frozen by the ticket.")
    if config["regime"]["composite_rule"] != "majority_vote":
        raise ValueError("C003 requires regime.composite_rule: majority_vote.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C003 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C003 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C003 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "monthly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C003 requires monthly last_trading_day rebalance.")


def _validate_c004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C004_CONFIG_KEYS:
        raise ValueError(f"C004 config keys must be exactly {EXPECTED_C004_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C004 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C004 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C004 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C004 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C004 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C004 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C004_VARIANTS:
        raise ValueError(f"C004 variants must be exactly {list(C004_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C004 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C004 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy"):
        raise ValueError("C004 macro_signals are frozen by the ticket.")
    if config["regime"]["composite_rule"] != "majority_vote":
        raise ValueError("C004 requires regime.composite_rule: majority_vote.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C004 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C004 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C004 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C004 requires quarterly last_trading_day rebalance.")


def _validate_c005_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C005_CONFIG_KEYS:
        raise ValueError(f"C005 config keys must be exactly {EXPECTED_C005_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C005 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C005 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C005 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C005 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C005 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C005 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C005_VARIANTS:
        raise ValueError(f"C005 variants must be exactly {list(C005_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C005 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C005 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve"):
        raise ValueError("C005 macro_signals must add only us_2_10_curve to the C004 signals.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C005 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C005 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C005 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C005 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C005 requires quarterly last_trading_day rebalance.")


def _validate_c006_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C006_CONFIG_KEYS:
        raise ValueError(f"C006 config keys must be exactly {EXPECTED_C006_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C006 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C006 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C006 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C006 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C006 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C006 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C006_VARIANTS:
        raise ValueError(f"C006 variants must be exactly {list(C006_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C006 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C006 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "usdcny_yoy",
    ):
        raise ValueError("C006 macro_signals must add only usdcny_yoy to the C005 signals.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C006 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C006 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C006 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C006 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C006 requires quarterly last_trading_day rebalance.")


def _validate_c007_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C007_CONFIG_KEYS:
        raise ValueError(f"C007 config keys must be exactly {EXPECTED_C007_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C007 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C007 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C007 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C007 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C007 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C007 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C007_VARIANTS:
        raise ValueError(f"C007 variants must be exactly {list(C007_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C007 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C007 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != ("usdkrw_yoy", "vix_60d_vs_240d", "dxy_yoy", "us_2_10_curve"):
        raise ValueError("C007 macro_signals must match C005 v4 exactly.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C007 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C007 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C007 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 20:
        raise ValueError("C007 requires selection.n: 20.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C007 requires quarterly last_trading_day rebalance.")


def _validate_c008_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C008_CONFIG_KEYS:
        raise ValueError(f"C008 config keys must be exactly {EXPECTED_C008_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C008 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C008 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C008 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C008 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C008 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C008 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C008_VARIANTS:
        raise ValueError(f"C008 variants must be exactly {list(C008_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C008 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C008 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
    ):
        raise ValueError("C008 macro_signals must add Brent to C005 v4 and exclude USDCNY.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C008 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C008 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C008 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C008 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C008 requires quarterly last_trading_day rebalance.")


def _validate_c010_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C010_CONFIG_KEYS:
        raise ValueError(f"C010 config keys must be exactly {EXPECTED_C010_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C010 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C010 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C010 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C010 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C010 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C010 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C010_VARIANTS:
        raise ValueError(f"C010 variants must be exactly {list(C010_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C010 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C010 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "copper_yoy",
    ):
        raise ValueError("C010 macro_signals must add only copper_yoy to C008 v6.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C010 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C010 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C010 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C010 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C010 requires quarterly last_trading_day rebalance.")


def _validate_c011_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C011_CONFIG_KEYS:
        raise ValueError(f"C011 config keys must be exactly {EXPECTED_C011_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C011 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C011 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C011 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C011 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C011 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C011 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C011_VARIANTS:
        raise ValueError(f"C011 variants must be exactly {list(C011_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C011 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C011 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
    ):
        raise ValueError("C011 macro_signals must add kr10y_yoy_change to C008 v6 and exclude copper.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C011 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C011 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C011 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C011 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C011 requires quarterly last_trading_day rebalance.")


def _validate_c012_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C012_CONFIG_KEYS:
        raise ValueError(f"C012 config keys must be exactly {EXPECTED_C012_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C012 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C012 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C012 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C012 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C012 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C012 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C012_VARIANTS:
        raise ValueError(f"C012 variants must be exactly {list(C012_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C012 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C012 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "kr3m_yoy_change",
    ):
        raise ValueError("C012 macro_signals must add kr3m_yoy_change to C011 v8 and exclude copper/USDCNY.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C012 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C012 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C012 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C012 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C012 requires quarterly last_trading_day rebalance.")


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
