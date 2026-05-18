from __future__ import annotations

import pandas as pd

from src.data.sector_aggregator import (
    _build_aggregate_summary,
    _build_sector_daily,
    _join_sector_mapping,
)


def test_join_sector_mapping_keeps_unmapped_rows() -> None:
    panel = pd.DataFrame(
        [
            {
                "date": pd.Timestamp("2026-01-02"),
                "ticker": "005930",
                "market_cap": 100.0,
                "traded_value": 10.0,
                "foreign_net_buy_amount": 1.0,
                "foreign_net_buy_shares": 2.0,
                "institution_net_buy_amount": 3.0,
                "institution_net_buy_shares": 4.0,
                "daily_return": 0.01,
            },
            {
                "date": pd.Timestamp("2026-01-02"),
                "ticker": "999999",
                "market_cap": 50.0,
                "traded_value": 5.0,
                "foreign_net_buy_amount": 1.0,
                "foreign_net_buy_shares": 2.0,
                "institution_net_buy_amount": 3.0,
                "institution_net_buy_shares": 4.0,
                "daily_return": 0.02,
            },
        ]
    )
    mapping = pd.DataFrame(
        [{"ticker": "005930", "final_sector_code": "01", "final_sector_name": "반도체/IT하드웨어"}]
    )

    result = _join_sector_mapping(panel, mapping)

    assert result.loc[result["ticker"] == "005930", "sector_code"].iloc[0] == "01"
    assert pd.isna(result.loc[result["ticker"] == "999999", "sector_code"].iloc[0])


def test_build_sector_daily_aggregates_flows_and_market_cap_weighted_return() -> None:
    stock_daily = pd.DataFrame(
        [
            _stock_row("005930", 100.0, 0.10, 10.0),
            _stock_row("000660", 50.0, -0.02, 20.0),
            _stock_row("035420", 25.0, 0.04, 30.0),
        ]
    )

    result = _build_sector_daily(stock_daily)

    row = result.iloc[0]
    assert row["n_stocks"] == 3
    assert row["sum_market_cap"] == 175.0
    assert row["sum_traded_value"] == 60.0
    assert row["sum_foreign_net_buy_amount"] == 6.0
    assert row["sum_foreign_net_buy_shares"] == 60.0
    assert row["sum_institution_net_buy_amount"] == 9.0
    assert row["sum_institution_net_buy_shares"] == 90.0
    assert row["cap_weighted_return"] == (100.0 * 0.10 + 50.0 * -0.02 + 25.0 * 0.04) / 175.0
    assert row["top1_market_cap_pct"] == 100.0 / 175.0
    assert row["top2_market_cap_pct"] == 50.0 / 175.0


def test_aggregate_summary_requires_eight_non_thin_groups_at_quarter_end() -> None:
    rows = []
    for sector_number in range(1, 13):
        rows.append(
            {
                "date": pd.Timestamp("2026-03-31"),
                "sector_code": f"{sector_number:02d}",
                "sector_name": f"sector-{sector_number}",
                "n_stocks": 3 if sector_number <= 8 else 2,
                "sum_market_cap": 100.0,
                "sum_traded_value": 10.0,
                "sum_foreign_net_buy_amount": 1.0,
                "sum_foreign_net_buy_shares": 1.0,
                "sum_institution_net_buy_amount": 1.0,
                "sum_institution_net_buy_shares": 1.0,
                "cap_weighted_return": 0.01,
                "top1_market_cap_pct": 0.5,
                "top2_market_cap_pct": 0.3,
            }
        )

    summary = _build_aggregate_summary(pd.DataFrame(rows))

    assert summary.loc[0, "groups_present"] == 12
    assert summary.loc[0, "groups_with_n_ge_3"] == 8
    assert bool(summary.loc[0, "hard_pass_ge_8_non_thin_groups"])


def _stock_row(ticker: str, market_cap: float, daily_return: float, traded_value: float) -> dict:
    return {
        "date": pd.Timestamp("2026-01-02"),
        "ticker": ticker,
        "sector_code": "01",
        "sector_name": "반도체/IT하드웨어",
        "market_cap": market_cap,
        "traded_value": traded_value,
        "foreign_net_buy_amount": 2.0,
        "foreign_net_buy_shares": 20.0,
        "institution_net_buy_amount": 3.0,
        "institution_net_buy_shares": 30.0,
        "daily_return": daily_return,
    }
