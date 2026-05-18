# E012 — E011 Top 4 견고성 + ablation (지피티 핵심 권장)

## 상태
계획됨

## 이게 무슨 ticket 인가

E011 (Top 4) 의 견고성 + 핵심 질문: **Flow 가 진짜 메인 알파인가
아니면 RS + Breadth 만으로도 충분한가?**

지피티 핵심 권장:
> RS only Top 4
> RS + Breadth Top 4
> Flow + RS + Breadth Top 4
>
> 만약 RS + Breadth 가 Flow+RS+Breadth 와 비슷하거나 더 좋으면, Flow
> 는 메인 알파 아니라 제거하거나 보조 진단으로 내려야.

## Test set (사전 등록)

### Score ablation (Top 4 고정)

| 변형 | Score |
|---|---|
| A | RS only |
| B | RS + Breadth |
| **C (E011 baseline)** | **Flow + RS + Breadth** |

### Top-K 주변 (Flow+RS+Breadth carrier 고정)

| K | Allocation |
|---|---|
| 3 | 2/2/1 (E007) |
| **4** (E011) | **2/1/1/1** |
| 5 | 1/1/1/1/1 |

### Lookback robustness (over-optimization 피하기 위해 최소)

| Test | window |
|---|---|
| Base | RS 20/60, Flow 20/60 |
| Extended | RS 60/120, Flow 60/120 |

### Cost stress (Top 4 carrier — E009 는 Top 3 였음)

| 시나리오 | commission / tax / slippage |
|---|---|
| base | 1.5 / 20 / 5 |
| 2x | 3.0 / 40 / 10 |
| 3x | 4.5 / 60 / 15 |
| extra slippage | 1.5 / 20 / 15 |

## 사전 등록 판정

| 결과 | 판정 |
|---|---|
| Score ablation: A (RS only) 또는 B (RS+Breadth) 가 C (Flow+RS+Breadth) 보다 ≥ 5pp 누적 우위 | **Flow 제거 권장** — RS+Breadth Top 4 가 새 챔피언 |
| C 가 A/B 보다 더 좋음 또는 비슷 | Flow 가 진짜 기여 — Top 4 champion 유지 |
| Top-K (K=3,4,5) 모두 샤프 ≥ 0.40 | 안정 구간 |
| Lookback (Extended) 큰 폭 변화 없음 | lookback robust |
| 3x 비용에서도 Top 4 누적 ≥ +150% | 비용 stress 통과 |

## 산출물

- reports/experiments/E012_top4_robustness_ablation/
- score_ablation/{rs_only,rs_breadth,flow_rs_breadth}/
- topk_grid/{k3,k4,k5}/
- lookback/{base,extended}/
- cost_stress/{base,2x,3x,extra_slippage}/
- robustness_summary.csv

## 엄격 제약

- engine, 기존 strategy 미수정
- D001-D015, E003-E011 byte-identical
- 새 코드 최소화 (기존 sector_flow_score, sector_rs_score, sector_breadth_score, sector_combined_score 재사용)
- 종합 비교 표 한국어
