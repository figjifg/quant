# Q-family Final Freeze

Status: CLOSED

Decision:

> Q-family CLOSED. Direct Q = production closed (survivor bias). ETF proxy = marginal (+0.01 Sharpe).
> Paper tracking 에 ETF 추가 X.
> R-family title-based: CLOSED as diagnostic.
> S-family 한다면 S000 feasibility diagnostic 만 (strict gate).
> Q-family 재개 = survivorship-safe data 확보 시.

## Scope

This freeze covers `Q000` through `Q008`, including `Q006.5` and `Q006.6`.

## Final Verdict

- Direct Q-family: production closed.
- ETF proxy path: marginal improvement only; no paper-tracking addition.
- Reopen condition: secure survivorship-safe historical constituent data.
- Next active family: NONE; paper tracking + deployment prep.
- S-family: optional only as S000 feasibility diagnostic with strict gates.

Production-grade edge currently comes from robust asset allocation, Korean macro/carry sleeve, tax-aware implementation, and stress-aware shadow tracking. New standalone alpha modules have not passed the gate.

## Honest Summary

US fundamental factor test found strong long-only performance in a survivor S&P100 universe, but failed to show robust cross-sectional factor premium.

Survivor universe and Mag 7/top contributor concentration explain much of the result.

ETF proxy improvement was marginal.

## Q000-Q008 Synthesis

| Ticket | Role | Freeze result |
|---|---|---|
| Q000 | US fundamental data audit gate | Diagnostic setup only; production use still requires PIT and survivorship-safe data. |
| Q001 | Universe construction | Current-survivor universe is not production-safe. |
| Q002 | Quality-only sleeve | Strong long-only result, but survivor bias prevents production use. |
| Q003 | Value-only sleeve | Diagnostic only; no robust production factor premium established. |
| Q004 | Shareholder-yield-only sleeve | Diagnostic only; no production promotion. |
| Q005 | Quality + value composite | Diagnostic only; no production promotion. |
| Q006 | Q + V + shareholder-yield composite | Best direct Q diagnostic path, but production closed due to survivor bias. |
| Q006.5 | Bias benchmark audit | Survivor universe, Mag 7, and top contributor concentration materially weaken the alpha claim. |
| Q006.6 | Factor ETF proxy benchmark | ETF proxy path is production-safer than direct survivor Q, but improvement is marginal. |
| Q007 | Cost and turnover validation | Sanity check only; does not reopen direct Q production. |
| Q008 | Portfolio combination | Best ETF proxy delta was about +0.01 Sharpe, not enough for paper tracking. |

## Direct Q Verdict

Direct Q is closed for production.

The direct Q tests are retained only as research diagnostics. They cannot be
used to promote a live or paper sleeve because the tested universe is a
survivor-biased S&P100-style universe. Without historical constituent
membership and delisting-safe data, direct Q results are not production
evidence.

## ETF Proxy Verdict

ETF proxy diagnostics using SCHD, COWZ, and MTUM are also closed for current
paper tracking.

The best observed portfolio-combination improvement was marginal, about
+0.01 Sharpe. That is not enough to add SCHD, COWZ, MTUM, or any Q-family ETF
proxy to paper tracking.

## Reopen Condition

Q-family can reopen only if survivorship-safe historical constituent data is
available and the ticket explicitly authorizes renewed Q-family work.

Until then:

- Do not reopen direct Q.
- Do not add ETF proxy Q sleeves to paper tracking.
- Do not modify `P08_IEF30`.
- Keep Q-family as a closed diagnostic archive.
