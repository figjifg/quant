from __future__ import annotations

import math

import pandas as pd

from src.audit.e007_vs_d013_attribution import (
    VALUE_COL,
    compare_spike_years,
    compare_year_breakdowns,
    quarterly_overlap,
)


def test_compare_year_breakdowns_counts_trades_by_entry_year() -> None:
    e007_equity = _equity(["2020-01-01", "2020-12-31", "2021-01-01", "2021-12-31"], [1.0, 1.1, 1.1, 1.32])
    d013_equity = _equity(["2020-01-01", "2020-12-31", "2021-01-01", "2021-12-31"], [1.0, 1.2, 1.2, 1.14])
    e007_trades = _trades(["2020-04-01", "2020-04-01", "2021-04-01"], ["000001", "000002", "000003"])
    d013_trades = _trades(["2020-04-01", "2021-04-01", "2021-04-01"], ["000001", "000004", "000005"])

    result = compare_year_breakdowns(e007_equity, e007_trades, d013_equity, d013_trades)

    row_2020 = result.loc[result["year"].eq(2020)].iloc[0]
    row_2021 = result.loc[result["year"].eq(2021)].iloc[0]
    assert math.isclose(row_2020["e007_cumulative_return"], 0.10)
    assert math.isclose(row_2020["d013_cumulative_return"], 0.20)
    assert row_2020["e007_trade_count"] == 2
    assert row_2021["e007_trade_count"] == 1
    assert row_2021["d013_trade_count"] == 2


def test_compare_spike_years_uses_total_cumulative_denominator() -> None:
    per_year = pd.DataFrame(
        {
            "year": [2020, 2025, 2026],
            "e007_cumulative_return": [0.10, 0.20, 0.30],
            "d013_cumulative_return": [0.05, 0.15, 0.25],
        }
    )

    result = compare_spike_years(per_year, spike_years=(2020, 2025))

    e007_2025 = result.loc[result["strategy"].eq("e007") & result["year_group"].eq("2025")].iloc[0]
    e007_total = (1.1 * 1.2 * 1.3) - 1.0
    assert math.isclose(e007_2025["total_cumulative_return"], e007_total)
    assert math.isclose(e007_2025["contribution_share"], 0.20 / e007_total)

    e007_combo = result.loc[result["strategy"].eq("e007") & result["year_group"].eq("2020+2025")].iloc[0]
    assert math.isclose(e007_combo["year_return_sum"], 0.30)
    assert math.isclose(e007_combo["cumulative_excluding_year_group"], e007_total - 0.30)


def test_quarterly_overlap_reports_jaccard_and_on_off_quarters() -> None:
    e007 = _trades(["2020-04-01", "2020-04-01", "2020-10-01"], ["000001", "000002", "000003"])
    d013 = _trades(["2020-04-01", "2020-04-01", "2020-07-01"], ["000001", "000004", "000005"])

    result = quarterly_overlap(e007, d013)

    q2 = result.loc[result["quarter"].eq("2020Q2")].iloc[0]
    assert q2["overlap_count"] == 1
    assert q2["union_count"] == 3
    assert math.isclose(q2["jaccard"], 1 / 3)
    assert math.isclose(q2["e007_same_as_d013_ratio"], 1 / 2)

    assert int(result["d013_on_e007_off"].sum()) == 1
    assert int(result["d013_off_e007_on"].sum()) == 1


def _equity(dates: list[str], values: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"date": pd.to_datetime(dates), VALUE_COL: values})


def _trades(entry_dates: list[str], tickers: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "entry_date": pd.to_datetime(entry_dates),
            "signal_date": pd.to_datetime(entry_dates) - pd.Timedelta(days=1),
            "exit_date": pd.to_datetime(entry_dates) + pd.Timedelta(days=60),
            "종목코드": pd.Series(tickers, dtype="string"),
        }
    )
