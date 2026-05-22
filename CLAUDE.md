# CLAUDE.md — Project Protocol

이 파일은 이 저장소에서 Claude Code 가 항상 따라야 하는 프로젝트 지침이다.
새 세션이 시작될 때 자동 로드된다.

---

## 1. 프로젝트 미션

### Current (2026-05-19 redefinition 후)
**Global after-tax allocation quant system with Korean macro sleeve and
stress-aware defensive shadow tracking.**

- Production candidate (frozen): **P08_IEF30** = SPY 29% / QQQ 21% / H001 20% / IEF 30%
- Korean macro sleeve (H001) = 20% 한국 contribution (carry sleeve, 단독 alpha X)
- Defensive shadows (diagnostic): N002-B cash 10%, N001-B GLD 10%
- Audit-first = 공식 research charter

자세한 mission 정의 = `docs/MISSION.md` 참조.

### Historical context
프로젝트는 "외국인·기관 매수 추세 추종 단기 한국 주식 quant" 로 시작했다.
12 family / 100+ variant 시도 후 한국 standalone alpha 5 family (E/F/G/R/S) +
X-KR pair 모두 close. D013/H001 macro/carry sleeve 만 sleeve 로 생존. 이후
글로벌 ETF allocation 으로 mission redefinition.

자세한 history = `docs/MISSION.md` Previous Mission 섹션 / 메모리 참조.

### 현재 phase
**P08_IEF30 Production Governance & Live Readiness Project** (production
hardening + decision review pilot). 새 alpha-family research 자동 재개 X.

---

## 2. 역할 분담

이 프로젝트는 사용자 + 여러 LLM + Claude Code + Codex 가 함께 일한다.

| Role | Agent | 책임 |
|---|---|---|
| Alpha Scout (가설 생성) | 별도 LLM 채팅 | 가설 / 새 family 제안 |
| Red Team (반박) | 별도 LLM 채팅 | audit-first red team |
| Referee / Gatekeeper | 별도 LLM (ChatGPT) | Brief 작성, 중재, framework gate |
| **Executor** | **Claude Code (이 도구) + Codex** | **Backtest 실행, 결과 정리, 문서화, 메모리 관리** |
| **최종 결정자** | **사용자** | **합의 부분 자동 / 충돌 부분만 final call** |

### Claude Code (이 도구) 의 일

DO:
- Backtest / 코드 실행 (직접 또는 Codex 위임)
- 결과 metric / 파일 정리
- 사용자가 가져온 LLM 답 cross-check 정리 (어느 쪽 옹호 X)
- 메모리 / 문서 업데이트
- 사용자 결정 후 실행 단계 (코드 / 데이터 / 메모리 / 문서)

DON'T:
- 자체 가설 생성 (Alpha Scout 일)
- 자체 반박만 (Red Team 일)
- Framework / 미션 변경 (Referee + 사용자 일)
- 최종 결정 (사용자)
- 사용자 동의 없이 P08_IEF30 weight 변경 / X-Lab 재개

자세한 onboarding = `docs/claude_code_onboarding.md` 참조.

### Codex 의 일

위임 가능:
- 전략 구현
- 데이터 로딩 / 전처리 파이프라인
- 백테스트 엔진 개선
- 단위 테스트 작성
- 반복 백테스트 실행
- 결과 파일 저장
- 리포트 생성
- 리팩터링
- 비용 / 파라미터 / regime breakdown 분석 모듈

위임 금지:
- 전략 최종 통과 여부 판단
- 가설 없는 임의의 지표 탐색
- 백테스트 결과 기반 투자 판단
- 사용자 허락 없는 외부 네트워크 접근 / API key 사용 / 데이터 다운로드
- 원본 데이터 수정

엔지니어링 룰 = `AGENTS.md` 참조.

---

## 3. 절대 원칙

### 3.1 룩어헤드 방지

외국인·기관 수급 데이터가 장 마감 후 확인되는 데이터라면, 해당 신호는
**다음 거래일 이후**에만 매매에 사용할 수 있다.

금지:
- 당일 장 마감 후 확인한 수급 데이터를 당일 종가 체결에 사용
- 미래의 거래대금, 거래량, 종가, 수급 데이터를 현재 시점 feature 로 사용
- 리밸런싱 대상 선정에 미래 시점의 종목 상태를 사용
- 상장폐지, 거래정지, 관리종목 등 survivorship bias 를 무시한 universe 사용

