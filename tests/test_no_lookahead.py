from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar, derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import run_candidate_backtest
from src.data.universe import build_execution_universe
from src.features.flow_ratios import build_flow_ratios
from src.features.market_gate import build_market_gate_features
from src.strategies.a001_fixed_holding import build_e001_flow_filter_candidates


@pytest.fixture
def synthetic_panel() -> pd.DataFrame:
    dates = pd.date_range("2025-01-03", periods=42, freq="B")
    tickers = [f"{index:06d}" for index in range(1, 7)]
    rows = []

    for ticker_index, ticker in enumerate(tickers, start=1):
        for day_index, date in enumerate(dates):
            if ticker == "000006" and date == dates[12]:
                continue

            close_price = 80.0 + ticker_index * 11.0 + day_index * (0.7 + ticker_index / 20.0)
            open_price = close_price - 0.35 - ticker_index / 100.0
            traded_value = 6_200_000_000.0 + ticker_index * 90_000_000.0 + day_index * 18_000_000.0
            foreign_net = (ticker_index - 2) * 16_000_000.0 + day_index * 9_000_000.0
            institution_net = (3 - ticker_index) * 10_000_000.0 + day_index * 7_000_000.0

            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": open_price,
                    "KRX종가": close_price,
                    "거래대금추정": traded_value,
                    "시가총액추정": 1_000_000_000_000.0 + ticker_index * 10_000_000_000.0 + day_index * 1_000_000.0,
                    "외국인순매수금액추정": foreign_net,
                    "기관순매수금액추정": institution_net,
                    "수급금액추정여부": False,
                    "거래대금추정여부": False,
                    "동적유니버스포함": True,
                }
            )

    panel = pd.DataFrame(rows)
    panel.loc[
        (panel["종목코드"] == "000005") & (panel["날짜"].isin([dates[13], dates[14]])),
        "거래대금추정",
    ] = pd.NA
    panel.loc[
        (panel["종목코드"] == "000003") & (panel["날짜"] == dates[24]),
        "수급금액추정여부",
    ] = True
    panel.loc[
        (panel["종목코드"] == "000004") & (panel["날짜"] == dates[25]),
        "거래대금추정여부",
    ] = True

    return panel


