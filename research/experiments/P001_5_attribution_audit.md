# P001.5 — E014 PIT 실패 attribution audit (짧고 제한적)

## 상태
계획됨

## 이게 무슨 ticket 인가

P001 PIT 검증에서 E014 FAIL. 지피티 권장: E014 살리기 위한 재탐색 아닌
**실패 원인 정확히 기록**용 짧은 attribution.

**핵심 원칙**: 명백한 bug 발견 시 한 번만 fix + rerun. 발견 안 되면 close.
재최적화 금지.

## 4 분석 항목 (지피티 권장)

### A. Source decomposition
3 가지 carrier 비교:
1. **KIS snapshot** (현재 E014, +362%)
2. **KRX current snapshot** (KRX 2026-05 의 분류를 과거에 적용) — 새로 계산 필요
3. **KRX PIT** (P001 결과, +147%)

목적:
- KIS vs KRX current snapshot 차이 = source taxonomy 차이
- KRX current vs KRX PIT 차이 = 진짜 PIT membership 차이
- 어느 쪽이 더 큰 원인인지 분리

### B. High-impact ticker attribution
종목별 누적 기여도 분해:
- snapshot E014 보유 but PIT E014 미보유 종목
- PIT E014 보유 but snapshot E014 미보유 종목
- 두 전략 공통 보유

특히 확인:
- NAVER (035420), 카카오 (035720)
- 셀트리온 (068270)
- LG화학 (051910), LG에너지솔루션 (373220)
- POSCO홀딩스 (005490)
- 한화오션 (042660), HMM 등
- 삼성바이오 (207940), 엔씨소프트 (036570)

### C. High-impact sector mapping manual review
KRX 41 업종 → 12 그룹 매핑 중 성과 영향 큰 sector 만 검토:
- 인터넷/서비스/통신 그룹 (KRX 일반서비스, IT 서비스, 통신서비스 등)
- 반도체/IT 그룹
- 화학/2차전지 그룹
- 헬스케어/제약
- 조선/기계/지주
- 매핑 bug 있는지 (예: '일반서비스' 가 어디로 갔는지)

### D. PIT E014 의 sector score 진단
포트폴리오 metric 말고 진단값:
- PIT sector RS+Breadth Rank IC
- Top 4 vs Bottom 4 spread t-stat
- PIT selected vs unselected forward return

목적:
- 진단 좋고 portfolio 만 나쁨 → within-sector stock selection 문제
- 진단도 나쁨 → Layer 2 score 자체가 snapshot 산물

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| Source decomposition: KRX current = KIS 비슷, PIT 만 낮음 | **진짜 PIT bias**, E014 close |
| KRX current 이미 낮음 | taxonomy 차이가 큰 원인, mapping 재고 가치 있음 |
| 명백한 mapping bug 발견 | 한 번 fix + rerun, 결과 보고 close |
| 특정 종목 (예: 한화오션) 분류 명백히 잘못 | 그 종목 manual override, 한 번 rerun |
| 모두 정상 | E014 close, backlog 만 남김 |

## 산출물

- reports/experiments/P001_5_attribution_audit/
- A_source_decomposition.csv
- B_ticker_attribution.csv (snapshot vs PIT 종목 차이)
- C_mapping_review.md
- D_pit_score_diagnostics.csv
- report.md (종합 + close/fix 결정)

## 엄격 제약

- E014 재탐색 아님 — 실패 원인 기록만
- 명백한 bug 발견 시만 한 번 rerun (mapping fix)
- 새 Layer 2 carrier 만들지 말 것
- engine, 기존 strategy 미수정
- D001-D015, E003-E015, F002-F012, G000-G002, P001 byte-identical
- 시간 제한: 한 번 cycle 만, 30분 이내