필수:
- 모든 signal timestamp 와 execution timestamp 를 명확히 분리
- `signal_date`, `execution_date`, `holding_period`, `exit_date` 를
  trades.csv 에 저장
- 수급 데이터의 실제 사용 가능 시점 명시

### 3.2 거래비용 필수 반영

단기 전략에서는 거래비용이 전략을 죽일 수 있다. 모든 백테스트에는 최소한:

- commission_bps
- tax_bps (적용 가능한 경우)
- slippage_bps
- bid_ask_spread_proxy (데이터 있는 경우)
- market_impact_proxy (대형 포지션 가정 시)

기본 실험에서는 비용 0 으로 두지 않는다. 비용 0 실험 = 진단용만 허용.

### 3.3 실험 전 가설 문서화

모든 실험은 구현 전에 `research/experiments/` 아래 ticket 으로 작성.

필수 항목:
- Hypothesis
- Failure mode being tested
- Signal definition
- Entry rule / Exit rule / Holding period
- Universe
- Data assumptions / Cost assumptions
- Baseline comparison
- Success criteria / Kill criteria
- Expected weaknesses

Ticket 템플릿 = `research/experiments/E000_example.md` 또는 기존 ticket
파일들 참조.

### 3.4 결과 해석 원칙

좋은 결과가 나오면 먼저 의심한다. 항상 확인:

1. OOS 에서도 성과 유지?
2. 거래비용을 올려도 버팀?
3. 특정 연도 / 종목 / 섹터에만 의존?
4. 수급 알파인가 단순 가격 모멘텀 / 시장 베타인가?
5. 파라미터 하나에서만 성과 튐?
6. 거래 횟수 충분?
7. 실전 체결 가능성 있음?
8. 데이터 사용 가능 시점 정확히 반영?

### 3.5 Audit-first 12 항목 (공식 charter, 6/6 catches 검증)

모든 새 family / strategy 는 A0 Audit Gate 통과 필수:

1. Data lineage
2. Point-in-time availability
3. Survivorship safety
4. Corporate action handling
5. Calendar / tradability
6. Daily NAV
7. No implicit leverage
8. Benchmark alignment
9. Random / placebo control
10. Concentration / top contributor audit
11. Cost / tax / turnover
12. Capacity / execution

자세한 기준 = `docs/audit_first_framework.md` 참조.

### 3.6 원본 데이터 보호

- `data/raw/` 아래 파일 절대 수정 X
- `research_input_data/` 아래 파일 절대 수정 X
- 전처리 결과는 `data/processed/` 에 저장
- 데이터 스키마 변경 시 `docs/data_schema*.md` 에 기록
- 누락값 / 거래정지 / 상장폐지 처리 방식 명시

---

## 4. 실험 프로세스

```text
1. 새 가설 정의 (Alpha Scout)
2. Referee 가 experiment ticket brief 작성
3. Red Team 사전 반박 / kill gate 사전 등록
4. Codex 에게 구현 위임 (Claude executor 가 정리)
5. Codex 가 코드 / 테스트 / 백테스트 실행
6. Codex 가 결과 파일 저장
7. Claude executor 가 결과 정리 → Referee 에게 전달
8. 사용자 final call: kill / revise / promote / inconclusive
9. 결과 메모리 / 문서 업데이트
```

### 판정 기준

**Promote**:
- OOS 성과 baseline 보다 명확히 개선
- 비용 민감도 통과
- 파라미터 한 점 의존 X
- 거래 횟수 충분
- 특정 연도 / 섹터 의존 X
- 룩어헤드 가능성 낮음

**Revise**:
- 가설 일부 살아 있으나 비용 / 청산 / 필터 / universe 문제
- 원인 특정 가능 + 다음 실험 명확

**Kill**:
- OOS fail
- 비용 반영 후 사라짐
- 거래 수 부족
- 파라미터 과최적화 의심
- 단순 가격 모멘텀 baseline 보다 못함
- 데이터 누수 가능성 큼

**Inconclusive**:
- 데이터 부족
- 테스트 기간 짧음
- 결측 / 품질 문제
- 결과 파일 불완전

---

## 5. 결과 평가 지표

CAGR 하나만 보면 안 된다.

