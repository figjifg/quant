from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ops.nav_update import ROOT

T000_REALIZED = ROOT / "reports/experiments/T000_tax_engine_audit/realized_gain_by_year.csv"
T000_UNREALIZED = ROOT / "reports/experiments/T000_tax_engine_audit/unrealized_gain_by_year.csv"
T004_TAX = ROOT / "reports/experiments/T004_account_vehicle_study/tax_by_vehicle.csv"
OUTPUT_DIR = ROOT / "paper_trading/operations/tax_ledger"

ANNUAL_EXEMPTION_KRW = 2_500_000.0


def compute_tax_ledger(as_of_date: str | pd.Timestamp | None = None, output_path: str | Path | None = None) -> Path:
    """Create the current tax-utilization ledger from existing T-family outputs."""

    as_of = pd.Timestamp(as_of_date) if as_of_date else pd.Timestamp("today").normalize()
    tax_year = int(as_of.year)

    realized = pd.read_csv(T000_REALIZED)
    realized = realized.loc[(realized["scenario"] == "T000-C") & (realized["year"].le(tax_year))]

    unrealized = pd.read_csv(T000_UNREALIZED, parse_dates=["date"])
    unrealized = unrealized.loc[(unrealized["scenario"] == "T000-C") & (unrealized["date"].le(as_of))]
    latest_unrealized = unrealized.sort_values("date").groupby("scenario").tail(1)

    tax_by_vehicle = pd.read_csv(T004_TAX)
    tax_by_vehicle = tax_by_vehicle.loc[tax_by_vehicle["tax_year"].le(tax_year)]

    rows = []
    for _, row in realized.iterrows():
        used_exemption = min(max(row["us_etf_net_realized_gain_krw"], 0.0), ANNUAL_EXEMPTION_KRW)
        rows.append(
            {
                "as_of_date": as_of.strftime("%Y-%m-%d"),
                "tax_year": int(row["year"]),
                "sleeve": "V1_overseas_etf_direct",
                "realized_gain_loss_krw": row["us_etf_net_realized_gain_krw"],
                "unrealized_gain_loss_krw": latest_unrealized["us_etf_unrealized_gain_krw"].iloc[0]
                if int(row["year"]) == tax_year and not latest_unrealized.empty
                else pd.NA,
                "used_annual_exemption_krw": used_exemption,
                "remaining_annual_exemption_krw": ANNUAL_EXEMPTION_KRW - used_exemption,
                "estimated_capital_gains_tax_krw": max(row["us_etf_net_realized_gain_krw"] - ANNUAL_EXEMPTION_KRW, 0.0) * 0.22,
                "dividend_withholding_krw": pd.NA,
                "vehicle_specific_tax_krw": pd.NA,
                "tax_professional_check_required": True,
            }
        )

    vehicle_summary = tax_by_vehicle.groupby(["vehicle", "label"], as_index=False)[
        [
            "capital_gains_tax_krw",
            "dividend_withholding_krw",
            "domestic_distribution_tax_krw",
            "isa_separate_tax_krw",
            "pension_tax_credit_krw",
            "total_tax_or_credit_krw",
        ]
    ].sum()
    for _, row in vehicle_summary.iterrows():
        rows.append(
            {
                "as_of_date": as_of.strftime("%Y-%m-%d"),
                "tax_year": f"through_{tax_year}",
                "sleeve": row["vehicle"],
                "realized_gain_loss_krw": pd.NA,
                "unrealized_gain_loss_krw": pd.NA,
                "used_annual_exemption_krw": pd.NA,
                "remaining_annual_exemption_krw": pd.NA,
                "estimated_capital_gains_tax_krw": row["capital_gains_tax_krw"],
                "dividend_withholding_krw": row["dividend_withholding_krw"],
                "vehicle_specific_tax_krw": row["total_tax_or_credit_krw"],
                "tax_professional_check_required": True,
            }
        )

    output = pd.DataFrame(rows)
    path = Path(output_path) if output_path else OUTPUT_DIR / f"tax_ledger_{as_of:%Y-%m-%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    print(compute_tax_ledger("2026-05-18").relative_to(ROOT))
