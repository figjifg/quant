from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from src.run_experiment import main
from src.strategies.b003_trigger_exploration import build_b003_trigger_exploration
from src.strategies.b006_t3_promote import build_b006_candidates


ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1e-9


def test_b006_candidate_builders_match_b003_immediate_and_acceleration() -> None:
    features = _features()
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    b006_candidates, _ = build_b006_candidates(features, universe)
    b003_candidates, _ = build_b003_trigger_exploration(features, universe)

    pd.testing.assert_frame_equal(
        b006_candidates["t1_baseline"].reset_index(drop=True),
        b003_candidates["immediate"].reset_index(drop=True),
    )
    pd.testing.assert_frame_equal(
        b006_candidates["t3_acceleration"].reset_index(drop=True),
        b003_candidates["acceleration"].reset_index(drop=True),
    )


def test_b006_real_panel_reproduces_b003_t3_and_b002_t1(tmp_path: Path) -> None:
    output_dir = tmp_path / "B006_t3_acceleration_promote"
    config_path = tmp_path / "b006.yaml"
    config_path.write_text(
        f"""experiment_id: B006
panels:
  - {ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv"}
  - {ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"}
periods:
  is:
    start: 2018-01-02
    end:   2022-12-30
  oos:
    start: 2023-01-02
    end:   2026-05-04
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  max_positions: 5
filter:
  type: flow_sign_both_positive
ranking:
  type: combined_flow_5
exit:
  type: signal_reversal
variants:
  - t1_baseline
  - t3_acceleration
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: {output_dir}
""",
        encoding="utf-8",
    )

    main(["--config", str(config_path)])

    expected_files = {
        "config.yaml",
        "metrics.json",
        "trades.csv",
        "signals.csv",
        "equity_curve.csv",
        "t3_promote_year_breakdown.csv",
        "cost_sensitivity.csv",
        "report.md",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    b006 = _read_metrics(output_dir / "metrics.json")
    b003 = _read_metrics(ROOT / "reports/experiments/B003_trigger_role_exploration/metrics.json")
    b002 = _read_metrics(ROOT / "reports/experiments/B002_signal_reversal_exit/metrics.json")

    _assert_shared_metrics_equal(b006["t3_acceleration"], b003["T3_acceleration"])
    _assert_shared_metrics_equal(b006["cost_0_t3_acceleration"], b003["cost_0_T3_acceleration"])
    _assert_shared_metrics_equal(b006["t1_baseline"], b002["headline"])
    _assert_shared_metrics_equal(b006["cost_0_t1_baseline"], b002["cost_0_headline"])


def _read_metrics(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_shared_metrics_equal(left: dict[str, object], right: dict[str, object]) -> None:
    for split in ("is", "oos"):
        left_split = left[split]
        right_split = right[split]
        for key in ("total_return", "hit_rate", "trade_count"):
            left_value = left_split[key]
            right_value = right_split[key]
            if isinstance(left_value, float) or isinstance(right_value, float):
                assert math.isclose(float(left_value), float(right_value), rel_tol=0.0, abs_tol=TOLERANCE)
            else:
                assert left_value == right_value


def _features() -> pd.DataFrame:
    rows = []
    for day_index, date in enumerate(pd.date_range("2025-01-02", periods=4, freq="B")):
        for ticker, fnv, inv, flow_1, flow_5 in (
            ("000010", 0.1 + day_index * 0.01, 0.2, 0.12 if day_index % 2 == 0 else 0.08, 0.50),
            ("000020", 0.2, 0.1 + day_index * 0.01, 0.20, 0.60),
            ("000030", -0.1, 0.3, 0.30, 0.70),
        ):
            rows.append(
                {
                    "execution_date": date + pd.offsets.BDay(1),
                    "signal_date": date,
                    "날짜": date,
                    "종목코드": ticker,
                    "fnv_5": fnv,
                    "inv_5": inv,
                    "combined_flow_1": flow_1,
                    "combined_flow_5": flow_5,
                }
            )
    return pd.DataFrame(rows)
