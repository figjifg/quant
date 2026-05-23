# D3 Precision Tuning Delta Report (v1 → v2)

Per Referee Option (b), this delta compares v1 first-pass parser to v2 precision-tuned parser using the same D1+D2 sample set.

## D3a extraction rates

| Field | v1 → v2 |
|---|---|
| amount_krw | 27.8% (v1 5.6%, delta +22.2pp) |
| shares | 13.9% (v1 2.8%, delta +11.1pp) |
| event_date | 13.9% (v1 2.8%, delta +11.1pp) |
| effective_date | 2.8% (v1 2.8%, delta +0.0pp) |
| shares_before | 2.8% (v1 0.0%, delta +2.8pp) |
| shares_after | 0.0% (v1 0.0%, delta +0.0pp) |

## D3b extraction rates

| Field | v1 → v2 |
|---|---|
| amount_krw | 23.5% (v1 0.0%, delta +23.5pp) |
| shares | 5.9% (v1 29.4%, delta -23.5pp) |
| conversion_price | 29.4% (v1 0.0%, delta +29.4pp) |
| event_date | 0.0% (v1 0.0%, delta +0.0pp) |
| effective_date | 5.9% (v1 0.0%, delta +5.9pp) |

## Confidence distribution
- D3a mean: v1 0.037 → v2 0.157
- D3b mean: v1 0.147 → v2 0.147

## Manual review rate
- D3a: v1 100.0% → v2 100.0%
- D3b: v1 100.0% → v2 100.0%

## Correction linkage
- corrections_total: 27 | linked: 3 | unlinked: 24

## Tuning techniques applied (v2)
- Multi-row label discovery (THEAD column headers + row headers + cell composition)
- Nested <TABLE> flatten via BeautifulSoup descendant walk
- COLSPAN / ROWSPAN expansion into 2D grid before label discovery
- Per-ACODE field keyword hints (using DART <DOCUMENT-NAME ACODE>) layered on top of generic fallback
- Expanded keyword lists from D2 schema example observations
- Flat-adjacency cell-pair fallback for simple tables

## Remaining failure modes
- HTML inline forms (D3a/D3b fallback path; D3c proper) still surface as manual_review
- ACODE-specific reset clauses (CB/BW) require body free-text parsing — manual flagged
- 자기주식취득결정 multi-row table with merged header/value cells still misses some fields without per-ACODE label enumeration tuned against actual XSD

## Next round candidates (if Referee approves further iteration)
1. Per-ACODE label enumeration against actual XSD specs (currently inferred from D2 sample only)
2. Manual audit on 30 samples per D3a/D3b base form to enumerate exact label phrasing
3. Targeted HTML inline parser (separate from XML branch)
4. Reset-clause body-text scanner for CB/BW conversion price adjustment

## Hard locks reaffirmed
- No strategy testing, no return outcome, no parser-strategy-ready claim