from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar, derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import run_candidate_backtest
from src.data.universe import build_execution_universe
from src.features.flow_ratios import build_flow_ratios
from src.features.market_gate import build_market_gate_features
from src.features.relative_flow import build_relative_flow_features
from src.features.sector_breadth_score import build_sector_breadth_scores
from src.features.sector_combined_score import build_sector_combined_scores
from src.features.stock_foreign_flow_score import build_stock_foreign_flow_scores
from src.features.stock_institution_flow_score import build_stock_institution_flow_scores
from src.features.stock_combined_score import build_stock_combined_scores
from src.features.stress_filter import stress_filter_scalars
from src.roles.filters import filter_persistence_4_of_5
from src.strategies.a001_fixed_holding import build_e001_flow_filter_candidates
from src.strategies.p002_d013_execution import SCENARIOS, p002_shift_candidates


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


def test_stress_filter_at_signal_date_unchanged_by_future_macro_and_kospi_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dates = pd.date_range("2025-01-01", periods=12, freq="B")
    aligned = pd.DataFrame(
        {
            "signal_date": dates,
            "vix": [20, 19, 18, 21, 22, 23, 24, 26, 27, 28, 29, 30],
            "dexkous_usdkrw": [1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090, 1100, 1110],
        }
    )
    breadth = pd.DataFrame(
        {
            "date": dates,
            "cap_weighted_return": [0.01, -0.01, 0.02, -0.02, 0.03, -0.03, 0.01, -0.01, 0.02, -0.02, 0.03, -0.03],
        }
    )

    def fake_align(signal_dates: object, input_dir: str) -> pd.DataFrame:
        wanted = pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()
        return aligned.loc[aligned["signal_date"].isin(wanted)].reset_index(drop=True)

    monkeypatch.setattr("src.features.stress_filter.align_macro_factors_to_korean_signal_dates", fake_align)
    before = stress_filter_scalars(
        dates,
        macro_data_dir="unused",
        market_breadth=breadth,
        z_window=3,
        usdkrw_yoy_lookback_days=3,
        kospi_vol_window=3,
    )

    mutated_aligned = aligned.copy()
    mutated_aligned.loc[mutated_aligned["signal_date"].gt(dates[8]), ["vix", "dexkous_usdkrw"]] = 9999.0
    mutated_breadth = breadth.copy()
    mutated_breadth.loc[pd.to_datetime(mutated_breadth["date"]).gt(dates[8]), "cap_weighted_return"] = 9.0

    def fake_mutated_align(signal_dates: object, input_dir: str) -> pd.DataFrame:
        wanted = pd.to_datetime(pd.Series(signal_dates), errors="raise").dt.normalize()
        return mutated_aligned.loc[mutated_aligned["signal_date"].isin(wanted)].reset_index(drop=True)

    monkeypatch.setattr("src.features.stress_filter.align_macro_factors_to_korean_signal_dates", fake_mutated_align)
    after = stress_filter_scalars(
        dates,
        macro_data_dir="unused",
        market_breadth=mutated_breadth,
        z_window=3,
        usdkrw_yoy_lookback_days=3,
        kospi_vol_window=3,
    )

    columns = ["VIX_z", "USDKRW_z", "KOSPI_vol_z", "stress_score", "exposure_scalar"]
    before_row = before.loc[before["signal_date"].eq(dates[8]), columns].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(dates[8]), columns].reset_index(drop=True)
    pd.testing.assert_frame_equal(after_row, before_row)


def test_combined_flow_1_at_signal_date_unchanged_by_future_panel_mutation(
    synthetic_pipeline: tuple[
        pd.DataFrame, KRXTradingCalendar, pd.DataFrame, pd.DataFrame, pd.DataFrame
    ],
) -> None:
    panel, calendar, features, _, _ = synthetic_pipeline
    signal_date = calendar.dates[26]
    ticker = "000002"
    before = features.loc[
        features["종목코드"].eq(ticker) & features["날짜"].eq(signal_date),
        "combined_flow_1",
    ].iloc[0]

    mutated = panel.copy()
    mutated.loc[mutated["날짜"].gt(signal_date), "거래대금추정"] = 1.0
    mutated.loc[mutated["날짜"].gt(signal_date), "외국인순매수금액추정"] = -999_000_000_000.0
    mutated.loc[mutated["날짜"].gt(signal_date), "기관순매수금액추정"] = -999_000_000_000.0
    mutated_features = build_flow_ratios(mutated, calendar)
    after = mutated_features.loc[
        mutated_features["종목코드"].eq(ticker) & mutated_features["날짜"].eq(signal_date),
        "combined_flow_1",
    ].iloc[0]

    assert after == before


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


