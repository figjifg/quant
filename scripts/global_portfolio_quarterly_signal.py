from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_CSV = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
H001_EQUITY_CSV = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "paper_trading/signals"

PORTFOLIOS: dict[str, dict[str, float]] = {
    "P08_IEF30": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30},
    "P08": {"SPY": 0.40, "QQQ": 0.30, "H001": 0.20, "IEF": 0.10},
    "P07": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "P07_IEF30": {"QQQ": 0.40, "H001": 0.30, "IEF": 0.30},
    "QQQ_100": {"QQQ": 1.00},
    "SPY_100": {"SPY": 1.00},
    "QQQ_SPY_50_50": {"QQQ": 0.50, "SPY": 0.50},
    "H001": {"H001": 1.00},
    "IEF": {"IEF": 1.00},
}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate global allocation paper-tracking signal JSON.")
    parser.add_argument("--quarter", help="Quarter label such as 2026-Q2. Defaults from --as-of.")
    parser.add_argument("--as-of", help="Paper mark date. Defaults to latest available ETF date.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args(argv)

    as_of = pd.Timestamp(args.as_of) if args.as_of else latest_etf_date()
    quarter = args.quarter or f"{as_of.year}-Q{((as_of.month - 1) // 3) + 1}"
    usdk_rw = latest_usdkrw(as_of)

    record = {
        "quarter": quarter,
        "as_of_date": as_of.strftime("%Y-%m-%d"),
        "status": "paper_tracking_only",
        "cash_deployment_status": "not_authorized_paper_only",
        "rebalance_frequency": "quarterly",
        "candidate_status_note": "P08_IEF30 is an I004 formal candidate, not a production deployment.",
        "portfolios": PORTFOLIOS,
        "component_marks": build_component_marks(as_of, float(usdk_rw["value"])),
        "usdk_rw": usdk_rw,
        "trading_guide": {
            "mode": "paper_only_nav_tracking",
            "actual_cash_deployment": "do_not_trade",
            "method": "Track KRW NAV from target weights and component marks at each quarter point.",
            "decision_gate": "Review only after at least 4 quarters of paper NAV agreement.",
        },
    }

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"global_{quarter}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


def latest_etf_date() -> pd.Timestamp:
    dates = []
    for ticker in ("SPY", "QQQ", "IEF"):
        frame = pd.read_csv(ETF_DIR / f"yf_{ticker}.csv", parse_dates=["Date"])
        dates.append(frame["Date"].max())
    return max(dates)


def build_component_marks(as_of: pd.Timestamp, usdk_rw: float) -> dict[str, dict[str, object]]:
    marks = {}
    for ticker in ("SPY", "QQQ", "IEF"):
        row = latest_etf_row(ticker, as_of)
        marks[ticker] = {
            "source": f"research_input_data/inputs/global_etf/yf_{ticker}.csv",
            "date": row["Date"].strftime("%Y-%m-%d"),
            "close_usd": float(row["Close"]),
            "close_krw_estimate": float(row["Close"]) * usdk_rw,
        }

    h001 = pd.read_csv(H001_EQUITY_CSV, parse_dates=["date"])
    h001 = h001.loc[h001["date"].le(as_of)].dropna(subset=["net_value"]).sort_values("date")
    if h001.empty:
        raise ValueError(f"No H001 NAV available on or before {as_of.date()}.")
    h001_row = h001.iloc[-1]
    marks["H001"] = {
        "source": "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv",
        "date": h001_row["date"].strftime("%Y-%m-%d"),
        "net_value_krw_nav": float(h001_row["net_value"]),
    }
    return marks


def latest_etf_row(ticker: str, as_of: pd.Timestamp) -> pd.Series:
    frame = pd.read_csv(ETF_DIR / f"yf_{ticker}.csv", parse_dates=["Date"])
    frame = frame.loc[frame["Date"].le(as_of)].dropna(subset=["Close"]).sort_values("Date")
    if frame.empty:
        raise ValueError(f"No {ticker} price available on or before {as_of.date()}.")
    return frame.iloc[-1]


def latest_usdkrw(as_of: pd.Timestamp) -> dict[str, object]:
    rates = pd.read_csv(USDKRW_CSV, parse_dates=["observation_date"], na_values=["."])
    rates["DEXKOUS"] = pd.to_numeric(rates["DEXKOUS"], errors="coerce")
    rates = rates.loc[rates["observation_date"].le(as_of)].dropna(subset=["DEXKOUS"]).sort_values("observation_date")
    if rates.empty:
        raise ValueError(f"No USDKRW observation available on or before {as_of.date()}.")
    row = rates.iloc[-1]
    return {
        "source": "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv",
        "date": row["observation_date"].strftime("%Y-%m-%d"),
        "value": float(row["DEXKOUS"]),
        "note": "Latest local USDKRW observation on or before as_of_date; no network refresh was used.",
    }


if __name__ == "__main__":
    main()
