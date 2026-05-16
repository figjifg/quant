from __future__ import annotations

import pandas as pd

from src.roles.filters import (
    filter_relative_flow_sign_both_positive,
    filter_relative_flow_sign_both_positive_z,
)


def test_filter_relative_flow_sign_both_positive_z_requires_both_positive() -> None:
    data = pd.DataFrame(
        {
            "종목코드": ["000010", "000020", "000030", "000040"],
            "fnv_5_z": [0.1, 0.1, 0.0, pd.NA],
            "inv_5_z": [0.2, -0.2, 0.2, 0.2],
        }
    )

    result = filter_relative_flow_sign_both_positive_z(data)

    assert list(result["종목코드"]) == ["000010"]


def test_filter_relative_flow_sign_both_positive_requires_both_positive() -> None:
    data = pd.DataFrame(
        {
            "종목코드": ["000010", "000020", "000030", "000040"],
            "fnv_5_rel": [0.1, 0.1, 0.0, pd.NA],
            "inv_5_rel": [0.2, -0.2, 0.2, 0.2],
        }
    )

    result = filter_relative_flow_sign_both_positive(data)

    assert list(result["종목코드"]) == ["000010"]
