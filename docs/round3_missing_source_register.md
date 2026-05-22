# Round 3 Missing Source Register

Date: 2026-05-22
Status: LIVING DOCUMENT (Round 3 audit 진행 중 update)
Origin: Referee Round 3 lock + Round 2 Step 5 findings

이 register 는 Round 3 의 5 A0 audit 에서 발견된 missing official source 를
누적 기록한다. 각 source 는 사용자 host 작업 영역. 사용자 명시 결정 후만
acquisition 진행.

## Seed Entries (Round 2 Step 5 already-discovered)

### S1 — Adjusted OHLC Source

**Status**: MISSING (Round 2 Step 5 confirmed)
**Blocks**: KR-G5-ADJOHLC-CORPACT-AUDIT-001 (Priority 1A) + downstream
KR-LIQ-FRAGILITY-AVOID / KR-LIQ-MIGRATION / KR-TURNOVER-ATTENTION
**Required fields**:
- `adjusted_open`, `adjusted_high`, `adjusted_low`, `adjusted_close`
- `adjustment_factor` per event
- 모두 PIT (사후 정정 X)

**Source candidates**:
| Source | Cost | 시간 | 난이도 |
|---|---|---|---|
| KRX 공식 수정주가 | 무료/일부 유료 | 1-2 주 | 중 |
| Bloomberg / Refinitiv | 유료 (구독) | 1 일 (구독 시) | 낮음 |
| FnGuide / FN데이터 | 유료 | 1-4 주 | 중 |
| pykrx + strict PIT 검증 | 무료 | 1 주 | 중 단 vendor restate 위험 |
| 자체 corporate_action ledger + 가격 재계산 | 무료 (DART) | 4-8 주 | 높음 |

자세히: `docs/data_gap_adjusted_ohlc.md`.

### S2 — Corporate Action Event Log

**Status**: MISSING
**Blocks**: KR-G5-ADJOHLC-CORPACT-AUDIT-001
**Required fields**:
- event_date, effective_date, ticker, event_type
- factor (adjustment factor)
- shares_before, shares_after
- cancellation / withdrawal linkage

**Event types coverage**:
- Split (액면분할)
- Reverse split (액면병합)
- Capital reduction (감자)
- Rights issue (유상증자)
- Bonus issue (무상증자)
- Merger (합병)
- Spin-off (분할)
- Suspension / resumption
- Listing transitions

**Source candidates**:
| Source | Cost | 시간 | 난이도 |
|---|---|---|---|
| OPENDART API 본문 XML + parser | 무료 (API) | 2-8 주 | 높음 |
| KRX 공시 archive | 무료 / 유료 | 1-3 주 | 중 |
| Vendor parsed events (FnGuide / KIS / 매경) | 유료 | 1-4 주 | 중 |

### S3 — KRX Suspension / Delisting / Managed Status

**Status**: MISSING (panel 에 STATUS column 없음)
**Blocks**: KR-TRADABILITY-SEMANTICS-AUDIT-001 (Priority 2) + downstream
KR-TRADABILITY-RESUME-RISK + KR-LIQ-FRAGILITY-AVOID
**Required fields**:
- `suspension_start_date`, `suspension_end_date`, `suspension_reason`
- `delisting_date`, `delisting_reason`
- `listing_status`: active / suspended / managed (관리종목) / 투자주의 /
  delisted

**Source candidates**:
- KRX 공시 시스템 (krx.co.kr)
- DART (delisting / 관리종목 지정 공시)
- Vendor (Bloomberg / Refinitiv listing status field)

자세히: `docs/tradability_semantics_audit.md`.

### S4 — Permanent Identifier Mapping

**Status**: MISSING (panel 의 종목코드 = KRX ticker only)
**Blocks**: KR-ID-LIFECYCLE-MASTER-AUDIT-001 (Priority 1B) + downstream 전체
**Required fields**:
- `permanent_id` (DART corp_code / ISIN / KRX permanent ID 등)
- `ticker_history` (per permanent_id 의 ticker rotation chronology)
- `name_history` (per permanent_id 의 name change chronology)
- `corporate_event_chain` (merger / split / rename 의 entity linkage)

**Source candidates**:
- DART corp_code 매핑 (이미 OPENDART parquet 안 corp_code 있음)
- KRX listed companies master file
- Vendor (FnGuide / KIS) entity mapping

### S5 — Dynamic Top100 Generation Rule

**Status**: UNKNOWN (rule documentation 미확인)
**Blocks**: KR-TOP100-PIT-LINEAGE-AUDIT-001 (Priority 3)
**Required**:
- Selection rule (market cap top N? trading value top N? composite?)
- Universe (전 KOSPI? KOSPI+KOSDAQ? exclude managed?)
- Rebalance frequency
- Timestamp lineage (어떤 시점의 market cap / trading value 기준)
- Reproducibility script

**Source candidates**:
- Repo 내부 (dynamic_top100 생성 script 있는지 확인 필요)
- Panel metadata 또는 README
- Vendor doc (만약 vendor 가 생성한 universe 라면)

### S6 — Flow Data Vendor Documentation