def test_p002_execution_scenarios_keep_execution_after_signal_date() -> None:
    calendar = KRXTradingCalendar(pd.to_datetime(["2025-03-31", "2025-04-01", "2025-04-02", "2025-04-03"]))
    candidates = pd.DataFrame(
        [
            {
                "signal_date": pd.Timestamp("2025-03-31"),
                "execution_date": pd.Timestamp("2025-04-01"),
                "종목코드": "000001",
                "market_cap": 1_000.0,
                "rank": 1,
            }
        ]
    )
    segments = ((pd.Timestamp("2025-03-31"), pd.Timestamp("2025-04-03")),)

    for spec in SCENARIOS.values():
        shifted = p002_shift_candidates(
            candidates,
            calendar,
            delay_trading_days=int(spec["delay_trading_days"]),
            segments=segments,
        )
        assert not shifted.empty
        assert shifted["signal_date"].lt(shifted["execution_date"]).all()


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


def test_relative_flow_cross_sectional_moments_at_signal_date_ignore_future_rows() -> None:
    current_signal_date = pd.Timestamp("2025-01-08")
    future_signal_date = pd.Timestamp("2025-01-09")
    rows = []
    for signal_date in (current_signal_date, future_signal_date):
        execution_date = signal_date + pd.Timedelta(days=1)
        for ticker_index in range(1, 31):
            rows.append(
                {
                    "날짜": signal_date,
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": f"{ticker_index:06d}",
                    "fnv_5": float(ticker_index),
                    "inv_5": float(ticker_index + 100),
                    "combined_flow_5": float(ticker_index + 200),
                }
            )
    features = pd.DataFrame(rows)
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    before = build_relative_flow_features(features, universe, min_count=30)
    mutated = features.copy()
    future_mask = mutated["signal_date"].eq(future_signal_date)
    mutated.loc[future_mask, ["fnv_5", "inv_5", "combined_flow_5"]] = 999_000.0
    after = build_relative_flow_features(mutated, universe, min_count=30)

    columns = ["종목코드", "fnv_5_z", "inv_5_z", "combined_flow_5_z", "fnv_5_rel", "inv_5_rel", "combined_flow_5_rel"]
    before_rows = before.loc[before["signal_date"].eq(current_signal_date), columns].reset_index(drop=True)
    after_rows = after.loc[after["signal_date"].eq(current_signal_date), columns].reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)


def test_persistence_4_of_5_at_signal_date_ignores_future_daily_flow_rows() -> None:
    dates = pd.bdate_range("2025-01-02", periods=7)
    features = pd.DataFrame(
        {
            "execution_date": dates + pd.offsets.BDay(1),
            "signal_date": dates,
            "종목코드": ["000010"] * len(dates),
            "fnv_5": [0.1] * len(dates),
            "inv_5": [0.1] * len(dates),
            "combined_flow_5": [0.2] * len(dates),
        }
    )
    daily = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    daily["combined_flow_1"] = [0.1, -0.1, 0.2, 0.3, 0.4, -0.2, -0.3]
    signal_date = dates[4]

    before = filter_persistence_4_of_5(features, daily)
    mutated = daily.copy()
    mutated.loc[mutated["signal_date"].gt(signal_date), "combined_flow_1"] = 999_000.0
    after = filter_persistence_4_of_5(features, mutated)

    before_row = before.loc[before["signal_date"].eq(signal_date)].reset_index(drop=True)
    after_row = after.loc[after["signal_date"].eq(signal_date)].reset_index(drop=True)

    assert not before_row.empty
    pd.testing.assert_frame_equal(after_row, before_row)


