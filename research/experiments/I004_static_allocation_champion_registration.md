# I004 — Static Allocation Champion Registration

Status: registered (formal candidate, NOT production deployment)

Candidate name: P08_IEF30 = SPY 29 / QQQ 21 / H001 20 / IEF 30

## Rationale

지피티 decision 그대로:

- Multi-metric score #1 (7점)
- Sharpe 1.172
- CAGR 12.7% (>= 12% 최소 기준)
- MDD -16.4%
- 2022 stress best (-14.6%, P07 -19.1% 대비 +4.5pp)
- COVID drawdown controlled (-16.4%)
- 2025 spike dependence low (-0.040, P07 -0.078 보다 작음)
- Rebalance frequency robust (monthly~annual Sharpe 차이 ±0.001)
- Clear economic structure: US broad/growth core + Korea macro satellite + Treasury diversifier

## Interpretation

- NOT merely grid-best Sharpe selection.
- I003.5 was pre-registered frontier validation.
- P08_IEF30 passed the multi-metric framework, not just Sharpe.

## Updated Rule

- Old rule "grid best cannot be final" remains valid for pure Sharpe picking.
- Multi-metric winner from pre-registered frontier testing may be promoted to formal candidate.
- Production deployment still requires additional validation.

## Known Limitations

- Long-history (2000-2002 dot-com, 2008 GFC) 미검증.
- IEF 30% duration risk.
- 2010-2026 US bull regime 의존성 미확인.
- H001 2010 이전 재현 X (Korea sleeve).
- 실제 세금/환전/배당 처리 미검증.
- ETF 거래 비용 / 분기 슬리피지 미검증.

## Pre-registered Production-final Gates

- I003.6 long-history US core stress 통과.
- I005 production-style validation (cost/FX/tax/execution).
- Paper tracking 4 분기 이상 NAV 일치.

## Comparison Table

| portfolio | weights | cagr | sharpe | max_drawdown | 2022_return | covid_mdd | 2025_spike_sharpe_delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P08_IEF30 | SPY29/QQQ21/H00120/IEF30 | 0.127384 | 1.172143 | -0.164077 | -0.146415 | -0.164077 | -0.040522 |
| P07 | QQQ50/H00130/IEF20 | 0.147724 | 1.210984 | -0.199070 | -0.191375 | -0.190961 | -0.077631 |
| P07_IEF30 | QQQ40/H00130/IEF30 | 0.131292 | 1.234846 | -0.178219 | -0.171102 | -0.162948 | -0.105858 |
| P08 | SPY40/QQQ30/H00120/IEF10 | 0.154328 | 1.109627 | -0.234285 | -0.170427 | -0.234285 | -0.009894 |
| QQQ | QQQ100 | 0.209756 | 1.003577 | -0.306440 |  |  |  |
| SPY | SPY100 | 0.159126 | 0.913187 | -0.296166 |  |  |  |
| H001 | H001100 | 0.097315 | 0.656752 | -0.339235 |  |  |  |

## Verdict

P08_IEF30 promoted to I004 formal static allocation champion candidate.
