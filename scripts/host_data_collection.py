from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "research_input_data" / "inputs"
GLOBAL_ETF_DIR = INPUT_DIR / "global_etf"
EQUITY_PANEL_DIR = INPUT_DIR / "equity_panels"


@dataclass(frozen=True)
class YFTarget:
    ticker: str
    start: str
    output_name: str
    label: str


LONG_HISTORY_TARGETS = [
    YFTarget("QQQ", "1999-03-01", "yf_QQQ_long.csv", "I003.6 long-history"),
    YFTarget("SPY", "1993-01-01", "yf_SPY_long.csv", "I003.6 long-history"),
    YFTarget("IEF", "2002-07-01", "yf_IEF_long.csv", "I003.6 long-history"),
    YFTarget("TLT", "2002-07-01", "yf_TLT_long.csv", "I003.6 long-history"),
    YFTarget("GLD", "2004-11-01", "yf_GLD_long.csv", "I003.6 long-history"),
]

EM_TARGETS = [
    YFTarget("VWO", "2005-03-01", "yf_em_VWO.csv", "J-family EM sleeve"),
    YFTarget("EWY", "2000-05-01", "yf_em_EWY.csv", "J-family EM sleeve"),
    YFTarget("EWJ", "1996-03-01", "yf_em_EWJ.csv", "J-family EM sleeve"),
    YFTarget("EWZ", "2000-07-01", "yf_em_EWZ.csv", "J-family EM sleeve"),
    YFTarget("MCHI", "2011-03-01", "yf_em_MCHI.csv", "J-family EM sleeve"),
]

SECTOR_TARGETS = [
    YFTarget("XLE", "1998-12-01", "yf_sector_XLE.csv", "K-family US sector"),
    YFTarget("XLF", "1998-12-01", "yf_sector_XLF.csv", "K-family US sector"),
    YFTarget("XLK", "1998-12-01", "yf_sector_XLK.csv", "K-family US sector"),
    YFTarget("XLV", "1998-12-01", "yf_sector_XLV.csv", "K-family US sector"),
    YFTarget("XLI", "1998-12-01", "yf_sector_XLI.csv", "K-family US sector"),
    YFTarget("XLY", "1998-12-01", "yf_sector_XLY.csv", "K-family US sector"),
    YFTarget("XLP", "1998-12-01", "yf_sector_XLP.csv", "K-family US sector"),
    YFTarget("XLU", "1998-12-01", "yf_sector_XLU.csv", "K-family US sector"),
    YFTarget("XLB", "1998-12-01", "yf_sector_XLB.csv", "K-family US sector"),
    YFTarget("XLRE", "2015-10-01", "yf_sector_XLRE.csv", "K-family US sector"),
    YFTarget("XLC", "2018-06-01", "yf_sector_XLC.csv", "K-family US sector"),
]

CRYPTO_TARGETS = [
    YFTarget("BTC-USD", "2014-09-01", "yf_crypto_BTC-USD.csv", "M-family crypto sleeve"),
    YFTarget("ETH-USD", "2017-11-01", "yf_crypto_ETH-USD.csv", "M-family crypto sleeve"),
]

FX_TARGETS = [
    YFTarget("FXY", "2007-02-01", "yf_fx_FXY.csv", "currency hedge"),
    YFTarget("FXE", "2005-12-01", "yf_fx_FXE.csv", "currency hedge"),
]


def main() -> int:
    print("Host data collection started.")
    print(f"Repo root: {ROOT}")
    print("Network is required. Run this on the user host, not in Codex sandbox.")
    GLOBAL_ETF_DIR.mkdir(parents=True, exist_ok=True)
    EQUITY_PANEL_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    try:
        download_yfinance_targets(
            LONG_HISTORY_TARGETS + EM_TARGETS + SECTOR_TARGETS + CRYPTO_TARGETS + FX_TARGETS
        )
    except Exception as exc:  # noqa: BLE001
        failures.append(f"yfinance downloads failed: {exc}")

    try:
        download_kosdaq150_panel()
    except Exception as exc:  # noqa: BLE001
        failures.append(f"pykrx KOSDAQ150 download failed: {exc}")

    if failures:
        print("\nFAILED")
        for failure in failures:
            print(f"- {failure}")
        print("\nFix the errors above, then rerun this script. Partial CSVs may exist.")
        return 1

    print("\nSUCCESS")
    print("All requested backlog data files were written.")
    print("Next: update research_input_data/docs/DATA_CATALOG.md with the new files.")
    return 0