def test_sector_combined_score_at_signal_date_ignores_future_component_rows() -> None:
    current_signal_date = pd.Timestamp("2025-03-31")
    future_signal_date = pd.Timestamp("2025-06-30")
    flow_scores = pd.DataFrame(
        {
            "signal_date": [current_signal_date, current_signal_date, future_signal_date, future_signal_date],
            "sector_code": ["01", "02", "01", "02"],
            "sector_name": ["sector_01", "sector_02", "sector_01", "sector_02"],
            "flow_score": [1.0, -1.0, 0.5, -0.5],
        }
    )
    rs_scores = pd.DataFrame(
        {
            "signal_date": [current_signal_date, current_signal_date, future_signal_date, future_signal_date],
            "sector_code": ["01", "02", "01", "02"],
            "sector_name": ["sector_01", "sector_02", "sector_01", "sector_02"],
            "rs_score": [0.5, 1.5, -0.5, 0.5],
        }
    )

    before = build_sector_combined_scores(flow_scores, rs_scores)
    mutated_flow = flow_scores.copy()
    mutated_rs = rs_scores.copy()
    mutated_flow.loc[mutated_flow["signal_date"].gt(current_signal_date), "flow_score"] = -999_000.0
    mutated_rs.loc[mutated_rs["signal_date"].gt(current_signal_date), "rs_score"] = 999_000.0
    after = build_sector_combined_scores(mutated_flow, mutated_rs)

    columns = ["signal_date", "sector_code", "flow_score", "rs_score", "combined_score"]
    before_rows = before.loc[before["signal_date"].eq(current_signal_date), columns].reset_index(drop=True)
    after_rows = after.loc[after["signal_date"].eq(current_signal_date), columns].reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)


def test_sector_breadth_score_at_signal_date_ignores_future_stock_and_kospi_rows() -> None:
    dates = pd.date_range("2025-01-02", periods=5, freq="B")
    rows = []
    for date in dates:
        for ticker, sector_code, flow, daily_return in (
            ("000001", "01", 10.0, 0.02),
            ("000002", "01", -10.0, 0.02),
            ("000003", "01", 10.0, -0.02),
            ("000004", "02", -10.0, -0.01),
            ("000005", "02", -10.0, 0.01),
            ("000006", "02", 10.0, -0.01),
        ):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "market_cap": 1_000.0,
                    "foreign_net_buy_amount": flow,
                    "daily_return": daily_return,
                }
            )
    stock = pd.DataFrame(rows)
    kospi = pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] * len(dates)})
    signal_date = pd.Timestamp("2025-01-07")

    before = build_sector_breadth_scores(stock, kospi, signal_dates=[signal_date], window=2)
    mutated_stock = stock.copy()
    mutated_kospi = kospi.copy()
    mutated_stock.loc[pd.to_datetime(mutated_stock["date"]).gt(signal_date), "foreign_net_buy_amount"] = 999_000.0
    mutated_stock.loc[pd.to_datetime(mutated_stock["date"]).gt(signal_date), "daily_return"] = 999.0
    mutated_kospi.loc[pd.to_datetime(mutated_kospi["date"]).gt(signal_date), "cap_weighted_return"] = -0.99
    after = build_sector_breadth_scores(mutated_stock, mutated_kospi, signal_dates=[signal_date], window=2)

    columns = ["signal_date", "sector_code", "sector_breadth_strict", "breadth_score"]
    before_rows = before.loc[:, columns].sort_values("sector_code").reset_index(drop=True)
    after_rows = after.loc[:, columns].sort_values("sector_code").reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)


def test_stock_foreign_flow_score_at_signal_date_ignores_future_stock_flow_rows() -> None:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    signal_date = pd.Timestamp("2025-01-07")
    rows = []
    for ticker, sector_code, foreign_values in (
        ("000001", "01", [10.0, 20.0, 30.0, 40.0, -1.0, -1.0]),
        ("000002", "01", [5.0, 5.0, 5.0, 5.0, 1.0, 1.0]),
        ("000003", "02", [3.0, 3.0, 3.0, 3.0, 1.0, 1.0]),
        ("000004", "02", [0.0, 1.0, 0.0, 1.0, 1.0, 1.0]),
    ):
        for date, foreign_value in zip(dates, foreign_values, strict=True):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "market_cap": 1_000.0,
                    "traded_value": 100.0,
                    "foreign_net_buy_amount": foreign_value,
                    "daily_return": 0.0,
                }
            )
    stock = pd.DataFrame(rows)

    before = build_stock_foreign_flow_scores(stock, signal_dates=[signal_date], value_window=2, mcap_window=3)
    mutated = stock.copy()
    future_mask = pd.to_datetime(mutated["date"]).gt(signal_date)
    mutated.loc[future_mask, "foreign_net_buy_amount"] = 999_000.0
    mutated.loc[future_mask, "traded_value"] = 1.0
    mutated.loc[future_mask, "market_cap"] = 1.0
    after = build_stock_foreign_flow_scores(mutated, signal_dates=[signal_date], value_window=2, mcap_window=3)

    columns = ["signal_date", "ticker", "raw_stock_foreign_flow_score", "stock_foreign_flow_score"]
    before_rows = before.loc[:, columns].sort_values("ticker").reset_index(drop=True)
    after_rows = after.loc[:, columns].sort_values("ticker").reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)


