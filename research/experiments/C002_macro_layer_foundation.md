# C002 — Macro layer foundation (variance decomposition + 데이터 수집 + predictions 정량화)

## Status
planned

## What this ticket is

C001 v2 의 매크로 layer hierarchical architecture 를 검증하고 v1 검증
(C003) 의 기반을 다지는 ticket. 3개의 sub-task 를 하나의 ticket 으로
묶음. **백테스트 없음. Predictions 의 PASS/FAIL 판정 없음.**

각 sub-task 가 분리된 ticket 보다 함께 묶인 이유: 셋 다 매크로 layer
의 same foundation prep 이고, 서로 의존적이며 (variance decomposition
결과에 따라 predictions 정의 미세 조정 가능), 백테스트나 verdict
없이 prep 만 하기 때문에 testing budget 인플레이션 위험 없음.

## Three sub-tasks

### Task 1: Variance decomposition
**목적**: C001 v2 의 architecture 의 premise (한국 KOSPI 의 macro/
sector/idiosyncratic 비율이 60/30/10 근처) 정량 검증.

### Task 2: 매크로 데이터 수집
**목적**: 매크로 layer v1 의 검증과 향후 deepening (v2-v6) 을 위해
필요한 macro 데이터 일괄 수집. C001 v2 의 HIGH priority 목록 모두.

### Task 3: 매크로 v1 predictions 정량화
**목적**: C001 v2 의 P1-P5 를 backtest-able 한 정확한 measurement
form 으로 변환. 사전 등록의 정량 명세화.

---

## Task 1 — Variance decomposition

### Methodology

**Input data**:
- KOSPI 일별 수익률 시계열 (2010-2026, ~4000 거래일)
  - Source: `market_breadth_kospi.cap_weighted_return` (caveat: B011
    에서 발견했듯이 dynamic top-100 survivorship-biased proxy. 정량
    분석 시 caveat 명시 + 가능하면 alternative source 추가)
- Macro factors:
  - USDKRW return (FRED, 이미 보유)
  - US 3m rate change (FRED, 이미 보유)
  - + Task 2 에서 수집한 변수들 (VIX, DXY, US 10y, USDCNY, HY spread)
- Sector factors (가능한 경우):
  - 한국 섹터 지수가 데이터에 없으므로 univers 의 시가총액 상위 N개
    종목들을 KIS 표준 또는 외부 분류로 grouping 한 sector return proxy
  - 또는 단순화: equity_panel 의 universe 상위 N개를 sector 별로
    aggregate
  - 이게 어렵다면 sector 항목은 "TODO for future ticket" 으로 표시

**Decomposition**:
일별 KOSPI return 을 OLS regression 으로 분해:

```
KOSPI_return(t) = α 
                + β_macro · [USDKRW_ret, US3m_Δ, VIX_Δ, ..., HY_Δ]
                + β_sector · [반도체_ret, 금융_ret, ..., 섹터들]
                + ε(t)
```

각 leg 의 R² contribution 계산. 산출:
- R²_macro: 매크로 변수들만으로 explained variance
- R²_sector: 섹터 변수들만으로 explained variance
- R²_combined: 둘 다 사용 시 explained variance
- R²_idiosyncratic: 1 - R²_combined

**Hierarchical decomposition** (better than simple R² sum):
- Step 1: regress KOSPI return on macro factors only → R²_macro_marginal
- Step 2: residuals from Step 1 → regress on sector factors → R²_sector_marginal
- Step 3: residuals from Step 2 → idiosyncratic

→ 결과로 macro%, sector%, idiosyncratic% 의 분해.

**Time windows**:
- 전체 16년 (2010-2026)
- 또한 sub-period: 2010-2017 vs 2018-2026 (regime change 가능성 확인)

### Pre-registered interpretation

C001 v2 의 architecture 의 falsification 적용:

| 결과 | 의미 | 다음 action |
|---|---|---|
| macro ≥ 50% | user reframing 강하게 확인 | architecture 진행, C003 |
| macro 30-50% | architecture 부분 확인 | architecture 진행, but sector layer 의 중요도 재인식 |
| **macro < 30%** | **F-Arch-1 발동** | **architecture 재설계 필요, C003 보류** |
| Idiosyncratic > 60% | 어느 layer 도 dominant 아님 | top-down 가설 자체 약함, 큰 재고 |

**Sub-period 차이**:
- 2010-2017 vs 2018-2026 의 macro% 가 ±15pp 이상 차이 → regime
  change 확인. v1 의 predictions 도 regime-conditional 일 수 있음
  → C003 의 검증 시 sub-period 별 별도 적용.

### Output

