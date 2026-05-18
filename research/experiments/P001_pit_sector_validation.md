# P001 — Point-in-time sector membership validation

## 상태
계획됨

## 이게 무슨 ticket 인가

E014 가 sector RS+Breadth 전략. 현재 sector mapping = KIS snapshot
2026-05 기준. PIT (point-in-time) 멤버십 아님 → classification bias
가능성. 지피티 권장 production validation 1순위.

E014 의 production readiness 가 PIT validation 통과에 가장 의존.

## 단계별 진행

### Stage 1: PIT source 옵션 조사
- KIS API 의 historical 업종 endpoint 존재 여부 (CTPF1002R 외 다른 TR)
- KRX 정보데이터시스템 (data.krx.co.kr) 의 historical 업종분류
- pykrx 라이브러리 (KRX scrape) 의 historical 가능성
- FnGuide WICS (유료, 사용자 가입 여부 확인)
- 또는 manual historical sector table 생성 가능 종목 list

### Stage 2: 선택된 source 로 historical 수집
- 분기말 시점 (D013/E014 의 매수 시점) 별로 종목 sector
- 최소 2010-2026 분기말 66 개 시점
- 또는 매월 month-end (더 정밀)
- 종목별 sector 변경 이력 (예: 카카오, NAVER, LG에너지솔루션, 한화오션)

### Stage 3: KIS snapshot 과 차이 측정
- 종목별 sector 가 시기에 따라 달라진 비율
- KIS snapshot 과 다른 종목 수 (분기 별)
- Top 10 시총 종목 중 sector 변경 있는 종목

### Stage 4: E014 를 PIT sector 로 재실행
- 새 sector mapping (PIT) 로 E001-rev 와 같은 pipeline
- sector aggregate 재계산
- E014 strategy 동일하게 재실행
- 새 metric (PIT 기반)

### Stage 5: PIT vs snapshot 결과 비교

| 항목 | Snapshot (현재 E014) | PIT (P001-rev) | 차이 |
|---|---|---|---|
| 누적 net | +362% | ? | ? |
| Sharpe | 0.63 | ? | ? |
| MDD | -36% | ? | ? |
| 양의 수익 연도 | 9 | ? | ? |
| Top 4 sector 빈도 | ? | ? | ? |
| D013 대비 | +108pp / +0.10 | ? | ? |

## 사전 등록 판정 (지피티 권장)

**Pass** (5 기준 모두):
1. PIT 재계산 후 누적 수익 크게 훼손 안 됨 (예: 80% 이상 유지)
2. Sharpe ≥ 0.55 유지
3. D013 대비 우위 유지 (+50pp 이상)
4. Sector contribution 구조 안 바뀜 (top 1 섹터 변화 작음)
5. Top 4 sector 선택 frequency 가 snapshot 과 크게 괴리 안 됨 (Jaccard ≥ 0.7)

**Fail**:
- 누적 50% 이하로 떨어짐 → snapshot bias 가 결정적
- Sharpe < 0.40 → 재구성 또는 fallback

**Partial**:
- 일부 기준만 통과 → 정량 보고 + 사용자 결정

## 산출물

- reports/experiments/P001_pit_sector_validation/
- stage1_source_options.md
- stage2_pit_mapping/ (실제 source 결정 시)
- stage3_snapshot_vs_pit_diff.csv
- stage4_e014_pit_metrics/
- stage5_comparison.csv
- report.md (pass/fail 판정 + 권고)

## 엄격 제약

- engine.py 미수정
- 기존 strategy 미수정
- D001-D015, E003-E015, F002-F012, G000-G002 byte-identical
- 새 데이터 source 사용 시 사용자 승인 (외부 API/download)
- 우리가 가진 source (KIS credential, panel data) 우선 활용
- sandbox pandas 없으면 직접 실행 OK

## 완료 기준

- Stage 1: source 옵션 정리 + 추천
- Stage 2-5: 선택된 source 로 진행 (사용자 승인 후)
- 최종 PIT pass/fail 판정 + production readiness 업데이트
