# Source Feasibility Report — Pre-2018 Executable Status

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0

## Candidate sources surveyed

| candidate | feasibility | notes |
|---|---|---|
| OPENDART `list.json` pblntfty=I 거래소공시 | **CONFIRMED FEASIBLE** | tested with bgn_de=20100101: returned status=000, 520 items for first 10 days |
| pykrx status / suspension endpoint | NOT FEASIBLE | no relevant API exposed by installed pykrx |
| KRX 정보데이터시스템 직접 scraping | NOT ATTEMPTED | would require dedicated HTTP scraping + manual licensing review |
| W001 v2 listing_status_events.csv | already in repo | covers 2018+ only (same source as S3) |
| W001 v2 listing_status_terminal.csv | already in repo | per-ticker terminal snapshot |
| Kiwoom 2010-2016 panel disappearance | NOT a status source | panel disappearance != suspension/delisting evidence |

## API access details

- Endpoint: `https://opendart.fss.or.kr/api/list.json`
- Query parameters: `crtfc_key` (from `.env`, not committed), `bgn_de`, `end_de`,
  `pblntf_ty=I`, `page_no`, `page_count`.
- Auth: OPENDART API key (stored in local `.env`, NOT committed to git).
- Rate limit per docs: 20,000 requests/day. Acquisition stays well within.
- Date range tested: 2010-01-01 → 2010-01-10 (10 days). Returned 520 items,
  52 pages — confirming pre-2018 data IS served.

## Acquisition strategy

- 3-month chunks (same as Round 4 S3 acquisition).
- 8 years × 4 quarters = 32 chunks for 2010-01-01 → 2017-12-31.
- `page_count=100` per page; iterate `page_no` until empty.
- 0.2s inter-chunk pause to avoid rate-limit triggers.

## Hard locks (preserved)

- No credential committed.
- No execution simulation.
- No strategy testing.
