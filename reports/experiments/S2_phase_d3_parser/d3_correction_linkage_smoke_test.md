# D3 Correction / Cancellation Linkage Smoke Test

Date: 2026-05-23 14:25:06

## Summary
- corrections_total (D1+D2 samples with correction_prefix in ['[기재정정]', '[첨부정정]', '[첨부추가]', '[연장결정]']): 27
- linked to a prior non-corrected original within 180 days, same corp_code + base_form + series_marker: 3
- unlinked: 24
- link rate: 11.1%

## Algorithm

```
for each correction row:
  candidates = where(
    corp_code_dart == correction.corp_code_dart
    AND base_form == correction.base_form
    AND correction_prefix is null
    AND series_marker matches (if any)
    AND rcept_date in [correction.rcept_date - 180d, correction.rcept_date]
  )
  if candidates non-empty: link to most recent
  else: leave unlinked → manual_review_required for the correction row
```

## Notes

- Smoke test relies on the union of D1+D2 sampled disclosures only. In production D3, the candidate set would be the full R000 KOSPI parquet (450k disclosures) — link rate would be substantially higher.
- Unlinked corrections in this smoke test = the original is outside the sampled set, NOT necessarily an algorithmic failure.
- True end-to-end smoke test requires R000 full join in C3 integration phase (not part of D3 checkpoint).

## Sample linkage details (first 10)

```
[
  {
    "correction_rcept_no": "20240708000261",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(자기주식취득결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20260305000671",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(자기주식취득결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20210820000414",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(전환사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20240605000316",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(전환사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20190225002597",
    "correction_prefix": "[첨부정정]",
    "base_form": "주요사항보고서(전환사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20260317000516",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(전환사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20180205000416",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(신주인수권부사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20180911000394",
    "correction_prefix": "[첨부정정]",
    "base_form": "주요사항보고서(신주인수권부사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20220317000121",
    "correction_prefix": "[기재정정]",
    "base_form": "주요사항보고서(신주인수권부사채권발행결정)",
    "linked_to": null,
    "days_gap": null
  },
  {
    "correction_rcept_no": "20200715900389",
    "correction_prefix": "[기재정정]",
    "base_form": "전환청구권행사",
    "linked_to": "20200710900612",
    "days_gap": 5
  }
]
```