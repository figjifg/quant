# Paper Trading Operations

Research Freeze v2 status: `P08_IEF30` is the frozen primary candidate and new alpha-family research is closed. The official mission is a global after-tax allocation quant system with Korean macro sleeve and stress-aware defensive shadow tracking.

R-family status: CLOSED as diagnostic. No marginal candidate added (Q ETF +0.01, R fail). Paper tracking dashboard unchanged.

Project research-discovery phase complete. X-Lab is closed for the ETF track;
V10 is diagnostic only and does not become a paper candidate. P08_IEF30 paper
tracking continues unchanged with N002-B / N001-B as defensive shadows.

Cadence:
- Weekly: drift_alert (5분)
- Monthly: NAV update + summary
- Quarterly: dry-run + evaluation + rebalance

4 quarter checkpoint: around 2027-Q2 = live decision.

Idle definition:

- No new marginal paper candidate
- P08_IEF30 paper tracking continues
- N002-B / N001-B shadows continue
- Quarterly evaluation
- Tax/broker confirmation
- Small live pilot plan
- Drawdown acceptance memo
- Closed family register update

Primary references:

- Research freeze: `docs/research_freeze_v2.md`
- Production manual: `docs/production_candidate_manual.md`
- Paper tracking manual: `docs/paper_tracking_manual.md`
- Risk statement: `docs/risk_statement.md`
- Tax/vehicle memo: `docs/tax_vehicle_memo.md`
- Backlog register: `docs/backlog_register.md`
- Final dashboard: `paper_trading/operations/dashboard.md`

T-family status: complete as research. O-family operations tooling is the next workstream.

Mission: build a tax-aware global allocation quant system using the validated Korean macro sleeve plus global ETF exposures.

Live constraint: all O-family outputs are paper operations artifacts. Tax-professional confirmation is required before any live implementation.

D013 + H001 KR carry paper trading 실거래 framework.
지피티 권장 3 버전 추적.

## 디렉토리

- signals/YYYY-Q.json — 분기별 D013 신호 (사전 등록, 수정 금지)
- executions/YYYY-Q.json — 실제 체결 기록 (사용자 작성)
- evaluations/YYYY-Q.md — 분기말 성과 + IS / slippage 보고

## 3 버전 추적 (지피티 권장)

| 버전 | 실거래 | 추적 |
|---|---|---|
| D013 original (cash) | X | baseline reference (OFF = cash 0%) |
| **H001 primary** | **O** | OFF = KR short-rate carry sleeve |
| H005 shadow | X | OFF = defensive basket (KR 50 / USD 25 / Treasury 25) |

evaluations/YYYY-Q.md 에 3 버전 모두 기록 권장.

## Final Six-Portfolio Dashboard

Final paper dashboard scope:

| Portfolio | Role |
|---|---|
| P08_IEF30 | Primary |
| N002-B cash 10% | Defensive shadow |
| N001-B GLD 10% | Defensive shadow |
| QQQ 100% | Benchmark |
| SPY 100% | Benchmark |
| H001 | Korean sleeve only |

Dashboard command:

```bash
.venv/bin/python -m src.ops.dashboard
```

Dashboard output: `paper_trading/operations/dashboard.md`

## I004 Global Allocation Portfolios (historical expanded paper set)

P08_IEF30은 formal candidate이며 실제 자금 투입 대상이 아니다. 아래 9개 포트폴리오는 paper NAV만 추적한다.

P08_IEF30 frozen status:
- Frozen weights: SPY 29 / QQQ 21 / H001 20 / IEF 30.
- Quarterly rebalance + 0pp no-trade band.
- HIFO + 250만원 annual exemption.
- MIX1 practical shadow = V1 taxable 50% + ISA 30% + 연금 20%.
- No new weights grid, no direct sleeve addition, and no macro gate.
- `I002` remains on hold.

| Group | Portfolio | Target weights |
|---|---|---|
| Primary | P08_IEF30 | SPY 29 / QQQ 21 / H001 20 / IEF 30 |
| Challenger | P08 | SPY 40 / QQQ 30 / H001 20 / IEF 10 |
| Challenger | P07 | QQQ 50 / H001 30 / IEF 20 |
| Challenger | P07_IEF30 | QQQ 40 / H001 30 / IEF 30 |
| Benchmark | QQQ 100 | QQQ 100 |
| Benchmark | SPY 100 | SPY 100 |
| Benchmark | QQQ/SPY 50/50 | QQQ 50 / SPY 50 |
| Benchmark | H001 | H001 100 |
| Benchmark | IEF | IEF 100 |

