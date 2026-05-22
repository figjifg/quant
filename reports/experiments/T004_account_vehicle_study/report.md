# T004 account / vehicle study

## 설정

- 대상: `P08_IEF30` = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- 기간: 2010-01-04 ~ 2026-05-18, 초기자본 100,000,000 KRW.
- Rebalance: quarterly, HIFO lot accounting where taxable, ongoing NAV, 매매 수수료 0.25%.
- T000/T003 baseline 호환을 위해 V1/V2의 배당 원천징수/분배금세는 세목으로 추적하되 NAV에서는 차감하지 않았다. 매매차익 관련 세금과 ISA 분리과세, 연금 세액공제는 NAV에 반영했다.
- Gross I003.5 참고 CAGR: 0.127384.
- T003-A / T000-C baseline 참고 CAGR: 0.124626.
- 국내 상장 ETF proxy는 tracking error 0으로 단순화했다.
- Diagnostic only: 한국 세법 2026 기준 단순화이며 실전 적용 전 세무 전문가 확인이 필요하다.

## 5 vehicle net 비교

| scenario | label   | net_cagr | net_cagr_after_pension_withdrawal_tax | net_cagr_delta_vs_t003_a_pp | final_nav | total_tax_or_credit_krw_16y | withdrawal_tax_krw |
| ---      | ---     | ---      | ---                                   | ---                         | ---       | ---                         | ---                |
| T004-V1  | 100% V1 | 0.124626 | 0.124626                              | 0.000000                    | 6.819531  | 26564978.780955             | 0.000000           |
| T004-V2  | 100% V2 | 0.123951 | 0.123951                              | -0.067438                   | 6.752910  | 26484509.942055             | 0.000000           |
| T004-V3  | 100% V3 | 0.124927 | 0.124927                              | 0.030112                    | 6.849478  | 13630414.024930             | 0.000000           |
| T004-V4  | 100% V4 | 0.132173 | 0.128267                              | 0.754737                    | 7.668728  | -13464000.000000            | 42178006.015168    |
| T004-V5  | 100% V5 | 0.130142 | 0.126242                              | 0.551588                    | 7.417339  | -6732000.000000             | 40795362.274992    |

## 3 mix net 비교

| scenario  | label                                    | net_cagr | net_cagr_after_pension_withdrawal_tax | net_cagr_delta_vs_t003_a_pp | final_nav | total_tax_or_credit_krw_16y | withdrawal_tax_krw |
| ---       | ---                                      | ---      | ---                                   | ---                         | ---       | ---                         | ---                |
| T004-MIX1 | 50% V1 + 30% ISA + 20% pension           | 0.126297 | 0.125463                              | 0.167109                    | 6.998355  | 14678813.597956             | 8435601.203034     |
| T004-MIX2 | 30% V1 + 30% ISA + 20% pension + 20% IRP | 0.127409 | 0.125785                              | 0.278297                    | 7.117916  | 8019417.841766              | 16594673.658032    |
| T004-MIX3 | 60% V2 + 20% pension + 20% IRP           | 0.126933 | 0.125299                              | 0.230766                    | 7.068959  | 11851505.965233             | 16594673.658032    |

## 가장 효율적 vehicle / mix

- Vehicle 기준 1위: T004-V4 100% V4, withdrawal tax 반영 CAGR 0.128267.
- Mix 기준 1위: T004-MIX2 30% V1 + 30% ISA + 20% pension + 20% IRP, withdrawal tax 반영 CAGR 0.125785.

## 양도세 22% vs 배당소득세 15.4% 영향

- V1 해외 ETF 직접: net CAGR 0.124626, 16년 capital gains tax 17,018,648 KRW, dividend withholding 9,546,331 KRW.
- V2 국내 상장 미국 ETF proxy: net CAGR 0.123951, 16년 국내 ETF 과세/분배금세 26,484,510 KRW.
- V2 - V1 net CAGR 차이: -0.067pp.
- 이 차이는 22% 양도세와 250만원 공제 조합을 15.4% 배당소득세형 과세로 바꾼 단순화 효과다. 금융소득 종합과세는 모델링하지 않았다.

## ISA 비과세 200만원 효과

- V3 ISA net CAGR: 0.124927.
- V3 ISA separate tax 16년 합계: 13,630,414 KRW.
- V3 - V2 net CAGR 차이: 0.098pp.
- ISA는 연 200만원 비과세 후 초과분 9.9% 분리과세로 모델링했다. 초기 1억원 전체가 단순화된 ISA lifetime cap 안에 있다고 가정했다.

## 연금저축/IRP 세액공제와 lock-up

