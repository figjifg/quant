# D2 Parser Wave Readiness

Each D3 parser wave needs a clear field map + failure modes. This document fixes those for waves D3a, D3b, D3c. Implementation NOT YET APPROVED by Referee.

## D3a — Treasury (자사주)

Forms covered:

- 주요사항보고서(자기주식취득결정), 자기주식취득결과보고서, 주요사항보고서(자기주식취득신탁계약체결결정), 주요사항보고서(자기주식취득신탁계약해지결정)

- 주요사항보고서(자기주식처분결정), 자기주식처분결과보고서

- 주식소각결정


Field map:

| Output schema field | Source TH label candidates | Notes |

|---|---|---|

| amount_krw | 취득예정금액, 처분예정금액, 소각예정금액 | 단위 원 vs 백만원 normalize |

| shares | 취득예정주식수, 처분예정주식수, 소각예정주식수 | 보통주/우선주 분리 |

| shares_before | 발행주식총수 / 자기주식 보유현황 | optional |

| shares_after | 처분/취득 후 자기주식 수 | computed if not explicit |

| event_date | 이사회 결의일 | rcept_date 가 아닌 결의일 |

| effective_date | 예정 취득/처분 기간 시작일 | optional |


Failure modes:

- 신탁계약 체결/해지: 금액/주식수 둘 다 unspecified → `parser_confidence` 낮춤

- 결과보고서 vs 결정 분리 → event_type 세분화

- 자회사 주요경영사항 suffix → 모회사 corp_code 별도 처리


## D3b — CB/BW + Conversion Request

Forms covered:

- 주요사항보고서(전환사채권발행결정), 주요사항보고서(신주인수권부사채권발행결정)

- 전환청구권행사 (제N회차)


Field map:

| Output schema field | Source TH label candidates | Notes |

|---|---|---|

| amount_krw | 사채총액, 발행금액 | |

| shares | 전환가능주식수, 신주인수가능주식수 | dilution proxy |

| factor | 전환가액 ÷ 전환가능주식수 | computed |

| event_date | 발행 결의일, 전환청구일 | |

| effective_date | 납입일, 전환일 | |


Failure modes:

- 회차 marker 누락 → series_marker null → linkage 어려움

- 전환가액 reset 조항 → 본문 텍스트에 description, structured field 아님 → manual_review_required

- 첨부정정 = factor/amount 변경 → linkage 필수


## D3c — 기타 (유증/무증/감자/합병·분할/추가상장/보호예수/대주주매도/철회·취소)

Forms covered:

- 주요사항보고서(유상증자결정), 주요사항보고서(무상증자결정)

- 주요사항보고서(감자결정)

- 주요사항보고서(회사합병결정), 주요사항보고서(회사분할결정), 회사분할합병결정

- 추가상장 (R000 KOSPI 3 disclosures only; KOSDAQ list API expansion required)

- 보호예수 (기타안내사항 형태)

- 임원ㆍ주요주주특정증권등소유상황보고서 + 거래계획

- 철회신고서 + 취소공시 (heterogeneous, base_form whitelist 필요)


Failure modes:

- 추가상장/보호예수 = `기타안내사항` 안에 자유 텍스트 → structured field 부재 → `manual_review_required` 빈도 높음

- 임원 보고서 = 거래 후 보고 (lag), 거래계획은 ex-ante → event_date 구분 필수

- 취소공시 = 다수가 shareholder event 아님 (예: 인증 취소) → whitelist 적용


## Parallelization gate

D3a / D3b / D3c parallelizable after D2 schema mapping (this document) Referee-approved. D3 implementation NOT YET APPROVED — awaiting Referee D2 review verdict.