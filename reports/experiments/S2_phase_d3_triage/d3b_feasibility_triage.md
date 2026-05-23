# D3b Feasibility Triage

Date: 2026-05-23 15:32:39

## 5-category classification (Referee taxonomy)

- `structured_extractable`: target field found in body table via label-keyword match
- `text_extractable`: target field present in free-text (outside tables) — keyword found in SECTION/COVER text
- `attachment_only`: tiny response, body XML absent
- `ambiguous`: HTML inline response without clear table label structure
- `not_extractable`: target field not found in any form within the body
- `missing_xml`: download failed in D1 (already known)

## Sub-category: `cb_issue` (n=6)

### Shares classification distribution
| Category | Count |
|---|---|
| structured_extractable | 3 |
| not_extractable | 2 |
| missing_xml | 1 |

### event_date classification distribution
| Category | Count |
|---|---|
| not_extractable | 5 |
| missing_xml | 1 |

### Per-row triage (sample-level)
| rcept_no | response_type | shares classification | event_date classification |
|---|---|---|---|
| 20210820000414 | dart_xml | not_extractable | not_extractable |
| 20240605000316 | dart_xml | structured_extractable | not_extractable |
| 20200720000291 | dart_xml | not_extractable | not_extractable |
| 20190225002597 | ? | missing_xml | missing_xml |
| 20260317000516 | dart_xml | structured_extractable | not_extractable |
| 20230131000267 | dart_xml | structured_extractable | not_extractable |

## Sub-category: `bw_issue` (n=5)

### Shares classification distribution
| Category | Count |
|---|---|
| not_extractable | 2 |
| missing_xml | 2 |
| structured_extractable | 1 |

### event_date classification distribution
| Category | Count |
|---|---|
| not_extractable | 3 |
| missing_xml | 2 |

### Per-row triage (sample-level)
| rcept_no | response_type | shares classification | event_date classification |
|---|---|---|---|
| 20200928000303 | dart_xml | not_extractable | not_extractable |
| 20180205000416 | ? | missing_xml | missing_xml |
| 20251002000306 | dart_xml | structured_extractable | not_extractable |
| 20180911000394 | ? | missing_xml | missing_xml |
| 20220317000121 | dart_xml | not_extractable | not_extractable |

## Sub-category: `conversion_request` (n=6)

### Shares classification distribution
| Category | Count |
|---|---|
| ambiguous | 5 |
| structured_extractable | 1 |

### event_date classification distribution
| Category | Count |
|---|---|
| ambiguous | 5 |
| structured_extractable | 1 |

### Per-row triage (sample-level)
| rcept_no | response_type | shares classification | event_date classification |
|---|---|---|---|
| 20200715900389 | html_inline | ambiguous | ambiguous |
| 20200721900353 | html_inline | ambiguous | ambiguous |
| 20181128900650 | html_inline | ambiguous | ambiguous |
| 20200710900612 | html_inline | ambiguous | ambiguous |
| 20200810900483 | html_inline | ambiguous | ambiguous |
| 20250930900968 | html_inline | structured_extractable | structured_extractable |

## Verdict
- CB issue: shares mostly text_extractable/ambiguous = 0 / 6
- BW issue: shares mostly text_extractable/ambiguous = 0 / 5
- conversion request: event_date mostly text_extractable/ambiguous = 5 / 6

Per Referee decision rule: 'If D3b shares/event_date are mostly text_extractable or ambiguous, do not continue generic parser tuning. Mark D3b as requiring per-form custom parser or manual audit.'

- text_extractable/ambiguous share is moderate (29.4%). Some D3b extraction may still be reachable via continued tuning.

## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready