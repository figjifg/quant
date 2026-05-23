# D3a Manual-Audit-Driven Label Enumeration

Date: 2026-05-23 15:32:39
Origin: Referee S2-D3-Triage verdict (2026-05-23).

## Scope
- D3a base forms audited: 7
- Available samples in D1+D2 union (Referee target was 10/base-form; we have fewer):
  - `주요사항보고서(자기주식취득결정)`: **4** samples available (target 10)
  - `주요사항보고서(자기주식처분결정)`: **5** samples available (target 10)
  - `주식소각결정`: **5** samples available (target 10)
  - `주요사항보고서(자기주식취득신탁계약체결결정)`: **5** samples available (target 10)
  - `주요사항보고서(자기주식취득신탁계약해지결정)`: **5** samples available (target 10)
  - `자기주식취득결과보고서`: **5** samples available (target 10)
  - `자기주식처분결과보고서`: **6** samples available (target 10)

**Limitation**: This is a desk-audit using the existing 36-row D3a sample. A true manual audit with 10 samples per base form would require acquiring more disclosures of each form. The determinism scores below should be read as 'how deterministic is the label-keyword mapping ON THE CURRENT SAMPLE'.

## Determinism scoring
- `deterministic`: ≥70% sample hit rate AND ≤5 distinct label phrasings
- `partially_deterministic`: 40-70% hit rate
- `non_deterministic`: <40% hit rate

## Base form: `자기주식처분결과보고서` (n=6)

### Field: `amount_krw`
- hit_rate: 66.7% (4 / 6)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [4] `1주당처분가액`
- sample value extractions:
  - `20231212000273` → `처분가액총 액`
  - `20251110000246` → `처분가액총 액`
  - `20260206001091` → `처분가액총 액`

### Field: `shares`
- hit_rate: 66.7% (4 / 6)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [4] `처분수량`
- sample value extractions:
  - `20231212000273` → `금융투자업자`
  - `20251110000246` → `금융투자업자`
  - `20260206001091` → `금융투자업자`

### Field: `event_date`
- hit_rate: 66.7% (4 / 6)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [4] `일 자`
- sample value extractions:
  - `20231212000273` → `종 류 | 수 량 | 1주당처분가액 | 처분가액총 액 | 처분대상 | 매도위탁 증권회사`
  - `20251110000246` → `종 류 | 수 량 | 1주당처분가액 | 처분가액총 액 | 처분대상 | 매도위탁 증권회사`
  - `20260206001091` → `종 류 | 수 량 | 1주당처분가액 | 처분가액총 액 | 처분대상 | 매도위탁 증권회사`

### Field: `effective_date`
- hit_rate: 66.7% (4 / 6)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [4] `부터`
- sample value extractions:
  - `20231212000273` → `까지`
  - `20251110000246` → `까지`
  - `20260206001091` → `까지`

## Base form: `자기주식취득결과보고서` (n=5)

### Field: `amount_krw`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `1주당취득가액`
- sample value extractions:
  - `20240912000423` → `취득가액총 액`
  - `20250819000166` → `취득가액총 액`
  - `20250221002351` → `취득가액총 액`

### Field: `shares`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `취득수량`
- sample value extractions:
  - `20240912000423` → `금융투자업자`
  - `20250819000166` → `금융투자업자`
  - `20250221002351` → `금융투자업자`

### Field: `event_date`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `일 자`
- sample value extractions:
  - `20240912000423` → `종 류 | 수 량 | 1주당취득가액 | 취득가액총 액 | 매수위탁 증권회사`
  - `20250819000166` → `종 류 | 수 량 | 1주당취득가액 | 취득가액총 액 | 매수위탁 증권회사`
  - `20250221002351` → `종 류 | 수 량 | 1주당취득가액 | 취득가액총 액 | 매수위탁 증권회사`

### Field: `effective_date`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `부터`
- sample value extractions:
  - `20240912000423` → `까지`
  - `20250819000166` → `까지`
  - `20250221002351` → `까지`

## Base form: `주식소각결정` (n=5)

### Field: `amount_krw`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `4. 소각예정금액(원)`
- sample value extractions:
  - `20260209800783` → `750,889,405`
  - `20240719800161` → `4,393,104,470`
  - `20250304801003` → `1,508,500,000`

### Field: `shares`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `event_date`
- hit_rate: 80.0% (4 / 5)
- determinism: **deterministic**
- distinct label phrasings (top 1):
  - [4] `9. 이사회결의일(결정일)`
- sample value extractions:
  - `20260209800783` → `2026-02-09`
  - `20240719800161` → `2024-07-19`
  - `20250304801003` → `2025-03-04`