@pytest.fixture
def synthetic_pipeline(
    synthetic_panel: pd.DataFrame,
) -> tuple[pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return _build_pipeline(synthetic_panel)


def _build_pipeline(
    panel: pd.DataFrame,
) -> tuple[pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    calendar = derive_trading_calendar(panel)
    features = build_flow_ratios(panel, calendar)
    universe = build_execution_universe(panel, calendar, exclude_estimated_flag_rows=True)
    candidates = build_e001_flow_filter_candidates(features, universe)
    return panel, calendar, features, universe, candidates


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def _candidate_set(candidates: pd.DataFrame, execution_date: pd.Timestamp) -> pd.DataFrame:
    columns = ["execution_date", "signal_date", "종목코드", "fnv_5", "inv_5", "combined_flow_5"]
    return (
        candidates.loc[candidates["execution_date"].eq(execution_date), columns]
        .sort_values(columns)
        .reset_index(drop=True)
    )


def _universe_set(universe: pd.DataFrame, execution_date: pd.Timestamp) -> pd.DataFrame:
    columns = ["execution_date", "signal_date", "종목코드", "avg_traded_value_20d"]
    return (
        universe.loc[universe["execution_date"].eq(execution_date), columns]
        .sort_values(columns)
        .reset_index(drop=True)
    )


def _mutate_panel_from_date(panel: pd.DataFrame, execution_date: pd.Timestamp) -> pd.DataFrame:
    mutated = panel.copy()
    future_mask = mutated["날짜"].ge(execution_date)
    mutated.loc[future_mask, "거래대금추정"] = 0.0
    mutated.loc[future_mask, "시가총액추정"] = 0.0
    mutated.loc[future_mask, "외국인순매수금액추정"] = -999_000_000_000.0
    mutated.loc[future_mask, "기관순매수금액추정"] = -999_000_000_000.0
    mutated.loc[future_mask, "시가"] = 0.0
    mutated.loc[future_mask, "KRX종가"] = 0.0
    mutated.loc[future_mask, "수급금액추정여부"] = ~mutated.loc[
        future_mask, "수급금액추정여부"
    ].astype(bool)
    mutated.loc[future_mask, "거래대금추정여부"] = ~mutated.loc[
        future_mask, "거래대금추정여부"
    ].astype(bool)
    mutated.loc[future_mask, "동적유니버스포함"] = ~mutated.loc[
        future_mask, "동적유니버스포함"
    ].astype(bool)
    return mutated


def test_signal_date_strictly_before_execution_date_in_signals_csv_equivalent(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    _, _, _, _, candidates = synthetic_pipeline

    assert not candidates.empty
    assert candidates["signal_date"].lt(candidates["execution_date"]).all()


def test_trade_holding_period_is_exact(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, _, candidates = synthetic_pipeline
    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[20],
        period_end=calendar.dates[-6],
    )

    holding_trades = result.trades.loc[result.trades["exit_reason"].eq("holding_period")]
    assert not holding_trades.empty
    for trade in holding_trades.itertuples(index=False):
        entry_index = calendar.dates.index(trade.entry_date)
        exit_index = calendar.dates.index(trade.exit_date)
        assert exit_index - entry_index == 5


def test_trade_entry_price_matches_panel_open_at_execution_date(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, _, candidates = synthetic_pipeline
    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[20],
        period_end=calendar.dates[-6],
    )
    prices = panel.set_index(["종목코드", "날짜"])["시가"]

    assert not result.trades.empty
    for trade in result.trades.itertuples(index=False):
        assert trade.entry_price == prices.loc[(trade.종목코드, trade.entry_date)]


def test_trade_exit_price_matches_panel_krx_close_at_exit_date(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, _, candidates = synthetic_pipeline
    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[20],
        period_end=calendar.dates[-6],
    )
    prices = panel.set_index(["종목코드", "날짜"])["KRX종가"]

    holding_trades = result.trades.loc[result.trades["exit_reason"].eq("holding_period")]
    assert not holding_trades.empty
    for trade in holding_trades.itertuples(index=False):
        assert trade.exit_price == prices.loc[(trade.종목코드, trade.exit_date)]


def test_universe_at_execution_date_reads_no_panel_row_with_date_at_or_after_execution_date(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, universe, _ = synthetic_pipeline
    execution_date = calendar.dates[27]
    before = _universe_set(universe, execution_date)
    mutated = _mutate_panel_from_date(panel, execution_date)
    _, _, _, mutated_universe, _ = _build_pipeline(mutated)
    after = _universe_set(mutated_universe, execution_date)

    assert not before.empty
    pd.testing.assert_frame_equal(after, before)


def test_strategy_candidates_at_execution_date_unchanged_by_future_panel_mutation(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, _, candidates = synthetic_pipeline
    execution_date = calendar.dates[27]
    before = _candidate_set(candidates, execution_date)
    mutated = _mutate_panel_from_date(panel, execution_date)
    _, _, _, _, mutated_candidates = _build_pipeline(mutated)
    after = _candidate_set(mutated_candidates, execution_date)

    assert not before.empty
    pd.testing.assert_frame_equal(after, before)


def test_full_backtest_trades_for_period_ending_at_T_unchanged_by_mutating_rows_after_T(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, _, _, candidates = synthetic_pipeline
    period_start = calendar.dates[20]
    period_end = calendar.dates[33]
    before = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=period_start,
        period_end=period_end,
    ).trades

    mutated = panel.copy()
    future_mask = mutated["날짜"].gt(period_end)
    mutated.loc[future_mask, "거래대금추정"] = 0.0
    mutated.loc[future_mask, "시가총액추정"] = 0.0
    mutated.loc[future_mask, "외국인순매수금액추정"] = -999_000_000_000.0
    mutated.loc[future_mask, "기관순매수금액추정"] = -999_000_000_000.0
    mutated.loc[future_mask, "시가"] = 0.0
    mutated.loc[future_mask, "KRX종가"] = 0.0
    mutated.loc[future_mask, "수급금액추정여부"] = True
    mutated.loc[future_mask, "거래대금추정여부"] = True
    mutated.loc[future_mask, "동적유니버스포함"] = False
    _, mutated_calendar, _, _, mutated_candidates = _build_pipeline(mutated)
    after = run_candidate_backtest(
        mutated,
        mutated_calendar,
        mutated_candidates,
        _costs(),
        period_start=period_start,
        period_end=period_end,
    ).trades

    assert not before.empty
    pd.testing.assert_frame_equal(after, before)


def test_holding_period_count_is_per_calendar_not_per_calendar_days() -> None:
    calendar = KRXTradingCalendar(pd.date_range("2025-01-03", periods=7, freq="B"))
    entry_date = pd.Timestamp("2025-01-03")

    exit_date = calendar.add_trading_days(entry_date, 5)

    assert exit_date == pd.Timestamp("2025-01-10")
    assert exit_date != entry_date + pd.Timedelta(days=5)


def test_market_gate_at_execution_date_uses_only_prior_signal_date_flows() -> None:
    calendar = KRXTradingCalendar(pd.date_range("2025-01-02", periods=8, freq="B"))
    flow = pd.DataFrame(
        {
            "date": calendar.dates,
            "kospi_foreign_net": [1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0],
            "kospi_institution_net": [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        }
    )
    signal_date = pd.Timestamp("2025-01-08")

    before = build_market_gate_features(flow, calendar)
    mutated = flow.copy()
    future_mask = mutated["date"].gt(signal_date)
    mutated.loc[future_mask, ["kospi_foreign_net", "kospi_institution_net"]] = -999.0
    after = build_market_gate_features(mutated, calendar)

    before_row = before.loc[before["signal_date"].eq(signal_date)].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(signal_date)].reset_index(drop=True)

    pd.testing.assert_frame_equal(after_row, before_row)
