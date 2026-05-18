from __future__ import annotations

import pandas as pd
import pytest

from src.features.sector_flow_score import build_sector_flow_scores


def _sector_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    rows = []
    for date_index, date in enumerate(dates, start=1):
        for sector_code, n_stocks, flow_base in (("01", 5, 10.0), ("02", 4, 20.0), ("03", 2, 30.0)):
            rows.append(
                {
                    "date": date,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "n_stocks": n_stocks,
                    "sum_market_cap": 1_000.0,
                    "sum_traded_value": 100.0,
                    "sum_foreign_net_buy_amount": flow_base + date_index,
                    "sum_foreign_net_buy_shares": 0.0,
                    "sum_institution_net_buy_amount": 0.0,
                    "sum_institution_net_buy_shares": 0.0,
                    "cap_weighted_return": 0.01,
                    "top1_market_cap_pct": 0.3,
                    "top2_market_cap_pct": 0.4,
                }
            )
    return pd.DataFrame(rows)


def test_flow_score_uses_expected_rolling_formula_and_cross_sectional_zscore() -> None:
    data = _sector_daily()
    signal_date = pd.Timestamp("2025-01-08")

    result = build_sector_flow_scores(data, signal_dates=[signal_date], value_window=2, mcap_window=3)
    by_sector = result.set_index("sector_code")

    sector_01_raw = ((15.0 + 14.0) / 200.0 + (15.0 + 14.0 + 13.0) / 1000.0) / 2.0
    sector_02_raw = ((25.0 + 24.0) / 200.0 + (25.0 + 24.0 + 23.0) / 1000.0) / 2.0
    mean = (sector_01_raw + sector_02_raw) / 2.0
    std = (((sector_01_raw - mean) ** 2 + (sector_02_raw - mean) ** 2) / 2.0) ** 0.5

    assert by_sector.loc["01", "flow_by_value_20d"] == pytest.approx((15.0 + 14.0) / 200.0)
    assert by_sector.loc["01", "flow_by_mcap_60d"] == pytest.approx((15.0 + 14.0 + 13.0) / 1000.0)
    assert by_sector.loc["01", "flow_score"] == pytest.approx((sector_01_raw - mean) / std)
    assert by_sector.loc["02", "flow_score"] == pytest.approx((sector_02_raw - mean) / std)


def test_thin_sector_is_excluded_from_score() -> None:
    result = build_sector_flow_scores(
        _sector_daily(),
        signal_dates=[pd.Timestamp("2025-01-08")],
        value_window=2,
        mcap_window=3,
    )
    thin = result.loc[result["sector_code"].eq("03")].iloc[0]

    assert not bool(thin["eligible_for_score"])
    assert pd.isna(thin["flow_score"])


def test_flow_score_at_signal_date_is_unchanged_by_future_rows() -> None:
    data = _sector_daily()
    signal_date = pd.Timestamp("2025-01-08")
    before = build_sector_flow_scores(data, signal_dates=[signal_date], value_window=2, mcap_window=3)

    mutated = data.copy()
    mutated.loc[pd.to_datetime(mutated["date"]).gt(signal_date), "sum_foreign_net_buy_amount"] = -999_999.0
    mutated.loc[pd.to_datetime(mutated["date"]).gt(signal_date), "sum_traded_value"] = 1.0
    mutated.loc[pd.to_datetime(mutated["date"]).gt(signal_date), "sum_market_cap"] = 1.0
    after = build_sector_flow_scores(mutated, signal_dates=[signal_date], value_window=2, mcap_window=3)

    pd.testing.assert_series_equal(
        before.sort_values("sector_code")["flow_score"].reset_index(drop=True),
        after.sort_values("sector_code")["flow_score"].reset_index(drop=True),
    )
