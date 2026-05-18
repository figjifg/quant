# C. KRX 41 to 12 Group Mapping Review

- KRX current snapshot date used for scenario A: 2026-05-06
- Verdict: no clear mechanical mapping bug found.
- Main judgment item: `일반서비스` is intentionally mapped to `99 기타`; this is conservative but may move large service names out of the KIS `서비스업 -> 인터넷/게임/SW` bucket.

## Focus Review

| KRX industry | mapped group | note |
|---|---:|---|
| IT 서비스 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| IT부품 | 01 반도체/IT하드웨어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 기계·장비 | 05 조선/기계/산업재 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 디지털컨텐츠 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 반도체 | 01 반도체/IT하드웨어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 방송서비스 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 비금속 | 03 2차전지/화학/소재 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 소프트웨어 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 오락·문화 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 운송장비·부품 | 02 자동차/운송장비 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 의료·정밀기기 | 07 헬스케어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 인터넷 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 일반서비스 | 99 기타 | Residual KRX service bucket mapped to 99 기타 by explicit manual_review; economically broad. |
| 전기·전자 | 01 반도체/IT하드웨어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 정보기기 | 01 반도체/IT하드웨어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 제약 | 07 헬스케어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 종이·목재 | 03 2차전지/화학/소재 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 컴퓨터서비스 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 통신 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 통신서비스 | 08 인터넷/게임/SW | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 통신장비 | 01 반도체/IT하드웨어 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |
| 화학 | 03 2차전지/화학/소재 | Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy. |

## Full KRX Industry Mapping

| KRX industry | mapped group | suspicious |
|---|---:|---|
| IT 서비스 | 08 인터넷/게임/SW | False |
| IT부품 | 01 반도체/IT하드웨어 | False |
| 건설 | 12 건설/부동산 | False |
| 광업 | 11 에너지/유틸리티 | False |
| 금속 | 04 철강금속 | False |
| 금융 | 06 금융 | False |
| 기계·장비 | 05 조선/기계/산업재 | False |
| 기타 | 99 기타 | False |
| 기타금융 | 06 금융 | False |
| 기타제조 | 99 기타 | False |
| 농업 임업 및 어업 | 10 음식료 | False |
| 디지털컨텐츠 | 08 인터넷/게임/SW | False |
| 반도체 | 01 반도체/IT하드웨어 | False |
| 방송서비스 | 08 인터넷/게임/SW | False |
| 보험 | 06 금융 | False |
| 부동산 | 12 건설/부동산 | False |
| 비금속 | 03 2차전지/화학/소재 | False |
| 섬유·의류 | 09 소비재/유통 | False |
| 소프트웨어 | 08 인터넷/게임/SW | False |
| 오락·문화 | 08 인터넷/게임/SW | False |
| 운송·창고 | 05 조선/기계/산업재 | False |
| 운송장비·부품 | 02 자동차/운송장비 | False |
| 유통 | 09 소비재/유통 | False |
| 은행 | 06 금융 | False |
| 음식료·담배 | 10 음식료 | False |
| 의료·정밀기기 | 07 헬스케어 | False |
| 인터넷 | 08 인터넷/게임/SW | False |
| 일반서비스 | 99 기타 | False |
| 전기·가스 | 11 에너지/유틸리티 | False |
| 전기·가스·수도 | 11 에너지/유틸리티 | False |
| 전기·전자 | 01 반도체/IT하드웨어 | False |
| 정보기기 | 01 반도체/IT하드웨어 | False |
| 제약 | 07 헬스케어 | False |
| 종이·목재 | 03 2차전지/화학/소재 | False |
| 증권 | 06 금융 | False |
| 출판·매체복제 | 08 인터넷/게임/SW | False |
| 컴퓨터서비스 | 08 인터넷/게임/SW | False |
| 통신 | 08 인터넷/게임/SW | False |
| 통신서비스 | 08 인터넷/게임/SW | False |
| 통신장비 | 01 반도체/IT하드웨어 | False |
| 화학 | 03 2차전지/화학/소재 | False |

## High Impact Tickers Checked

- 삼성바이오 207940: snapshot_only, diff=0.264413
- LG화학 051910: pit_only, diff=-0.128461
- LG화학 051910: pit_only, diff=-0.119264
- LG에너지솔루션 373220: snapshot_only, diff=0.102999
- 삼성바이오 207940: snapshot_only, diff=0.098393
- POSCO홀딩스 005490: pit_only, diff=0.089924
- 셀트리온 068270: snapshot_only, diff=-0.081758
- NAVER 035420: snapshot_only, diff=0.066195
- 셀트리온 068270: snapshot_only, diff=-0.060061
- LG에너지솔루션 373220: snapshot_only, diff=-0.055146
- 삼성바이오 207940: snapshot_only, diff=-0.041114
- 셀트리온 068270: pit_only, diff=0.039123
- 삼성바이오 207940: common, diff=0.031115
- NAVER 035420: snapshot_only, diff=-0.030456
- LG화학 051910: common, diff=-0.027352
- HMM 011200: common, diff=0.025228
- POSCO홀딩스 005490: pit_only, diff=-0.020550
- HMM 011200: common, diff=-0.019173
- HMM 011200: pit_only, diff=0.018103
- 셀트리온 068270: pit_only, diff=-0.015671
