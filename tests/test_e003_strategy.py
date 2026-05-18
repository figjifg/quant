from __future__ import annotations

import pandas as pd
import pytest

from src.strategies.e003_b_count_matched import build_count_matched_sector_candidates
from src.strategies.e003_c_pure_basket import build_pure_sector_basket_candidates


def _panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "날짜": [pd.Timestamp("2025-03-31")] * 8,
            "종목코드": ["000001", "000002", "000003", "000004", "000005", "000006", "000007", "000008"],
            "KRX종가": [100.0] * 8,
            "상장주식수": [1000, 900, 800, 700, 600, 500, 400, 300],
        }
    )


def _universe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "signal_date": [pd.Timestamp("2025-03-31")] * 8,
            "execution_date": [pd.Timestamp("2025-04-01")] * 8,
            "종목코드": ["000001", "000002", "000003", "000004", "000005", "000006", "000007", "000008"],
        }
    )


def _quarterly_regime(regime_on: bool = True) -> pd.DataFrame:
    return pd.DataFrame({"signal_date": [pd.Timestamp("2025-03-31")], "regime_on": [regime_on]})


def _mapping() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["000001", "000002", "000003", "000004", "000005", "000006", "000007", "000008"],
            "final_sector_code": ["01", "01", "02", "03", "03", "03", "99", "04"],
            "final_sector_name": ["IT", "IT", "Auto", "Chem", "Chem", "Chem", "Other", "Steel"],
        }
    )


def test_count_matched_takes_at_most_one_name_per_sector_by_market_cap_order() -> None:
    result = build_count_matched_sector_candidates(_panel(), _universe(), _quarterly_regime(), _mapping(), max_positions=4)

    assert list(result["종목코드"]) == ["000001", "000003", "000004", "000007"]
    assert list(result["sector_code"]) == ["01", "02", "03", "99"]
    assert result["sector_code"].is_unique


def test_count_matched_gate_off_returns_no_candidates() -> None:
    result = build_count_matched_sector_candidates(
        _panel(),
        _universe(),
        _quarterly_regime(regime_on=False),
        _mapping(),
        max_positions=4,
    )

    assert result.empty


def test_pure_basket_excludes_other_and_thin_sectors_then_sector_equal_weights() -> None:
    result = build_pure_sector_basket_candidates(
        _panel(),
        _universe(),
        _quarterly_regime(),
        _mapping(),
        min_sector_members=2,
    )

    assert set(result["sector_code"]) == {"01", "03"}
    sector_weights = result.groupby("sector_code")["target_weight"].sum()
    assert sector_weights.to_dict() == pytest.approx({"01": 0.5, "03": 0.5})
    chem = result.loc[result["sector_code"].eq("03")].set_index("종목코드")["target_weight"]
    assert chem["000004"] > chem["000005"] > chem["000006"]


def test_pure_basket_requires_minimum_sector_members() -> None:
    result = build_pure_sector_basket_candidates(
        _panel(),
        _universe(),
        _quarterly_regime(),
        _mapping(),
        min_sector_members=3,
    )

    assert set(result["sector_code"]) == {"03"}
    assert result["target_weight"].sum() == pytest.approx(1.0)
