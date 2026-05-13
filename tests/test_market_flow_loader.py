from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.data.market_flow import load_market_flow


def test_load_market_flow_reads_utf8_sig_and_required_columns(tmp_path: Path) -> None:
    path = tmp_path / "market_flow.csv"
    path.write_text(
        "\ufeffdate,kospi_foreign_net,kospi_institution_net,ignored\n"
        "2025-01-02,10,-3,1\n"
        "2025-01-03,5,2,2\n",
        encoding="utf-8",
    )
    calendar = KRXTradingCalendar(pd.to_datetime(["2025-01-02", "2025-01-03"]))

    result = load_market_flow(path, calendar)

    assert list(result.columns) == ["kospi_foreign_net", "kospi_institution_net"]
    assert list(result.index) == [pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-03")]
    assert result.loc[pd.Timestamp("2025-01-03"), "kospi_institution_net"] == 2


def test_load_market_flow_drops_dates_not_in_calendar(tmp_path: Path) -> None:
    path = tmp_path / "market_flow.csv"
    path.write_text(
        "date,kospi_foreign_net,kospi_institution_net\n"
        "2025-01-02,10,1\n"
        "2025-01-04,999,999\n"
        "2025-01-06,20,2\n",
        encoding="utf-8",
    )
    calendar = KRXTradingCalendar(pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]))

    result = load_market_flow(path, calendar)

    assert list(result.index) == [pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-06")]


def test_load_market_flow_raises_on_missing_required_column(tmp_path: Path) -> None:
    path = tmp_path / "market_flow.csv"
    path.write_text("date,kospi_foreign_net\n2025-01-02,10\n", encoding="utf-8")
    calendar = KRXTradingCalendar(pd.to_datetime(["2025-01-02"]))

    with pytest.raises(ValueError, match="missing required columns"):
        load_market_flow(path, calendar)


def test_load_market_flow_drops_nan_rows_inside_calendar_range(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "market_flow.csv"
    path.write_text(
        "date,kospi_foreign_net,kospi_institution_net\n"
        "2025-01-02,10,1\n"
        "2025-01-03,,2\n"
        "2025-01-06,20,3\n",
        encoding="utf-8",
    )
    calendar = KRXTradingCalendar(
        pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"])
    )

    result = load_market_flow(path, calendar)

    assert list(result.index) == [pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-06")]
    captured = capsys.readouterr().out
    assert "Dropping 1 NaN row" in captured


def test_load_market_flow_raises_on_duplicate_dates(tmp_path: Path) -> None:
    path = tmp_path / "market_flow.csv"
    path.write_text(
        "date,kospi_foreign_net,kospi_institution_net\n"
        "2025-01-02,10,1\n"
        "2025-01-02,11,2\n",
        encoding="utf-8",
    )
    calendar = KRXTradingCalendar(pd.to_datetime(["2025-01-02"]))

    with pytest.raises(ValueError, match="duplicate date"):
        load_market_flow(path, calendar)