분기 signal 산출:

```bash
.venv/bin/python scripts/global_portfolio_quarterly_signal.py --quarter YYYY-Q --as-of YYYY-MM-DD
```

산출 위치: `paper_trading/signals/global_YYYY-Q.json`

각 portfolio별 기록 항목:
- quarterly rebalance target weights
- KRW NAV tracking
- component NAV: SPY / QQQ / IEF 가격과 H001 NAV
- USDKRW 환산 정보
- 실제 매매는 paper only (NAV 만 계산)

사용자 가이드:
- 실제 자금 투입은 아직 X.
- 4 분기 이상 paper NAV 일치 시 cash deployment 여부를 별도 결정.

## N-family stress diversifier backlog

N-family is a partial hedge library, not a free lunch. It does not modify
P08_IEF30 and does not affect the four primary P08_IEF30 paper tracking NAVs.

Rules:
- P08_IEF30 remains frozen during N-family research.
- N-family results are backlog candidate library entries only.
- No new best-Sharpe search.
- Live deployment decisions must combine 4 quarters of paper tracking, tax
  confirmation, and N-family stress validation.

## 4 NAV tracking (T-family complete)

P08_IEF30은 아래 4개 버전으로 동시 추적한다.

| Version | Definition |
|---|---|
| Gross P08_IEF30 | 연구 기준 세전 NAV |
| V1 taxable P08_IEF30 | 해외 ETF 직접, HIFO + 250만원 공제 + 양도세 22% |
| MIX1 practical shadow | V1 50% + ISA 30% + 연금 20%, 단순함 우선 |
| V4 pension-only shadow | 연금저축 100%, withdrawal tax 반영, lock-up 가정 |

T-family best practice:
- HIFO + 250만원 공제 = default taxable-lot 가정
- Quarterly rebalance = operational default
- No-trade band = X
- TLH = trending bull sample에서 효과 작음
- Account/vehicle = 가장 큰 implementation lever

세무 전문가 확인은 live 전 필수다.

## T007 Broker Comparison

T007-lite broker comparison is template-ready. It is not broker-data complete.
All actual broker fee, FX, product-lineup, tax-report, fractional-trading, and
order-function information must be collected by the user host from official
broker sources and rechecked immediately before live deployment.

References:
- Broker comparison template: `docs/t007_broker_comparison.md`
- Broker selection guide: `docs/broker_selection_guide.md`
- User host worksheet: `paper_trading/operations/broker_research_worksheet.md`

Priority for P08_IEF30 / MIX1:
- MIX1 requires V1 taxable 50%, ISA 30%, and pension 20% operation.
- FX spread is the largest broker cost to verify.
- Tax-report quality means HIFO support or clean manual lot handling plus KRW
  2.5 million annual exemption handling.

## Defensive Shadow Candidates (N-family)

The four primary NAV versions above remain unchanged. The following N-family
variants are added as shadow-only defensive candidates for forward tracking:

| Candidate | Definition | Status |
|---|---|---|
| N002-B | `P08_IEF30` + cash 10%, proportionally reduced from SPY / QQQ / H001 / IEF | Shadow only, live X |
| N001-B | `P08_IEF30` + GLD 10%, proportionally reduced from SPY / QQQ / H001 / IEF | Shadow only, live X |

Weights:

| Candidate | SPY | QQQ | H001 | IEF | Cash | GLD |
|---|---:|---:|---:|---:|---:|---:|
| N002-B | 26.1% | 18.9% | 18.0% | 27.0% | 10.0% | 0.0% |
| N001-B | 26.1% | 18.9% | 18.0% | 27.0% | 0.0% | 10.0% |

Purpose:
- Four-quarter forward tracking only.
- Confirm whether defensive candidates are superior in stress periods.
- No live deployment and no `P08_IEF30` weight change during tracking.

## O-family operations tooling

