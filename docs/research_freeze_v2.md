# Research Freeze v2

## Mission

Official mission:

> Global after-tax allocation quant system with Korean macro sleeve and stress-aware defensive shadow tracking

The project is now in deployment preparation. Q-family is closed. R-family
title-based diagnostics are closed. S-family is CLOSED_DIAGNOSTIC_ARTIFACT.
X-Lab ETF track is closed. W001 repairs Korean equity backtest infrastructure;
S001-G is allowed once after W001 only as corrected smoke test infrastructure
QA, alpha X.

Audit-first framework 5/5 catches:
- Q-family survivor artifact
- R-family title fail
- S-family measurement artifact
- X-ETF001 momentum < fixed
- X-ETF900 dynamic < simpler

Korean alpha + US fundamental + ETF tactical 모두 fail/marginal.
P08_IEF30 + N-family = only robust framework.

## Frozen Primary

Primary production candidate:

| Portfolio | SPY | QQQ | H001 | IEF |
|---|---:|---:|---:|---:|
| P08_IEF30 | 29% | 21% | 20% | 30% |

Rules:

- `P08_IEF30` is fixed as the primary paper/live candidate.
- The frozen implementation is SPY 29 / QQQ 21 / H001 20 / IEF 30.
- Do not modify D013, H001, P08_IEF30 strategy code, or `src/backtest/engine.py` as part of deployment prep.

## Defensive Shadows

The defensive shadows are tracked for forward evidence only:

| Shadow | Definition | Status |
|---|---|---|
| N002-B | P08_IEF30 with 10% cash, other sleeves scaled down | Defensive shadow |
| N001-B | P08_IEF30 with 10% GLD, other sleeves scaled down | Defensive shadow |

The shadows do not replace the primary candidate and are not a free lunch claim.

## Family Register

| Family | Freeze status |
|---|---|
| D-family | `D013` is the Korea macro sleeve carrier. |
| E-family | `E014` sector snapshot failed point-in-time validation and is demoted. |
| F-family | Stock ranking produced a null result. |
| G-family | Slow overlay produced a null result. |
| H-family | `H001` is the Korean sleeve champion: D013 ON = Korean top 5, OFF = KR carry. |
| I-family | `P08_IEF30` is the formal candidate after `I003.6`, with GFC warning retained. |
| T-family | HIFO + KRW 2.5M exemption + MIX1: V1 50%, ISA 30%, pension 20%. |
| O-family | Operations tooling automation is complete. |
| N-family | Cash and gold are defensive shadows, not free-lunch replacements. |
| K-family | Sector defensive work is backlog; sector momentum is rejected. |
| J-family | EM static work is backlog; EM momentum is rejected as catastrophic. |
| Q-family | CLOSED. Direct Q is production closed due to survivorship bias; ETF proxy improvement was marginal and is not added to paper tracking. |
| R-family | CLOSED. Title-based Korean shareholder-return disclosure buckets failed the standalone promotion gate. |
| S-family | CLOSED_DIAGNOSTIC_ARTIFACT. S000 strong result = measurement artifact. |
| X-Lab ETF track | CLOSED. V10 marginal diagnostic only; dynamic ETF rotation failed versus simpler N-family shadows. |
| W001 | ACTIVE Korean equity backtest engine repair; infrastructure, alpha X. |
| V001 | ACTIVE P08 Korean sleeve data integrity regression; no re-optimization. |
| L000 | ACTIVE small live pilot go/no-go pack. |

## Freeze Meaning

Research Freeze v2 means:

- Q-family is closed unless survivorship-safe historical constituent data is secured.
- R-family title-based strategy is CLOSED as diagnostic.
- X-Lab ETF track is CLOSED; no X030, no paper tracking, no P08 import, and no
  P08 weight change.
- 새 alpha family expansion X. S-family is closed as measurement artifact.
- No new weights grid, sleeve search, macro gate, sector momentum, EM momentum, or crypto promotion work is authorized.
- Result interpretation remains separate from engineering output.

## Q-family Closure

Final Q-family decision:

> Q-family CLOSED. Direct Q = production closed (survivor bias). ETF proxy = marginal (+0.01 Sharpe).
> Paper tracking 에 ETF 추가 X.
> R-family title-based: CLOSED as diagnostic.
> S-family 한다면 S000 feasibility diagnostic 만 (strict gate).
> Q-family 재개 = survivorship-safe data 확보 시.

Direct Q remains diagnostic only. ETF proxy sleeves are not added to paper
tracking.

## R-family Closure

R-family title-based diagnostics are closed. R000 OPENDART audit passed, but
R001-R004 failed the standalone gate. R005/R006 are skipped. R005-QA-lite is a
closure sanity check only (production X). R007 DART body parsing is backlog
only under specific reopen conditions.

Expression guardrail: title-based bucket failed, not all Korean retirement is
bad. Within tested simple frameworks, Korean standalone alpha has not passed
production gates.

## Korean Alpha Framework Update

Prior framework: short-horizon mean reversion = credible candidate.

Updated framework: measurement artifact under audit. Korean standalone alpha
다시 매우 어려움.

## Change Conditions

The freeze can be revisited only after one of the following:

- Four quarters of paper tracking are complete.
- A clear new data source or hypothesis is supplied in a ticket.
- The mission is explicitly redefined by the user.

Until then, forward work should preserve `P08_IEF30` as primary and track `N002-B` / `N001-B` as shadows only.
