# L000 Live Pilot Go/No-Go Pack

Status: ACTIVE decision pack.

## Purpose

Define the small live pilot decision framework for `P08_IEF30` without
changing weights, strategy code, or research conclusions.

## Pilot Amount Framework

Pilot amount: 10-30% of total target assets.

Use the lower end when broker, tax-lot, or paper/live tracking processes are
new. Use the upper end only after the order procedure, tax tracking, and NAV
reconciliation are operationally ready.

## Order Procedure

Use `docs/u000_live_deployment_playbook.md` as the operating playbook.

Required before first order:

- Account NAV locked.
- Target sleeve amounts calculated from frozen `P08_IEF30` weights.
- Limit-order plan prepared.
- FX and settlement assumptions recorded.
- HIFO tax-lot tracking initialized.

## Stop Conditions

Use `docs/u002_drawdown_acceptance_memo.md` as the drawdown behavior memo.

Stop new funding and escalation if any of the following occur:

- Data error prevents target NAV or target weight calculation.
- Tax-lot tracking fails.
- Rule-violating order occurs.
- Account constraints prevent target sleeve replication.
- Unexplained paper/live NAV divergence exceeds the threshold below.

## Paper/Live Divergence

Paper/live divergence threshold: NAV 5% 초과.

If live NAV diverges from paper NAV by more than 5% and the difference is not
explained by fees, FX, taxes, timing, or product mapping, the pilot goes to
hold/review.

## Tax Lot Tracking

- Track tax lots from the first fill.
- Default lot policy follows the live deployment playbook.
- Record realized gain/loss, FX rate, commission, withholding, and tax basis.
- No discretionary sale is allowed without a tax-lot impact record.

## Go/No-Go Checklist

- `P08_IEF30` frozen weights confirmed.
- D013/H001 regression status reviewed.
- Broker order process tested.
- Tax-lot sheet ready.
- Drawdown memo accepted.
- Paper/live reconciliation process ready.
- Initial pilot size selected within 10-30%.
- No unresolved data integrity blocker.

## Post-pilot Framework

After the pilot window, choose one:

- Increase: order process clean, tax tracking clean, paper/live divergence
  within threshold, and no rule breach.
- End: persistent operational blocker, unacceptable divergence, or inability
  to replicate sleeves.
- Hold: evidence is incomplete or a regression remains open.
