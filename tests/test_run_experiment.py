from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


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


def _write_synthetic_panel(path: Path) -> None:
    dates = pd.date_range("2025-01-02", periods=55, freq="B")
    tickers = [f"{index:06d}" for index in range(1, 7)]
    rows = []
    for ticker_index, ticker in enumerate(tickers, start=1):
        for day_index, date in enumerate(dates):
            close_price = 100.0 + ticker_index * 3.0 + day_index * 0.5
            rows.append(
                {
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
            )
    pd.DataFrame(rows).to_csv(path, index=False)