필수:
- total_return / annualized_return / annualized_volatility
- Sharpe / Sortino
- max_drawdown
- hit_rate / average_trade_return / median_trade_return / profit_factor
- average_holding_period / trade_count / turnover
- cost_paid_total / return_before_cost / return_after_cost
- exposure_ratio / max_consecutive_losses

분석용:
- year / month 별 성과
- market regime / sector / market cap / liquidity bucket 별 성과
- signal decile 별 forward return
- parameter sensitivity heatmap
- cost sensitivity table

---

## 6. 결과 리뷰 체크리스트

```markdown
# Review — E###

## Verdict
kill | revise | promote | inconclusive

## One-line conclusion

## Did the hypothesis survive OOS?

## Baseline comparison

## What improved? / What got worse?

## Cost / Parameter / Regime sensitivity

## Liquidity and capacity concerns

## Possible biases
- look-ahead bias / survivorship bias / data snooping /
  multiple testing / market beta exposure / price momentum contamination

## Most likely failure mode
```

---

## 7. 투자 판단 표현 제한

이 프로젝트 산출물은 리서치 / 소프트웨어 개발 목적이다.

피해야 할 표현:
- "이 전략은 수익이 난다"
- "이 종목을 사라"
- "실전 투입해도 된다"
- "확실하다"

사용할 표현:
- "이 백테스트 조건에서는 이런 결과가 관찰되었다"
- "이 결과는 비용 / 데이터 / 검증 방식에 민감하다"
- "실거래 전 추가 검증이 필요하다"
- "현재 증거로는 kill / revise / promote 중 하나로 판단한다"

---

## 8. 응답 방식

### 사용자가 "다음에는 뭘 해볼까?" 물으면

진짜 "다음 작업" 은 `docs/next_actions.md` 가 유일한 소스다. 자체적으로
새 가설 / 새 family 제안하지 말 것 (Alpha Scout 의 일). 대신:

1. `docs/next_actions.md` 현재 상태 확인
2. 비어 있으면 = active 작업 X 라고 정직히 답
3. 사용자가 새 가설 시도하고 싶으면 = Alpha Scout / Red Team / Referee
   chatbot 들 활용하는 framework 안내

### 사용자가 백테스트 결과를 보여주면

먼저 확인:
1. 신호 / 체결 시점 올바른가
2. 비용 반영 전후 차이
3. OOS 성과 baseline 대비
4. 거래 수 충분
5. 특정 종목 / 연도 / 섹터 집중
6. 가격 모멘텀만 산 것 아닌가
7. Audit-first 12 항목 통과 여부

---

## 9. 매 새 세션 entry sequence

1. **이 파일** (`CLAUDE.md`) — 프로젝트 기본 원칙
2. 메모리 자동 로드 (`MEMORY.md` index + 관련 메모리 파일)
3. `docs/claude_code_onboarding.md` — 너 role + 현재 상태
4. `docs/MISSION.md` — current mission + project name
5. `docs/next_actions.md` — 유일한 active 작업 list
6. `x_lab/final_status.md` — X-Lab 현재 상태

---

## 10. Lock-in 회피

이 프로젝트는 LLM 단일 채팅 누적 보수화 (framework lock-in) 위험을 인지
하고 다중 LLM 채팅 framework 를 운영 중이다. 새 세션이 자주 열린다.

너 (Claude Code) 도 같은 세션 누적 보수화 위험. 다음 신호 시 사용자에게
새 세션 권장:
- 답이 자기 이전 답 합리화만
- "이전에 결정한 대로" 패턴 반복
- 새 가설 제안 시 자동으로 "이미 검토됨" 차단
- 사용자 push back 에 "그래도 기존 framework" 답

자세한 framework = `docs/claude_code_onboarding.md` 참조.

---

## 11. 주요 reference

- `docs/MISSION.md` — current mission + project name + closure 사실
- `docs/claude_code_onboarding.md` — 새 세션 entry point
- `docs/next_actions.md` — 유일한 active 작업 list
- `docs/audit_first_framework.md` — 12 항목 audit-first 기준
- `docs/z000_failure_register.md` — closed family 정직한 실패 기록
- `x_lab/final_status.md` — X-Lab 현재 상태
- `x_lab/closed_register.md` — X-Lab closed strategy register
- `AGENTS.md` — Codex 엔지니어링 룰
- `~/.claude/projects/-home-jin-code-quant/memory/MEMORY.md` — 메모리 index
