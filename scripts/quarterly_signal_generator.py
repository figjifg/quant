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

KR_RATE_SOURCE = "FRED IR3TIB01KRM156N"
KR_RATE_CSV = ROOT / "research_input_data/inputs/macro_features/fred_kr_short_rate.csv"
KR_RATE_COLUMN = "IR3TIB01KRM156N"


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
    record.update(_regime_off_sleeve_fields(record["signal_date"]))
    path = write_signal_record(record, ROOT / args.output_root)
    print(path.relative_to(ROOT))
    print(record)


def _regime_off_sleeve_fields(signal_date: str) -> dict[str, object]:
    rates = pd.read_csv(KR_RATE_CSV, parse_dates=["observation_date"], na_values=["."])
    rates[KR_RATE_COLUMN] = pd.to_numeric(rates[KR_RATE_COLUMN], errors="coerce")
    rates = rates.dropna(subset=[KR_RATE_COLUMN]).sort_values("observation_date")
    asof = rates.loc[rates["observation_date"].le(pd.Timestamp(signal_date))]
    if asof.empty:
        estimated_quarter_carry = None
    else:
        annual_rate = float(asof.iloc[-1][KR_RATE_COLUMN]) / 100.0
        estimated_quarter_carry = (1.0 + annual_rate / 12.0) ** 3 - 1.0
    return {
        "regime_off_sleeve": "KR_short_rate_carry",
        "kr_rate_source": KR_RATE_SOURCE,
        "estimated_quarter_carry": estimated_quarter_carry,
    }


if __name__ == "__main__":
    main()
