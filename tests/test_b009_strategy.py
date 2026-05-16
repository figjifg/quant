from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from src.run_experiment import main
from src.strategies.b007_filter_exploration import build_b007_candidates
from src.strategies.b009_f3_promote import VARIANTS, build_b009_candidates


ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1e-9


def test_b009_candidates_match_b007_f1_and_f3() -> None:
    features = _features()
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    b009_candidates, _ = build_b009_candidates(features, universe)
    b007_candidates, _, _ = build_b007_candidates(features, universe, min_count=3)

    pd.testing.assert_frame_equal(
        b009_candidates["f1_baseline"].reset_index(drop=True),
        b007_candidates["f1_baseline"].reset_index(drop=True),
    )
    pd.testing.assert_frame_equal(
        b009_candidates["f3_promote"].reset_index(drop=True),
        b007_candidates["f3_persistence_4_of_5"].reset_index(drop=True),
    )


def test_b009_real_panel_reproduces_b007_f3_and_b006_t3(tmp_path: Path) -> None:
    output_dir = tmp_path / "B009_f3_filter_promote"
    config_path = tmp_path / "b009.yaml"
    config_path.write_text(
        f"""experiment_id: B009
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
trigger:
  type: acceleration
ranking:
  type: combined_flow_5
exit:
  type: signal_reversal
variants:
  - f1_baseline
  - f3_promote
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
        "f3_promote_year_breakdown.csv",
        "cost_sensitivity.csv",
        "report.md",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    b009 = _read_metrics(output_dir / "metrics.json")
    b007 = _read_metrics(ROOT / "reports/experiments/B007_filter_role_exploration/metrics.json")
    b006 = _read_metrics(ROOT / "reports/experiments/B006_t3_acceleration_promote/metrics.json")

    assert set(B009_VARIANTS_WITH_COSTS()) == set(b009)
    _assert_shared_metrics_equal(b009["f1_baseline"], b006["t3_acceleration"])
    _assert_shared_metrics_equal(b009["cost_0_f1_baseline"], b006["cost_0_t3_acceleration"])
    _assert_shared_metrics_equal(b009["f1_baseline"], b007["f1_baseline"])
    _assert_shared_metrics_equal(b009["cost_0_f1_baseline"], b007["cost_0_f1_baseline"])
    _assert_shared_metrics_equal(b009["f3_promote"], b007["f3_persistence_4_of_5"])
    _assert_shared_metrics_equal(b009["cost_0_f3_promote"], b007["cost_0_f3_persistence_4_of_5"])

    trades_b009 = pd.read_csv(output_dir / "trades.csv", dtype={"종목코드": "string"})
    trades_b007 = pd.read_csv(
        ROOT / "reports/experiments/B007_filter_role_exploration/trades.csv",
        dtype={"종목코드": "string"},
    )
    f3_b009 = trades_b009.loc[trades_b009["variant"].eq("f3_promote")].drop(columns="variant").reset_index(drop=True)
    f3_b007 = trades_b007.loc[trades_b007["variant"].eq("F3")].drop(columns="variant").reset_index(drop=True)
    shared_columns = [column for column in f3_b007.columns if column in f3_b009.columns]
    pd.testing.assert_frame_equal(f3_b009.loc[:, shared_columns], f3_b007.loc[:, shared_columns])


def B009_VARIANTS_WITH_COSTS() -> tuple[str, ...]:
    return (*VARIANTS, *(f"cost_0_{variant}" for variant in VARIANTS))


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
    for day_index, date in enumerate(pd.date_range("2025-01-02", periods=6, freq="B")):
        for ticker, fnv, inv, flow_1, flow_5 in (
            ("000010", 0.1 + day_index * 0.01, 0.2, 0.20, 0.50),
            ("000020", 0.2, 0.1 + day_index * 0.01, 0.18, 0.60),
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
