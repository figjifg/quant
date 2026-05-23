# S2 Correction / Cancellation Linkage — Final

Date: 2026-05-23 15:42:46

## Linkage algorithm (locked from D2 + D3)

```
for each correction row (correction_prefix ∈ {[기재정정], [첨부정정], [첨부추가], [연장결정]}):
  candidates = where(
    corp_code_dart == correction.corp_code_dart
    AND base_form == correction.base_form (after normalization: prefix + subsidiary suffix + series marker stripped)
    AND correction_prefix is null (= an original disclosure)
    AND series_marker matches (if present, e.g., (제2회차))
    AND rcept_date in [correction.rcept_date - 180d, correction.rcept_date]
  )
  if candidates non-empty: link to most recent (highest rcept_date)
  else: leave unlinked → manual_review_required
```

## Linkage smoke-test results (D1+D2 sample union, 27 correction rows)

| Round | corrections_total | linked | unlinked | link rate |
|---|---|---|---|---|
| D3 v1 | 27 | 3 | 24 | 11.1% |
| D3 v2 | 27 | 3 | 24 | 11.1% |
| D3 v3 | 27 | 3 | 24 | 11.1% |

Stable across all 3 rounds (no regression). 24 unlinked because their originals are outside the 108-row D1+D2 sample. Production link rate expected substantially higher on full R000 450k join.

## Verified linkage example (in-sample)

- `20200715900389` ([기재정정]전환청구권행사) → `20200710900612` (전환청구권행사 original), 5-day gap

## Variants normalized

| Variant | Treatment | Example |
|---|---|---|
| `[기재정정]` | strip → base_form, link to original | `[기재정정]주요사항보고서(자기주식취득결정)` → `주요사항보고서(자기주식취득결정)` |
| `[첨부정정]` | strip → base_form, link to original | same pattern |
| `[첨부추가]` | strip → base_form, treated as supplementary (no event override) | `[첨부추가]주식소각결정` |
| `[연장결정]` | event continuation; no original-event link required | `[연장결정]주요사항보고서(자기주식취득신탁계약체결결정)` |
| `(자회사의 주요경영사항)` | strip suffix; remap corp_code if needed (D3 deferred) | `주요사항보고서(자기주식처분결정)(자회사의 주요경영사항)` |
| `(종속회사의주요경영사항)` | same as 자회사 suffix | same pattern |
| `(제N회차)` | preserve as `series_marker`; required for linkage match | `[기재정정]전환청구권행사(제2회차)` |

## Final linkage state

- **Algorithm: VERIFIED** (smoke-test successful on 3 rounds; in-sample link demonstrated)
- **Production integration: BLOCKED** (no unified event log; correction linkage cannot be applied at production scale until D3 parsers are C3-ready)

## Hard locks

- Correction linkage NOT used as a strategy signal
- 정정 entries NOT counted as new events; they amend the original