# R-family Closure

Status: CLOSED as diagnostic.

## Overall verdict

R000 OPENDART audit passed: disclosure-date based PIT event study is feasible,
with the caveat that filing time is date-only and all trades are conservatively
entered at the next KRX trading-day open.
However, R001-R004 failed the standalone promotion gate. Simple title-based
Korean shareholder-return disclosures — buyback announcements, dividend increase
events, cancellation/retirement-related events, and composite shareholder-return
signals — did not show robust positive post-event drift versus KOSPI.
The only mildly positive result was R001 21d at +0.10% mean excess, but hit rate
was below 50%, longer holding periods were negative, and subperiod robustness was
absent. R003/R004 were negative or weak, and the 2022-2026 subperiod was broadly
negative.
R002 should be described carefully as a title-based cancellation/retirement-
related bucket unless true share-retirement-only labels are confirmed. The result
rejects the coarse title-based event bucket, not necessarily every possible
high-quality legal-retirement intensity signal.

## Production decision

- R-family title-based strategy CLOSED
- R005 cost validation skip (gross 이미 negative)
- R005-QA-lite 만 sanity check (production X)
- R006 portfolio combination skip (standalone gate 미통과)
- Paper tracking 추가 X
- R007 DART body parsing = backlog

## R007 reopen conditions

1. True retirement-only events 분리 가능
2. Buyback amount / market cap PIT parse 가능
3. Dividend amount / yield / increase rate parse 가능
4. Price-return vs total-return (dividend caveat) 처리
5. Size / liquidity / sector / market-cap matched control 가능
6. Pre-registered intensity-based hypotheses (broad keyword fishing X)
7. 사전 등록 (예: buyback ≥ 1-2% market cap, retirement ≥ 0.5-1%, dividend increase + high yield)

## Language guardrails

- 소각 실패 X, title-based bucket 실패 O.
- 한국 alpha 없음 X, tested simple frameworks 안에서 fail O.
- 다음 = P08_IEF30 4분기 paper tracking + deployment prep, 새 alpha X.
- S-family 한다면 S000 feasibility diagnostic 만 (strict gate).
