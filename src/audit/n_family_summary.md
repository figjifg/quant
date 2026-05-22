# N-family Summary

Status: memory note for future audit work.

## Scope

N-family covered six tickets:

- N000 stress diversifier baseline.
- N001 gold sleeve.
- N002 cash / SHY sleeve.
- N003 duration mix.
- N004 commodity / dollar sleeve.
- N005 multi-stress comparison.

All N-family work is a partial hedge library, not a direct `P08_IEF30`
replacement path.

## Main Finding

No candidate delivered a free lunch. The strongest candidates improved some
stress windows, but no variant improved return and drawdown across every
stress window simultaneously.

## Defensive Shadow Candidates

- N002-B: `P08_IEF30` + cash 10%, funded by proportional reduction from SPY /
  QQQ / H001 / IEF.
- N001-B: `P08_IEF30` + GLD 10%, funded by proportional reduction from SPY /
  QQQ / H001 / IEF.

These two are approved for paper tracking as defensive shadows only. They are
not live allocations and do not modify frozen `P08_IEF30`.

## Trade-offs

- N002-B ranked best in the N005 multi-stress comparison by MDD-first scoring,
  but still reduced dot-com proxy return.
- N001-B was a credible GLD 10% shadow, especially for GFC / COVID / 2022
  stress, but dot-com coverage used a proxy because GLD history was missing.
- Long-duration Treasury exposure, especially TLT-heavy variants, confirmed
  material 2022 rate-shock risk.
- Commodity / dollar variants helped 2022 in places but did not provide a
  complete all-stress answer.

## P08_IEF30 Frozen Justification

`P08_IEF30` remains frozen because N-family produced defensive candidates, not
a robust replacement. The correct next step is forward paper tracking of N002-B
and N001-B alongside the existing four P08_IEF30 NAV versions.

## Next Priority Framework

- K-family: first priority, strict-budget US sector sleeve diagnostic.
- J-family: second priority.
- L-family: third priority.
- M-family: lowest-priority backlog.

K-family starts as diagnostics and candidate-library work only. It is not a
primary allocation change.
