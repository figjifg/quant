# X000 Project Charter

X-Lab is quarantined.

No result from X-Lab affects `P08_IEF30` unless it passes the Import Gate.

## Separation From P08

- X-Lab result -> no P08 weight change.
- X-Lab result -> no P08 paper tracking addition.
- X-Lab result -> no `production candidate` label.
- X-Lab result -> diagnostic only before audit gate pass.

The `P08_IEF30` production track is frozen. X-Lab is a sandbox where failure is
acceptable and expected.

## Import Gate

Import into the main project requires:

- `X030` deep validation PASS
- `X040` paper-eligibility PASS
- user / research director approval
- separate ticket, such as `M000`, for P08 import review

Passing a local X-Lab diagnostic does not itself authorize production use.

## Roles

Research director, user / GPT:

- chooses strategy candidates
- approves candidate pre-registration
- defines pass criteria and kill criteria
- approves any import gate review

Claude / Codex:

- runs backtests
- calculates metrics
- performs sanity checks
- records diagnostic outputs without production interpretation

## Meaning Of This Charter

`P08_IEF30` remains the frozen production track. X-Lab is a quarantined alpha
research lab and failed-strategy sandbox.
