from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "research_input_data" / "inputs" / "us_fundamentals" / "sec_edgar_sample.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"


@dataclass(frozen=True)
class SampleCompany:
    ticker: str
    cik: int


SAMPLE_COMPANIES = [
    SampleCompany("AAPL", 320193),
    SampleCompany("MSFT", 789019),
    SampleCompany("GOOGL", 1652044),
    SampleCompany("AMZN", 1018724),
    SampleCompany("META", 1326801),
    SampleCompany("NVDA", 1045810),
    SampleCompany("BRK.B", 1067983),
    SampleCompany("JPM", 19617),
    SampleCompany("V", 1403161),
    SampleCompany("JNJ", 200406),
]

CORE_TAGS = {
    "roic_candidates": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "StockholdersEquity",
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
    ],
    "fcf_candidates": [
        "NetCashProvidedByUsedInOperatingActivities",
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "Revenues",
    ],
    "leverage_candidates": [
        "Assets",
        "Liabilities",
        "StockholdersEquity",
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
    ],
    "shareholder_yield_candidates": [
        "PaymentsOfDividends",
        "PaymentsForRepurchaseOfCommonStock",
        "CommonStocksIncludingAdditionalPaidInCapital",
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
    ],
    "earnings_yield_candidates": [
        "NetIncomeLoss",
        "EarningsPerShareDiluted",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Q000 host-only SEC EDGAR companyfacts PIT data audit."
    )
    parser.add_argument(
        "--user-agent",
        required=True,
        help="SEC-required User-Agent, for example 'name email@example.com'.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.15,
        help="Delay between SEC requests. Default stays below 10 req/sec.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output JSON path.",
    )
    args = parser.parse_args()

    print("Q000 SEC EDGAR audit started.")
    print("Network is required. Run this on the user host, not in the Codex sandbox.")
    print("This script only audits PIT feasibility; it does not run a backtest.")

    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, company in enumerate(SAMPLE_COMPANIES, start=1):
        print(f"[{index}/{len(SAMPLE_COMPANIES)}] {company.ticker} CIK {company.cik:010d}")
        try:
            facts = fetch_companyfacts(company.cik, args.user_agent)
        except Exception as exc:  # noqa: BLE001
            failures.append({"ticker": company.ticker, "error": str(exc)})
            print(f"  failed: {exc}")
            continue

        audit = audit_companyfacts(company, facts)
        results.append(audit)
        print(
            "  filings="
            f"{audit['filing_date_count']} "
            "tags_found="
            f"{audit['core_tag_summary']['total_found']}/"
            f"{audit['core_tag_summary']['total_checked']}"
        )
        time.sleep(args.sleep_seconds)

    payload = {
        "source": "SEC EDGAR companyfacts API",
        "endpoint_template": SEC_COMPANYFACTS_URL,
        "network_required": True,
        "point_in_time_gate": "Use fact filed dates; never use facts before filed.",
        "survivorship_gate": "Sample audit is not a universe. Q001 must solve delisted historical universe.",
        "sample_companies": [company.__dict__ for company in SAMPLE_COMPANIES],
        "core_tags": CORE_TAGS,
        "results": results,
        "failures": failures,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {args.output}")
    print("Next: record this generated file in research_input_data/docs/DATA_CATALOG.md.")
    return 0 if not failures else 1


def fetch_companyfacts(cik: int, user_agent: str) -> dict[str, Any]:
    request = urllib.request.Request(
        SEC_COMPANYFACTS_URL.format(cik=cik),
        headers={
            "User-Agent": user_agent,
            "Accept-Encoding": "identity",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"SEC HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"SEC request failed: {exc.reason}") from exc


def audit_companyfacts(company: SampleCompany, facts: dict[str, Any]) -> dict[str, Any]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    found_by_group: dict[str, list[str]] = {}
    missing_by_group: dict[str, list[str]] = {}
    filing_dates: set[str] = set()
    form_counts: dict[str, int] = {}

    for group, tags in CORE_TAGS.items():
        found: list[str] = []
        missing: list[str] = []
        for tag in tags:
            tag_payload = us_gaap.get(tag)
            if tag_payload is None:
                missing.append(tag)
                continue
            found.append(tag)
            for unit_entries in tag_payload.get("units", {}).values():
                for entry in unit_entries:
                    filed = entry.get("filed")
                    if filed:
                        filing_dates.add(filed)
                    form = entry.get("form")
                    if form:
                        form_counts[form] = form_counts.get(form, 0) + 1
        found_by_group[group] = found
        missing_by_group[group] = missing

    total_checked = sum(len(tags) for tags in CORE_TAGS.values())
    total_found = sum(len(tags) for tags in found_by_group.values())
    sample_facts = build_sample_fact_rows(us_gaap)

    return {
        "ticker": company.ticker,
        "cik": f"{company.cik:010d}",
        "entity_name": facts.get("entityName"),
        "filing_date_count": len(filing_dates),
        "first_filing_date": min(filing_dates) if filing_dates else None,
        "last_filing_date": max(filing_dates) if filing_dates else None,
        "form_counts": dict(sorted(form_counts.items())),
        "core_tag_summary": {
            "total_checked": total_checked,
            "total_found": total_found,
            "found_by_group": found_by_group,
            "missing_by_group": missing_by_group,
        },
        "sample_fact_rows": sample_facts,
    }


def build_sample_fact_rows(us_gaap: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    priority_tags = [
        "NetCashProvidedByUsedInOperatingActivities",
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForRepurchaseOfCommonStock",
        "PaymentsOfDividends",
        "CommonStockSharesOutstanding",
        "NetIncomeLoss",
    ]
    for tag in priority_tags:
        tag_payload = us_gaap.get(tag)
        if tag_payload is None:
            continue
        for unit, entries in tag_payload.get("units", {}).items():
            for entry in entries[-3:]:
                rows.append(
                    {
                        "tag": tag,
                        "unit": unit,
                        "fy": entry.get("fy"),
                        "fp": entry.get("fp"),
                        "form": entry.get("form"),
                        "filed": entry.get("filed"),
                        "end": entry.get("end"),
                        "frame": entry.get("frame"),
                        "value_present": "val" in entry,
                    }
                )
    return rows


if __name__ == "__main__":
    raise SystemExit(main())

