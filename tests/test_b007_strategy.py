from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.run_experiment import main
from src.strategies.b006_t3_promote import build_b006_candidates
from src.strategies.b007_filter_exploration import VARIANTS, build_b007_candidates, run_b007_variants


ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1e-9


def test_b007_f1_candidates_match_b006_t3_acceleration() -> None:
    features = _features()
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    b007_candidates, _, _ = build_b007_candidates(features, universe, min_count=3)
    b006_candidates, _ = build_b006_candidates(features, universe)

    pd.testing.assert_frame_equal(
        b007_candidates["f1_baseline"].reset_index(drop=True),
        b006_candidates["t3_acceleration"].reset_index(drop=True),
    )


def test_b007_variants_produce_non_trivial_synthetic_trades() -> None:
    panel = _panel()
    calendar = derive_trading_calendar(panel)
    features = _features_from_calendar(calendar)
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    runs, candidates, _, _ = run_b007_variants(
        panel=panel,
        calendar=calendar,
        flow_features=features,
        universe=universe,
        costs=Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        min_count=30,
    )

    assert tuple(runs) == VARIANTS
    assert all(len(runs[variant].trades) > 0 for variant in VARIANTS)
    assert all(len(candidates[variant]) > 0 for variant in VARIANTS)


def test_b007_real_panel_reproduces_b006_t3(tmp_path: Path) -> None:
    output_dir = tmp_path / "B007_filter_role_exploration"
    config_path = tmp_path / "b007.yaml"
    config_path.write_text(
        f"""experiment_id: B007
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
filter:
  candidates:
    - flow_sign_both_positive
    - relative_AND_absolute_positive
    - persistence_4_of_5
relative:
  cross_sectional_min_count: 30
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
        "filter_exploration_year_breakdown.csv",
        "filter_overlap_matrix.csv",
        "cost_sensitivity.csv",
        "report.md",
    }
    assert expected_files == {path.name for path in output_dir.iterdir() if path.is_file()}

    b007 = _read_metrics(output_dir / "metrics.json")
    b006 = _read_metrics(ROOT / "reports/experiments/B006_t3_acceleration_promote/metrics.json")

    assert set(B007_VARIANT_KEYS := tuple(B007_VARIANTS_WITH_COSTS())) == set(b007)
    _assert_shared_metrics_equal(b007["f1_baseline"], b006["t3_acceleration"])
    _assert_shared_metrics_equal(b007["cost_0_f1_baseline"], b006["cost_0_t3_acceleration"])

    trades_b007 = pd.read_csv(output_dir / "trades.csv", dtype={"종목코드": "string"})
    trades_b006 = pd.read_csv(
        ROOT / "reports/experiments/B006_t3_acceleration_promote/trades.csv",
        dtype={"종목코드": "string"},
    )
    f1 = trades_b007.loc[trades_b007["variant"].eq("F1")].drop(columns="variant").reset_index(drop=True)
    t3 = trades_b006.loc[trades_b006["variant"].eq("t3_acceleration")].drop(columns="variant").reset_index(drop=True)
    shared_columns = [column for column in t3.columns if column in f1.columns]
    pd.testing.assert_frame_equal(f1.loc[:, shared_columns], t3.loc[:, shared_columns])

    assert all(b007[variant]["is"]["trade_count"] > 0 for variant in VARIANTS)
    assert all(b007[variant]["oos"]["trade_count"] > 0 for variant in VARIANTS)


def B007_VARIANTS_WITH_COSTS() -> tuple[str, ...]:
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


def _panel() -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", periods=7)
    rows = []
    for date_index, date in enumerate(dates):
        for ticker_index in range(1, 33):
            price = 100.0 + ticker_index + date_index
            rows.append(
                {
                    "날짜": date,
                    "종목코드": f"{ticker_index:06d}",
                    "시가": price,
                    "KRX종가": price + 0.5,
                }
            )
    return pd.DataFrame(rows)


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


def _features_from_calendar(calendar: object) -> pd.DataFrame:
    rows = []
    for date_index, signal_date in enumerate(calendar.dates[:-1]):
        execution_date = calendar.dates[date_index + 1]
        for ticker_index in range(1, 33):
            ticker = f"{ticker_index:06d}"
            centered = ticker_index - 16.5
            rows.append(
                {
                    "날짜": signal_date,
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "fnv_5": centered / 100.0,
                    "inv_5": centered / 100.0,
                    "combined_flow_1": 0.1 if centered > 0 else -0.1,
                    "combined_flow_5": centered / 50.0,
                }
            )
    return pd.DataFrame(rows)
