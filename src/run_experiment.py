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
from src.features.macro_regime import (
    D005_SIGNAL_NAMES,
    D003_SIGNAL_NAMES,
    D009_SIGNAL_NAMES,
    EIGHT_PPI_SIGNAL_NAMES,
    build_macro_regime_daily,
    exposure_scalar,
    factor_aggregation_composite,
    monthly_regime_log,
    quarterly_regime_log,
)
from src.features.regime import regime_gate_on, regime_state_log
from src.features.sector_flow_score import (
    build_rank_ic_diagnostics,
    build_sector_flow_scores,
    build_sector_forward_returns,
    build_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics,
    diagnostics_pass,
    quarter_end_dates,
)
from src.features.sector_combined_score import (
    build_rank_ic_diagnostics as build_combined_rank_ic_diagnostics,
    build_sector_combined_scores,
    build_sector_forward_returns as build_combined_sector_forward_returns,
    build_subperiod_diagnostics as build_combined_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics as build_combined_top_bottom_spread_diagnostics,
    diagnostics_pass as combined_diagnostics_pass,
)
from src.features.sector_breadth_score import (
    build_rank_ic_diagnostics as build_breadth_rank_ic_diagnostics,
    build_sector_breadth_scores,
    build_subperiod_diagnostics as build_breadth_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics as build_breadth_top_bottom_spread_diagnostics,
)
from src.features.sector_rs_score import (
    build_rank_ic_diagnostics as build_rs_rank_ic_diagnostics,
    build_sector_forward_returns as build_rs_sector_forward_returns,
    build_sector_rs_scores,
    build_subperiod_diagnostics as build_rs_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics as build_rs_top_bottom_spread_diagnostics,
    diagnostics_pass as rs_diagnostics_pass,
    quarter_end_dates as rs_quarter_end_dates,
)
from src.features.stock_rs_score import (
    build_stock_forward_returns,
    build_stock_rank_ic_diagnostics,
    build_stock_rs_scores,
    build_stock_top_bottom_spread_diagnostics,
)
from src.features.stock_foreign_flow_score import build_stock_foreign_flow_scores
from src.features.stock_institution_flow_score import build_stock_institution_flow_scores
from src.reporting.metrics import compute_metrics, metrics_is_oos
from src.reporting.report import write_report
from src.reporting.subperiod_analyzer import (
    rolling_year_sharpe,
    spike_years,
    subperiod_metrics_row,
    year_breakdown as subperiod_year_breakdown,
)
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
from src.strategies.b011_gate_only_full_timeline import (
    VARIANTS as B011_VARIANTS,
    build_kospi_buy_and_hold_result,
    run_b011_variants,
)
from src.strategies.c003_monthly_macro_gate import (
    VARIANTS as C003_VARIANTS,
    _run_segmented_cash,
    monthly_execution_dates,
    run_c003_variants,
    run_monthly_mcap_backtest,
)
from src.strategies.c004_quarterly_macro_gate import (
    VARIANTS as C004_VARIANTS,
    _quarterly_execution_candidates,
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
from src.strategies.c013_quarterly_macro_v10 import VARIANTS as C013_VARIANTS, run_c013_variants
from src.strategies.c014_quarterly_macro_v11 import VARIANTS as C014_VARIANTS, run_c014_variants
from src.strategies.c015_quarterly_macro_v12 import VARIANTS as C015_VARIANTS, run_c015_variants
from src.strategies.c016_quarterly_macro_v13 import VARIANTS as C016_VARIANTS, run_c016_variants
from src.strategies.c017_quarterly_macro_v14 import VARIANTS as C017_VARIANTS, run_c017_variants
from src.strategies.c018_quarterly_macro_v15 import VARIANTS as C018_VARIANTS, run_c018_variants
from src.strategies.c019_quarterly_macro_v16 import VARIANTS as C019_VARIANTS, run_c019_variants
from src.strategies.c020_quarterly_macro_v17 import VARIANTS as C020_VARIANTS, run_c020_variants
from src.strategies.d001_factor_aggregation import VARIANTS as D001_VARIANTS, run_d001_variants
from src.strategies.d002_zscore_24mo import VARIANTS as D002_VARIANTS, run_d002_variants
from src.strategies.d003_block_expansion import VARIANTS as D003_VARIANTS, run_d003_variants
from src.strategies.d004_position_sizing import (
    VARIANTS as D004_VARIANTS,
    run_d004_variants,
    run_quarterly_sized_mcap_backtest,
)
from src.strategies.d005_korea_growth import VARIANTS as D005_VARIANTS, run_d005_variants
from src.strategies.d006_window_grid import VARIANTS as D006_VARIANTS, run_d006_variants
from src.strategies.d007_threshold_grid import VARIANTS as D007_VARIANTS, run_d007_variants
from src.strategies.d008_subperiod_analysis import VARIANTS as D008_VARIANTS, run_d008_variants
from src.strategies.d009_chatgpt_holistic import VARIANTS as D009_VARIANTS, run_d009_variants
from src.strategies.d010_window_grid_on_d009 import VARIANTS as D010_VARIANTS, run_d010_variants
from src.strategies.d011_threshold_grid_on_d009 import VARIANTS as D011_VARIANTS, run_d011_variants
from src.strategies.d012_subperiod_on_d009 import VARIANTS as D012_VARIANTS, run_d012_variants
from src.strategies.d013_d009_threshold_minus_0p2 import VARIANTS as D013_VARIANTS, run_d013_variants
from src.strategies.d014_window_grid_on_d013 import VARIANTS as D014_VARIANTS, run_d014_variants
from src.strategies.d015_subperiod_on_d013 import VARIANTS as D015_VARIANTS, run_d015_variants
from src.strategies.e003_a_d013_replication import run_e003_a_variants
from src.strategies.e003_b_count_matched import run_e003_b_variants
from src.strategies.e003_c_pure_basket import run_e003_c_variants, run_weighted_quarterly_basket_backtest
from src.strategies.e004_flow_only import (
    build_e004_flow_top_sector_candidates,
    build_e004_sector_selection_log,
)
from src.strategies.e005_rs_only import (
    build_e005_rs_top_sector_candidates,
    build_e005_sector_selection_log,
)
from src.strategies.e006_flow_plus_rs import (
    build_e006_flow_plus_rs_top_sector_candidates,
    build_e006_sector_selection_log,
)
from src.strategies.e007_flow_rs_breadth import (
    build_e007_flow_rs_breadth_top_sector_candidates,
    build_e007_sector_selection_log,
)
from src.strategies.e008_topk_grid import (
    build_e008_sector_selection_log,
    build_e008_topk_grid_candidates,
    topk_label,
)
from src.strategies.e009_cost_stress import (
    SCENARIO_ORDER as E009_SCENARIO_ORDER,
    build_e009_cost_stress_candidates,
    validate_e009_cost_scenarios,
)
from src.strategies.e011_top4_champion import build_e011_top4_champion_candidates
from src.strategies.e012_robustness_ablation import (
    SCORE_ABLATIONS as E012_SCORE_ABLATIONS,
    TOPK_GRID as E012_TOPK_GRID,
    build_e012_score_ablation_candidates,
    build_e012_topk_grid_candidates,
    topk_summary_label as e012_topk_summary_label,
    validate_e012_cost_scenarios,
)
from src.strategies.e013_subperiod_spike import build_e013_top4_candidates, e013_segments_for_trading_window
from src.strategies.e014_rs_breadth_top4 import build_e014_rs_breadth_top4_candidates, rs_breadth_score_view
from src.strategies.e015_validation import (
    PASS_THRESHOLDS as E015_PASS_THRESHOLDS,
    SPIKE_EXCLUSION_GROUPS as E015_SPIKE_EXCLUSION_GROUPS,
    TOPK_STABILITY_GRID as E015_TOPK_STABILITY_GRID,
    build_e015_validation_candidates,
    drawdown_summary as e015_drawdown_summary,
    e015_segments_for_trading_window,
    topk_label as e015_topk_label,
)
from src.strategies.f002_stock_rs_d013_direct import (
    build_f002_d013_direct_score_universe,
    build_f002_stock_rs_d013_direct_candidates,
)
from src.strategies.f002_stock_rs_e014 import (
    build_f002_e014_selection_universe,
    build_f002_stock_rs_e014_candidates,
)
from src.strategies.f003_foreign_flow_d013_direct import (
    build_f003_d013_direct_score_universe,
    build_f003_foreign_flow_d013_direct_candidates,
)
from src.strategies.f003_foreign_flow_e014 import (
    build_f003_e014_selection_universe,
    build_f003_foreign_flow_e014_candidates,
)
from src.strategies.f004_institution_flow_d013_direct import (
    build_f004_d013_direct_score_universe,
    build_f004_institution_flow_d013_direct_candidates,
)
from src.strategies.f004_institution_flow_e014 import (
    build_f004_e014_selection_universe,
    build_f004_institution_flow_e014_candidates,
)
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
    "panel_date_filters",
    "market_breadth_csv",
    "macro_data_dir",
    "sector_mapping_csv",
    "period",
    "universe",
    "strategy",
    "regime",
    "selection",
    "rebalance",
    "costs",
    "variants",
    "output_dir",
)
EXPECTED_E004_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "panel_date_filters",
    "market_breadth_csv",
    "macro_data_dir",
    "sector_aggregate_csv",
    "stock_sector_daily_csv",
    "period",
    "universe",
    "strategy",
    "regime",
    "selection",
    "rebalance",
    "costs",
    "diagnostics",
    "variants",
    "output_dir",
)
EXPECTED_E005_CONFIG_KEYS = tuple(
    list(EXPECTED_E004_CONFIG_KEYS[: EXPECTED_E004_CONFIG_KEYS.index("period")])
    + ["sector_mapping_csv"]
    + list(EXPECTED_E004_CONFIG_KEYS[EXPECTED_E004_CONFIG_KEYS.index("period") :])
)
EXPECTED_E006_CONFIG_KEYS = EXPECTED_E005_CONFIG_KEYS
EXPECTED_E007_CONFIG_KEYS = EXPECTED_E005_CONFIG_KEYS
EXPECTED_E008_CONFIG_KEYS = EXPECTED_E005_CONFIG_KEYS
EXPECTED_E009_CONFIG_KEYS = tuple(
    "cost_scenarios" if key == "costs" else key for key in EXPECTED_E007_CONFIG_KEYS
)
EXPECTED_E011_CONFIG_KEYS = EXPECTED_E007_CONFIG_KEYS
EXPECTED_E012_CONFIG_KEYS = tuple(
    "cost_scenarios" if key == "costs" else key for key in EXPECTED_E008_CONFIG_KEYS
)
EXPECTED_E013_CONFIG_KEYS = EXPECTED_E007_CONFIG_KEYS[:-4] + (
    "costs",
    "subperiods",
    "variants",
    "per_year_analysis",
    "rolling_3yr_sharpe",
    "output_dir",
)
EXPECTED_E014_CONFIG_KEYS = EXPECTED_E011_CONFIG_KEYS
EXPECTED_F002_CONFIG_KEYS = (
    "experiment_id",
    "carrier",
    "panels",
    "panel_date_filters",
    "market_breadth_csv",
    "macro_data_dir",
    "sector_aggregate_csv",
    "stock_sector_daily_csv",
    "sector_mapping_csv",
    "period",
    "universe",
    "strategy",
    "regime",
    "selection",
    "rebalance",
    "costs",
    "diagnostics",
    "variants",
    "output_dir",
)
EXPECTED_E015_CONFIG_KEYS = EXPECTED_E007_CONFIG_KEYS[:-4] + (
    "cost_scenarios",
    "subperiods",
    "spike_exclusions",
    "validation",
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
EXPECTED_C013_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C014_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C015_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C016_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C017_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C018_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C019_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_C020_CONFIG_KEYS = EXPECTED_C003_CONFIG_KEYS
EXPECTED_D001_CONFIG_KEYS = (
    "experiment_id",
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
    "variants",
    "output_dir",
)
EXPECTED_D002_CONFIG_KEYS = EXPECTED_D001_CONFIG_KEYS
EXPECTED_D003_CONFIG_KEYS = EXPECTED_D001_CONFIG_KEYS
EXPECTED_D004_CONFIG_KEYS = (
    "experiment_id",
    "panels",
    "panel_date_filters",
    "market_breadth_csv",
    "macro_data_dir",
    "period",
    "universe",
    "strategy",
    "regime",
    "sizing",
    "selection",
    "rebalance",
    "costs",
    "variants",
    "output_dir",
)
EXPECTED_D005_CONFIG_KEYS = EXPECTED_D001_CONFIG_KEYS
EXPECTED_D006_CONFIG_KEYS = (
    "experiment_id",
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
    "variants_per_window",
    "fixed_baselines",
    "output_dir",
)
EXPECTED_D007_CONFIG_KEYS = (
    "experiment_id",
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
    "variants_per_threshold",
    "fixed_baselines",
    "output_dir",
)
EXPECTED_D008_CONFIG_KEYS = (
    "experiment_id",
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
    "subperiods",
    "variants",
    "per_year_analysis",
    "rolling_3yr_sharpe",
    "output_dir",
)
EXPECTED_D009_CONFIG_KEYS = EXPECTED_D001_CONFIG_KEYS
EXPECTED_D010_CONFIG_KEYS = EXPECTED_D006_CONFIG_KEYS
EXPECTED_D011_CONFIG_KEYS = EXPECTED_D007_CONFIG_KEYS
EXPECTED_D012_CONFIG_KEYS = EXPECTED_D008_CONFIG_KEYS
EXPECTED_D013_CONFIG_KEYS = EXPECTED_D001_CONFIG_KEYS
EXPECTED_D014_CONFIG_KEYS = EXPECTED_D006_CONFIG_KEYS
EXPECTED_D015_CONFIG_KEYS = EXPECTED_D008_CONFIG_KEYS
EXPECTED_B010_SURVIVAL_KEYS = ("b009_metrics_path",)
EXPECTED_B011_PERIOD_KEYS = ("start", "end", "exclude_calendar_years")
EXPECTED_B011_SELECTION_KEYS = ("type", "n")
EXPECTED_C003_REGIME_KEYS = ("macro_signals", "composite_rule", "on_threshold")
EXPECTED_D001_REGIME_KEYS = ("aggregation", "z_score_window_months", "on_threshold", "blocks")
EXPECTED_D002_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D003_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D004_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D005_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D006_REGIME_KEYS = ("aggregation", "on_threshold", "z_score_window_grid", "blocks")
EXPECTED_D007_REGIME_KEYS = ("aggregation", "z_score_window_months", "on_threshold_grid", "blocks")
EXPECTED_D008_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D009_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D010_REGIME_KEYS = EXPECTED_D006_REGIME_KEYS
EXPECTED_D011_REGIME_KEYS = EXPECTED_D007_REGIME_KEYS
EXPECTED_D012_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D013_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D014_REGIME_KEYS = EXPECTED_D006_REGIME_KEYS
EXPECTED_D015_REGIME_KEYS = EXPECTED_D001_REGIME_KEYS
EXPECTED_D001_STRATEGY_KEYS = ("lookback", "max_positions")
EXPECTED_D002_STRATEGY_KEYS = EXPECTED_D001_STRATEGY_KEYS
EXPECTED_D003_STRATEGY_KEYS = EXPECTED_D001_STRATEGY_KEYS
EXPECTED_D004_STRATEGY_KEYS = EXPECTED_D001_STRATEGY_KEYS
EXPECTED_D005_STRATEGY_KEYS = EXPECTED_D001_STRATEGY_KEYS
EXPECTED_D004_SIZING_KEYS = ("function", "k", "composite_floor")
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
    elif experiment_id == "E005":
        _validate_e005_config_shape(config)
        run_e005_experiment(config, config_path)
    elif experiment_id == "E006":
        _validate_e006_config_shape(config)
        run_e006_experiment(config, config_path)
    elif experiment_id == "E007":
        _validate_e007_config_shape(config)
        run_e007_experiment(config, config_path)
    elif experiment_id == "E008":
        _validate_e008_config_shape(config)
        run_e008_experiment(config, config_path)
    elif experiment_id == "E009":
        _validate_e009_config_shape(config)
        run_e009_experiment(config, config_path)
    elif experiment_id == "E011":
        _validate_e011_config_shape(config)
        run_e011_experiment(config, config_path)
    elif experiment_id == "E012":
        _validate_e012_config_shape(config)
        run_e012_experiment(config, config_path)
    elif experiment_id == "E013":
        _validate_e013_config_shape(config)
        run_e013_experiment(config, config_path)
    elif experiment_id == "E014":
        _validate_e014_config_shape(config)
        run_e014_experiment(config, config_path)
    elif experiment_id == "E015":
        _validate_e015_config_shape(config)
        run_e015_experiment(config, config_path)
    elif experiment_id == "F002":
        _validate_f002_config_shape(config)
        run_f002_experiment(config, config_path)
    elif experiment_id == "F003":
        _validate_f003_config_shape(config)
        run_f003_experiment(config, config_path)
    elif experiment_id == "F004":
        _validate_f004_config_shape(config)
        run_f004_experiment(config, config_path)
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
    elif experiment_id == "C013":
        _validate_c013_config_shape(config)
        run_c013_experiment(config, config_path)
    elif experiment_id == "C014":
        _validate_c014_config_shape(config)
        run_c014_experiment(config, config_path)
    elif experiment_id == "C015":
        _validate_c015_config_shape(config)
        run_c015_experiment(config, config_path)
    elif experiment_id == "C016":
        _validate_c016_config_shape(config)
        run_c016_experiment(config, config_path)
    elif experiment_id == "C017":
        _validate_c017_config_shape(config)
        run_c017_experiment(config, config_path)
    elif experiment_id == "C018":
        _validate_c018_config_shape(config)
        run_c018_experiment(config, config_path)
    elif experiment_id == "C019":
        _validate_c019_config_shape(config)
        run_c019_experiment(config, config_path)
    elif experiment_id == "C020":
        _validate_c020_config_shape(config)
        run_c020_experiment(config, config_path)
    elif experiment_id == "D001":
        _validate_d001_config_shape(config)
        run_d001_experiment(config, config_path)
    elif experiment_id == "D002":
        _validate_d002_config_shape(config)
        run_d002_experiment(config, config_path)
    elif experiment_id == "D003":
        _validate_d003_config_shape(config)
        run_d003_experiment(config, config_path)
    elif experiment_id == "D004":
        _validate_d004_config_shape(config)
        run_d004_experiment(config, config_path)
    elif experiment_id == "D005":
        _validate_d005_config_shape(config)
        run_d005_experiment(config, config_path)
    elif experiment_id == "D006":
        _validate_d006_config_shape(config)
        run_d006_experiment(config, config_path)
    elif experiment_id == "D007":
        _validate_d007_config_shape(config)
        run_d007_experiment(config, config_path)
    elif experiment_id == "D008":
        _validate_d008_config_shape(config)
        run_d008_experiment(config, config_path)
    elif experiment_id == "D009":
        _validate_d009_config_shape(config)
        run_d009_experiment(config, config_path)
    elif experiment_id == "D010":
        _validate_d010_config_shape(config)
        run_d010_experiment(config, config_path)
    elif experiment_id == "D011":
        _validate_d011_config_shape(config)
        run_d011_experiment(config, config_path)
    elif experiment_id == "D012":
        _validate_d012_config_shape(config)
        run_d012_experiment(config, config_path)
    elif experiment_id == "D013":
        _validate_d013_config_shape(config)
        run_d013_experiment(config, config_path)
    elif experiment_id == "D014":
        _validate_d014_config_shape(config)
        run_d014_experiment(config, config_path)
    elif experiment_id == "D015":
        _validate_d015_config_shape(config)
        run_d015_experiment(config, config_path)
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
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    run_outputs = {
        "A_d013_replication": run_e003_a_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        ),
        "B_count_matched": run_e003_b_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            sector_mapping=sector_mapping,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        ),
        "C_pure_basket": run_e003_c_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            sector_mapping=sector_mapping,
            costs=costs,
            segments=segments,
            min_sector_members=int(config["selection"]["pure_basket_min_sector_members"]),
        ),
    }

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    variant_metrics: dict[str, dict[str, dict[str, Any]]] = {}
    variant_candidates: dict[str, pd.DataFrame] = {}
    variant_runs: dict[str, BacktestResult] = {}
    for variant_name, (runs, candidates) in run_outputs.items():
        main_candidates = candidates["factor_macro_gate_mcap"]
        zero_result = _e003_zero_cost_result(
            panel,
            calendar,
            main_candidates,
            quarterly_log,
            segments,
            weighted=variant_name == "C_pure_basket",
        )
        metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        enriched_candidates = _e003_candidates_with_sector(main_candidates, sector_mapping)
        variant_metrics[variant_name] = metrics
        variant_candidates[variant_name] = enriched_candidates
        variant_runs[variant_name] = runs["factor_macro_gate_mcap"]

        variant_dir = output_dir / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, variant_dir / "config.yaml")
        _write_json(variant_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), variant_dir / "trades.csv")
        _write_ticker_safe_csv(_e003_signals(enriched_candidates), variant_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(variant_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            variant_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            variant_dir / "subperiod_breakdown.csv",
            index=False,
        )
        _e003_sector_holdings(enriched_candidates).to_csv(variant_dir / "sector_holdings.csv", index=False)

    comparison = _e003_comparison_summary(variant_metrics, variant_candidates)
    overlap = _e003_sector_holding_overlap(variant_candidates)
    comparison.to_csv(output_dir / "comparison_summary.csv", index=False)
    overlap.to_csv(output_dir / "sector_holding_overlap.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    _write_e003_layer2_report(output_dir, config, comparison, overlap)


def _e003_zero_cost_result(
    panel: pd.DataFrame,
    calendar: object,
    candidates: pd.DataFrame,
    quarterly_regime: pd.DataFrame,
    segments: tuple[tuple[object, object], ...],
    *,
    weighted: bool,
) -> BacktestResult:
    kwargs = {
        "panel": panel,
        "calendar": calendar,
        "candidates": candidates,
        "costs": Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        "segments": segments,
        "rebalance_dates": quarterly_execution_dates(calendar, quarterly_regime, segments),
    }
    if weighted:
        return run_weighted_quarterly_basket_backtest(**kwargs)
    return run_quarterly_mcap_backtest(**kwargs)


def _e003_variant_metrics(
    runs: dict[str, BacktestResult],
    zero_result: BacktestResult,
    calendar: object,
    candidate_years: tuple[int, ...],
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for variant in D009_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0
    metrics["factor_macro_gate_mcap"]["cost_0_cumulative_net_total_return"] = cost_0["cumulative_net_total_return"]
    return metrics


def _e003_candidates_with_sector(candidates: pd.DataFrame, sector_mapping: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        data = candidates.copy()
        for column in ("sector_code", "sector_name", "target_weight"):
            if column not in data.columns:
                data[column] = pd.Series(dtype="object")
        return data
    data = candidates.copy()
    data["종목코드"] = data["종목코드"].astype("string").str.zfill(6)
    if "sector_code" in data.columns and "sector_name" in data.columns:
        return data
    mapping = sector_mapping.loc[:, ["ticker", "final_sector_code", "final_sector_name"]].copy()
    mapping["ticker"] = mapping["ticker"].astype("string").str.zfill(6)
    mapping["sector_code"] = mapping["final_sector_code"].astype("string").str.zfill(2)
    mapping["sector_name"] = mapping["final_sector_name"].astype("string")
    data = data.merge(
        mapping.loc[:, ["ticker", "sector_code", "sector_name"]],
        left_on="종목코드",
        right_on="ticker",
        how="left",
        validate="many_to_one",
    ).drop(columns=["ticker"])
    if "target_weight" not in data.columns:
        data["target_weight"] = data.groupby("signal_date")["종목코드"].transform(lambda values: 1.0 / len(values))
    return data


def _e003_signals(candidates: pd.DataFrame) -> pd.DataFrame:
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


def _e003_sector_holdings(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=[
                "signal_date",
                "execution_date",
                "sector_code",
                "sector_name",
                "n_holdings",
                "sector_weight",
                "tickers",
            ]
        )
    data = candidates.copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["execution_date"] = pd.to_datetime(data["execution_date"], errors="raise").dt.normalize()
    data["target_weight"] = pd.to_numeric(data.get("target_weight", 0.0), errors="coerce")
    rows = []
    for keys, group in data.groupby(["signal_date", "execution_date", "sector_code", "sector_name"], dropna=False):
        signal_date, execution_date, sector_code, sector_name = keys
        rows.append(
            {
                "signal_date": signal_date,
                "execution_date": execution_date,
                "sector_code": sector_code,
                "sector_name": sector_name,
                "n_holdings": int(len(group)),
                "sector_weight": float(group["target_weight"].sum()) if "target_weight" in group else float("nan"),
                "tickers": " ".join(group["종목코드"].astype(str).str.zfill(6).sort_values()),
            }
        )
    return pd.DataFrame(rows).sort_values(["signal_date", "sector_code"]).reset_index(drop=True)


def _e003_comparison_summary(
    variant_metrics: dict[str, dict[str, dict[str, Any]]],
    variant_candidates: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    for variant, metrics in variant_metrics.items():
        block = metrics["factor_macro_gate_mcap"]
        candidates = variant_candidates[variant]
        rows.append(
            {
                "variant": variant,
                "cumulative_net_total_return": block["cumulative_net_total_return"],
                "sharpe": block["sharpe"],
                "max_drawdown": block["max_drawdown"],
                "trade_count": block["trade_count"],
                "positive_years": block["positive_years"],
                "avg_quarterly_holdings": _e003_avg_quarterly_holdings(candidates),
            }
        )
    table = pd.DataFrame(rows)
    baseline = table.loc[table["variant"].eq("A_d013_replication")].iloc[0]
    for column in ("cumulative_net_total_return", "sharpe", "max_drawdown"):
        table[f"vs_A_{column}_pp"] = table[column] - baseline[column]
    return table


def _e003_avg_quarterly_holdings(candidates: pd.DataFrame) -> float:
    if candidates.empty:
        return 0.0
    counts = candidates.groupby("signal_date")["종목코드"].nunique()
    return float(counts.mean()) if not counts.empty else 0.0


def _e003_sector_holding_overlap(variant_candidates: dict[str, pd.DataFrame]) -> pd.DataFrame:
    signal_dates = sorted(
        {
            pd.Timestamp(date).normalize()
            for candidates in variant_candidates.values()
            for date in pd.to_datetime(candidates.get("signal_date", pd.Series(dtype="datetime64[ns]")), errors="coerce").dropna()
        }
    )
    rows = []
    for signal_date in signal_dates:
        sets = {
            variant: _e003_ticker_set(candidates, signal_date)
            for variant, candidates in variant_candidates.items()
        }
        sector_sets = {
            variant: _e003_sector_set(candidates, signal_date)
            for variant, candidates in variant_candidates.items()
        }
        row: dict[str, Any] = {"signal_date": signal_date}
        for variant, tickers in sets.items():
            row[f"{variant}_n_holdings"] = len(tickers)
            row[f"{variant}_n_sectors"] = len(sector_sets[variant])
        for left, right in (
            ("A_d013_replication", "B_count_matched"),
            ("A_d013_replication", "C_pure_basket"),
            ("B_count_matched", "C_pure_basket"),
        ):
            row[f"{left}_vs_{right}_ticker_overlap_pct"] = _e003_overlap_pct(sets[left], sets[right])
            row[f"{left}_vs_{right}_sector_overlap_pct"] = _e003_overlap_pct(sector_sets[left], sector_sets[right])
        rows.append(row)
    return pd.DataFrame(rows)


def _e003_ticker_set(candidates: pd.DataFrame, signal_date: pd.Timestamp) -> set[str]:
    if candidates.empty:
        return set()
    dates = pd.to_datetime(candidates["signal_date"], errors="raise").dt.normalize()
    return set(candidates.loc[dates.eq(signal_date), "종목코드"].astype(str).str.zfill(6))


def _e003_sector_set(candidates: pd.DataFrame, signal_date: pd.Timestamp) -> set[str]:
    if candidates.empty or "sector_code" not in candidates.columns:
        return set()
    dates = pd.to_datetime(candidates["signal_date"], errors="raise").dt.normalize()
    return set(candidates.loc[dates.eq(signal_date), "sector_code"].astype(str))


def _e003_overlap_pct(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return float("nan")
    denominator = min(len(left), len(right))
    if denominator == 0:
        return 0.0
    return float(len(left & right) / denominator)


def _write_e003_layer2_report(
    output_dir: Path,
    config: dict[str, Any],
    comparison: pd.DataFrame,
    overlap: pd.DataFrame,
) -> None:
    lines = [
        "# E003 Layer 2 Baselines Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_mapping_csv: {config['sector_mapping_csv']}",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- execution: signal quarter-end T executes on next KRX trading day",
        "- cost_policy: commission 1.5 bps per leg, tax 20 bps sell leg, slippage 5 bps per leg",
        "",
    ]
    lines.extend(_b004_dataframe_table("Comparison Summary", comparison))
    if not overlap.empty:
        overlap_summary = pd.DataFrame(
            [
                {
                    "metric": column,
                    "mean": float(pd.to_numeric(overlap[column], errors="coerce").mean()),
                }
                for column in overlap.columns
                if column.endswith("_overlap_pct")
            ]
        )
        lines.extend(_b004_dataframe_table("Average Overlap", overlap_summary))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e004_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    stock_sector_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    panel = _e004_panel_with_sector_columns(panel, stock_sector_daily)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)

    sector_dates = quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    forward_returns = build_sector_forward_returns(sector_daily, flow_scores["signal_date"].drop_duplicates())
    rank_ic = build_rank_ic_diagnostics(flow_scores, forward_returns)
    spread = build_top_bottom_spread_diagnostics(
        flow_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    subperiod = build_subperiod_diagnostics(rank_ic, spread)
    passed = diagnostics_pass(rank_ic, spread)

    costs = _costs_from_config(config["costs"])
    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    candidates = build_e004_flow_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        flow_scores=flow_scores,
        calendar=calendar,
        top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
    )
    selection_log = build_e004_sector_selection_log(candidates, flow_scores)

    rank_ic.to_csv(output_dir / "diagnostics_rank_ic.csv", index=False)
    spread.to_csv(output_dir / "diagnostics_top_bottom_spread.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_diagnostics.csv", index=False)
    selection_log.to_csv(output_dir / "sector_selection_log.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    comparison = _e004_comparison_frame(None)
    portfolio_metrics: dict[str, dict[str, Any]] | None = None
    if passed:
        filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=costs,
                segments=segments,
                rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        zero_result = _e003_zero_cost_result(
            panel,
            calendar,
            filtered_candidates,
            quarterly_log,
            segments,
            weighted=True,
        )
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        portfolio_dir = output_dir / "portfolio"
        portfolio_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, portfolio_dir / "config.yaml")
        _write_json(portfolio_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), portfolio_dir / "trades.csv")
        _write_ticker_safe_csv(_e004_signals(filtered_candidates), portfolio_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(portfolio_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            portfolio_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            portfolio_dir / "subperiod_breakdown.csv",
            index=False,
        )
        comparison = _e004_comparison_frame(portfolio_metrics)
    comparison.to_csv(output_dir / "comparison_with_e003.csv", index=False)
    _write_e004_flow_report(output_dir, config, rank_ic, spread, subperiod, passed, portfolio_metrics, comparison)


def _e004_panel_with_sector_columns(panel: pd.DataFrame, stock_sector_daily: pd.DataFrame) -> pd.DataFrame:
    sector = stock_sector_daily.loc[:, ["date", "ticker", "sector_code", "sector_name"]].copy()
    sector["날짜"] = pd.to_datetime(sector["date"], errors="raise").dt.normalize()
    sector["종목코드"] = sector["ticker"].astype("string").str.zfill(6)
    sector["sector_code"] = sector["sector_code"].astype("string").str.zfill(2)
    sector["sector_name"] = sector["sector_name"].astype("string")
    data = panel.copy()
    data["종목코드"] = data["종목코드"].astype("string").str.zfill(6)
    return data.merge(
        sector.loc[:, ["날짜", "종목코드", "sector_code", "sector_name"]],
        on=["날짜", "종목코드"],
        how="left",
        validate="many_to_one",
    )


def _e004_filter_sector_daily_to_period(sector_daily: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    data = sector_daily.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()
    start = pd.Timestamp(config["period"]["start"]).normalize()
    end = pd.Timestamp(config["period"]["end"]).normalize()
    excluded_years = {int(year) for year in config["period"]["exclude_calendar_years"]}
    data = data.loc[data["date"].between(start, end)].copy()
    if excluded_years:
        data = data.loc[~data["date"].dt.year.isin(excluded_years)].copy()
    return data


def _e004_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "sector_flow_score"]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals["sector_flow_score"], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _e004_comparison_frame(portfolio_metrics: dict[str, dict[str, Any]] | None) -> pd.DataFrame:
    rows = []
    e003_path = Path("reports/experiments/E003_layer2_baselines/A_d013_replication/metrics.json")
    if e003_path.exists():
        e003 = json.loads(e003_path.read_text(encoding="utf-8"))
        block = e003["factor_macro_gate_mcap"]
        rows.append(
            {
                "variant": "E003_A_d013_replication",
                "cumulative_net_total_return": block.get("cumulative_net_total_return"),
                "sharpe": block.get("sharpe"),
                "max_drawdown": block.get("max_drawdown"),
                "trade_count": block.get("trade_count"),
            }
        )
    if portfolio_metrics is not None:
        block = portfolio_metrics["factor_macro_gate_mcap"]
        rows.append(
            {
                "variant": "E004_flow_top3",
                "cumulative_net_total_return": block.get("cumulative_net_total_return"),
                "sharpe": block.get("sharpe"),
                "max_drawdown": block.get("max_drawdown"),
                "trade_count": block.get("trade_count"),
            }
        )
    return pd.DataFrame(rows, columns=["variant", "cumulative_net_total_return", "sharpe", "max_drawdown", "trade_count"])


def _write_e004_flow_report(
    output_dir: Path,
    config: dict[str, Any],
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
    subperiod: pd.DataFrame,
    passed: bool,
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    comparison: pd.DataFrame,
) -> None:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    verdict = "PASS" if passed else "FAIL"
    lines = [
        "# E004 Flow Score Only Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_aggregate_csv: {config['sector_aggregate_csv']}",
        "- score: z-score across sectors of average(flow_by_value_20d, flow_by_mcap_60d)",
        "- timing: signal quarter-end T uses sector data through T; execution is T+1 or later",
        "- thin_sector_policy: n_stocks <= 2 excluded from score and Top-K selection",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
        "## Diagnostic Verdict",
        "",
        f"- verdict: {verdict}",
        f"- rank_ic_mean: {rank_summary['rank_ic']}",
        f"- rank_ic_std: {rank_summary.get('rank_ic_std', float('nan'))}",
        f"- rank_ic_t_stat: {rank_summary.get('rank_ic_t_stat', float('nan'))}",
        f"- top_bottom_spread_mean: {spread_summary['spread']}",
        f"- top_bottom_spread_std: {spread_summary.get('spread_std', float('nan'))}",
        f"- top_bottom_spread_t_stat: {spread_summary.get('spread_t_stat', float('nan'))}",
        f"- positive_spread_ratio: {spread_summary.get('positive_spread_ratio', float('nan'))}",
        "",
    ]
    lines.extend(_b004_dataframe_table("Subperiod Diagnostics", subperiod))
    lines.extend(_b004_dataframe_table("Comparison With E003", comparison))
    if portfolio_metrics is None:
        lines.extend(["## Portfolio", "", "Portfolio skipped because the pre-registered diagnostic pass rule was not met.", ""])
    else:
        portfolio = pd.DataFrame(
            [
                {
                    "variant": "E004_flow_top3",
                    "cumulative_net_total_return": portfolio_metrics["factor_macro_gate_mcap"]["cumulative_net_total_return"],
                    "sharpe": portfolio_metrics["factor_macro_gate_mcap"]["sharpe"],
                    "max_drawdown": portfolio_metrics["factor_macro_gate_mcap"]["max_drawdown"],
                    "trade_count": portfolio_metrics["factor_macro_gate_mcap"]["trade_count"],
                }
            ]
        )
        lines.extend(_b004_dataframe_table("Portfolio Metrics", portfolio))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e005_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    stock_sector_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    panel = _e004_panel_with_sector_columns(panel, stock_sector_daily)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)

    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    forward_returns = build_rs_sector_forward_returns(sector_daily, rs_scores["signal_date"].drop_duplicates())
    rank_ic = build_rs_rank_ic_diagnostics(rs_scores, forward_returns)
    spread = build_rs_top_bottom_spread_diagnostics(
        rs_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    subperiod = build_rs_subperiod_diagnostics(rank_ic, spread)
    passed = rs_diagnostics_pass(rank_ic, spread)

    costs = _costs_from_config(config["costs"])
    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    candidates = build_e005_rs_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        rs_scores=rs_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
    )
    selection_log = build_e005_sector_selection_log(candidates, rs_scores)

    rank_ic.to_csv(output_dir / "diagnostics_rank_ic.csv", index=False)
    spread.to_csv(output_dir / "diagnostics_top_bottom_spread.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_diagnostics.csv", index=False)
    selection_log.to_csv(output_dir / "sector_selection_log.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    comparison = _e005_comparison_frame(None, rank_ic, spread)
    portfolio_metrics: dict[str, dict[str, Any]] | None = None
    if passed:
        filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=costs,
                segments=segments,
                rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        zero_result = _e003_zero_cost_result(
            panel,
            calendar,
            filtered_candidates,
            quarterly_log,
            segments,
            weighted=True,
        )
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        portfolio_dir = output_dir / "portfolio"
        portfolio_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, portfolio_dir / "config.yaml")
        _write_json(portfolio_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), portfolio_dir / "trades.csv")
        _write_ticker_safe_csv(_e005_signals(filtered_candidates), portfolio_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(portfolio_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            portfolio_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            portfolio_dir / "subperiod_breakdown.csv",
            index=False,
        )
        comparison = _e005_comparison_frame(portfolio_metrics, rank_ic, spread)
    comparison.to_csv(output_dir / "comparison_with_e003_e004.csv", index=False)
    _write_e005_rs_report(output_dir, config, rank_ic, spread, subperiod, passed, portfolio_metrics, comparison)


def _e005_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "sector_rs_score"]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals["sector_rs_score"], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _e005_comparison_frame(
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "variant",
        "verdict",
        "rank_ic_mean",
        "spread_t_stat",
        "cumulative_net_total_return",
        "sharpe",
        "max_drawdown",
        "trade_count",
    ]
    rows = []
    e003_path = Path("reports/experiments/E003_layer2_baselines/A_d013_replication/metrics.json")
    if e003_path.exists():
        e003 = json.loads(e003_path.read_text(encoding="utf-8"))
        block = e003["factor_macro_gate_mcap"]
        rows.append(
            {
                "variant": "E003_A_d013_replication",
                "verdict": "BASELINE",
                "rank_ic_mean": pd.NA,
                "spread_t_stat": pd.NA,
                "cumulative_net_total_return": block.get("cumulative_net_total_return"),
                "sharpe": block.get("sharpe"),
                "max_drawdown": block.get("max_drawdown"),
                "trade_count": block.get("trade_count"),
            }
        )

    e004_rank = _summary_metric_from_csv(Path("reports/experiments/E004_flow_score_only/diagnostics_rank_ic.csv"), "rank_ic")
    e004_spread_t = _summary_metric_from_csv(
        Path("reports/experiments/E004_flow_score_only/diagnostics_top_bottom_spread.csv"), "spread_t_stat"
    )
    rows.append(
        {
            "variant": "E004_flow_top3",
            "verdict": "FAIL",
            "rank_ic_mean": e004_rank,
            "spread_t_stat": e004_spread_t,
            "cumulative_net_total_return": pd.NA,
            "sharpe": pd.NA,
            "max_drawdown": pd.NA,
            "trade_count": pd.NA,
        }
    )

    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    portfolio_block = portfolio_metrics["factor_macro_gate_mcap"] if portfolio_metrics is not None else {}
    rows.append(
        {
            "variant": "E005_rs_top3",
            "verdict": "PASS" if portfolio_metrics is not None else "FAIL",
            "rank_ic_mean": rank_summary["rank_ic"],
            "spread_t_stat": spread_summary["spread_t_stat"],
            "cumulative_net_total_return": portfolio_block.get("cumulative_net_total_return", pd.NA),
            "sharpe": portfolio_block.get("sharpe", pd.NA),
            "max_drawdown": portfolio_block.get("max_drawdown", pd.NA),
            "trade_count": portfolio_block.get("trade_count", pd.NA),
        }
    )
    return pd.DataFrame(rows, columns=columns)


def _summary_metric_from_csv(path: Path, column: str) -> object:
    if not path.exists():
        return pd.NA
    data = pd.read_csv(path)
    summary = data.loc[data["signal_date"].astype(str).eq("ALL")]
    if summary.empty or column not in summary.columns:
        return pd.NA
    return float(summary.iloc[0][column])


def _write_e005_rs_report(
    output_dir: Path,
    config: dict[str, Any],
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
    subperiod: pd.DataFrame,
    passed: bool,
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    comparison: pd.DataFrame,
) -> None:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    verdict = "PASS" if passed else "FAIL"
    lines = [
        "# E005 Relative Strength Only Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_aggregate_csv: {config['sector_aggregate_csv']}",
        f"- kospi_baseline_csv: {config['market_breadth_csv']}",
        "- score: z-score across sectors of average(sector_rel_ret_20d, sector_rel_ret_60d)",
        "- timing: signal quarter-end T uses sector and KOSPI data through T; execution is T+1 or later",
        "- thin_sector_policy: n_stocks <= 2 excluded from score and Top-K selection",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
        "## Diagnostic Verdict",
        "",
        f"- verdict: {verdict}",
        f"- rank_ic_mean: {rank_summary['rank_ic']}",
        f"- rank_ic_std: {rank_summary.get('rank_ic_std', float('nan'))}",
        f"- rank_ic_t_stat: {rank_summary.get('rank_ic_t_stat', float('nan'))}",
        f"- top_bottom_spread_mean: {spread_summary['spread']}",
        f"- top_bottom_spread_std: {spread_summary.get('spread_std', float('nan'))}",
        f"- top_bottom_spread_t_stat: {spread_summary.get('spread_t_stat', float('nan'))}",
        f"- positive_spread_ratio: {spread_summary.get('positive_spread_ratio', float('nan'))}",
        "",
    ]
    lines.extend(_b004_dataframe_table("Subperiod Diagnostics", subperiod))
    lines.extend(_b004_dataframe_table("Comparison With E003/E004", comparison))
    if portfolio_metrics is None:
        lines.extend(["## Portfolio", "", "Portfolio skipped because the pre-registered diagnostic pass rule was not met.", ""])
    else:
        portfolio = pd.DataFrame(
            [
                {
                    "variant": "E005_rs_top3",
                    "cumulative_net_total_return": portfolio_metrics["factor_macro_gate_mcap"]["cumulative_net_total_return"],
                    "sharpe": portfolio_metrics["factor_macro_gate_mcap"]["sharpe"],
                    "max_drawdown": portfolio_metrics["factor_macro_gate_mcap"]["max_drawdown"],
                    "trade_count": portfolio_metrics["factor_macro_gate_mcap"]["trade_count"],
                }
            ]
        )
        lines.extend(_b004_dataframe_table("Portfolio Metrics", portfolio))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e006_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)

    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    combined_scores = build_sector_combined_scores(flow_scores, rs_scores)
    forward_returns = build_combined_sector_forward_returns(
        sector_daily,
        combined_scores["signal_date"].drop_duplicates(),
    )
    rank_ic = build_combined_rank_ic_diagnostics(combined_scores, forward_returns)
    spread = build_combined_top_bottom_spread_diagnostics(
        combined_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    subperiod = build_combined_subperiod_diagnostics(rank_ic, spread)
    passed = combined_diagnostics_pass(rank_ic, spread)

    costs = _costs_from_config(config["costs"])
    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    candidates = build_e006_flow_plus_rs_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
    )
    selection_log = build_e006_sector_selection_log(candidates, combined_scores)

    combined_scores.to_csv(output_dir / "sector_combined_scores.csv", index=False)
    rank_ic.to_csv(output_dir / "diagnostics_rank_ic.csv", index=False)
    spread.to_csv(output_dir / "diagnostics_top_bottom_spread.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_diagnostics.csv", index=False)
    selection_log.to_csv(output_dir / "sector_selection_log.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    comparison = _e006_comparison_frame(None, rank_ic, spread)
    portfolio_metrics: dict[str, dict[str, Any]] | None = None
    if passed:
        filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=costs,
                segments=segments,
                rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        zero_result = _e003_zero_cost_result(
            panel,
            calendar,
            filtered_candidates,
            quarterly_log,
            segments,
            weighted=True,
        )
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        portfolio_dir = output_dir / "portfolio"
        portfolio_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, portfolio_dir / "config.yaml")
        _write_json(portfolio_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), portfolio_dir / "trades.csv")
        _write_ticker_safe_csv(_e006_signals(filtered_candidates), portfolio_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(portfolio_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            portfolio_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            portfolio_dir / "subperiod_breakdown.csv",
            index=False,
        )
        comparison = _e006_comparison_frame(portfolio_metrics, rank_ic, spread)
    comparison.to_csv(output_dir / "comparison_with_e003_e004_e005.csv", index=False)
    _write_e006_report(output_dir, config, rank_ic, spread, subperiod, passed, portfolio_metrics, comparison)


def _e006_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "sector_combined_score"]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals["sector_combined_score"], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _e006_comparison_frame(
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    e003_path = Path("reports/experiments/E003_layer2_baselines/A_d013_replication/metrics.json")
    if e003_path.exists():
        e003 = json.loads(e003_path.read_text(encoding="utf-8"))
        block = e003["factor_macro_gate_mcap"]
        rows.append(
            {
                "variant": "E003_A_d013_replication",
                "verdict": "BASELINE",
                "rank_ic_mean": pd.NA,
                "spread_t_stat": pd.NA,
                "cumulative_net_total_return": block.get("cumulative_net_total_return"),
                "sharpe": block.get("sharpe"),
                "max_drawdown": block.get("max_drawdown"),
                "trade_count": block.get("trade_count"),
            }
        )
    rows.append(
        {
            "variant": "E004_flow_top3",
            "verdict": "FAIL",
            "rank_ic_mean": _summary_metric_from_csv(Path("reports/experiments/E004_flow_score_only/diagnostics_rank_ic.csv"), "rank_ic"),
            "spread_t_stat": _summary_metric_from_csv(
                Path("reports/experiments/E004_flow_score_only/diagnostics_top_bottom_spread.csv"), "spread_t_stat"
            ),
            "cumulative_net_total_return": pd.NA,
            "sharpe": pd.NA,
            "max_drawdown": pd.NA,
            "trade_count": pd.NA,
        }
    )
    e005_metrics = _variant_metrics_from_json(
        Path("reports/experiments/E005_relative_strength_only/portfolio/metrics.json"),
        "factor_macro_gate_mcap",
    )
    rows.append(
        {
            "variant": "E005_rs_top3",
            "verdict": "PASS" if e005_metrics else "FAIL",
            "rank_ic_mean": _summary_metric_from_csv(
                Path("reports/experiments/E005_relative_strength_only/diagnostics_rank_ic.csv"), "rank_ic"
            ),
            "spread_t_stat": _summary_metric_from_csv(
                Path("reports/experiments/E005_relative_strength_only/diagnostics_top_bottom_spread.csv"), "spread_t_stat"
            ),
            "cumulative_net_total_return": e005_metrics.get("cumulative_net_total_return", pd.NA),
            "sharpe": e005_metrics.get("sharpe", pd.NA),
            "max_drawdown": e005_metrics.get("max_drawdown", pd.NA),
            "trade_count": e005_metrics.get("trade_count", pd.NA),
        }
    )

    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    portfolio_block = portfolio_metrics["factor_macro_gate_mcap"] if portfolio_metrics is not None else {}
    rows.append(
        {
            "variant": "E006_flow_plus_rs_top3",
            "verdict": "PASS" if portfolio_metrics is not None else "FAIL",
            "rank_ic_mean": rank_summary["rank_ic"],
            "spread_t_stat": spread_summary["spread_t_stat"],
            "cumulative_net_total_return": portfolio_block.get("cumulative_net_total_return", pd.NA),
            "sharpe": portfolio_block.get("sharpe", pd.NA),
            "max_drawdown": portfolio_block.get("max_drawdown", pd.NA),
            "trade_count": portfolio_block.get("trade_count", pd.NA),
        }
    )
    return pd.DataFrame(
        rows,
        columns=[
            "variant",
            "verdict",
            "rank_ic_mean",
            "spread_t_stat",
            "cumulative_net_total_return",
            "sharpe",
            "max_drawdown",
            "trade_count",
        ],
    )


def _variant_metrics_from_json(path: Path, variant: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    block = data.get(variant, {})
    return block if isinstance(block, dict) else {}


def _write_e006_report(
    output_dir: Path,
    config: dict[str, Any],
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
    subperiod: pd.DataFrame,
    passed: bool,
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    comparison: pd.DataFrame,
) -> None:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    verdict = "PASS" if passed else "FAIL"
    lines = [
        "# E006 Flow Plus RS Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_aggregate_csv: {config['sector_aggregate_csv']}",
        f"- sector_mapping_csv: {config['sector_mapping_csv']}",
        f"- kospi_baseline_csv: {config['market_breadth_csv']}",
        "- score: average(Flow Score, RS Score), where each component is already cross-sectional z-scored",
        "- timing: signal quarter-end T uses sector and KOSPI data through T; execution is T+1 or later",
        "- thin_sector_policy: n_stocks <= 2 excluded from component scores and Top-K selection",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
        "## Diagnostic Verdict",
        "",
        f"- verdict: {verdict}",
        f"- rank_ic_mean: {rank_summary['rank_ic']}",
        f"- rank_ic_std: {rank_summary.get('rank_ic_std', float('nan'))}",
        f"- rank_ic_t_stat: {rank_summary.get('rank_ic_t_stat', float('nan'))}",
        f"- top_bottom_spread_mean: {spread_summary['spread']}",
        f"- top_bottom_spread_std: {spread_summary.get('spread_std', float('nan'))}",
        f"- top_bottom_spread_t_stat: {spread_summary.get('spread_t_stat', float('nan'))}",
        f"- positive_spread_ratio: {spread_summary.get('positive_spread_ratio', float('nan'))}",
        "",
    ]
    lines.extend(_b004_dataframe_table("Subperiod Diagnostics", subperiod))
    lines.extend(_b004_dataframe_table("Comparison With E003/E004/E005", comparison))
    if portfolio_metrics is None:
        lines.extend(["## Portfolio", "", "Portfolio skipped because the pre-registered diagnostic pass rule was not met.", ""])
    else:
        portfolio = pd.DataFrame(
            [
                {
                    "variant": "E006_flow_plus_rs_top3",
                    "cumulative_net_total_return": portfolio_metrics["factor_macro_gate_mcap"]["cumulative_net_total_return"],
                    "sharpe": portfolio_metrics["factor_macro_gate_mcap"]["sharpe"],
                    "max_drawdown": portfolio_metrics["factor_macro_gate_mcap"]["max_drawdown"],
                    "trade_count": portfolio_metrics["factor_macro_gate_mcap"]["trade_count"],
                }
            ]
        )
        lines.extend(_b004_dataframe_table("Portfolio Metrics", portfolio))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e007_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)

    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=sector_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    combined_scores = build_sector_combined_scores(flow_scores, rs_scores, breadth_scores)
    forward_returns = build_combined_sector_forward_returns(sector_daily, combined_scores["signal_date"].drop_duplicates())
    rank_ic = build_combined_rank_ic_diagnostics(combined_scores, forward_returns)
    spread = build_combined_top_bottom_spread_diagnostics(
        combined_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    subperiod = build_combined_subperiod_diagnostics(rank_ic, spread)
    passed = combined_diagnostics_pass(rank_ic, spread)

    breadth_rank_ic = build_breadth_rank_ic_diagnostics(breadth_scores, forward_returns)
    breadth_spread = build_breadth_top_bottom_spread_diagnostics(
        breadth_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    breadth_subperiod = build_breadth_subperiod_diagnostics(breadth_rank_ic, breadth_spread)

    costs = _costs_from_config(config["costs"])
    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    candidates = build_e007_flow_rs_breadth_top_sector_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
    )
    selection_log = build_e007_sector_selection_log(candidates, combined_scores)

    breadth_scores.to_csv(output_dir / "breadth_diagnostic.csv", index=False)
    combined_scores.to_csv(output_dir / "sector_combined_scores.csv", index=False)
    rank_ic.to_csv(output_dir / "diagnostics_rank_ic.csv", index=False)
    spread.to_csv(output_dir / "diagnostics_top_bottom_spread.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_diagnostics.csv", index=False)
    breadth_rank_ic.to_csv(output_dir / "diagnostics_breadth_rank_ic.csv", index=False)
    breadth_spread.to_csv(output_dir / "diagnostics_breadth_top_bottom_spread.csv", index=False)
    breadth_subperiod.to_csv(output_dir / "subperiod_breadth_diagnostics.csv", index=False)
    selection_log.to_csv(output_dir / "sector_selection_log.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    comparison = _e007_comparison_frame(None, rank_ic, spread)
    portfolio_metrics: dict[str, dict[str, Any]] | None = None
    if passed:
        filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=costs,
                segments=segments,
                rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        zero_result = _e003_zero_cost_result(
            panel,
            calendar,
            filtered_candidates,
            quarterly_log,
            segments,
            weighted=True,
        )
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        portfolio_dir = output_dir / "portfolio"
        portfolio_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, portfolio_dir / "config.yaml")
        _write_json(portfolio_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), portfolio_dir / "trades.csv")
        _write_ticker_safe_csv(_e007_signals(filtered_candidates), portfolio_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(portfolio_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            portfolio_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            portfolio_dir / "subperiod_breakdown.csv",
            index=False,
        )
        comparison = _e007_comparison_frame(portfolio_metrics, rank_ic, spread)
    comparison.to_csv(output_dir / "comparison_with_all_e.csv", index=False)
    _write_e007_report(
        output_dir,
        config,
        rank_ic,
        spread,
        subperiod,
        breadth_rank_ic,
        breadth_spread,
        breadth_subperiod,
        passed,
        portfolio_metrics,
        comparison,
    )


def _e007_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "sector_combined_score"]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals["sector_combined_score"], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _e007_comparison_frame(
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    e003_path = Path("reports/experiments/E003_layer2_baselines/A_d013_replication/metrics.json")
    if e003_path.exists():
        e003 = json.loads(e003_path.read_text(encoding="utf-8"))
        block = e003["factor_macro_gate_mcap"]
        rows.append(
            {
                "variant": "E003_A_d013_replication",
                "verdict": "BASELINE",
                "rank_ic_mean": pd.NA,
                "spread_t_stat": pd.NA,
                "cumulative_net_total_return": block.get("cumulative_net_total_return"),
                "sharpe": block.get("sharpe"),
                "max_drawdown": block.get("max_drawdown"),
                "trade_count": block.get("trade_count"),
            }
        )
    for variant, report_dir, expected_pass in (
        ("E004_flow_top3", Path("reports/experiments/E004_flow_score_only"), False),
        ("E005_rs_top3", Path("reports/experiments/E005_relative_strength_only"), True),
        ("E006_flow_plus_rs_top3", Path("reports/experiments/E006_flow_plus_rs"), True),
    ):
        metrics = _variant_metrics_from_json(report_dir / "portfolio" / "metrics.json", "factor_macro_gate_mcap")
        rows.append(
            {
                "variant": variant,
                "verdict": "PASS" if metrics else ("PASS" if expected_pass and metrics else "FAIL"),
                "rank_ic_mean": _summary_metric_from_csv(report_dir / "diagnostics_rank_ic.csv", "rank_ic"),
                "spread_t_stat": _summary_metric_from_csv(report_dir / "diagnostics_top_bottom_spread.csv", "spread_t_stat"),
                "cumulative_net_total_return": metrics.get("cumulative_net_total_return", pd.NA),
                "sharpe": metrics.get("sharpe", pd.NA),
                "max_drawdown": metrics.get("max_drawdown", pd.NA),
                "trade_count": metrics.get("trade_count", pd.NA),
            }
        )
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    portfolio_block = portfolio_metrics["factor_macro_gate_mcap"] if portfolio_metrics is not None else {}
    rows.append(
        {
            "variant": "E007_flow_rs_breadth_top3",
            "verdict": "PASS" if portfolio_metrics is not None else "FAIL",
            "rank_ic_mean": rank_summary["rank_ic"],
            "spread_t_stat": spread_summary["spread_t_stat"],
            "cumulative_net_total_return": portfolio_block.get("cumulative_net_total_return", pd.NA),
            "sharpe": portfolio_block.get("sharpe", pd.NA),
            "max_drawdown": portfolio_block.get("max_drawdown", pd.NA),
            "trade_count": portfolio_block.get("trade_count", pd.NA),
        }
    )
    return pd.DataFrame(
        rows,
        columns=[
            "variant",
            "verdict",
            "rank_ic_mean",
            "spread_t_stat",
            "cumulative_net_total_return",
            "sharpe",
            "max_drawdown",
            "trade_count",
        ],
    )


def _write_e007_report(
    output_dir: Path,
    config: dict[str, Any],
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
    subperiod: pd.DataFrame,
    breadth_rank_ic: pd.DataFrame,
    breadth_spread: pd.DataFrame,
    breadth_subperiod: pd.DataFrame,
    passed: bool,
    portfolio_metrics: dict[str, dict[str, Any]] | None,
    comparison: pd.DataFrame,
) -> None:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    breadth_rank_summary = breadth_rank_ic.loc[breadth_rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    breadth_spread_summary = breadth_spread.loc[breadth_spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    verdict = "PASS" if passed else "FAIL"
    lines = [
        "# E007 Flow RS Breadth Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_aggregate_csv: {config['sector_aggregate_csv']}",
        f"- stock_sector_daily_csv: {config['stock_sector_daily_csv']}",
        f"- sector_mapping_csv: {config['sector_mapping_csv']}",
        f"- kospi_baseline_csv: {config['market_breadth_csv']}",
        "- breadth_score: z-score across sectors of strict breadth, the share of stocks with positive 20-day foreign net buy "
        "and positive 20-day relative return versus KOSPI",
        "- combined_score: average(Flow Score, RS Score, Breadth Score), requiring all three component scores to be "
        "valid",
        "- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later",
        "- thin_sector_policy: n_stocks <= 2 excluded from breadth, combined score, and Top-K selection",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
        "## Breadth Standalone Diagnostic",
        "",
        f"- rank_ic_mean: {breadth_rank_summary['rank_ic']}",
        f"- rank_ic_std: {breadth_rank_summary.get('rank_ic_std', float('nan'))}",
        f"- rank_ic_t_stat: {breadth_rank_summary.get('rank_ic_t_stat', float('nan'))}",
        f"- top_bottom_spread_mean: {breadth_spread_summary['spread']}",
        f"- top_bottom_spread_t_stat: {breadth_spread_summary.get('spread_t_stat', float('nan'))}",
        "",
        "## Combined Diagnostic Verdict",
        "",
        f"- verdict: {verdict}",
        f"- rank_ic_mean: {rank_summary['rank_ic']}",
        f"- rank_ic_std: {rank_summary.get('rank_ic_std', float('nan'))}",
        f"- rank_ic_t_stat: {rank_summary.get('rank_ic_t_stat', float('nan'))}",
        f"- top_bottom_spread_mean: {spread_summary['spread']}",
        f"- top_bottom_spread_std: {spread_summary.get('spread_std', float('nan'))}",
        f"- top_bottom_spread_t_stat: {spread_summary.get('spread_t_stat', float('nan'))}",
        f"- positive_spread_ratio: {spread_summary.get('positive_spread_ratio', float('nan'))}",
        "",
    ]
    lines.extend(_b004_dataframe_table("Combined Subperiod Diagnostics", subperiod))
    lines.extend(_b004_dataframe_table("Breadth Subperiod Diagnostics", breadth_subperiod))
    lines.extend(_b004_dataframe_table("Comparison With All E", comparison))
    if portfolio_metrics is None:
        lines.extend(["## Portfolio", "", "Portfolio skipped because the pre-registered diagnostic pass rule was not met.", ""])
    else:
        portfolio = pd.DataFrame(
            [
                {
                    "variant": "E007_flow_rs_breadth_top3",
                    "cumulative_net_total_return": portfolio_metrics["factor_macro_gate_mcap"]["cumulative_net_total_return"],
                    "sharpe": portfolio_metrics["factor_macro_gate_mcap"]["sharpe"],
                    "max_drawdown": portfolio_metrics["factor_macro_gate_mcap"]["max_drawdown"],
                    "trade_count": portfolio_metrics["factor_macro_gate_mcap"]["trade_count"],
                }
            ]
        )
        lines.extend(_b004_dataframe_table("Portfolio Metrics", portfolio))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e008_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)

    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=sector_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    combined_scores = build_sector_combined_scores(flow_scores, rs_scores, breadth_scores)
    forward_returns = build_combined_sector_forward_returns(sector_daily, combined_scores["signal_date"].drop_duplicates())
    rank_ic = build_combined_rank_ic_diagnostics(combined_scores, forward_returns)
    spread = build_combined_top_bottom_spread_diagnostics(
        combined_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    subperiod = build_combined_subperiod_diagnostics(rank_ic, spread)
    passed = combined_diagnostics_pass(rank_ic, spread)
    breadth_rank_ic = build_breadth_rank_ic_diagnostics(breadth_scores, forward_returns)
    breadth_spread = build_breadth_top_bottom_spread_diagnostics(
        breadth_scores,
        forward_returns,
        k=int(config["diagnostics"]["top_bottom_k"]),
    )
    breadth_subperiod = build_breadth_subperiod_diagnostics(breadth_rank_ic, breadth_spread)

    costs = _costs_from_config(config["costs"])
    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    top_sector_counts_grid = tuple(
        tuple(int(value) for value in counts) for counts in config["selection"]["top_sector_stock_counts_grid"]
    )
    candidates_by_k = build_e008_topk_grid_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
        top_sector_counts_grid=top_sector_counts_grid,
    )

    breadth_scores.to_csv(output_dir / "breadth_diagnostic.csv", index=False)
    combined_scores.to_csv(output_dir / "sector_combined_scores.csv", index=False)
    rank_ic.to_csv(output_dir / "diagnostics_rank_ic.csv", index=False)
    spread.to_csv(output_dir / "diagnostics_top_bottom_spread.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_diagnostics.csv", index=False)
    breadth_rank_ic.to_csv(output_dir / "diagnostics_breadth_rank_ic.csv", index=False)
    breadth_spread.to_csv(output_dir / "diagnostics_breadth_top_bottom_spread.csv", index=False)
    breadth_subperiod.to_csv(output_dir / "subperiod_breadth_diagnostics.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    summary_rows: list[dict[str, Any]] = []
    metrics_by_k: dict[str, dict[str, dict[str, Any]]] = {}
    for counts in top_sector_counts_grid:
        label = topk_label(counts)
        top_dir = output_dir / label
        top_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(config_path, top_dir / "config.yaml")
        candidates = candidates_by_k[label]
        build_e008_sector_selection_log(candidates, combined_scores).to_csv(top_dir / "sector_selection_log.csv", index=False)

        if not passed:
            _write_json(top_dir / "metrics.json", {})
            _write_ticker_safe_csv(_e007_signals(candidates.iloc[0:0]), top_dir / "signals.csv")
            pd.DataFrame().to_csv(top_dir / "trades.csv", index=False)
            pd.DataFrame().to_csv(top_dir / "equity_curve.csv", index=False)
            summary_rows.append(_e008_grid_summary_row(len(counts), counts, None))
            continue

        filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=costs,
                segments=segments,
                rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        zero_result = _e003_zero_cost_result(panel, calendar, filtered_candidates, quarterly_log, segments, weighted=True)
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        metrics_by_k[label] = portfolio_metrics
        _write_json(top_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), top_dir / "trades.csv")
        _write_ticker_safe_csv(_e007_signals(filtered_candidates), top_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(top_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            top_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            top_dir / "subperiod_breakdown.csv",
            index=False,
        )
        summary_rows.append(_e008_grid_summary_row(len(counts), counts, portfolio_metrics))

    grid_summary = pd.DataFrame(summary_rows).sort_values("top_k").reset_index(drop=True)
    grid_summary["e007_exact_reproduction"] = False
    if "top_3" in metrics_by_k:
        grid_summary.loc[grid_summary["top_k"].eq(3), "e007_exact_reproduction"] = _e008_matches_e007(
            metrics_by_k["top_3"]
        )
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    _write_e008_report(
        output_dir,
        config,
        rank_ic,
        spread,
        subperiod,
        breadth_rank_ic,
        breadth_spread,
        breadth_subperiod,
        passed,
        grid_summary,
    )


def _e008_grid_summary_row(
    top_k: int,
    counts: tuple[int, ...],
    portfolio_metrics: dict[str, dict[str, Any]] | None,
) -> dict[str, Any]:
    block = portfolio_metrics["factor_macro_gate_mcap"] if portfolio_metrics is not None else {}
    return {
        "top_k": top_k,
        "top_sector_stock_counts": "/".join(str(value) for value in counts),
        "cumulative_net_total_return": block.get("cumulative_net_total_return", pd.NA),
        "sharpe": block.get("sharpe", pd.NA),
        "max_drawdown": block.get("max_drawdown", pd.NA),
        "trade_count": block.get("trade_count", pd.NA),
    }


def _e008_matches_e007(portfolio_metrics: dict[str, dict[str, Any]]) -> bool:
    e007_path = Path("reports/experiments/E007_flow_rs_breadth/portfolio/metrics.json")
    if not e007_path.exists():
        return False
    e007_metrics = json.loads(e007_path.read_text(encoding="utf-8"))
    current = portfolio_metrics.get("factor_macro_gate_mcap", {})
    expected = e007_metrics.get("factor_macro_gate_mcap", {})
    keys = ("cumulative_net_total_return", "sharpe", "max_drawdown", "trade_count")
    return all(current.get(key) == expected.get(key) for key in keys)


def _e008_robustness_verdict(grid_summary: pd.DataFrame) -> str:
    numeric = grid_summary.copy()
    numeric["cumulative_net_total_return"] = pd.to_numeric(numeric["cumulative_net_total_return"], errors="coerce")
    numeric["sharpe"] = pd.to_numeric(numeric["sharpe"], errors="coerce")
    robust = numeric["sharpe"].ge(0.40) & numeric["cumulative_net_total_return"].ge(1.50)
    robust_count = int(robust.sum())
    top3_robust = bool(robust.loc[numeric["top_k"].eq(3)].any())
    other_sharpe_max = numeric.loc[~numeric["top_k"].eq(3), "sharpe"].max()
    if robust_count >= 3:
        return "튼튼한 안정 구간"
    if top3_robust and pd.notna(other_sharpe_max) and float(other_sharpe_max) < 0.30:
        return "절벽 - 과최적화 의심"
    return "어중간"


def _write_e008_report(
    output_dir: Path,
    config: dict[str, Any],
    rank_ic: pd.DataFrame,
    spread: pd.DataFrame,
    subperiod: pd.DataFrame,
    breadth_rank_ic: pd.DataFrame,
    breadth_spread: pd.DataFrame,
    breadth_subperiod: pd.DataFrame,
    passed: bool,
    grid_summary: pd.DataFrame,
) -> None:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    spread_summary = spread.loc[spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    breadth_rank_summary = breadth_rank_ic.loc[breadth_rank_ic["signal_date"].astype(str).eq("ALL")].iloc[0]
    breadth_spread_summary = breadth_spread.loc[breadth_spread["signal_date"].astype(str).eq("ALL")].iloc[0]
    e003 = _variant_metrics_from_json(
        Path("reports/experiments/E003_layer2_baselines/A_d013_replication/metrics.json"),
        "factor_macro_gate_mcap",
    )
    e003_compare = pd.DataFrame(
        [
            {
                "variant": "E003_A_d013_replication",
                "cumulative_net_total_return": e003.get("cumulative_net_total_return", pd.NA),
                "sharpe": e003.get("sharpe", pd.NA),
                "max_drawdown": e003.get("max_drawdown", pd.NA),
                "trade_count": e003.get("trade_count", pd.NA),
            }
        ]
    )
    lines = [
        "# E008 Top-K Robustness Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        f"- sector_aggregate_csv: {config['sector_aggregate_csv']}",
        f"- stock_sector_daily_csv: {config['stock_sector_daily_csv']}",
        f"- sector_mapping_csv: {config['sector_mapping_csv']}",
        f"- top_sector_stock_counts_grid: {config['selection']['top_sector_stock_counts_grid']}",
        "- carrier: E007 Flow + RS + Breadth score",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later",
        "",
        "## Combined Diagnostic Verdict",
        "",
        f"- verdict: {'PASS' if passed else 'FAIL'}",
        f"- rank_ic_mean: {rank_summary['rank_ic']}",
        f"- top_bottom_spread_t_stat: {spread_summary.get('spread_t_stat', float('nan'))}",
        "",
        "## Breadth Standalone Diagnostic",
        "",
        f"- rank_ic_mean: {breadth_rank_summary['rank_ic']}",
        f"- top_bottom_spread_t_stat: {breadth_spread_summary.get('spread_t_stat', float('nan'))}",
        "",
    ]
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("E003-A Baseline", e003_compare))
    lines.extend(_b004_dataframe_table("Combined Subperiod Diagnostics", subperiod))
    lines.extend(_b004_dataframe_table("Breadth Subperiod Diagnostics", breadth_subperiod))
    lines.extend(
        [
            "## Robustness Verdict",
            "",
            f"- verdict: {_e008_robustness_verdict(grid_summary)}",
            f"- E007 K=3 exact reproduction: {bool(grid_summary.loc[grid_summary['top_k'].eq(3), 'e007_exact_reproduction'].any())}",
            "",
        ]
    )
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e009_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)

    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=sector_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    combined_scores = build_sector_combined_scores(flow_scores, rs_scores, breadth_scores)

    segments = _b011_segments(config)
    candidate_years = _b011_candidate_years(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    sector_mapping = pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    candidates = build_e009_cost_stress_candidates(
        panel=panel,
        universe=universe,
        quarterly_regime=quarterly_log,
        combined_scores=combined_scores,
        sector_mapping=sector_mapping,
        calendar=calendar,
    )
    filtered_candidates = _quarterly_execution_candidates(candidates, calendar, quarterly_log, segments)
    rebalance_dates = quarterly_execution_dates(calendar, quarterly_log, segments)
    zero_result = _e003_zero_cost_result(panel, calendar, filtered_candidates, quarterly_log, segments, weighted=True)

    summary_rows: list[dict[str, Any]] = []
    metrics_by_scenario: dict[str, dict[str, dict[str, Any]]] = {}
    for scenario in E009_SCENARIO_ORDER:
        scenario_config = dict(config)
        scenario_config["costs"] = dict(config["cost_scenarios"][scenario])
        scenario_config["output_dir"] = str(output_dir / scenario)
        scenario_dir = output_dir / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        _write_json(scenario_dir / "config.yaml", scenario_config)

        runs = {
            "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
                panel=panel,
                calendar=calendar,
                candidates=filtered_candidates,
                costs=_costs_from_config(config["cost_scenarios"][scenario]),
                segments=segments,
                rebalance_dates=rebalance_dates,
            ),
            "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
            "cash": _run_segmented_cash(calendar=calendar, segments=segments),
        }
        portfolio_metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
        metrics_by_scenario[scenario] = portfolio_metrics
        _write_json(scenario_dir / "metrics.json", portfolio_metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), scenario_dir / "trades.csv")
        _write_ticker_safe_csv(_e007_signals(filtered_candidates), scenario_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(scenario_dir / "equity_curve.csv", index=False)
        _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years).to_csv(
            scenario_dir / "quarterly_year_breakdown.csv",
            index=False,
        )
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar).to_csv(
            scenario_dir / "subperiod_breakdown.csv",
            index=False,
        )
        block = portfolio_metrics["factor_macro_gate_mcap"]
        summary_rows.append(
            {
                "scenario": scenario,
                "commission_bps": float(config["cost_scenarios"][scenario]["commission_bps"]),
                "tax_bps_sell": float(config["cost_scenarios"][scenario]["tax_bps_sell"]),
                "slippage_bps": float(config["cost_scenarios"][scenario]["slippage_bps"]),
                "cumulative_net_total_return": block["cumulative_net_total_return"],
                "sharpe": block["sharpe"],
                "max_drawdown": block["max_drawdown"],
                "trade_count": block["trade_count"],
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary["base_exact_e007_reproduction"] = False
    summary.loc[summary["scenario"].eq("base"), "base_exact_e007_reproduction"] = _e009_base_matches_e007(
        metrics_by_scenario["base"]
    )
    summary.to_csv(output_dir / "cost_stress_summary.csv", index=False)
    _write_e009_report(output_dir, config, summary)


def _e009_base_matches_e007(portfolio_metrics: dict[str, dict[str, Any]]) -> bool:
    e007_path = Path("reports/experiments/E007_flow_rs_breadth/portfolio/metrics.json")
    if not e007_path.exists():
        return False
    e007_metrics = json.loads(e007_path.read_text(encoding="utf-8"))
    current = portfolio_metrics.get("factor_macro_gate_mcap", {})
    expected = e007_metrics.get("factor_macro_gate_mcap", {})
    keys = ("cumulative_net_total_return", "sharpe", "max_drawdown", "trade_count")
    return all(current.get(key) == expected.get(key) for key in keys)


def _write_e009_report(output_dir: Path, config: dict[str, Any], summary: pd.DataFrame) -> None:
    d018 = pd.DataFrame()
    d018_path = Path("reports/experiments/D018_d013_cost_stress/cost_stress_summary.csv")
    if d018_path.exists():
        d018 = pd.read_csv(d018_path)
    three_x = summary.loc[summary["scenario"].eq("3x")].iloc[0]
    lines = [
        "# E009 Cost Stress Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: E007 Flow + RS + Breadth, Top 3 sectors, holdings 2/2/1",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later",
        "",
    ]
    lines.extend(_b004_dataframe_table("Cost Stress Summary", summary))
    if not d018.empty:
        comparison = d018.loc[d018["scenario"].isin(["base", "3x"]), ["scenario", "net_cum", "sharpe", "max_drawdown"]].copy()
        comparison = comparison.rename(
            columns={
                "net_cum": "d018_d013_cumulative_net_total_return",
                "sharpe": "d018_d013_sharpe",
                "max_drawdown": "d018_d013_max_drawdown",
            }
        )
        lines.extend(_b004_dataframe_table("D018 D013 Comparison", comparison))
    lines.extend(
        [
            "## Verdict Checks",
            "",
            f"- base_exact_e007_reproduction: {bool(summary.loc[summary['scenario'].eq('base'), 'base_exact_e007_reproduction'].iloc[0])}",
            f"- 3x cumulative_net_total_return >= 0: {bool(float(three_x['cumulative_net_total_return']) >= 0.0)}",
            f"- 3x sharpe >= 0.20: {bool(float(three_x['sharpe']) >= 0.20)}",
            "",
        ]
    )
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_e011_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_e_layer2_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    candidates = build_e011_top4_champion_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )
    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs, metrics, zero_result = _run_e_layer2_portfolio(
        panel=context["panel"],
        calendar=context["calendar"],
        market_breadth=context["market_breadth"],
        candidates=filtered,
        quarterly_log=context["quarterly_log"],
        costs=costs,
        segments=context["segments"],
        candidate_years=context["candidate_years"],
    )
    summary = _e011_summary(metrics)
    summary["e008_top4_exact_reproduction"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/E008_topk_robustness/top_4/metrics.json"),
    )
    summary["e007_exact_match"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/E007_flow_rs_breadth/portfolio/metrics.json"),
    )
    summary["d013_exact_match"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/D013_d009_threshold_minus_0p2/metrics.json"),
    )
    comparison = _e014_comparison(metrics)

    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_e007_signals(filtered), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        output_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        output_dir / "subperiod_breakdown.csv", index=False
    )
    build_e008_sector_selection_log(filtered, context["combined_scores"]).to_csv(
        output_dir / "sector_selection_log.csv", index=False
    )
    context["quarterly_log"].to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    summary.to_csv(output_dir / "champion_summary.csv", index=False)
    _write_e011_report(output_dir, config, summary)


def run_e012_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_e_layer2_context(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    score_candidates = build_e012_score_ablation_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )
    topk_candidates = build_e012_topk_grid_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )

    base_costs = _costs_from_config(config["cost_scenarios"]["base"])
    score_rows = []
    score_metrics: dict[str, dict[str, dict[str, Any]]] = {}
    for score_name in E012_SCORE_ABLATIONS:
        metrics = _write_e012_variant_run(
            output_dir=output_dir / "score_ablation" / score_name,
            config=config,
            context=context,
            candidates=score_candidates[score_name],
            costs=base_costs,
        )
        score_metrics[score_name] = metrics
        score_rows.append(_summary_row(score_name, metrics))
    score_summary = pd.DataFrame(score_rows)
    score_summary["c_exact_e011"] = False
    score_summary.loc[score_summary["variant"].eq("flow_rs_breadth"), "c_exact_e011"] = _metrics_match_path(
        score_metrics["flow_rs_breadth"],
        Path("reports/experiments/E011_top4_champion_registration/metrics.json"),
    )

    topk_rows = []
    for counts in E012_TOPK_GRID:
        label = e012_topk_summary_label(counts)
        metrics = _write_e012_variant_run(
            output_dir=output_dir / "topk_grid" / label,
            config=config,
            context=context,
            candidates=topk_candidates[label],
            costs=base_costs,
        )
        row = _summary_row(label, metrics)
        row["top_k"] = len(counts)
        row["top_sector_stock_counts"] = "/".join(str(value) for value in counts)
        topk_rows.append(row)
    topk_summary = pd.DataFrame(topk_rows).sort_values("top_k").reset_index(drop=True)

    cost_rows = []
    top4 = score_candidates["flow_rs_breadth"]
    for scenario in E009_SCENARIO_ORDER:
        metrics = _write_e012_variant_run(
            output_dir=output_dir / "cost_stress" / scenario,
            config=config,
            context=context,
            candidates=top4,
            costs=_costs_from_config(config["cost_scenarios"][scenario]),
        )
        row = _summary_row(scenario, metrics)
        row.update(config["cost_scenarios"][scenario])
        cost_rows.append(row)
    cost_summary = pd.DataFrame(cost_rows)

    score_summary.to_csv(output_dir / "score_ablation_summary.csv", index=False)
    topk_summary.to_csv(output_dir / "topk_grid_summary.csv", index=False)
    cost_summary.to_csv(output_dir / "cost_stress_summary.csv", index=False)
    _write_e012_report(output_dir, config, score_summary, topk_summary, cost_summary)


def run_e013_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_e_layer2_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    candidates = build_e013_top4_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )
    subperiod_rows: list[dict[str, Any]] = []
    per_year_frames: list[pd.DataFrame] = []
    full_result: BacktestResult | None = None
    full_filtered = pd.DataFrame()

    for subperiod in config["subperiods"]:
        name = str(subperiod["name"])
        start = pd.Timestamp(subperiod["start"]).normalize()
        end = pd.Timestamp(subperiod["end"]).normalize()
        segments = e013_segments_for_trading_window(
            segments=context["segments"],
            trading_start=start,
            trading_end=end,
        )
        filtered = _quarterly_execution_candidates(candidates, context["calendar"], context["quarterly_log"], segments)
        runs, metrics, zero_result = _run_e_layer2_portfolio(
            panel=context["panel"],
            calendar=context["calendar"],
            market_breadth=context["market_breadth"],
            candidates=filtered,
            quarterly_log=context["quarterly_log"],
            costs=costs,
            segments=segments,
            candidate_years=_d008_candidate_years(start, end, config["period"]["exclude_calendar_years"]),
        )
        subperiod_dir = output_dir / name
        subperiod_dir.mkdir(parents=True, exist_ok=True)
        subperiod_config = _d008_config_for_subperiod(config, subperiod)
        (subperiod_dir / "config.yaml").write_text(
            yaml.safe_dump(subperiod_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(subperiod_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), subperiod_dir / "trades.csv")
        _write_ticker_safe_csv(_e007_signals(filtered), subperiod_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(subperiod_dir / "equity_curve.csv", index=False)
        year_breakdown = _d009_year_breakdown(
            runs=runs,
            calendar=context["calendar"],
            candidate_years=_d008_candidate_years(start, end, config["period"]["exclude_calendar_years"]),
        )
        year_breakdown.to_csv(subperiod_dir / "quarterly_year_breakdown.csv", index=False)
        _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
            subperiod_dir / "subperiod_breakdown.csv", index=False
        )
        context["quarterly_log"].to_csv(subperiod_dir / "quarterly_regime_log.csv", index=False)
        per_year = subperiod_year_breakdown(
            runs["factor_macro_gate_mcap"],
            context["calendar"],
            years=_d008_candidate_years(start, end, config["period"]["exclude_calendar_years"]),
        )
        per_year.insert(0, "subperiod", name)
        per_year_frames.append(per_year)
        subperiod_rows.append(
            subperiod_metrics_row(
                name=name,
                start=start,
                end=end,
                net_result=runs["factor_macro_gate_mcap"],
                cost_0_result=zero_result,
                calendar=context["calendar"],
                positive_years=int(metrics["factor_macro_gate_mcap"]["positive_years"]),
            )
        )
        if name == "full":
            full_result = runs["factor_macro_gate_mcap"]
            full_filtered = filtered

    if full_result is None:
        raise ValueError("E013 requires a subperiod named 'full'.")
    subperiod_table = pd.DataFrame(subperiod_rows)
    per_year_breakdown = pd.concat(per_year_frames, ignore_index=True)
    full_years = _d008_candidate_years(
        pd.Timestamp(config["subperiods"][0]["start"]),
        pd.Timestamp(config["subperiods"][0]["end"]),
        config["period"]["exclude_calendar_years"],
    )
    rolling = rolling_year_sharpe(
        full_result,
        context["calendar"],
        start_year=min(year for year in full_years if year >= 2015),
        end_year=max(full_years),
        window_years=3,
    )
    full_per_year = per_year_breakdown.loc[per_year_breakdown["subperiod"].eq("full")].copy()
    spike = spike_years(
        full_per_year.loc[:, ["year", "net"]],
        float(subperiod_table.loc[subperiod_table["subperiod"].eq("full"), "net"].iloc[0]),
    )
    contribution = _e013_contribution_tables(full_result, full_filtered, context["calendar"])
    overlap = _e013_d013_overlap(full_filtered)

    subperiod_table["full_exact_e011"] = False
    subperiod_table.loc[subperiod_table["subperiod"].eq("full"), "full_exact_e011"] = _metrics_match_path(
        json.loads((output_dir / "full" / "metrics.json").read_text(encoding="utf-8")),
        Path("reports/experiments/E011_top4_champion_registration/metrics.json"),
    )
    subperiod_table.to_csv(output_dir / "subperiod_table.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    rolling.to_csv(output_dir / "rolling_3yr_sharpe.csv", index=False)
    spike.to_csv(output_dir / "spike_year_contribution.csv", index=False)
    contribution["year"].to_csv(output_dir / "year_contribution.csv", index=False)
    contribution["sector"].to_csv(output_dir / "sector_contribution.csv", index=False)
    overlap.to_csv(output_dir / "d013_overlap_quarterly.csv", index=False)
    _write_e013_report(output_dir, config, subperiod_table, per_year_breakdown, spike, contribution, overlap)


def run_e014_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_e_layer2_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    candidates = build_e014_rs_breadth_top4_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )
    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs, metrics, zero_result = _run_e_layer2_portfolio(
        panel=context["panel"],
        calendar=context["calendar"],
        market_breadth=context["market_breadth"],
        candidates=filtered,
        quarterly_log=context["quarterly_log"],
        costs=costs,
        segments=context["segments"],
        candidate_years=context["candidate_years"],
    )
    summary = pd.DataFrame([_summary_row("E014_rs_breadth_top4", metrics)])
    summary["e012_rs_breadth_exact_reproduction"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/E012_top4_robustness_ablation/score_ablation/rs_breadth/metrics.json"),
    )
    summary["e011_exact_match"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/E011_top4_champion_registration/metrics.json"),
    )
    summary["d013_exact_match"] = _metrics_match_path(
        metrics,
        Path("reports/experiments/D013_d009_threshold_minus_0p2/metrics.json"),
    )

    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_e007_signals(filtered), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        output_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        output_dir / "subperiod_breakdown.csv", index=False
    )
    build_e008_sector_selection_log(filtered, rs_breadth_score_view(context["combined_scores"])).to_csv(
        output_dir / "sector_selection_log.csv", index=False
    )
    context["quarterly_log"].to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    summary.to_csv(output_dir / "champion_summary.csv", index=False)
    comparison = _e014_comparison(metrics)
    comparison.to_csv(output_dir / "comparison_with_d013_e011.csv", index=False)
    _write_e014_report(output_dir, config, summary, comparison)


def run_f002_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_f002_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    carrier = str(config["carrier"])
    carrier_dir = output_dir / ("A_d013_direct" if carrier == "d013_direct" else "B_e014")
    carrier_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, carrier_dir / "config.yaml")

    if carrier == "d013_direct":
        candidate_builder = build_f002_stock_rs_d013_direct_candidates
        candidates = candidate_builder(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_n=int(config["selection"]["n"]),
        )
        diagnostic_scores = build_f002_d013_direct_score_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_rs_score_universe"
        ic_mode = "universe"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = False
        carrier_label = "F002-A D013 direct"
    elif carrier == "e014":
        candidates = build_f002_stock_rs_e014_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores = build_f002_e014_selection_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_rs_score"
        ic_mode = "within_sector"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = True
        carrier_label = "F002-B E014"
    else:
        raise ValueError("F002 carrier must be 'd013_direct' or 'e014'.")

    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs = {
        "factor_macro_gate_mcap": (
            run_weighted_quarterly_basket_backtest
            if weighted
            else run_quarterly_mcap_backtest
        )(
            panel=context["panel"],
            calendar=context["calendar"],
            candidates=filtered,
            costs=costs,
            segments=context["segments"],
            rebalance_dates=quarterly_execution_dates(context["calendar"], context["quarterly_log"], context["segments"]),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            context["market_breadth"], calendar=context["calendar"], segments=context["segments"]
        ),
        "cash": _run_segmented_cash(calendar=context["calendar"], segments=context["segments"]),
    }
    zero_result = _e003_zero_cost_result(
        context["panel"], context["calendar"], filtered, context["quarterly_log"], context["segments"], weighted=weighted
    )
    metrics = _e003_variant_metrics(runs, zero_result, context["calendar"], context["candidate_years"])
    rank_ic = build_stock_rank_ic_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
    )
    spread = build_stock_top_bottom_spread_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
        k=spread_k,
    )
    diagnostics = _f002_diagnostics_frame(carrier_label, rank_ic, spread)

    _write_json(carrier_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), carrier_dir / "trades.csv")
    _write_ticker_safe_csv(_f002_signals(filtered, score_column=score_column), carrier_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(carrier_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        carrier_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        carrier_dir / "subperiod_breakdown.csv", index=False
    )
    rank_ic.to_csv(carrier_dir / "rank_ic.csv", index=False)
    spread.to_csv(carrier_dir / "top_bottom_spread.csv", index=False)
    diagnostics.to_csv(carrier_dir / "diagnostics_summary.csv", index=False)
    context["quarterly_log"].to_csv(carrier_dir / "quarterly_regime_log.csv", index=False)
    _write_f002_root_outputs(output_dir, config)


def _build_f002_context(config: dict[str, Any]) -> dict[str, Any]:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)
    signal_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=signal_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=signal_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=signal_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    stock_scores = build_stock_rs_scores(
        stock_daily,
        sector_daily,
        signal_dates=signal_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_sector_stocks=int(config["selection"].get("min_sector_stocks", 2)),
    )
    return {
        "panel": panel,
        "calendar": calendar,
        "universe": universe,
        "market_breadth": market_breadth,
        "quarterly_log": quarterly_log,
        "combined_scores": build_sector_combined_scores(flow_scores, rs_scores, breadth_scores),
        "stock_scores": stock_scores,
        "forward_returns": build_stock_forward_returns(stock_daily, signal_dates),
        "segments": _b011_segments(config),
        "candidate_years": _b011_candidate_years(config),
    }


def run_f003_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_f003_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    carrier = str(config["carrier"])
    carrier_dir = output_dir / ("A_d013_direct" if carrier == "d013_direct" else "B_e014")
    carrier_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, carrier_dir / "config.yaml")

    if carrier == "d013_direct":
        candidates = build_f003_foreign_flow_d013_direct_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_n=int(config["selection"]["n"]),
        )
        diagnostic_scores = build_f003_d013_direct_score_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_foreign_flow_score_universe"
        ic_mode = "universe"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = False
        carrier_label = "F003-A D013 direct"
    elif carrier == "e014":
        candidates = build_f003_foreign_flow_e014_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores = build_f003_e014_selection_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_foreign_flow_score"
        ic_mode = "within_sector"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = True
        carrier_label = "F003-B E014"
    else:
        raise ValueError("F003 carrier must be 'd013_direct' or 'e014'.")

    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs = {
        "factor_macro_gate_mcap": (
            run_weighted_quarterly_basket_backtest
            if weighted
            else run_quarterly_mcap_backtest
        )(
            panel=context["panel"],
            calendar=context["calendar"],
            candidates=filtered,
            costs=costs,
            segments=context["segments"],
            rebalance_dates=quarterly_execution_dates(context["calendar"], context["quarterly_log"], context["segments"]),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            context["market_breadth"], calendar=context["calendar"], segments=context["segments"]
        ),
        "cash": _run_segmented_cash(calendar=context["calendar"], segments=context["segments"]),
    }
    zero_result = _e003_zero_cost_result(
        context["panel"], context["calendar"], filtered, context["quarterly_log"], context["segments"], weighted=weighted
    )
    metrics = _e003_variant_metrics(runs, zero_result, context["calendar"], context["candidate_years"])
    rank_ic = build_stock_rank_ic_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
    )
    spread = build_stock_top_bottom_spread_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
        k=spread_k,
    )
    diagnostics = _f002_diagnostics_frame(carrier_label, rank_ic, spread)

    _write_json(carrier_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), carrier_dir / "trades.csv")
    _write_ticker_safe_csv(_f002_signals(filtered, score_column=score_column), carrier_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(carrier_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        carrier_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        carrier_dir / "subperiod_breakdown.csv", index=False
    )
    rank_ic.to_csv(carrier_dir / "rank_ic.csv", index=False)
    spread.to_csv(carrier_dir / "top_bottom_spread.csv", index=False)
    diagnostics.to_csv(carrier_dir / "diagnostics_summary.csv", index=False)
    context["quarterly_log"].to_csv(carrier_dir / "quarterly_regime_log.csv", index=False)
    _write_f003_root_outputs(output_dir, config)


def _build_f003_context(config: dict[str, Any]) -> dict[str, Any]:
    context = _build_f002_context_without_stock_scores(config)
    context["stock_scores"] = build_stock_foreign_flow_scores(
        context["stock_daily"],
        signal_dates=context["signal_dates"],
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_sector_stocks=int(config["selection"].get("min_sector_stocks", 2)),
    )
    context["forward_returns"] = build_stock_forward_returns(context["stock_daily"], context["signal_dates"])
    return context


def run_f004_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_f004_context(config)
    costs = _costs_from_config(config["costs"])
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    carrier = str(config["carrier"])
    carrier_dir = output_dir / ("A_d013_direct" if carrier == "d013_direct" else "B_e014")
    carrier_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, carrier_dir / "config.yaml")

    if carrier == "d013_direct":
        candidates = build_f004_institution_flow_d013_direct_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_n=int(config["selection"]["n"]),
        )
        diagnostic_scores = build_f004_d013_direct_score_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            stock_scores=context["stock_scores"],
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_institution_flow_score_universe"
        ic_mode = "universe"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = False
        carrier_label = "F004-A D013 direct"
    elif carrier == "e014":
        candidates = build_f004_institution_flow_e014_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            calendar=context["calendar"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores = build_f004_e014_selection_universe(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            stock_scores=context["stock_scores"],
            top_sector_counts=tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]),
        )
        diagnostic_scores["ticker"] = diagnostic_scores["종목코드"].astype(str).str.zfill(6)
        score_column = "stock_institution_flow_score"
        ic_mode = "within_sector"
        spread_k = int(config["diagnostics"]["top_bottom_k"])
        weighted = True
        carrier_label = "F004-B E014"
    else:
        raise ValueError("F004 carrier must be 'd013_direct' or 'e014'.")

    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs = {
        "factor_macro_gate_mcap": (
            run_weighted_quarterly_basket_backtest
            if weighted
            else run_quarterly_mcap_backtest
        )(
            panel=context["panel"],
            calendar=context["calendar"],
            candidates=filtered,
            costs=costs,
            segments=context["segments"],
            rebalance_dates=quarterly_execution_dates(context["calendar"], context["quarterly_log"], context["segments"]),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(
            context["market_breadth"], calendar=context["calendar"], segments=context["segments"]
        ),
        "cash": _run_segmented_cash(calendar=context["calendar"], segments=context["segments"]),
    }
    zero_result = _e003_zero_cost_result(
        context["panel"], context["calendar"], filtered, context["quarterly_log"], context["segments"], weighted=weighted
    )
    metrics = _e003_variant_metrics(runs, zero_result, context["calendar"], context["candidate_years"])
    rank_ic = build_stock_rank_ic_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
    )
    spread = build_stock_top_bottom_spread_diagnostics(
        diagnostic_scores,
        context["forward_returns"],
        score_column=score_column,
        mode=ic_mode,
        k=spread_k,
    )
    diagnostics = _f002_diagnostics_frame(carrier_label, rank_ic, spread)

    _write_json(carrier_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), carrier_dir / "trades.csv")
    _write_ticker_safe_csv(_f002_signals(filtered, score_column=score_column), carrier_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(carrier_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        carrier_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        carrier_dir / "subperiod_breakdown.csv", index=False
    )
    rank_ic.to_csv(carrier_dir / "rank_ic.csv", index=False)
    spread.to_csv(carrier_dir / "top_bottom_spread.csv", index=False)
    diagnostics.to_csv(carrier_dir / "diagnostics_summary.csv", index=False)
    context["quarterly_log"].to_csv(carrier_dir / "quarterly_regime_log.csv", index=False)
    _write_f004_root_outputs(output_dir, config)


def _build_f004_context(config: dict[str, Any]) -> dict[str, Any]:
    context = _build_f002_context_without_stock_scores(config)
    context["stock_scores"] = build_stock_institution_flow_scores(
        context["stock_daily"],
        signal_dates=context["signal_dates"],
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_sector_stocks=int(config["selection"].get("min_sector_stocks", 2)),
    )
    context["forward_returns"] = build_stock_forward_returns(context["stock_daily"], context["signal_dates"])
    return context


def _build_f002_context_without_stock_scores(config: dict[str, Any]) -> dict[str, Any]:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)
    signal_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=signal_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=signal_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=signal_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"].get("min_sector_stocks", 3)),
    )
    return {
        "panel": panel,
        "calendar": calendar,
        "universe": universe,
        "market_breadth": market_breadth,
        "quarterly_log": quarterly_log,
        "combined_scores": build_sector_combined_scores(flow_scores, rs_scores, breadth_scores),
        "stock_daily": stock_daily,
        "sector_daily": sector_daily,
        "signal_dates": signal_dates,
        "segments": _b011_segments(config),
        "candidate_years": _b011_candidate_years(config),
    }


def run_e015_experiment(config: dict[str, Any], config_path: Path) -> None:
    context = _build_e_layer2_context(config)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    base_candidates = build_e015_validation_candidates(
        panel=context["panel"],
        universe=context["universe"],
        quarterly_regime=context["quarterly_log"],
        combined_scores=context["combined_scores"],
        sector_mapping=context["sector_mapping"],
        calendar=context["calendar"],
    )
    filtered = _quarterly_execution_candidates(
        base_candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    base_runs, base_metrics, zero_result = _run_e_layer2_portfolio(
        panel=context["panel"],
        calendar=context["calendar"],
        market_breadth=context["market_breadth"],
        candidates=filtered,
        quarterly_log=context["quarterly_log"],
        costs=_costs_from_config(config["cost_scenarios"]["base"]),
        segments=context["segments"],
        candidate_years=context["candidate_years"],
    )
    _write_json(output_dir / "metrics.json", base_metrics)
    _write_ticker_safe_csv(_b011_trades(base_runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_e007_signals(filtered), output_dir / "signals.csv")
    _d001_wide_equity_curve(base_runs).to_csv(output_dir / "equity_curve.csv", index=False)
    _c010_subperiod_breakdown(base_runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        output_dir / "subperiod_breakdown.csv", index=False
    )
    context["quarterly_log"].to_csv(output_dir / "quarterly_regime_log.csv", index=False)

    cost_summary = _e015_cost_stress(config, context, filtered)
    topk_stability = _e015_topk_stability(config, context)
    subperiod_table = _e015_subperiod_table(config, context, base_candidates)
    spike_exclusion = _e015_spike_exclusion(config, context, base_candidates)
    contribution = _e015_contribution_tables(base_runs["factor_macro_gate_mcap"], filtered, context["calendar"])
    d013_overlap = _e015_overlap(filtered, Path("reports/experiments/D013_d009_threshold_minus_0p2/signals.csv"), "d013")
    e011_overlap = _e015_overlap(filtered, Path("reports/experiments/E011_top4_champion_registration/signals.csv"), "e011")
    mdd = _e015_mdd_attribution(base_runs["factor_macro_gate_mcap"], filtered, context["calendar"])
    pass_fail = _e015_pass_fail(base_metrics, cost_summary, topk_stability, spike_exclusion, contribution)

    cost_summary.to_csv(output_dir / "cost_stress_summary.csv", index=False)
    topk_stability.to_csv(output_dir / "topk_stability.csv", index=False)
    subperiod_table.to_csv(output_dir / "subperiod_table.csv", index=False)
    spike_exclusion.to_csv(output_dir / "spike_exclusion.csv", index=False)
    contribution["year"].to_csv(output_dir / "year_contribution.csv", index=False)
    contribution["sector"].to_csv(output_dir / "sector_contribution.csv", index=False)
    contribution["stock"].to_csv(output_dir / "stock_contribution.csv", index=False)
    contribution["rebalance"].to_csv(output_dir / "rebalance_contribution.csv", index=False)
    d013_overlap.to_csv(output_dir / "d013_overlap.csv", index=False)
    e011_overlap.to_csv(output_dir / "e011_overlap.csv", index=False)
    mdd["summary"].to_csv(output_dir / "mdd_summary.csv", index=False)
    _write_ticker_safe_csv(mdd["trades"], output_dir / "mdd_trades.csv")
    pass_fail.to_csv(output_dir / "pass_fail.csv", index=False)
    _write_e015_mdd_markdown(output_dir, mdd)
    _write_e015_finding_log(output_dir, topk_stability)
    _write_e015_report(
        output_dir,
        config,
        pass_fail,
        cost_summary,
        topk_stability,
        subperiod_table,
        spike_exclusion,
        contribution,
        d013_overlap,
        e011_overlap,
        mdd,
    )


def _e015_cost_stress(config: dict[str, Any], context: dict[str, Any], filtered: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario in E009_SCENARIO_ORDER:
        _, metrics, _ = _run_e_layer2_portfolio(
            panel=context["panel"],
            calendar=context["calendar"],
            market_breadth=context["market_breadth"],
            candidates=filtered,
            quarterly_log=context["quarterly_log"],
            costs=_costs_from_config(config["cost_scenarios"][scenario]),
            segments=context["segments"],
            candidate_years=context["candidate_years"],
        )
        row = _summary_row(scenario, metrics)
        row.update(config["cost_scenarios"][scenario])
        rows.append(row)
    return pd.DataFrame(rows)


def _e015_topk_stability(config: dict[str, Any], context: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for counts in E015_TOPK_STABILITY_GRID:
        candidates = build_e015_validation_candidates(
            panel=context["panel"],
            universe=context["universe"],
            quarterly_regime=context["quarterly_log"],
            combined_scores=context["combined_scores"],
            sector_mapping=context["sector_mapping"],
            calendar=context["calendar"],
            top_sector_counts=counts,
        )
        filtered = _quarterly_execution_candidates(
            candidates, context["calendar"], context["quarterly_log"], context["segments"]
        )
        _, metrics, _ = _run_e_layer2_portfolio(
            panel=context["panel"],
            calendar=context["calendar"],
            market_breadth=context["market_breadth"],
            candidates=filtered,
            quarterly_log=context["quarterly_log"],
            costs=_costs_from_config(config["cost_scenarios"]["base"]),
            segments=context["segments"],
            candidate_years=context["candidate_years"],
        )
        row = _summary_row(e015_topk_label(counts), metrics)
        row["top_k"] = len(counts)
        row["top_sector_stock_counts"] = "/".join(str(value) for value in counts)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("top_k").reset_index(drop=True)


def _e015_subperiod_table(config: dict[str, Any], context: dict[str, Any], candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for subperiod in config["subperiods"]:
        name = str(subperiod["name"])
        start = pd.Timestamp(subperiod["start"]).normalize()
        end = pd.Timestamp(subperiod["end"]).normalize()
        segments = e015_segments_for_trading_window(
            segments=context["segments"],
            trading_start=start,
            trading_end=end,
        )
        filtered = _quarterly_execution_candidates(candidates, context["calendar"], context["quarterly_log"], segments)
        runs, metrics, zero_result = _run_e_layer2_portfolio(
            panel=context["panel"],
            calendar=context["calendar"],
            market_breadth=context["market_breadth"],
            candidates=filtered,
            quarterly_log=context["quarterly_log"],
            costs=_costs_from_config(config["cost_scenarios"]["base"]),
            segments=segments,
            candidate_years=_d008_candidate_years(start, end, config["period"]["exclude_calendar_years"]),
        )
        rows.append(
            subperiod_metrics_row(
                name=name,
                start=start,
                end=end,
                net_result=runs["factor_macro_gate_mcap"],
                cost_0_result=zero_result,
                calendar=context["calendar"],
                positive_years=int(metrics["factor_macro_gate_mcap"]["positive_years"]),
            )
        )
    return pd.DataFrame(rows)


def _e015_spike_exclusion(config: dict[str, Any], context: dict[str, Any], candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_excluded = [int(year) for year in config["period"]["exclude_calendar_years"]]
    for years in E015_SPIKE_EXCLUSION_GROUPS:
        excluded = sorted(set(base_excluded).union(years))
        scenario_config = dict(config)
        scenario_config["period"] = dict(config["period"])
        scenario_config["period"]["exclude_calendar_years"] = excluded
        segments = _b011_segments(scenario_config)
        candidate_years = _b011_candidate_years(scenario_config)
        filtered = _quarterly_execution_candidates(candidates, context["calendar"], context["quarterly_log"], segments)
        _, metrics, _ = _run_e_layer2_portfolio(
            panel=context["panel"],
            calendar=context["calendar"],
            market_breadth=context["market_breadth"],
            candidates=filtered,
            quarterly_log=context["quarterly_log"],
            costs=_costs_from_config(config["cost_scenarios"]["base"]),
            segments=segments,
            candidate_years=candidate_years,
        )
        row = _summary_row("+".join(str(year) for year in years), metrics)
        row["excluded_years"] = "+".join(str(year) for year in years)
        rows.append(row)
    return pd.DataFrame(rows)


def _e015_contribution_tables(
    result: BacktestResult,
    candidates: pd.DataFrame,
    calendar: object,
) -> dict[str, pd.DataFrame]:
    trades = _b011_trades(result, calendar)
    if trades.empty or candidates.empty:
        empty = pd.DataFrame(columns=["group", "net_pnl", "trade_count", "contribution_ratio"])
        return {"year": empty, "sector": empty, "stock": empty, "rebalance": empty}
    annotated = trades.merge(
        candidates.loc[:, ["signal_date", "종목코드", "sector_code", "sector_name"]].drop_duplicates(),
        on=["signal_date", "종목코드"],
        how="left",
        validate="many_to_one",
    )
    annotated["net_pnl"] = (
        pd.to_numeric(annotated["shares"], errors="raise")
        * (pd.to_numeric(annotated["exit_price"], errors="raise") - pd.to_numeric(annotated["entry_price"], errors="raise"))
        - pd.to_numeric(annotated["cost_paid"], errors="raise")
    )
    annotated["year"] = pd.to_datetime(annotated["entry_date"], errors="raise").dt.year
    annotated["stock"] = annotated["종목코드"].astype(str).str.zfill(6)
    annotated["rebalance"] = pd.to_datetime(annotated["signal_date"], errors="raise").dt.strftime("%Y-%m-%d")
    positive = float(annotated.loc[annotated["net_pnl"].gt(0), "net_pnl"].sum())
    denominator = positive if positive != 0.0 else float(annotated["net_pnl"].abs().sum())
    return {
        "year": _contribution_group(annotated, "year", denominator),
        "sector": _contribution_group(annotated, "sector_name", denominator),
        "stock": _contribution_group(annotated, "stock", denominator),
        "rebalance": _contribution_group(annotated, "rebalance", denominator),
    }


def _e015_overlap(candidates: pd.DataFrame, reference_path: Path, reference_label: str) -> pd.DataFrame:
    columns = [
        "quarter",
        f"{reference_label}_count",
        "e015_count",
        "overlap_count",
        "union_count",
        "jaccard",
        f"{reference_label}_tickers",
        "e015_tickers",
        "overlap_tickers",
    ]
    if candidates.empty or not reference_path.exists():
        return pd.DataFrame(columns=columns)
    reference = pd.read_csv(reference_path, dtype={"ticker": "string", "종목코드": "string"})
    if "ticker" not in reference.columns and "종목코드" in reference.columns:
        reference["ticker"] = reference["종목코드"]
    reference["signal_date"] = pd.to_datetime(reference["signal_date"], errors="raise").dt.normalize()
    current = candidates.loc[:, ["signal_date", "종목코드"]].copy()
    current["signal_date"] = pd.to_datetime(current["signal_date"], errors="raise").dt.normalize()
    current["ticker"] = current["종목코드"].astype(str).str.zfill(6)
    rows = []
    for signal_date in sorted(set(reference["signal_date"]).union(set(current["signal_date"]))):
        ref_set = set(reference.loc[reference["signal_date"].eq(signal_date), "ticker"].astype(str).str.zfill(6))
        cur_set = set(current.loc[current["signal_date"].eq(signal_date), "ticker"].astype(str).str.zfill(6))
        union = ref_set | cur_set
        overlap = ref_set & cur_set
        rows.append(
            {
                "quarter": signal_date,
                f"{reference_label}_count": len(ref_set),
                "e015_count": len(cur_set),
                "overlap_count": len(overlap),
                "union_count": len(union),
                "jaccard": len(overlap) / len(union) if union else 0.0,
                f"{reference_label}_tickers": " ".join(sorted(ref_set)),
                "e015_tickers": " ".join(sorted(cur_set)),
                "overlap_tickers": " ".join(sorted(overlap)),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def _e015_mdd_attribution(
    result: BacktestResult,
    candidates: pd.DataFrame,
    calendar: object,
) -> dict[str, pd.DataFrame]:
    summary = pd.DataFrame([e015_drawdown_summary(result)])
    trades = _b011_trades(result, calendar)
    if not trades.empty:
        peak = pd.Timestamp(summary.loc[0, "peak_date"]).normalize()
        trough = pd.Timestamp(summary.loc[0, "trough_date"]).normalize()
        trades = trades.loc[
            pd.to_datetime(trades["entry_date"], errors="raise").dt.normalize().between(peak, trough)
        ].copy()
        if not trades.empty and not candidates.empty:
            trades = trades.merge(
                candidates.loc[:, ["signal_date", "종목코드", "sector_code", "sector_name"]].drop_duplicates(),
                on=["signal_date", "종목코드"],
                how="left",
                validate="many_to_one",
            )
    return {"summary": summary, "trades": trades}


def _e015_pass_fail(
    metrics: dict[str, dict[str, Any]],
    cost_summary: pd.DataFrame,
    topk_stability: pd.DataFrame,
    spike_exclusion: pd.DataFrame,
    contribution: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    headline = metrics["factor_macro_gate_mcap"]
    three_x = cost_summary.loc[cost_summary["variant"].eq("3x")].iloc[0]
    spike_all = spike_exclusion.loc[spike_exclusion["excluded_years"].eq("2020+2025+2026")].iloc[0]
    top1_sector = _top_contribution(contribution["sector"])
    top1_stock = _top_contribution(contribution["stock"])
    topk_min_sharpe = float(pd.to_numeric(topk_stability["sharpe"], errors="coerce").min())
    rows = [
        ("cumulative_ge_d013", headline["cumulative_net_total_return"], E015_PASS_THRESHOLDS["cumulative_vs_d013"], float(headline["cumulative_net_total_return"]) >= E015_PASS_THRESHOLDS["cumulative_vs_d013"]),
        ("sharpe_ge_d013", headline["sharpe"], E015_PASS_THRESHOLDS["sharpe_vs_d013"], float(headline["sharpe"]) >= E015_PASS_THRESHOLDS["sharpe_vs_d013"]),
        ("mdd_ge_minus_45pct", headline["max_drawdown"], E015_PASS_THRESHOLDS["max_drawdown_floor"], float(headline["max_drawdown"]) >= E015_PASS_THRESHOLDS["max_drawdown_floor"]),
        (
            "cost_3x_ge_d013_3x",
            three_x["cumulative_net_total_return"],
            f"{E015_PASS_THRESHOLDS['d013_3x_cumulative']} or sharpe {E015_PASS_THRESHOLDS['d013_3x_sharpe']}",
            float(three_x["cumulative_net_total_return"]) >= E015_PASS_THRESHOLDS["d013_3x_cumulative"]
            or float(three_x["sharpe"]) >= E015_PASS_THRESHOLDS["d013_3x_sharpe"],
        ),
        ("spike_excluded_ge_d013", spike_all["cumulative_net_total_return"], E015_PASS_THRESHOLDS["d013_spike_excluded_cumulative"], float(spike_all["cumulative_net_total_return"]) >= E015_PASS_THRESHOLDS["d013_spike_excluded_cumulative"]),
        ("top1_sector_lt_50pct", top1_sector, E015_PASS_THRESHOLDS["top1_sector_contribution_ceiling"], top1_sector < E015_PASS_THRESHOLDS["top1_sector_contribution_ceiling"]),
        ("top1_stock_lt_40pct", top1_stock, E015_PASS_THRESHOLDS["top1_stock_contribution_ceiling"], top1_stock < E015_PASS_THRESHOLDS["top1_stock_contribution_ceiling"]),
        ("topk_all_sharpe_ge_0p40", topk_min_sharpe, E015_PASS_THRESHOLDS["topk_sharpe_floor"], topk_min_sharpe >= E015_PASS_THRESHOLDS["topk_sharpe_floor"]),
    ]
    frame = pd.DataFrame(rows, columns=["criterion", "actual", "threshold", "passed"])
    frame["passed"] = frame["passed"].astype(bool)
    return frame


def _top_contribution(frame: pd.DataFrame) -> float:
    if frame.empty or "contribution_ratio" not in frame.columns:
        return 0.0
    values = pd.to_numeric(frame["contribution_ratio"], errors="coerce").dropna()
    return 0.0 if values.empty else float(values.max())


def _e014_comparison(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = [_summary_row("E014_rs_breadth_top4", metrics)]
    references = (
        ("D013", Path("reports/experiments/D013_d009_threshold_minus_0p2/metrics.json")),
        ("E011", Path("reports/experiments/E011_top4_champion_registration/metrics.json")),
    )
    for label, path in references:
        if not path.exists():
            continue
        loaded = json.loads(path.read_text(encoding="utf-8"))
        rows.append(_summary_row(label, loaded))
    frame = pd.DataFrame(rows)
    if len(frame) > 1:
        base = frame.loc[frame["variant"].eq("E014_rs_breadth_top4")].iloc[0]
        frame["cumulative_diff_vs_e014"] = pd.to_numeric(frame["cumulative_net_total_return"], errors="coerce") - float(
            base["cumulative_net_total_return"]
        )
        frame["sharpe_diff_vs_e014"] = pd.to_numeric(frame["sharpe"], errors="coerce") - float(base["sharpe"])
        frame["mdd_diff_vs_e014"] = pd.to_numeric(frame["max_drawdown"], errors="coerce") - float(base["max_drawdown"])
    return frame


def _build_e_layer2_context(config: dict[str, Any]) -> dict[str, Any]:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    sector_daily = pd.read_csv(config["sector_aggregate_csv"], encoding="utf-8-sig")
    sector_daily = _e004_filter_sector_daily_to_period(sector_daily, config)
    stock_daily = pd.read_csv(config["stock_sector_daily_csv"], encoding="utf-8-sig", dtype={"ticker": "string"})
    stock_daily = _e004_filter_sector_daily_to_period(stock_daily, config)
    sector_dates = rs_quarter_end_dates(sector_daily)
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    flow_scores = build_sector_flow_scores(
        sector_daily,
        signal_dates=sector_dates,
        value_window=int(config["strategy"]["flow_by_value_window"]),
        mcap_window=int(config["strategy"]["flow_by_mcap_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    rs_scores = build_sector_rs_scores(
        sector_daily,
        market_breadth,
        signal_dates=sector_dates,
        short_window=int(config["strategy"]["short_window"]),
        long_window=int(config["strategy"]["long_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    breadth_scores = build_sector_breadth_scores(
        stock_daily,
        market_breadth,
        signal_dates=sector_dates,
        window=int(config["strategy"]["breadth_window"]),
        min_stocks=int(config["selection"]["min_sector_stocks"]),
    )
    return {
        "panel": panel,
        "calendar": calendar,
        "universe": universe,
        "market_breadth": market_breadth,
        "quarterly_log": quarterly_log,
        "combined_scores": build_sector_combined_scores(flow_scores, rs_scores, breadth_scores),
        "sector_mapping": pd.read_csv(config["sector_mapping_csv"], encoding="utf-8-sig", dtype={"ticker": "string"}),
        "segments": _b011_segments(config),
        "candidate_years": _b011_candidate_years(config),
    }


def _run_e_layer2_portfolio(
    *,
    panel: pd.DataFrame,
    calendar: object,
    market_breadth: pd.DataFrame,
    candidates: pd.DataFrame,
    quarterly_log: pd.DataFrame,
    costs: Costs,
    segments: tuple[tuple[object, object], ...],
    candidate_years: tuple[int, ...],
) -> tuple[dict[str, BacktestResult], dict[str, dict[str, Any]], BacktestResult]:
    runs = {
        "factor_macro_gate_mcap": run_weighted_quarterly_basket_backtest(
            panel=panel,
            calendar=calendar,
            candidates=candidates,
            costs=costs,
            segments=segments,
            rebalance_dates=quarterly_execution_dates(calendar, quarterly_log, segments),
        ),
        "kospi_buy_and_hold": build_kospi_buy_and_hold_result(market_breadth, calendar=calendar, segments=segments),
        "cash": _run_segmented_cash(calendar=calendar, segments=segments),
    }
    zero_result = _e003_zero_cost_result(panel, calendar, candidates, quarterly_log, segments, weighted=True)
    metrics = _e003_variant_metrics(runs, zero_result, calendar, candidate_years)
    return runs, metrics, zero_result


def _write_e012_variant_run(
    *,
    output_dir: Path,
    config: dict[str, Any],
    context: dict[str, Any],
    candidates: pd.DataFrame,
    costs: Costs,
) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    filtered = _quarterly_execution_candidates(
        candidates, context["calendar"], context["quarterly_log"], context["segments"]
    )
    runs, metrics, zero_result = _run_e_layer2_portfolio(
        panel=context["panel"],
        calendar=context["calendar"],
        market_breadth=context["market_breadth"],
        candidates=filtered,
        quarterly_log=context["quarterly_log"],
        costs=costs,
        segments=context["segments"],
        candidate_years=context["candidate_years"],
    )
    variant_config = dict(config)
    variant_config["output_dir"] = str(output_dir)
    (output_dir / "config.yaml").write_text(
        yaml.safe_dump(variant_config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], context["calendar"]), output_dir / "trades.csv")
    _write_ticker_safe_csv(_e007_signals(filtered), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    _d009_year_breakdown(runs=runs, calendar=context["calendar"], candidate_years=context["candidate_years"]).to_csv(
        output_dir / "quarterly_year_breakdown.csv", index=False
    )
    _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, context["calendar"]).to_csv(
        output_dir / "subperiod_breakdown.csv", index=False
    )
    return metrics


def _summary_row(variant: str, metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    block = metrics["factor_macro_gate_mcap"]
    return {
        "variant": variant,
        "cumulative_net_total_return": block["cumulative_net_total_return"],
        "sharpe": block["sharpe"],
        "max_drawdown": block["max_drawdown"],
        "trade_count": block["trade_count"],
    }


def _f002_signals(candidates: pd.DataFrame, *, score_column: str) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]
        )
    signals = candidates.loc[:, ["signal_date", "execution_date", "종목코드", score_column]].copy()
    signals["date"] = signals["signal_date"]
    signals["ticker"] = signals["종목코드"].astype(str).str.zfill(6)
    signals["signal_value"] = pd.to_numeric(signals[score_column], errors="raise")
    signals["included_in_trade"] = True
    return signals.loc[:, ["date", "ticker", "signal_value", "signal_date", "execution_date", "included_in_trade"]]


def _f002_diagnostics_frame(carrier: str, rank_ic: pd.DataFrame, spread: pd.DataFrame) -> pd.DataFrame:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].eq("ALL")]
    spread_summary = spread.loc[spread["signal_date"].eq("ALL")]
    row: dict[str, Any] = {"carrier": carrier}
    if not rank_summary.empty:
        rank = rank_summary.iloc[0]
        row.update(
            {
                "rank_ic_pooled": rank.get("rank_ic"),
                "rank_ic_mean": rank.get("rank_ic_mean_quarterly"),
                "rank_ic_t_stat": rank.get("rank_ic_t_stat"),
                "rank_ic_n_quarters": rank.get("n_quarters"),
            }
        )
    if not spread_summary.empty:
        sp = spread_summary.iloc[0]
        row.update(
            {
                "spread": sp.get("spread"),
                "spread_t_stat": sp.get("spread_t_stat"),
                "positive_spread_ratio": sp.get("positive_spread_ratio"),
            }
        )
    return pd.DataFrame([row])


def _write_f002_root_outputs(output_dir: Path, config: dict[str, Any]) -> None:
    rows = []
    diagnostics = []
    for label, dirname, baseline in (
        ("F002-A D013 direct", "A_d013_direct", "F001-A D013 direct"),
        ("F002-B E014", "B_e014", "F001-B E014 neutral"),
    ):
        metrics_path = output_dir / dirname / "metrics.json"
        diag_path = output_dir / dirname / "diagnostics_summary.csv"
        if metrics_path.exists():
            loaded = json.loads(metrics_path.read_text(encoding="utf-8"))
            row = _summary_row(label, loaded)
            row["baseline_variant"] = baseline
            rows.append(row)
        if diag_path.exists():
            diagnostics.append(pd.read_csv(diag_path))
    baseline_path = Path("reports/experiments/F001_layer3_neutral_baseline/baseline_summary.csv")
    if rows and baseline_path.exists():
        baselines = pd.read_csv(baseline_path)
        if "baseline" in baselines.columns:
            baselines = baselines.rename(
                columns={
                    "baseline": "variant",
                    "cum_net": "cumulative_net_total_return",
                    "mdd": "max_drawdown",
                }
            )
        by_name = baselines.set_index("variant")
        for row in rows:
            baseline_name = row["baseline_variant"]
            if baseline_name in by_name.index:
                base = by_name.loc[baseline_name]
                row["baseline_cumulative_net_total_return"] = base["cumulative_net_total_return"]
                row["baseline_sharpe"] = base["sharpe"]
                row["baseline_max_drawdown"] = base["max_drawdown"]
                row["cumulative_uplift_vs_f001"] = row["cumulative_net_total_return"] - base["cumulative_net_total_return"]
                row["sharpe_uplift_vs_f001"] = row["sharpe"] - base["sharpe"]
                row["mdd_uplift_vs_f001"] = row["max_drawdown"] - base["max_drawdown"]
    comparison = pd.DataFrame(rows)
    if not comparison.empty:
        comparison.to_csv(output_dir / "carrier_comparison.csv", index=False)
    if diagnostics:
        pd.concat(diagnostics, ignore_index=True).to_csv(output_dir / "ic_diagnostics.csv", index=False)
    shutil.copyfile(Path(f"configs/backtests/f002_{'a' if config['carrier'] == 'd013_direct' else 'b'}.yaml"), output_dir / "config.yaml")
    _write_f002_report(output_dir, config, comparison, pd.concat(diagnostics, ignore_index=True) if diagnostics else pd.DataFrame())


def _write_f002_report(
    output_dir: Path,
    config: dict[str, Any],
    comparison: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> None:
    lines = [
        "# F002 Stock RS Only Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- stock_rs: stock 20d/60d cumulative return minus sector 20d/60d cumulative return",
        "- timing: signal quarter-end T uses stock and sector returns through T; execution is T+1 or later",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
    ]
    if not diagnostics.empty:
        lines.extend(_b004_dataframe_table("IC Diagnostics", diagnostics))
    if not comparison.empty:
        lines.extend(_b004_dataframe_table("Carrier Comparison", comparison))
    verdict = _f002_verdict(comparison, diagnostics)
    lines.extend(["## Verdict", "", f"- {verdict}", ""])
    output_dir.joinpath("report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _f002_verdict(comparison: pd.DataFrame, diagnostics: pd.DataFrame) -> str:
    if comparison.empty or diagnostics.empty or len(comparison) < 2 or len(diagnostics) < 2:
        return "pending - both carriers have not been generated yet"
    merged = comparison.merge(diagnostics, left_on="variant", right_on="carrier", how="left")
    passed = (
        pd.to_numeric(merged["cumulative_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["sharpe_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["rank_ic_t_stat"], errors="coerce").ge(2.0)
    )
    pass_count = int(passed.sum())
    if pass_count == 2:
        return "통과, F003 진행"
    if pass_count == 1:
        return "weak"
    return "RS 종목 단위 약함"


def _write_f003_root_outputs(output_dir: Path, config: dict[str, Any]) -> None:
    rows = []
    diagnostics = []
    for label, dirname, baseline, f002_variant in (
        ("F003-A D013 direct", "A_d013_direct", "F001-A D013 direct", "F002-A D013 direct"),
        ("F003-B E014", "B_e014", "F001-B E014 neutral", "F002-B E014"),
    ):
        metrics_path = output_dir / dirname / "metrics.json"
        diag_path = output_dir / dirname / "diagnostics_summary.csv"
        if metrics_path.exists():
            loaded = json.loads(metrics_path.read_text(encoding="utf-8"))
            row = _summary_row(label, loaded)
            row["baseline_variant"] = baseline
            row["f002_variant"] = f002_variant
            rows.append(row)
        if diag_path.exists():
            diagnostics.append(pd.read_csv(diag_path))
    baseline_path = Path("reports/experiments/F001_layer3_neutral_baseline/baseline_summary.csv")
    if rows and baseline_path.exists():
        baselines = pd.read_csv(baseline_path)
        if "baseline" in baselines.columns:
            baselines = baselines.rename(
                columns={
                    "baseline": "variant",
                    "cum_net": "cumulative_net_total_return",
                    "mdd": "max_drawdown",
                }
            )
        by_name = baselines.set_index("variant")
        for row in rows:
            baseline_name = row["baseline_variant"]
            if baseline_name in by_name.index:
                base = by_name.loc[baseline_name]
                row["baseline_cumulative_net_total_return"] = base["cumulative_net_total_return"]
                row["baseline_sharpe"] = base["sharpe"]
                row["baseline_max_drawdown"] = base["max_drawdown"]
                row["cumulative_uplift_vs_f001"] = row["cumulative_net_total_return"] - base["cumulative_net_total_return"]
                row["sharpe_uplift_vs_f001"] = row["sharpe"] - base["sharpe"]
                row["mdd_uplift_vs_f001"] = row["max_drawdown"] - base["max_drawdown"]
    f002_path = Path("reports/experiments/F002_stock_rs_only/carrier_comparison.csv")
    if rows and f002_path.exists():
        f002 = pd.read_csv(f002_path).set_index("variant")
        for row in rows:
            f002_variant = row["f002_variant"]
            if f002_variant in f002.index:
                base = f002.loc[f002_variant]
                row["f002_cumulative_net_total_return"] = base["cumulative_net_total_return"]
                row["f002_sharpe"] = base["sharpe"]
                row["f002_max_drawdown"] = base["max_drawdown"]
                row["cumulative_diff_vs_f002"] = row["cumulative_net_total_return"] - base["cumulative_net_total_return"]
                row["sharpe_diff_vs_f002"] = row["sharpe"] - base["sharpe"]
                row["mdd_diff_vs_f002"] = row["max_drawdown"] - base["max_drawdown"]
    comparison = pd.DataFrame(rows)
    if not comparison.empty:
        comparison.to_csv(output_dir / "carrier_comparison.csv", index=False)
    all_diagnostics = pd.concat(diagnostics, ignore_index=True) if diagnostics else pd.DataFrame()
    if not all_diagnostics.empty:
        all_diagnostics.to_csv(output_dir / "ic_diagnostics.csv", index=False)
    shutil.copyfile(Path(f"configs/backtests/f003_{'a' if config['carrier'] == 'd013_direct' else 'b'}.yaml"), output_dir / "config.yaml")
    _write_f003_report(output_dir, config, comparison, all_diagnostics)


def _write_f003_report(
    output_dir: Path,
    config: dict[str, Any],
    comparison: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> None:
    lines = [
        "# F003 Stock Foreign Flow Only Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- stock_foreign_flow: mean of 20d foreign net buy / 20d traded value and 60d foreign net buy / market cap",
        "- zscore: within-sector cross-sectional z-score",
        "- missing_flow_policy: stock-level foreign flow input NaNs are not imputed; affected stocks are excluded from diagnostics and portfolio candidates",
        "- timing: signal quarter-end T uses stock flow, traded value, and market cap through T; execution is T+1 or later",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
    ]
    if not diagnostics.empty:
        lines.extend(_b004_dataframe_table("IC Diagnostics", diagnostics))
    if not comparison.empty:
        lines.extend(_b004_dataframe_table("Carrier Comparison", comparison))
    verdict = _f003_verdict(comparison, diagnostics)
    lines.extend(["## Verdict", "", f"- {verdict}", ""])
    output_dir.joinpath("report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _f003_verdict(comparison: pd.DataFrame, diagnostics: pd.DataFrame) -> str:
    if comparison.empty or diagnostics.empty or len(comparison) < 2 or len(diagnostics) < 2:
        return "pending - both carriers have not been generated yet"
    merged = comparison.merge(diagnostics, left_on="variant", right_on="carrier", how="left")
    passed = (
        pd.to_numeric(merged["cumulative_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["sharpe_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["rank_ic_t_stat"], errors="coerce").ge(2.0)
    )
    pass_count = int(passed.sum())
    if pass_count == 2:
        return "surprise pass"
    if pass_count == 1:
        return "weak"
    return "stock-level Flow 단독 약함"


def _write_f004_root_outputs(output_dir: Path, config: dict[str, Any]) -> None:
    rows = []
    diagnostics = []
    for label, dirname, baseline, f003_variant in (
        ("F004-A D013 direct", "A_d013_direct", "F001-A D013 direct", "F003-A D013 direct"),
        ("F004-B E014", "B_e014", "F001-B E014 neutral", "F003-B E014"),
    ):
        metrics_path = output_dir / dirname / "metrics.json"
        diag_path = output_dir / dirname / "diagnostics_summary.csv"
        if metrics_path.exists():
            loaded = json.loads(metrics_path.read_text(encoding="utf-8"))
            row = _summary_row(label, loaded)
            row["baseline_variant"] = baseline
            row["f003_variant"] = f003_variant
            rows.append(row)
        if diag_path.exists():
            diagnostics.append(pd.read_csv(diag_path))
    baseline_path = Path("reports/experiments/F001_layer3_neutral_baseline/baseline_summary.csv")
    if rows and baseline_path.exists():
        baselines = pd.read_csv(baseline_path)
        if "baseline" in baselines.columns:
            baselines = baselines.rename(
                columns={
                    "baseline": "variant",
                    "cum_net": "cumulative_net_total_return",
                    "mdd": "max_drawdown",
                }
            )
        by_name = baselines.set_index("variant")
        for row in rows:
            baseline_name = row["baseline_variant"]
            if baseline_name in by_name.index:
                base = by_name.loc[baseline_name]
                row["baseline_cumulative_net_total_return"] = base["cumulative_net_total_return"]
                row["baseline_sharpe"] = base["sharpe"]
                row["baseline_max_drawdown"] = base["max_drawdown"]
                row["cumulative_uplift_vs_f001"] = row["cumulative_net_total_return"] - base["cumulative_net_total_return"]
                row["sharpe_uplift_vs_f001"] = row["sharpe"] - base["sharpe"]
                row["mdd_uplift_vs_f001"] = row["max_drawdown"] - base["max_drawdown"]
    f003_path = Path("reports/experiments/F003_foreign_flow_only/carrier_comparison.csv")
    if rows and f003_path.exists():
        f003 = pd.read_csv(f003_path).set_index("variant")
        for row in rows:
            f003_variant = row["f003_variant"]
            if f003_variant in f003.index:
                base = f003.loc[f003_variant]
                row["f003_cumulative_net_total_return"] = base["cumulative_net_total_return"]
                row["f003_sharpe"] = base["sharpe"]
                row["f003_max_drawdown"] = base["max_drawdown"]
                row["cumulative_diff_vs_f003"] = row["cumulative_net_total_return"] - base["cumulative_net_total_return"]
                row["sharpe_diff_vs_f003"] = row["sharpe"] - base["sharpe"]
                row["mdd_diff_vs_f003"] = row["max_drawdown"] - base["max_drawdown"]
    comparison = pd.DataFrame(rows)
    if not comparison.empty:
        comparison.to_csv(output_dir / "carrier_comparison.csv", index=False)
    all_diagnostics = pd.concat(diagnostics, ignore_index=True) if diagnostics else pd.DataFrame()
    if not all_diagnostics.empty:
        all_diagnostics.to_csv(output_dir / "ic_diagnostics.csv", index=False)
    shutil.copyfile(Path(f"configs/backtests/f004_{'a' if config['carrier'] == 'd013_direct' else 'b'}.yaml"), output_dir / "config.yaml")
    _write_f004_report(output_dir, config, comparison, all_diagnostics)


def _write_f004_report(
    output_dir: Path,
    config: dict[str, Any],
    comparison: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> None:
    lines = [
        "# F004 Stock Institution Flow Only Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- stock_institution_flow: mean of 20d institution net buy / 20d traded value and 60d institution net buy / market cap",
        "- zscore: within-sector cross-sectional z-score",
        "- missing_flow_policy: stock-level institution flow input NaNs are not imputed; affected stocks are excluded from diagnostics and portfolio candidates",
        "- missing_flow_rate_note: current stock-sector daily input has institution flow missingness comparable to foreign flow; exact source-panel rate is documented in the ticket",
        "- timing: signal quarter-end T uses stock flow, traded value, and market cap through T; execution is T+1 or later",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "",
    ]
    if not diagnostics.empty:
        lines.extend(_b004_dataframe_table("IC Diagnostics", diagnostics))
    if not comparison.empty:
        lines.extend(_b004_dataframe_table("Carrier Comparison", comparison))
    verdict = _f004_verdict(comparison, diagnostics)
    lines.extend(["## Verdict", "", f"- {verdict}", ""])
    output_dir.joinpath("report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _f004_verdict(comparison: pd.DataFrame, diagnostics: pd.DataFrame) -> str:
    if comparison.empty or diagnostics.empty or len(comparison) < 2 or len(diagnostics) < 2:
        return "pending - both carriers have not been generated yet"
    merged = comparison.merge(diagnostics, left_on="variant", right_on="carrier", how="left")
    passed = (
        pd.to_numeric(merged["cumulative_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["sharpe_uplift_vs_f001"], errors="coerce").gt(0)
        & pd.to_numeric(merged["rank_ic_t_stat"], errors="coerce").ge(2.0)
    )
    pass_count = int(passed.sum())
    if pass_count == 2:
        return "surprise pass"
    if pass_count == 1:
        return "weak"
    return "stock-level institution Flow 단독 약함"


def _e011_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame([_summary_row("E011_top4_champion", metrics)])


def _metrics_match_path(metrics: dict[str, dict[str, Any]], path: Path) -> bool:
    if not path.exists():
        return False
    expected = json.loads(path.read_text(encoding="utf-8"))
    current_block = metrics.get("factor_macro_gate_mcap", {})
    expected_block = expected.get("factor_macro_gate_mcap", {})
    keys = ("cumulative_net_total_return", "sharpe", "max_drawdown", "trade_count")
    return all(current_block.get(key) == expected_block.get(key) for key in keys)


def _write_e011_report(output_dir: Path, config: dict[str, Any], summary: pd.DataFrame) -> None:
    lines = [
        "# E011 Top4 Champion Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: E007 Flow + RS + Breadth, Top 4 sectors, holdings 2/1/1/1",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later",
        "",
    ]
    lines.extend(_b004_dataframe_table("Champion Summary", summary))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_e014_report(output_dir: Path, config: dict[str, Any], summary: pd.DataFrame, comparison: pd.DataFrame) -> None:
    lines = [
        "# E014 RS+Breadth Top4 Registration Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: RS + Breadth score, Flow excluded, Top 4 sectors, holdings 2/1/1/1",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later",
        "",
    ]
    lines.extend(_b004_dataframe_table("Champion Summary", summary))
    lines.extend(_b004_dataframe_table("D013/E011 Comparison", comparison))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_e012_report(
    output_dir: Path,
    config: dict[str, Any],
    score_summary: pd.DataFrame,
    topk_summary: pd.DataFrame,
    cost_summary: pd.DataFrame,
) -> None:
    flow_main_alpha = False
    if {"rs_breadth", "flow_rs_breadth"}.issubset(set(score_summary["variant"])):
        c = float(score_summary.loc[score_summary["variant"].eq("flow_rs_breadth"), "sharpe"].iloc[0])
        b = float(score_summary.loc[score_summary["variant"].eq("rs_breadth"), "sharpe"].iloc[0])
        flow_main_alpha = c > b
    robust_k = int((pd.to_numeric(topk_summary["sharpe"], errors="coerce") >= 0.40).sum())
    lines = [
        "# E012 Top4 Robustness Ablation Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: E011 Top4 unless the table explicitly changes score or Top-K",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- lookback_robustness: skipped",
        "",
    ]
    lines.extend(_b004_dataframe_table("Score Ablation", score_summary))
    lines.extend(["## Pre-Registered Flow Verdict", "", f"- flow_main_alpha: {flow_main_alpha}", ""])
    lines.extend(_b004_dataframe_table("Top-K Grid", topk_summary))
    lines.extend(_b004_dataframe_table("Cost Stress", cost_summary))
    lines.extend(["## Robustness Verdict", "", f"- topk_sharpe_ge_0p40_count: {robust_k}", ""])
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_e015_mdd_markdown(output_dir: Path, mdd: dict[str, pd.DataFrame]) -> None:
    lines = ["# E015 MDD Attribution", ""]
    lines.extend(_b004_dataframe_table("MDD Summary", mdd["summary"]))
    lines.extend(_b004_dataframe_table("Trades During MDD", mdd["trades"]))
    output_dir.joinpath("mdd_attribution.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_e015_finding_log(output_dir: Path, topk_stability: pd.DataFrame) -> None:
    best = topk_stability.sort_values("sharpe", ascending=False).head(1)
    lines = [
        "# E015 Finding Log",
        "",
        "E015 is validation-only. Any stronger adjacent result is recorded here as backlog only and is not adopted.",
        "",
    ]
    if not best.empty and str(best.iloc[0]["variant"]) != "top_4":
        lines.append(
            f"- Top-K adjacent check: {best.iloc[0]['variant']} had the highest Sharpe "
            f"({best.iloc[0]['sharpe']}), but E014 remains frozen at Top 4."
        )
    else:
        lines.append("- No adjacent Top-K finding outranked frozen Top 4 on Sharpe.")
    output_dir.joinpath("finding_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_e015_report(
    output_dir: Path,
    config: dict[str, Any],
    pass_fail: pd.DataFrame,
    cost_summary: pd.DataFrame,
    topk_stability: pd.DataFrame,
    subperiod_table: pd.DataFrame,
    spike_exclusion: pd.DataFrame,
    contribution: dict[str, pd.DataFrame],
    d013_overlap: pd.DataFrame,
    e011_overlap: pd.DataFrame,
    mdd: dict[str, pd.DataFrame],
) -> None:
    verdict = "E014-L2-PROTOTYPE-CHAMPION 동결" if bool(pass_fail["passed"].all()) else "fallback"
    lines = [
        "# E015 RS+Breadth Top4 Validation Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: E014 frozen RS + Breadth Top 4, holdings 2/1/1/1",
        "- validation_only: no new weights, lookbacks, K, allocation, or variables are adopted",
        "",
    ]
    lines.extend(_b004_dataframe_table("Pass/Fail", pass_fail))
    lines.extend(["## Verdict", "", f"- {verdict}", ""])
    lines.extend(_b004_dataframe_table("Cost Stress", cost_summary))
    lines.extend(_b004_dataframe_table("Top-K Stability", topk_stability))
    lines.extend(_b004_dataframe_table("Subperiod Table", subperiod_table))
    lines.extend(_b004_dataframe_table("Spike Exclusion", spike_exclusion))
    lines.extend(_b004_dataframe_table("Year Contribution", contribution["year"]))
    lines.extend(_b004_dataframe_table("Sector Contribution", contribution["sector"]))
    lines.extend(_b004_dataframe_table("Stock Contribution", contribution["stock"].head(20)))
    lines.extend(_b004_dataframe_table("Rebalance Contribution", contribution["rebalance"].head(20)))
    lines.extend(_b004_dataframe_table("D013 Overlap", d013_overlap))
    lines.extend(_b004_dataframe_table("E011 Overlap", e011_overlap))
    lines.extend(_b004_dataframe_table("MDD Summary", mdd["summary"]))
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _e013_contribution_tables(
    result: BacktestResult,
    candidates: pd.DataFrame,
    calendar: object,
) -> dict[str, pd.DataFrame]:
    trades = _b011_trades(result, calendar)
    if trades.empty or candidates.empty:
        empty = pd.DataFrame(columns=["group", "net_pnl", "trade_count", "contribution_ratio"])
        return {"year": empty, "sector": empty}
    annotated = trades.merge(
        candidates.loc[:, ["signal_date", "종목코드", "sector_code", "sector_name"]].drop_duplicates(),
        on=["signal_date", "종목코드"],
        how="left",
        validate="many_to_one",
    )
    annotated["net_pnl"] = (
        pd.to_numeric(annotated["shares"], errors="raise")
        * (pd.to_numeric(annotated["exit_price"], errors="raise") - pd.to_numeric(annotated["entry_price"], errors="raise"))
        - pd.to_numeric(annotated["cost_paid"], errors="raise")
    )
    annotated["year"] = pd.to_datetime(annotated["entry_date"], errors="raise").dt.year
    total_positive = float(annotated.loc[annotated["net_pnl"].gt(0), "net_pnl"].sum())
    denom = total_positive if total_positive != 0.0 else float(annotated["net_pnl"].abs().sum())
    year = _contribution_group(annotated, "year", denom)
    sector = _contribution_group(annotated, "sector_name", denom)
    return {"year": year, "sector": sector}


def _contribution_group(frame: pd.DataFrame, column: str, denominator: float) -> pd.DataFrame:
    grouped = (
        frame.groupby(column, dropna=False)
        .agg(net_pnl=("net_pnl", "sum"), trade_count=("net_pnl", "size"))
        .reset_index()
        .rename(columns={column: "group"})
        .sort_values("net_pnl", ascending=False)
        .reset_index(drop=True)
    )
    grouped["contribution_ratio"] = grouped["net_pnl"] / denominator if denominator else 0.0
    return grouped


def _e013_d013_overlap(candidates: pd.DataFrame) -> pd.DataFrame:
    d013_path = Path("reports/experiments/D013_d009_threshold_minus_0p2/signals.csv")
    if candidates.empty or not d013_path.exists():
        return pd.DataFrame(
            columns=[
                "quarter",
                "d013_count",
                "e013_count",
                "overlap_count",
                "union_count",
                "jaccard",
                "d013_tickers",
                "e013_tickers",
                "overlap_tickers",
            ]
        )
    d013 = pd.read_csv(d013_path, dtype={"ticker": "string", "종목코드": "string"})
    if "ticker" not in d013.columns and "종목코드" in d013.columns:
        d013["ticker"] = d013["종목코드"]
    d013["signal_date"] = pd.to_datetime(d013["signal_date"], errors="raise").dt.normalize()
    e013 = candidates.loc[:, ["signal_date", "종목코드"]].copy()
    e013["signal_date"] = pd.to_datetime(e013["signal_date"], errors="raise").dt.normalize()
    e013["ticker"] = e013["종목코드"].astype(str).str.zfill(6)
    rows = []
    for signal_date in sorted(set(d013["signal_date"]).union(set(e013["signal_date"]))):
        d_set = set(d013.loc[d013["signal_date"].eq(signal_date), "ticker"].astype(str).str.zfill(6))
        e_set = set(e013.loc[e013["signal_date"].eq(signal_date), "ticker"].astype(str).str.zfill(6))
        union = d_set | e_set
        overlap = d_set & e_set
        rows.append(
            {
                "quarter": signal_date,
                "d013_count": len(d_set),
                "e013_count": len(e_set),
                "overlap_count": len(overlap),
                "union_count": len(union),
                "jaccard": len(overlap) / len(union) if union else 0.0,
                "d013_tickers": " ".join(sorted(d_set)),
                "e013_tickers": " ".join(sorted(e_set)),
                "overlap_tickers": " ".join(sorted(overlap)),
            }
        )
    return pd.DataFrame(rows)


def _write_e013_report(
    output_dir: Path,
    config: dict[str, Any],
    subperiod_table: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    spike: pd.DataFrame,
    contribution: dict[str, pd.DataFrame],
    overlap: pd.DataFrame,
) -> None:
    overlap_mean = pd.to_numeric(overlap.get("jaccard", pd.Series(dtype="float64")), errors="coerce").mean()
    lines = [
        "# E013 Top4 Subperiod Spike Metrics Summary",
        "",
        "## Metadata",
        "",
        f"- panels: {', '.join(config['panels'])}",
        "- carrier: E011 Top4 champion; only trading window changes by subperiod",
        "- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2",
        "- spike_reference: E007 0.542974; D013 0.625452",
        "",
    ]
    lines.extend(_b004_dataframe_table("Subperiod Table", subperiod_table))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Spike Year Contribution", spike))
    lines.extend(_b004_dataframe_table("Year Contribution", contribution["year"]))
    lines.extend(_b004_dataframe_table("Sector Contribution", contribution["sector"]))
    lines.extend(_b004_dataframe_table("D013 Overlap Quarterly", overlap))
    lines.extend(["## Overlap Summary", "", f"- mean_jaccard: {overlap_mean}", ""])
    output_dir.joinpath("report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def run_c013_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c013_variants(
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
    metrics, cost_0_result = _c013_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c013_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c013_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c013_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c013_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c014_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c014_variants(
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
    metrics, cost_0_result = _c014_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c014_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c014_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c014_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c014_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c015_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c015_variants(
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
    metrics, cost_0_result = _c015_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c015_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c015_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c015_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c015_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c016_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c016_variants(
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
    metrics, cost_0_result = _c016_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c016_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c016_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c016_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c016_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c017_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c017_variants(
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
    metrics, cost_0_result = _c017_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c017_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c017_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c017_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c017_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c018_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c018_variants(
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
    metrics, cost_0_result = _c018_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c018_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c018_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c018_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c018_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c019_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c019_variants(
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
    metrics, cost_0_result = _c019_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c019_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c019_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c019_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c019_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_c020_experiment(config: dict[str, Any], config_path: Path) -> None:
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

    runs, candidates = run_c020_variants(
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
    metrics, cost_0_result = _c020_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _c020_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["macro_gate_mcap"], cost_0_result, calendar)
    verdict = _c020_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["macro_gate_mcap"]), output_dir / "signals.csv")
    _c020_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_c020_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_d001_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d001_variants(
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
    metrics, cost_0_result = _d001_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d001_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    verdict = _d001_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d001_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_d002_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d002_variants(
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
    metrics, cost_0_result = _d002_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d002_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    verdict = _d002_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d002_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d002_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_d003_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D003_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d003_variants(
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
    metrics, cost_0_result = _d003_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d003_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    verdict = _d003_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d003_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d003_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, verdict)


def run_d004_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    quarterly_log["exposure_scalar"] = quarterly_log["composite"].map(exposure_scalar)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d004_variants(
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
    metrics, cost_0_result = _d004_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_sized_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d004_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_sized_mcap"], cost_0_result, calendar)
    exposure_distribution = _d004_exposure_distribution(quarterly_log)
    magnitude_return_scatter = _d004_magnitude_return_scatter(quarterly_log, runs["factor_macro_sized_mcap"])
    verdict = _d004_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_sized_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_d004_signals(candidates["factor_macro_sized_mcap"]), output_dir / "signals.csv")
    _d004_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    exposure_distribution.to_csv(output_dir / "exposure_distribution.csv", index=False)
    magnitude_return_scatter.to_csv(output_dir / "magnitude_return_scatter.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d004_report(
        output_dir,
        config,
        metrics,
        year_breakdown,
        subperiod_breakdown,
        exposure_distribution,
        magnitude_return_scatter,
        verdict,
    )


def run_d005_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D005_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d005_variants(
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
    metrics, cost_0_result = _d005_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d005_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    verdict = _d005_verdict_summary(metrics)
    b7_diagnostics = _d005_b7_block_diagnostics(quarterly_log)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d005_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    b7_diagnostics.to_csv(output_dir / "b7_block_diagnostics.csv", index=False)
    _write_d005_report(output_dir, config, metrics, year_breakdown, subperiod_breakdown, b7_diagnostics, verdict)


def run_d006_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    grid_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    window_metrics: dict[int, dict[str, dict[str, Any]]] = {}
    for window in (int(value) for value in config["regime"]["z_score_window_grid"]):
        factor_monthly_regime = factor_aggregation_composite(
            monthly_raw_regime,
            z_score_window_months=window,
            on_threshold=float(config["regime"]["on_threshold"]),
            blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
        )
        quarterly_log = quarterly_regime_log(factor_monthly_regime)
        runs, candidates = run_d006_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        )
        metrics, cost_0_result = _d006_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=segments,
            candidate_years=candidate_years,
        )
        year_breakdown = _d006_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        warmup = _d006_warmup_diagnosis(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d006_window_verdict_summary(window, metrics, warmup)

        per_window_config = _d006_config_for_window(config, window)
        window_dir = output_dir / f"window_{window:02d}mo"
        window_dir.mkdir(parents=True, exist_ok=True)
        (window_dir / "config.yaml").write_text(
            yaml.safe_dump(per_window_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(window_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), window_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), window_dir / "signals.csv")
        _d006_wide_equity_curve(runs).to_csv(window_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(window_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(window_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(window_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(window_dir / "verdict_summary.csv", index=False)
        _write_d006_window_report(window_dir, per_window_config, metrics, year_breakdown, subperiod_breakdown, warmup, verdict)

        grid_rows.append(_d006_grid_summary_row(window, metrics, subperiod_breakdown, warmup))
        verdict_rows.extend(verdict.to_dict("records"))
        window_metrics[window] = metrics

    grid_summary = pd.DataFrame(grid_rows).sort_values("window").reset_index(drop=True)
    verdict_summary = _d006_grid_verdict_summary(grid_summary, verdict_rows)
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d006_report(output_dir, config, grid_summary, verdict_summary, window_metrics)


def run_d007_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    grid_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    threshold_metrics: dict[float, dict[str, dict[str, Any]]] = {}
    for threshold in (float(value) for value in config["regime"]["on_threshold_grid"]):
        factor_monthly_regime = factor_aggregation_composite(
            monthly_raw_regime,
            z_score_window_months=int(config["regime"]["z_score_window_months"]),
            on_threshold=threshold,
            blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
        )
        quarterly_log = quarterly_regime_log(factor_monthly_regime)
        runs, candidates = run_d007_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        )
        metrics, cost_0_result = _d007_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=segments,
            candidate_years=candidate_years,
        )
        year_breakdown = _d007_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d007_threshold_verdict_summary(threshold, metrics)

        per_threshold_config = _d007_config_for_threshold(config, threshold)
        threshold_dir = output_dir / f"threshold_{_d007_threshold_slug(threshold)}"
        threshold_dir.mkdir(parents=True, exist_ok=True)
        (threshold_dir / "config.yaml").write_text(
            yaml.safe_dump(per_threshold_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(threshold_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), threshold_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), threshold_dir / "signals.csv")
        _d007_wide_equity_curve(runs).to_csv(threshold_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(threshold_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(threshold_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(threshold_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(threshold_dir / "verdict_summary.csv", index=False)
        _write_d007_threshold_report(
            threshold_dir,
            per_threshold_config,
            metrics,
            year_breakdown,
            subperiod_breakdown,
            verdict,
        )

        grid_rows.append(_d007_grid_summary_row(threshold, metrics, subperiod_breakdown))
        verdict_rows.extend(verdict.to_dict("records"))
        threshold_metrics[threshold] = metrics

    grid_summary = pd.DataFrame(grid_rows).sort_values("threshold").reset_index(drop=True)
    verdict_summary = _d007_grid_verdict_summary(grid_summary, verdict_rows)
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d007_report(output_dir, config, grid_summary, verdict_summary, threshold_metrics)


def run_d008_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=EIGHT_PPI_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    base_segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    subperiod_rows: list[dict[str, Any]] = []
    per_year_frames: list[pd.DataFrame] = []
    full_result: BacktestResult | None = None

    for subperiod in config["subperiods"]:
        name = str(subperiod["name"])
        start = pd.Timestamp(subperiod["start"]).normalize()
        end = pd.Timestamp(subperiod["end"]).normalize()
        runs, candidates = run_d008_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=base_segments,
            max_positions=max_positions,
            trading_start=start,
            trading_end=end,
        )
        subperiod_config = _d008_config_for_subperiod(config, subperiod)
        subperiod_years = _d008_candidate_years(start, end, config["period"]["exclude_calendar_years"])
        metrics, cost_0_result = _d001_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=_d008_segments_for_subperiod(base_segments, start, end),
            candidate_years=subperiod_years,
        )
        year_breakdown = _d006_year_breakdown(runs=runs, calendar=calendar, candidate_years=subperiod_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d008_subperiod_verdict_summary(name, metrics)
        per_year = subperiod_year_breakdown(
            runs["factor_macro_gate_mcap"],
            calendar,
            years=subperiod_years,
        )
        per_year.insert(0, "subperiod", name)

        subperiod_dir = output_dir / name
        subperiod_dir.mkdir(parents=True, exist_ok=True)
        (subperiod_dir / "config.yaml").write_text(
            yaml.safe_dump(subperiod_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(subperiod_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), subperiod_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), subperiod_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(subperiod_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(subperiod_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(subperiod_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(subperiod_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(subperiod_dir / "verdict_summary.csv", index=False)
        _write_d008_subperiod_report(subperiod_dir, subperiod_config, metrics, year_breakdown, subperiod_breakdown, verdict)

        subperiod_rows.append(
            subperiod_metrics_row(
                name=name,
                start=start,
                end=end,
                net_result=runs["factor_macro_gate_mcap"],
                cost_0_result=cost_0_result,
                calendar=calendar,
                positive_years=int(metrics["factor_macro_gate_mcap"]["positive_years"]),
            )
        )
        per_year_frames.append(per_year)
        if name == "full":
            full_result = runs["factor_macro_gate_mcap"]

    if full_result is None:
        raise ValueError("D008 requires a subperiod named 'full'.")

    subperiod_table = pd.DataFrame(subperiod_rows)
    per_year_breakdown = pd.concat(per_year_frames, ignore_index=True)
    full_years = _d008_candidate_years(
        pd.Timestamp(config["subperiods"][0]["start"]),
        pd.Timestamp(config["subperiods"][0]["end"]),
        config["period"]["exclude_calendar_years"],
    )
    rolling = rolling_year_sharpe(
        full_result,
        calendar,
        start_year=min(year for year in full_years if year >= 2015),
        end_year=max(full_years),
        window_years=3,
    )
    verdict_summary = _d008_verdict_summary(subperiod_table)
    full_per_year = per_year_breakdown.loc[per_year_breakdown["subperiod"].eq("full")].copy()
    spike = spike_years(
        full_per_year.loc[:, ["year", "net"]],
        float(subperiod_table.loc[subperiod_table["subperiod"].eq("full"), "net"].iloc[0]),
    )

    subperiod_table.to_csv(output_dir / "subperiod_table.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    rolling.to_csv(output_dir / "rolling_3yr_sharpe.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    spike.to_csv(output_dir / "spike_year_contribution.csv", index=False)
    _write_d008_report(output_dir, config, subperiod_table, per_year_breakdown, rolling, verdict_summary, spike)


def run_d009_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d009_variants(
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
    metrics, cost_0_result = _d009_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    per_year_breakdown = subperiod_year_breakdown(runs["factor_macro_gate_mcap"], calendar, years=candidate_years)
    block_diagnostics = _d009_block_diagnostics(quarterly_log)
    verdict = _d009_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    block_diagnostics.to_csv(output_dir / "block_diagnostics.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    _write_d009_report(
        output_dir,
        config,
        metrics,
        year_breakdown,
        subperiod_breakdown,
        block_diagnostics,
        per_year_breakdown,
        verdict,
    )


def run_d010_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    grid_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    window_metrics: dict[int, dict[str, dict[str, Any]]] = {}
    for window in (int(value) for value in config["regime"]["z_score_window_grid"]):
        factor_monthly_regime = factor_aggregation_composite(
            monthly_raw_regime,
            z_score_window_months=window,
            on_threshold=float(config["regime"]["on_threshold"]),
            blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
        )
        quarterly_log = quarterly_regime_log(factor_monthly_regime)
        runs, candidates = run_d010_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        )
        metrics, cost_0_result = _d009_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=segments,
            candidate_years=candidate_years,
        )
        year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        warmup = _d006_warmup_diagnosis(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d010_window_verdict_summary(window, metrics, warmup)

        per_window_config = _d006_config_for_window(config, window)
        window_dir = output_dir / f"window_{window:02d}mo"
        window_dir.mkdir(parents=True, exist_ok=True)
        (window_dir / "config.yaml").write_text(
            yaml.safe_dump(per_window_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(window_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), window_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), window_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(window_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(window_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(window_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(window_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(window_dir / "verdict_summary.csv", index=False)
        _write_d010_window_report(window_dir, per_window_config, metrics, year_breakdown, subperiod_breakdown, warmup, verdict)

        grid_rows.append(_d006_grid_summary_row(window, metrics, subperiod_breakdown, warmup))
        verdict_rows.extend(verdict.to_dict("records"))
        window_metrics[window] = metrics

    grid_summary = pd.DataFrame(grid_rows).sort_values("window").reset_index(drop=True)
    verdict_summary = _d006_grid_verdict_summary(grid_summary, verdict_rows)
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d010_report(output_dir, config, grid_summary, verdict_summary, window_metrics)


def run_d011_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    grid_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    threshold_metrics: dict[float, dict[str, dict[str, Any]]] = {}
    for threshold in (float(value) for value in config["regime"]["on_threshold_grid"]):
        factor_monthly_regime = factor_aggregation_composite(
            monthly_raw_regime,
            z_score_window_months=int(config["regime"]["z_score_window_months"]),
            on_threshold=threshold,
            blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
        )
        quarterly_log = quarterly_regime_log(factor_monthly_regime)
        runs, candidates = run_d011_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        )
        metrics, cost_0_result = _d009_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=segments,
            candidate_years=candidate_years,
        )
        year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d011_threshold_verdict_summary(threshold, metrics)

        per_threshold_config = _d007_config_for_threshold(config, threshold)
        threshold_dir = output_dir / f"threshold_{_d007_threshold_slug(threshold)}"
        threshold_dir.mkdir(parents=True, exist_ok=True)
        (threshold_dir / "config.yaml").write_text(
            yaml.safe_dump(per_threshold_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(threshold_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), threshold_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), threshold_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(threshold_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(threshold_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(threshold_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(threshold_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(threshold_dir / "verdict_summary.csv", index=False)
        _write_d011_threshold_report(threshold_dir, per_threshold_config, metrics, year_breakdown, subperiod_breakdown, verdict)

        grid_rows.append(_d007_grid_summary_row(threshold, metrics, subperiod_breakdown))
        verdict_rows.extend(verdict.to_dict("records"))
        threshold_metrics[threshold] = metrics

    grid_summary = pd.DataFrame(grid_rows).sort_values("threshold").reset_index(drop=True)
    verdict_summary = _d007_grid_verdict_summary(grid_summary, verdict_rows)
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d011_report(output_dir, config, grid_summary, verdict_summary, threshold_metrics)


def run_d012_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    base_segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    subperiod_rows: list[dict[str, Any]] = []
    per_year_frames: list[pd.DataFrame] = []
    full_result: BacktestResult | None = None

    for subperiod in config["subperiods"]:
        name = str(subperiod["name"])
        start = pd.Timestamp(subperiod["start"]).normalize()
        end = pd.Timestamp(subperiod["end"]).normalize()
        runs, candidates = run_d012_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=base_segments,
            max_positions=max_positions,
            trading_start=start,
            trading_end=end,
        )
        subperiod_config = _d008_config_for_subperiod(config, subperiod)
        subperiod_years = _d008_candidate_years(start, end, config["period"]["exclude_calendar_years"])
        metrics, cost_0_result = _d009_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=_d008_segments_for_subperiod(base_segments, start, end),
            candidate_years=subperiod_years,
        )
        year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=subperiod_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d012_subperiod_verdict_summary(name, metrics)
        per_year = subperiod_year_breakdown(runs["factor_macro_gate_mcap"], calendar, years=subperiod_years)
        per_year.insert(0, "subperiod", name)

        subperiod_dir = output_dir / name
        subperiod_dir.mkdir(parents=True, exist_ok=True)
        (subperiod_dir / "config.yaml").write_text(
            yaml.safe_dump(subperiod_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(subperiod_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), subperiod_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), subperiod_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(subperiod_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(subperiod_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(subperiod_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(subperiod_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(subperiod_dir / "verdict_summary.csv", index=False)
        _write_d012_subperiod_report(subperiod_dir, subperiod_config, metrics, year_breakdown, subperiod_breakdown, verdict)

        subperiod_rows.append(
            subperiod_metrics_row(
                name=name,
                start=start,
                end=end,
                net_result=runs["factor_macro_gate_mcap"],
                cost_0_result=cost_0_result,
                calendar=calendar,
                positive_years=int(metrics["factor_macro_gate_mcap"]["positive_years"]),
            )
        )
        per_year_frames.append(per_year)
        if name == "full":
            full_result = runs["factor_macro_gate_mcap"]

    if full_result is None:
        raise ValueError("D012 requires a subperiod named 'full'.")

    subperiod_table = pd.DataFrame(subperiod_rows)
    per_year_breakdown = pd.concat(per_year_frames, ignore_index=True)
    full_years = _d008_candidate_years(
        pd.Timestamp(config["subperiods"][0]["start"]),
        pd.Timestamp(config["subperiods"][0]["end"]),
        config["period"]["exclude_calendar_years"],
    )
    rolling = rolling_year_sharpe(
        full_result,
        calendar,
        start_year=min(year for year in full_years if year >= 2015),
        end_year=max(full_years),
        window_years=3,
    )
    verdict_summary = _d008_verdict_summary(subperiod_table)
    full_per_year = per_year_breakdown.loc[per_year_breakdown["subperiod"].eq("full")].copy()
    spike = spike_years(
        full_per_year.loc[:, ["year", "net"]],
        float(subperiod_table.loc[subperiod_table["subperiod"].eq("full"), "net"].iloc[0]),
    )

    subperiod_table.to_csv(output_dir / "subperiod_table.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    rolling.to_csv(output_dir / "rolling_3yr_sharpe.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    spike.to_csv(output_dir / "spike_year_contribution.csv", index=False)
    _write_d012_report(output_dir, config, subperiod_table, per_year_breakdown, rolling, verdict_summary, spike)


def run_d013_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    runs, candidates = run_d013_variants(
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
    metrics, cost_0_result = _d009_metrics(
        runs=runs,
        panel=panel,
        calendar=calendar,
        candidates=candidates["factor_macro_gate_mcap"],
        quarterly_regime=quarterly_log,
        segments=segments,
        candidate_years=candidate_years,
    )
    year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
    subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
    per_year_breakdown = subperiod_year_breakdown(runs["factor_macro_gate_mcap"], calendar, years=candidate_years)
    block_diagnostics = _d009_block_diagnostics(quarterly_log)
    verdict = _d013_verdict_summary(metrics)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), output_dir / "trades.csv")
    _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), output_dir / "signals.csv")
    _d001_wide_equity_curve(runs).to_csv(output_dir / "equity_curve.csv", index=False)
    year_breakdown.to_csv(output_dir / "quarterly_year_breakdown.csv", index=False)
    quarterly_log.to_csv(output_dir / "quarterly_regime_log.csv", index=False)
    subperiod_breakdown.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    verdict.to_csv(output_dir / "verdict_summary.csv", index=False)
    block_diagnostics.to_csv(output_dir / "block_diagnostics.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    _write_d013_report(
        output_dir,
        config,
        metrics,
        year_breakdown,
        subperiod_breakdown,
        block_diagnostics,
        per_year_breakdown,
        verdict,
    )


def run_d014_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])
    candidate_years = _b011_candidate_years(config)

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    grid_rows: list[dict[str, Any]] = []
    verdict_rows: list[dict[str, Any]] = []
    window_metrics: dict[int, dict[str, dict[str, Any]]] = {}
    for window in (int(value) for value in config["regime"]["z_score_window_grid"]):
        factor_monthly_regime = factor_aggregation_composite(
            monthly_raw_regime,
            z_score_window_months=window,
            on_threshold=float(config["regime"]["on_threshold"]),
            blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
        )
        quarterly_log = quarterly_regime_log(factor_monthly_regime)
        runs, candidates = run_d014_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=segments,
            max_positions=max_positions,
        )
        metrics, cost_0_result = _d009_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=segments,
            candidate_years=candidate_years,
        )
        year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=candidate_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        warmup = _d006_warmup_diagnosis(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d014_window_verdict_summary(window, metrics, warmup)

        per_window_config = _d006_config_for_window(config, window)
        window_dir = output_dir / f"window_{window:02d}mo"
        window_dir.mkdir(parents=True, exist_ok=True)
        (window_dir / "config.yaml").write_text(
            yaml.safe_dump(per_window_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(window_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), window_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), window_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(window_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(window_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(window_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(window_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(window_dir / "verdict_summary.csv", index=False)
        _write_d014_window_report(window_dir, per_window_config, metrics, year_breakdown, subperiod_breakdown, warmup, verdict)

        grid_rows.append(_d006_grid_summary_row(window, metrics, subperiod_breakdown, warmup))
        verdict_rows.extend(verdict.to_dict("records"))
        window_metrics[window] = metrics

    grid_summary = pd.DataFrame(grid_rows).sort_values("window").reset_index(drop=True)
    verdict_summary = _d006_grid_verdict_summary(grid_summary, verdict_rows)
    grid_summary.to_csv(output_dir / "grid_summary.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    _write_d014_report(output_dir, config, grid_summary, verdict_summary, window_metrics)


def run_d015_experiment(config: dict[str, Any], config_path: Path) -> None:
    panel, calendar, universe = _build_b011_inputs(config)
    market_breadth = pd.read_csv(config["market_breadth_csv"], encoding="utf-8-sig")
    raw_daily_regime = build_macro_regime_daily(
        pd.Index(calendar.dates),
        macro_data_dir=config["macro_data_dir"],
        on_threshold=2,
        macro_signals=D009_SIGNAL_NAMES,
    )
    monthly_raw_regime = monthly_regime_log(raw_daily_regime)
    factor_monthly_regime = factor_aggregation_composite(
        monthly_raw_regime,
        z_score_window_months=int(config["regime"]["z_score_window_months"]),
        on_threshold=float(config["regime"]["on_threshold"]),
        blocks=_d001_blocks_from_config(config["regime"]["blocks"]),
    )
    quarterly_log = quarterly_regime_log(factor_monthly_regime)
    base_segments = _b011_segments(config)
    costs = _costs_from_config(config["costs"])
    max_positions = int(config["selection"]["n"])

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")

    subperiod_rows: list[dict[str, Any]] = []
    per_year_frames: list[pd.DataFrame] = []
    full_result: BacktestResult | None = None

    for subperiod in config["subperiods"]:
        name = str(subperiod["name"])
        start = pd.Timestamp(subperiod["start"]).normalize()
        end = pd.Timestamp(subperiod["end"]).normalize()
        runs, candidates = run_d015_variants(
            panel=panel,
            calendar=calendar,
            universe=universe,
            quarterly_regime=quarterly_log,
            market_breadth=market_breadth,
            costs=costs,
            segments=base_segments,
            max_positions=max_positions,
            trading_start=start,
            trading_end=end,
        )
        subperiod_config = _d008_config_for_subperiod(config, subperiod)
        subperiod_years = _d008_candidate_years(start, end, config["period"]["exclude_calendar_years"])
        metrics, cost_0_result = _d009_metrics(
            runs=runs,
            panel=panel,
            calendar=calendar,
            candidates=candidates["factor_macro_gate_mcap"],
            quarterly_regime=quarterly_log,
            segments=_d008_segments_for_subperiod(base_segments, start, end),
            candidate_years=subperiod_years,
        )
        year_breakdown = _d009_year_breakdown(runs=runs, calendar=calendar, candidate_years=subperiod_years)
        subperiod_breakdown = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], cost_0_result, calendar)
        verdict = _d015_subperiod_verdict_summary(name, metrics)
        per_year = subperiod_year_breakdown(runs["factor_macro_gate_mcap"], calendar, years=subperiod_years)
        per_year.insert(0, "subperiod", name)

        subperiod_dir = output_dir / name
        subperiod_dir.mkdir(parents=True, exist_ok=True)
        (subperiod_dir / "config.yaml").write_text(
            yaml.safe_dump(subperiod_config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        _write_json(subperiod_dir / "metrics.json", metrics)
        _write_ticker_safe_csv(_b011_trades(runs["factor_macro_gate_mcap"], calendar), subperiod_dir / "trades.csv")
        _write_ticker_safe_csv(_c008_signals(candidates["factor_macro_gate_mcap"]), subperiod_dir / "signals.csv")
        _d001_wide_equity_curve(runs).to_csv(subperiod_dir / "equity_curve.csv", index=False)
        year_breakdown.to_csv(subperiod_dir / "quarterly_year_breakdown.csv", index=False)
        quarterly_log.to_csv(subperiod_dir / "quarterly_regime_log.csv", index=False)
        subperiod_breakdown.to_csv(subperiod_dir / "subperiod_breakdown.csv", index=False)
        verdict.to_csv(subperiod_dir / "verdict_summary.csv", index=False)
        _write_d015_subperiod_report(subperiod_dir, subperiod_config, metrics, year_breakdown, subperiod_breakdown, verdict)

        subperiod_rows.append(
            subperiod_metrics_row(
                name=name,
                start=start,
                end=end,
                net_result=runs["factor_macro_gate_mcap"],
                cost_0_result=cost_0_result,
                calendar=calendar,
                positive_years=int(metrics["factor_macro_gate_mcap"]["positive_years"]),
            )
        )
        per_year_frames.append(per_year)
        if name == "full":
            full_result = runs["factor_macro_gate_mcap"]

    if full_result is None:
        raise ValueError("D015 requires a subperiod named 'full'.")

    subperiod_table = pd.DataFrame(subperiod_rows)
    per_year_breakdown = pd.concat(per_year_frames, ignore_index=True)
    full_years = _d008_candidate_years(
        pd.Timestamp(config["subperiods"][0]["start"]),
        pd.Timestamp(config["subperiods"][0]["end"]),
        config["period"]["exclude_calendar_years"],
    )
    rolling = rolling_year_sharpe(
        full_result,
        calendar,
        start_year=min(year for year in full_years if year >= 2015),
        end_year=max(full_years),
        window_years=3,
    )
    verdict_summary = _d008_verdict_summary(subperiod_table)
    full_per_year = per_year_breakdown.loc[per_year_breakdown["subperiod"].eq("full")].copy()
    spike = spike_years(
        full_per_year.loc[:, ["year", "net"]],
        float(subperiod_table.loc[subperiod_table["subperiod"].eq("full"), "net"].iloc[0]),
    )

    subperiod_table.to_csv(output_dir / "subperiod_table.csv", index=False)
    per_year_breakdown.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    rolling.to_csv(output_dir / "rolling_3yr_sharpe.csv", index=False)
    verdict_summary.to_csv(output_dir / "verdict_summary.csv", index=False)
    spike.to_csv(output_dir / "spike_year_contribution.csv", index=False)
    _write_d015_report(output_dir, config, subperiod_table, per_year_breakdown, rolling, verdict_summary, spike)


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
C013_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C013_macro_v10_us_cpi")
C013_QUARTERLY_CUMULATIVE_NET = 0.8128975579087656
C013_QUARTERLY_COST_0_CUMULATIVE_NET = 1.123436064013747
C014_QUARTERLY_OUTPUT_DIR = Path("reports/experiments/C014_macro_v11_us_ppi")
C014_QUARTERLY_CUMULATIVE_NET = 1.1136051550981834
C014_QUARTERLY_COST_0_CUMULATIVE_NET = 1.483915813335873
D001_OUTPUT_DIR = Path("reports/experiments/D001_factor_aggregation_pivot")
D001_CUMULATIVE_NET = 1.2906841868750734
D001_COST_0_CUMULATIVE_NET = 1.397144393892741
D001_TRADE_COUNT = 70


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


def _c013_metrics(
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
    for variant in C013_VARIANTS:
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
    cpi_brent = quarterly_regime.loc[:, ["US_CPI_yoy", "Brent_yoy"]].dropna()
    cpi_curve = quarterly_regime.loc[:, ["US_CPI_yoy", "US_2_10_curve_spread"]].dropna()
    cpi_usdkrw = quarterly_regime.loc[:, ["US_CPI_yoy", "USDKRW_yoy"]].dropna()
    cpi_decel_brent = quarterly_regime.loc[:, ["US_CPI_decel", "Brent_yoy"]].dropna()
    cpi_decel_curve = quarterly_regime.loc[:, ["US_CPI_decel", "US_2_10_curve_spread"]].dropna()
    cpi_decel_usdkrw = quarterly_regime.loc[:, ["US_CPI_decel", "USDKRW_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c011_v8_cumulative_net_total_return"] = C011_QUARTERLY_CUMULATIVE_NET
    v1["c011_v8_cost_0_cumulative_net_total_return"] = C011_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v10_minus_v8_cumulative_net_pp"] = v1_return - C011_QUARTERLY_CUMULATIVE_NET
    v1["v10_minus_v8_cost_0_cumulative_net_pp"] = cost_0_return - C011_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["us_cpi_favorable_quarters"] = int(complete_quarters["favorable_US_CPI"].sum())
    v1["us_cpi_total_quarters"] = int(len(complete_quarters))
    v1["us_cpi_yoy_brent_yoy_correlation"] = (
        float(cpi_brent["US_CPI_yoy"].corr(cpi_brent["Brent_yoy"])) if len(cpi_brent) >= 2 else float("nan")
    )
    v1["us_cpi_yoy_curve_spread_correlation"] = (
        float(cpi_curve["US_CPI_yoy"].corr(cpi_curve["US_2_10_curve_spread"]))
        if len(cpi_curve) >= 2
        else float("nan")
    )
    v1["us_cpi_yoy_usdkrw_yoy_correlation"] = (
        float(cpi_usdkrw["US_CPI_yoy"].corr(cpi_usdkrw["USDKRW_yoy"])) if len(cpi_usdkrw) >= 2 else float("nan")
    )
    v1["us_cpi_decel_brent_yoy_correlation"] = (
        float(cpi_decel_brent["US_CPI_decel"].corr(cpi_decel_brent["Brent_yoy"]))
        if len(cpi_decel_brent) >= 2
        else float("nan")
    )
    v1["us_cpi_decel_curve_spread_correlation"] = (
        float(cpi_decel_curve["US_CPI_decel"].corr(cpi_decel_curve["US_2_10_curve_spread"]))
        if len(cpi_decel_curve) >= 2
        else float("nan")
    )
    v1["us_cpi_decel_usdkrw_yoy_correlation"] = (
        float(cpi_decel_usdkrw["US_CPI_decel"].corr(cpi_decel_usdkrw["USDKRW_yoy"]))
        if len(cpi_decel_usdkrw) >= 2
        else float("nan")
    )
    spike = quarterly_regime.loc[
        quarterly_regime["signal_date"].between(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))
    ]
    v1["inflation_spike_2022_regime_on_quarters"] = int(spike["regime_on"].sum())
    v1["inflation_spike_2022_total_quarters"] = int(len(spike))
    v1["inflation_spike_2022_cpi_favorable_quarters"] = int(spike["favorable_US_CPI"].sum())

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c013_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c011_quarterly = _c011_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C013_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c011_v8_macro_gate_mcap_net_total_return"] = c011_quarterly.get(year, float("nan"))
        row["v10_minus_v8_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c011_v8_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c013_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v10_minus_v8_cumulative_net_pp"])
    max_cpi_yoy_corr = max(
        abs(float(v1["us_cpi_yoy_brent_yoy_correlation"])),
        abs(float(v1["us_cpi_yoy_curve_spread_correlation"])),
        abs(float(v1["us_cpi_yoy_usdkrw_yoy_correlation"])),
    )
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v10 cumulative net improves on C011 v8 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C013 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "US CPI yoy correlations with Brent, curve, and USDKRW are descriptive redundancy checks",
                "value": max_cpi_yoy_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c014_metrics(
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
    for variant in C014_VARIANTS:
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
    ppi_cpi = quarterly_regime.loc[:, ["US_PPI_decel", "US_CPI_decel"]].dropna()
    ppi_brent = quarterly_regime.loc[:, ["US_PPI_decel", "Brent_yoy"]].dropna()
    ppi_dxy = quarterly_regime.loc[:, ["US_PPI_decel", "DXY_yoy"]].dropna()
    ppi_yoy_cpi_yoy = quarterly_regime.loc[:, ["US_PPI_yoy", "US_CPI_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c013_v10_cumulative_net_total_return"] = C013_QUARTERLY_CUMULATIVE_NET
    v1["c013_v10_cost_0_cumulative_net_total_return"] = C013_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v11_minus_v10_cumulative_net_pp"] = v1_return - C013_QUARTERLY_CUMULATIVE_NET
    v1["v11_minus_v10_cost_0_cumulative_net_pp"] = cost_0_return - C013_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["us_ppi_favorable_quarters"] = int(complete_quarters["favorable_US_PPI"].sum())
    v1["us_ppi_total_quarters"] = int(len(complete_quarters))
    v1["us_ppi_decel_us_cpi_decel_correlation"] = (
        float(ppi_cpi["US_PPI_decel"].corr(ppi_cpi["US_CPI_decel"])) if len(ppi_cpi) >= 2 else float("nan")
    )
    v1["us_ppi_decel_brent_yoy_correlation"] = (
        float(ppi_brent["US_PPI_decel"].corr(ppi_brent["Brent_yoy"])) if len(ppi_brent) >= 2 else float("nan")
    )
    v1["us_ppi_decel_dxy_yoy_correlation"] = (
        float(ppi_dxy["US_PPI_decel"].corr(ppi_dxy["DXY_yoy"])) if len(ppi_dxy) >= 2 else float("nan")
    )
    v1["us_ppi_yoy_us_cpi_yoy_correlation"] = (
        float(ppi_yoy_cpi_yoy["US_PPI_yoy"].corr(ppi_yoy_cpi_yoy["US_CPI_yoy"]))
        if len(ppi_yoy_cpi_yoy) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c014_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c013_quarterly = _c013_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C014_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c013_v10_macro_gate_mcap_net_total_return"] = c013_quarterly.get(year, float("nan"))
        row["v11_minus_v10_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c013_v10_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c014_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v11_minus_v10_cumulative_net_pp"])
    cpi_ppi_corr = abs(float(v1["us_ppi_decel_us_cpi_decel_correlation"]))
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v11 cumulative net improves on C013 v10 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C014 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "US PPI decel vs US CPI decel correlation is a descriptive redundancy check",
                "value": cpi_ppi_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c015_metrics(
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
    for variant in C015_VARIANTS:
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
    unrate_cpi = quarterly_regime.loc[:, ["US_UNRATE_yoy_change", "US_CPI_yoy"]].dropna()
    unrate_curve = quarterly_regime.loc[:, ["US_UNRATE_yoy_change", "US_2_10_curve_spread"]].dropna()
    unrate_usdkrw = quarterly_regime.loc[:, ["US_UNRATE_yoy_change", "USDKRW_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v12_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v12_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["us_unrate_favorable_quarters"] = int(complete_quarters["favorable_US_UNRATE"].sum())
    v1["us_unrate_total_quarters"] = int(len(complete_quarters))
    v1["us_unrate_change_us_cpi_yoy_correlation"] = (
        float(unrate_cpi["US_UNRATE_yoy_change"].corr(unrate_cpi["US_CPI_yoy"]))
        if len(unrate_cpi) >= 2
        else float("nan")
    )
    v1["us_unrate_change_curve_spread_correlation"] = (
        float(unrate_curve["US_UNRATE_yoy_change"].corr(unrate_curve["US_2_10_curve_spread"]))
        if len(unrate_curve) >= 2
        else float("nan")
    )
    v1["us_unrate_change_usdkrw_yoy_correlation"] = (
        float(unrate_usdkrw["US_UNRATE_yoy_change"].corr(unrate_usdkrw["USDKRW_yoy"]))
        if len(unrate_usdkrw) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c015_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C015_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v12_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c015_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v12_minus_v11_cumulative_net_pp"])
    max_corr = max(
        abs(float(v1["us_unrate_change_us_cpi_yoy_correlation"])),
        abs(float(v1["us_unrate_change_curve_spread_correlation"])),
        abs(float(v1["us_unrate_change_usdkrw_yoy_correlation"])),
    )
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v12 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C015 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "US UNRATE yoy-change correlations with CPI yoy, curve, and USDKRW are descriptive redundancy checks",
                "value": max_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c016_metrics(
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
    for variant in C016_VARIANTS:
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
    kr_cpi_available = complete_quarters.loc[complete_quarters["KR_CPI_decel"].notna()]
    kr_cpi_us_cpi = complete_quarters.loc[:, ["KR_CPI_decel", "US_CPI_decel"]].dropna()
    kr_cpi_brent = complete_quarters.loc[:, ["KR_CPI_decel", "Brent_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v13_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v13_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["kr_cpi_favorable_quarters"] = int(kr_cpi_available["favorable_KR_CPI"].sum())
    v1["kr_cpi_total_quarters_with_data"] = int(len(kr_cpi_available))
    v1["kr_cpi_missing_quarters"] = int(complete_quarters["KR_CPI_decel"].isna().sum())
    v1["kr_cpi_decel_us_cpi_decel_correlation"] = (
        float(kr_cpi_us_cpi["KR_CPI_decel"].corr(kr_cpi_us_cpi["US_CPI_decel"]))
        if len(kr_cpi_us_cpi) >= 2
        else float("nan")
    )
    v1["kr_cpi_decel_brent_yoy_correlation"] = (
        float(kr_cpi_brent["KR_CPI_decel"].corr(kr_cpi_brent["Brent_yoy"]))
        if len(kr_cpi_brent) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c016_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C016_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v13_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c016_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v13_minus_v11_cumulative_net_pp"])
    cpi_corr = abs(float(v1["kr_cpi_decel_us_cpi_decel_correlation"]))
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v13 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C016 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "KR CPI decel vs US CPI decel correlation is a descriptive redundancy check",
                "value": cpi_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c017_metrics(
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
    for variant in C017_VARIANTS:
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
    exports_available = complete_quarters.loc[complete_quarters["KR_exports_yoy"].notna()]
    exports_brent = complete_quarters.loc[:, ["KR_exports_yoy", "Brent_yoy"]].dropna()
    exports_usdkrw = complete_quarters.loc[:, ["KR_exports_yoy", "USDKRW_yoy"]].dropna()
    exports_us_cpi = complete_quarters.loc[:, ["KR_exports_yoy", "US_CPI_decel"]].dropna()
    exports_us_ppi = complete_quarters.loc[:, ["KR_exports_yoy", "US_PPI_decel"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v14_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v14_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["kr_exports_favorable_quarters"] = int(exports_available["favorable_KR_exports"].sum())
    v1["kr_exports_total_quarters_with_data"] = int(len(exports_available))
    v1["kr_exports_missing_quarters"] = int(complete_quarters["KR_exports_yoy"].isna().sum())
    v1["kr_exports_yoy_brent_yoy_correlation"] = (
        float(exports_brent["KR_exports_yoy"].corr(exports_brent["Brent_yoy"]))
        if len(exports_brent) >= 2
        else float("nan")
    )
    v1["kr_exports_yoy_usdkrw_yoy_correlation"] = (
        float(exports_usdkrw["KR_exports_yoy"].corr(exports_usdkrw["USDKRW_yoy"]))
        if len(exports_usdkrw) >= 2
        else float("nan")
    )
    v1["kr_exports_yoy_us_cpi_decel_correlation"] = (
        float(exports_us_cpi["KR_exports_yoy"].corr(exports_us_cpi["US_CPI_decel"]))
        if len(exports_us_cpi) >= 2
        else float("nan")
    )
    v1["kr_exports_yoy_us_ppi_decel_correlation"] = (
        float(exports_us_ppi["KR_exports_yoy"].corr(exports_us_ppi["US_PPI_decel"]))
        if len(exports_us_ppi) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c017_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C017_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v14_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c017_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v14_minus_v11_cumulative_net_pp"])
    max_corr = max(
        abs(float(v1["kr_exports_yoy_brent_yoy_correlation"])),
        abs(float(v1["kr_exports_yoy_usdkrw_yoy_correlation"])),
        abs(float(v1["kr_exports_yoy_us_cpi_decel_correlation"])),
        abs(float(v1["kr_exports_yoy_us_ppi_decel_correlation"])),
    )
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v14 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C017 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "KR exports yoy correlations with Brent, USDKRW, US CPI, and US PPI are descriptive checks",
                "value": max_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c018_metrics(
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
    for variant in C018_VARIANTS:
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
    m2_available = complete_quarters.loc[complete_quarters["US_M2_yoy"].notna()]
    m2_cpi = complete_quarters.loc[:, ["US_M2_yoy", "US_CPI_decel"]].dropna()
    m2_curve = complete_quarters.loc[:, ["US_M2_yoy", "US_2_10_curve_spread"]].dropna()
    m2_usdkrw = complete_quarters.loc[:, ["US_M2_yoy", "USDKRW_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v15_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v15_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["us_m2_favorable_quarters"] = int(m2_available["favorable_US_M2"].sum())
    v1["us_m2_total_quarters_with_data"] = int(len(m2_available))
    v1["us_m2_missing_quarters"] = int(complete_quarters["US_M2_yoy"].isna().sum())
    v1["us_m2_yoy_us_cpi_decel_correlation"] = (
        float(m2_cpi["US_M2_yoy"].corr(m2_cpi["US_CPI_decel"])) if len(m2_cpi) >= 2 else float("nan")
    )
    v1["us_m2_yoy_curve_spread_correlation"] = (
        float(m2_curve["US_M2_yoy"].corr(m2_curve["US_2_10_curve_spread"]))
        if len(m2_curve) >= 2
        else float("nan")
    )
    v1["us_m2_yoy_usdkrw_yoy_correlation"] = (
        float(m2_usdkrw["US_M2_yoy"].corr(m2_usdkrw["USDKRW_yoy"])) if len(m2_usdkrw) >= 2 else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c018_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C018_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v15_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c018_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v15_minus_v11_cumulative_net_pp"])
    max_corr = max(
        abs(float(v1["us_m2_yoy_us_cpi_decel_correlation"])),
        abs(float(v1["us_m2_yoy_curve_spread_correlation"])),
        abs(float(v1["us_m2_yoy_usdkrw_yoy_correlation"])),
    )
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v15 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C018 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "US M2 yoy correlations with US CPI decel, curve, and USDKRW are descriptive checks",
                "value": max_corr,
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c019_metrics(
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
    for variant in C019_VARIANTS:
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
    usdjpy_available = complete_quarters.loc[complete_quarters["USDJPY_yoy"].notna()]
    usdjpy_dxy = complete_quarters.loc[:, ["USDJPY_yoy", "DXY_yoy"]].dropna()
    usdjpy_usdkrw = complete_quarters.loc[:, ["USDJPY_yoy", "USDKRW_yoy"]].dropna()
    usdjpy_vix = complete_quarters.loc[:, ["USDJPY_yoy", "VIX_60d_avg"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v16_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v16_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["usdjpy_favorable_quarters"] = int(usdjpy_available["favorable_USDJPY"].sum())
    v1["usdjpy_total_quarters_with_data"] = int(len(usdjpy_available))
    v1["usdjpy_missing_quarters"] = int(complete_quarters["USDJPY_yoy"].isna().sum())
    v1["usdjpy_yoy_dxy_yoy_correlation"] = (
        float(usdjpy_dxy["USDJPY_yoy"].corr(usdjpy_dxy["DXY_yoy"])) if len(usdjpy_dxy) >= 2 else float("nan")
    )
    v1["usdjpy_yoy_usdkrw_yoy_correlation"] = (
        float(usdjpy_usdkrw["USDJPY_yoy"].corr(usdjpy_usdkrw["USDKRW_yoy"]))
        if len(usdjpy_usdkrw) >= 2
        else float("nan")
    )
    v1["usdjpy_yoy_vix_60d_avg_correlation"] = (
        float(usdjpy_vix["USDJPY_yoy"].corr(usdjpy_vix["VIX_60d_avg"]))
        if len(usdjpy_vix) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c019_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C019_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v16_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c019_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v16_minus_v11_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v16 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C019 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "USDJPY yoy vs DXY yoy correlation is the key descriptive redundancy check",
                "value": float(v1["usdjpy_yoy_dxy_yoy_correlation"]),
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _c020_metrics(
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
    for variant in C020_VARIANTS:
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
    jp10y_available = complete_quarters.loc[complete_quarters["JP10Y_yoy_change"].notna()]
    jp10y_us10y = complete_quarters.loc[:, ["JP10Y_yoy_change", "US10Y_yoy_change"]].dropna()
    jp10y_kr10y = complete_quarters.loc[:, ["JP10Y_yoy_change", "KR10Y_yoy_change"]].dropna()
    jp10y_usdjpy = complete_quarters.loc[:, ["JP10Y_yoy_change", "USDJPY_yoy"]].dropna()

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["v17_minus_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["v17_minus_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["jp10y_favorable_quarters"] = int(jp10y_available["favorable_JP10Y"].sum())
    v1["jp10y_total_quarters_with_data"] = int(len(jp10y_available))
    v1["jp10y_missing_quarters"] = int(complete_quarters["JP10Y_yoy_change"].isna().sum())
    v1["jp10y_yoy_change_us10y_yoy_change_correlation"] = (
        float(jp10y_us10y["JP10Y_yoy_change"].corr(jp10y_us10y["US10Y_yoy_change"]))
        if len(jp10y_us10y) >= 2
        else float("nan")
    )
    v1["jp10y_yoy_change_kr10y_yoy_change_correlation"] = (
        float(jp10y_kr10y["JP10Y_yoy_change"].corr(jp10y_kr10y["KR10Y_yoy_change"]))
        if len(jp10y_kr10y) >= 2
        else float("nan")
    )
    v1["jp10y_yoy_change_usdjpy_yoy_correlation"] = (
        float(jp10y_usdjpy["JP10Y_yoy_change"].corr(jp10y_usdjpy["USDJPY_yoy"]))
        if len(jp10y_usdjpy) >= 2
        else float("nan")
    )

    subperiod = _c010_subperiod_breakdown(runs["macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _c020_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in C020_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["v17_minus_v11_macro_gate_mcap_return"] = (
            row["macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _c020_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    base = _c003_verdict_summary(metrics)
    v1 = metrics["macro_gate_mcap"]
    delta = float(v1["v17_minus_v11_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "V1 v17 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "C020 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "JP10y yoy change correlations with US10y, KR10y, and USDJPY are descriptive checks",
                "value": float(v1["jp10y_yoy_change_us10y_yoy_change_correlation"]),
                "threshold": 0.7,
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _d001_metrics(
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
    for variant in D001_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()]
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["d001_minus_c014_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["d001_minus_c014_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    c014_trades = _read_reference_trades(C014_QUARTERLY_OUTPUT_DIR / "trades.csv")
    d001_trade_keys = _trade_key_set(runs["factor_macro_gate_mcap"].trades)
    v1["c014_trade_overlap_jaccard"] = _jaccard(d001_trade_keys, c014_trades)
    v1["d001_trade_count_for_overlap"] = int(len(d001_trade_keys))
    v1["c014_trade_count_for_overlap"] = int(len(c014_trades))

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d006_metrics(
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
    for variant in D006_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()]
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d009_metrics(
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
    for variant in D009_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()].copy()
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]
    z_columns = [column for column in quarterly_regime.columns if column.endswith("_z")]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")
    for column in z_columns:
        name = column.removesuffix("_z")
        series = pd.to_numeric(complete_quarters[column], errors="coerce").dropna()
        v1[f"{name}_z_mean"] = float(series.mean()) if not series.empty else float("nan")
        v1[f"{name}_z_std"] = float(series.std(ddof=0)) if not series.empty else float("nan")
        v1[f"{name}_z_positive_share"] = float(series.gt(0.0).mean()) if not series.empty else float("nan")

    d001_metrics = _read_reference_metrics(D001_OUTPUT_DIR / "metrics.json")
    d001_v1 = d001_metrics.get("factor_macro_gate_mcap", {})
    d001_cost_0 = d001_metrics.get("cost_0_factor_macro_gate_mcap", {})
    d001_net = _float_or_nan(d001_v1.get("cumulative_net_total_return"))
    d001_cost0 = _float_or_nan(d001_cost_0.get("cumulative_net_total_return", d001_v1.get("cost_0_cumulative_net_total_return")))
    v1["d001_cumulative_net_total_return"] = d001_net
    v1["d001_cost_0_cumulative_net_total_return"] = d001_cost0
    v1["d009_minus_d001_cumulative_net_pp"] = v1_return - d001_net
    v1["d009_minus_d001_cost_0_cumulative_net_pp"] = cost_0_return - d001_cost0

    d001_trades = _read_reference_trades_df(D001_OUTPUT_DIR / "trades.csv")
    v1["d001_trade_quarter_overlap_jaccard"] = _jaccard_quarters(
        _quarter_key_set_from_trades(runs["factor_macro_gate_mcap"].trades),
        _quarter_key_set_from_trades(d001_trades),
    )
    d009_on, d001_on = _aligned_quarter_on_sets(quarterly_regime, _read_reference_quarterly_regime(D001_OUTPUT_DIR / "quarterly_regime_log.csv"))
    v1["d009_on_d001_off_quarter_count"] = int(len(d009_on - d001_on))
    v1["d009_off_d001_on_quarter_count"] = int(len(d001_on - d009_on))

    yearly_returns = v1["yearly_net_total_return"]
    v1["return_2025_contribution_share"] = (
        float(yearly_returns.get("2025", float("nan"))) / v1_return if v1_return != 0.0 else float("nan")
    )
    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d001_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    c014_quarterly = _c014_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D001_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["c014_v11_macro_gate_mcap_net_total_return"] = c014_quarterly.get(year, float("nan"))
        row["d001_minus_c014_v11_macro_gate_mcap_return"] = (
            row["factor_macro_gate_mcap_net_total_return"] - row["c014_v11_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d006_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D006_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        rows.append(row)
    return pd.DataFrame(rows)


def _d009_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    d001_quarterly = _d001_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D009_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["d001_factor_macro_gate_mcap_net_total_return"] = d001_quarterly.get(year, float("nan"))
        row["d009_minus_d001_factor_macro_gate_mcap_return"] = (
            row["factor_macro_gate_mcap_net_total_return"] - row["d001_factor_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d008_candidate_years(start: object, end: object, excluded_years: list[object]) -> tuple[int, ...]:
    excluded = {int(year) for year in excluded_years}
    start_year = pd.Timestamp(start).year
    end_year = pd.Timestamp(end).year
    return tuple(year for year in range(start_year, end_year + 1) if year not in excluded)


def _d008_segments_for_subperiod(
    segments: tuple[tuple[object, object], ...],
    start: object,
    end: object,
) -> tuple[tuple[pd.Timestamp, pd.Timestamp], ...]:
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    restricted: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for segment_start, segment_end in segments:
        left = max(pd.Timestamp(segment_start).normalize(), start_ts)
        right = min(pd.Timestamp(segment_end).normalize(), end_ts)
        if left <= right:
            restricted.append((left, right))
    return tuple(restricted)


def _d008_config_for_subperiod(config: dict[str, Any], subperiod: dict[str, Any]) -> dict[str, Any]:
    per_subperiod = dict(config)
    per_subperiod["subperiod"] = dict(subperiod)
    per_subperiod["period"] = dict(config["period"])
    per_subperiod["period"]["start"] = subperiod["start"]
    per_subperiod["period"]["end"] = subperiod["end"]
    per_subperiod.pop("subperiods", None)
    per_subperiod.pop("per_year_analysis", None)
    per_subperiod.pop("rolling_3yr_sharpe", None)
    per_subperiod["output_dir"] = str(Path(config["output_dir"]) / str(subperiod["name"]))
    return per_subperiod


def _d008_subperiod_verdict_summary(name: str, metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    v1 = metrics["factor_macro_gate_mcap"]
    sharpe = float(v1["sharpe"])
    return pd.DataFrame(
        [
            {
                "hypothesis": f"{name}_sharpe_band",
                "description": "D008 pre-registered OOS Sharpe band applied to this isolated trading window",
                "value": sharpe,
                "threshold": 0.30,
                "verdict": _d008_sharpe_verdict(sharpe),
                "passes": bool(sharpe >= 0.30),
            }
        ]
    )


def _d008_verdict_summary(subperiod_table: pd.DataFrame) -> pd.DataFrame:
    indexed = subperiod_table.set_index("subperiod")
    rows: list[dict[str, Any]] = []
    for scheme in ("a", "b", "c"):
        is_name = f"scheme_{scheme}_is"
        oos_name = f"scheme_{scheme}_oos"
        is_sharpe = float(indexed.loc[is_name, "Sharpe"])
        oos_sharpe = float(indexed.loc[oos_name, "Sharpe"])
        rows.append(
            {
                "scheme": scheme.upper(),
                "IS_Sharpe": is_sharpe,
                "OOS_Sharpe": oos_sharpe,
                "IS_net": float(indexed.loc[is_name, "net"]),
                "OOS_net": float(indexed.loc[oos_name, "net"]),
                "IS_annualized": float(indexed.loc[is_name, "annualized"]),
                "OOS_annualized": float(indexed.loc[oos_name, "annualized"]),
                "OOS_ratio_to_IS_Sharpe": oos_sharpe / is_sharpe if is_sharpe != 0.0 else float("nan"),
                "verdict": _d008_sharpe_verdict(oos_sharpe),
            }
        )
    return pd.DataFrame(rows)


def _d008_sharpe_verdict(sharpe: float) -> str:
    if pd.isna(sharpe) or sharpe < 0.10:
        return "OOS_COLLAPSE"
    if sharpe < 0.20:
        return "WEAK"
    if sharpe < 0.30:
        return "MARGINAL"
    if sharpe < 0.40:
        return "ACCEPTABLE"
    return "STRONG"


def _d001_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    aliased = dict(metrics)
    aliased["macro_gate_mcap"] = metrics["factor_macro_gate_mcap"]
    base = _c003_verdict_summary(aliased)
    v1 = metrics["factor_macro_gate_mcap"]
    delta = float(v1["d001_minus_c014_v11_cumulative_net_pp"])
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "D001 cumulative net improves on C014 v11 by >= 5pp",
                "value": delta,
                "threshold": 0.05,
                "passes": bool(delta >= 0.05),
            },
            {
                "hypothesis": "H8",
                "description": "D001 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "Regime ON share and composite/block distributions are descriptive checks",
                "value": float(v1["regime_on_share"]),
                "threshold": "",
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _d009_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    v1 = metrics["factor_macro_gate_mcap"]
    sharpe = float(v1["sharpe"])
    if sharpe >= 0.55:
        verdict = "STRONG ADOPT"
    elif sharpe >= 0.40:
        verdict = "COMPARABLE ADOPT"
    elif sharpe >= 0.30:
        verdict = "MARGINAL"
    else:
        verdict = "KEEP D001"
    return pd.DataFrame(
        [
            {
                "hypothesis": "H1",
                "description": "D009 cumulative net return is positive",
                "value": float(v1["cumulative_net_total_return"]),
                "threshold": 0.0,
                "verdict": "",
                "passes": bool(float(v1["cumulative_net_total_return"]) > 0.0),
            },
            {
                "hypothesis": "H6",
                "description": "D009 net / cost-0 is at least 0.7",
                "value": float(v1["net_to_cost_0_ratio"]),
                "threshold": 0.7,
                "verdict": "",
                "passes": bool(float(v1["net_to_cost_0_ratio"]) >= 0.7),
            },
            {
                "hypothesis": "H7",
                "description": "D009 holistic carrier Sharpe band versus D001 reference",
                "value": sharpe,
                "threshold": "0.55 / 0.40 / 0.30",
                "verdict": verdict,
                "passes": bool(sharpe >= 0.40),
            },
            {
                "hypothesis": "H8",
                "description": "2025 contribution share is descriptive spike-dependency diagnostic",
                "value": float(v1["return_2025_contribution_share"]),
                "threshold": "",
                "verdict": "",
                "passes": pd.NA,
            },
            {
                "hypothesis": "H9",
                "description": "Block scores, variable z-scores, composite distribution, and D001 overlap are descriptive checks",
                "value": float(v1["composite_mean"]),
                "threshold": "",
                "verdict": "",
                "passes": pd.NA,
            },
        ]
    )


def _d010_window_verdict_summary(window: int, metrics: dict[str, dict[str, Any]], warmup: dict[str, Any]) -> pd.DataFrame:
    verdict = _d006_window_verdict_summary(window, metrics, warmup)
    verdict.loc[verdict["hypothesis"].eq("H1"), "description"] = "60-month D010 reproduces D009 Sharpe 0.4144"
    verdict.loc[verdict["hypothesis"].eq("H1"), "threshold"] = 0.4144
    verdict.loc[verdict["hypothesis"].eq("H1"), "passes"] = bool(round(float(metrics["factor_macro_gate_mcap"]["sharpe"]), 4) == 0.4144) if window == 60 else pd.NA
    return verdict


def _d011_threshold_verdict_summary(threshold: float, metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    verdict = _d007_threshold_verdict_summary(threshold, metrics)
    verdict.loc[verdict["hypothesis"].eq("H1"), "description"] = "Threshold 0.0 reproduces D009 Sharpe 0.4144"
    verdict.loc[verdict["hypothesis"].eq("H1"), "threshold_value"] = 0.4144
    verdict.loc[verdict["hypothesis"].eq("H1"), "passes"] = bool(round(float(metrics["factor_macro_gate_mcap"]["sharpe"]), 4) == 0.4144) if threshold == 0.0 else pd.NA
    return verdict


def _d012_subperiod_verdict_summary(name: str, metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    verdict = _d008_subperiod_verdict_summary(name, metrics)
    verdict["description"] = "D012 pre-registered OOS Sharpe band applied to this isolated D009 trading window"
    return verdict


def _d013_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    verdict = _d009_verdict_summary(metrics)
    v1 = metrics["factor_macro_gate_mcap"]
    sharpe = float(v1["sharpe"])
    cumulative = float(v1["cumulative_net_total_return"])
    if sharpe >= 0.50 and cumulative >= 2.0:
        band = "CHAMPION"
    elif sharpe >= 0.45:
        band = "EXCELLENT"
    elif sharpe >= 0.40:
        band = "BETTER THAN D009"
    else:
        band = "RECHECK"
    verdict.loc[verdict["hypothesis"].eq("H1"), "description"] = "D013 reproduces D011 threshold -0.2 cumulative return"
    verdict.loc[verdict["hypothesis"].eq("H1"), "threshold"] = 2.5458
    verdict.loc[verdict["hypothesis"].eq("H1"), "passes"] = bool(round(cumulative, 4) == 2.5458)
    verdict.loc[verdict["hypothesis"].eq("H7"), "description"] = "D013 pre-registered threshold -0.2 Sharpe band"
    verdict.loc[verdict["hypothesis"].eq("H7"), "threshold"] = "0.50+ and 200%+ / 0.45 / 0.40"
    verdict.loc[verdict["hypothesis"].eq("H7"), "verdict"] = band
    verdict.loc[verdict["hypothesis"].eq("H7"), "passes"] = bool(sharpe >= 0.40)
    return verdict


def _d014_window_verdict_summary(window: int, metrics: dict[str, dict[str, Any]], warmup: dict[str, Any]) -> pd.DataFrame:
    verdict = _d006_window_verdict_summary(window, metrics, warmup)
    verdict.loc[verdict["hypothesis"].eq("H1"), "description"] = "60-month D014 reproduces D013 Sharpe 0.5334"
    verdict.loc[verdict["hypothesis"].eq("H1"), "threshold"] = 0.5334
    verdict.loc[verdict["hypothesis"].eq("H1"), "passes"] = bool(round(float(metrics["factor_macro_gate_mcap"]["sharpe"]), 4) == 0.5334) if window == 60 else pd.NA
    return verdict


def _d015_subperiod_verdict_summary(name: str, metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    verdict = _d008_subperiod_verdict_summary(name, metrics)
    verdict["description"] = "D015 pre-registered OOS Sharpe band applied to this isolated D013 trading window"
    return verdict


def _d006_warmup_diagnosis(
    net_result: BacktestResult,
    cost_0_result: BacktestResult,
    calendar: object,
) -> dict[str, Any]:
    start = pd.Timestamp("2010-01-04")
    end = pd.Timestamp("2014-12-31")
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
    trades = net_result.trades.copy()
    if trades.empty:
        trade_count = 0
    else:
        entry_dates = pd.to_datetime(trades["entry_date"], errors="raise")
        trade_count = int(entry_dates.between(start, end).sum())
    return {
        "period": "2010-2014",
        "start": start.date().isoformat(),
        "end": end.date().isoformat(),
        "trade_count": trade_count,
        "net_total_return": net["total_return"],
        "cost_0_total_return": cost_0["total_return"],
    }


def _d006_window_verdict_summary(window: int, metrics: dict[str, dict[str, Any]], warmup: dict[str, Any]) -> pd.DataFrame:
    v1 = metrics["factor_macro_gate_mcap"]
    sharpe = float(v1["sharpe"])
    rows = [
        {
            "window": window,
            "hypothesis": "H1",
            "description": "60-month D006 reproduces D001 Sharpe 0.4842",
            "value": sharpe,
            "threshold": 0.4842,
            "passes": bool(round(sharpe, 4) == 0.4842) if window == 60 else pd.NA,
        },
        {
            "window": window,
            "hypothesis": "H7",
            "description": "Window Sharpe is at least 0.40 for plateau count",
            "value": sharpe,
            "threshold": 0.40,
            "passes": bool(sharpe >= 0.40),
        },
        {
            "window": window,
            "hypothesis": "H8",
            "description": "2010-2014 warmup-artifact trade count and return diagnostic",
            "value": warmup["trade_count"],
            "threshold": ">0 for 36mo/48mo",
            "passes": bool(window not in (36, 48) or int(warmup["trade_count"]) > 0),
        },
        {
            "window": window,
            "hypothesis": "H9",
            "description": "ON share, max DD, and composite distribution are descriptive checks",
            "value": float(v1["regime_on_share"]),
            "threshold": "",
            "passes": pd.NA,
        },
    ]
    return pd.DataFrame(rows)


def _d006_grid_summary_row(
    window: int,
    metrics: dict[str, dict[str, Any]],
    subperiod_breakdown: pd.DataFrame,
    warmup: dict[str, Any],
) -> dict[str, Any]:
    v1 = metrics["factor_macro_gate_mcap"]
    cost_0 = metrics["cost_0_factor_macro_gate_mcap"]
    subperiod = subperiod_breakdown.set_index("period")
    return {
        "window": window,
        "net_cum": float(v1["cumulative_net_total_return"]),
        "cost0_cum": float(cost_0["cumulative_net_total_return"]),
        "Sharpe": float(v1["sharpe"]),
        "MaxDD": float(v1["max_drawdown"]),
        "pos_years": int(v1["positive_years"]),
        "annualized": float(v1["annualized_return"]),
        "ON_share": float(v1["regime_on_share"]),
        "trades": int(v1["trade_count"]),
        "2010-2017_net": float(subperiod.loc["2010-2017", "v1_net_total_return"]),
        "2018-2026_net": float(subperiod.loc["2018-2026", "v1_net_total_return"]),
        "2010-2014_trades": int(warmup["trade_count"]),
        "2010-2014_net": float(warmup["net_total_return"]),
        "composite_mean": float(v1["composite_mean"]),
        "composite_std": float(v1["composite_std"]),
        "composite_positive_share": float(v1["composite_positive_share"]),
    }


def _d006_grid_verdict_summary(grid_summary: pd.DataFrame, window_verdict_rows: list[dict[str, Any]]) -> pd.DataFrame:
    plateau_count = int(pd.to_numeric(grid_summary["Sharpe"], errors="raise").ge(0.40).sum())
    if plateau_count >= 4:
        verdict = "STRONG PLATEAU"
    elif plateau_count == 3:
        verdict = "PLATEAU"
    elif plateau_count == 2:
        verdict = "MARGINAL"
    elif plateau_count == 1:
        verdict = "CLIFF"
    else:
        verdict = "REPRODUCIBILITY FAILURE"
    grid_rows = [
        {
            "scope": "grid",
            "hypothesis": "H7",
            "description": "Pre-registered count of windows with Sharpe >= 0.40",
            "value": plateau_count,
            "threshold": "3 of 5 for plateau; 4 of 5 for strong plateau",
            "passes": bool(plateau_count >= 3),
            "verdict": verdict,
        }
    ]
    window_rows = [dict(row, scope="window", verdict="") for row in window_verdict_rows]
    return pd.DataFrame(grid_rows + window_rows)


def _d006_config_for_window(config: dict[str, Any], window: int) -> dict[str, Any]:
    per_window = dict(config)
    per_window["regime"] = dict(config["regime"])
    per_window["regime"]["z_score_window_months"] = window
    return per_window


def _d007_metrics(
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
    for variant in D007_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()]
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]
    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d007_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D007_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        rows.append(row)
    return pd.DataFrame(rows)


def _d007_threshold_verdict_summary(threshold: float, metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    v1 = metrics["factor_macro_gate_mcap"]
    sharpe = float(v1["sharpe"])
    return pd.DataFrame(
        [
            {
                "threshold": threshold,
                "hypothesis": "H1",
                "description": "Threshold 0.0 reproduces D001 Sharpe 0.4842",
                "value": sharpe,
                "threshold_value": 0.4842,
                "passes": bool(round(sharpe, 4) == 0.4842) if threshold == 0.0 else pd.NA,
            },
            {
                "threshold": threshold,
                "hypothesis": "H7",
                "description": "Threshold Sharpe is at least 0.40 for plateau count",
                "value": sharpe,
                "threshold_value": 0.40,
                "passes": bool(sharpe >= 0.40),
            },
            {
                "threshold": threshold,
                "hypothesis": "H8",
                "description": "ON share, trade count, max DD, and subperiod returns are descriptive checks",
                "value": float(v1["regime_on_share"]),
                "threshold_value": "",
                "passes": pd.NA,
            },
        ]
    )


def _d007_grid_summary_row(
    threshold: float,
    metrics: dict[str, dict[str, Any]],
    subperiod_breakdown: pd.DataFrame,
) -> dict[str, Any]:
    v1 = metrics["factor_macro_gate_mcap"]
    cost_0 = metrics["cost_0_factor_macro_gate_mcap"]
    subperiod = subperiod_breakdown.set_index("period")
    return {
        "threshold": threshold,
        "net_cum": float(v1["cumulative_net_total_return"]),
        "cost0_cum": float(cost_0["cumulative_net_total_return"]),
        "Sharpe": float(v1["sharpe"]),
        "MaxDD": float(v1["max_drawdown"]),
        "pos_years": int(v1["positive_years"]),
        "annualized": float(v1["annualized_return"]),
        "ON_share": float(v1["regime_on_share"]),
        "trades": int(v1["trade_count"]),
        "2010-2017_net": float(subperiod.loc["2010-2017", "v1_net_total_return"]),
        "2018-2026_net": float(subperiod.loc["2018-2026", "v1_net_total_return"]),
        "composite_mean": float(v1["composite_mean"]),
        "composite_std": float(v1["composite_std"]),
        "composite_positive_share": float(v1["composite_positive_share"]),
    }


def _d007_grid_verdict_summary(grid_summary: pd.DataFrame, threshold_verdict_rows: list[dict[str, Any]]) -> pd.DataFrame:
    plateau_count = int(pd.to_numeric(grid_summary["Sharpe"], errors="raise").ge(0.40).sum())
    if plateau_count >= 4:
        verdict = "STRONG PLATEAU"
    elif plateau_count == 3:
        verdict = "PLATEAU"
    elif plateau_count == 2:
        verdict = "MARGINAL"
    elif plateau_count == 1:
        verdict = "CLIFF"
    else:
        verdict = "REPRODUCIBILITY FAILURE"
    grid_rows = [
        {
            "scope": "grid",
            "hypothesis": "H7",
            "description": "Pre-registered count of thresholds with Sharpe >= 0.40",
            "value": plateau_count,
            "threshold": "3 of 5 for plateau; 4 of 5 for strong plateau",
            "passes": bool(plateau_count >= 3),
            "verdict": verdict,
        }
    ]
    threshold_rows = [dict(row, scope="threshold", verdict="") for row in threshold_verdict_rows]
    return pd.DataFrame(grid_rows + threshold_rows)


def _d007_threshold_slug(threshold: float) -> str:
    sign = "p" if threshold >= 0.0 else "m"
    magnitude = f"{abs(threshold):.1f}".replace(".", "p")
    return f"{sign}{magnitude}"


def _d007_config_for_threshold(config: dict[str, Any], threshold: float) -> dict[str, Any]:
    per_threshold = dict(config)
    per_threshold["regime"] = dict(config["regime"])
    per_threshold["regime"]["on_threshold"] = threshold
    return per_threshold


def _d002_metrics(
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
    for variant in D002_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()]
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["d001_cumulative_net_total_return"] = D001_CUMULATIVE_NET
    v1["d001_cost_0_cumulative_net_total_return"] = D001_COST_0_CUMULATIVE_NET
    v1["d002_minus_d001_cumulative_net_pp"] = v1_return - D001_CUMULATIVE_NET
    v1["d002_minus_d001_cost_0_cumulative_net_pp"] = cost_0_return - D001_COST_0_CUMULATIVE_NET
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["d002_minus_c014_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["d002_minus_c014_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    c014_trades = _read_reference_trades(C014_QUARTERLY_OUTPUT_DIR / "trades.csv")
    d002_trade_keys = _trade_key_set(runs["factor_macro_gate_mcap"].trades)
    v1["c014_trade_overlap_jaccard"] = _jaccard(d002_trade_keys, c014_trades)
    v1["d002_trade_count_for_overlap"] = int(len(d002_trade_keys))
    v1["c014_trade_count_for_overlap"] = int(len(c014_trades))
    v1["d001_trade_count_reference"] = D001_TRADE_COUNT
    v1["d002_minus_d001_trade_count"] = int(v1["trade_count"]) - D001_TRADE_COUNT
    trades = runs["factor_macro_gate_mcap"].trades
    if trades.empty:
        v1["trade_count_2010_2014"] = 0
    else:
        entry_dates = pd.to_datetime(trades["entry_date"], errors="raise")
        in_warmup_check = entry_dates.between(pd.Timestamp("2010-01-01"), pd.Timestamp("2014-12-31"))
        v1["trade_count_2010_2014"] = int(in_warmup_check.sum())

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d002_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    d001_quarterly = _d001_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D002_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["d001_factor_macro_gate_mcap_net_total_return"] = d001_quarterly.get(year, float("nan"))
        row["d002_minus_d001_factor_macro_gate_mcap_return"] = (
            row["factor_macro_gate_mcap_net_total_return"] - row["d001_factor_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d002_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    aliased = dict(metrics)
    aliased["macro_gate_mcap"] = metrics["factor_macro_gate_mcap"]
    base = _c003_verdict_summary(aliased)
    v1 = metrics["factor_macro_gate_mcap"]
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "D002 Sharpe >= 0.40 and 2010-2014 trade count > 0",
                "value": float(v1["sharpe"]),
                "threshold": 0.40,
                "passes": bool(float(v1["sharpe"]) >= 0.40 and int(v1["trade_count_2010_2014"]) > 0),
            },
            {
                "hypothesis": "H8",
                "description": "D002 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "Regime ON share and composite/block distributions are descriptive checks",
                "value": float(v1["regime_on_share"]),
                "threshold": "",
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _d003_metrics(
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
    for variant in D003_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()]
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["d001_cumulative_net_total_return"] = D001_CUMULATIVE_NET
    v1["d001_cost_0_cumulative_net_total_return"] = D001_COST_0_CUMULATIVE_NET
    v1["d003_minus_d001_cumulative_net_pp"] = v1_return - D001_CUMULATIVE_NET
    v1["d003_minus_d001_cost_0_cumulative_net_pp"] = cost_0_return - D001_COST_0_CUMULATIVE_NET
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["d003_minus_c014_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["d003_minus_c014_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    for block_name, columns in {
        "usd_fx": ("usdkrw_yoy_fav_score", "dxy_yoy_fav_score", "usdcny_yoy_fav_score"),
        "rates": (
            "us_2_10_curve_fav_score",
            "kr10y_yoy_change_fav_score",
            "kr3m_yoy_change_fav_score",
            "jp10y_yoy_change_fav_score",
        ),
        "inflation": ("us_cpi_decel_fav_score", "us_ppi_decel_fav_score", "kr_cpi_decel_fav_score"),
    }.items():
        v1[f"{block_name}_within_block_avg_std"] = (
            float(complete_quarters.loc[:, list(columns)].std(axis=1, ddof=0).mean())
            if not complete_quarters.empty
            else float("nan")
        )

    d001_trades = _read_reference_trades(D001_OUTPUT_DIR / "trades.csv")
    d003_trade_keys = _trade_key_set(runs["factor_macro_gate_mcap"].trades)
    v1["d001_trade_overlap_jaccard"] = _jaccard(d003_trade_keys, d001_trades)
    v1["d003_trade_count_for_overlap"] = int(len(d003_trade_keys))
    v1["d001_trade_count_for_overlap"] = int(len(d001_trades))

    trades = runs["factor_macro_gate_mcap"].trades
    if trades.empty:
        v1["trade_count_2010_2014"] = 0
        v1["subperiod_2010_2017_trade_count"] = 0
        v1["subperiod_2018_2026_trade_count"] = 0
    else:
        entry_dates = pd.to_datetime(trades["entry_date"], errors="raise")
        v1["trade_count_2010_2014"] = int(entry_dates.between("2010-01-01", "2014-12-31").sum())
        v1["subperiod_2010_2017_trade_count"] = int(entry_dates.between("2010-01-01", "2017-12-31").sum())
        v1["subperiod_2018_2026_trade_count"] = int(entry_dates.between("2018-01-01", "2026-12-31").sum())

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d003_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    d001_quarterly = _d001_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D003_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["d001_factor_macro_gate_mcap_net_total_return"] = d001_quarterly.get(year, float("nan"))
        row["d003_minus_d001_factor_macro_gate_mcap_return"] = (
            row["factor_macro_gate_mcap_net_total_return"] - row["d001_factor_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d003_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    aliased = dict(metrics)
    aliased["macro_gate_mcap"] = metrics["factor_macro_gate_mcap"]
    base = _c003_verdict_summary(aliased)
    v1 = metrics["factor_macro_gate_mcap"]
    h7_pass = (
        float(v1["d003_minus_d001_cumulative_net_pp"]) >= 0.0
        or (float(v1["sharpe"]) >= 0.48 and float(v1["max_drawdown"]) >= -0.2367)
    ) and float(v1["sharpe"]) >= 0.40
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "D003 block expansion improves D001 net, or improves/holds risk-adjusted profile with Sharpe >= 0.40",
                "value": float(v1["d003_minus_d001_cumulative_net_pp"]),
                "threshold": 0.0,
                "passes": bool(h7_pass),
            },
            {
                "hypothesis": "H8",
                "description": "D003 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "Block scores, within-block dispersion, composite distribution, ON share, and D001 overlap are descriptive checks",
                "value": float(v1["regime_on_share"]),
                "threshold": "",
                "passes": pd.NA,
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _d004_metrics(
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
    for variant in D004_VARIANTS:
        block = dict(compute_metrics(runs[variant].equity_curve, runs[variant].trades, calendar))
        yearly_returns = _b011_year_returns(runs[variant], calendar, candidate_years)
        block["cumulative_net_total_return"] = block["total_return"]
        block["yearly_net_total_return"] = {str(year): value for year, value in yearly_returns.items()}
        block["positive_years"] = int(sum(value > 0.0 for value in yearly_returns.values()))
        metrics[variant] = block

    zero_result = run_quarterly_sized_mcap_backtest(
        panel=panel,
        calendar=calendar,
        candidates=candidates,
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=segments,
        rebalance_dates=quarterly_execution_dates(calendar, quarterly_regime, segments),
    )
    cost_0 = dict(compute_metrics(zero_result.equity_curve, zero_result.trades, calendar))
    cost_0["cumulative_net_total_return"] = cost_0["total_return"]
    metrics["cost_0_factor_macro_sized_mcap"] = cost_0

    v1 = metrics["factor_macro_sized_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()].copy()
    exposure = pd.to_numeric(complete_quarters["exposure_scalar"], errors="raise")
    partial = complete_quarters.loc[exposure.gt(0.0) & exposure.lt(1.0)]
    full = complete_quarters.loc[exposure.eq(1.0)]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["d001_cumulative_net_total_return"] = D001_CUMULATIVE_NET
    v1["d001_cost_0_cumulative_net_total_return"] = D001_COST_0_CUMULATIVE_NET
    v1["d004_minus_d001_cumulative_net_pp"] = v1_return - D001_CUMULATIVE_NET
    v1["d004_minus_d001_cost_0_cumulative_net_pp"] = cost_0_return - D001_COST_0_CUMULATIVE_NET
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["d004_minus_c014_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["d004_minus_c014_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    v1["exposure_scalar_mean"] = float(exposure.mean()) if not exposure.empty else float("nan")
    v1["exposure_scalar_std"] = float(exposure.std(ddof=0)) if not exposure.empty else float("nan")
    v1["exposure_scalar_zero_share"] = float(exposure.eq(0.0).mean()) if not exposure.empty else float("nan")
    v1["exposure_scalar_one_share"] = float(exposure.eq(1.0).mean()) if not exposure.empty else float("nan")
    v1["exposure_scalar_partial_share"] = (
        float((exposure.gt(0.0) & exposure.lt(1.0)).mean()) if not exposure.empty else float("nan")
    )
    on_exposure = exposure.loc[exposure.gt(0.0)]
    v1["on_quarters_mean_exposure"] = float(on_exposure.mean()) if not on_exposure.empty else float("nan")
    v1["partial_exposure_quarter_count"] = int(len(partial))
    v1["full_exposure_quarter_count"] = int(len(full))

    scatter = _d004_magnitude_return_scatter(quarterly_regime, runs["factor_macro_sized_mcap"])
    partial_scatter = scatter.loc[scatter["exposure_scalar"].gt(0.0) & scatter["exposure_scalar"].lt(1.0)]
    full_scatter = scatter.loc[scatter["exposure_scalar"].eq(1.0)]
    v1["partial_exposure_quarter_avg_return"] = (
        float(partial_scatter["forward_quarter_return"].mean()) if not partial_scatter.empty else float("nan")
    )
    v1["full_exposure_quarter_cumulative_gain"] = _compound_return(full_scatter["forward_quarter_return"])
    v1["partial_exposure_quarter_cumulative_gain"] = _compound_return(partial_scatter["forward_quarter_return"])

    d001_quarters = _quarter_key_set_from_trades(_read_reference_trades_df(D001_OUTPUT_DIR / "trades.csv"))
    d004_quarters = _quarter_key_set_from_trades(runs["factor_macro_sized_mcap"].trades)
    v1["d001_quarter_overlap_jaccard"] = _jaccard_quarters(d004_quarters, d001_quarters)
    v1["d004_quarter_count_for_overlap"] = int(len(d004_quarters))
    v1["d001_quarter_count_for_overlap"] = int(len(d001_quarters))

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_sized_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d004_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    d001_quarterly = _d001_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D004_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["d001_factor_macro_gate_mcap_net_total_return"] = d001_quarterly.get(year, float("nan"))
        row["d004_minus_d001_factor_macro_return"] = (
            row["factor_macro_sized_mcap_net_total_return"] - row["d001_factor_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d004_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    aliased = {
        "macro_gate_mcap": metrics["factor_macro_sized_mcap"],
        "kospi_buy_and_hold": metrics["kospi_buy_and_hold"],
        "cash": metrics["cash"],
    }
    base = _c003_verdict_summary(aliased)
    v1 = metrics["factor_macro_sized_mcap"]
    h7_strong = float(v1["sharpe"]) >= 0.48 and float(v1["cumulative_net_total_return"]) >= D001_CUMULATIVE_NET
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "D004 sizing improves Sharpe versus D001 or cumulative net versus D001; strong if both pass",
                "value": float(v1["d004_minus_d001_cumulative_net_pp"]),
                "threshold": 0.0,
                "passes": bool(float(v1["sharpe"]) >= 0.48 or float(v1["cumulative_net_total_return"]) >= D001_CUMULATIVE_NET),
            },
            {
                "hypothesis": "H8",
                "description": "Composite magnitude diagnostics: ON-quarter exposure and partial-vs-full quarter returns",
                "value": float(v1["on_quarters_mean_exposure"]),
                "threshold": "",
                "passes": pd.NA,
            },
            {
                "hypothesis": "H9",
                "description": "Exposure scalar distribution and D001 quarter overlap are descriptive checks",
                "value": float(v1["exposure_scalar_mean"]),
                "threshold": "",
                "passes": pd.NA,
            },
            {
                "hypothesis": "H7_STRONG",
                "description": "Sharpe >= D001 0.48 and cumulative net >= D001 +129.07%",
                "value": float(v1["sharpe"]),
                "threshold": 0.48,
                "passes": bool(h7_strong),
            },
        ]
    )
    return pd.concat([base, h7_h9], ignore_index=True)


def _d005_metrics(
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
    for variant in D005_VARIANTS:
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
    metrics["cost_0_factor_macro_gate_mcap"] = cost_0

    v1 = metrics["factor_macro_gate_mcap"]
    cost_0_return = float(cost_0["cumulative_net_total_return"])
    v1_return = float(v1["cumulative_net_total_return"])
    complete_quarters = quarterly_regime.loc[quarterly_regime["composite"].notna()].copy()
    block_columns = [column for column in quarterly_regime.columns if column.startswith("block_") and column.endswith("_score")]

    v1["cost_0_cumulative_net_total_return"] = cost_0_return
    v1["net_to_cost_0_ratio"] = v1_return / cost_0_return if cost_0_return != 0.0 else float("nan")
    v1["d001_cumulative_net_total_return"] = D001_CUMULATIVE_NET
    v1["d001_cost_0_cumulative_net_total_return"] = D001_COST_0_CUMULATIVE_NET
    v1["d005_minus_d001_cumulative_net_pp"] = v1_return - D001_CUMULATIVE_NET
    v1["d005_minus_d001_cost_0_cumulative_net_pp"] = cost_0_return - D001_COST_0_CUMULATIVE_NET
    v1["c014_v11_cumulative_net_total_return"] = C014_QUARTERLY_CUMULATIVE_NET
    v1["c014_v11_cost_0_cumulative_net_total_return"] = C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["d005_minus_c014_v11_cumulative_net_pp"] = v1_return - C014_QUARTERLY_CUMULATIVE_NET
    v1["d005_minus_c014_v11_cost_0_cumulative_net_pp"] = cost_0_return - C014_QUARTERLY_COST_0_CUMULATIVE_NET
    v1["regime_on_share"] = float(quarterly_regime["regime_on"].mean()) if not quarterly_regime.empty else float("nan")
    v1["regime_on_share_complete_quarters"] = (
        float(complete_quarters["regime_on"].mean()) if not complete_quarters.empty else float("nan")
    )
    v1["composite_mean"] = float(complete_quarters["composite"].mean()) if not complete_quarters.empty else float("nan")
    v1["composite_std"] = float(complete_quarters["composite"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["composite_positive_share"] = (
        float(complete_quarters["composite"].ge(0.0).mean()) if not complete_quarters.empty else float("nan")
    )
    for column in block_columns:
        metric_name = column.removeprefix("block_").removesuffix("_score") + "_avg_score"
        v1[metric_name] = float(complete_quarters[column].mean()) if not complete_quarters.empty else float("nan")

    pair = complete_quarters.loc[:, ["kr_exports_yoy_z", "kr_cli_value_z"]].dropna()
    v1["kr_exports_yoy_z_mean"] = float(complete_quarters["kr_exports_yoy_z"].mean()) if not complete_quarters.empty else float("nan")
    v1["kr_exports_yoy_z_std"] = float(complete_quarters["kr_exports_yoy_z"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["kr_cli_value_z_mean"] = float(complete_quarters["kr_cli_value_z"].mean()) if not complete_quarters.empty else float("nan")
    v1["kr_cli_value_z_std"] = float(complete_quarters["kr_cli_value_z"].std(ddof=0)) if not complete_quarters.empty else float("nan")
    v1["kr_exports_yoy_z_kr_cli_value_z_correlation"] = (
        float(pair["kr_exports_yoy_z"].corr(pair["kr_cli_value_z"])) if len(pair) >= 2 else float("nan")
    )

    d001_quarters = _quarter_key_set_from_trades(_read_reference_trades_df(D001_OUTPUT_DIR / "trades.csv"))
    d005_quarters = _quarter_key_set_from_trades(runs["factor_macro_gate_mcap"].trades)
    v1["d001_quarter_overlap_jaccard"] = _jaccard_quarters(d005_quarters, d001_quarters)
    v1["d005_quarter_count_for_overlap"] = int(len(d005_quarters))
    v1["d001_quarter_count_for_overlap"] = int(len(d001_quarters))
    d001_regime = _read_reference_quarterly_regime(D001_OUTPUT_DIR / "quarterly_regime_log.csv")
    d005_on, d001_on = _aligned_quarter_on_sets(quarterly_regime, d001_regime)
    v1["d005_on_d001_off_quarter_count"] = int(len(d005_on - d001_on))
    v1["d005_off_d001_on_quarter_count"] = int(len(d001_on - d005_on))

    trades = runs["factor_macro_gate_mcap"].trades
    if trades.empty:
        v1["trade_count_2010_2014"] = 0
        v1["subperiod_2010_2017_trade_count"] = 0
        v1["subperiod_2018_2026_trade_count"] = 0
    else:
        entry_dates = pd.to_datetime(trades["entry_date"], errors="raise")
        v1["trade_count_2010_2014"] = int(entry_dates.between("2010-01-01", "2014-12-31").sum())
        v1["subperiod_2010_2017_trade_count"] = int(entry_dates.between("2010-01-01", "2017-12-31").sum())
        v1["subperiod_2018_2026_trade_count"] = int(entry_dates.between("2018-01-01", "2026-12-31").sum())

    subperiod = _c010_subperiod_breakdown(runs["factor_macro_gate_mcap"], zero_result, calendar)
    for _, row in subperiod.iterrows():
        prefix = str(row["period"]).replace("-", "_")
        v1[f"subperiod_{prefix}_net_total_return"] = float(row["v1_net_total_return"])
        v1[f"subperiod_{prefix}_cost_0_total_return"] = float(row["v1_cost_0_total_return"])
    return metrics, zero_result


def _d005_year_breakdown(
    *,
    runs: dict[str, BacktestResult],
    calendar: object,
    candidate_years: tuple[int, ...],
) -> pd.DataFrame:
    d001_quarterly = _d001_quarterly_year_reference()
    rows = []
    for year in candidate_years:
        row: dict[str, Any] = {"year": year}
        for variant in D005_VARIANTS:
            row[f"{variant}_net_total_return"] = _b011_year_returns(runs[variant], calendar, (year,))[year]
        row["d001_factor_macro_gate_mcap_net_total_return"] = d001_quarterly.get(year, float("nan"))
        row["d005_minus_d001_factor_macro_gate_mcap_return"] = (
            row["factor_macro_gate_mcap_net_total_return"] - row["d001_factor_macro_gate_mcap_net_total_return"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _d005_verdict_summary(metrics: dict[str, dict[str, Any]]) -> pd.DataFrame:
    aliased = dict(metrics)
    aliased["macro_gate_mcap"] = metrics["factor_macro_gate_mcap"]
    base = _c003_verdict_summary(aliased)
    v1 = metrics["factor_macro_gate_mcap"]
    h7_pass = (
        float(v1["d005_minus_d001_cumulative_net_pp"]) >= 0.0
        or (float(v1["sharpe"]) >= 0.48 and float(v1["max_drawdown"]) >= -0.2367)
    ) and float(v1["sharpe"]) >= 0.40
    h7_h9 = pd.DataFrame(
        [
            {
                "hypothesis": "H7",
                "description": "D005 improves D001 net, or improves/holds risk-adjusted profile with Sharpe >= 0.40",
                "value": float(v1["d005_minus_d001_cumulative_net_pp"]),
                "threshold": 0.0,
                "passes": bool(h7_pass),
            },
            {
                "hypothesis": "H8",
                "description": "D005 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026",
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
                "description": "B7 block effect, composite distribution, ON share, and D001 overlap are descriptive checks",
                "value": float(v1["korea_growth_avg_score"]),
                "threshold": "",
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


def _c013_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c014_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c015_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c016_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c017_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c018_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c019_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _c020_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _c011_wide_equity_curve(runs)


def _d001_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["factor_macro_gate_mcap"].equity_curve["date"],
            "V1_factor_macro_gate_mcap_net_value": runs["factor_macro_gate_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _d002_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _d001_wide_equity_curve(runs)


def _d003_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _d001_wide_equity_curve(runs)


def _d005_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _d001_wide_equity_curve(runs)


def _d006_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _d001_wide_equity_curve(runs)


def _d007_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return _d001_wide_equity_curve(runs)


def _d004_wide_equity_curve(runs: dict[str, BacktestResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": runs["factor_macro_sized_mcap"].equity_curve["date"],
            "V1_factor_macro_sized_mcap_net_value": runs["factor_macro_sized_mcap"].equity_curve["net_value"],
            "V2_kospi_buy_and_hold_net_value": runs["kospi_buy_and_hold"].equity_curve["net_value"],
            "V3_cash_net_value": runs["cash"].equity_curve["net_value"],
        }
    )


def _d004_signals(candidates: pd.DataFrame) -> pd.DataFrame:
    signals = _c008_signals(candidates)
    if candidates.empty:
        signals["target_weight"] = pd.Series(dtype="float64")
        signals["exposure_scalar"] = pd.Series(dtype="float64")
        return signals
    extras = candidates.loc[:, ["signal_date", "execution_date", "종목코드", "target_weight", "exposure_scalar"]].copy()
    extras["ticker"] = extras["종목코드"].astype(str).str.zfill(6)
    merged = signals.merge(
        extras.loc[:, ["signal_date", "execution_date", "ticker", "target_weight", "exposure_scalar"]],
        on=["signal_date", "execution_date", "ticker"],
        how="left",
        validate="one_to_one",
    )
    return merged


def _d004_exposure_distribution(quarterly_regime: pd.DataFrame) -> pd.DataFrame:
    data = quarterly_regime.loc[quarterly_regime["composite"].notna(), ["signal_date", "composite", "exposure_scalar"]].copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["quarter"] = data["signal_date"].dt.to_period("Q").astype(str)
    data["is_zero"] = data["exposure_scalar"].eq(0.0)
    data["is_full"] = data["exposure_scalar"].eq(1.0)
    data["is_partial"] = data["exposure_scalar"].gt(0.0) & data["exposure_scalar"].lt(1.0)
    return data.loc[:, ["signal_date", "quarter", "composite", "exposure_scalar", "is_zero", "is_partial", "is_full"]]


def _d004_magnitude_return_scatter(quarterly_regime: pd.DataFrame, result: BacktestResult) -> pd.DataFrame:
    exposure = _d004_exposure_distribution(quarterly_regime)
    if exposure.empty:
        return pd.DataFrame(columns=["signal_date", "quarter", "composite", "exposure_scalar", "forward_quarter_return"])
    nav = result.equity_curve.loc[:, ["date", "net_value"]].copy()
    nav["date"] = pd.to_datetime(nav["date"], errors="raise").dt.normalize()
    nav["net_value"] = pd.to_numeric(nav["net_value"], errors="raise")
    rows = []
    exposure = exposure.sort_values("signal_date").reset_index(drop=True)
    start_dates: list[pd.Timestamp | pd.NaT] = []
    for signal_date in exposure["signal_date"]:
        future = nav.loc[nav["date"].gt(pd.Timestamp(signal_date).normalize())]
        start_dates.append(pd.NaT if future.empty else pd.Timestamp(future.iloc[0]["date"]).normalize())
    for index, row in exposure.iterrows():
        signal_date = pd.Timestamp(row["signal_date"]).normalize()
        start_date = start_dates[index]
        if pd.isna(start_date):
            forward_return = float("nan")
        else:
            next_start = start_dates[index + 1] if index + 1 < len(start_dates) else pd.NaT
            if pd.isna(next_start):
                end_source = nav.loc[nav["date"].ge(start_date)]
            else:
                end_source = nav.loc[nav["date"].ge(start_date) & nav["date"].lt(next_start)]
            if end_source.empty:
                forward_return = float("nan")
                rows.append(
                    {
                        "signal_date": signal_date,
                        "quarter": row["quarter"],
                        "composite": row["composite"],
                        "exposure_scalar": row["exposure_scalar"],
                        "forward_quarter_return": forward_return,
                    }
                )
                continue
            start_nav = float(nav.loc[nav["date"].eq(start_date), "net_value"].iloc[0])
            end_nav = float(end_source.iloc[-1]["net_value"])
            forward_return = end_nav / start_nav - 1.0 if start_nav != 0.0 else float("nan")
        rows.append(
            {
                "signal_date": signal_date,
                "quarter": row["quarter"],
                "composite": row["composite"],
                "exposure_scalar": row["exposure_scalar"],
                "forward_quarter_return": forward_return,
            }
        )
    return pd.DataFrame(rows)


def _compound_return(returns: pd.Series) -> float:
    values = pd.to_numeric(returns, errors="coerce").dropna()
    if values.empty:
        return float("nan")
    return float((1.0 + values).prod() - 1.0)


def _d001_blocks_from_config(blocks: list[dict[str, Any]]) -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    parsed = []
    for block in blocks:
        parsed.append(
            (
                str(block["name"]),
                tuple((str(variable["name"]), int(variable["sign"])) for variable in block["vars"]),
            )
        )
    return tuple(parsed)


def _trade_key_set(trades: pd.DataFrame) -> set[tuple[pd.Timestamp, pd.Timestamp, str]]:
    if trades.empty:
        return set()
    return {
        (
            pd.Timestamp(row["signal_date"]).normalize(),
            pd.Timestamp(row["entry_date"]).normalize(),
            str(row["종목코드"]).zfill(6),
        )
        for _, row in trades.iterrows()
    }


def _read_reference_trades(path: Path) -> set[tuple[pd.Timestamp, pd.Timestamp, str]]:
    if not path.exists():
        return set()
    return _trade_key_set(pd.read_csv(path, dtype={"종목코드": "string"}))


def _read_reference_trades_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=TRADE_COLUMNS)
    return pd.read_csv(path, dtype={"종목코드": "string"})


def _read_reference_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_reference_quarterly_regime(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["signal_date", "regime_on"])
    return pd.read_csv(path)


def _float_or_nan(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _jaccard(left: set[tuple[pd.Timestamp, pd.Timestamp, str]], right: set[tuple[pd.Timestamp, pd.Timestamp, str]]) -> float:
    union = left | right
    if not union:
        return float("nan")
    return len(left & right) / len(union)


def _quarter_key_set_from_trades(trades: pd.DataFrame) -> set[str]:
    if trades.empty:
        return set()
    signal_dates = pd.to_datetime(trades["signal_date"], errors="raise").dt.to_period("Q")
    return set(signal_dates.astype(str))


def _jaccard_quarters(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return float("nan")
    return len(left & right) / len(union)


def _aligned_quarter_on_sets(left: pd.DataFrame, right: pd.DataFrame) -> tuple[set[str], set[str]]:
    if left.empty or right.empty:
        return set(), set()
    left_data = left.loc[:, ["signal_date", "regime_on"]].copy()
    right_data = right.loc[:, ["signal_date", "regime_on"]].copy()
    left_data["quarter"] = pd.to_datetime(left_data["signal_date"], errors="raise").dt.to_period("Q").astype(str)
    right_data["quarter"] = pd.to_datetime(right_data["signal_date"], errors="raise").dt.to_period("Q").astype(str)
    left_on = set(left_data.loc[left_data["regime_on"].astype(bool), "quarter"])
    right_on = set(right_data.loc[right_data["regime_on"].astype(bool), "quarter"])
    return left_on, right_on


def _d005_b7_block_diagnostics(quarterly_regime: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "signal_date",
        "block_korea_growth_score",
        "kr_exports_yoy_z",
        "kr_cli_value_z",
        "kr_exports_yoy_fav_score",
        "kr_cli_value_fav_score",
    ]
    available = [column for column in columns if column in quarterly_regime.columns]
    data = quarterly_regime.loc[:, available].copy()
    if data.empty:
        return pd.DataFrame(columns=[*columns, "quarter", "kr_exports_z_cli_z_correlation_full"])
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["quarter"] = data["signal_date"].dt.to_period("Q").astype(str)
    pair = data.loc[:, ["kr_exports_yoy_z", "kr_cli_value_z"]].dropna()
    data["kr_exports_z_cli_z_correlation_full"] = (
        float(pair["kr_exports_yoy_z"].corr(pair["kr_cli_value_z"])) if len(pair) >= 2 else float("nan")
    )
    return data.loc[:, [*columns, "quarter", "kr_exports_z_cli_z_correlation_full"]]


def _d009_block_diagnostics(quarterly_regime: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "signal_date",
        "block_global_risk_score",
        "block_usd_fx_score",
        "block_us_rates_score",
        "block_inflation_score",
        "block_growth_score",
        "vix_60d_vs_240d_z",
        "baa10y_spread_level_z",
        "usdkrw_yoy_z",
        "dxy_yoy_z",
        "us_10y_real_level_z",
        "us_2_10_curve_z",
        "brent_yoy_z",
        "us_breakeven_level_z",
        "kr_cli_value_z",
        "kr_exports_yoy_z",
        "composite",
        "regime_on",
    ]
    available = [column for column in columns if column in quarterly_regime.columns]
    data = quarterly_regime.loc[:, available].copy()
    if data.empty:
        return pd.DataFrame(columns=[*columns, "quarter"])
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["quarter"] = data["signal_date"].dt.to_period("Q").astype(str)
    return data.loc[:, [*available, "quarter"]]


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


def _c013_quarterly_year_reference() -> dict[int, float]:
    path = C013_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _c014_quarterly_year_reference() -> dict[int, float]:
    path = C014_QUARTERLY_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["macro_gate_mcap_net_total_return"])
    }


def _d001_quarterly_year_reference() -> dict[int, float]:
    path = D001_OUTPUT_DIR / "quarterly_year_breakdown.csv"
    if not path.exists():
        return {}
    data = pd.read_csv(path)
    return {
        int(row["year"]): float(row["factor_macro_gate_mcap_net_total_return"])
        for _, row in data.iterrows()
        if not pd.isna(row["factor_macro_gate_mcap_net_total_return"])
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


def _write_c013_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C013 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c011_v8_reference | C011 v8 quarterly cumulative net +55.00%; cost-0 +83.35%; yearly columns read from C011 output files |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_cpi_formula | CPI yoy is CPI(T) / CPI(T-12 months) - 1; CPI decel is CPI yoy(T) - CPI yoy(T-12 months); favorable when decel <= 0 |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c013_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c014_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C014 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c013_v10_reference | C013 v10 quarterly cumulative net +81.29%; cost-0 +112.34%; yearly columns read from C013 output files |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| us_ppi_formula | PPI yoy is PPI(T) / PPI(T-12 months) - 1; PPI decel is PPI yoy(T) - PPI yoy(T-12 months); favorable when decel <= 0 |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c014_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c015_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C015 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, US UNRATE yoy change >= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| us_unrate_timing | UNRATE is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only UNRATE releases available by the signal date |",
            "| us_unrate_formula | UNRATE yoy change is UNRATE(T) - UNRATE(T-12 months), in percentage points; favorable when yoy change >= 0 |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c015_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c016_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C016 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, KR CPI yoy decel <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| kr_cpi_timing | KORCPALTT01CTGYM is monthly and already yoy percent; each observation is treated as available 14 days after month-end |",
            "| kr_cpi_formula | KR CPI decel is KORCPALTT01CTGYM(T) - KORCPALTT01CTGYM(T-12 months); favorable when decel <= 0 |",
            "| kr_cpi_gap_policy | if the latest KR CPI observation is stale by more than 62 days at the signal date, KR_CPI_yoy and KR_CPI_decel are unavailable and favorable_KR_CPI is False |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c016_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c017_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C017 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, KR exports yoy >= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| kr_exports_timing | XTEXVA01KRM664S is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only exports releases available by the signal date |",
            "| kr_exports_formula | KR exports yoy is XTEXVA01KRM664S(T) / XTEXVA01KRM664S(T-12 months) - 1; favorable when yoy >= 0 |",
            "| kr_exports_sign | growth is favorable, unlike declining-favorable Brent/CPI/PPI/KR10y signals |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c017_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c018_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C018 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, US M2 yoy >= 5%; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| us_m2_timing | M2SL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only M2 releases available by the signal date |",
            "| us_m2_formula | US M2 yoy is M2SL(T) / M2SL(T-12 months) - 1; favorable when yoy >= 0.05 |",
            "| us_m2_sign | growth at or above 5% is favorable as an expansionary monetary stance |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c018_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c019_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C019 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, USDJPY yoy >= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| usdjpy_timing | DEXJPUS is daily FRED data with U.S. after-close timing, so Korean signal date T uses observations dated T-1 or earlier |",
            "| usdjpy_formula | USDJPY yoy is DEXJPUS(T) / DEXJPUS(T-252 trading days) - 1; favorable when yoy >= 0 |",
            "| usdjpy_sign | yen weakening is favorable because JPY is treated as the carry-trade funding currency, inverse to the USDKRW asset-currency sign |",
            "| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |",
            "| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c019_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_c020_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# C020 Metrics Summary", ""]
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
            "| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, JP10y yoy change <= 0; ON when score >= 2 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| jp10y_timing | IRLTLT01JPM156N is monthly FRED data; each observation is treated as available 14 days after month-end, so quarter-end signals use only releases available by the signal date |",
            "| jp10y_formula | JP10y yoy change is JGB10Y(T) - JGB10Y(T-12 months), in percentage points; favorable when <= 0 |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_c020_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d001_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D001 Metrics Summary", ""]
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
            "| macro_gate | C014 eight raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d001_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d009_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    block_diagnostics: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D009 Metrics Summary", ""]
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
            "| macro_gate | D009 ten raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight two-variable blocks; ON when composite >= 0 |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Block Diagnostics", block_diagnostics))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d008_subperiod_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D008 Subperiod Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| subperiod | {config['subperiod']['name']} |",
            f"| trading_start | {config['subperiod']['start']} |",
            f"| trading_end | {config['subperiod']['end']} |",
            "| macro_gate | frozen D001 factor aggregation; only trading window is restricted |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d001_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d008_report(
    output_dir: Path,
    config: dict[str, Any],
    subperiod_table: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    rolling: pd.DataFrame,
    verdict: pd.DataFrame,
    spike: pd.DataFrame,
) -> None:
    lines = ["# D008 OOS Subperiod Split Metrics Summary", ""]
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
            "| macro_gate | frozen D001 factor aggregation; only trading window changes by subperiod |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Subperiod Table", subperiod_table))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Rolling 3-Year Sharpe", rolling))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    lines.extend(_b004_dataframe_table("Spike Year Contribution", spike))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d010_window_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    warmup: dict[str, Any],
    verdict: pd.DataFrame,
) -> None:
    window = int(config["regime"]["z_score_window_months"])
    lines = [f"# D010 {window}mo Metrics Summary", ""]
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
            f"| macro_gate | D009 ten variables transformed to {window}-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |",
            f"| z_score_warmup | rows with fewer than {window} monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("2010-2014 Warmup Diagnosis", pd.DataFrame([warmup])))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d010_report(
    output_dir: Path,
    config: dict[str, Any],
    grid_summary: pd.DataFrame,
    verdict_summary: pd.DataFrame,
    window_metrics: dict[int, dict[str, dict[str, Any]]],
) -> None:
    lines = ["# D010 Metrics Summary", ""]
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
            f"| z_score_window_grid | {json.dumps(config['regime']['z_score_window_grid'])} |",
            "| macro_gate | D009 variables, factor blocks, signs, threshold, selection, costs, and rebalance are unchanged; only z-score window varies |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict_summary))
    lines.extend(["## Reproduction Check", ""])
    d009_sharpe = float(window_metrics[60]["factor_macro_gate_mcap"]["sharpe"])
    lines.append(f"- 60mo Sharpe: {_format_report_value(d009_sharpe)}")
    lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d011_threshold_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    threshold = float(config["regime"]["on_threshold"])
    lines = [f"# D011 Threshold {threshold:g} Metrics Summary", ""]
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
            f"| macro_gate | D009 ten variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= {threshold:g} |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d011_report(
    output_dir: Path,
    config: dict[str, Any],
    grid_summary: pd.DataFrame,
    verdict_summary: pd.DataFrame,
    threshold_metrics: dict[float, dict[str, dict[str, Any]]],
) -> None:
    lines = ["# D011 Metrics Summary", ""]
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
            f"| on_threshold_grid | {json.dumps(config['regime']['on_threshold_grid'])} |",
            "| macro_gate | D009 variables, 60-month z-score window, factor blocks, signs, selection, costs, and rebalance are unchanged; only composite threshold varies |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict_summary))
    lines.extend(["## Reproduction Check", ""])
    d009_sharpe = float(threshold_metrics[0.0]["factor_macro_gate_mcap"]["sharpe"])
    lines.append(f"- Threshold 0.0 Sharpe: {_format_report_value(d009_sharpe)}")
    lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d012_subperiod_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D012 Subperiod Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| subperiod | {config['subperiod']['name']} |",
            f"| trading_start | {config['subperiod']['start']} |",
            f"| trading_end | {config['subperiod']['end']} |",
            "| macro_gate | frozen D009 factor aggregation; only trading window is restricted |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d012_report(
    output_dir: Path,
    config: dict[str, Any],
    subperiod_table: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    rolling: pd.DataFrame,
    verdict: pd.DataFrame,
    spike: pd.DataFrame,
) -> None:
    lines = ["# D012 OOS Subperiod Split Metrics Summary", ""]
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
            "| macro_gate | frozen D009 factor aggregation; only trading window changes by subperiod |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Subperiod Table", subperiod_table))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Rolling 3-Year Sharpe", rolling))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    lines.extend(_b004_dataframe_table("Spike Year Contribution", spike))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d013_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    block_diagnostics: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D013 Metrics Summary", ""]
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
            "| macro_gate | D009 ten raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight two-variable blocks; ON when composite >= -0.2 |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Block Diagnostics", block_diagnostics))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d014_window_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    warmup: dict[str, Any],
    verdict: pd.DataFrame,
) -> None:
    window = int(config["regime"]["z_score_window_months"])
    lines = [f"# D014 {window}mo Metrics Summary", ""]
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
            f"| macro_gate | D009 ten variables transformed to {window}-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= -0.2 |",
            f"| z_score_warmup | rows with fewer than {window} monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("2010-2014 Warmup Diagnosis", pd.DataFrame([warmup])))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d014_report(
    output_dir: Path,
    config: dict[str, Any],
    grid_summary: pd.DataFrame,
    verdict_summary: pd.DataFrame,
    window_metrics: dict[int, dict[str, dict[str, Any]]],
) -> None:
    lines = ["# D014 Metrics Summary", ""]
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
            f"| z_score_window_grid | {json.dumps(config['regime']['z_score_window_grid'])} |",
            "| macro_gate | D013 variables, factor blocks, signs, threshold -0.2, selection, costs, and rebalance are unchanged; only z-score window varies |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict_summary))
    lines.extend(["## Reproduction Check", ""])
    d013_sharpe = float(window_metrics[60]["factor_macro_gate_mcap"]["sharpe"])
    lines.append(f"- 60mo Sharpe: {_format_report_value(d013_sharpe)}")
    lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d015_subperiod_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D015 Subperiod Metrics Summary", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            "| key | value |",
            "| --- | --- |",
            f"| subperiod | {config['subperiod']['name']} |",
            f"| trading_start | {config['subperiod']['start']} |",
            f"| trading_end | {config['subperiod']['end']} |",
            "| macro_gate | frozen D013 factor aggregation; only trading window is restricted |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d009_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d015_report(
    output_dir: Path,
    config: dict[str, Any],
    subperiod_table: pd.DataFrame,
    per_year_breakdown: pd.DataFrame,
    rolling: pd.DataFrame,
    verdict: pd.DataFrame,
    spike: pd.DataFrame,
) -> None:
    lines = ["# D015 OOS Subperiod Split Metrics Summary", ""]
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
            "| macro_gate | frozen D013 factor aggregation; only trading window changes by subperiod |",
            "| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Subperiod Table", subperiod_table))
    lines.extend(_b004_dataframe_table("Per-Year Breakdown", per_year_breakdown))
    lines.extend(_b004_dataframe_table("Rolling 3-Year Sharpe", rolling))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    lines.extend(_b004_dataframe_table("Spike Year Contribution", spike))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d002_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    window = int(config["regime"]["z_score_window_months"])
    lines = ["# D002 Metrics Summary", ""]
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
            f"| macro_gate | C014 eight raw variables transformed to {window}-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |",
            f"| z_score_warmup | rows with fewer than {window} monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d002_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d003_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D003 Metrics Summary", ""]
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
            "| macro_gate | Thirteen raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d003_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d004_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    exposure_distribution: pd.DataFrame,
    magnitude_return_scatter: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D004 Metrics Summary", ""]
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
            "| macro_gate | D001 factor composite preserved; exposure = clip(composite, 0, 1.0) / 1.0 |",
            "| sizing | per-stock target weight is 0.20 * exposure_scalar for five top-market-cap stocks; cash return is 0 |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and exposure 0 |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, D001 carrier unchanged |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39% |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d004_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Exposure Distribution", exposure_distribution))
    lines.extend(_b004_dataframe_table("Magnitude Return Scatter", magnitude_return_scatter))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d005_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    b7_diagnostics: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    lines = ["# D005 Metrics Summary", ""]
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
            "| macro_gate | D001 eight raw variables plus KR exports yoy and OECD CLI Korea level transformed to 60-month rolling z-scores, sign-adjusted, averaged by seven equal-weight factor blocks; ON when composite >= 0 |",
            "| b7_korea_growth | KR exports yoy sign +1; OECD CLI Korea level sign +1; block score is the within-block average |",
            "| timing | monthly Korea macro observations are treated as available 14 days after month-end; quarter-end signals use only values available by signal_date |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |",
            "| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39% |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d005_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("B7 Block Diagnostics", b7_diagnostics))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d006_window_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    warmup: dict[str, Any],
    verdict: pd.DataFrame,
) -> None:
    window = int(config["regime"]["z_score_window_months"])
    lines = [f"# D006 {window}mo Metrics Summary", ""]
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
            f"| macro_gate | D001 eight raw variables transformed to {window}-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |",
            f"| z_score_warmup | rows with fewer than {window} monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d006_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("2010-2014 Warmup Diagnosis", pd.DataFrame([warmup])))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d006_report(
    output_dir: Path,
    config: dict[str, Any],
    grid_summary: pd.DataFrame,
    verdict_summary: pd.DataFrame,
    window_metrics: dict[int, dict[str, dict[str, Any]]],
) -> None:
    lines = ["# D006 Metrics Summary", ""]
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
            f"| z_score_window_grid | {json.dumps(config['regime']['z_score_window_grid'])} |",
            "| macro_gate | D001 variables, factor blocks, signs, threshold, selection, costs, and rebalance are unchanged; only z-score window varies |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict_summary))
    lines.extend(["## Reproduction Check", ""])
    d001_sharpe = float(window_metrics[60]["factor_macro_gate_mcap"]["sharpe"])
    lines.append(f"- 60mo Sharpe: {_format_report_value(d001_sharpe)}")
    lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d007_threshold_report(
    output_dir: Path,
    config: dict[str, Any],
    metrics: dict[str, dict[str, Any]],
    year_breakdown: pd.DataFrame,
    subperiod_breakdown: pd.DataFrame,
    verdict: pd.DataFrame,
) -> None:
    threshold = float(config["regime"]["on_threshold"])
    lines = [f"# D007 Threshold {threshold:g} Metrics Summary", ""]
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
            f"| macro_gate | D001 eight raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= {threshold:g} |",
            "| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |",
            "| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |",
            "| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |",
            "| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_d007_metric_table(metrics))
    lines.extend(_b004_dataframe_table("Quarterly Year Breakdown", year_breakdown))
    lines.extend(_b004_dataframe_table("Subperiod Breakdown", subperiod_breakdown))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict))
    (output_dir / "report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_d007_report(
    output_dir: Path,
    config: dict[str, Any],
    grid_summary: pd.DataFrame,
    verdict_summary: pd.DataFrame,
    threshold_metrics: dict[float, dict[str, dict[str, Any]]],
) -> None:
    lines = ["# D007 Metrics Summary", ""]
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
            f"| on_threshold_grid | {json.dumps(config['regime']['on_threshold_grid'])} |",
            "| macro_gate | D001 variables, 60-month z-score window, factor blocks, signs, selection, costs, and rebalance are unchanged; only composite threshold varies |",
            "| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |",
            "| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |",
            "| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |",
            "| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |",
            "",
        ]
    )
    lines.extend(_b004_dataframe_table("Grid Summary", grid_summary))
    lines.extend(_b004_dataframe_table("Verdict Summary", verdict_summary))
    lines.extend(["## Reproduction Check", ""])
    d001_sharpe = float(threshold_metrics[0.0]["factor_macro_gate_mcap"]["sharpe"])
    lines.append(f"- Threshold 0.0 Sharpe: {_format_report_value(d001_sharpe)}")
    lines.append("")
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


def _c013_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C013_VARIANTS:
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
            f"| v10_minus_v8_cumulative_net_pp | {_format_report_value(v1['v10_minus_v8_cumulative_net_pp'])} |",
            f"| v10_minus_v8_cost_0_cumulative_net_pp | {_format_report_value(v1['v10_minus_v8_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| us_cpi_favorable_quarters | {_format_report_value(v1['us_cpi_favorable_quarters'])} |",
            f"| us_cpi_total_quarters | {_format_report_value(v1['us_cpi_total_quarters'])} |",
            f"| us_cpi_yoy_brent_yoy_correlation | {_format_report_value(v1['us_cpi_yoy_brent_yoy_correlation'])} |",
            f"| us_cpi_yoy_curve_spread_correlation | {_format_report_value(v1['us_cpi_yoy_curve_spread_correlation'])} |",
            f"| us_cpi_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['us_cpi_yoy_usdkrw_yoy_correlation'])} |",
            f"| us_cpi_decel_brent_yoy_correlation | {_format_report_value(v1['us_cpi_decel_brent_yoy_correlation'])} |",
            f"| us_cpi_decel_curve_spread_correlation | {_format_report_value(v1['us_cpi_decel_curve_spread_correlation'])} |",
            f"| us_cpi_decel_usdkrw_yoy_correlation | {_format_report_value(v1['us_cpi_decel_usdkrw_yoy_correlation'])} |",
            f"| inflation_spike_2022_regime_on_quarters | {_format_report_value(v1['inflation_spike_2022_regime_on_quarters'])} |",
            f"| inflation_spike_2022_total_quarters | {_format_report_value(v1['inflation_spike_2022_total_quarters'])} |",
            f"| inflation_spike_2022_cpi_favorable_quarters | {_format_report_value(v1['inflation_spike_2022_cpi_favorable_quarters'])} |",
            "",
        ]
    )
    return lines


def _c014_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C014_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C013 V10 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c013_v10_cumulative_net_total_return | {_format_report_value(C013_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c013_v10_cost_0_cumulative_net_total_return | {_format_report_value(C013_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v11_minus_v10_cumulative_net_pp | {_format_report_value(v1['v11_minus_v10_cumulative_net_pp'])} |",
            f"| v11_minus_v10_cost_0_cumulative_net_pp | {_format_report_value(v1['v11_minus_v10_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| us_ppi_favorable_quarters | {_format_report_value(v1['us_ppi_favorable_quarters'])} |",
            f"| us_ppi_total_quarters | {_format_report_value(v1['us_ppi_total_quarters'])} |",
            f"| us_ppi_decel_us_cpi_decel_correlation | {_format_report_value(v1['us_ppi_decel_us_cpi_decel_correlation'])} |",
            f"| us_ppi_decel_brent_yoy_correlation | {_format_report_value(v1['us_ppi_decel_brent_yoy_correlation'])} |",
            f"| us_ppi_decel_dxy_yoy_correlation | {_format_report_value(v1['us_ppi_decel_dxy_yoy_correlation'])} |",
            f"| us_ppi_yoy_us_cpi_yoy_correlation | {_format_report_value(v1['us_ppi_yoy_us_cpi_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c015_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C015_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v12_minus_v11_cumulative_net_pp | {_format_report_value(v1['v12_minus_v11_cumulative_net_pp'])} |",
            f"| v12_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v12_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| us_unrate_favorable_quarters | {_format_report_value(v1['us_unrate_favorable_quarters'])} |",
            f"| us_unrate_total_quarters | {_format_report_value(v1['us_unrate_total_quarters'])} |",
            f"| us_unrate_change_us_cpi_yoy_correlation | {_format_report_value(v1['us_unrate_change_us_cpi_yoy_correlation'])} |",
            f"| us_unrate_change_curve_spread_correlation | {_format_report_value(v1['us_unrate_change_curve_spread_correlation'])} |",
            f"| us_unrate_change_usdkrw_yoy_correlation | {_format_report_value(v1['us_unrate_change_usdkrw_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c016_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C016_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v13_minus_v11_cumulative_net_pp | {_format_report_value(v1['v13_minus_v11_cumulative_net_pp'])} |",
            f"| v13_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v13_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| kr_cpi_favorable_quarters | {_format_report_value(v1['kr_cpi_favorable_quarters'])} |",
            f"| kr_cpi_total_quarters_with_data | {_format_report_value(v1['kr_cpi_total_quarters_with_data'])} |",
            f"| kr_cpi_missing_quarters | {_format_report_value(v1['kr_cpi_missing_quarters'])} |",
            f"| kr_cpi_decel_us_cpi_decel_correlation | {_format_report_value(v1['kr_cpi_decel_us_cpi_decel_correlation'])} |",
            f"| kr_cpi_decel_brent_yoy_correlation | {_format_report_value(v1['kr_cpi_decel_brent_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c017_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C017_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v14_minus_v11_cumulative_net_pp | {_format_report_value(v1['v14_minus_v11_cumulative_net_pp'])} |",
            f"| v14_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v14_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| kr_exports_favorable_quarters | {_format_report_value(v1['kr_exports_favorable_quarters'])} |",
            f"| kr_exports_total_quarters_with_data | {_format_report_value(v1['kr_exports_total_quarters_with_data'])} |",
            f"| kr_exports_missing_quarters | {_format_report_value(v1['kr_exports_missing_quarters'])} |",
            f"| kr_exports_yoy_brent_yoy_correlation | {_format_report_value(v1['kr_exports_yoy_brent_yoy_correlation'])} |",
            f"| kr_exports_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['kr_exports_yoy_usdkrw_yoy_correlation'])} |",
            f"| kr_exports_yoy_us_cpi_decel_correlation | {_format_report_value(v1['kr_exports_yoy_us_cpi_decel_correlation'])} |",
            f"| kr_exports_yoy_us_ppi_decel_correlation | {_format_report_value(v1['kr_exports_yoy_us_ppi_decel_correlation'])} |",
            "",
        ]
    )
    return lines


def _c018_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C018_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v15_minus_v11_cumulative_net_pp | {_format_report_value(v1['v15_minus_v11_cumulative_net_pp'])} |",
            f"| v15_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v15_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| us_m2_favorable_quarters | {_format_report_value(v1['us_m2_favorable_quarters'])} |",
            f"| us_m2_total_quarters_with_data | {_format_report_value(v1['us_m2_total_quarters_with_data'])} |",
            f"| us_m2_missing_quarters | {_format_report_value(v1['us_m2_missing_quarters'])} |",
            f"| us_m2_yoy_us_cpi_decel_correlation | {_format_report_value(v1['us_m2_yoy_us_cpi_decel_correlation'])} |",
            f"| us_m2_yoy_curve_spread_correlation | {_format_report_value(v1['us_m2_yoy_curve_spread_correlation'])} |",
            f"| us_m2_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['us_m2_yoy_usdkrw_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _c019_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C019_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v16_minus_v11_cumulative_net_pp | {_format_report_value(v1['v16_minus_v11_cumulative_net_pp'])} |",
            f"| v16_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v16_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| usdjpy_favorable_quarters | {_format_report_value(v1['usdjpy_favorable_quarters'])} |",
            f"| usdjpy_total_quarters_with_data | {_format_report_value(v1['usdjpy_total_quarters_with_data'])} |",
            f"| usdjpy_missing_quarters | {_format_report_value(v1['usdjpy_missing_quarters'])} |",
            f"| usdjpy_yoy_dxy_yoy_correlation | {_format_report_value(v1['usdjpy_yoy_dxy_yoy_correlation'])} |",
            f"| usdjpy_yoy_usdkrw_yoy_correlation | {_format_report_value(v1['usdjpy_yoy_usdkrw_yoy_correlation'])} |",
            f"| usdjpy_yoy_vix_60d_avg_correlation | {_format_report_value(v1['usdjpy_yoy_vix_60d_avg_correlation'])} |",
            "",
        ]
    )
    return lines


def _c020_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in C020_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["macro_gate_mcap"]
    lines.extend(
        [
            "",
            "## C014 V11 Reference",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| c014_v11_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_CUMULATIVE_NET)} |",
            f"| c014_v11_cost_0_cumulative_net_total_return | {_format_report_value(C014_QUARTERLY_COST_0_CUMULATIVE_NET)} |",
            f"| v17_minus_v11_cumulative_net_pp | {_format_report_value(v1['v17_minus_v11_cumulative_net_pp'])} |",
            f"| v17_minus_v11_cost_0_cumulative_net_pp | {_format_report_value(v1['v17_minus_v11_cost_0_cumulative_net_pp'])} |",
            f"| regime_on_share | {_format_report_value(v1['regime_on_share'])} |",
            f"| jp10y_favorable_quarters | {_format_report_value(v1['jp10y_favorable_quarters'])} |",
            f"| jp10y_total_quarters_with_data | {_format_report_value(v1['jp10y_total_quarters_with_data'])} |",
            f"| jp10y_missing_quarters | {_format_report_value(v1['jp10y_missing_quarters'])} |",
            f"| jp10y_yoy_change_us10y_yoy_change_correlation | {_format_report_value(v1['jp10y_yoy_change_us10y_yoy_change_correlation'])} |",
            f"| jp10y_yoy_change_kr10y_yoy_change_correlation | {_format_report_value(v1['jp10y_yoy_change_kr10y_yoy_change_correlation'])} |",
            f"| jp10y_yoy_change_usdjpy_yoy_correlation | {_format_report_value(v1['jp10y_yoy_change_usdjpy_yoy_correlation'])} |",
            "",
        ]
    )
    return lines


def _d001_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D001_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("c014_v11_cumulative_net_total_return", C014_QUARTERLY_CUMULATIVE_NET),
        ("c014_v11_cost_0_cumulative_net_total_return", C014_QUARTERLY_COST_0_CUMULATIVE_NET),
        ("d001_minus_c014_v11_cumulative_net_pp", v1["d001_minus_c014_v11_cumulative_net_pp"]),
        ("d001_minus_c014_v11_cost_0_cumulative_net_pp", v1["d001_minus_c014_v11_cost_0_cumulative_net_pp"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("korea_avg_score", v1["korea_avg_score"]),
        ("c014_trade_overlap_jaccard", v1["c014_trade_overlap_jaccard"]),
    ]
    lines.extend(["", "## D001 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d009_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D009_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("cost_0_cumulative_net_total_return", v1["cost_0_cumulative_net_total_return"]),
        ("d001_cumulative_net_total_return", v1["d001_cumulative_net_total_return"]),
        ("d001_cost_0_cumulative_net_total_return", v1["d001_cost_0_cumulative_net_total_return"]),
        ("d009_minus_d001_cumulative_net_pp", v1["d009_minus_d001_cumulative_net_pp"]),
        ("d009_minus_d001_cost_0_cumulative_net_pp", v1["d009_minus_d001_cost_0_cumulative_net_pp"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("growth_avg_score", v1["growth_avg_score"]),
        ("return_2025_contribution_share", v1["return_2025_contribution_share"]),
        ("d001_trade_quarter_overlap_jaccard", v1["d001_trade_quarter_overlap_jaccard"]),
        ("d009_on_d001_off_quarter_count", v1["d009_on_d001_off_quarter_count"]),
        ("d009_off_d001_on_quarter_count", v1["d009_off_d001_on_quarter_count"]),
    ]
    variable_rows = []
    for name in D009_SIGNAL_NAMES:
        variable_rows.extend(
            [
                (f"{name}_z_mean", v1[f"{name}_z_mean"]),
                (f"{name}_z_std", v1[f"{name}_z_std"]),
                (f"{name}_z_positive_share", v1[f"{name}_z_positive_share"]),
            ]
        )
    lines.extend(["", "## D009 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in [*reference_rows, *variable_rows]:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d002_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D002_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("d001_cumulative_net_total_return", D001_CUMULATIVE_NET),
        ("d001_cost_0_cumulative_net_total_return", D001_COST_0_CUMULATIVE_NET),
        ("d002_minus_d001_cumulative_net_pp", v1["d002_minus_d001_cumulative_net_pp"]),
        ("d002_minus_d001_cost_0_cumulative_net_pp", v1["d002_minus_d001_cost_0_cumulative_net_pp"]),
        ("c014_v11_cumulative_net_total_return", C014_QUARTERLY_CUMULATIVE_NET),
        ("c014_v11_cost_0_cumulative_net_total_return", C014_QUARTERLY_COST_0_CUMULATIVE_NET),
        ("d002_minus_c014_v11_cumulative_net_pp", v1["d002_minus_c014_v11_cumulative_net_pp"]),
        ("d002_minus_c014_v11_cost_0_cumulative_net_pp", v1["d002_minus_c014_v11_cost_0_cumulative_net_pp"]),
        ("trade_count_2010_2014", v1["trade_count_2010_2014"]),
        ("d001_trade_count_reference", v1["d001_trade_count_reference"]),
        ("d002_minus_d001_trade_count", v1["d002_minus_d001_trade_count"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("korea_avg_score", v1["korea_avg_score"]),
        ("c014_trade_overlap_jaccard", v1["c014_trade_overlap_jaccard"]),
    ]
    lines.extend(["", "## D002 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d003_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D003_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("d001_cumulative_net_total_return", D001_CUMULATIVE_NET),
        ("d001_cost_0_cumulative_net_total_return", D001_COST_0_CUMULATIVE_NET),
        ("d003_minus_d001_cumulative_net_pp", v1["d003_minus_d001_cumulative_net_pp"]),
        ("d003_minus_d001_cost_0_cumulative_net_pp", v1["d003_minus_d001_cost_0_cumulative_net_pp"]),
        ("c014_v11_cumulative_net_total_return", C014_QUARTERLY_CUMULATIVE_NET),
        ("c014_v11_cost_0_cumulative_net_total_return", C014_QUARTERLY_COST_0_CUMULATIVE_NET),
        ("d003_minus_c014_v11_cumulative_net_pp", v1["d003_minus_c014_v11_cumulative_net_pp"]),
        ("d003_minus_c014_v11_cost_0_cumulative_net_pp", v1["d003_minus_c014_v11_cost_0_cumulative_net_pp"]),
        ("subperiod_2010_2017_net_total_return", v1["subperiod_2010_2017_net_total_return"]),
        ("subperiod_2010_2017_cost_0_total_return", v1["subperiod_2010_2017_cost_0_total_return"]),
        ("subperiod_2010_2017_trade_count", v1["subperiod_2010_2017_trade_count"]),
        ("trade_count_2010_2014", v1["trade_count_2010_2014"]),
        ("subperiod_2018_2026_net_total_return", v1["subperiod_2018_2026_net_total_return"]),
        ("subperiod_2018_2026_cost_0_total_return", v1["subperiod_2018_2026_cost_0_total_return"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("rates_avg_score", v1["rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("usd_fx_within_block_avg_std", v1["usd_fx_within_block_avg_std"]),
        ("rates_within_block_avg_std", v1["rates_within_block_avg_std"]),
        ("inflation_within_block_avg_std", v1["inflation_within_block_avg_std"]),
        ("d001_trade_overlap_jaccard", v1["d001_trade_overlap_jaccard"]),
    ]
    lines.extend(["", "## D003 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d004_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D004_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_sized_mcap"]
    reference_rows = [
        ("d001_cumulative_net_total_return", D001_CUMULATIVE_NET),
        ("d001_cost_0_cumulative_net_total_return", D001_COST_0_CUMULATIVE_NET),
        ("d004_minus_d001_cumulative_net_pp", v1["d004_minus_d001_cumulative_net_pp"]),
        ("d004_minus_d001_cost_0_cumulative_net_pp", v1["d004_minus_d001_cost_0_cumulative_net_pp"]),
        ("c014_v11_cumulative_net_total_return", C014_QUARTERLY_CUMULATIVE_NET),
        ("c014_v11_cost_0_cumulative_net_total_return", C014_QUARTERLY_COST_0_CUMULATIVE_NET),
        ("d004_minus_c014_v11_cumulative_net_pp", v1["d004_minus_c014_v11_cumulative_net_pp"]),
        ("d004_minus_c014_v11_cost_0_cumulative_net_pp", v1["d004_minus_c014_v11_cost_0_cumulative_net_pp"]),
        ("subperiod_2010_2017_net_total_return", v1["subperiod_2010_2017_net_total_return"]),
        ("subperiod_2010_2017_cost_0_total_return", v1["subperiod_2010_2017_cost_0_total_return"]),
        ("subperiod_2018_2026_net_total_return", v1["subperiod_2018_2026_net_total_return"]),
        ("subperiod_2018_2026_cost_0_total_return", v1["subperiod_2018_2026_cost_0_total_return"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("exposure_scalar_mean", v1["exposure_scalar_mean"]),
        ("exposure_scalar_std", v1["exposure_scalar_std"]),
        ("exposure_scalar_zero_share", v1["exposure_scalar_zero_share"]),
        ("exposure_scalar_one_share", v1["exposure_scalar_one_share"]),
        ("exposure_scalar_partial_share", v1["exposure_scalar_partial_share"]),
        ("on_quarters_mean_exposure", v1["on_quarters_mean_exposure"]),
        ("partial_exposure_quarter_count", v1["partial_exposure_quarter_count"]),
        ("partial_exposure_quarter_avg_return", v1["partial_exposure_quarter_avg_return"]),
        ("full_exposure_quarter_cumulative_gain", v1["full_exposure_quarter_cumulative_gain"]),
        ("partial_exposure_quarter_cumulative_gain", v1["partial_exposure_quarter_cumulative_gain"]),
        ("d001_quarter_overlap_jaccard", v1["d001_quarter_overlap_jaccard"]),
    ]
    lines.extend(["", "## D004 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d005_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D005_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("d001_cumulative_net_total_return", D001_CUMULATIVE_NET),
        ("d001_cost_0_cumulative_net_total_return", D001_COST_0_CUMULATIVE_NET),
        ("d005_minus_d001_cumulative_net_pp", v1["d005_minus_d001_cumulative_net_pp"]),
        ("d005_minus_d001_cost_0_cumulative_net_pp", v1["d005_minus_d001_cost_0_cumulative_net_pp"]),
        ("c014_v11_cumulative_net_total_return", C014_QUARTERLY_CUMULATIVE_NET),
        ("c014_v11_cost_0_cumulative_net_total_return", C014_QUARTERLY_COST_0_CUMULATIVE_NET),
        ("d005_minus_c014_v11_cumulative_net_pp", v1["d005_minus_c014_v11_cumulative_net_pp"]),
        ("d005_minus_c014_v11_cost_0_cumulative_net_pp", v1["d005_minus_c014_v11_cost_0_cumulative_net_pp"]),
        ("subperiod_2010_2017_net_total_return", v1["subperiod_2010_2017_net_total_return"]),
        ("subperiod_2010_2017_cost_0_total_return", v1["subperiod_2010_2017_cost_0_total_return"]),
        ("subperiod_2010_2017_trade_count", v1["subperiod_2010_2017_trade_count"]),
        ("trade_count_2010_2014", v1["trade_count_2010_2014"]),
        ("subperiod_2018_2026_net_total_return", v1["subperiod_2018_2026_net_total_return"]),
        ("subperiod_2018_2026_cost_0_total_return", v1["subperiod_2018_2026_cost_0_total_return"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("korea_avg_score", v1["korea_avg_score"]),
        ("korea_growth_avg_score", v1["korea_growth_avg_score"]),
        ("kr_exports_yoy_z_mean", v1["kr_exports_yoy_z_mean"]),
        ("kr_exports_yoy_z_std", v1["kr_exports_yoy_z_std"]),
        ("kr_cli_value_z_mean", v1["kr_cli_value_z_mean"]),
        ("kr_cli_value_z_std", v1["kr_cli_value_z_std"]),
        ("kr_exports_yoy_z_kr_cli_value_z_correlation", v1["kr_exports_yoy_z_kr_cli_value_z_correlation"]),
        ("d001_quarter_overlap_jaccard", v1["d001_quarter_overlap_jaccard"]),
        ("d005_on_d001_off_quarter_count", v1["d005_on_d001_off_quarter_count"]),
        ("d005_off_d001_on_quarter_count", v1["d005_off_d001_on_quarter_count"]),
    ]
    lines.extend(["", "## D005 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d006_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D006_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("cost_0_cumulative_net_total_return", v1["cost_0_cumulative_net_total_return"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("regime_on_share_complete_quarters", v1["regime_on_share_complete_quarters"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("korea_avg_score", v1["korea_avg_score"]),
    ]
    lines.extend(["", "## D006 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
    return lines


def _d007_metric_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
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
    for variant in D007_VARIANTS:
        block = metrics[variant]
        lines.append("| " + variant + " | " + " | ".join(_format_report_value(block[column]) for column in columns) + " |")
    v1 = metrics["factor_macro_gate_mcap"]
    reference_rows = [
        ("cost_0_cumulative_net_total_return", v1["cost_0_cumulative_net_total_return"]),
        ("regime_on_share", v1["regime_on_share"]),
        ("regime_on_share_complete_quarters", v1["regime_on_share_complete_quarters"]),
        ("composite_mean", v1["composite_mean"]),
        ("composite_std", v1["composite_std"]),
        ("composite_positive_share", v1["composite_positive_share"]),
        ("global_risk_avg_score", v1["global_risk_avg_score"]),
        ("usd_fx_avg_score", v1["usd_fx_avg_score"]),
        ("us_rates_avg_score", v1["us_rates_avg_score"]),
        ("inflation_avg_score", v1["inflation_avg_score"]),
        ("commodity_avg_score", v1["commodity_avg_score"]),
        ("korea_avg_score", v1["korea_avg_score"]),
    ]
    lines.extend(["", "## D007 Diagnostics", "", "| metric | value |", "| --- | ---: |"])
    for metric, value in reference_rows:
        lines.append(f"| {metric} | {_format_report_value(value)} |")
    lines.append("")
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
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E003 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E003 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"E003 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E003 regime keys must be exactly {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != (
        "type",
        "n",
        "count_matched_sector_max_per_sector",
        "pure_basket_min_sector_members",
        "pure_basket_exclude_sector_codes",
    ):
        raise ValueError("E003 selection keys do not match the Layer 2 baseline ticket.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"E003 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E003 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != ("A_d013_replication", "B_count_matched", "C_pure_basket"):
        raise ValueError("E003 variants must be A_d013_replication, B_count_matched, C_pure_basket.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E003 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E003 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("E003 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E003 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E003 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E003 requires regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E003 factor blocks/signs must match D013/D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("E003-A/B require selection market_cap_top_n n=5.")
    if int(config["selection"]["count_matched_sector_max_per_sector"]) != 1:
        raise ValueError("E003-B requires max one name per sector.")
    if int(config["selection"]["pure_basket_min_sector_members"]) != 3:
        raise ValueError("E003-C requires thin-sector cutoff of at least 3 names.")
    if tuple(str(code).zfill(2) for code in config["selection"]["pure_basket_exclude_sector_codes"]) != ("99",):
        raise ValueError("E003-C requires sector 99 exclusion.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E003 requires quarterly last_trading_day rebalance.")


def _validate_e004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E004_CONFIG_KEYS:
        raise ValueError(f"E004 config keys must be exactly {EXPECTED_E004_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E004 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E004 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != ("flow_by_value_window", "flow_by_mcap_window"):
        raise ValueError("E004 strategy keys must be flow_by_value_window, flow_by_mcap_window.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E004 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
        raise ValueError("E004 selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("E004 diagnostics keys must be exactly top_bottom_k.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E004 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E004 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E004 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["flow_by_value_window"]) != 20:
        raise ValueError("E004 requires strategy.flow_by_value_window: 20.")
    if int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("E004 requires strategy.flow_by_mcap_window: 60.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E004 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E004 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E004 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E004 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E004 requires quarterly last_trading_day rebalance.")
    if int(config["selection"]["top_sectors"]) != 3:
        raise ValueError("E004 requires selection.top_sectors: 3.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 2, 1):
        raise ValueError("E004 requires selection.top_sector_stock_counts: [2, 2, 1].")
    if int(config["selection"]["min_sector_stocks"]) != 3:
        raise ValueError("E004 requires selection.min_sector_stocks: 3.")
    if int(config["diagnostics"]["top_bottom_k"]) != 3:
        raise ValueError("E004 requires diagnostics.top_bottom_k: 3.")
    if tuple(config["variants"]) != ("diagnostics", "portfolio_if_pass"):
        raise ValueError("E004 variants must be diagnostics, portfolio_if_pass.")


def _validate_e005_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E005_CONFIG_KEYS:
        raise ValueError(f"E005 config keys must be exactly {EXPECTED_E005_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E005 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E005 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != ("short_window", "long_window"):
        raise ValueError("E005 strategy keys must be short_window, long_window.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E005 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
        raise ValueError("E005 selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("E005 diagnostics keys must be exactly top_bottom_k.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E005 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E005 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E005 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["short_window"]) != 20:
        raise ValueError("E005 requires strategy.short_window: 20.")
    if int(config["strategy"]["long_window"]) != 60:
        raise ValueError("E005 requires strategy.long_window: 60.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E005 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E005 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E005 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E005 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E005 requires quarterly last_trading_day rebalance.")
    if int(config["selection"]["top_sectors"]) != 3:
        raise ValueError("E005 requires selection.top_sectors: 3.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 2, 1):
        raise ValueError("E005 requires selection.top_sector_stock_counts: [2, 2, 1].")
    if int(config["selection"]["min_sector_stocks"]) != 3:
        raise ValueError("E005 requires selection.min_sector_stocks: 3.")
    if int(config["diagnostics"]["top_bottom_k"]) != 3:
        raise ValueError("E005 requires diagnostics.top_bottom_k: 3.")
    if tuple(config["variants"]) != ("diagnostics", "portfolio_if_pass"):
        raise ValueError("E005 variants must be diagnostics, portfolio_if_pass.")


def _validate_e006_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E006_CONFIG_KEYS:
        raise ValueError(f"E006 config keys must be exactly {EXPECTED_E006_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E006 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E006 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != ("flow_by_value_window", "flow_by_mcap_window", "short_window", "long_window"):
        raise ValueError("E006 strategy keys must be flow_by_value_window, flow_by_mcap_window, short_window, long_window.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E006 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
        raise ValueError("E006 selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("E006 diagnostics keys must be exactly top_bottom_k.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E006 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E006 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E006 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["flow_by_value_window"]) != 20:
        raise ValueError("E006 requires strategy.flow_by_value_window: 20.")
    if int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("E006 requires strategy.flow_by_mcap_window: 60.")
    if int(config["strategy"]["short_window"]) != 20:
        raise ValueError("E006 requires strategy.short_window: 20.")
    if int(config["strategy"]["long_window"]) != 60:
        raise ValueError("E006 requires strategy.long_window: 60.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E006 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E006 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E006 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E006 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E006 requires quarterly last_trading_day rebalance.")
    if int(config["selection"]["top_sectors"]) != 3:
        raise ValueError("E006 requires selection.top_sectors: 3.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 2, 1):
        raise ValueError("E006 requires selection.top_sector_stock_counts: [2, 2, 1].")
    if int(config["selection"]["min_sector_stocks"]) != 3:
        raise ValueError("E006 requires selection.min_sector_stocks: 3.")
    if int(config["diagnostics"]["top_bottom_k"]) != 3:
        raise ValueError("E006 requires diagnostics.top_bottom_k: 3.")
    if tuple(config["variants"]) != ("diagnostics", "portfolio_if_pass"):
        raise ValueError("E006 variants must be diagnostics, portfolio_if_pass.")


def _validate_e007_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E007_CONFIG_KEYS:
        raise ValueError(f"E007 config keys must be exactly {EXPECTED_E007_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E007 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E007 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != (
        "flow_by_value_window",
        "flow_by_mcap_window",
        "short_window",
        "long_window",
        "breadth_window",
    ):
        raise ValueError(
            "E007 strategy keys must be flow_by_value_window, flow_by_mcap_window, short_window, long_window, breadth_window."
        )
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E007 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
        raise ValueError("E007 selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("E007 diagnostics keys must be exactly top_bottom_k.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E007 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E007 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E007 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["flow_by_value_window"]) != 20:
        raise ValueError("E007 requires strategy.flow_by_value_window: 20.")
    if int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("E007 requires strategy.flow_by_mcap_window: 60.")
    if int(config["strategy"]["short_window"]) != 20:
        raise ValueError("E007 requires strategy.short_window: 20.")
    if int(config["strategy"]["long_window"]) != 60:
        raise ValueError("E007 requires strategy.long_window: 60.")
    if int(config["strategy"]["breadth_window"]) != 20:
        raise ValueError("E007 requires strategy.breadth_window: 20.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E007 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E007 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E007 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E007 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E007 requires quarterly last_trading_day rebalance.")
    if int(config["selection"]["top_sectors"]) != 3:
        raise ValueError("E007 requires selection.top_sectors: 3.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 2, 1):
        raise ValueError("E007 requires selection.top_sector_stock_counts: [2, 2, 1].")
    if int(config["selection"]["min_sector_stocks"]) != 3:
        raise ValueError("E007 requires selection.min_sector_stocks: 3.")
    if int(config["diagnostics"]["top_bottom_k"]) != 3:
        raise ValueError("E007 requires diagnostics.top_bottom_k: 3.")
    if tuple(config["variants"]) != ("diagnostics", "portfolio_if_pass"):
        raise ValueError("E007 variants must be diagnostics, portfolio_if_pass.")


def _validate_e008_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E008_CONFIG_KEYS:
        raise ValueError(f"E008 config keys must be exactly {EXPECTED_E008_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"E008 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"E008 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != (
        "flow_by_value_window",
        "flow_by_mcap_window",
        "short_window",
        "long_window",
        "breadth_window",
    ):
        raise ValueError(
            "E008 strategy keys must be flow_by_value_window, flow_by_mcap_window, short_window, long_window, breadth_window."
        )
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"E008 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != ("top_sector_stock_counts_grid", "min_sector_stocks"):
        raise ValueError("E008 selection keys must be top_sector_stock_counts_grid, min_sector_stocks.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("E008 diagnostics keys must be exactly top_bottom_k.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"E008 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("E008 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("E008 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["flow_by_value_window"]) != 20:
        raise ValueError("E008 requires strategy.flow_by_value_window: 20.")
    if int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("E008 requires strategy.flow_by_mcap_window: 60.")
    if int(config["strategy"]["short_window"]) != 20:
        raise ValueError("E008 requires strategy.short_window: 20.")
    if int(config["strategy"]["long_window"]) != 60:
        raise ValueError("E008 requires strategy.long_window: 60.")
    if int(config["strategy"]["breadth_window"]) != 20:
        raise ValueError("E008 requires strategy.breadth_window: 20.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("E008 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("E008 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("E008 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("E008 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("E008 requires quarterly last_trading_day rebalance.")
    grid = tuple(tuple(int(value) for value in counts) for counts in config["selection"]["top_sector_stock_counts_grid"])
    if grid != ((3, 2), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1)):
        raise ValueError("E008 requires selection.top_sector_stock_counts_grid: [[3,2], [2,2,1], [2,1,1,1], [1,1,1,1,1]].")
    if int(config["selection"]["min_sector_stocks"]) != 3:
        raise ValueError("E008 requires selection.min_sector_stocks: 3.")
    if int(config["diagnostics"]["top_bottom_k"]) != 3:
        raise ValueError("E008 requires diagnostics.top_bottom_k: 3.")
    if tuple(config["variants"]) != ("diagnostics", "portfolio_if_pass"):
        raise ValueError("E008 variants must be diagnostics, portfolio_if_pass.")


def _validate_e009_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E009_CONFIG_KEYS:
        raise ValueError(f"E009 config keys must be exactly {EXPECTED_E009_CONFIG_KEYS}; got {keys}.")
    e007_like = {
        key: (dict(config["cost_scenarios"]["base"]) if key == "costs" else config[key])
        for key in EXPECTED_E007_CONFIG_KEYS
    }
    e007_like["experiment_id"] = "E007"
    e007_like["variants"] = ["diagnostics", "portfolio_if_pass"]
    _validate_e007_config_shape(e007_like)
    validate_e009_cost_scenarios(config["cost_scenarios"])
    if tuple(config["variants"]) != ("cost_stress",):
        raise ValueError("E009 variants must be exactly cost_stress.")


def _validate_e011_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E011_CONFIG_KEYS:
        raise ValueError(f"E011 config keys must be exactly {EXPECTED_E011_CONFIG_KEYS}; got {keys}.")
    e007_like = dict(config)
    e007_like["experiment_id"] = "E007"
    e007_like["selection"] = dict(config["selection"])
    e007_like["selection"]["top_sectors"] = 3
    e007_like["selection"]["top_sector_stock_counts"] = [2, 2, 1]
    e007_like["variants"] = ["diagnostics", "portfolio_if_pass"]
    _validate_e007_config_shape(e007_like)
    if int(config["selection"]["top_sectors"]) != 4:
        raise ValueError("E011 requires selection.top_sectors: 4.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 1, 1, 1):
        raise ValueError("E011 requires selection.top_sector_stock_counts: [2, 1, 1, 1].")
    if tuple(config["variants"]) != ("champion",):
        raise ValueError("E011 variants must be exactly champion.")


def _validate_e012_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E012_CONFIG_KEYS:
        raise ValueError(f"E012 config keys must be exactly {EXPECTED_E012_CONFIG_KEYS}; got {keys}.")
    e008_like = {
        key: (dict(config["cost_scenarios"]["base"]) if key == "costs" else config[key])
        for key in EXPECTED_E008_CONFIG_KEYS
    }
    e008_like["experiment_id"] = "E008"
    e008_like["selection"] = {
        "top_sector_stock_counts_grid": [[3, 2], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]],
        "min_sector_stocks": config["selection"]["min_sector_stocks"],
    }
    e008_like["variants"] = ["diagnostics", "portfolio_if_pass"]
    _validate_e008_config_shape(e008_like)
    if tuple(config["selection"].keys()) != (
        "score_ablation_top_sector_stock_counts",
        "top_sector_stock_counts_grid",
        "min_sector_stocks",
    ):
        raise ValueError("E012 selection keys must be score_ablation_top_sector_stock_counts, top_sector_stock_counts_grid, min_sector_stocks.")
    if tuple(int(value) for value in config["selection"]["score_ablation_top_sector_stock_counts"]) != (2, 1, 1, 1):
        raise ValueError("E012 requires score_ablation_top_sector_stock_counts: [2, 1, 1, 1].")
    grid = tuple(tuple(int(value) for value in counts) for counts in config["selection"]["top_sector_stock_counts_grid"])
    if grid != E012_TOPK_GRID:
        raise ValueError("E012 requires Top-K grid [[2,2,1], [2,1,1,1], [1,1,1,1,1]].")
    validate_e012_cost_scenarios(config["cost_scenarios"])
    if tuple(config["variants"]) != ("score_ablation", "topk_grid", "cost_stress"):
        raise ValueError("E012 variants must be score_ablation, topk_grid, cost_stress.")


def _validate_e013_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E013_CONFIG_KEYS:
        raise ValueError(f"E013 config keys must be exactly {EXPECTED_E013_CONFIG_KEYS}; got {keys}.")
    e011_like = dict(config)
    e011_like["diagnostics"] = {"top_bottom_k": 3}
    e011_like["variants"] = ["champion"]
    e011_like["output_dir"] = config["output_dir"]
    ordered = {key: e011_like[key] for key in EXPECTED_E011_CONFIG_KEYS}
    ordered["experiment_id"] = "E011"
    _validate_e011_config_shape(ordered)
    if tuple(config["variants"]) != ("factor_macro_gate_mcap", "kospi_buy_and_hold", "cash"):
        raise ValueError("E013 variants must match E011 portfolio variants.")
    expected_subperiods = (
        ("full", "2010-01-04", "2026-05-04"),
        ("scheme_a_is", "2015-01-01", "2020-12-31"),
        ("scheme_a_oos", "2021-01-01", "2026-05-04"),
        ("scheme_b_is", "2015-01-01", "2019-12-31"),
        ("scheme_b_oos", "2020-01-01", "2026-05-04"),
        ("scheme_c_is", "2015-01-01", "2021-12-31"),
        ("scheme_c_oos", "2022-01-01", "2026-05-04"),
    )
    actual_subperiods = tuple((item["name"], str(item["start"]), str(item["end"])) for item in config["subperiods"])
    if actual_subperiods != expected_subperiods:
        raise ValueError("E013 subperiods must match the ticket exactly.")
    if config["per_year_analysis"] is not True or config["rolling_3yr_sharpe"] is not True:
        raise ValueError("E013 requires per_year_analysis and rolling_3yr_sharpe enabled.")


def _validate_e014_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E014_CONFIG_KEYS:
        raise ValueError(f"E014 config keys must be exactly {EXPECTED_E014_CONFIG_KEYS}; got {keys}.")
    e011_like = dict(config)
    e011_like["experiment_id"] = "E011"
    _validate_e011_config_shape(e011_like)
    if tuple(config["variants"]) != ("champion",):
        raise ValueError("E014 variants must be exactly champion.")


def _validate_f002_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_F002_CONFIG_KEYS:
        raise ValueError(f"F002 config keys must be exactly {EXPECTED_F002_CONFIG_KEYS}; got {keys}.")
    if config["carrier"] not in {"d013_direct", "e014"}:
        raise ValueError("F002 carrier must be d013_direct or e014.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"F002 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"F002 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != (
        "flow_by_value_window",
        "flow_by_mcap_window",
        "short_window",
        "long_window",
        "breadth_window",
    ):
        raise ValueError("F002 strategy keys must match Layer 2 score windows.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"F002 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"F002 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("F002 diagnostics keys must be exactly top_bottom_k.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("F002 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("F002 requires period.exclude_calendar_years: [2016].")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("F002 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("F002 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("F002 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("F002 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("F002 requires quarterly last_trading_day rebalance.")
    if config["carrier"] == "d013_direct":
        if tuple(config["selection"].keys()) != ("type", "n", "min_sector_stocks"):
            raise ValueError("F002-A selection keys must be type, n, min_sector_stocks.")
        if config["selection"]["type"] != "stock_rs_top_n" or int(config["selection"]["n"]) != 5:
            raise ValueError("F002-A requires stock_rs_top_n n=5.")
        if int(config["diagnostics"]["top_bottom_k"]) != 5:
            raise ValueError("F002-A requires diagnostics.top_bottom_k: 5.")
        if tuple(config["variants"]) != ("d013_direct",):
            raise ValueError("F002-A variants must be exactly d013_direct.")
    else:
        if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
            raise ValueError("F002-B selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
        if int(config["selection"]["top_sectors"]) != 4:
            raise ValueError("F002-B requires selection.top_sectors: 4.")
        if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 1, 1, 1):
            raise ValueError("F002-B requires top_sector_stock_counts: [2, 1, 1, 1].")
        if int(config["diagnostics"]["top_bottom_k"]) != 1:
            raise ValueError("F002-B requires diagnostics.top_bottom_k: 1.")
        if tuple(config["variants"]) != ("e014",):
            raise ValueError("F002-B variants must be exactly e014.")


def _validate_f003_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_F002_CONFIG_KEYS:
        raise ValueError(f"F003 config keys must be exactly {EXPECTED_F002_CONFIG_KEYS}; got {keys}.")
    if config["carrier"] not in {"d013_direct", "e014"}:
        raise ValueError("F003 carrier must be d013_direct or e014.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"F003 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"F003 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != (
        "flow_by_value_window",
        "flow_by_mcap_window",
        "short_window",
        "long_window",
        "breadth_window",
    ):
        raise ValueError("F003 strategy keys must match Layer 2 score windows.")
    if int(config["strategy"]["flow_by_value_window"]) != 20 or int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("F003 requires stock foreign flow windows 20 and 60.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"F003 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"F003 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("F003 diagnostics keys must be exactly top_bottom_k.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("F003 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("F003 requires period.exclude_calendar_years: [2016].")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("F003 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("F003 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("F003 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("F003 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("F003 requires quarterly last_trading_day rebalance.")
    if config["carrier"] == "d013_direct":
        if tuple(config["selection"].keys()) != ("type", "n", "min_sector_stocks"):
            raise ValueError("F003-A selection keys must be type, n, min_sector_stocks.")
        if config["selection"]["type"] != "stock_foreign_flow_top_n" or int(config["selection"]["n"]) != 5:
            raise ValueError("F003-A requires stock_foreign_flow_top_n n=5.")
        if int(config["diagnostics"]["top_bottom_k"]) != 5:
            raise ValueError("F003-A requires diagnostics.top_bottom_k: 5.")
        if tuple(config["variants"]) != ("d013_direct",):
            raise ValueError("F003-A variants must be exactly d013_direct.")
    else:
        if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
            raise ValueError("F003-B selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
        if int(config["selection"]["top_sectors"]) != 4:
            raise ValueError("F003-B requires selection.top_sectors: 4.")
        if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 1, 1, 1):
            raise ValueError("F003-B requires top_sector_stock_counts: [2, 1, 1, 1].")
        if int(config["diagnostics"]["top_bottom_k"]) != 1:
            raise ValueError("F003-B requires diagnostics.top_bottom_k: 1.")
        if tuple(config["variants"]) != ("e014",):
            raise ValueError("F003-B variants must be exactly e014.")


def _validate_f004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_F002_CONFIG_KEYS:
        raise ValueError(f"F004 config keys must be exactly {EXPECTED_F002_CONFIG_KEYS}; got {keys}.")
    if config["carrier"] not in {"d013_direct", "e014"}:
        raise ValueError("F004 carrier must be d013_direct or e014.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"F004 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"F004 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != (
        "flow_by_value_window",
        "flow_by_mcap_window",
        "short_window",
        "long_window",
        "breadth_window",
    ):
        raise ValueError("F004 strategy keys must match Layer 2 score windows.")
    if int(config["strategy"]["flow_by_value_window"]) != 20 or int(config["strategy"]["flow_by_mcap_window"]) != 60:
        raise ValueError("F004 requires stock institution flow windows 20 and 60.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"F004 regime keys must match D013: {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"F004 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["diagnostics"].keys()) != ("top_bottom_k",):
        raise ValueError("F004 diagnostics keys must be exactly top_bottom_k.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("F004 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("F004 requires period.exclude_calendar_years: [2016].")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("F004 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("F004 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("F004 requires D013 regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("F004 factor blocks/signs must match D013/D009 exactly.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("F004 requires quarterly last_trading_day rebalance.")
    if config["carrier"] == "d013_direct":
        if tuple(config["selection"].keys()) != ("type", "n", "min_sector_stocks"):
            raise ValueError("F004-A selection keys must be type, n, min_sector_stocks.")
        if config["selection"]["type"] != "stock_institution_flow_top_n" or int(config["selection"]["n"]) != 5:
            raise ValueError("F004-A requires stock_institution_flow_top_n n=5.")
        if int(config["diagnostics"]["top_bottom_k"]) != 5:
            raise ValueError("F004-A requires diagnostics.top_bottom_k: 5.")
        if tuple(config["variants"]) != ("d013_direct",):
            raise ValueError("F004-A variants must be exactly d013_direct.")
    else:
        if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
            raise ValueError("F004-B selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
        if int(config["selection"]["top_sectors"]) != 4:
            raise ValueError("F004-B requires selection.top_sectors: 4.")
        if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 1, 1, 1):
            raise ValueError("F004-B requires top_sector_stock_counts: [2, 1, 1, 1].")
        if int(config["diagnostics"]["top_bottom_k"]) != 1:
            raise ValueError("F004-B requires diagnostics.top_bottom_k: 1.")
        if tuple(config["variants"]) != ("e014",):
            raise ValueError("F004-B variants must be exactly e014.")


def _validate_e015_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_E015_CONFIG_KEYS:
        raise ValueError(f"E015 config keys must be exactly {EXPECTED_E015_CONFIG_KEYS}; got {keys}.")
    e012_like = {
        key: (config["cost_scenarios"] if key == "cost_scenarios" else config[key])
        for key in EXPECTED_E012_CONFIG_KEYS
        if key in config or key == "cost_scenarios"
    }
    e012_like["experiment_id"] = "E012"
    e012_like["selection"] = {
        "score_ablation_top_sector_stock_counts": [2, 1, 1, 1],
        "top_sector_stock_counts_grid": [[2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]],
        "min_sector_stocks": config["selection"]["min_sector_stocks"],
    }
    e012_like["diagnostics"] = {"top_bottom_k": 3}
    e012_like["variants"] = ["score_ablation", "topk_grid", "cost_stress"]
    e012_like["output_dir"] = config["output_dir"]
    ordered = {key: e012_like[key] for key in EXPECTED_E012_CONFIG_KEYS}
    _validate_e012_config_shape(ordered)
    if tuple(config["selection"].keys()) != ("top_sectors", "top_sector_stock_counts", "min_sector_stocks"):
        raise ValueError("E015 selection keys must be top_sectors, top_sector_stock_counts, min_sector_stocks.")
    if int(config["selection"]["top_sectors"]) != 4:
        raise ValueError("E015 requires selection.top_sectors: 4.")
    if tuple(int(value) for value in config["selection"]["top_sector_stock_counts"]) != (2, 1, 1, 1):
        raise ValueError("E015 requires selection.top_sector_stock_counts: [2, 1, 1, 1].")
    expected_spikes = [
        [2020],
        [2025],
        [2026],
        [2020, 2025, 2026],
    ]
    if config["spike_exclusions"] != expected_spikes:
        raise ValueError("E015 spike_exclusions must match the ticket exactly.")
    if config["validation"] != {
        "topk_stability_counts": [[2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]],
        "no_exploration": True,
    }:
        raise ValueError("E015 validation block must freeze Top-K stability and no_exploration exactly.")
    expected_subperiods = (
        ("full", "2010-01-04", "2026-05-04"),
        ("scheme_a_is", "2015-01-01", "2020-12-31"),
        ("scheme_a_oos", "2021-01-01", "2026-05-04"),
        ("scheme_b_is", "2015-01-01", "2019-12-31"),
        ("scheme_b_oos", "2020-01-01", "2026-05-04"),
        ("scheme_c_is", "2015-01-01", "2021-12-31"),
        ("scheme_c_oos", "2022-01-01", "2026-05-04"),
    )
    actual_subperiods = tuple((item["name"], str(item["start"]), str(item["end"])) for item in config["subperiods"])
    if actual_subperiods != expected_subperiods:
        raise ValueError("E015 subperiods must match the ticket exactly.")


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


def _validate_c013_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C013_CONFIG_KEYS:
        raise ValueError(f"C013 config keys must be exactly {EXPECTED_C013_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C013 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C013 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C013 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C013 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C013 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C013 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C013_VARIANTS:
        raise ValueError(f"C013 variants must be exactly {list(C013_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C013 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C013 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
    ):
        raise ValueError("C013 macro_signals must add us_cpi_decel to C011 v8 and exclude copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C013 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C013 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C013 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C013 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C013 requires quarterly last_trading_day rebalance.")


def _validate_c014_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C014_CONFIG_KEYS:
        raise ValueError(f"C014 config keys must be exactly {EXPECTED_C014_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C014 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C014 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C014 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C014 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C014 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C014 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C014_VARIANTS:
        raise ValueError(f"C014 variants must be exactly {list(C014_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C014 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C014 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
    ):
        raise ValueError("C014 macro_signals must add us_ppi_decel to C013 v10 and exclude copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C014 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C014 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C014 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C014 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C014 requires quarterly last_trading_day rebalance.")


def _validate_c015_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C015_CONFIG_KEYS:
        raise ValueError(f"C015 config keys must be exactly {EXPECTED_C015_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C015 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C015 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C015 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C015 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C015 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C015 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C015_VARIANTS:
        raise ValueError(f"C015 variants must be exactly {list(C015_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C015 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C015 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "us_unrate_change",
    ):
        raise ValueError("C015 macro_signals must add us_unrate_change to C014 v11 and exclude copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C015 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C015 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C015 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C015 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C015 requires quarterly last_trading_day rebalance.")


def _validate_c016_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C016_CONFIG_KEYS:
        raise ValueError(f"C016 config keys must be exactly {EXPECTED_C016_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C016 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C016 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C016 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C016 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C016 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C016 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C016_VARIANTS:
        raise ValueError(f"C016 variants must be exactly {list(C016_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C016 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C016 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "kr_cpi_decel",
    ):
        raise ValueError("C016 macro_signals must add kr_cpi_decel to C014 v11 and exclude UNRATE/copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C016 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C016 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C016 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C016 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C016 requires quarterly last_trading_day rebalance.")


def _validate_c017_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C017_CONFIG_KEYS:
        raise ValueError(f"C017 config keys must be exactly {EXPECTED_C017_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C017 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C017 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C017 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C017 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C017 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C017 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C017_VARIANTS:
        raise ValueError(f"C017 variants must be exactly {list(C017_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C017 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C017 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "kr_exports_yoy",
    ):
        raise ValueError("C017 macro_signals must add kr_exports_yoy to C014 v11 and exclude UNRATE/KR CPI/copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C017 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C017 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C017 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C017 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C017 requires quarterly last_trading_day rebalance.")


def _validate_c018_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C018_CONFIG_KEYS:
        raise ValueError(f"C018 config keys must be exactly {EXPECTED_C018_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C018 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C018 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C018 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C018 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C018 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C018 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C018_VARIANTS:
        raise ValueError(f"C018 variants must be exactly {list(C018_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C018 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C018 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "us_m2_yoy",
    ):
        raise ValueError("C018 macro_signals must add us_m2_yoy to C014 v11 and exclude UNRATE/KR CPI/KR exports/copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C018 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C018 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C018 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C018 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C018 requires quarterly last_trading_day rebalance.")


def _validate_c019_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C019_CONFIG_KEYS:
        raise ValueError(f"C019 config keys must be exactly {EXPECTED_C019_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C019 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C019 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C019 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C019 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C019 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C019 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C019_VARIANTS:
        raise ValueError(f"C019 variants must be exactly {list(C019_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C019 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C019 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "usdjpy_yoy",
    ):
        raise ValueError("C019 macro_signals must add usdjpy_yoy to C014 v11 and exclude UNRATE/KR CPI/KR exports/US M2/copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C019 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C019 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C019 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C019 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C019 requires quarterly last_trading_day rebalance.")


def _validate_c020_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_C020_CONFIG_KEYS:
        raise ValueError(f"C020 config keys must be exactly {EXPECTED_C020_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"C020 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"C020 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_C003_REGIME_KEYS:
        raise ValueError(f"C020 regime keys must be exactly {EXPECTED_C003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"C020 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"C020 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"C020 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["variants"]) != C020_VARIANTS:
        raise ValueError(f"C020 variants must be exactly {list(C020_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("C020 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("C020 requires period.exclude_calendar_years: [2016].")
    if tuple(config["regime"]["macro_signals"]) != (
        "usdkrw_yoy",
        "vix_60d_vs_240d",
        "dxy_yoy",
        "us_2_10_curve",
        "brent_yoy",
        "kr10y_yoy_change",
        "us_cpi_decel",
        "us_ppi_decel",
        "jp10y_yoy_change",
    ):
        raise ValueError("C020 macro_signals must add jp10y_yoy_change to C014 v11 and exclude UNRATE/KR CPI/KR exports/US M2/USDJPY/copper/USDCNY/KR3m.")
    if config["regime"]["composite_rule"] != "count_favorable":
        raise ValueError("C020 requires regime.composite_rule: count_favorable.")
    if int(config["regime"]["on_threshold"]) != 2:
        raise ValueError("C020 requires regime.on_threshold: 2.")
    if config["selection"]["type"] != "market_cap_top_n":
        raise ValueError("C020 requires selection.type: market_cap_top_n.")
    if int(config["selection"]["n"]) != 5:
        raise ValueError("C020 requires selection.n: 5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("C020 requires quarterly last_trading_day rebalance.")


def _validate_d001_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D001_CONFIG_KEYS:
        raise ValueError(f"D001 config keys must be exactly {EXPECTED_D001_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D001 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D001 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D001 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D001_REGIME_KEYS:
        raise ValueError(f"D001 regime keys must be exactly {EXPECTED_D001_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D001 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D001 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D001 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D001_VARIANTS:
        raise ValueError(f"D001 variants must be exactly {list(D001_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D001 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D001 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D001 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D001 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D001 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D001 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D001 factor blocks/signs are frozen by the ticket.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D001 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D001 requires quarterly last_trading_day rebalance.")


def _validate_d002_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D002_CONFIG_KEYS:
        raise ValueError(f"D002 config keys must be exactly {EXPECTED_D002_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D002 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D002 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D002_STRATEGY_KEYS:
        raise ValueError(f"D002 strategy keys must be exactly {EXPECTED_D002_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D002_REGIME_KEYS:
        raise ValueError(f"D002 regime keys must be exactly {EXPECTED_D002_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D002 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D002 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D002 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D002_VARIANTS:
        raise ValueError(f"D002 variants must be exactly {list(D002_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D002 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D002 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D002 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D002 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 24:
        raise ValueError("D002 requires regime.z_score_window_months: 24.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D002 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D002 factor blocks/signs are frozen by the ticket.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D002 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D002 requires quarterly last_trading_day rebalance.")


def _validate_d003_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D003_CONFIG_KEYS:
        raise ValueError(f"D003 config keys must be exactly {EXPECTED_D003_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D003 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D003 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D003_STRATEGY_KEYS:
        raise ValueError(f"D003 strategy keys must be exactly {EXPECTED_D003_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D003_REGIME_KEYS:
        raise ValueError(f"D003 regime keys must be exactly {EXPECTED_D003_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D003 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D003 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D003 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D003_VARIANTS:
        raise ValueError(f"D003 variants must be exactly {list(D003_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D003 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D003 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D003 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D003 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D003 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D003 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1), ("usdjpy_yoy", 1))),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1), ("usdcny_yoy", -1))),
        (
            "rates",
            (
                ("us_2_10_curve", 1),
                ("kr10y_yoy_change", -1),
                ("kr3m_yoy_change", -1),
                ("jp10y_yoy_change", -1),
            ),
        ),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1), ("kr_cpi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D003 factor blocks/signs are frozen by the ticket.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D003 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D003 requires quarterly last_trading_day rebalance.")


def _validate_d004_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D004_CONFIG_KEYS:
        raise ValueError(f"D004 config keys must be exactly {EXPECTED_D004_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D004 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D004 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D004_STRATEGY_KEYS:
        raise ValueError(f"D004 strategy keys must be exactly {EXPECTED_D004_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D004_REGIME_KEYS:
        raise ValueError(f"D004 regime keys must be exactly {EXPECTED_D004_REGIME_KEYS}.")
    if tuple(config["sizing"].keys()) != EXPECTED_D004_SIZING_KEYS:
        raise ValueError(f"D004 sizing keys must be exactly {EXPECTED_D004_SIZING_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D004 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D004 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D004 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D004_VARIANTS:
        raise ValueError(f"D004 variants must be exactly {list(D004_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D004 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D004 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D004 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D004 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D004 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D004 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D004 factor blocks/signs are frozen to D001.")
    if config["sizing"]["function"] != "linear":
        raise ValueError("D004 requires sizing.function: linear.")
    if float(config["sizing"]["k"]) != 1.0 or float(config["sizing"]["composite_floor"]) != 0.0:
        raise ValueError("D004 requires sizing.k: 1.0 and sizing.composite_floor: 0.0.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D004 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D004 requires quarterly last_trading_day rebalance.")


def _validate_d005_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D005_CONFIG_KEYS:
        raise ValueError(f"D005 config keys must be exactly {EXPECTED_D005_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D005 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D005 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D005_STRATEGY_KEYS:
        raise ValueError(f"D005 strategy keys must be exactly {EXPECTED_D005_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D005_REGIME_KEYS:
        raise ValueError(f"D005 regime keys must be exactly {EXPECTED_D005_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D005 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D005 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D005 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D005_VARIANTS:
        raise ValueError(f"D005 variants must be exactly {list(D005_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D005 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D005 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D005 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D005 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D005 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D005 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
        ("korea_growth", (("kr_exports_yoy", 1), ("kr_cli_value", 1))),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D005 factor blocks/signs must preserve D001 B1-B6 and add B7 Korea Growth.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D005 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D005 requires quarterly last_trading_day rebalance.")


def _validate_d006_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D006_CONFIG_KEYS:
        raise ValueError(f"D006 config keys must be exactly {EXPECTED_D006_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D006 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D006 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D006 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D006_REGIME_KEYS:
        raise ValueError(f"D006 regime keys must be exactly {EXPECTED_D006_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D006 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D006 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D006 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants_per_window"]) != ("factor_macro_gate_mcap",):
        raise ValueError("D006 variants_per_window must be exactly ['factor_macro_gate_mcap'].")
    if tuple(config["fixed_baselines"]) != ("kospi_buy_and_hold", "cash"):
        raise ValueError("D006 fixed_baselines must be exactly ['kospi_buy_and_hold', 'cash'].")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D006 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D006 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D006 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D006 requires regime.aggregation: factor_z_score.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D006 requires regime.on_threshold: 0.0.")
    if tuple(int(value) for value in config["regime"]["z_score_window_grid"]) != (36, 48, 60, 72, 84):
        raise ValueError("D006 requires z_score_window_grid: [36, 48, 60, 72, 84].")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D006 factor blocks/signs are frozen to D001.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D006 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D006 requires quarterly last_trading_day rebalance.")


def _validate_d007_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D007_CONFIG_KEYS:
        raise ValueError(f"D007 config keys must be exactly {EXPECTED_D007_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D007 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D007 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D007 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D007_REGIME_KEYS:
        raise ValueError(f"D007 regime keys must be exactly {EXPECTED_D007_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D007 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D007 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D007 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants_per_threshold"]) != ("factor_macro_gate_mcap",):
        raise ValueError("D007 variants_per_threshold must be exactly ['factor_macro_gate_mcap'].")
    if tuple(config["fixed_baselines"]) != ("kospi_buy_and_hold", "cash"):
        raise ValueError("D007 fixed_baselines must be exactly ['kospi_buy_and_hold', 'cash'].")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D007 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D007 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D007 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D007 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D007 requires regime.z_score_window_months: 60.")
    expected_thresholds = (-0.2, -0.1, 0.0, 0.1, 0.2)
    if tuple(float(value) for value in config["regime"]["on_threshold_grid"]) != expected_thresholds:
        raise ValueError("D007 requires on_threshold_grid: [-0.2, -0.1, 0.0, 0.1, 0.2].")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D007 factor blocks/signs are frozen to D001.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D007 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D007 requires quarterly last_trading_day rebalance.")


def _validate_d008_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D008_CONFIG_KEYS:
        raise ValueError(f"D008 config keys must be exactly {EXPECTED_D008_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D008 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D008 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D008 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D008_REGIME_KEYS:
        raise ValueError(f"D008 regime keys must be exactly {EXPECTED_D008_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D008 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D008 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D008 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D008_VARIANTS:
        raise ValueError(f"D008 variants must be exactly {list(D008_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D008 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D008 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D008 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D008 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D008 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D008 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1),)),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_2_10_curve", 1),)),
        ("inflation", (("us_cpi_decel", -1), ("us_ppi_decel", -1))),
        ("commodity", (("brent_yoy", -1),)),
        ("korea", (("kr10y_yoy_change", -1),)),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D008 factor blocks/signs are frozen to D001.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D008 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D008 requires quarterly last_trading_day rebalance.")
    expected_subperiods = (
        ("full", "2010-01-04", "2026-05-04"),
        ("scheme_a_is", "2015-01-01", "2020-12-31"),
        ("scheme_a_oos", "2021-01-01", "2026-05-04"),
        ("scheme_b_is", "2015-01-01", "2019-12-31"),
        ("scheme_b_oos", "2020-01-01", "2026-05-04"),
        ("scheme_c_is", "2015-01-01", "2021-12-31"),
        ("scheme_c_oos", "2022-01-01", "2026-05-04"),
    )
    observed = tuple((str(item["name"]), str(item["start"]), str(item["end"])) for item in config["subperiods"])
    if observed != expected_subperiods:
        raise ValueError("D008 subperiods must match the ticket exactly.")
    if config["per_year_analysis"] is not True or config["rolling_3yr_sharpe"] is not True:
        raise ValueError("D008 requires per_year_analysis and rolling_3yr_sharpe enabled.")


def _validate_d009_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D009_CONFIG_KEYS:
        raise ValueError(f"D009 config keys must be exactly {EXPECTED_D009_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D009 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D009 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D009 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D009_REGIME_KEYS:
        raise ValueError(f"D009 regime keys must be exactly {EXPECTED_D009_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D009 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D009 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D009 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D009_VARIANTS:
        raise ValueError(f"D009 variants must be exactly {list(D009_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D009 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D009 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D009 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D009 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D009 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D009 requires regime.on_threshold: 0.0.")
    expected_blocks = (
        ("global_risk", (("vix_60d_vs_240d", -1), ("baa10y_spread_level", -1))),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_10y_real_level", -1), ("us_2_10_curve", 1))),
        ("inflation", (("brent_yoy", -1), ("us_breakeven_level", -1))),
        ("growth", (("kr_cli_value", 1), ("kr_exports_yoy", 1))),
    )
    if _d001_blocks_from_config(config["regime"]["blocks"]) != expected_blocks:
        raise ValueError("D009 factor blocks/signs must match the holistic ticket exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D009 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D009 requires quarterly last_trading_day rebalance.")


def _validate_d010_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D010_CONFIG_KEYS:
        raise ValueError(f"D010 config keys must be exactly {EXPECTED_D010_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D010 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D010 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D010 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D010_REGIME_KEYS:
        raise ValueError(f"D010 regime keys must be exactly {EXPECTED_D010_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D010 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D010 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D010 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants_per_window"]) != ("factor_macro_gate_mcap",):
        raise ValueError("D010 variants_per_window must be exactly ['factor_macro_gate_mcap'].")
    if tuple(config["fixed_baselines"]) != ("kospi_buy_and_hold", "cash"):
        raise ValueError("D010 fixed_baselines must be exactly ['kospi_buy_and_hold', 'cash'].")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D010 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D010 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D010 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D010 requires regime.aggregation: factor_z_score.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D010 requires regime.on_threshold: 0.0.")
    if tuple(int(value) for value in config["regime"]["z_score_window_grid"]) != (36, 48, 60, 72, 84):
        raise ValueError("D010 requires z_score_window_grid: [36, 48, 60, 72, 84].")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D010 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D010 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D010 requires quarterly last_trading_day rebalance.")


def _validate_d011_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D011_CONFIG_KEYS:
        raise ValueError(f"D011 config keys must be exactly {EXPECTED_D011_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D011 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D011 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D011 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D011_REGIME_KEYS:
        raise ValueError(f"D011 regime keys must be exactly {EXPECTED_D011_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D011 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D011 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D011 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants_per_threshold"]) != ("factor_macro_gate_mcap",):
        raise ValueError("D011 variants_per_threshold must be exactly ['factor_macro_gate_mcap'].")
    if tuple(config["fixed_baselines"]) != ("kospi_buy_and_hold", "cash"):
        raise ValueError("D011 fixed_baselines must be exactly ['kospi_buy_and_hold', 'cash'].")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D011 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D011 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D011 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D011 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D011 requires regime.z_score_window_months: 60.")
    if tuple(float(value) for value in config["regime"]["on_threshold_grid"]) != (-0.2, -0.1, 0.0, 0.1, 0.2):
        raise ValueError("D011 requires on_threshold_grid: [-0.2, -0.1, 0.0, 0.1, 0.2].")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D011 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D011 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D011 requires quarterly last_trading_day rebalance.")


def _validate_d012_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D012_CONFIG_KEYS:
        raise ValueError(f"D012 config keys must be exactly {EXPECTED_D012_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D012 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D012 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D012 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D012_REGIME_KEYS:
        raise ValueError(f"D012 regime keys must be exactly {EXPECTED_D012_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D012 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D012 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D012 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D012_VARIANTS:
        raise ValueError(f"D012 variants must be exactly {list(D012_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D012 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D012 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D012 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D012 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D012 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != 0.0:
        raise ValueError("D012 requires regime.on_threshold: 0.0.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D012 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D012 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D012 requires quarterly last_trading_day rebalance.")
    expected_subperiods = (
        ("full", "2010-01-04", "2026-05-04"),
        ("scheme_a_is", "2015-01-01", "2020-12-31"),
        ("scheme_a_oos", "2021-01-01", "2026-05-04"),
        ("scheme_b_is", "2015-01-01", "2019-12-31"),
        ("scheme_b_oos", "2020-01-01", "2026-05-04"),
        ("scheme_c_is", "2015-01-01", "2021-12-31"),
        ("scheme_c_oos", "2022-01-01", "2026-05-04"),
    )
    observed = tuple((str(item["name"]), str(item["start"]), str(item["end"])) for item in config["subperiods"])
    if observed != expected_subperiods:
        raise ValueError("D012 subperiods must match the ticket exactly.")
    if config["per_year_analysis"] is not True or config["rolling_3yr_sharpe"] is not True:
        raise ValueError("D012 requires per_year_analysis and rolling_3yr_sharpe enabled.")


def _validate_d013_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D013_CONFIG_KEYS:
        raise ValueError(f"D013 config keys must be exactly {EXPECTED_D013_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D013 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D013 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D013 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D013_REGIME_KEYS:
        raise ValueError(f"D013 regime keys must be exactly {EXPECTED_D013_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D013 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D013 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D013 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D013_VARIANTS:
        raise ValueError(f"D013 variants must be exactly {list(D013_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D013 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D013 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D013 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D013 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D013 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("D013 requires regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D013 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D013 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D013 requires quarterly last_trading_day rebalance.")


def _validate_d014_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D014_CONFIG_KEYS:
        raise ValueError(f"D014 config keys must be exactly {EXPECTED_D014_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D014 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D014 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D014 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D014_REGIME_KEYS:
        raise ValueError(f"D014 regime keys must be exactly {EXPECTED_D014_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D014 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D014 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D014 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants_per_window"]) != ("factor_macro_gate_mcap",):
        raise ValueError("D014 variants_per_window must be exactly ['factor_macro_gate_mcap'].")
    if tuple(config["fixed_baselines"]) != ("kospi_buy_and_hold", "cash"):
        raise ValueError("D014 fixed_baselines must be exactly ['kospi_buy_and_hold', 'cash'].")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D014 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D014 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D014 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D014 requires regime.aggregation: factor_z_score.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("D014 requires regime.on_threshold: -0.2.")
    if tuple(int(value) for value in config["regime"]["z_score_window_grid"]) != (36, 48, 60, 72, 84):
        raise ValueError("D014 requires z_score_window_grid: [36, 48, 60, 72, 84].")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D014 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D014 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D014 requires quarterly last_trading_day rebalance.")


def _validate_d015_config_shape(config: dict[str, Any]) -> None:
    keys = tuple(config.keys())
    if keys != EXPECTED_D015_CONFIG_KEYS:
        raise ValueError(f"D015 config keys must be exactly {EXPECTED_D015_CONFIG_KEYS}; got {keys}.")
    if tuple(config["period"].keys()) != EXPECTED_B011_PERIOD_KEYS:
        raise ValueError(f"D015 period keys must be exactly {EXPECTED_B011_PERIOD_KEYS}.")
    if tuple(config["universe"].keys()) != EXPECTED_UNIVERSE_KEYS:
        raise ValueError(f"D015 universe keys must be exactly {EXPECTED_UNIVERSE_KEYS}.")
    if tuple(config["strategy"].keys()) != EXPECTED_D001_STRATEGY_KEYS:
        raise ValueError(f"D015 strategy keys must be exactly {EXPECTED_D001_STRATEGY_KEYS}.")
    if tuple(config["regime"].keys()) != EXPECTED_D015_REGIME_KEYS:
        raise ValueError(f"D015 regime keys must be exactly {EXPECTED_D015_REGIME_KEYS}.")
    if tuple(config["selection"].keys()) != EXPECTED_B011_SELECTION_KEYS:
        raise ValueError(f"D015 selection keys must be exactly {EXPECTED_B011_SELECTION_KEYS}.")
    if tuple(config["rebalance"].keys()) != EXPECTED_C003_REBALANCE_KEYS:
        raise ValueError(f"D015 rebalance keys must be exactly {EXPECTED_C003_REBALANCE_KEYS}.")
    if tuple(config["costs"].keys()) != EXPECTED_COST_KEYS:
        raise ValueError(f"D015 costs keys must be exactly {EXPECTED_COST_KEYS}.")
    if tuple(config["variants"]) != D015_VARIANTS:
        raise ValueError(f"D015 variants must be exactly {list(D015_VARIANTS)}.")
    if config["universe"].get("require_dynamic_top100") is not True:
        raise ValueError("D015 requires universe.require_dynamic_top100: true.")
    if tuple(int(year) for year in config["period"]["exclude_calendar_years"]) != (2016,):
        raise ValueError("D015 requires period.exclude_calendar_years: [2016].")
    if int(config["strategy"]["lookback"]) != 5 or int(config["strategy"]["max_positions"]) != 5:
        raise ValueError("D015 requires strategy.lookback: 5 and max_positions: 5.")
    if config["regime"]["aggregation"] != "factor_z_score":
        raise ValueError("D015 requires regime.aggregation: factor_z_score.")
    if int(config["regime"]["z_score_window_months"]) != 60:
        raise ValueError("D015 requires regime.z_score_window_months: 60.")
    if float(config["regime"]["on_threshold"]) != -0.2:
        raise ValueError("D015 requires regime.on_threshold: -0.2.")
    if _d001_blocks_from_config(config["regime"]["blocks"]) != _d009_expected_blocks():
        raise ValueError("D015 factor blocks/signs must match D009 exactly.")
    if config["selection"]["type"] != "market_cap_top_n" or int(config["selection"]["n"]) != 5:
        raise ValueError("D015 requires selection market_cap_top_n n=5.")
    if config["rebalance"]["frequency"] != "quarterly" or config["rebalance"]["anchor"] != "last_trading_day":
        raise ValueError("D015 requires quarterly last_trading_day rebalance.")
    expected_subperiods = (
        ("full", "2010-01-04", "2026-05-04"),
        ("scheme_a_is", "2015-01-01", "2020-12-31"),
        ("scheme_a_oos", "2021-01-01", "2026-05-04"),
        ("scheme_b_is", "2015-01-01", "2019-12-31"),
        ("scheme_b_oos", "2020-01-01", "2026-05-04"),
        ("scheme_c_is", "2015-01-01", "2021-12-31"),
        ("scheme_c_oos", "2022-01-01", "2026-05-04"),
    )
    observed = tuple((str(item["name"]), str(item["start"]), str(item["end"])) for item in config["subperiods"])
    if observed != expected_subperiods:
        raise ValueError("D015 subperiods must match the ticket exactly.")
    if config["per_year_analysis"] is not True or config["rolling_3yr_sharpe"] is not True:
        raise ValueError("D015 requires per_year_analysis and rolling_3yr_sharpe enabled.")


def _d009_expected_blocks() -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    return (
        ("global_risk", (("vix_60d_vs_240d", -1), ("baa10y_spread_level", -1))),
        ("usd_fx", (("usdkrw_yoy", -1), ("dxy_yoy", -1))),
        ("us_rates", (("us_10y_real_level", -1), ("us_2_10_curve", 1))),
        ("inflation", (("brent_yoy", -1), ("us_breakeven_level", -1))),
        ("growth", (("kr_cli_value", 1), ("kr_exports_yoy", 1))),
    )


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
