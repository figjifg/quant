from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import pandas as pd
import yaml


OTHER_CODE = "99"


@dataclass(frozen=True)
class SectorMapping:
    groups: Mapping[str, str]
    manual_override: Mapping[str, str]
    non_industry_kis_codes: frozenset[str]
    kis_mcls_mapping: Mapping[str, str]
    ksic_code_mapping: Mapping[str, str]

    @property
    def mapped_group_codes(self) -> set[str]:
        return set(self.groups) - {OTHER_CODE}


def load_sector_mapping(path: str | Path) -> SectorMapping:
    with Path(path).open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    groups = _string_mapping(raw["groups"])
    manual_override = _string_mapping(raw.get("manual_override", {}))
    non_industry_kis_codes = frozenset(str(value) for value in raw.get("non_industry_kis_codes", []))
    kis_mcls_mapping = _string_mapping(raw["kis_mcls_mapping"])
    ksic_code_mapping = _string_mapping(raw["ksic_code_mapping"])
    valid_codes = set(groups)
    invalid = sorted(
        {
            *set(manual_override.values()),
            *set(kis_mcls_mapping.values()),
            *set(ksic_code_mapping.values()),
        }
        - valid_codes
    )
    if invalid:
        raise ValueError(f"Unknown sector group codes in mapping: {invalid}")

    return SectorMapping(
        groups=groups,
        manual_override=manual_override,
        non_industry_kis_codes=non_industry_kis_codes,
        kis_mcls_mapping=kis_mcls_mapping,
        ksic_code_mapping=ksic_code_mapping,
    )


def apply_sector_mapping(snapshot: pd.DataFrame, mapping: SectorMapping) -> pd.DataFrame:
    required = {
        "pdno",
        "prdt_name",
        "idx_bztp_mcls_cd_name",
        "std_idst_clsf_cd",
        "std_idst_clsf_cd_name",
    }
    missing = sorted(required - set(snapshot.columns))
    if missing:
        raise ValueError(f"Snapshot is missing required columns: {missing}")

    rows = snapshot.copy()
    rows["ticker"] = rows["pdno"].astype("string").str.extract(r"(\d{6})$", expand=False)
    rows["ksic_code"] = rows["std_idst_clsf_cd"].map(_normalize_code)
    manual_codes = rows["ticker"].map(mapping.manual_override)
    industry_kis = ~rows["idx_bztp_mcls_cd_name"].isin(mapping.non_industry_kis_codes)
    kis_codes = rows["idx_bztp_mcls_cd_name"].where(industry_kis).map(mapping.kis_mcls_mapping)
    ksic_codes = rows["ksic_code"].map(mapping.ksic_code_mapping)
    rows["final_sector_code"] = manual_codes.fillna(kis_codes).fillna(ksic_codes).fillna(OTHER_CODE)
    rows["final_sector_name"] = rows["final_sector_code"].map(mapping.groups)
    rows["mapping_source"] = "other"
    rows.loc[ksic_codes.notna(), "mapping_source"] = "ksic_fallback"
    rows.loc[kis_codes.notna(), "mapping_source"] = "kis_mcls"
    rows.loc[manual_codes.notna(), "mapping_source"] = "manual_override"

    return rows[
        [
            "pdno",
            "ticker",
            "prdt_name",
            "idx_bztp_mcls_cd_name",
            "std_idst_clsf_cd_name",
            "final_sector_code",
            "final_sector_name",
            "mapping_source",
        ]
    ].rename(columns={"idx_bztp_mcls_cd_name": "kis_mcls", "std_idst_clsf_cd_name": "ksic"})


def _string_mapping(raw: Mapping[object, object]) -> dict[str, str]:
    return {str(key): str(value) for key, value in raw.items()}


def _normalize_code(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text.zfill(6) if text.isdigit() else text
