from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.run_experiment import _write_ticker_safe_csv


def test_run_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "E001_pipeline_sanity_fixed_holding"
    config_path = tmp_path / "e001.yaml"
    _write_synthetic_panel(panel_path)
    config_path.write_text(
        f"""experiment_id: E001
panels:
  - {panel_path}
periods:
  is:
    start: 2025-01-30
    end:   2025-02-14
  oos:
    start: 2025-02-17
    end:   2025-02-28
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 5
  max_positions: 5
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "-m", "src.run_experiment", "--config", str(config_path)],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    expected_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "cost_sensitivity.csv",
        "report.md",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)


def test_run_e002_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "E002_dynamic_exit_volatility_stop"
    config_path = tmp_path / "e002.yaml"
    _write_synthetic_panel(panel_path, include_high_low=True)
    config_path.write_text(
        f"""experiment_id: E002
panels:
  - {panel_path}
periods:
  is:
    start: 2025-01-30
    end:   2025-02-14
  oos:
    start: 2025-02-17
    end:   2025-03-19
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: 2.0
  vol_stop_atr_window: 20
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "-m", "src.run_experiment", "--config", str(config_path)],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    expected_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "cost_sensitivity.csv",
        "report.md",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "cap_only",
        "stop_only",
        "E001_replay",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_headline",
        "cost_0_E001_replay",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)


def test_run_e003_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    market_flow_path = tmp_path / "market_flow.csv"
    output_dir = tmp_path / "reports" / "E003_market_flow_gate"
    config_path = tmp_path / "e003.yaml"
    _write_synthetic_panel(panel_path)
    _write_synthetic_market_flow(market_flow_path)
    config_path.write_text(
        f"""experiment_id: E003
panels:
  - {panel_path}
market_flow:
  path: {market_flow_path}
periods:
  is:
    start: 2025-01-30
    end:   2025-02-14
  oos:
    start: 2025-02-17
    end:   2025-03-19
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: null
  vol_stop_atr_window: 20
gate:
  window: 5
  threshold: 0
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "-m", "src.run_experiment", "--config", str(config_path)],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    expected_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "cost_sensitivity.csv",
        "report.md",
        "market_gate_timeseries.csv",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "cap_only",
        "inverted_gate",
        "price_gate",
        "double_gate",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_headline",
        "cost_0_cap_only",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)


def test_run_e004_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "E004_signal_strength_top_quintile"
    config_path = tmp_path / "e004.yaml"
    _write_synthetic_panel(panel_path)
    config_path.write_text(
        f"""experiment_id: E004
panels:
  - {panel_path}
periods:
  is:
    start: 2025-01-30
    end:   2025-02-14
  oos:
    start: 2025-02-17
    end:   2025-03-19
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: null
  vol_stop_atr_window: 20
quintile:
  value: 5
  min_daily_universe_size: 20
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "-m", "src.run_experiment", "--config", str(config_path)],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    expected_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "cost_sensitivity.csv",
        "report.md",
        "quintile_membership_sample.csv",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "cap_only",
        "bottom_quintile",
        "middle_quintile",
        "top_decile",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_headline",
        "cost_0_cap_only",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)


def test_ticker_safe_csv_writer_preserves_leading_zero_codes(tmp_path: Path) -> None:
    path = tmp_path / "trades.csv"
    frame = pd.DataFrame(
        {
            "entry_date": ["2025-01-02", "2025-01-03"],
            "종목코드": [20, "000030"],
            "exit_date": ["2025-01-07", "2025-01-08"],
        }
    )

    _write_ticker_safe_csv(frame, path)

    raw = path.read_text(encoding="utf-8")
    round_tripped = pd.read_csv(path, dtype={"종목코드": "string"})
    assert ",000020," in raw
    assert list(round_tripped["종목코드"]) == ["000020", "000030"]


def _write_synthetic_panel(path: Path, *, include_high_low: bool = False) -> None:
    dates = pd.date_range("2025-01-02", periods=55, freq="B")
    tickers = [f"{index:06d}" for index in range(1, 7)]
    rows = []
    for ticker_index, ticker in enumerate(tickers, start=1):
        for day_index, date in enumerate(dates):
            close_price = 100.0 + ticker_index * 3.0 + day_index * 0.5
            row = {
                "날짜": date.date().isoformat(),
                "종목코드": ticker,
                "시가": close_price - 0.2,
                "종가": close_price,
                "KRX종가": close_price,
                "거래대금추정": 6_000_000_000.0 + ticker_index * 50_000_000.0,
                "외국인순매수금액추정": 20_000_000.0 + ticker_index * 1_000_000.0,
                "기관순매수금액추정": 15_000_000.0 + ticker_index * 1_000_000.0,
                "수급금액추정여부": False,
                "거래대금추정여부": False,
                "동적유니버스포함": True,
            }
            if include_high_low:
                row["고가"] = close_price + 0.5
                row["저가"] = close_price - 0.5
            rows.append(row)
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_synthetic_market_flow(path: Path) -> None:
    dates = pd.date_range("2025-01-02", periods=55, freq="B")
    rows = []
    for index, date in enumerate(dates):
        rows.append(
            {
                "date": date.date().isoformat(),
                "kospi_foreign_net": 100.0 if index % 7 != 0 else -500.0,
                "kospi_institution_net": 50.0,
                "ignored": index,
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