- V4 연금저축 paper CAGR: 0.132173, withdrawal tax 반영 CAGR 0.128267, 16년 세액공제 -13,464,000 KRW.
- V5 IRP paper CAGR: 0.130142, withdrawal tax 반영 CAGR 0.126242, 16년 세액공제 -6,732,000 KRW.
- V4/V5는 55세 이후 연금 인출세 5.5%를 terminal tax로 별도 반영했다. 조기인출 16.5% 기타소득세는 diagnostic으로만 `lock_up_analysis.csv`에 기록했다.

| vehicle | label           | paper_final_nav_krw | paper_cagr_before_withdrawal_tax | pension_withdrawal_tax_rate | pension_withdrawal_tax_krw | final_nav_after_pension_withdrawal_tax_krw | cagr_after_pension_withdrawal_tax | early_withdrawal_penalty_rate_diagnostic | early_withdrawal_penalty_krw_diagnostic | lock_up_assumption                               |
| ---     | ---             | ---                 | ---                              | ---                         | ---                        | ---                                        | ---                               | ---                                      | ---                                     | ---                                              |
| V4      | Pension savings | 766872836.639411    | 0.132173                         | 0.055000                    | 42178006.015168            | 724694830.624244                           | 0.128267                          | 0.165000                                 | 126534018.045503                        | 16-year lock-up; no early withdrawal in headline |
| V5      | IRP             | 741733859.545311    | 0.130142                         | 0.055000                    | 40795362.274992            | 700938497.270319                           | 0.126242                          | 0.165000                                 | 122386086.824976                        | 16-year lock-up; no early withdrawal in headline |

## 세금 종류별 요약

| vehicle | label                        | capital_gains_tax_krw | dividend_withholding_krw | domestic_distribution_tax_krw | isa_separate_tax_krw | pension_tax_credit_krw | total_tax_or_credit_krw |
| ---     | ---                          | ---                   | ---                      | ---                           | ---                  | ---                    | ---                     |
| V1      | Overseas ETF direct taxable  | 17018647.921280       | 9546330.859675           | 0.000000                      | 0.000000             | 0.000000               | 26564978.780955         |
| V2      | Korean-listed US ETF taxable | 0.000000              | 9689034.325596           | 16795475.616459               | 0.000000             | 0.000000               | 26484509.942055         |
| V3      | Brokerage ISA                | 0.000000              | 0.000000                 | 0.000000                      | 13630414.024930      | 0.000000               | 13630414.024930         |
| V4      | Pension savings              | 0.000000              | 0.000000                 | 0.000000                      | 0.000000             | -13464000.000000       | -13464000.000000        |
| V5      | IRP                          | 0.000000              | 0.000000                 | 0.000000                      | 0.000000             | -6732000.000000        | -6732000.000000         |

## 한국 세법 가정

- 기준: 2026년 현재 한국 거주자 기준 단순화.
- V1: 해외 상장 ETF 직접 보유, 양도세 22%, 연 250만원 공제, 배당 원천징수 15%.
- V2: 국내 상장 해외 ETF proxy, 매매차익과 분배금을 배당소득세 15.4%로 단순화, 250만원 공제 없음.
- V3: ISA 일반형, 연 200만원 비과세, 초과분 9.9% 분리과세, 국내 상장 ETF만 허용.
- V4: 연금저축, 연 600만원 세액공제 대상, 13.2% 세액공제, 연금 인출세 5.5%.
- V5: IRP, 연 300만원 세액공제 대상, 13.2% 세액공제, 연금 인출세 5.5%, 위험자산 70% 제한 통과.
- 금융소득 종합과세, 실제 ETF 과표기준가, 환헤지/환노출 상품 차이, broker별 원천징수/신고 처리, 세액공제 자격 제한은 모델링하지 않았다.

## Verdict

- Verdict: diagnostic 기준으로 production 운용의 우선 검토 조합은 T004-MIX2이다.
- 단일 vehicle로는 T004-V4이 가장 높지만, 연금/IRP 결과는 장기 lock-up과 인출세 가정에 의존한다.
- T-family 종합 결론: T000 HIFO+250만원 공제는 약 +0.45pp 개선, T001/T002/T003은 효과가 미미했다. T004에서는 vehicle/account 선택이 가장 큰 잠재 source로 나타났다.
- 이 결론은 세무 자문 전까지 실행 권고가 아니라 account/vehicle 설계 후보를 좁히는 diagnostic 결과다.

## Files

- vehicle_scenarios.csv
- tax_by_vehicle.csv
- vehicle_attribution.csv
- lock_up_analysis.csv
- daily_nav_by_vehicle.csv
