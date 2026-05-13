from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.features.market_gate import build_kospi_proxy_close_series, build_market_gate_features


def _calendar() -> KRXTradingCalendar:
    return KRXTradingCalendar(pd.date_range("2025-01-02", periods=8, freq="B"))


def _market_flow(values: list[tuple[float, float]]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=len(values), freq="B")
    return pd.DataFrame(
        {
            "date": dates,
            "kospi_foreign_net": [foreign for foreign, _ in values],
            "kospi_institution_net": [institution for _, institution in values],
        }
    )


def test_market_gate_uses_5_day_rolling_sum_ending_at_signal_date() -> None:
    calendar = _calendar()
    flow = _market_flow([(1, 1), (2, -1), (3, 1), (-1, 1), (4, 0), (-20, 0)])
    closes = pd.Series([100, 101, 102, 103, 104, 110, 111, 112], index=calendar.dates)

    result = build_market_gate_features(flow, calendar, closes)

    row = result.loc[result["signal_date"].eq(pd.Timestamp("2025-01-08"))].iloc[0]
    assert row["kospi_combined_net_5"] == 11
    assert bool(row["market_gate_on"]) is True
    assert row["execution_date"] == pd.Timestamp("2025-01-09")


def test_market_gate_is_false_when_window_is_insufficient_or_nan() -> None:
    calendar = _calendar()
    flow = _market_flow([(1, 1), (1, 1), (1, 1), (1, 1), (-10, 0)])
    flow.loc[2, "kospi_foreign_net"] = pd.NA

    result = build_market_gate_features(flow, calendar)

    assert result.loc[:3, "kospi_combined_net_5"].isna().all()
    assert not result.loc[:3, "market_gate_on"].any()
    assert pd.isna(result.loc[4, "kospi_combined_net_5"])
    assert bool(result.loc[4, "market_gate_on"]) is False
    assert bool(result.loc[4, "market_gate_off"]) is False


def test_inverted_gate_only_turns_on_when_flow_gate_is_well_defined_and_false() -> None:
    calendar = _calendar()
    flow = _market_flow([(1, 1), (1, 1), (1, 1), (1, 1), (-20, 0), (-1, -1)])

    result = build_market_gate_features(flow, calendar)

    assert not result.loc[:3, "market_gate_off"].any()
    assert bool(result.loc[4, "market_gate_defined"]) is True
    assert bool(result.loc[4, "market_gate_on"]) is False
    assert bool(result.loc[4, "market_gate_off"]) is True


def test_price_gate_uses_5_trading_day_return_and_double_gate_is_and() -> None:
    calendar = _calendar()
    flow = _market_flow([(2, 0)] * 8)
    closes = pd.Series([100, 101, 102, 103, 104, 106, 100, 99], index=calendar.dates)

    result = build_market_gate_features(flow, calendar, closes)

    positive = result.loc[result["signal_date"].eq(pd.Timestamp("2025-01-09"))].iloc[0]
    negative = result.loc[result["signal_date"].eq(pd.Timestamp("2025-01-13"))].iloc[0]
    assert abs(positive["kospi_5d_return"] - 0.06) < 1e-12
    assert bool(positive["price_gate_on"]) is True
    assert bool(positive["double_gate_on"]) is True
    assert negative["kospi_5d_return"] < 0
    assert bool(negative["price_gate_on"]) is False
    assert bool(negative["double_gate_on"]) is False


def test_market_gate_feature_at_signal_date_unchanged_by_future_flow_mutation() -> None:
    calendar = _calendar()
    flow = _market_flow([(1, 1), (1, 1), (1, 1), (1, 1), (2, 0), (2, 0), (2, 0), (2, 0)])
    signal_date = pd.Timestamp("2025-01-08")
    before = build_market_gate_features(flow, calendar)
    mutated = flow.copy()
    mutated.loc[mutated["date"].gt(signal_date), ["kospi_foreign_net", "kospi_institution_net"]] = -999
    after = build_market_gate_features(mutated, calendar)

    before_row = before.loc[before["signal_date"].eq(signal_date)].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(signal_date)].reset_index(drop=True)

    pd.testing.assert_frame_equal(after_row, before_row)


def test_missing_market_flow_calendar_date_is_conservative_gate_off() -> None:
    calendar = _calendar()
    flow = _market_flow([(5, 0), (5, 0), (5, 0), (5, 0), (5, 0)])
    flow = flow.loc[flow["date"].ne(pd.Timestamp("2025-01-06"))]

    result = build_market_gate_features(flow, calendar)

    assert pd.isna(result.loc[4, "kospi_combined_net_5"])
    assert bool(result.loc[4, "market_gate_on"]) is False


def test_kospi_proxy_close_series_is_defined_for_all_calendar_days() -> None:
    calendar = _calendar()
    rows = []
    for ticker, base in [("000010", 100.0), ("000020", 200.0)]:
        for index, date in enumerate(calendar.dates):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "KRX종가": base + index,
                    "거래대금추정": 1_000.0 + index,
                }
            )
    panel = pd.DataFrame(rows)

    proxy = build_kospi_proxy_close_series(panel, calendar)
    features = build_market_gate_features(_market_flow([(2, 0)] * 8), calendar, proxy)

    assert list(proxy.index) == list(calendar.dates)
    assert proxy.notna().all()
    assert features["price_gate_on"].dtype == bool
