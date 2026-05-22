# J001 Static EM Diversifier

Status: BACKLOG (after J000)

## Purpose

Test whether a small static J-family sleeve improves stress behavior for
`P08_IEF30` while reducing US concentration.

EM is a risk asset, not a stress hedge. The strict budget is intended to avoid
optimizing into unstable country exposure.

## Pre-registered Candidates

| Candidate | Definition |
|---|---|
| J001-A | `P08_IEF30` + VWO 5% |
| J001-B | `P08_IEF30` + VWO 10% |
| J001-C | `P08_IEF30` + EWJ 5% |
| J001-D | `P08_IEF30` + EWJ 10% |
| J001-E | `P08_IEF30` + EWY 5% |
| J001-F | `P08_IEF30` + EWY 10% |

Sleeves are funded by proportional reduction from SPY / QQQ / H001 / IEF.
J001-E and J001-F must explicitly note possible double exposure with the H001
Korea sleeve.

## Common Settings

- 2010-2026 daily NAV using H001.
- Quarterly rebalance.
- Gross NAV, no tax model.
- KRW conversion using local USDKRW interpolation.
- Four stress windows from the N000 framework.
- Compare against `N002-B` cash, `N001-B` GLD, and `K001-B` XLP.

## Guardrails

- No additional EM ETFs.
- No weight grid beyond the six registered candidates.
- No direct `P08_IEF30` promotion.
- Existing D013, H001, `P08_IEF30`, and engine code remain frozen.
