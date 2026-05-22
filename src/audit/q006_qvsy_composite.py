from __future__ import annotations

import argparse
from pathlib import Path

from src.audit.q002_quality_only import ETF_DIR, FUNDAMENTAL_DIR, PRICE_DIR, Q001_REPORT_DIR, ROOT
from src.audit.q003_value_only import build_comparison_report, run_q_family


REPORT_DIR = ROOT / "reports" / "experiments" / "Q006_qvsy_composite"


def main() -> int:
    parser = argparse.ArgumentParser(description="Q006 pre-registered US QVSY composite audit.")
    parser.add_argument("--fundamental-dir", type=Path, default=FUNDAMENTAL_DIR)
    parser.add_argument("--price-dir", type=Path, default=PRICE_DIR)
    parser.add_argument("--etf-dir", type=Path, default=ETF_DIR)
    parser.add_argument("--q001-report-dir", type=Path, default=Q001_REPORT_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--comparison", action="store_true", help="Write Q-family comparison after Q003-Q006 exist.")
    args = parser.parse_args()
    run_q_family("Q006", args.fundamental_dir, args.price_dir, args.etf_dir, args.q001_report_dir, args.report_dir)
    if args.comparison:
        build_comparison_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
