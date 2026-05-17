from __future__ import annotations

import pandas as pd

from src.data.sector_mapping_loader import apply_sector_mapping, load_sector_mapping


def test_apply_sector_mapping_prefers_kis_mcls_over_ksic():
    mapping = load_sector_mapping("configs/sector_mapping.yaml")
    snapshot = pd.DataFrame(
        [
            {
                "pdno": "00000A005930",
                "prdt_name": "삼성전자보통주",
                "idx_bztp_mcls_cd_name": "서비스업",
                "std_idst_clsf_cd": "032601",
                "std_idst_clsf_cd_name": "반도체 제조업",
            }
        ]
    )

    result = apply_sector_mapping(snapshot, mapping)

    assert result.loc[0, "ticker"] == "005930"
    assert result.loc[0, "final_sector_code"] == "08"
    assert result.loc[0, "mapping_source"] == "kis_mcls"


def test_apply_sector_mapping_uses_ksic_fallback_for_missing_mcls():
    mapping = load_sector_mapping("configs/sector_mapping.yaml")
    snapshot = pd.DataFrame(
        [
            {
                "pdno": "00000A373220",
                "prdt_name": "LG에너지솔루션보통주",
                "idx_bztp_mcls_cd_name": None,
                "std_idst_clsf_cd": "32802",
                "std_idst_clsf_cd_name": "일차전지 및 축전지 제조업",
            }
        ]
    )

    result = apply_sector_mapping(snapshot, mapping)

    assert result.loc[0, "final_sector_code"] == "03"
    assert result.loc[0, "mapping_source"] == "ksic_fallback"


def test_non_industry_kis_code_uses_ksic_fallback():
    mapping = load_sector_mapping("configs/sector_mapping.yaml")
    snapshot = pd.DataFrame(
        [
            {
                "pdno": "00000A035720",
                "prdt_name": "카카오보통주",
                "idx_bztp_mcls_cd_name": "KOGI(지배구조지수)",
                "std_idst_clsf_cd": "106301",
                "std_idst_clsf_cd_name": "자료처리, 호스팅, 포털 및 기타 인터넷 정보매개서비스업",
            }
        ]
    )

    result = apply_sector_mapping(snapshot, mapping)

    assert result.loc[0, "ticker"] == "035720"
    assert result.loc[0, "final_sector_code"] == "08"
    assert result.loc[0, "final_sector_name"] == "인터넷/게임/SW"
    assert result.loc[0, "mapping_source"] == "ksic_fallback"


def test_apply_sector_mapping_marks_unmapped_rows_as_other():
    mapping = load_sector_mapping("configs/sector_mapping.yaml")
    snapshot = pd.DataFrame(
        [
            {
                "pdno": "00000A000000",
                "prdt_name": None,
                "idx_bztp_mcls_cd_name": None,
                "std_idst_clsf_cd": None,
                "std_idst_clsf_cd_name": None,
            }
        ]
    )

    result = apply_sector_mapping(snapshot, mapping)

    assert result.loc[0, "final_sector_code"] == "99"
    assert result.loc[0, "mapping_source"] == "other"
