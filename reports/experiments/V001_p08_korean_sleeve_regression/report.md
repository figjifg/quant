# V001 P08 Korean Sleeve Regression

Verdict: PASS_BYTE_IDENTICAL

## 확인 결과

- D013/H001 metrics byte-identical: True
- Entry/exit KRX calendar bad count: 0
- Top 5 holdings tradability fail count: 0
- Impossible daily return rows in panel: 452

## 판정

W001 유틸을 사용한 회귀 확인에서 D013/H001 기존 산출물은 재작성하지 않았다. metrics.json 내용이 baseline snapshot과 동일하고 진입/청산 날짜가 KRX trading day 및 signal_date 이후 조건을 만족하면 PASS_BYTE_IDENTICAL이다.
