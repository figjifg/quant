from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.audit.q000_us_fundamental_data_audit import (
    CONCEPT_ALIASES,
    DATA_DIR,
    ROOT,
    analyze_ticker,
    coverage_summary,
    load_facts,
    write_audit_outputs,
    write_csv,
)


REPORT_DIR = ROOT / "reports" / "experiments" / "Q001_universe_construction"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
DEFAULT_USER_AGENT = "claude-code-q001 <q001@example.com>"

Q001_TICKERS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "META",
    "NVDA",
    "BRK-B",
    "TSLA",
    "JPM",
    "V",
    "MA",
    "PG",
    "JNJ",
    "HD",
    "UNH",
    "BAC",
    "XOM",
    "CVX",
    "KO",
    "PEP",
    "ABBV",
    "MRK",
    "PFE",
    "COST",
    "AVGO",
    "WMT",
    "LLY",
    "ORCL",
    "ADBE",
    "CRM",
    "NFLX",
    "CSCO",
    "INTC",
    "AMD",
    "QCOM",
    "TXN",
    "IBM",
    "GE",
    "BA",
    "CAT",
    "DE",
    "RTX",
    "LMT",
    "GS",
    "MS",
    "C",
    "WFC",
    "AXP",
    "BLK",
    "SPGI",
    "BX",
    "MMC",
    "PYPL",
    "INTU",
    "NOW",
    "ABT",
    "TMO",
    "AMGN",
    "MDT",
    "BMY",
    "GILD",
    "CI",
    "ELV",
    "DHR",
    "SYK",
    "ZTS",
    "ISRG",
    "REGN",
    "VRTX",
    "BIIB",
    "MU",
    "KLAC",
    "LRCX",
    "AMAT",
    "ASML",
    "NKE",
    "SBUX",
    "MCD",
    "DIS",
    "T",
    "VZ",
    "CMCSA",
    "TMUS",
    "CHTR",
    "F",
    "GM",
    "UPS",
    "FDX",
    "UNP",
    "LIN",
    "DOW",
    "APD",
    "FCX",
    "NEM",
    "GOLD",
    "NEE",
    "DUK",
    "SO",
    "AEP",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Q001 current large-cap SEC companyfacts universe audit.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--sleep-seconds", type=float, default=0.15)
    parser.add_argument("--tickers", nargs="*", default=Q001_TICKERS)
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    run_q001(
        data_dir=args.data_dir,
        report_dir=args.report_dir,
        tickers=args.tickers,
        user_agent=args.user_agent,
        sleep_seconds=args.sleep_seconds,
        download=not args.no_download,
    )
    return 0


def run_q001(
    data_dir: Path,
    report_dir: Path,
    tickers: list[str],
    user_agent: str,
    sleep_seconds: float,
    download: bool,
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    ticker_map = load_ticker_map(data_dir)

    universe_rows = []
    analyses = []
    sector_rows = []
    for index, ticker in enumerate(tickers, start=1):
        cik = ticker_map.get(ticker)
        row = {
            "ticker": ticker,
            "cik": str(cik).zfill(10) if cik is not None else "",
            "download_status": "missing_cik",
            "facts_path": "",
            "entity_name": "",
            "us_gaap_concept_count": "",
            "earliest_filing": "",
            "latest_filing": "",
            "sector": "unknown",
            "sic": "",
        }
        print(f"[{index}/{len(tickers)}] {ticker}")
        if cik is None:
            universe_rows.append(row)
            continue

        facts_path = data_dir / f"{ticker}_facts.json"
        row["facts_path"] = str(facts_path.relative_to(ROOT))
        if facts_path.exists():
            row["download_status"] = "existing"
        elif download:
            try:
                facts = fetch_json(SEC_COMPANYFACTS_URL.format(cik=cik), user_agent)
                facts_path.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                row["download_status"] = "downloaded"
                time.sleep(sleep_seconds)
            except Exception as exc:  # noqa: BLE001
                row["download_status"] = f"failed: {exc}"
                universe_rows.append(row)
                time.sleep(sleep_seconds)
                continue
        else:
            row["download_status"] = "not_downloaded"
            universe_rows.append(row)
            continue

        try:
            analysis = analyze_ticker(ticker, load_facts(data_dir, ticker))
            analyses.append(analysis)
            row["entity_name"] = analysis["entity_name"]
            row["us_gaap_concept_count"] = analysis["us_gaap_concept_count"]
            row["earliest_filing"] = analysis["earliest_filing"]
            row["latest_filing"] = analysis["latest_filing"]
        except Exception as exc:  # noqa: BLE001
            row["download_status"] = f"audit_failed: {exc}"

        try:
            sector = fetch_sector(cik, user_agent)
            row.update(sector)
            time.sleep(sleep_seconds)
        except Exception as exc:  # noqa: BLE001
            row["sector"] = f"unknown: {exc}"
            time.sleep(sleep_seconds)

        universe_rows.append(row)
        sector_rows.append({"ticker": ticker, "sector": row["sector"], "sic": row["sic"]})

    write_csv(
        report_dir / "universe_list.csv",
        [
            "ticker",
            "cik",
            "download_status",
            "facts_path",
            "entity_name",
            "us_gaap_concept_count",
            "earliest_filing",
            "latest_filing",
            "sector",
            "sic",
        ],
        universe_rows,
    )
    if analyses:
        write_audit_outputs(report_dir, analyses)
    else:
        write_csv(report_dir / "coverage_matrix.csv", ["ticker"], [])
        write_csv(report_dir / "pit_lag_distribution.csv", ["ticker"], [])
        write_csv(report_dir / "concept_aliases_used.csv", ["ticker"], [])

    write_sector_distribution(report_dir / "sector_distribution.csv", sector_rows)
    write_q001_report(report_dir, tickers, universe_rows, analyses)


def load_ticker_map(data_dir: Path) -> dict[str, int]:
    company_tickers_path = data_dir / "company_tickers.json"
    if not company_tickers_path.exists():
        raise FileNotFoundError(f"Missing SEC company_tickers map: {company_tickers_path}")
    company_tickers = json.loads(company_tickers_path.read_text(encoding="utf-8"))
    ticker_map = {
        str(item["ticker"]).upper(): int(item["cik_str"])
        for item in company_tickers.values()
        if item.get("ticker") and item.get("cik_str")
    }
    cik_map_path = data_dir / "cik_map.json"
    if cik_map_path.exists():
        ticker_map.update(
            {
                str(ticker).upper(): int(cik)
                for ticker, cik in json.loads(cik_map_path.read_text(encoding="utf-8")).items()
            }
        )
    return ticker_map


def fetch_json(url: str, user_agent: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
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


def fetch_sector(cik: int, user_agent: str) -> dict[str, str]:
    submissions = fetch_json(SEC_SUBMISSIONS_URL.format(cik=cik), user_agent)
    return {
        "sector": submissions.get("sicDescription") or "unknown",
        "sic": str(submissions.get("sic") or ""),
    }


def write_sector_distribution(path: Path, sector_rows: list[dict[str, str]]) -> None:
    counts: dict[tuple[str, str], int] = {}
    for row in sector_rows:
        key = (row.get("sector", "unknown"), row.get("sic", ""))
        counts[key] = counts.get(key, 0) + 1
    rows = [
        {"sector": sector, "sic": sic, "ticker_count": count}
        for (sector, sic), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0]))
    ]
    write_csv(path, ["sector", "sic", "ticker_count"], rows)


