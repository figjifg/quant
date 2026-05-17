# E001-rev non-industry KIS code handling

## Policy
- `non_industry_kis_codes` in `configs/sector_mapping.yaml` are not allowed to map directly through `kis_mcls_mapping`.
- Mapping priority is manual override, KIS industry mid-class excluding non-industry codes, KSIC fallback, then `99` other.

## Configured non-industry KIS codes
- `KOGI(지배구조지수)`

## Handled snapshot rows

| ticker | name | kis_mcls | ksic | final_sector_code | final_sector_name | mapping_source |
|---|---|---|---|---|---|---|
| 022100 | 포스코DX보통주 | KOGI(지배구조지수) | 건축기술, 엔지니어링 및 관련기술 서비스업 | 05 | 조선/기계/산업재 | ksic_fallback |
| 022520 | 코오롱아이넷보통주 | KOGI(지배구조지수) | 상품 종합 도매업 | 09 | 소비재/유통 | ksic_fallback |
| 030790 | 비케이탑스보통주 | KOGI(지배구조지수) | 컴퓨터 프로그래밍, 시스템 통합 및 관리업 | 08 | 인터넷/게임/SW | ksic_fallback |
| 035720 | 카카오보통주 | KOGI(지배구조지수) | 자료처리, 호스팅, 포털 및 기타 인터넷 정보매개서비스업 | 08 | 인터넷/게임/SW | ksic_fallback |

Code validation: `kis_mcls` direct mappings among non-industry rows = 0.
