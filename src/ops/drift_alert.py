from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.ops.nav_update import DEFAULT_PORTFOLIOS, ROOT, load_component_nav
from src.ops.rebalance_report import drifted_weights, quarter_start_proxy

REAL_YIELD_CSV = ROOT / "research_input_data/inputs/macro_features/fred_us_10y_real.csv"
OUTPUT_DIR = ROOT / "paper_trading/operations/drift_alerts"
TARGET = DEFAULT_PORTFOLIOS["P08_IEF30"]


def compute_drift_alerts(as_of_date: str | pd.Timestamp | None = None, output_path: str | Path | None = None) -> Path:
    """Compute drift and simple risk alerts for P08_IEF30."""

    as_of = pd.Timestamp(as_of_date) if as_of_date else None
    component_nav = load_component_nav(as_of)
    quarter = f"{component_nav.index.max().year}-Q{((component_nav.index.max().month - 1) // 3) + 1}"
    current_quarter_nav = component_nav.loc[component_nav.index >= quarter_start_proxy(quarter)]
    weights = drifted_weights(current_quarter_nav, TARGET)
    nav = sum(component_nav[ticker] * weight for ticker, weight in TARGET.items())
    rolling_mdd = nav / nav.rolling(252, min_periods=1).max() - 1.0

    real_yield_shock = load_real_yield_shock(as_of or component_nav.index.max())
    us_equity = component_nav["SPY"]
    us_equity_drawdown = float(us_equity.iloc[-1] / us_equity.rolling(252, min_periods=1).max().iloc[-1] - 1.0)
    drift_pp = {ticker: (weights[ticker] - TARGET[ticker]) * 100.0 for ticker in TARGET}
    alerts = {
        "as_of_date": component_nav.index.max().strftime("%Y-%m-%d"),
        "portfolio": "P08_IEF30",
        "drift_pp": drift_pp,
        "portfolio_rolling_mdd": float(rolling_mdd.iloc[-1]),
        "real_yield_2022_like_rate_shock_proxy_pp": real_yield_shock,
        "us_equity_drawdown_vs_52w_high": us_equity_drawdown,
        "h001_regime_state": "paper_check_required_from_D013_macro_gate",
        "thresholds": {
            "component_drift_pp": 10.0,
            "portfolio_mdd": -0.15,
            "us_equity_drawdown": -0.20,
            "real_yield_change_pp": 1.0,
        },
        "triggered_alerts": [],
        "tax_professional_check_required_before_live": True,
    }
    if max(abs(value) for value in drift_pp.values()) > alerts["thresholds"]["component_drift_pp"]:
        alerts["triggered_alerts"].append("component_drift_gt_10pp")
    if alerts["portfolio_rolling_mdd"] < alerts["thresholds"]["portfolio_mdd"]:
        alerts["triggered_alerts"].append("portfolio_mdd_lt_minus_15pct")
    if us_equity_drawdown < alerts["thresholds"]["us_equity_drawdown"]:
        alerts["triggered_alerts"].append("us_equity_drawdown_lt_minus_20pct")
    if real_yield_shock is not None and abs(real_yield_shock) > alerts["thresholds"]["real_yield_change_pp"]:
        alerts["triggered_alerts"].append("real_yield_change_gt_1pp")

    path = Path(output_path) if output_path else OUTPUT_DIR / f"drift_alert_{component_nav.index.max():%Y-%m-%d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(alerts, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_real_yield_shock(as_of: pd.Timestamp) -> float | None:
    if not REAL_YIELD_CSV.exists():
        return None
    frame = pd.read_csv(REAL_YIELD_CSV)
    date_col = "observation_date" if "observation_date" in frame.columns else frame.columns[0]
    value_col = [col for col in frame.columns if col != date_col][0]
    frame[date_col] = pd.to_datetime(frame[date_col])
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    frame = frame.loc[frame[date_col].le(as_of)].dropna(subset=[value_col]).sort_values(date_col)
    if len(frame) < 252:
        return None
    return float(frame[value_col].iloc[-1] - frame[value_col].iloc[-252])


if __name__ == "__main__":
    print(compute_drift_alerts("2026-05-18").relative_to(ROOT))
