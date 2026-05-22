# Broker Selection Guide

Status: framework only. User host broker research is pending.

This guide is for selecting a broker setup for P08_IEF30 and MIX1 operations.
It does not contain verified broker-specific facts. All concrete broker data
must be filled by the user host from official broker sources and rechecked
immediately before live deployment.

## Objective

P08_IEF30 practical operation uses MIX1:

- V1 taxable: 50%
- ISA: 30%
- Pension: 20%

The broker setup should minimize operational errors, FX cost, and tax-report
friction while supporting the required account vehicles.

## Mandatory Conditions

A broker or broker combination must satisfy all mandatory conditions before
being considered live-ready:

- Overseas ETF trading is available for instruments such as SPY, QQQ, and IEF.
- FX conversion is automatic or available at a reasonable, documented spread.
- HIFO lot accounting is supported, or the user can manually process lots from
  clean export files.
- Tax reports separate overseas capital gains and dividends.
- Tax reports either apply the KRW 2.5 million annual overseas capital-gain
  exemption or provide enough detail for the user to apply it manually.

## Recommended Conditions

These are not strict blockers, but they improve execution quality and reduce
manual work:

- Brokerage-type ISA support for domestic-listed US ETF substitutes.
- Pension-savings and IRP support with domestic-listed US equity and Treasury
  ETF lineups.
- Fractional trading for rebalance precision.
- VWAP, scheduled order, recurring order, or reservation order support for
  slippage control.
- Quarterly automatic alerts or reports.

## Broker Combination Framework

### 1 Broker Integrated Setup

Use one broker when a single platform can support V1 taxable, ISA, pension, and
IRP requirements with acceptable FX, tax reports, and order tools.

Candidate category: broad-service brokers such as 한국투자증권, 미래에셋증권,
삼성증권, or similar. This is a category note only; exact capability must be
confirmed by the user host.

Advantages:
- Simple operations.
- One tax and reporting workflow.
- Lower transfer and monitoring complexity.

Risks:
- One broker may be weaker in FX spread, product lineup, tax reporting, or
  order tools.
- Promotion/event terms may expire and change the cost profile.

### Multi-Broker Setup

Use multiple brokers when each account sleeve has a different best platform:

- V1 taxable: overseas direct ETF broker with strong FX and tax-lot reporting.
- ISA: broker with strong brokerage-type ISA and domestic-listed US ETF lineup.
- Pension/IRP: broker with strong pension ETF lineup and account operations.

Advantages:
- Better fit per account vehicle.
- Potentially lower FX and better product coverage.
- Taxable sleeve can prioritize HIFO and tax-report quality.

Risks:
- More operational work.
- More reconciliation across NAV, tax reports, and rebalance targets.
- More chances for account-level drift.

## Cost Sensitivity

Use the following T-family operating assumptions when comparing broker setups:

- Commission: 0.25% default total trading-cost proxy where needed.
- FX spread scenario: 10 bps.
- Total annual cost assumption: 0.6% per year.

For P08_IEF30, quarterly rebalance turnover is expected to be near 2%, so
commission differences are less important than FX spread and tax-report
quality. The T-family sensitivity note is that 10 bps of FX spread corresponds
to approximately -0.6 percentage points over 16 years.

## Live Readiness Rule

Broker selection is not final until the user host rechecks official broker
sources immediately before live deployment. Fees, FX spreads, promotional
events, product lineups, tax reports, fractional trading, and order functions
can change without warning.
