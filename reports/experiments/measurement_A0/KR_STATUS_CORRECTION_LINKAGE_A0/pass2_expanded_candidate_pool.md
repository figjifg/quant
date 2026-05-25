# Pass-2 Expanded Candidate Pool

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 2)

## Pools used in Pass 2

| pool | rows | source |
|---|---:|---|
| `filtered_status` | 17924 | combined `krx_status_events_*.csv` (pass-1 used this only) |
| `raw_pblntfty` | 726123 | combined `dart_pblntfty_I_all_*.csv` (pass-2 addition) |

Total raw + filtered: **744047**.

## What "raw_pblntfty" means

OPENDART `list.json?pblntfty=I` (거래소공시) raw responses. Includes all KRX
exchange disclosures — not just the suspension / resumption / delisting / managed /
liquidation events the filtered status pool retains. So the raw pool contains
e.g. 중요내용공시, 매매거래정지및정지해제, 풍문 또는 보도에 대한 해명, etc.

## Including cross-category originals

The Referee verdict explicitly permits using delisting / managed / other as
**candidate-original context only**. This does NOT authorise a delisting parser
or managed parser. No new event_category is parsed.

## Issuer keying

Per-correction issuer pre-filter:

- prefer `corp_code` match;
- else `stock_code_str` (6-digit, zero-padded);
- else normalized `corp_name` (suffixes `(주)` / `주식회사` removed, whitespace
  collapsed).

## What the expanded pool does NOT do

- Does NOT lower the bar on correction-row authority. Correction rows remain
  `manual_review_required = True`.
- Does NOT promote raw_pblntfty candidates to authoritative status.
- Does NOT enable strategy / execution / performance work.
