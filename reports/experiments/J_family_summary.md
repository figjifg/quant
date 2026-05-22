# J-family Summary

Status: GENERATED FROM J000-J002 REPORT FILES

## Scope

- J-family tested EM and EM-adjacent equity exposure only: VWO, EWY, EWJ, EWZ, MCHI.
- All runs used local data only, KRW conversion with local USDKRW interpolation, and gross NAV.
- `D013`, `H001`, `P08_IEF30`, and `engine.py` were not modified.
- J-family is a backlog candidate library. No `P08_IEF30` direct promotion is made.

## J000 Baseline

Full-sample KRW buy-and-hold results:

| ETF | CAGR | Sharpe | MDD | SPY corr |
|---|---:|---:|---:|---:|
| VWO | 0.088566 | 0.608799 | -0.501732 | 0.792262 |
| EWY | 0.114122 | 0.508187 | -0.571679 | 0.589786 |
| EWJ | 0.050711 | 0.275804 | -0.566732 | 0.704135 |
| EWZ | 0.077149 | 0.291887 | -0.738305 | 0.592942 |
| MCHI | 0.046253 | 0.200805 | -0.528265 | 0.515081 |

Finding: EM/country ETFs reduce US concentration mechanically, but full-sample
drawdowns are large. EWY had the highest CAGR in J000, while EWZ had the
deepest drawdown.

## J001 Static Sleeve

Best J001 full-history CAGR was J001-F at 0.127874, but its MDD was -0.178344.
The best J-family stress ranking inside J001 was J001-D, with average stress
delta vs `P08_IEF30` of -1.057280pp return and +0.043394pp MDD.

Comparator ranking from `J001_static_em_diversifier/metrics.json`:

| Rank | Variant | Family | Return score pp | MDD score pp |
|---:|---|---|---:|---:|
| 1 | N002-B | N002 | -0.449441 | 1.621524 |
| 2 | N001-B | N001 | 1.824415 | 0.714920 |
| 3 | K001-B | K001 | -0.190103 | 0.604488 |
| 4 | J001-D | J001 | -1.057280 | 0.043394 |
| 5 | J001-C | J001 | -0.531889 | 0.021801 |

Finding: static EM/Japan/Korea sleeves did not beat the N-family diversifiers
or K001-B. EWJ 10% was the least weak J001 stress candidate, but its return
tradeoff was still worse than K001-B and N-family alternatives.

## J002 Momentum

J002-A failed all J003 validation gates:

| Gate | Result |
|---|---|
| Return + MDD + Sharpe all better than `P08_IEF30` | false |
| Four stress windows all improved | false |
| No 2025 spike dependency | false |
| Subperiods all superior | false |
| Promotion pass | false |

Full-history J002 metrics:

| Variant | CAGR | Sharpe | MDD |
|---|---:|---:|---:|
| J002-A | 0.098328 | 0.921498 | -0.202372 |
| J002-B | 0.065900 | 0.603830 | -0.258290 |
| J002-C | 0.053131 | 0.342626 | -0.390476 |
| P08_IEF30 | 0.127294 | 1.174390 | -0.164077 |

Combined N/K/J stress ranking placed J002 variants at the bottom:

| Rank | Variant | Family | Return score pp | MDD score pp |
|---:|---|---|---:|---:|
| 1 | N002-B | N-family | 0.446445 | 2.283723 |
| 2 | N001-B | N-family | 1.554226 | 1.494456 |
| 6 | K001-B | K001 | -0.190103 | 0.604488 |
| 21 | J002-A | J002 | -15.270864 | -17.560542 |
| 22 | J002-B | J002 | -15.700464 | -17.849211 |
| 23 | J002-C | J002 | -21.196356 | -23.486151 |

## Sector vs EM Diversifier

K-family defensive sector exposure was materially better than J-family EM
equity exposure for this role. K001-B had positive average MDD improvement
against `P08_IEF30` across the stress matrix, while J001 variants were at best
near-flat on MDD and negative on return. J002 momentum increased equity risk
and did not act as a stress diversifier, especially in dot-com/GFC proxy
windows and 2022.

## Verdict

- Best J variant: J001-D as the least weak stress diagnostic candidate.
- Highest-return J static candidate: J001-F, but it worsened drawdown and is
  not the selected stress candidate.
- J002 promotion: failed.
- J-family verdict: backlog only.
- Ranking conclusion: N-family remains ahead of K-family, and K-family remains
  ahead of J-family for diversifier use.
- Next recommendation: proceed only if a new L/M family ticket is explicitly
  registered; do not revise J-family parameters without a new ticket.
