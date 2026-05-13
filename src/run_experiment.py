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
from src.data.universe import build_execution_universe
from src.features.flow_ratios import build_atr_pct, build_flow_ratios
from src.reporting.metrics import metrics_is_oos
from src.reporting.report import write_report
from src.strategies.baselines import (
    run_b0_cash,
    run_b1_buy_and_hold,
    run_b2_universe_5d_rebalance,
    run_b3_price_momentum,
)
from src.strategies.e001_flow_filter import build_e001_flow_filter_candidates


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
EXPECTED_PERIOD_KEYS = ("is", "oos")
EXPECTED_SPLIT_KEYS = ("start", "end")
EXPECTED_UNIVERSE_KEYS = (
    "require_dynamic_top100",
    "min_avg_traded_value_20d",
    "exclude_estimated_flag_rows",
)
EXPECTED_STRATEGY_KEYS = ("lookback", "holding", "max_positions")
EXPECTED_EXIT_KEYS = ("vol_stop_k", "vol_stop_atr_window")
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
            vol_stop_k=vol_stop_k,
            vol_stop_atr_window=atr_window,
            atr_features=atr_features,
        ),
        "cap_only": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=holding_cap,
        ),
        "stop_only": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=999,
            vol_stop_k=vol_stop_k,
            vol_stop_atr_window=atr_window,
            atr_features=atr_features,
        ),
        "E001_replay": run_candidate_backtest(
            panel,
            calendar,
            headline_candidates,
            costs,
            is_start,
            oos_end,
            max_positions=max_positions,
            holding=5,
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
            vol_stop_k=vol_stop_k,
            vol_stop_atr_window=atr_window,
            atr_features=atr_features,
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
    cost_0_headline = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=holding_cap,
        vol_stop_k=vol_stop_k,
        vol_stop_atr_window=atr_window,
        atr_features=atr_features,
    )
    cost_0_e001_replay = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        zero_costs,
        is_start,
        oos_end,
        max_positions=max_positions,
        holding=5,
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
) -> None:
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, output_dir / "config.yaml")
    _write_json(output_dir / "metrics.json", metrics)
    headline_result.trades.to_csv(output_dir / "trades.csv", index=False)
    _signals_frame(headline_candidates).to_csv(output_dir / "signals.csv", index=False)
    headline_result.equity_curve.to_csv(output_dir / "equity_curve.csv", index=False)
    cost_sensitivity.to_csv(output_dir / "cost_sensitivity.csv", index=False)
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


def _costs_from_config(costs: dict[str, Any]) -> Costs:
    return Costs(
        commission_bps=float(costs["commission_bps"]),
        tax_bps_sell=float(costs["tax_bps_sell"]),
        slippage_bps=float(costs["slippage_bps"]),
    )


def _signals_frame(candidates: pd.DataFrame) -> pd.DataFrame:
    columns = ["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"]
    signals = candidates.loc[:, columns].copy()
    signals["signal"] = True
    return signals


def _metadata(config: dict[str, Any], panel: pd.DataFrame, calendar: object) -> dict[str, Any]:
    return {
        "panels_used": list(config["panels"]),
        "is_start": _date_string(config["periods"]["is"]["start"]),
        "is_end": _date_string(config["periods"]["is"]["end"]),
        "oos_start": _date_string(config["periods"]["oos"]["start"]),
        "oos_end": _date_string(config["periods"]["oos"]["end"]),
        "estimate_row_policy": "headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is universally True in the Kiwoom panel and is not used as a filter; diagnostic_estimate_included reincludes the 거래대금추정여부 rows",
        "integrated_column_policy": "KRX종가 preferred; 종가 only as pre-NXT fallback",
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
