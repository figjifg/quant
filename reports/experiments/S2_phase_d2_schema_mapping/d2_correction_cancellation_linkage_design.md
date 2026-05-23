# D2 Correction / Cancellation / Withdrawal Linkage Design

Per Referee D2 mandatory: correction / cancellation / amendment form normalization.

## Variant taxonomy

| Prefix / form | Meaning | Linkage required |
|---|---|---|
| `[기재정정]` | 본문 기재 정정 | YES → link to most recent non-corrected version of same (corp_code + base_form) |
| `[첨부정정]` | 첨부 정정 | YES (same as above) |
| `[첨부추가]` | 첨부 추가 | NO — supplement, original event intact |
| `[연장결정]` | 연장 결정 | NO — event continuation, no original-event reference |
| `철회신고서` | 철회 | YES → original event must be marked withdrawn |
| `취소공시` (e.g., 가족친화인증 취소) | 취소 | YES → original event marked cancelled |

## Linkage algorithm (D3 design)

```python
def link_correction(df_events):
    # 1. normalize report_nm → (correction_prefix, base_form, subsidiary_suffix, series_marker)
    # 2. for each correction_prefix row, find most recent prior row with:
    #    - same corp_code
    #    - same base_form (after strip)
    #    - same series_marker (if any)
    #    - rcept_date <= correction.rcept_date
    # 3. link via 'original_rcept_no' field
    # 4. event_date_effective = correction's event_date if specified, else original's
    # 5. amount_after_correction = correction's amounts (override original)
    pass
```

## Output schema linkage fields (Referee 17-field schema)

| Field | Use in linkage |
|---|---|
| `rcept_no` | this disclosure |
| `cancellation_linkage` | original_rcept_no if this is a correction/cancellation |
| `event_date` | base or corrected business date |
| `effective_date` | overrides set by correction if any |
| `parser_confidence` | reduced if linkage is ambiguous (multiple candidate originals) |

## Edge cases observed in samples

- `[기재정정]주요사항보고서(자기주식취득결정)` linking to original `주요사항보고서(자기주식취득결정)` → typical case

- `[기재정정]주요사항보고서(자기주식취득결정)(자회사의 주요경영사항)` — subsidiary variant — must match same `(자회사의 주요경영사항)` suffix

- `[기재정정]전환청구권행사(제2회차)` — series_marker `(제2회차)` must match

- `철회신고서` (120 in R000) — body XML may not name original explicitly; use `corp_code + rcept_date window (≤30 days prior)` as fallback

- `취소공시` patterns are heterogeneous (e.g., `가족친화인증 취소`) — most are NOT shareholder events; filter by base_form whitelist before linkage