def write_q001_report(
    report_dir: Path,
    requested_tickers: list[str],
    universe_rows: list[dict[str, Any]],
    analyses: list[dict[str, Any]],
) -> None:
    completed = [row for row in universe_rows if row["download_status"] in {"existing", "downloaded"}]
    failures = [row for row in universe_rows if row["download_status"] not in {"existing", "downloaded"}]
    summary = coverage_summary(analyses) if analyses else {
        "by_concept": {concept: 0 for concept in CONCEPT_ALIASES},
        "covered_cells": 0,
        "total_cells": 0,
        "coverage_rate": 0.0,
        "non_dividend_covered_cells": 0,
        "non_dividend_total_cells": 0,
        "non_dividend_coverage_rate": 0.0,
        "concepts_at_95pct": 0,
    }
    concept_lines = "\n".join(
        f"| {concept} | {covered}/{len(analyses)} | {(covered / len(analyses) if analyses else 0):.1%} |"
        for concept, covered in summary["by_concept"].items()
    )
    failure_lines = "\n".join(
        f"- {row['ticker']}: {row['download_status']}" for row in failures[:20]
    ) or "- 없음"
    earliest = min((item["earliest_filing"] for item in analyses if item["earliest_filing"]), default="")
    latest = max((item["latest_filing"] for item in analyses if item["latest_filing"]), default="")
    completion_rate = len(completed) / len(requested_tickers) if requested_tickers else 0.0
    verdict = "OK" if completion_rate >= 0.90 and summary["coverage_rate"] >= 0.90 else "NEEDS_REVIEW"

    report = f"""# Q001 Universe Construction

## Verdict

{verdict}. 현재 large-cap 후보 universe 기준으로 SEC `companyfacts` 다운로드를 시도했고, 확보된 파일에 대해서만 coverage audit을 완료했다. 이 universe는 현재 ticker 목록 기반이므로 survivorship-free universe가 아니며 historical backtest universe로 직접 사용하면 안 된다.

## 핵심 결과

- 요청 ticker 수: {len(requested_tickers)}
- companyfacts 확보 ticker 수: {len(completed)}
- companyfacts 확보율: {completion_rate:.1%}
- audit 성공 ticker 수: {len(analyses)}
- non-dividend 14개 concept coverage: {summary["non_dividend_covered_cells"]}/{summary["non_dividend_total_cells"]} ({summary["non_dividend_coverage_rate"]:.1%})
- Dividends 포함 전체 15개 concept coverage: {summary["covered_cells"]}/{summary["total_cells"]} ({summary["coverage_rate"]:.1%})
- 95% 이상 coverage concept 수: {summary["concepts_at_95pct"]}/15
- filing date 범위: {earliest} ~ {latest}
- sector 분포는 SEC submissions `sicDescription` 기준이며, 시가총액 분포는 가격/주식수 PIT 원천이 없어 이번 산출물에서 제외했다.

## Coverage

| Concept | Covered | Coverage |
| --- | ---: | ---: |
{concept_lines}

## 실패 및 제외

{failure_lines}

## 한계

- 현재 S&P 100 유사 ticker list 기반이므로 survivorship bias가 있다. Q-family historical backtest에는 별도 survivorship-free membership, delisting, ticker-change 처리가 필요하다.
- Financial statement fact는 반드시 SEC `filed` 날짜 이후에만 feature로 노출해야 한다. `period_end` 기준 사용은 look-ahead다.
- 이 작업은 universe/data feasibility audit이며 factor grid search나 성과 해석을 수행하지 않았다.

## 다음 단계

Q002 Quality only로 진행 가능하다. 단, Q002도 현재 universe 한계를 report metadata에 명시하고, historical survivorship-free universe가 완성되기 전에는 production/promotion 판단에 쓰지 않는다.

## 산출물

- `universe_list.csv`
- `coverage_matrix.csv`
- `sector_distribution.csv`
- `pit_lag_distribution.csv`
- `concept_aliases_used.csv`
"""
    (report_dir / "report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
