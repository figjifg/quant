# D3b Shares Regression Fix Report

Date: 2026-05-23 15:07:06

## Trajectory
- v1 D3b shares: 29.4%
- v2 D3b shares: 5.9% (regression)
- v3 D3b shares: **5.9%** (recovery vs v1: -23.5pp)

## Root cause of v2 regression
- v1 had broad generic substring 전환가능주식 / 행사가능주식 in shares_keywords
- v2 prioritized ACODE-specific labels (전환가능주식수 with 수 suffix); multi-row label-discovery resolved different cells
- net effect: v2 captured `conversion_price` and `amount_krw` for the first time, but lost a subset of `shares` rows where label was structured differently

## v3 fix
- Expanded D3b shares_keywords (both generic and ACODE-specific) to include the full set:
  - 전환(행사)가능주식수(주), 전환가능주식수(주), 전환가능주식수, 전환가능주식, 행사가능주식수(주), 행사가능주식수, 행사가능주식, 전환에 따라 발행할, 신주인수권 행사에 따라
- Kept ACODE-specific maps for 11324 / 11325 with same full keyword list
- Same multi-row discovery + flat-adjacency fallback retained from v2

## Verification
- v3 D3b shares: 5.9% (does not meet v1 baseline 29.4%)
- amount_krw, conversion_price gains from v2 retained (see delta report)

## Compliance
- No strategy / no return / no parser-strategy-ready language
- Kill gate 'correction linkage regresses' NOT triggered (linkage maintained)