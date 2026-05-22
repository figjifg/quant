# T007-lite Broker Comparison Template

Status: TEMPLATE READY. User host collection is pending.

This document is a framework only. Broker fees, FX spreads, tax-report
features, order types, and promotional events change often. All broker
information below must be collected directly by the user host from official
broker pages, terms, and fee notices, then rechecked immediately before any
live deployment.

## Target Brokers

- 한국투자증권
- 미래에셋증권
- 키움증권
- 토스증권
- NH투자증권
- 삼성증권
- KB증권

## Comparison Table

Fill every blank from broker official sources only. Do not infer values from
blogs, community posts, or old screenshots.

| Broker | 해외 ETF 수수료 | 환전 spread | 자동환전 | HIFO 지원 | 소수점 매매 | ISA 가능 | 연금 가능 | IRP 가능 | VWAP/예약주문 | 세금 리포트 |
|---|---|---|---|---|---|---|---|---|---|---|
| 한국투자증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| 미래에셋증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| 키움증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| 토스증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| NH투자증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| 삼성증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |
| KB증권 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 | 사용자 host 직접 수집 후 채움 |

## Field Definitions

- 해외 ETF 수수료: US-listed ETF order commission, including online/offline
  differences, minimum commission, and event/promotion period. Lower is better,
  but promotion expiry must be recorded.
- 환전 spread: USD/KRW conversion spread or preferential exchange-rate terms.
  Record the normal rate, event rate, eligibility condition, and expiry. This
  is the most important explicit cost item for P08_IEF30 operations.
- 자동환전: Whether USD can be bought automatically at order execution or
  settlement, and whether the execution FX rate is transparent.
- HIFO 지원: Whether the broker supports high-in-first-out lot selection or a
  functionally equivalent tax-lot method. If not supported, record whether the
  user can manually export lots and process HIFO outside the broker.
- 소수점 매매: Whether fractional US ETF trading is available, and whether it
  supports the target ETF set such as SPY, QQQ, and IEF.
- ISA 가능: Whether the broker supports a brokerage-type ISA suitable for the
  MIX1 ISA sleeve. US-listed ETFs are generally not the ISA target; record
  domestic-listed US ETF availability separately.
- 연금 가능: Whether pension-savings accounts can buy domestic-listed US equity
  and Treasury ETF substitutes for the MIX1 pension sleeve.
- IRP 가능: Whether IRP account lineup is broad enough for domestic-listed US
  equity and Treasury ETF substitutes, including risky-asset limits.
- VWAP/예약주문: Whether the broker supports VWAP-like execution, scheduled
  orders, recurring orders, or order reservation functions that reduce manual
  execution risk.
- 세금 리포트: Whether reports separate capital gains and dividends, expose lot
  history, apply or show the KRW 2.5 million annual overseas capital-gain
  exemption, and are usable for tax filing.

## P08_IEF30 Operating Priorities

P08_IEF30 practical implementation tracks MIX1: V1 taxable 50%, ISA 30%, and
pension 20%. A single broker is operationally attractive only if it can support
all required account types and the needed ETF substitutes. If not, a multi-
broker setup may be cleaner.

Quarterly rebalance turnover is expected to be near 2%, so commission drag is
relatively small. FX spread is the more important cost: in T-family sensitivity,
FX spread of 10 bps corresponds to approximately -0.6 percentage points over
16 years.

Tax-report quality is operationally critical. For the V1 taxable sleeve, the
minimum acceptable standard is either broker-side HIFO and KRW 2.5 million
annual exemption handling, or clean export files that allow the user to process
HIFO and the exemption manually.

Live-readiness note: broker information must be reconfirmed immediately before
live deployment because fees, events, product lineups, tax reports, and order
features change frequently.