`docs/variance_decomposition_2010_2026.md`:
- 위 methodology 결과 표
- Hierarchical R² 분해
- Sub-period 분석
- C001 v2 architecture 에 대한 quantitative verdict

---

## Task 2 — 매크로 데이터 수집

### 수집 대상 (C001 v2 HIGH priority 일괄)

| 변수 | Source | FRED series | 빈도 | Coverage |
|---|---|---|---|---|
| VIX | FRED | VIXCLS | daily | 1990-2026, 4270 rows in 2010-2026 |
| DXY | FRED | DTWEXBGS | daily | 2006-2026, 4266 rows in 2010-2026 |
| US 2y treasury | FRED | DGS2 | daily | 1976-2026, 4270 rows in 2010-2026 |
| US 10y treasury | FRED | DGS10 | daily | 1962-2026, 4270 rows in 2010-2026 |
| USDCNY | FRED | DEXCHUS | daily | 1981-2026, 4266 rows in 2010-2026 |
| **Credit spread (Baa-10y)** | FRED | **BAA10Y** | daily | 1986-2026, 4270 rows in 2010-2026 |

**Note on credit spread**: Original plan listed BAMLH0A0HYM2 (ICE BofA
US HY OAS), but FRED's ICE BofA series were truncated to 2023-2026
only (license change at some point). Substituted with BAA10Y
(Moody's Baa Corporate Bond Yield minus 10-Year Treasury) which has
1986+ history. This is the classical "credit risk" spread proxy
used in macro research; mechanism equivalent for our purpose.

### 수집 상태 — Claude 가 사용자 승인 후 직접 완료 (2026-05-16)

FRED 다운로드는 Codex sandbox 가 network access 제한 가능성 있어,
Claude 가 사용자 승인 후 bash curl 로 직접 진행. 다음 6개 파일이
`research_input_data/inputs/macro_features/` 에 저장됨:

- `fred_vix.csv`
- `fred_dxy.csv`
- `fred_dgs2.csv`
- `fred_dgs10.csv`
- `fred_dexchus.csv`
- `fred_baa10y_spread.csv` (was originally HY spread; substituted)

기존에 있던 `fred_dgs3mo.csv`, `fred_dexkous_usdkrw.csv` 와 함께 총 8개
FRED series 사용 가능.

**Codex 의 남은 작업** (network access 불필요):
- 다운로드된 8개 파일의 schema 검증 + loader 확장
- `src/data/macro_factors.py` (NEW) 또는 기존 모듈에 추가
- 각 series 별 unit test
- 결측 / 휴장일 처리 정책 코드화

### Data timing 정책

매크로 변수의 사용 시점 (look-ahead 방지):
- 미국 데이터 (VIX, DXY, US 금리, HY spread, USDCNY): 미국 시장
  마감 후 발표 → 한국 다음 거래일 09:00 시점에 사용 가능 → **한국
  signal_date T+1 에 적용**
- USDKRW: 한국 시장 마감 시점 (15:30) 의 KRX rate, FRED 는 다음날
  발표 → 한국 signal_date T 에 사용 (이미 보유 데이터의 timing 과 동일)

이 timing 을 `data_timing_risks` 메모리에 추가 (있으면 update).

### Output

- 새 데이터 파일들 (`research_input_data/inputs/macro_features/fred_*.csv`)
- `src/data/macro_factors.py` (NEW)
- `tests/test_macro_factors_loading.py`
- `docs/macro_factors_schema.md` — 각 series 의 schema, coverage,
  타이밍 정책 문서

---

## Task 3 — 매크로 v1 predictions 정량화

C001 v2 의 P1-P5 를 backtest-able 한 정확한 form 으로 변환.

### Common definitions

**시점 T**: 각 거래일
**lookback**: prediction 조건 측정의 과거 window
**forward**: outcome 측정의 미래 window
**outcome**: KOSPI 수익률 (variance decomposition 에서 정의한 동일
proxy 사용)

### P1 — USDKRW 단일

**Predict**:
- 조건 A: USDKRW(T) / USDKRW(T-252) - 1 ≤ 0 (KRW 1년 강세)
- 조건 B: USDKRW(T) / USDKRW(T-252) - 1 ≥ +5% (KRW 1년 큰 약세)
- 조건 C: 위 둘 사이 (-5% ~ +5%) → 중립

**Forward**:
- y = (cumulative KOSPI return over [T+1, T+252])

**Pre-registered hypothesis**:
- Mean(y | 조건 A) ≥ +10%
- Mean(y | 조건 B) ≤ 0%
- 두 mean 의 t-test p < 0.05 (n_A ≥ 5 AND n_B ≥ 5)

### P2 — US Fed phase

**Predict**:
- Δrate = US3mRate(T) - US3mRate(T-252)
- 조건 A: Δrate < 0 (1년간 금리 하락)
- 조건 B: Δrate > +1.0% (1년간 강한 긴축)

**Forward**: 동일 (252거래일 KOSPI return)

**Hypothesis**:
- Mean(y | 조건 A) ≥ +5%
- Mean(y | 조건 B) ≤ 0%

### P3 — Combined (P1 ∧ P2)

**Predict**:
- 조건: USDKRW yoy ≤ 0 AND Δrate < 0

**Forward**: 동일

**Hypothesis**:
- Mean(y | 조건) ≥ +20%
- AND Mean(y | 조건) > Mean(y | P1 단독) (combined 가 single-leg 보다
  strictly 큼)

### P4 — XOR (one leg only)

**Predict**:
- 조건: (USDKRW yoy ≤ 0) XOR (Δrate < 0)

**Forward**: 동일

**Hypothesis**:
- Mean(y | 조건) ∈ [-5%, +10%] (중립)

### P5 — Neither

**Predict**:
- 조건: USDKRW yoy ≥ +5% AND Δrate > +1.0%

**Forward**: 동일

**Hypothesis**:
- Mean(y | 조건) ≤ 0%

### Sample size considerations

16년 = ~4000 거래일. 매일 prediction 측정 가능하지만 forward window
가 252 거래일이면 **independent observations 는 약 4000/252 ≈ 16개**.
n=16 은 통계적으로 작음.

**현실적 처리**:
- Daily measurement → overlapping forward windows (정직하게 acknowledge)
- 결과 해석 시 confidence interval 매우 넓음
- 본질적으로 16-20 개의 independent regime 관측이므로 **statistical
  power 한계 인정**
- 보완: Bootstrap (block bootstrap 으로 overlap 보정) 으로 CI 추정

### Output

`research/strategy_thesis/C002_predictions_quantified.md`:
- 위 5 predictions 의 정확한 formula
- 각 prediction 의 sample size 추정
- Bootstrap methodology 명시
- Pre-registered statistical thresholds (significance, effect size)

---

## Order of work

1. **Task 1 (variance decomposition)**: 데이터 수집 전에 가능한
   부분부터 (이미 가진 USDKRW + US3m + market_breadth + equity panel).
   섹터 데이터 없으면 partial decomposition.
2. **Task 2 (데이터 수집)**: 사용자 승인 후 외부 네트워크 접근.
3. **Task 1 redo**: 새 macro 변수들 포함해서 variance decomposition
   재실행. Full decomposition.
4. **Task 3 (predictions 정량화)**: 별도 작업, 데이터 수집 후 (sample
   size 등 확인 필요).

각 단계마다 commit. Codex 호출 한 번에 모두 가능 or 분리 가능.

---

## Output files

- `docs/variance_decomposition_2010_2026.md`
- `docs/macro_factors_schema.md`
- `research_input_data/inputs/macro_features/fred_*.csv` (6 new files)
- `src/data/macro_factors.py` (NEW)
- `tests/test_macro_factors_loading.py` (NEW)
- `research/strategy_thesis/C002_predictions_quantified.md`
- `reports/experiments/C002_macro_layer_foundation/` (variance
  decomposition 의 plot / table)

---

## Completion criteria

- pytest fully green
- 모든 데이터 파일 schema 검증 통과
- Variance decomposition 결과가 C001 v2 의 architecture verdict 에
  명확한 답
- Predictions 정량 formula 가 C003 에서 즉시 적용 가능한 form

---

## Out of scope for C002

- ❌ Predictions 의 actual 검증 (그건 C003)
- ❌ Strategy 백테스트
- ❌ Macro v2-v6 의 데이터 수집 (현재 v1 + v2 의 VIX 만, 추가는 필요시
  별도 ticket)
- ❌ Sector / stock layer 작업
- ❌ Engine 변경

---

## 사용자 승인 필요 사항

이 ticket 의 두 가지가 사용자 명시 승인 필요:

1. **외부 네트워크 접근** (FRED 다운로드): 처음으로 우리 프로젝트가
   외부에서 데이터 가져옴. CLAUDE.md 의 "사용자 허락 없는 외부 네트워크
   접근 금지" 규칙에 해당.
2. **데이터 추가**: `research_input_data/inputs/macro_features/` 에
   새 파일 추가. 기존 데이터에 큰 의존 strategy 가 없으니 안전하지만
   사용자 인지 필요.

승인 후 Codex 위임.

## Result summary
DO NOT FILL until completion.

## Claude review
DO NOT FILL until result files are read.
