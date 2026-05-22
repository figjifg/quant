# R005-QA-lite sanity check

Status: diagnostic closure sanity check only; production X.

## Verdict

R-family CLOSED. No bug found. Title-based bucket fails on its own merits.

이 감사는 R001-R004 기존 결과를 덮어쓰지 않는다. 샘플 단위 return 재현에서 blocking bug는 발견되지 않았다.

## Event label audit

- R002 category rows: 6
- R002 mixed title bucket present: False
- 해석: R002는 true share-retirement-only 법률 라벨이 아니라 title-based cancellation/retirement-related bucket으로만 기술한다.
- 표현: 소각 실패 X, title-based bucket 실패 O.

## Return calculation audit

- Sample rows reproduced: 36
- Alignment/calculation bug found: False
- 확인 항목: KOSPI benchmark window와 event-stock window 동일 trading-day, T+1 open 진입, holding end exit, gross/KOSPI/excess return.

## Dividend caveat audit

- Dividend caveat rows: 6
- R003/R004는 price return only다. 현재 title-based 파일에는 PIT dividend amount, ex-dividend date, total-return series가 없어 배당락 gap을 정량 분리하지 못한다.
- 단, 이 caveat는 R001/R002 실패를 살리지 못한다.

## Duplicate / overlap audit

- Duplicate/overlap rows: 2279
- 같은 종목의 같은 분기 내 연속 공시와 R001+R003 중복은 `duplicate_audit.csv`에 기록했다.
- R004 composite 해석 시 event count 과대계상 가능성을 주의한다.

## Files

- `event_label_audit.csv`
- `return_calc_audit.csv`
- `dividend_caveat.csv`
- `duplicate_audit.csv`
