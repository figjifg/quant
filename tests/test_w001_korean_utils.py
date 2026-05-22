from __future__ import annotations

import pandas as pd

from src.utils.backtest_sanity_checks import check_entry_exit_lineage
from src.utils.corporate_action import adjust_for_corporate_actions, detect_impossible_returns
from src.utils.flow_safe import flow_with_safety_marker, is_flow_t1_safe, reconcile_sample
from src.utils.korean_calendar import KoreanTradingCalendar, trading_day_coverage
from src.utils.tradability import TRADABLE_STATES, mark_tradable_rows, tradable_state


def test_calendar_panel_dates_cover_at_least_90pct() -> None:
    panel = pd.DataFrame({"날짜": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"]), "KRX종가": [1, 2, 3]})
    calendar = KoreanTradingCalendar.from_panel(panel)
    assert trading_day_coverage(panel, calendar) >= 0.90
    assert calendar.is_trading_day("2026-01-05")
    assert calendar.next_trading_day("2026-01-02") == pd.Timestamp("2026-01-05")
    assert calendar.prev_trading_day("2026-01-06") == pd.Timestamp("2026-01-05")


def test_tradability_excludes_estimated_zero_value_and_limit_open() -> None:
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"]),
            "종목코드": ["005930", "005930", "005930"],
            "시가": [100.0, 130.0, 110.0],
            "고가": [101.0, 131.0, 111.0],
            "저가": [99.0, 129.0, 109.0],
            "KRX종가": [100.0, 120.0, 110.0],
            "거래대금추정": [1000.0, 1000.0, 0.0],
            "거래대금추정여부": [False, False, False],
            "동적유니버스포함": [True, True, True],
        }
    )
    out = mark_tradable_rows(panel)
    assert out["tradable"].tolist() == [True, False, False]


def test_impossible_return_and_lineage_checks() -> None:
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "종목코드": ["005930", "005930"],
            "KRX종가": [100.0, 170.0],
        }
    )
    bad_returns = detect_impossible_returns(panel)
    assert len(bad_returns) == 1

    calendar = KoreanTradingCalendar.from_panel(panel)
    trades = pd.DataFrame(
        {
            "signal_date": pd.to_datetime(["2026-01-02"]),
            "entry_date": pd.to_datetime(["2026-01-05"]),
            "exit_date": pd.to_datetime(["2026-01-05"]),
        }
    )
    assert check_entry_exit_lineage(trades, calendar) == 0


def test_adjust_for_corporate_actions_alias_only_and_source_marker() -> None:
    """Round 3 audit confirms adjust_for_corporate_actions() does not adjust prices.

    The W001 v1.x docstring fix now exposes this state explicitly via the
    `adjusted_*_source == 'unadjusted_raw_alias'` marker so downstream
    callers can detect that they are reading raw values.
    """
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"]),
            "종목코드": ["005930", "005930", "005930"],
            "시가": [100.0, 102.0, 103.0],
            "고가": [101.0, 103.0, 104.0],
            "저가": [99.0, 101.0, 102.0],
            "KRX종가": [100.0, 102.0, 103.0],
            "종가": [100.0, 102.0, 103.0],
        }
    )
    out = adjust_for_corporate_actions(panel)
    assert (out["adjusted_close"] == pd.to_numeric(out["종가"], errors="coerce")).all()
    assert (out["adjusted_close_source"] == "unadjusted_raw_alias").all()
    assert (out["adjusted_open_source"] == "unadjusted_raw_alias").all()


def test_tradable_state_partial_categorical() -> None:
    """W001 v1.x tradable_state() exposes the causes that can be classified
    from existing panel data alone.

    Cause priority (first match wins): data_missing > limit_lock_candidate
    > panel_absence > executable. Causes that need external sources
    (true_suspension, delisting_transition, corporate_action_day) are
    reserved in TRADABLE_STATES but never assigned in v1.x.
    """
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime(
                ["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"]
            ),
            "종목코드": ["005930"] * 5,
            "시가": [100.0, 130.0, 110.0, None, 120.0],
            "고가": [101.0, 131.0, 111.0, None, 121.0],
            "저가": [99.0, 129.0, 109.0, None, 119.0],
            "KRX종가": [100.0, 120.0, 110.0, None, 120.0],
            "거래대금추정": [1000.0, 1000.0, 0.0, 1000.0, 1000.0],
            "거래대금추정여부": [False, False, False, False, False],
            "동적유니버스포함": [True, True, True, True, False],
        }
    )
    state = tradable_state(panel)
    assert state.tolist() == [
        "executable",            # 2026-01-02 normal
        "limit_lock_candidate",  # 2026-01-05 30% gap (raw close jump, may include corp action)
        "data_missing",          # 2026-01-06 trading value = 0
        "data_missing",          # 2026-01-07 OHLC missing
        "panel_absence",         # 2026-01-08 not in dynamic universe
    ]
    # Reserved causes are in the enum but never set by v1.x
    assert "true_suspension" in TRADABLE_STATES
    assert "delisting_transition" in TRADABLE_STATES
    assert "corporate_action_day" in TRADABLE_STATES
    assert not state.isin({"true_suspension", "delisting_transition", "corporate_action_day"}).any()


