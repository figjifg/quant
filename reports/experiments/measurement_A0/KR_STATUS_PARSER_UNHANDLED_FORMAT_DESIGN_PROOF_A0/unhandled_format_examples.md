# Unhandled-format design proof — representative examples

Inspection samples ONLY. NOT validation, NOT approval, NOT parsed rows.
Candidate values are hypothetical / proof-only (NOT effective dates).

## relative_tbd_keep_fail_closed
- 20100305800323 [relative_or_tbd_marker] labels=해제일 | imm="시 주요사항보고서(영업양수) 제출일 익일 단," | hypothetical_iso_PROOF_ONLY=(none)
- 20100426800466 [relative_or_tbd_marker] labels=해제일 | imm="시 주요사항보고서(합병) 제출일 익일 단, 우" | hypothetical_iso_PROOF_ONLY=(none)
- 20110412800376 [relative_or_tbd_marker] labels=해제일 | imm="시 우회상장 확인서 및 첨부서류 제출일 익일" | hypothetical_iso_PROOF_ONLY=(none)
- 20120319800557 [relative_or_tbd_marker] labels=해제일 | imm="시 우회상장 확인서 및 첨부서류 제출일 익일" | hypothetical_iso_PROOF_ONLY=(none)
- 20120416800427 [relative_or_tbd_marker] labels=해제일 | imm="시 우회상장 확인서 및 첨부서류 제출일 익일" | hypothetical_iso_PROOF_ONLY=(none)

## ambiguous_requires_manual_or_later_design
- 20101230900335 [other_ambiguous] labels=정지일|정지기간 | imm="시 2010-12-30 15:36:00 나.만 가.정지일시 2010-12-30 15:36:" | hypothetical_iso_PROOF_ONLY=(none)
- 20111214900344 [other_ambiguous] labels=정지일|정지기간|재개일 | imm="시 2011-12-14 14:37:00 나.만 가.정지일시 2011-12-14 14:37: 의 장개시전 시간외매매는 성립되지 않습니다." | hypothetical_iso_PROOF_ONLY=(none)

## out_of_scope_keep_fail_closed
- 20111013900324 [date_range_or_period_text] labels=정지기간 | imm="가.변경전 2011년 04월 21일~상장폐지" | hypothetical_iso_PROOF_ONLY=(none)

## future_parser_change_candidate_guarded
- 20210430900254 [absolute_date_unhandled_format] labels=변경일 | imm="자) '21.5.3 □ (대상법인) 코스닥시장" | hypothetical_iso_PROOF_ONLY=2021-05-03