| Ticket | Command / function | Output |
|---|---|---|
| O000 | `src.ops.nav_update.compute_daily_nav(portfolios, as_of_date)` | `paper_trading/operations/nav_history/` |
| O001 | `src.ops.gross_tax_nav.compute_gross_tax_nav(p08_ief30, as_of_date)` | `paper_trading/operations/nav_history/` |
| O002 | `src.ops.tax_ledger.compute_tax_ledger(as_of_date)` | `paper_trading/operations/tax_ledger/` |
| O003 | `src.ops.rebalance_report.generate_rebalance_report(quarter)` | `paper_trading/operations/rebalance_reports/` |
| O004 | `src.ops.drift_alert.compute_drift_alerts(as_of_date)` | `paper_trading/operations/drift_alerts/` |
| O005 | `src.ops.quarterly_evaluation.generate_quarterly_evaluation(quarter)` | `paper_trading/operations/` |

Sample local run:

```bash
.venv/bin/python -m src.ops.nav_update
.venv/bin/python -m src.ops.gross_tax_nav
.venv/bin/python -m src.ops.tax_ledger
.venv/bin/python -m src.ops.rebalance_report
.venv/bin/python -m src.ops.drift_alert
.venv/bin/python -m src.ops.quarterly_evaluation
```

The sample run uses only local data and does not modify D013, H001, or `src/backtest/engine.py`.

## 분기 운영 절차

### 1. 분기말 신호 산출 (분기말 거래일 장 마감 후, T 일)

```bash
.venv/bin/python scripts/quarterly_signal_generator.py --refresh-d013 --quarter YYYY-Q
```

신호 산출:
- regime_on, top 5 tickers (D013)
- regime_off_sleeve = "KR_short_rate_carry" (H001 champion)
- kr_rate_source = "FRED IR3TIB01KRM156N"
- estimated_quarter_carry (분기 carry 추정값)

### 2. 실거래 체결 (T+1 거래일)

**ON 분기 (regime_on = true)**:
- 매수: signals/YYYY-Q.json 의 5 종목 each 20%
- 시가 매수 (시장가 금지)
- 슬리피지 / participation rate ≤ 5% / VWAP/TWAP 권장

**OFF 분기 (regime_on = false)**:
- KR short-rate carry sleeve 매수
- 1순위: MMF / CMA (가장 실전적)
- 2순위: KOFR ETF (예: KODEX KOFR금리 액티브 합성)
- 3순위 reference: 단기채 ETF

### 3. 체결 기록 (executions/YYYY-Q.json)

```json
{
  "quarter": "YYYY-Q",
  "execution_date": "YYYY-MM-DD",
  "regime_state": "on or off",
  "primary_h001": {
    "fills": [...],
    "implementation_shortfall_bps": ?
  },
  "shadow_d013_original": {
    "off_return": 0.0 (cash) or actual cash carry
  },
  "shadow_h005_basket": {
    "off_returns": {"kr_carry": ?, "usdkrw": ?, "treasury": ?}
  }
}
```

### 4. 분기말 평가 (evaluations/YYYY-Q.md)

3 버전 누적 수익 비교:
- D013 original
- H001 primary
- H005 shadow

OFF 시기:
- KR carry MMF/CMA 실제 수익 vs FRED proxy 차이
- KOFR ETF 실제 수익 vs proxy 차이
- 어느 구현이 가장 가까운가

ON 시기:
- 5 종목 IS / slippage
- Cash fallback 이벤트

### 5. 4 분기 누적 후 평가 → Live pilot 결정

docs/live_pilot_criteria.md 의 10 go/no-go criteria.
3 버전 중 H001 이 primary, H005 가 shadow reference.

Pilot 1 진입 시 carrier = H001 (KR carry sleeve), AUM ≤ 10억 원.

## Quarter list

| Quarter | Status |
|---|---|
| 2026-Q1 | D013 ON, 5 종목 매수 (paper trading 시작) |
| 2026-Q2 | 6월말 신호 산출 예정 (OFF 이면 H001 KR carry sleeve) |
| 2026-Q3 | 9월말 |
| 2026-Q4 | 12월말 |
| 2027-Q1 | 3월말 → 4 분기 누적 평가 |

## 주의

- 사후 신호 수정 금지
- 임의 종목 추가/제거 금지
- D013 regime OFF 시 cash 가 아닌 KR carry sleeve 보유 (H001 champion)
- H005 shadow 는 paper 만 (실거래 X)
- AUM 단계 docs/aum_progression.md 준수