def test_tradable_state_full_with_suspension_events() -> None:
    """W001 v2 C5: when suspension_events is supplied, tradable_state separates
    true_suspension (KRX-confirmed suspension window) and delisting_transition
    (after delisting event) from the legacy collapsed flags.
    """
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime([
                "2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07",
                "2026-01-02", "2026-01-05", "2026-01-06",
            ]),
            "종목코드": ["005930"] * 4 + ["000999"] * 3,
            "시가": [100.0, 102.0, 103.0, 104.0, 50.0, 51.0, 52.0],
            "고가": [101.0, 103.0, 104.0, 105.0, 51.0, 52.0, 53.0],
            "저가": [99.0, 101.0, 102.0, 103.0, 49.0, 50.0, 51.0],
            "KRX종가": [100.0, 102.0, 103.0, 104.0, 50.0, 51.0, 52.0],
            "거래대금추정": [1000.0] * 7,
            "거래대금추정여부": [False] * 7,
            "동적유니버스포함": [True] * 7,
        }
    )
    events = pd.DataFrame(
        {
            "ticker": ["005930", "005930", "000999"],
            "rcept_dt": pd.to_datetime(["2026-01-05", "2026-01-07", "2026-01-05"]),
            "category": ["suspension", "resumption", "delisting"],
        }
    )
    state = tradable_state(panel, suspension_events=events)
    # 005930: 1/2 executable, 1/5-1/6 true_suspension (in suspension window),
    # 1/7 executable again (resumption on 1/7 ends the window inclusive of start)
    # 000999: 1/2 executable, 1/5 delisting_transition, 1/6 delisting_transition
    assert state.tolist() == [
        "executable",
        "true_suspension",
        "true_suspension",
        "executable",
        "executable",
        "delisting_transition",
        "delisting_transition",
    ]


def test_flow_safety_marker_and_t1_check() -> None:
    """W001 v2 C7: flow_with_safety_marker exposes vendor estimation flag and
    a conservative t+1 safety boolean. Round 4 S6 reconciliation showed sample
    sign match 100% / institution 99.8% / within +/-5% = 95%; the wrapper
    captures that "vendor flag = True" is informational, not disqualifying.
    """
    panel = pd.DataFrame(
        {
            "날짜": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "종목코드": ["005930", "005930"],
            "거래대금추정": [1.0e12, 0.0],
            "수급금액추정여부": [True, True],
            "외국인순매수금액추정": [1.8e11, 0.0],
            "기관순매수금액추정": [4.5e10, 0.0],
            "외국인순매매량": [2.3e6, 0.0],
            "기관순매매량": [5.4e5, 0.0],
        }
    )
    annotated = flow_with_safety_marker(panel)
    assert annotated["flow_estimation_marker"].tolist() == [True, True]
    assert annotated["flow_t1_safe"].tolist() == [True, False]

    safe = is_flow_t1_safe(annotated.iloc[0])
    not_safe = is_flow_t1_safe(annotated.iloc[1])
    assert safe is True
    assert not_safe is False

    # Reconciliation helper returns 0 counts on empty merge (sanity only)
    krx_official = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02"]),
            "ticker": ["005930"],
            "krx_foreign": [1.83e11],
            "krx_institution": [4.5e10],
        }
    )
    metrics = reconcile_sample(panel, krx_official)
    assert metrics["n_pairs"] == 1
    assert metrics["foreign_sign_match_pct"] == 100.0
    assert metrics["institution_sign_match_pct"] == 100.0