**Status**: PARTIAL (field 존재하지만 doc 부재)
**Blocks**: KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 (Priority 4)
**Required**:
- Sign convention 명시 (+ = 매수 / - = 매도 정확히)
- Unit 명시 (KRW / 백만 KRW / 십억 KRW)
- Publication timing (장 마감 후 / 익일 / 익영업일)
- Missing flow 처리 방식 (0 vs NaN 구별)
- Vendor coverage (전 종목? 일부?)

**Source candidates**:
- 기존 vendor (panel 제공한 source) 문서
- KRX 투자자별 거래실적 사이트 (krx.co.kr)
- Internal data acquisition documentation (있다면)

## Cross-Card Source Priority

| Source | Blocks Priority 1A | 1B | 2 | 3 | 4 |
|---|:-:|:-:|:-:|:-:|:-:|
| S1 Adjusted OHLC | ✅ | | △ | △ | |
| S2 Corporate Action Log | ✅ | △ | △ | △ | |
| S3 Suspension Status | | △ | ✅ | △ | △ |
| S4 Permanent ID | △ | ✅ | △ | △ | △ |
| S5 Top100 Generation Rule | | △ | | ✅ | |
| S6 Flow Documentation | | | | | ✅ |

**Critical path**: S1 + S2 + S4 = G5 + ID lifecycle 통과의 필수.

## Acquisition Path Recommendation (사용자 host 결정)

만약 모든 source 한 번에 acquire:
- **Vendor 통합 구독** (Bloomberg / Refinitiv) = 빠른 path, 비용 큼 (월
  단위 구독료)
- **KRX 데이터 + 자체 parser** = 무료 / 저비용, 시간 4-8 주
- **Hybrid** = vendor 일부 + 자체 일부

만약 단계별:
1. S4 (Permanent ID) 먼저 = OPENDART corp_code 이미 있음, mapping 작업만
2. S2 (Corporate Action Log) = OPENDART API + parser (R-family Q2 backlog
   와 partial overlap)
3. S1 (Adjusted OHLC) = S2 통과 후 가격 재계산 가능 (또는 vendor 직접)
4. S3 (Suspension Status) = KRX 공시 site
5. S5 (Top100 Rule) = repo 내부 doc 확인 → 없으면 vendor doc
6. S6 (Flow Doc) = vendor 문의

## Update Convention

Round 3 audit 진행 중 새 missing source 발견 시 이 register 에 추가:
- Section heading (S7, S8, ...) 으로 entry 추가
- Status / Blocks / Required fields / Source candidates 명시
- 영향 받는 카드 priority 표 업데이트

## Update Log

| Date | Update |
|---|---|
| 2026-05-22 | Seed (S1-S6) from Round 2 Step 5 findings + Round 3 spec |
| 2026-05-22 | Round 3 Step 5 audit 결과 반영 + Referee Round 3 final lock priority 갱신 |

## Round 3 Final Priority Tier (Referee 명시)

Round 3 Step 5 audit 5/5 complete + Referee final lock 결과:

| Source | Tier | Status | 비고 |
|---|---|---|---|
| **S1** Adjusted OHLC | 🔴 **mandatory** | OPEN | adjusted return enables G5 unblock |
| **S2** Corporate Action Event Log | 🔴 **mandatory** | OPEN | 147 event classification + factor chain |
| **S3** KRX Suspension Status | 🔴 **mandatory** | OPEN | true_suspension distinction (Tradability unblock) |
| **S4** Permanent ID fallback | 🟡 **needed for full lifecycle pass** | OPEN | 6% non-DART fallback; DART 94% already strong base |
| **S5** Top100 Rule | 🟢 **RESOLVED** | CLOSED (reverse-engineered) | Selection rule = 거래대금추정 top 100, 100% reproducible. External source 불필요. |
| **S6** Flow Vendor Documentation | 🔴 **mandatory for any flow continuation** | OPEN | 100% estimated flag 정정 finding |

### S5 Closure Note

S5 (Dynamic Top100 Generation Rule) = **resolved by reverse-engineered
reproducible rule** (KR-TOP100-PIT-LINEAGE-AUDIT-001 Step 2). Generation
script 별도 acquisition 불필요.

단 **Top100 Gate 5 dependency 는 open** (trading value = 거래량 × close,
close = raw → split day 의 trading value 일부 왜곡). 이는 S1 (Adjusted OHLC)
이 close 시점에 같이 해결.

## Round 4 Acquisition Path (Referee 명시)

Mandatory sources (S1 + S2 + S3 + S6) acquire 후:
1. W001 v2 code fix (`docs/W001_v2_infrastructure_repair_plan.md`)
2. Re-A0 gate 실행 (`docs/W001_v2_reA0_gate_spec.md`)
3. Referee 재승인
4. Round 5+ strategy diagnostic 가능

S4 (Permanent ID fallback) = optional but needed for full lifecycle pass.
S5 = closed.

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/data_gap_adjusted_ohlc.md` (S1 + S2 상세)
- `docs/tradability_semantics_audit.md` (S3 상세)
- `docs/adjustment_engine_requirements.md` (S1 + S2 + W001 v2 spec)
- `docs/backlog_A0_queue.md` (Round 1 task Q1 + Q2, S2 와 partial overlap)