def download_yfinance_targets(targets: list[YFTarget]) -> None:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("missing dependency: install yfinance in the host environment") from exc

    for index, target in enumerate(targets, start=1):
        output_path = GLOBAL_ETF_DIR / target.output_name
        print(f"\n[{index}/{len(targets)}] {target.label}: downloading {target.ticker} from {target.start}")
        data = yf.download(
            target.ticker,
            start=target.start,
            progress=False,
            auto_adjust=True,
            actions=False,
            threads=False,
        )
        if data.empty:
            raise RuntimeError(f"{target.ticker}: yfinance returned no rows")
        data = flatten_yfinance_columns(data)
        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required.difference(data.columns)
        if missing:
            raise RuntimeError(f"{target.ticker}: missing columns after download: {sorted(missing)}")
        data = data.reset_index()
        if "Date" not in data.columns:
            first_col = data.columns[0]
            data = data.rename(columns={first_col: "Date"})
        data["Date"] = pd.to_datetime(data["Date"]).dt.strftime("%Y-%m-%d")
        data.insert(0, "Ticker", target.ticker)
        data.to_csv(output_path, index=False)
        print(f"  wrote {len(data):,} rows -> {output_path.relative_to(ROOT)}")


def flatten_yfinance_columns(data: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(data.columns, pd.MultiIndex):
        return data.copy()
    flattened = data.copy()
    flattened.columns = [
        col[0] if col[0] in {"Open", "High", "Low", "Close", "Volume"} else "_".join(str(part) for part in col if part)
        for col in flattened.columns
    ]
    return flattened


def download_kosdaq150_panel() -> None:
    try:
        from pykrx import stock
    except ImportError as exc:
        raise RuntimeError("missing dependency: install pykrx in the host environment") from exc

    output_path = EQUITY_PANEL_DIR / "pykrx_kosdaq150_panel.csv"
    print("\n[KOSDAQ150] collecting quarterly constituent snapshots and daily OHLCV")
    quarter_dates = quarter_end_dates("20100101", "20261231")
    ticker_to_names: dict[str, str] = {}
    tickers: set[str] = set()
    membership_rows: list[dict[str, str]] = []
    kosdaq150_index_code = "2203"

    for date in quarter_dates:
        print(f"  constituent snapshot {date}")
        snapshot = stock.get_index_portfolio_deposit_file(kosdaq150_index_code, date)
        if not snapshot:
            print(f"    no snapshot rows for {date}; skipping")
            continue
        for ticker in snapshot:
            tickers.add(ticker)
            ticker_to_names[ticker] = stock.get_market_ticker_name(ticker)
            membership_rows.append({"snapshot_date": date, "종목코드": ticker})
        time.sleep(0.25)

    if not tickers:
        raise RuntimeError("KOSDAQ150 constituent collection returned no tickers")

    print(f"  unique KOSDAQ150 tickers: {len(tickers):,}")
    frames: list[pd.DataFrame] = []
    membership_by_snapshot = build_membership_by_snapshot(membership_rows)
    for index, ticker in enumerate(sorted(tickers), start=1):
        print(f"  [{index}/{len(tickers)}] daily OHLCV {ticker} {ticker_to_names.get(ticker, '')}")
        ohlcv = stock.get_market_ohlcv_by_date("20100101", "20261231", ticker)
        if ohlcv.empty:
            print(f"    no OHLCV rows for {ticker}; skipping")
            continue
        data = ohlcv.reset_index().rename(
            columns={
                "날짜": "날짜",
                "시가": "시가",
                "고가": "고가",
                "저가": "저가",
                "종가": "종가",
                "거래량": "거래량",
                "거래대금": "거래대금",
                "등락률": "Change",
            }
        )
        data["날짜"] = pd.to_datetime(data["날짜"]).dt.strftime("%Y-%m-%d")
        data.insert(1, "종목코드", ticker)
        data.insert(2, "종목명", ticker_to_names.get(ticker, ""))
        data["KRX종가"] = data["종가"]
        data["krx_close_source"] = "pykrx_ohlcv_close"
        data["KOSDAQ150분기스냅샷포함"] = data["날짜"].map(
            lambda value: ticker in membership_for_date(value, membership_by_snapshot)
        )
        frames.append(data)
        time.sleep(0.25)

    if not frames:
        raise RuntimeError("KOSDAQ150 OHLCV collection returned no rows")

    panel = pd.concat(frames, ignore_index=True).sort_values(["날짜", "종목코드"])
    panel.to_csv(output_path, index=False)
    print(f"  wrote {len(panel):,} rows -> {output_path.relative_to(ROOT)}")


def quarter_end_dates(start: str, end: str) -> list[str]:
    dates = pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq="QE")
    return [date.strftime("%Y%m%d") for date in dates]


def build_membership_by_snapshot(rows: list[dict[str, str]]) -> dict[pd.Timestamp, set[str]]:
    result: dict[pd.Timestamp, set[str]] = {}
    for row in rows:
        snapshot_date = pd.Timestamp(row["snapshot_date"])
        result.setdefault(snapshot_date, set()).add(row["종목코드"])
    return result


def membership_for_date(date_text: str, membership_by_snapshot: dict[pd.Timestamp, set[str]]) -> set[str]:
    date = pd.Timestamp(date_text)
    eligible = [snapshot_date for snapshot_date in membership_by_snapshot if snapshot_date <= date]
    if not eligible:
        return set()
    return membership_by_snapshot[max(eligible)]


if __name__ == "__main__":
    sys.exit(main())
