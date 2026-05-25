# Pass-2 Unit Test Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)
Parser version: krx_status_html_inline-1.1.0

## Test result: **34 / 34 passing**

## Test breakdown

Pre-existing 26 tests (1.0.0):
- categorize_* (5)
- find_first_date_* / find_date_range_* (5)
- detect_body_format_* / extract_body_* (4)
- find_label_hits_* / resumption_time (4)
- parse_disclosure end-to-end (8)

New 8 tests (1.1.0):
- `test_period_change_after_change_marker_picks_after_period`
- `test_period_change_korean_after_marker`
- `test_period_change_jeongjeong_marker`
- `test_period_change_without_explicit_markers_falls_back_to_last`
- `test_ordinary_suspension_unchanged`
- `test_period_change_negative_control_still_blocks`
- `test_period_change_correction_still_forces_manual_review`
- `test_parser_version_tagged`

## Test command

`.venv/bin/python -m pytest tests/test_krx_status_html_inline.py -v`

## Test file

`tests/test_krx_status_html_inline.py`
