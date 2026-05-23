# KR-EXECUTABLE-STATUS-BACKLOG-001 — Source Requirement Register

Date: 2026-05-23
Verdict: **DATA BACKLOG** (P2) per Referee 2026-05-23.
Status: A0 NOT started. Awaiting acquisition of an authoritative executable-status source.

## Purpose

This register documents what we need before the KR executable-status (suspension / halt /
limit lock / surveillance / managed) coverage audit can begin.

This is **not** the A0 audit. It is the prerequisite source requirement list.

## What "executable status" must answer

For every (date, ticker) the audit must be able to determine:

1. Could the ticker be executed at all on that date (no full-day suspension)?
2. Was there an intraday halt? When? How long?
3. Was the close pinned to the upper or lower limit?
4. Was the ticker in 관리종목 / 투자주의 / 투자경고 / 투자위험 surveillance state?
5. Was the ticker in liquidation / 정리매매?

Panel presence alone does NOT answer any of these. A non-zero `거래량` row does not prove
"executable" — it only proves "non-zero observed trades occurred at some point in the day".

## Currently in-repo sources

| source | covers | gap |
|---|---|---|
| `data/processed/w001_v2/panel_with_tradable_state.csv` | `tradable_state` column (v1.x derivation) | `tradable_state = panel_absence` ≠ officially_delisted (TRAD_000001 critical defect); v2 wiring incomplete |
| `data/processed/w001_v2/listing_status_events.csv` | suspension / resumption / delisting / managed / surveillance events | filtered from DART pblntfty=I — coverage 53.1% of disappeared tickers per ACQUISITION_SUMMARY.md |
| `data/processed/w001_v2/listing_status_terminal.csv` | terminal_status per ticker | terminal only — not intraday halt / limit lock / surveillance state per day |
| `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv` | 10,774 status events filtered from DART | source = DART 거래소공시, not KRX official halt log |
| Equity panel `거래량 == 0` rows | observable proxy | NOT authoritative — panel may report zero volume for many reasons |
| Equity panel `거래대금추정 == 0` rows | observable proxy | same caveat |

Net gap: **no authoritative per-day per-ticker executable-status feed** in the repo.

## What an authoritative source would provide

The acquisition target must give:

- Per-day per-ticker tradability label: `tradable_no_event | intraday_halt | full_day_suspended | upper_limit | lower_limit | surveillance | managed | liquidation | delisted`.
- Halt windows (timestamps) for any intraday halt.
- Limit-lock decisions (upper / lower / both).
- Surveillance announcements with start_date / end_date.
- Verifiable provenance: each label record sourced from KRX or KOSCOM directly, not derived.

## Candidate sources to acquire (no commitment)

| candidate | endpoint / channel | notes |
|---|---|---|
| KRX 매매거래정지 종목 조회 | KRX 정보데이터시스템 매매거래정지 화면 | KRX official — needs official endpoint + per-day fetch |
| KRX 단일가매매 종목 조회 | KRX 정보데이터시스템 | for limit-lock state evaluation |
| KRX 관리종목·투자주의·투자경고·투자위험 | KRX 정보데이터시스템 | surveillance status |
| KOSCOM market microstructure feed | KOSCOM | intraday halt windows; commercial license |
| OPENDART pblntfty=I 거래소공시 | partial coverage already in S3 | supplement only; insufficient on its own per TRAD_000002 closure |

This is candidate-only. Acquisition requires Referee approval as a separate phase.

## Acquisition prerequisites

1. Referee verdict explicitly opening `KR-EXECUTABLE-STATUS-COVERAGE-A0-001` (currently
   NOT approved).
2. Defined scope: dates, markets, status taxonomy.
3. Provenance rule: each record stamped with `source_url`, `fetched_at`, `vendor_label`.
4. Hard-prohibition affirmation: acquisition must NOT add features, NOT run strategies,
   NOT estimate liquidity, NOT compute returns.

## Until acquired

- The audit `KR-EXECUTABLE-STATUS-COVERAGE-A0-001` MUST NOT start.
- Any "executable" claim based on panel presence or `거래량 > 0` alone is **rejected**.
- Any strategy that depends on tradability correctness remains CLOSED.
- This register is updated only when an official source is acquired or when scope changes
  via a fresh Referee verdict.

## Interaction with W001 v2 tradable_state

`tradable_state` in `panel_with_tradable_state.csv` is a v1.x derivation. It documents the
current best-effort label using panel + S3 events. Per TRAD_000001 (still CLOSED via S3
acquisition) the label remains an approximation:

- `panel_absence` does not mean officially delisted.
- `zero_volume` does not mean halted.
- `limit_lock` is inferred from price range, not from KRX official limit-lock log.

The current label is acceptable as a research filter under W001 v2 hard locks. It is
NOT acceptable as the basis for any execution-readiness claim.

## Cross references

- `../KR_FIELD_METADATA_CONTRACT_A0/field_metadata_contract.md` (tradable_state column
  spec)
- `../KR_OHLCV_UNIT_INVARIANT_A0/ohlcv_invariant_summary.md` ("OHL=0 close>0" pattern
  finding — strong correlate of suspension but NOT proof)
- `../KR_LISTED_UNIVERSE_COVERAGE_BACKLOG/source_requirement_register.md` (sibling P2
  backlog)

## Hard locks

- This document is a **register only**; no audit conducted.
- Adding rows to this register does not constitute an A0 finding.
- Executable claims remain prohibited until acquisition + A0 audit complete.
- No production / paper / P08 / live readiness / shadow connection.
