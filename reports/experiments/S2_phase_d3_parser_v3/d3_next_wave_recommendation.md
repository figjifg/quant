# D3 Next Wave Recommendation (v3)

Date: 2026-05-23 15:07:06

## D3a v3
- denominator: 36 | ok rate: 100.0% | manual_review: 100.0%

## D3b v3
- denominator: 17 | ok rate: 82.4% | manual_review: 100.0%

## Honest assessment
- D3b shares regression: PARTIALLY FIXED (v1 29.4% → v3 5.9%)
- D3b event_date: STILL 0% (v2 0.0% → v3 0.0%)
- D3a field rates: see delta report — track v2 → v3 deltas per field
- manual_review_required still high (D3a 100.0% / D3b 100.0%); parser remains NOT strategy-ready

## Open options for Referee
- (a) Approve D3c full implementation
- (b) Continue D3a/D3b tuning (deeper per-ACODE manual audit, conversion request body-text parser, HTML inline dedicated branch)
- (c) Larger-sample integration smoke test (e.g., 500 disclosures)
- (d) Hold and proceed to C2/C3 integration design
- (e) Other narrowing

Executor offers no recommendation; defers to Referee.

## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready