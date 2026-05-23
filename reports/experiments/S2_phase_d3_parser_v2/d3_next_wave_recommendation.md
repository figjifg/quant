# D3 Next Wave Recommendation (v2)

## D3a v2 result
- denominator: 36 | ok rate: 100.0% | manual_review: 100.0%

## D3b v2 result
- denominator: 17 | ok rate: 82.4% | manual_review: 100.0%

## Honest assessment
- v2 multi-strategy label discovery raises extraction rates above v1 baseline (see delta report)
- v2 still does NOT meet production strategy-ready bar; D3 remains an infrastructure repair phase
- Per-ACODE field-keyword hints are based on D2 sample observation, not exhaustive enumeration against DART XSD — further tuning rounds may be needed

## Open options for Referee
- (a) Approve D3c full implementation now
- (b) Additional D3a/D3b tuning round (deeper per-ACODE enumeration + manual-audit sampling) before D3c
- (c) Larger-sample integration smoke test (e.g., 500 disclosures) before D3c
- (d) Hold D3 and proceed to C2/C3 integration design
- (e) Other narrowing or hold

Executor offers no recommendation between (a)/(b)/(c)/(d) — defers to Referee given the residual precision uncertainty.

## Hard locks reaffirmed
- No strategy testing, no return outcome, no parser-strategy-ready claim
- End condition = D3 precision-tuning checkpoint only