# S2 — OPENDART Body Parser Plan

Date: 2026-05-22
Status: **acquisition feasibility verified**. Parser 구축 = 사용자 결정 후 별도 phase
Origin: Round 3 missing source S2 (Corporate Action Event Log)

## Feasibility Verified

OPENDART body XML download = **OK** (사용자 API key 사용).

Sample test (기아 자기주식취득결정, rcept_no=20240125000291):
- Endpoint: `https://opendart.fss.or.kr/api/document.xml`
- Response: ZIP containing `{rcept_no}.xml` (4,449 bytes)
- XML format: DART3 schema (DOCUMENT > BODY > LIBRARY > SECTION > TABLE)
- 구조화된 metadata + 표 형식 본문

## Scope

S2 body parser = Round 3 carrier corporate action event log:
- 자사주 취득 / 처분 / 소각
- CB / BW 발행 + 전환청구
- 유상증자 / 무상증자
- 감자
- 합병 / 분할
- 추가상장 / 보호예수 해제
- 대주주 매도

각 event 의 정확한 amount / shares / 효력 발생일 추출.

## Effort Estimate

| Phase | 작업 | Time | Difficulty |
|---|---|---|---|
| 0 | API endpoint verification | ✅ done | low |
| 1 | Body XML bulk download (450k disclosures 또는 filtered) | 1-2 days | low (sequential API call) |
| 2 | XML schema 분석 (DART3 form mapping) | 3-5 days | medium |
| 3 | Type별 parser (자사주 / CB·BW / 증자 / 감자 / 합병 / 추가상장 / 보호예수 / 대주주매도) | 2-4 weeks | high (수작업 sample 검증 + edge case) |
| 4 | 정정공시 linkage + cancellation handling | 1 week | medium |
| 5 | Sample audit (per type 20-50건 manual verification) | 1 week | high |
| 6 | Output schema 통합 + W001 v2 integration | 3-5 days | medium |

**Total: 5-9 weeks**.

## Alternative

| Source | Cost | Time | Trade-off |
|---|---|---|---|
| 자체 구축 (위) | 무료 | 5-9 weeks | 통제 / 무료 |
| Vendor (FnGuide / KIS / 매경) | 유료 (구독) | 1-4 weeks | 빠름 / 비용 |
| Hybrid (vendor + 자체 sample 검증) | 유료 일부 | 3-6 weeks | 균형 |

## Recommendation

이 작업 = 시간 크고 사용자 결정 필요:
- **Option A** = 자체 구축 (무료, 1-2 개월). Codex 위임 가능 (W001 v2 와 같이).
- **Option B** = vendor (유료, 빠름). 단 구독료 + vendor field coverage 검증 부담.
- **Option C** = 일단 보류, S1 + S3 + S6 만으로 기능 가능 부분 우선 진행.

다른 source (S1, S3, S4, S6) 와 달리 즉시 acquire 어렵고 큰 작업이라 **별도 사용자 결정 권장**.

## Body Sample 보관

`data/acquired/round4/s2_dart_body_samples/20240125000291_document.xml.zip`
(첫 2KB sample, 기아 자기주식취득결정)

Parser 시작 시 sample 확장 + schema 분석부터.

## Related

- `docs/W001_v2_infrastructure_repair_plan.md` Component 3
- `docs/round3_missing_source_register.md` S2
- `docs/data_gap_KR_OVERHANG_AVOID.md` (S2 cover 시 영향)
