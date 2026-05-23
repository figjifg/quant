# D3 Precision Tuning Delta (v2 → v3, with v1 baseline)

Date: 2026-05-23 15:07:06

## D3a extraction rates
| Field | v1 → v2 → **v3** |
|---|---|
| amount_krw | 5.6% → 27.8% → **36.1%** (v1→v2: +22.2pp, v2→v3: +8.3pp) |
| shares | 2.8% → 13.9% → **13.9%** (v1→v2: +11.1pp, v2→v3: +0.0pp) |
| event_date | 2.8% → 13.9% → **13.9%** (v1→v2: +11.1pp, v2→v3: +0.0pp) |
| effective_date | 2.8% → 2.8% → **2.8%** (v1→v2: +0.0pp, v2→v3: +0.0pp) |
| shares_before | 0.0% → 2.8% → **2.8%** (v1→v2: +2.8pp, v2→v3: +0.0pp) |
| shares_after | 0.0% → 0.0% → **0.0%** (v1→v2: +0.0pp, v2→v3: +0.0pp) |

## D3b extraction rates
| Field | v1 → v2 → **v3** |
|---|---|
| amount_krw | 0.0% → 23.5% → **23.5%** (v1→v2: +23.5pp, v2→v3: -0.0pp) |
| shares | 29.4% → 5.9% → **5.9%** (v1→v2: -23.5pp, v2→v3: +0.0pp) |
| conversion_price | 0.0% → 29.4% → **29.4%** (v1→v2: +29.4pp, v2→v3: -0.0pp) |
| event_date | 0.0% → 0.0% → **0.0%** (v1→v2: +0.0pp, v2→v3: +0.0pp) |
| effective_date | 0.0% → 5.9% → **5.9%** (v1→v2: +5.9pp, v2→v3: +0.0pp) |

## Confidence trend
- D3a mean: v1 0.037 → v2 0.157 → **v3 0.185**
- D3b mean: v1 0.147 → v2 0.147 → **v3 0.147**

## Manual review rate
- D3a: v1 100.0% → v2 100.0% → **v3 100.0%**
- D3b: v1 100.0% → v2 100.0% → **v3 100.0%**

## Correction linkage
- v3: corrections_total 27, linked 3, unlinked 24

## V3 tuning techniques applied
- ACODE-specific label inventory loaded from JSON (extracted from 104 XMLs)
- `&cr;` HTML entity normalized in cell text
- Number-prefix label tolerance ('1. 취득예정주식(주)' substring-matches '취득예정주식')
- D3b event_date keyword expanded: 발행결의일, 청구일, 전환청구일
- D3b shares keywords broadened to cover both v1 generic + v2 ACODE-specific labels
- effective_date kept separate from event_date (no rcept_date fallback per Referee)