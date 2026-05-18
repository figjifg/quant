from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.audit.paper_trading_protocol import build_signal_record, write_signal_record


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate one quarterly D013 paper-trading signal JSON.")
    parser.add_argument("--quarter", help="Quarter label such as 2026-Q2. Defaults to latest D013 quarter.")
    parser.add_argument("--d013-dir", default="reports/experiments/D013_d009_threshold_minus_0p2")
    parser.add_argument("--output-root", default="reports/experiments/P004_paper_trading_protocol")
    parser.add_argument("--refresh-d013", action="store_true", help="Run configs/backtests/d013.yaml before reading outputs.")
    args = parser.parse_args(argv)

    if args.refresh_d013:
        subprocess.run(
            [sys.executable, "-m", "src.run_experiment", "--config", "configs/backtests/d013.yaml"],
            cwd=ROOT,
            check=True,
        )

    d013_dir = ROOT / args.d013_dir
    quarterly = pd.read_csv(d013_dir / "quarterly_regime_log.csv", parse_dates=["signal_date"])
    signals = pd.read_csv(d013_dir / "signals.csv", parse_dates=["signal_date", "execution_date"])
    signals = signals.rename(columns={"ticker": "종목코드", "signal_value": "market_cap"})
    signals["rank"] = signals.groupby("signal_date")["market_cap"].rank(method="first", ascending=False).astype(int)

    record = build_signal_record(
        quarterly_regime=quarterly,
        candidates=signals,
        quarter=args.quarter,
        max_positions=5,
    )
    path = write_signal_record(record, ROOT / args.output_root)
    print(path.relative_to(ROOT))
    print(record)


if __name__ == "__main__":
    main()
