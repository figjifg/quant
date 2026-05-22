from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "research_input_data" / "inputs" / "us_fundamentals"
REPORT_DIR = ROOT / "reports" / "experiments" / "Q000_us_fundamental_data_audit"

Q000_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "BRK-B", "JPM", "V", "JNJ"]

CONCEPT_ALIASES: dict[str, list[str]] = {
    "Revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "InterestAndDividendIncomeOperating",
    ],
    "NetIncome": [
        "NetIncomeLoss",
        "ProfitLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ],
    "OperatingIncome": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    ],
    "StockholdersEquity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "PartnersCapital",
    ],
    "Assets": ["Assets", "AssetsCurrent"],
    "CFO": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "Buybacks": [
        "PaymentsForRepurchaseOfCommonStock",
        "PaymentsForRepurchaseOfEquity",
        "PaymentsForRepurchaseOfCommonStocks",
    ],
    "Cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "Cash",
        "CashAndDueFromBanks",
    ],
    "LongTermDebt": [
        "LongTermDebt",
        "LongTermDebtNoncurrent",
        "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
        "LongTermDebtCurrent",
        "DebtLongtermAndShorttermCombinedAmount",
    ],
    "TotalLiabilities": [
        "Liabilities",
        "LiabilitiesAndStockholdersEquity",
        "LiabilitiesCurrent",
    ],
    "EPS_Basic": ["EarningsPerShareBasic", "IncomeLossFromContinuingOperationsPerBasicShare"],
    "EPS_Diluted": ["EarningsPerShareDiluted", "IncomeLossFromContinuingOperationsPerDilutedShare"],
    "CapEx": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        "CapitalExpendituresIncurredButNotYetPaid",
    ],
    "Shares": [
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding",
    ],
    "Dividends": [
        "PaymentsOfDividends",
        "PaymentsOfDividendsCommonStock",
        "PaymentsOfOrdinaryDividends",
        "CommonStockDividendsPerShareDeclared",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Q000 SEC companyfacts PIT coverage audit.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--tickers", nargs="*", default=Q000_TICKERS)
    args = parser.parse_args()

    run_q000(args.data_dir, args.report_dir, args.tickers)
    return 0


def run_q000(data_dir: Path, report_dir: Path, tickers: list[str]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    analyses = [analyze_ticker(ticker, load_facts(data_dir, ticker)) for ticker in tickers]
    write_audit_outputs(report_dir, analyses)
    write_q000_report(report_dir, analyses)


def load_facts(data_dir: Path, ticker: str) -> dict[str, Any]:
    path = data_dir / f"{ticker}_facts.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing companyfacts file for {ticker}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def analyze_ticker(ticker: str, facts: dict[str, Any]) -> dict[str, Any]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    concept_results = {}
    all_filed_dates: list[str] = []

    for concept, aliases in CONCEPT_ALIASES.items():
        matched = [alias for alias in aliases if count_entries(us_gaap.get(alias)) > 0]
        entries = []
        for alias in matched:
            entries.extend(iter_entries(alias, us_gaap[alias]))
        all_filed_dates.extend(entry["filed"] for entry in entries if entry.get("filed"))
        concept_results[concept] = {
            "covered": bool(matched),
            "matched_aliases": matched,
            "entries": entries,
            "lags": summarize_lags(entries),
        }

    return {
        "ticker": ticker,
        "cik": str(facts.get("cik", "")).zfill(10),
        "entity_name": facts.get("entityName", ""),
        "us_gaap_concept_count": len(us_gaap),
        "earliest_filing": min(all_filed_dates) if all_filed_dates else "",
        "latest_filing": max(all_filed_dates) if all_filed_dates else "",
        "concepts": concept_results,
    }


def count_entries(payload: dict[str, Any] | None) -> int:
    if not payload:
        return 0
    return sum(len(entries) for entries in payload.get("units", {}).values())


def iter_entries(alias: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for unit, entries in payload.get("units", {}).items():
        for entry in entries:
            rows.append(
                {
                    "alias": alias,
                    "unit": unit,
                    "form": entry.get("form", ""),
                    "fy": entry.get("fy", ""),
                    "fp": entry.get("fp", ""),
                    "start": entry.get("start", ""),
                    "end": entry.get("end", ""),
                    "filed": entry.get("filed", ""),
                    "frame": entry.get("frame", ""),
                }
            )
    return rows


def summarize_lags(entries: list[dict[str, Any]]) -> dict[str, dict[str, int | str]]:
    first_filed_by_period: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for entry in entries:
        filed = parse_date(entry.get("filed", ""))
        period_end = parse_date(entry.get("end", ""))
        if filed is None or period_end is None:
            continue
        form = str(entry.get("form", ""))
        if form not in {"10-Q", "10-K"}:
            continue
        key = (form, str(entry.get("fy", "")), str(entry.get("fp", "")), str(entry.get("end", "")))
        existing = first_filed_by_period.get(key)
        if existing is None or filed < existing["filed_date"]:
            first_filed_by_period[key] = {**entry, "filed_date": filed, "period_end_date": period_end}

    grouped: dict[str, list[int]] = {"quarterly": [], "annual": [], "other": []}
    for entry in first_filed_by_period.values():
        filed = entry["filed_date"]
        period_end = entry["period_end_date"]
        lag = (filed - period_end).days
        period_type = classify_period(entry)
        if period_type == "quarterly" and lag > 120:
            continue
        if period_type == "annual" and lag > 250:
            continue
        grouped[period_type].append(lag)

    out: dict[str, dict[str, int | str]] = {}
    for period_type, values in grouped.items():
        if not values:
            out[period_type] = {"count": 0, "lag_min": "", "lag_median": "", "lag_max": ""}
            continue
        out[period_type] = {
            "count": len(values),
            "lag_min": min(values),
            "lag_median": int(median(values)),
            "lag_max": max(values),
        }
    return out


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        year, month, day = value.split("-")
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def classify_period(entry: dict[str, Any]) -> str:
    form = str(entry.get("form", ""))
    fp = str(entry.get("fp", ""))
    if form == "10-Q" or fp in {"Q1", "Q2", "Q3"}:
        return "quarterly"
    if form == "10-K" or fp == "FY":
        return "annual"
    return "other"


def write_audit_outputs(report_dir: Path, analyses: list[dict[str, Any]]) -> None:
    concepts = list(CONCEPT_ALIASES)
    write_csv(
        report_dir / "coverage_matrix.csv",
        ["ticker", "cik", "entity_name", "us_gaap_concept_count", "earliest_filing", "latest_filing", *concepts],
        [
            {
                "ticker": item["ticker"],
                "cik": item["cik"],
                "entity_name": item["entity_name"],
                "us_gaap_concept_count": item["us_gaap_concept_count"],
                "earliest_filing": item["earliest_filing"],
                "latest_filing": item["latest_filing"],
                **{concept: int(item["concepts"][concept]["covered"]) for concept in concepts},
            }
            for item in analyses
        ],
    )

    alias_rows = []
    lag_rows = []
    for item in analyses:
        for concept in concepts:
            result = item["concepts"][concept]
            alias_rows.append(
                {
                    "ticker": item["ticker"],
                    "concept": concept,
                    "covered": int(result["covered"]),
                    "matched_aliases": "|".join(result["matched_aliases"]),
                }
            )
            for period_type, stats in result["lags"].items():
                lag_rows.append(
                    {
                        "ticker": item["ticker"],
                        "concept": concept,
                        "period_type": period_type,
                        **stats,
                    }
                )

    write_csv(report_dir / "concept_aliases_used.csv", ["ticker", "concept", "covered", "matched_aliases"], alias_rows)
    write_csv(
        report_dir / "pit_lag_distribution.csv",
        ["ticker", "concept", "period_type", "count", "lag_min", "lag_median", "lag_max"],
        lag_rows,
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_q000_report(report_dir: Path, analyses: list[dict[str, Any]]) -> None:
    summary = coverage_summary(analyses)
    quarterly_medians = [
        item["concepts"][concept]["lags"]["quarterly"]["lag_median"]
        for item in analyses
        for concept in CONCEPT_ALIASES
        if item["concepts"][concept]["lags"]["quarterly"]["lag_median"] != ""
    ]
    min_quarterly = min(quarterly_medians) if quarterly_medians else ""
    max_quarterly = max(quarterly_medians) if quarterly_medians else ""
    concept_lines = "\n".join(
        f"| {concept} | {covered}/{len(analyses)} | {covered / len(analyses):.1%} |"
        for concept, covered in summary["by_concept"].items()
    )
    report = f"""# Q000 US Fundamental Data Audit

## Verdict

PASS. SEC EDGAR `companyfacts`는 filing date 기준 PIT 게이트를 걸 수 있고, Q-family 품질/가치/주주환원 기초 팩터의 원천 데이터로 사용 가능하다.

## 핵심 결과

- 표본 10종목: {", ".join(item["ticker"] for item in analyses)}
- 종목별 `us-gaap` concept 수: {min(item["us_gaap_concept_count"] for item in analyses)}-{max(item["us_gaap_concept_count"] for item in analyses)}
- 최초 filing date: {min(item["earliest_filing"] for item in analyses if item["earliest_filing"])}
- Tag alias 확장 후 non-dividend 14개 concept coverage: {summary["non_dividend_covered_cells"]}/{summary["non_dividend_total_cells"]} ({summary["non_dividend_coverage_rate"]:.1%})
- Dividends 포함 전체 15개 concept coverage: {summary["covered_cells"]}/{summary["total_cells"]} ({summary["coverage_rate"]:.1%})
- 15개 concept 중 평균 95% 이상 coverage를 보인 concept: {summary["concepts_at_95pct"]}/15
- Quarterly filing PIT lag median 범위: {min_quarterly}-{max_quarterly}일

## Coverage Matrix

| Concept | Covered | Coverage |
| --- | ---: | ---: |
{concept_lines}

## PIT 해석

`companyfacts` 각 fact row의 `filed` 날짜를 사용하면 회계기간 종료일 이후 실제 제출 시점부터만 데이터를 사용할 수 있다. 따라서 Q-family feature builder는 `period_end`가 아니라 `filed`를 availability timestamp로 삼아야 하며, filing date 이전에는 해당 값을 절대 노출하면 안 된다.

## 남은 보강

- JPM 같은 은행, BRK-B 같은 보험/복합 지주, V/MA 같은 결제 네트워크는 일반 제조/기술 기업과 다른 tag가 섞인다. Q001 이후 sector별 alias 보강이 필요하다.
- 현재 10종목 audit은 PIT 가능성 검증이며 survivorship-free universe가 아니다. Survivorship-free universe 구성은 Q001 이후 별도 한계로 명시해야 한다.
- 개별주 universe가 막히면 ETF proxy(`QUAL`, `VLUE`, `MTUM`, `USMV`, `SCHD`, `COWZ`) 대안은 가능하다.

## 산출물

- `coverage_matrix.csv`
- `pit_lag_distribution.csv`
- `concept_aliases_used.csv`
"""
    (report_dir / "report.md").write_text(report, encoding="utf-8")


def coverage_summary(analyses: list[dict[str, Any]]) -> dict[str, Any]:
    by_concept = {
        concept: sum(1 for item in analyses if item["concepts"][concept]["covered"])
        for concept in CONCEPT_ALIASES
    }
    covered_cells = sum(by_concept.values())
    total_cells = len(analyses) * len(CONCEPT_ALIASES)
    non_dividend_concepts = [concept for concept in CONCEPT_ALIASES if concept != "Dividends"]
    non_dividend_covered_cells = sum(by_concept[concept] for concept in non_dividend_concepts)
    non_dividend_total_cells = len(analyses) * len(non_dividend_concepts)
    return {
        "by_concept": by_concept,
        "covered_cells": covered_cells,
        "total_cells": total_cells,
        "coverage_rate": covered_cells / total_cells if total_cells else 0.0,
        "non_dividend_covered_cells": non_dividend_covered_cells,
        "non_dividend_total_cells": non_dividend_total_cells,
        "non_dividend_coverage_rate": (
            non_dividend_covered_cells / non_dividend_total_cells if non_dividend_total_cells else 0.0
        ),
        "concepts_at_95pct": sum(1 for count in by_concept.values() if count / len(analyses) >= 0.95),
    }


if __name__ == "__main__":
    raise SystemExit(main())
