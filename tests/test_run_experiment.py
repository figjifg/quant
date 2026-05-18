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
    market_breadth_path = tmp_path / "market_breadth.csv"
    sector_mapping_path = tmp_path / "sector_mapping.csv"
    output_dir = tmp_path / "reports" / "E003_layer2_baselines"
    config_path = tmp_path / "e003.yaml"
    _write_synthetic_panel(panel_path)
    _write_synthetic_market_breadth(market_breadth_path)
    _write_synthetic_sector_mapping(sector_mapping_path)
    config_path.write_text(
        f"""experiment_id: E003
panels:
  - {panel_path}
panel_date_filters: {{}}
market_breadth_csv: {market_breadth_path}
macro_data_dir: research_input_data/inputs/macro_features
sector_mapping_csv: {sector_mapping_path}
period:
  start: 2025-01-02
  end:   2025-03-19
  exclude_calendar_years: [2016]
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  max_positions: 5
regime:
  aggregation: factor_z_score
  z_score_window_months: 60
  on_threshold: -0.2
  blocks:
    - name: global_risk
      vars:
        - {{name: vix_60d_vs_240d, sign: -1}}
        - {{name: baa10y_spread_level, sign: -1}}
    - name: usd_fx
      vars:
        - {{name: usdkrw_yoy, sign: -1}}
        - {{name: dxy_yoy, sign: -1}}
    - name: us_rates
      vars:
        - {{name: us_10y_real_level, sign: -1}}
        - {{name: us_2_10_curve, sign: 1}}
    - name: inflation
      vars:
        - {{name: brent_yoy, sign: -1}}
        - {{name: us_breakeven_level, sign: -1}}
    - name: growth
      vars:
        - {{name: kr_cli_value, sign: 1}}
        - {{name: kr_exports_yoy, sign: 1}}
selection:
  type: market_cap_top_n
  n: 5
  count_matched_sector_max_per_sector: 1
  pure_basket_min_sector_members: 3
  pure_basket_exclude_sector_codes: ["99"]
rebalance:
  frequency: quarterly
  anchor: last_trading_day
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
variants:
  - A_d013_replication
  - B_count_matched
  - C_pure_basket
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "-m", "src.run_experiment", "--config", str(config_path)],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    expected_top_level_files = {
        "config.yaml",
        "comparison_summary.csv",
        "quarterly_regime_log.csv",
        "report.md",
        "sector_holding_overlap.csv",
    }
    assert expected_top_level_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    expected_variant_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "quarterly_year_breakdown.csv",
        "subperiod_breakdown.csv",
        "sector_holdings.csv",
    }
    for variant in ("A_d013_replication", "B_count_matched", "C_pure_basket"):
        variant_dir = output_dir / variant
        assert expected_variant_files == {path.name for path in variant_dir.iterdir() if path.is_file()}
        metrics = json.loads((variant_dir / "metrics.json").read_text(encoding="utf-8"))
        assert set(metrics) == {
            "factor_macro_gate_mcap",
            "kospi_buy_and_hold",
            "cash",
            "cost_0_factor_macro_gate_mcap",
        }


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


def test_run_b001_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "B001_market_cap_normalized_signal"
    config_path = tmp_path / "b001.yaml"
    _write_synthetic_panel(panel_path)
    config_path.write_text(
        f"""experiment_id: B001
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
normalization:
  divisor: 시가총액
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
        "trade_mcap_composition.csv",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "A002_replay",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_headline",
        "cost_0_A002_replay",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)

    composition = pd.read_csv(output_dir / "trade_mcap_composition.csv")
    assert set(composition["run"]) == {"headline", "A002_replay"}


def test_run_b002_experiment_cli_writes_required_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "B002_signal_reversal_exit"
    config_path = tmp_path / "b002.yaml"
    _write_synthetic_panel(panel_path)
    config_path.write_text(
        f"""experiment_id: B002
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
  max_positions: 5
exit:
  type: signal_reversal
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
        "exit_reason_breakdown.csv",
        "holding_period_distribution.csv",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "headline",
        "A002_replay",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_headline",
        "cost_0_A002_replay",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)

    exit_reasons = pd.read_csv(output_dir / "exit_reason_breakdown.csv")
    holding_periods = pd.read_csv(output_dir / "holding_period_distribution.csv")
    assert set(exit_reasons["run"]) == {"headline", "A002_replay"}
    assert set(holding_periods["run"]) == {"headline", "A002_replay"}


def test_run_b003_experiment_cli_writes_trigger_outputs(tmp_path: Path) -> None:
    panel_path = tmp_path / "synthetic_panel.csv"
    output_dir = tmp_path / "reports" / "B003_trigger_role_exploration"
    config_path = tmp_path / "b003.yaml"
    _write_synthetic_panel(panel_path)
    config_path.write_text(
        f"""experiment_id: B003
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
  max_positions: 5
exit:
  type: signal_reversal
trigger:
  candidates: [immediate, freshness, acceleration, persistence_3d]
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
        "exit_reason_breakdown.csv",
        "holding_period_distribution.csv",
        "trade_set_overlap.csv",
        "trades_immediate.csv",
        "signals_immediate.csv",
        "equity_curve_immediate.csv",
        "trades_freshness.csv",
        "signals_freshness.csv",
        "equity_curve_freshness.csv",
        "trades_acceleration.csv",
        "signals_acceleration.csv",
        "equity_curve_acceleration.csv",
        "trades_persistence_3d.csv",
        "signals_persistence_3d.csv",
        "equity_curve_persistence_3d.csv",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {
        "T1_immediate",
        "T2_freshness",
        "T3_acceleration",
        "T4_persistence_3d",
        "B0",
        "B1",
        "B2",
        "B3",
        "diagnostic_estimate_included",
        "cost_0_T1_immediate",
        "cost_0_T2_freshness",
        "cost_0_T3_acceleration",
        "cost_0_T4_persistence_3d",
    }
    assert all(set(metrics[key]) == {"is", "oos", "full"} for key in metrics)
    assert list(pd.read_csv(output_dir / "cost_sensitivity.csv")["run"].unique())


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
                "시가총액추정": 1_000_000_000_000.0 + ticker_index * 10_000_000_000.0,
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


def _write_synthetic_market_breadth(path: Path) -> None:
    dates = pd.date_range("2025-01-02", periods=55, freq="B")
    pd.DataFrame(
        {
            "date": [date.date().isoformat() for date in dates],
            "cap_weighted_return": [0.001 if index % 2 == 0 else -0.0005 for index, _ in enumerate(dates)],
        }
    ).to_csv(path, index=False)


def _write_synthetic_sector_mapping(path: Path) -> None:
    rows = []
    sectors = [
        ("01", "IT"),
        ("02", "Auto"),
        ("03", "Chem"),
        ("04", "Steel"),
        ("05", "Industrial"),
        ("99", "Other"),
    ]
    for index, (code, name) in enumerate(sectors, start=1):
        ticker = f"{index:06d}"
        rows.append(
            {
                "pdno": f"00000A{ticker}",
                "ticker": ticker,
                "prdt_name": ticker,
                "kis_mcls": name,
                "ksic": name,
                "final_sector_code": code,
                "final_sector_name": name,
                "mapping_source": "test",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)
