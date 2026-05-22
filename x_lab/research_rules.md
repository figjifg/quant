# X-Lab Research Rules

X-Lab is quarantined. The P08 production track remains frozen.

## A0 Audit Gate

Every strategy must be registered before research and must pass the A0 audit
framework before moving to scans.

The A0 audit covers:

1. data lineage
2. point-in-time availability
3. survivorship safety
4. corporate action handling
5. calendar / tradability
6. daily NAV
7. no implicit leverage
8. benchmark alignment
9. random / placebo control
10. concentration / top contributor audit
11. cost / tax / turnover
12. capacity / execution

A0 fail means diagnostic only: no production claim, no paper candidate, and no
P08 import.

## Import Gate

No X-Lab result affects `P08_IEF30` unless all of the following are true:

- `X030` deep validation PASS
- `X040` paper-eligibility PASS
- user / research director approval
- a separate import review ticket, such as `M000`, explicitly approves P08
  import consideration

Until then, all X-Lab outputs are sandbox artifacts.
