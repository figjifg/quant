# D019 — D013 최대 손실폭 (MDD) 원인 분석

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 권장. D013 의 최대 손실폭이 -33.92% — D001 (-23.67%) 보다 큼.
Layer 4 의 drawdown 쿨다운, 스트레스 필터 설계 전에 -34% 가 언제, 왜
발생했는지 정확히 알아야 함.

새 backtest 없음. D013 의 기존 equity_curve.csv 와 trades.csv 만
분석.

## 분석 항목

### A. 최대 손실 구간 식별
- 누적 가치 peak 날짜
- trough 날짜 (저점)
- recovery 날짜 (peak 회복) — 회복 안 됐으면 명시
- 손실 기간 (peak → trough 거래일 수)
- 회복 기간 (trough → recovery 거래일 수)

### B. 그 기간 의 매매 결정
- 손실 구간에 매수했던 분기들 (entry quarters)
- 손실 구간에 매도했던 분기들
- 손실의 주된 발생: 매수 후 가격 하락 vs 매도 후 가격 회복 등
- 매수 종목들 (그 분기에 어떤 5 종목)

### C. 그 기간 의 매크로 신호
- D013 의 합성 점수 추이
- 5 블록 각각의 점수 변화
- 어느 변수가 가장 negative 였는지
- 매수 신호가 잘못된 시점이었나, 맞았는데 시장이 더 빠졌나

### D. 그 기간 의 시장 환경
- KOSPI 자체의 같은 기간 수익
- VIX 추이
- USDKRW 추이
- US 10y real yield, BAA10Y spread 추이

### E. D013 vs D001 비교
- 같은 기간 D001 의 누적 가치 변화
- 같은 기간 D001 의 매수/매도 결정
- D013 가 매수한 분기에 D001 은 OFF 였는지

## 사전 등록 진단

| 발견 | 해석 | Layer 4 영향 |
|---|---|---|
| 특정 한 분기의 매수가 -X% 손실 → 시장 급락 | 매크로 신호가 너무 늦었음 | 변동성 타겟팅 + 스트레스 필터 필요 |
| 여러 분기 연속 매수 → 약세장 누적 | 매크로 게이트가 약세장 못 잡음 | MDD 쿨다운 필요 |
| 매도 후 회복장 놓침 | 매크로 게이트가 너무 빨리 OFF | (Layer 4 가 해결 어려움) |
| 특정 종목 / 섹터 집중 | concentration 문제 | Layer 4 의 종목/섹터 cap 필요 |

## 구현

분석 위주, 새 backtest 없음.

추가만:
- `src/audit/mdd_attribution.py` (신규) — 최대 손실 구간 식별 +
  매크로/시장 환경 정렬 분석 함수
- `reports/experiments/D019_d013_mdd_attribution/mdd_summary.csv` —
  최대 손실 구간의 기본 정보
- `reports/experiments/D019_d013_mdd_attribution/mdd_quarters_detail.csv` —
  손실 구간의 분기별 매수/매도 정보
- `reports/experiments/D019_d013_mdd_attribution/macro_signal_during_mdd.csv` —
  손실 구간의 변수별 z-score 추이
- `reports/experiments/D019_d013_mdd_attribution/report.md` — 종합 분석

**수정 금지**:
- engine.py
- 기존 strategy 모듈 (a001-a004, b001-b011, c003-c020, d001-d018)
- D013 의 모든 결과 (감사만)
- research_input_data/

## 완료 기준
- pytest 통과
- D013 결과 unchanged
- 최종 보고:
  - 최대 손실 시작/저점/회복 (있다면) 날짜
  - 손실 비중을 가장 크게 만든 분기 / 종목
  - 그 기간의 매크로 신호 상태
  - 그 기간의 시장 환경
  - Layer 4 설계에 대한 권고