### Field: `effective_date`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

## Base form: `주요사항보고서(자기주식처분결정)` (n=5)

### Field: `amount_krw`
- hit_rate: 60.0% (3 / 5)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [3] `3. 처분예정금액(원)`
- sample value extractions:
  - `20240425800294` → `보통주식 | 279,874,700`
  - `20250625000494` → `보통주식`
  - `20241220000155` → `보통주식`

### Field: `shares`
- hit_rate: 60.0% (3 / 5)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [3] `1. 처분예정주식(주)`
- sample value extractions:
  - `20240425800294` → `보통주식 | 5,477`
  - `20250625000494` → `보통주식`
  - `20241220000155` → `보통주식`

### Field: `event_date`
- hit_rate: 20.0% (1 / 5)
- determinism: **non_deterministic**
- distinct label phrasings (top 1):
  - [1] `9. 처분결정일`
- sample value extractions:
  - `20240425800294` → `2024.04.25`

### Field: `effective_date`
- hit_rate: 60.0% (3 / 5)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [3] `4. 처분예정기간`
- sample value extractions:
  - `20240425800294` → `시작일 | 2024.04.26`
  - `20250625000494` → `시작일`
  - `20241220000155` → `시작일`

## Base form: `주요사항보고서(자기주식취득결정)` (n=4)

### Field: `amount_krw`
- hit_rate: 50.0% (2 / 4)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [2] `2. 취득예정금액(원)`
- sample value extractions:
  - `20240708000261` → `보통주식`
  - `20260305000671` → `보통주식`

### Field: `shares`
- hit_rate: 50.0% (2 / 4)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [2] `1. 취득예정주식(주)`
- sample value extractions:
  - `20240708000261` → `보통주식`
  - `20260305000671` → `보통주식`

### Field: `event_date`
- hit_rate: 0.0% (0 / 4)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `effective_date`
- hit_rate: 50.0% (2 / 4)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [2] `3. 취득예상기간`
- sample value extractions:
  - `20240708000261` → `시작일`
  - `20260305000671` → `시작일`

## Base form: `주요사항보고서(자기주식취득신탁계약체결결정)` (n=5)

### Field: `amount_krw`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `shares`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `event_date`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `effective_date`
- hit_rate: 20.0% (1 / 5)
- determinism: **non_deterministic**
- distinct label phrasings (top 1):
  - [1] `2. 계약기간`
- sample value extractions:
  - `20231124000433` → `시작일`

## Base form: `주요사항보고서(자기주식취득신탁계약해지결정)` (n=5)

### Field: `amount_krw`
- hit_rate: 60.0% (3 / 5)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [3] `1. 계약금액(원)`
- sample value extractions:
  - `20250131000515` → `해지 전`
  - `20230104000469` → `해지 전`
  - `20260220800948` → `해지 전 | 15,000,000,000`

### Field: `shares`
- hit_rate: 0.0% (0 / 5)
- determinism: **non_deterministic**
- distinct label phrasings: _none captured in current sample_

### Field: `event_date`
- hit_rate: 20.0% (1 / 5)
- determinism: **non_deterministic**
- distinct label phrasings (top 1):
  - [1] `8. 이사회결의일(결정일)`
- sample value extractions:
  - `20260220800948` → `-`

### Field: `effective_date`
- hit_rate: 60.0% (3 / 5)
- determinism: **partially_deterministic**
- distinct label phrasings (top 1):
  - [3] `2. 해지 전 계약기간`
- sample value extractions:
  - `20250131000515` → `시작일`
  - `20230104000469` → `시작일`
  - `20260220800948` → `시작일 | 2025년 08월 20일`

## Overall D3a label determinism summary

| Base form | # fields deterministic | # partial | # non-deterministic |
|---|---|---|---|
| 자기주식처분결과보고서 | 0 | 4 | 0 |
| 자기주식취득결과보고서 | 4 | 0 | 0 |
| 주식소각결정 | 2 | 0 | 2 |
| 주요사항보고서(자기주식처분결정) | 0 | 3 | 1 |
| 주요사항보고서(자기주식취득결정) | 0 | 3 | 1 |
| 주요사항보고서(자기주식취득신탁계약체결결정) | 0 | 0 | 4 |
| 주요사항보고서(자기주식취득신탁계약해지결정) | 0 | 2 | 2 |

## Verdict

- Labels are NOT consistently deterministic across base forms. Only 2 of 7 base forms have ≥2 deterministic target fields.
- Per Referee decision rule: 'If D3a labels remain ambiguous, lock D3a as PARTIAL.'
- Executor recommendation: lock D3a as PARTIAL.

## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready