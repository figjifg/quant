# D2 Actual Form Taxonomy Mapping

Maps Referee 14-event-type taxonomy → actual DART report_nm forms observed in samples.

| Event type | Expected keywords | Actual forms (sample-observed) | N(total) | N(D1) | N(D2) | Coverage |
|---|---|---|---|---|---|---|
| treasury_acquire | 자기주식취득결정 | [기재정정]주요사항보고서(자기주식취득결정); 주요사항보고서(자기주식취득결정); 자기주식취득결정(자회사의 주요경영사항) | 5 | 5 | 0 | covered |
| treasury_dispose | 자기주식처분결정 | 주요사항보고서(자기주식처분결정)(자회사의 주요경영사항); 주요사항보고서(자기주식처분결정) | 5 | 5 | 0 | covered |
| treasury_cancel | 주식소각결정 | 주식소각결정 | 5 | 0 | 5 | covered |
| cb_issue | 전환사채권발행결정 | [기재정정]주요사항보고서(전환사채권발행결정); 주요사항보고서(전환사채권발행결정); [첨부정정]주요사항보고서(전환사채권발행결정) | 5 | 5 | 0 | covered |
| bw_issue | 신주인수권부사채권발행결정 | 주요사항보고서(신주인수권부사채권발행결정); [기재정정]주요사항보고서(신주인수권부사채권발행결정); [첨부정정]주요사항보고서(신주인수권부사채권발행결정) | 5 | 5 | 0 | covered |
| conversion_request | 전환청구권행사 | [기재정정]전환청구권행사; 전환청구권행사; 전환청구권행사(제2회차) | 5 | 5 | 0 | covered |
| rights_issue | 유상증자결정 | [기재정정]유상증자결정(종속회사의주요경영사항); 주요사항보고서(유상증자결정); [기재정정]주요사항보고서(유상증자결정) | 5 | 5 | 0 | covered |
| bonus_issue | 무상증자결정 | 주요사항보고서(무상증자결정)(자회사의 주요경영사항); 주요사항보고서(무상증자결정); [기재정정]주요사항보고서(유무상증자결정); [기재정정]유무상증자결정(종속회사의주요경영사항) | 5 | 5 | 0 | covered |
| capital_reduction | 감자결정 | 감자결정(자율공시)(종속회사의주요경영사항); 주요사항보고서(감자결정); [첨부추가]주요사항보고서(감자결정) | 5 | 5 | 0 | covered |
| merger_split | 회사합병결정, 회사분할결정, 회사분할합병결정 | [첨부정정]주요사항보고서(회사합병결정); 주요사항보고서(회사분할결정); 회사합병결정(종속회사의주요경영사항); 주요사항보고서(회사합병결정); [기재정정]주요사항보고서(회사합병결정) | 5 | 5 | 0 | covered |
| additional_listing | 추가상장 | [기재정정]기타시장안내 (추가상장 유예 관련 안내); 기타시장안내 (추가상장 유예 관련 안내) | 3 | 0 | 3 | covered |
| lockup_release | 보호예수, 의무보유 | 기타안내사항(안내공시) (보통주 의무보유(보호예수)기간 만료)); 기타안내사항(안내공시)(보통주 의무보유(보호예수)기간 만료); 기타안내사항(안내공시) (주성코퍼레이션 보통주 보호예수기간 만료안내); 기타안내사항(안내공시)(보호예수기간 만료 안내); 기타안내사항(안내공시)(바이오노트 보통주 의무보유(보호예수)기간 만료 안내) | 5 | 0 | 5 | covered |
| major_shareholder_sale | 임원ㆍ주요주주특정증권등소유상황보고서, 임원ㆍ주요주주특정증권등거래계획 | 임원ㆍ주요주주특정증권등소유상황보고서 | 5 | 0 | 5 | covered |
| correction_withdrawal_cancel | 철회신고서, 취소공시 | 철회신고서; 철회신고서(㈜미래에셋글로벌위탁관리부동산투자회사); 철회신고서((주)제이알글로벌위탁관리부동산투자회사) | 5 | 0 | 5 | covered |

## Variant normalization (apply in D3 parser pipeline)

```
CORRECTION_PREFIXES = ['[기재정정]', '[첨부정정]', '[첨부추가]', '[연장결정]']
SUBSIDIARY_SUFFIXES = ['(자회사의 주요경영사항)', '(종속회사의주요경영사항)']
SERIES_PATTERN = r'\(제\d+회차\)'
```
Normalize each report_nm by stripping correction prefix, subsidiary suffix, series marker → base_form.