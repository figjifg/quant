# KR-LISTED-UNIVERSE-COVERAGE-BACKLOG-001 — Source Requirement Register

Date: 2026-05-23
Verdict: **DATA BACKLOG** (P2) per Referee 2026-05-23.
Status: A0 NOT started. Awaiting acquisition of an authoritative listed-universe source.

## Purpose

This register documents what we need before the KR listed-universe coverage audit can begin.
This is **not** the A0 audit. It is the prerequisite source requirement list.

## What "listed universe" must answer

For every (date, ticker) the audit must be able to determine:

1. Was the ticker listed on KOSPI / KOSDAQ on that date (under the symbol used)?
2. When did the ticker first list?
3. When did the ticker delist (if applicable)?
4. Were there any name / corp_code reassignments on the symbol?
5. Did the ticker undergo merger / split / consolidation that changed its identity?

A panel that contains rows for ticker T over a date range is **not** a substitute for the
above. Panel coverage reflects vendor selection rules — not actual KRX listing status.

## Currently in-repo sources

| source | covers | gap |
|---|---|---|
| 4 equity panels (panel.csv ×4) | vendor's selected universe per file | NOT a listed-universe source; biased by selection |
| `data/processed/w001_v2/permanent_id_master.csv` | krx_first_snapshot / krx_last_snapshot per ticker | derived from sample snapshots — not a continuous daily universe |
| `data/acquired/round4/s4_listed_companies/krx_ever_listed_table.csv` | KRX list via pykrx, 5 sample snapshots | sample-only; gaps between snapshots not resolved |
| `data/acquired/round4/s4_listed_companies/krx_listed_companies_master.csv` | per-snapshot rows | 5 snapshots = NOT daily universe |
| `data/processed/sector_membership_kis_snapshot_20260518.csv` | KIS latest snapshot | latest only — historical PIT not preserved |

Net gap: **no continuous daily KRX listed-universe table** in the repo.

## What an authoritative source would provide

The acquisition target must give:

- Daily granularity (`yyyy-mm-dd → set of listed tickers`).
- Per-ticker first listing date and (if applicable) delisting date.
- Per-ticker market segment (KOSPI / KOSDAQ / KONEX), with intra-life moves tracked.
- Corporate-action linkage when a ticker is reissued or merged.
- Verifiable provenance (a fetched-from-URL record, not a vendor-aggregated table).

## Candidate sources to acquire (no commitment)

| candidate | endpoint | notes |
|---|---|---|
| pykrx `get_business_days` + per-day `get_market_ticker_list` | pykrx; needs KRX_ID/KRX_PW (already in `.env`) | builds a daily universe by iterating trading days; may rate-limit on multi-year fetch |
| KRX `getJsonData.cmd` 상장종목 검색 | http://data.krx.co.kr/ | KRX official endpoint; needs careful per-day fetch + change-log normalisation |
| OPENDART `corpCode.xml` + linked filings | https://opendart.fss.or.kr/api/corpCode.xml | gives corp_code↔stock_code mapping; not directly a daily list but adds lifecycle context |
| DART-listed disclosures (already partially in S3) | `data/acquired/round4/s3_krx_status/` | covers 거래소공시 status events — supplements but does not replace daily universe |

This is candidate-only. Acquisition requires Referee approval as a separate phase.

## Acquisition prerequisites

1. Referee verdict explicitly opening `KR-LISTED-UNIVERSE-COVERAGE-A0-001` (currently NOT
   approved).
2. Defined scope: dates covered, markets included, identifier conventions (ticker vs
   permanent_id vs corp_code).
3. Defined provenance rule: each row must record the fetch URL + timestamp.
4. Hard-prohibition affirmation: acquisition must NOT add features, NOT run strategies,
   NOT estimate liquidity, NOT compute returns.

## Until acquired

- The audit `KR-LISTED-UNIVERSE-COVERAGE-A0-001` MUST NOT start.
- Any survivorship-safety claim based on panel-only data is **rejected**.
- Any strategy that depends on listed-universe correctness remains CLOSED.
- This register is updated only when an official source is acquired or when scope changes
  via a fresh Referee verdict.

## Cross references

- `../KR_FIELD_METADATA_CONTRACT_A0/field_metadata_contract.md` (W001 v2 universe schema)
- `../KR_CALENDAR_PANEL_ALIGN_A0/calendar_panel_alignment_summary.md` (panel-only union
  calendar = not authoritative)
- `../KR_EXECUTABLE_STATUS_BACKLOG/source_requirement_register.md` (sibling P2 backlog)

## Hard locks

- This document is a **register only**; no audit conducted.
- Adding rows to this register does not constitute an A0 finding.
- Survivorship-safe claims remain prohibited until acquisition + A0 audit complete.
