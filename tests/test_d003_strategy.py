from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.costs import Costs
from src.features.macro_regime import factor_aggregation_composite
from src.strategies.d003_block_expansion import run_d003_variants


def test_d003_config_has_frozen_block_expansion_structure() -> None:
    config = yaml.safe_load(Path("configs/backtests/d003.yaml").read_text(encoding="utf-8"))
    blocks = config["regime"]["blocks"]
    variables = [variable for block in blocks for variable in block["vars"]]

    assert [block["name"] for block in blocks] == ["global_risk", "usd_fx", "rates", "inflation", "commodity"]
    assert len(variables) == 13
    assert any(variable == {"name": "kr10y_yoy_change", "sign": -1} for variable in blocks[2]["vars"])
    assert all(block["name"] != "korea" for block in blocks)
    assert {"name": "usdjpy_yoy", "sign": 1} in blocks[0]["vars"]


def test_d003_within_block_average_changes_multi_variable_block_scores() -> None:
    dates = pd.date_range("2020-01-31", periods=60, freq="ME")
    regime = _d003_factor_regime_frame(dates)
    blocks = _d003_blocks()

    result = factor_aggregation_composite(regime, z_score_window_months=60, blocks=blocks)
    row = result.iloc[-1]

    assert row["block_usd_fx_score"] == pytest.approx(
        (row["usdkrw_yoy_fav_score"] + row["dxy_yoy_fav_score"] + row["usdcny_yoy_fav_score"]) / 3.0
    )
    assert row["block_rates_score"] == pytest.approx(
        (
            row["us_2_10_curve_fav_score"]
            + row["kr10y_yoy_change_fav_score"]
            + row["kr3m_yoy_change_fav_score"]
            + row["jp10y_yoy_change_fav_score"]
        )
        / 4.0
    )
    assert row["block_inflation_score"] == pytest.approx(
        (row["us_cpi_decel_fav_score"] + row["us_ppi_decel_fav_score"] + row["kr_cpi_decel_fav_score"]) / 3.0
    )
    for block_name, fav_columns in {
        "usd_fx": ["usdkrw_yoy_fav_score", "dxy_yoy_fav_score", "usdcny_yoy_fav_score"],
        "rates": ["us_2_10_curve_fav_score", "kr10y_yoy_change_fav_score", "kr3m_yoy_change_fav_score"],
        "inflation": ["us_cpi_decel_fav_score", "us_ppi_decel_fav_score", "kr_cpi_decel_fav_score"],
    }.items():
        block_score = row[f"block_{block_name}_score"]
        assert any(block_score != pytest.approx(row[column]) for column in fav_columns)


def test_d003_zscore_window_uses_no_future_rows() -> None:
    dates = pd.date_range("2020-01-31", periods=61, freq="ME")
    before = _d003_factor_regime_frame(dates)
    after = before.copy()
    after.loc[60, after.columns.difference(["signal_date"])] = 9999.0
    blocks = _d003_blocks()

    before_result = factor_aggregation_composite(before, z_score_window_months=60, blocks=blocks)
    after_result = factor_aggregation_composite(after, z_score_window_months=60, blocks=blocks)

    columns = [column for column in before_result.columns if column.endswith("_z") or column.startswith("block_")]
    columns.append("composite")
    pd.testing.assert_series_equal(before_result.loc[59, columns], after_result.loc[59, columns])


def test_d003_factor_quarterly_gate_uses_next_day_execution() -> None:
    dates = pd.to_datetime(["2025-03-31", "2025-04-01", "2025-06-30", "2025-07-01"])
    calendar = KRXTradingCalendar(dates)

    runs, candidates = run_d003_variants(
        panel=_panel(dates),
        calendar=calendar,
        universe=_universe(dates),
        quarterly_regime=_quarterly_regime(["2025-03-31", "2025-06-30"], [True, False]),
        market_breadth=_market_breadth(dates),
        costs=Costs(commission_bps=0.0, tax_bps_sell=0.0, slippage_bps=0.0),
        segments=((dates[0], dates[-1]),),
        max_positions=5,
    )

    assert set(runs) == {"factor_macro_gate_mcap", "kospi_buy_and_hold", "cash"}
    assert candidates["factor_macro_gate_mcap"]["signal_date"].unique().tolist() == [pd.Timestamp("2025-03-31")]
    assert runs["factor_macro_gate_mcap"].trades["entry_date"].tolist() == [pd.Timestamp("2025-04-01")] * 5
    assert all(runs["factor_macro_gate_mcap"].trades["entry_date"] > runs["factor_macro_gate_mcap"].trades["signal_date"])


def _d003_blocks() -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    config = yaml.safe_load(Path("configs/backtests/d003.yaml").read_text(encoding="utf-8"))
    return tuple(
        (block["name"], tuple((variable["name"], int(variable["sign"])) for variable in block["vars"]))
        for block in config["regime"]["blocks"]
    )


def _d003_factor_regime_frame(dates: pd.DatetimeIndex) -> pd.DataFrame:
    values = pd.Series(range(1, len(dates) + 1), dtype="float64")
    reverse = values.iloc[::-1].reset_index(drop=True)
    return pd.DataFrame(
        {
            "signal_date": dates,
            "VIX_60d_avg": values,
            "VIX_240d_avg": [1.0] * len(dates),
            "USDJPY_yoy": values,
            "USDKRW_yoy": values,
            "DXY_yoy": reverse,
            "USDCNY_yoy": [1.0] * len(dates),
            "US_2_10_curve_spread": values,
            "KR10Y_yoy_change": values,
            "KR3M_yoy_change": reverse,
            "JP10Y_yoy_change": [1.0] * len(dates),
            "US_CPI_decel": values,
            "US_PPI_decel": reverse,
            "KR_CPI_decel": [1.0] * len(dates),
            "Brent_yoy": values,
        }
    )


def _panel(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for date_index, date in enumerate(dates):
        for ticker_index in range(6):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": f"00000{ticker_index}",
                    "시가": 100.0 + date_index,
                    "KRX종가": 101.0 + date_index,
                    "상장주식수": 1_000_000 + ticker_index,
                }
            )
    return pd.DataFrame(rows)


def _universe(dates: pd.DatetimeIndex) -> pd.DataFrame:
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


def _quarterly_regime(signal_dates: list[str], regime_on: list[bool]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": pd.to_datetime(signal_dates),
            "composite": [0.1 if on else -0.1 for on in regime_on],
            "regime_score": [0.1 if on else -0.1 for on in regime_on],
            "regime_on": regime_on,
        }
    )


def _market_breadth(dates: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] + [0.01] * (len(dates) - 1)})
