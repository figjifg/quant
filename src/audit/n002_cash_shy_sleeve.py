from __future__ import annotations

from src.audit.n_family_stress import run_experiment


VARIANTS = {
    "N002-A": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "SHY": 0.30},
    "N002-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "cash": 0.10},
    "N002-C": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.15, "SHY": 0.15},
}


def main() -> None:
    run_experiment(
        experiment_id="N002",
        slug="cash_shy_sleeve",
        title="N002 Cash / SHY Sleeve",
        variants=VARIANTS,
        hypotheses=[
            "SHY may have lower duration risk than IEF.",
            "Cash/SHY may provide better 2022 rate-shock defense than IEF 30%.",
        ],
        emphasis=["Cash return은 FRED IR3TIB01KRM156N 로컬 파일 기반 KR 단기금리 carry로 계산했다."],
    )


if __name__ == "__main__":
    main()
