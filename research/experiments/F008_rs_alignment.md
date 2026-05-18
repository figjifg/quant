# F008 RS + Foreign/Institution Alignment

## Hypothesis

Stock RS should perform better when foreign and institution flows align with
the trend.

## Specification

- Base: stock RS score.
- Foreign positive and institution positive: +1.0.
- Foreign positive only: +0.5.
- Foreign negative only: -0.5.
- Foreign negative and institution negative: -1.0.
- Missing flow inputs receive no adjustment.
- Normalize final score within sector on each signal date.
- Carriers: D013 direct and E014 top-4 sector carrier.

## Outputs

`reports/experiments/F008_rs_alignment/`

