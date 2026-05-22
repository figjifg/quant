# X-Lab Closed Register

X-Lab is quarantined. Closed strategies are retained as diagnostic records and
must not be imported into P08 without the Import Gate.

## Closed Strategies

| Strategy | Status | Reason | Sub-finding |
| --- | --- | --- | --- |
| X-ETF001 | CLOSED | X-ETF001 time-series momentum: 40/40 variants closed. Best after-cost Sharpe 0.700, below P08 proxy 1.036 and EW13 0.855. | CLOSED — NO_ACTIONABLE_EDGE_OVER_STATIC_ALLOCATION_OR_SIMPLE_SHADOWS. |
| X-ETF900 | CLOSED | X-ETF900 final defensive challenge: 24/24 variants closed. Best V10 Sharpe 1.149; after-tax weakened to 1.066; P08 + 10% V10 combo MDD +1.21pp, below 2pp deep combo gate. | V10 marginally beat P08 proxy but underperformed N001-B GLD 10% and N002-B cash 10%; action X. |
| X-KR001 | CLOSED | X-KR001 Korean pair/residual mean reversion: 12/12 variants closed (6 pre-registered × long-only/long-short). Gate 7 (turnover/tax/slippage kills) 12/12, gate 6 (two subperiod fail) 11/12, gate 1 (after-cost Sharpe<1) 8/12. Top variant XKR001_V02 long_only Sharpe 1.497 / CAGR 175.78% / MDD -99.7% = impossible-return artifact. A0 sanity 4 FAIL (long-short beta/residual impossible return). | CLOSED — NO_ACTIONABLE_KOREAN_PAIR_OR_RESIDUAL_MEAN_REVERSION_EDGE. Long-short borrow infeasible (KR short 제한); long-only fallback retail X. W001 engine repair 후에도 일부 measurement artifact 잔존. |

## Framework Finding

N-family simpler vs ETF dynamic framework 확정.
Simpler fixed N-family shadows > dynamic ETF rotation.
V10 is a marginal diagnostic reference only: production X, paper X, P08 import X.

X-KR track 확정. Korean simple standalone alpha (sector / stock ranking / title event / mean reversion / pair) 5 family 모두 audit-first gate 미통과. D013/H001 macro/carry sleeve 가 유일 생존 Korean contribution.

---

## 2026-05-22 — Bull/Bear/Referee First Cycle Final

X-Lab "FULL CLOSED" status 가 첫 multi-LLM cycle 진행 중 일시 reopen
시도되었으나, Step 5 A0 audit 결과 두 TEST 카드 모두 BACKLOG 강등되어
**effective reopen X**.

### Step 3 lock → Step 5 final lock

| Strategy ID | Step 3 verdict | Step 5 verdict |
|---|---|---|
| KR-PASSIVE-REBALANCE-001 A형 | TEST | BACKLOG (A0 FAIL, KRX event calendar 부재) |
| KR-OVERHANG-AVOID-001 filter형 | TEST | BACKLOG (A0 PARTIAL, DART body parser 부재) |
| KR-DART-BODY-RETURN-001 | BACKLOG | BACKLOG (unchanged) |
| KR-EARNINGS-DRIFT-001 | BACKLOG | BACKLOG (unchanged) |
| KR-CONDITIONAL-SHOCK-REVERSION-001 | BACKLOG | BACKLOG (unchanged) |
| KR-QUALITY-VALUE-RETURN-001 | BACKLOG | BACKLOG (unchanged) |

Cycle 1 end state: TEST 0 / BACKLOG 6 / REJECT 0.

### X-Lab status

**FULL CLOSED 유지**. Cycle 1 의 2 reopen 시도 = data prerequisite 부족으로
모두 BACKLOG. 새 TEST 진입 X.

**여전히 CLOSED**:
- 기존 X-ETF001 / X-ETF900 / X-KR001 pair (위 표)
- 모든 closed family (E/F/G/K/J/Q/R/S)

**BACKLOG (성과 테스트 금지, data prerequisite 부족)**: 6 카드.

자세한 lock / unblock 조건:
- `docs/step5_A0_verdict_lock.md` — Step 5 verdict 공식 lock
- `docs/backlog_A0_queue.md` — 데이터 인프라 task Q1 / Q2
- `docs/data_gap_KR_PASSIVE_REBALANCE.md` — Q1 누락 필드
- `docs/data_gap_KR_OVERHANG_AVOID.md` — Q2 누락 taxonomy / parser
- `docs/backlog_register.md` (Bull/Bear/Referee First Cycle Cards 섹션)
- `research/experiments/KR_PASSIVE_REBALANCE_001_A_test.md` (spec lock 됨, 사용 X)
- `research/experiments/KR_OVERHANG_AVOID_001_filter_test.md` (spec lock 됨, 사용 X)

### Forbidden (Cycle 1 lock)

- No backtest
- No Codex performance test 위임
- No production / paper / P08 / live readiness / shadow track 연결
- 사이클 진행 중 spec 사후 수정 = Bear 재심의 없이 X
- Reduced / proxy 변형 = 글로벌 REJECT trigger 영역
