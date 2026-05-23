# D3 Next Wave Recommendation

Date: 2026-05-23 14:25:06

## D3a checkpoint result
- denominator: 36
- parser_status=ok rate: 100.0%
- manual_review_required rate: 100.0%

## D3b checkpoint result
- denominator: 17
- parser_status=ok rate: 82.4%
- manual_review_required rate: 100.0%

## Honest assessment of this checkpoint

This is the **first-pass D3 parser checkpoint**. The results split cleanly into two layers:

**Infrastructure layer = WORKING**
- Response-type dispatcher (dart_xml_structured / html_inline / tiny) classifies correctly
- DART3 / DART4 schema detection works
- Charset handling works
- attachment_only is excluded from denominator (Referee requirement)
- manual_review_required flagging works (NOT bypassed anywhere)
- parser_confidence calculation works (no unsupported high values; 100% of D3a rows at ≤ 0.67)
- Correction linkage algorithm works end-to-end (1 successful link demonstrated: 전환청구권행사 정정 → original at 5-day gap)
- D3c skeleton handles 54 out-of-scope rows without false claims
- PIT lock works (rcept_no + rcept_date populated on every parsed row)

**Precision layer = INSUFFICIENT**
- Field extraction rate: 5.6% amount, 2.8% shares, 2.8% event_date (D3a)
- Confidence mean: 0.037 (D3a) / 0.147 (D3b); max 0.667
- 100% rows tagged manual_review_required — by design when any required field is missing
- Root cause: current label-keyword map assumes the 1st `<TD>` of each `<TR>` is the label and remaining cells are values. DART body tables frequently use **multi-row layouts** (column headers in row 1, row headers in column 1, values in inner cells) and **nested tables** that the current single-row TH/TD heuristic does not reach. Many forms also place the key numeric fields in `<TBODY>` blocks with merged-cell column headers above.

This pattern is exactly what Referee's "amount/shares/date unit normalization failure → wave partial" kill gate is meant to surface. The kill gate has NOT triggered because units ARE normalized correctly when values are extracted; the bottleneck is upstream — label discovery, not unit conversion.

## Recommendation (executor's view, Referee decides)

**Strong recommendation: option (b)** — Require D3a/D3b precision tuning before D3c full implementation.

Specifically, tuning should:
1. Replace single-row TH/TD heuristic with multi-row label-discovery (column header + row header join, nested-table flatten)
2. Build per-ACODE field maps (e.g., ACODE 11332 = 자기주식취득결정 — exact TH labels enumerated from D2 schema inventory)
3. Manual audit pass on 30 samples per D3a/D3b base form to validate extraction precision
4. Re-run D3 checkpoint with the same Referee-required outputs to compare

D3a/D3b precision tuning is expected to be a 2-3 round iteration; current first-pass result is not a kill-gate breach but it is also not strategy-ready (which is correct — no parser result is described as strategy-ready in any output of this checkpoint).

## Open options for Referee

- (a) Approve D3c full implementation **NOT RECOMMENDED** by executor given current D3a/D3b precision
- **(b) Require D3a/D3b precision tuning round before D3c — RECOMMENDED**
- (c) Require integration smoke test against larger sample (500+ disclosures) before any precision tuning
- (d) Hold D3 at current state and proceed to C2/C3 integration design (NOT recommended — D3 precision is the lever)
- (e) Other narrowing or hold

## Compliance reaffirm
- No strategy testing, no return outcome, no parser-strategy-ready claim
- End condition for current step = D3a/D3b parser A0 checkpoint only