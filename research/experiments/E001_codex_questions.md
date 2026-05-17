# E001 Codex questions

E001 mapping was frozen in `configs/sector_mapping.yaml` before validation.
The generated outputs are present, but the preregistered validation criteria
do not all pass, so this needs user/Claude direction before any post-freeze
mapping change.

## 1. Coverage criterion fails because `KOGI(지배구조지수)` is forced to 기타

- Ticket rule says `KOGI(지배구조지수)` -> `99` 기타.
- In the snapshot, `035720` 카카오 has KIS 중분류 `KOGI(지배구조지수)` and KSIC
  `자료처리, 호스팅, 포털 및 기타 인터넷 정보매개서비스업`.
- Because KIS 중분류 has priority, 카카오 becomes `99` 기타 instead of KSIC
  fallback `08`.
- Worst quarter-end coverage is 2021Q2:
  - 종목수 coverage: 99.00%
  - 시총가중 coverage: 95.5748%
  - 기타 row: 카카오, 시총가중 4.4252%

Question: should KIS `KOGI(지배구조지수)` remain hard-coded to `99`, or should
index-like KIS labels use KSIC fallback when the row is an operating company?

## 2. Group average stock-count criterion fails for a top-100 universe

Average quarter-end stock counts by group include several groups below 10:

- `04` 철강금속: 4.06
- `07` 헬스케어: 6.11
- `09` 소비재/유통: 8.02
- `10` 음식료: 3.53
- `11` 에너지/유틸리티: 1.52
- `12` 건설/부동산: 3.36

Question: should criterion b be evaluated on the full 923-stock snapshot, or
is failure acceptable because quarter-end validation uses the dynamic top-100
universe?

## 3. Single-group dominance criterion fails structurally

Maximum quarter-end 시총가중 share is `01` 반도체/IT하드웨어 in 2026Q2:

- max weight: 60.0349%
- quarter-end date: 2026-05-06

This appears driven by Korean large-cap concentration, not by an unmapped
sector issue.

Question: should criterion c remain a hard pass/fail gate for this universe,
or should it be reported as a concentration diagnostic?
