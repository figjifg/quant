from __future__ import annotations

import pandas as pd
import pytest

from src.features.sector_rs_score import build_sector_rs_scores


def _sector_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    rows = []
    for date_index, date in enumerate(dates, start=1):
        for sector_code, n_stocks, return_step in (("01", 5, 0.001), ("02", 4, 0.002), ("03", 2, 0.003)):
            rows.append(
                {
                    "date": date,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "n_stocks": n_stocks,
                    "sum_market_cap": 1_000.0,
                    "sum_traded_value": 100.0,
                    "sum_foreign_net_buy_amount": 0.0,
                    "sum_foreign_net_buy_shares": 0.0,
                    "sum_institution_net_buy_amount": 0.0,
                    "sum_institution_net_buy_shares": 0.0,
                    "cap_weighted_return": return_step * date_index,
                    "top1_market_cap_pct": 0.3,
                    "top2_market_cap_pct": 0.4,
                }
            )
    return pd.DataFrame(rows)


def _kospi_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    return pd.DataFrame(
        {
            "date": dates,
            "cap_weighted_return": [0.0005 * index for index in range(1, 7)],
        }
    )


def test_rs_score_uses_kospi_relative_rolling_sums_and_cross_sectional_zscore() -> None:
    signal_date = pd.Timestamp("2025-01-08")

    result = build_sector_rs_scores(
        _sector_daily(),
        _kospi_daily(),
        signal_dates=[signal_date],
        short_window=2,
        long_window=3,
    )
    by_sector = result.set_index("sector_code")

    kospi_2d = 0.0005 * 4 + 0.0005 * 5
    kospi_3d = 0.0005 * 3 + 0.0005 * 4 + 0.0005 * 5
    sector_01_raw = (((0.001 * 4 + 0.001 * 5) - kospi_2d) + ((0.001 * 3 + 0.001 * 4 + 0.001 * 5) - kospi_3d)) / 2.0
    sector_02_raw = (((0.002 * 4 + 0.002 * 5) - kospi_2d) + ((0.002 * 3 + 0.002 * 4 + 0.002 * 5) - kospi_3d)) / 2.0
    mean = (sector_01_raw + sector_02_raw) / 2.0
    std = (((sector_01_raw - mean) ** 2 + (sector_02_raw - mean) ** 2) / 2.0) ** 0.5

    assert by_sector.loc["01", "sector_rel_ret_20d"] == pytest.approx((0.001 * 4 + 0.001 * 5) - kospi_2d)
    assert by_sector.loc["01", "sector_rel_ret_60d"] == pytest.approx((0.001 * 3 + 0.001 * 4 + 0.001 * 5) - kospi_3d)
    assert by_sector.loc["01", "rs_score"] == pytest.approx((sector_01_raw - mean) / std)
    assert by_sector.loc["02", "rs_score"] == pytest.approx((sector_02_raw - mean) / std)


def test_thin_sector_is_excluded_from_rs_score() -> None:
    result = build_sector_rs_scores(
        _sector_daily(),
        _kospi_daily(),
        signal_dates=[pd.Timestamp("2025-01-08")],
        short_window=2,
        long_window=3,
    )
    thin = result.loc[result["sector_code"].eq("03")].iloc[0]

    assert not bool(thin["eligible_for_score"])
    assert pd.isna(thin["rs_score"])


def test_rs_score_at_signal_date_is_unchanged_by_future_sector_and_kospi_rows() -> None:
    sector = _sector_daily()
    kospi = _kospi_daily()
    signal_date = pd.Timestamp("2025-01-08")
    before = build_sector_rs_scores(sector, kospi, signal_dates=[signal_date], short_window=2, long_window=3)

    mutated_sector = sector.copy()
    mutated_sector.loc[pd.to_datetime(mutated_sector["date"]).gt(signal_date), "cap_weighted_return"] = 999.0
    mutated_kospi = kospi.copy()
    mutated_kospi.loc[pd.to_datetime(mutated_kospi["date"]).gt(signal_date), "cap_weighted_return"] = -999.0
    after = build_sector_rs_scores(mutated_sector, mutated_kospi, signal_dates=[signal_date], short_window=2, long_window=3)

    pd.testing.assert_series_equal(
        before.sort_values("sector_code")["rs_score"].reset_index(drop=True),
        after.sort_values("sector_code")["rs_score"].reset_index(drop=True),
    )


def test_missing_kospi_baseline_date_raises() -> None:
    kospi = _kospi_daily().loc[lambda frame: frame["date"].ne(pd.Timestamp("2025-01-08"))]

    with pytest.raises(ValueError, match="kospi_daily is missing"):
        build_sector_rs_scores(
            _sector_daily(),
            kospi,
            signal_dates=[pd.Timestamp("2025-01-08")],
            short_window=2,
            long_window=3,
        )
