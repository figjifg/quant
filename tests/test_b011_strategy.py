from __future__ import annotations

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.strategies.b011_gate_only_full_timeline import (
    build_kospi_buy_and_hold_result,
    run_b011_variants,
)


def test_b011_gate_only_trades_when_gate_on_and_none_when_gate_off() -> None:
    calendar = KRXTradingCalendar(pd.date_range("2025-01-02", periods=4, freq="B"))
    panel = _panel(calendar.dates)
    universe = _universe(calendar.dates)
    market_breadth = _market_breadth(calendar.dates, [0.0, 0.01, 0.01, 0.01])
    costs = Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0)

    runs_on, candidates_on, _ = run_b011_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        kospi_proxy=_kospi_proxy(calendar.dates, gate_on=True),
        market_breadth=market_breadth,
        costs=costs,
        segments=((calendar.dates[0], calendar.dates[-1]),),
        max_positions=5,
    )
    runs_off, candidates_off, _ = run_b011_variants(
        panel=panel,
        calendar=calendar,
        universe=universe,
        kospi_proxy=_kospi_proxy(calendar.dates, gate_on=False),
        market_breadth=market_breadth,
        costs=costs,
        segments=((calendar.dates[0], calendar.dates[-1]),),
        max_positions=5,
    )

    assert not candidates_on["gate_only_mcap"].empty
    assert len(runs_on["gate_only_mcap"].trades) > 0
    assert candidates_off["gate_only_mcap"].empty
    assert runs_off["gate_only_mcap"].trades.empty


def test_b011_kospi_buy_and_hold_tracks_cap_weighted_return_directly() -> None:
    calendar = KRXTradingCalendar(pd.date_range("2025-01-02", periods=4, freq="B"))
    market_breadth = _market_breadth(calendar.dates, [0.0, 0.10, -0.05, 0.20])

    result = build_kospi_buy_and_hold_result(
        market_breadth,
        calendar=calendar,
        segments=((calendar.dates[0], calendar.dates[-1]),),
    )

    assert result.trades.empty
    assert result.equity_curve["net_value"].round(6).tolist() == [1.0, 1.1, 1.045, 1.254]
    assert result.equity_curve["cash"].tolist() == [0.0, 0.0, 0.0, 0.0]


def _panel(dates: tuple[pd.Timestamp, ...]) -> pd.DataFrame:
    rows = []
    for date_index, date in enumerate(dates):
        for ticker_index in range(6):
            ticker = f"00000{ticker_index}"
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": 100.0 + date_index,
                    "KRX종가": 101.0 + date_index,
                    "상장주식수": 1_000_000 + ticker_index,
                }
            )
    return pd.DataFrame(rows)


def _universe(dates: tuple[pd.Timestamp, ...]) -> pd.DataFrame:
    rows = []
    for signal_date, execution_date in zip(dates[:-1], dates[1:], strict=False):
        for ticker_index in range(6):
            rows.append(
                {
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": f"00000{ticker_index}",
                }
            )
    return pd.DataFrame(rows)


def _kospi_proxy(dates: tuple[pd.Timestamp, ...], *, gate_on: bool) -> pd.DataFrame:
    level = 2.0 if gate_on else 1.0
    sma = 1.0 if gate_on else 2.0
    return pd.DataFrame(
        {
            "kospi_proxy_level": [level] * len(dates),
            "kospi_proxy_sma_200": [sma] * len(dates),
        },
        index=pd.Index(dates, name="date"),
    )


def _market_breadth(dates: tuple[pd.Timestamp, ...], returns: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"date": list(dates), "cap_weighted_return": returns})
