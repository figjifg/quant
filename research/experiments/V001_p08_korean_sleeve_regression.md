# V001 P08 Korean Sleeve Data Integrity Regression

Status: ACTIVE.

## Purpose

Confirm that the D013/H001 Korean sleeve used by `P08_IEF30` is not affected
by the S001 issue set.

This is a data integrity regression. Alpha re-optimization X.

## Required Checks

1. D013 returns adjusted 사용 확인.
2. Quarterly rebalance KRX calendar align.
3. Filtered-row next-date X.
4. Impossible single-period return X.
5. Top 5 holdings rebalance date 거래 가능.
6. Adjusted data 후 constraints valid.
7. D013/H001 summary metrics 변화 X.

## Output Directory

`reports/experiments/V001_p08_korean_sleeve_regression/`

## Verdict Rule

- byte-identical or similar -> P08 live unchanged.
- materially changed -> D013/H001 validation reopen only.

## Non-scope

- No P08 weight re-optimization.
- No D013/H001 strategy change.
- No S-family alpha retry.