def test_stock_institution_flow_score_at_signal_date_ignores_future_stock_flow_rows() -> None:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    signal_date = pd.Timestamp("2025-01-07")
    rows = []
    for ticker, sector_code, institution_values in (
        ("000001", "01", [10.0, 20.0, 30.0, 40.0, -1.0, -1.0]),
        ("000002", "01", [5.0, 5.0, 5.0, 5.0, 1.0, 1.0]),
        ("000003", "02", [3.0, 3.0, 3.0, 3.0, 1.0, 1.0]),
        ("000004", "02", [0.0, 1.0, 0.0, 1.0, 1.0, 1.0]),
    ):
        for date, institution_value in zip(dates, institution_values, strict=True):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "market_cap": 1_000.0,
                    "traded_value": 100.0,
                    "institution_net_buy_amount": institution_value,
                    "daily_return": 0.0,
                }
            )
    stock = pd.DataFrame(rows)

    before = build_stock_institution_flow_scores(stock, signal_dates=[signal_date], value_window=2, mcap_window=3)
    mutated = stock.copy()
    future_mask = pd.to_datetime(mutated["date"]).gt(signal_date)
    mutated.loc[future_mask, "institution_net_buy_amount"] = 999_000.0
    mutated.loc[future_mask, "traded_value"] = 1.0
    mutated.loc[future_mask, "market_cap"] = 1.0
    after = build_stock_institution_flow_scores(mutated, signal_dates=[signal_date], value_window=2, mcap_window=3)

    columns = ["signal_date", "ticker", "raw_stock_institution_flow_score", "stock_institution_flow_score"]
    before_rows = before.loc[:, columns].sort_values("ticker").reset_index(drop=True)
    after_rows = after.loc[:, columns].sort_values("ticker").reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)


def test_stock_combined_score_at_signal_date_ignores_future_component_rows() -> None:
    dates = pd.date_range("2025-01-02", periods=8, freq="B")
    signal_date = pd.Timestamp("2025-01-09")
    rows = []
    for ticker, sector_code, scale in (
        ("000001", "01", 1.0),
        ("000002", "01", 2.0),
        ("000003", "02", 3.0),
        ("000004", "02", 4.0),
    ):
        for day_index, date in enumerate(dates):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": f"sector_{sector_code}",
                    "market_cap": 1_000.0 + scale,
                    "traded_value": 100.0 + scale,
                    "foreign_net_buy_amount": scale * (day_index + 1.0),
                    "institution_net_buy_amount": scale * (2.0 - day_index / 10.0),
                    "daily_return": 0.001 * scale * (day_index + 1.0),
                }
            )
    stock = pd.DataFrame(rows)
    sector = (
        stock.groupby(["date", "sector_code", "sector_name"], as_index=False)["daily_return"]
        .mean()
        .rename(columns={"daily_return": "cap_weighted_return"})
    )

    before = build_stock_combined_scores(
        stock,
        sector,
        variant="f007",
        signal_dates=[signal_date],
        short_window=2,
        long_window=3,
        flow_value_window=2,
        flow_mcap_window=3,
        liquidity_short_window=2,
        liquidity_long_window=4,
        volatility_window=3,
    )
    mutated = stock.copy()
    future_mask = pd.to_datetime(mutated["date"]).gt(signal_date)
    mutated.loc[future_mask, ["foreign_net_buy_amount", "institution_net_buy_amount"]] = -999_000.0
    mutated.loc[future_mask, ["traded_value", "market_cap"]] = 1.0
    mutated.loc[future_mask, "daily_return"] = -0.99
    after = build_stock_combined_scores(
        mutated,
        sector,
        variant="f007",
        signal_dates=[signal_date],
        short_window=2,
        long_window=3,
        flow_value_window=2,
        flow_mcap_window=3,
        liquidity_short_window=2,
        liquidity_long_window=4,
        volatility_window=3,
    )

    columns = ["signal_date", "ticker", "raw_stock_combined_score", "stock_combined_score"]
    before_rows = before.loc[:, columns].sort_values("ticker").reset_index(drop=True)
    after_rows = after.loc[:, columns].sort_values("ticker").reset_index(drop=True)

    pd.testing.assert_frame_equal(after_rows, before_rows)
