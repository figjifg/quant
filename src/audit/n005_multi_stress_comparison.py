from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(".")
OUTPUT_DIR = ROOT / "reports/experiments/N005_multi_stress_comparison"

SOURCE_EXPERIMENTS = {
    "N001": ROOT / "reports/experiments/N001_gold_sleeve/delta_vs_baseline.csv",
    "N002": ROOT / "reports/experiments/N002_cash_shy_sleeve/delta_vs_baseline.csv",
    "N003": ROOT / "reports/experiments/N003_duration_mix/delta_vs_baseline.csv",
    "N004": ROOT / "reports/experiments/N004_commodity_dollar_sleeve/delta_vs_baseline.csv",
}

EXPECTED_VARIANTS = [
    "N001-A",
    "N001-B",
    "N002-A",
    "N002-B",
    "N002-C",
    "N003-A",
    "N003-B",
    "N003-C",
    "N004-A",
    "N004-B",
    "N004-C",
]

STRESS_ORDER = [
    "dot_com_proxy_2002_07_2003_12",
    "gfc_proxy_2008_2009",
    "covid_2020_02_2020_03",
    "rate_shock_2022",
]

STRESS_LABELS = {
    "dot_com_proxy_2002_07_2003_12": "dot-com proxy 2002-07~2003-12",
    "gfc_proxy_2008_2009": "GFC proxy 2008-2009",
    "covid_2020_02_2020_03": "COVID 2020-02~2020-03",
    "rate_shock_2022": "2022 rate shock",
}

TOLERANCE_PP = 1e-9


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matrix = build_stress_matrix(load_variant_deltas())
    ranking_by_stress = build_best_ranking_by_stress(matrix)
    overall = build_overall_score_ranking(matrix)
    trade_off = build_trade_off_analysis(matrix)

    matrix.to_csv(OUTPUT_DIR / "all_variants_stress_matrix.csv", index=False)
    ranking_by_stress.to_csv(OUTPUT_DIR / "best_ranking_by_stress.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "overall_score_ranking.csv", index=False)
    trade_off.to_csv(OUTPUT_DIR / "trade_off_analysis.csv", index=False)
    write_report(matrix, ranking_by_stress, overall, trade_off)


def load_variant_deltas() -> pd.DataFrame:
    frames = []
    for experiment, path in SOURCE_EXPERIMENTS.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing source result: {path}")
        data = pd.read_csv(path)
        data["source_experiment"] = experiment
        frames.append(data)

    combined = pd.concat(frames, ignore_index=True)
    variants = combined["variant"].drop_duplicates().tolist()
    if variants != EXPECTED_VARIANTS:
        raise ValueError(f"Unexpected variants. Expected {EXPECTED_VARIANTS}, got {variants}")

    observed_stress = combined["stress_window"].drop_duplicates().tolist()
    if observed_stress != STRESS_ORDER:
        raise ValueError(f"Unexpected stress windows. Expected {STRESS_ORDER}, got {observed_stress}")

    expected_rows = len(EXPECTED_VARIANTS) * len(STRESS_ORDER)
    if len(combined) != expected_rows:
        raise ValueError(f"Expected {expected_rows} variant-stress rows, got {len(combined)}")

    return combined


def build_stress_matrix(data: pd.DataFrame) -> pd.DataFrame:
    rows = data.copy()
    rows["stress_label"] = rows["stress_window"].map(STRESS_LABELS)
    rows["return_improved"] = rows["delta_return_pp"] > TOLERANCE_PP
    rows["mdd_improved"] = rows["delta_mdd_pp"] > TOLERANCE_PP
    rows["return_worsened"] = rows["delta_return_pp"] < -TOLERANCE_PP
    rows["mdd_worsened"] = rows["delta_mdd_pp"] < -TOLERANCE_PP
    rows["stress_order"] = rows["stress_window"].map({name: idx for idx, name in enumerate(STRESS_ORDER)})
    rows["variant_order"] = rows["variant"].map({name: idx for idx, name in enumerate(EXPECTED_VARIANTS)})

    columns = [
        "variant",
        "stress_window",
        "stress_label",
        "measurement_type",
        "total_return",
        "baseline_total_return",
        "delta_return_pp",
        "daily_max_drawdown",
        "baseline_daily_max_drawdown",
        "delta_mdd_pp",
        "return_improved",
        "mdd_improved",
        "return_worsened",
        "mdd_worsened",
        "proxy_excluded_sleeves",
    ]
    return (
        rows.sort_values(["variant_order", "stress_order"])
        .loc[:, columns]
        .reset_index(drop=True)
    )


def build_best_ranking_by_stress(matrix: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stress_window in STRESS_ORDER:
        stress_rows = matrix.loc[matrix["stress_window"].eq(stress_window)].copy()
        stress_rows = stress_rows.sort_values(
            ["delta_mdd_pp", "delta_return_pp", "variant"],
            ascending=[False, False, True],
        ).head(3)
        for rank, row in enumerate(stress_rows.itertuples(index=False), start=1):
            rows.append(
                {
                    "stress_window": row.stress_window,
                    "stress_label": row.stress_label,
                    "rank": rank,
                    "variant": row.variant,
                    "delta_return_pp": row.delta_return_pp,
                    "delta_mdd_pp": row.delta_mdd_pp,
                    "total_return": row.total_return,
                    "daily_max_drawdown": row.daily_max_drawdown,
                    "measurement_type": row.measurement_type,
                    "proxy_excluded_sleeves": row.proxy_excluded_sleeves,
                }
            )
    return pd.DataFrame(rows)


def build_overall_score_ranking(matrix: pd.DataFrame) -> pd.DataFrame:
    scores = (
        matrix.groupby("variant", sort=False)
        .agg(
            return_score_pp=("delta_return_pp", "mean"),
            mdd_score_pp=("delta_mdd_pp", "mean"),
            stress_count=("stress_window", "count"),
            return_improved_count=("return_improved", "sum"),
            mdd_improved_count=("mdd_improved", "sum"),
            return_worsened_count=("return_worsened", "sum"),
            mdd_worsened_count=("mdd_worsened", "sum"),
        )
        .reset_index()
    )
    scores["balanced_score_pp"] = (scores["return_score_pp"] + scores["mdd_score_pp"]) / 2.0
    scores = scores.sort_values(
        ["mdd_score_pp", "return_score_pp", "balanced_score_pp", "variant"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    scores.insert(0, "overall_rank", range(1, len(scores) + 1))
    return scores


def build_trade_off_analysis(matrix: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant, group in matrix.groupby("variant", sort=False):
        improved = group.loc[group["mdd_improved"], "stress_window"].tolist()
        worsened = group.loc[group["mdd_worsened"], "stress_window"].tolist()
        return_improved = group.loc[group["return_improved"], "stress_window"].tolist()
        return_worsened = group.loc[group["return_worsened"], "stress_window"].tolist()
        best = group.sort_values(["delta_mdd_pp", "delta_return_pp"], ascending=[False, False]).iloc[0]
        worst = group.sort_values(["delta_mdd_pp", "delta_return_pp"], ascending=[True, True]).iloc[0]
        rows.append(
            {
                "variant": variant,
                "mdd_improved_stress_count": len(improved),
                "mdd_worsened_stress_count": len(worsened),
                "return_improved_stress_count": len(return_improved),
                "return_worsened_stress_count": len(return_worsened),
                "all_stress_mdd_improved": len(improved) == len(STRESS_ORDER),
                "all_stress_return_improved": len(return_improved) == len(STRESS_ORDER),
                "all_stress_return_and_mdd_improved": (
                    len(improved) == len(STRESS_ORDER) and len(return_improved) == len(STRESS_ORDER)
                ),
                "has_mdd_trade_off": len(improved) > 0 and len(worsened) > 0,
                "has_return_trade_off": len(return_improved) > 0 and len(return_worsened) > 0,
                "mdd_improved_stresses": ";".join(improved),
                "mdd_worsened_stresses": ";".join(worsened),
                "return_improved_stresses": ";".join(return_improved),
                "return_worsened_stresses": ";".join(return_worsened),
                "best_mdd_stress": best["stress_window"],
                "best_mdd_delta_pp": best["delta_mdd_pp"],
                "worst_mdd_stress": worst["stress_window"],
                "worst_mdd_delta_pp": worst["delta_mdd_pp"],
            }
        )
    return pd.DataFrame(rows)


def write_report(
    matrix: pd.DataFrame,
    ranking_by_stress: pd.DataFrame,
    overall: pd.DataFrame,
    trade_off: pd.DataFrame,
) -> None:
    top_overall = overall.iloc[0]
    top_by_stress = ranking_by_stress.loc[ranking_by_stress["rank"].eq(1)].copy()
    all_stress_improvers = trade_off.loc[trade_off["all_stress_return_and_mdd_improved"], "variant"].tolist()
    mdd_tradeoffs = trade_off.loc[trade_off["has_mdd_trade_off"], "variant"].tolist()
    gfc_top = top_by_stress.loc[top_by_stress["stress_window"].eq("gfc_proxy_2008_2009")].iloc[0]
    rate_top = top_by_stress.loc[top_by_stress["stress_window"].eq("rate_shock_2022")].iloc[0]
    covid_top = top_by_stress.loc[top_by_stress["stress_window"].eq("covid_2020_02_2020_03")].iloc[0]
    dotcom_top = top_by_stress.loc[top_by_stress["stress_window"].eq("dot_com_proxy_2002_07_2003_12")].iloc[0]

    lines = [
        "# N005 Multi-stress Comparison",
        "",
        "Status: GENERATED BY `src.audit.n005_multi_stress_comparison`",
        "",
        "## 범위",
        "",
        "- N000 baseline 및 N001-N004의 기존 결과만 로드했다.",
        "- 새 weights grid X. N001-N004의 사전 등록 weights 그대로 사용했다.",
        "- 새 최고 Sharpe 검색 X. Stress response 종합 비교만 수행했다.",
        "- `P08_IEF30` 직접 변경 X, 직접 promote X.",
        "- N-family 결과는 backlog candidate library 전용이다.",
        "- Live deployment 판단은 N-family 결과와 paper tracking 결과를 종합해 별도 결정한다.",
        "",
        "## 11 Variant x 4 Stress 종합 표",
        "",
        table_for_report(
            matrix,
            [
                "variant",
                "stress_label",
                "delta_return_pp",
                "delta_mdd_pp",
                "total_return",
                "daily_max_drawdown",
                "measurement_type",
                "proxy_excluded_sleeves",
            ],
        ),
        "",
        "## Stress별 Best Diversifier",
        "",
        f"- GFC: {gfc_top['variant']} (return {gfc_top['delta_return_pp']:.4f}pp, MDD {gfc_top['delta_mdd_pp']:.4f}pp).",
        f"- 2022 rate shock: {rate_top['variant']} (return {rate_top['delta_return_pp']:.4f}pp, MDD {rate_top['delta_mdd_pp']:.4f}pp).",
        f"- COVID: {covid_top['variant']} (return {covid_top['delta_return_pp']:.4f}pp, MDD {covid_top['delta_mdd_pp']:.4f}pp).",
        f"- Dot-com proxy: {dotcom_top['variant']} (return {dotcom_top['delta_return_pp']:.4f}pp, MDD {dotcom_top['delta_mdd_pp']:.4f}pp).",
        "",
        table_for_report(
            ranking_by_stress,
            [
                "stress_label",
                "rank",
                "variant",
                "delta_return_pp",
                "delta_mdd_pp",
                "measurement_type",
                "proxy_excluded_sleeves",
            ],
        ),
        "",
        "## Multi-stress Overall Ranking",
        "",
        f"- Overall best: {top_overall['variant']} (return score {top_overall['return_score_pp']:.4f}pp, MDD score {top_overall['mdd_score_pp']:.4f}pp).",
        "- Ranking은 diversifier 목적에 맞춰 MDD score 우선, return score 보조 기준으로 정렬했다.",
        "",
        table_for_report(
            overall,
            [
                "overall_rank",
                "variant",
                "return_score_pp",
                "mdd_score_pp",
                "balanced_score_pp",
                "return_improved_count",
                "mdd_improved_count",
                "return_worsened_count",
                "mdd_worsened_count",
            ],
        ),
        "",
        "## Trade-off 분석",
        "",
        f"- TLT 30% variant인 N003-A는 GFC에서 MDD {mdd_delta(matrix, 'N003-A', 'gfc_proxy_2008_2009'):.4f}pp 개선했지만 2022에서 MDD {mdd_delta(matrix, 'N003-A', 'rate_shock_2022'):.4f}pp 악화했다.",
        f"- GLD 10% variant인 N001-B는 GFC MDD {mdd_delta(matrix, 'N001-B', 'gfc_proxy_2008_2009'):.4f}pp, COVID MDD {mdd_delta(matrix, 'N001-B', 'covid_2020_02_2020_03'):.4f}pp, 2022 MDD {mdd_delta(matrix, 'N001-B', 'rate_shock_2022'):.4f}pp 개선했다. Dot-com proxy는 GLD 관측치 부재로 baseline과 사실상 동일한 proxy다.",
        f"- MDD 기준 trade-off variant: {', '.join(mdd_tradeoffs) if mdd_tradeoffs else '없음'}.",
        f"- P08_IEF30 baseline보다 return과 MDD를 모든 stress에서 동시에 개선한 variant: {', '.join(all_stress_improvers) if all_stress_improvers else '없음'}.",
        "",
        table_for_report(
            trade_off,
            [
                "variant",
                "mdd_improved_stress_count",
                "mdd_worsened_stress_count",
                "return_improved_stress_count",
                "return_worsened_stress_count",
                "all_stress_return_and_mdd_improved",
                "has_mdd_trade_off",
                "best_mdd_stress",
                "best_mdd_delta_pp",
                "worst_mdd_stress",
                "worst_mdd_delta_pp",
            ],
        ),
        "",
        "## Verdict",
        "",
        f"- GFC -31% practical hedge: 부분 발견. GFC MDD 기준 1위는 {gfc_top['variant']}로 MDD를 {gfc_top['delta_mdd_pp']:.4f}pp 개선해 -31.27% baseline을 약 {gfc_top['daily_max_drawdown'] * 100.0:.2f}%까지 낮췄지만, drawdown 자체는 여전히 크다.",
        f"- GLD 10%인 N001-B도 GFC return {return_delta(matrix, 'N001-B', 'gfc_proxy_2008_2009'):.4f}pp, MDD {mdd_delta(matrix, 'N001-B', 'gfc_proxy_2008_2009'):.4f}pp 개선으로 유효한 hedge 후보에 남는다.",
        f"- Multi-stress best diversifier candidate는 {top_overall['variant']}다. 단, 이는 `P08_IEF30` 직접 대체가 아니라 backlog candidate library entry다.",
        "- `P08_IEF30` 직접 promote X. Frozen baseline은 유지한다.",
        "- 다음 framework: paper tracking 4분기 이상 지속 + 새 family 검토. N-family 결과와 live paper tracking 결과를 합쳐 production 후보를 재판단한다.",
        "- J-family / K-family / L-family / M-family 우선순위 재평가: K-family를 1순위로 둔다. 2022 stress에서 commodity/dollar와 sector/inflation exposure의 가치가 보였으므로 US sector validation이 가장 직접적이다. J-family는 2순위, L-family는 3순위, M-family는 기존대로 최하위 backlog다.",
        "",
        "## 산출물",
        "",
        "- all_variants_stress_matrix.csv",
        "- best_ranking_by_stress.csv",
        "- overall_score_ranking.csv",
        "- trade_off_analysis.csv",
        "- report.md",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def mdd_delta(matrix: pd.DataFrame, variant: str, stress_window: str) -> float:
    row = matrix.loc[matrix["variant"].eq(variant) & matrix["stress_window"].eq(stress_window)]
    if row.empty:
        raise ValueError(f"Missing matrix row: {variant} {stress_window}")
    return float(row.iloc[0]["delta_mdd_pp"])


def return_delta(matrix: pd.DataFrame, variant: str, stress_window: str) -> float:
    row = matrix.loc[matrix["variant"].eq(variant) & matrix["stress_window"].eq(stress_window)]
    if row.empty:
        raise ValueError(f"Missing matrix row: {variant} {stress_window}")
    return float(row.iloc[0]["delta_return_pp"])


def table_for_report(data: pd.DataFrame, columns: list[str]) -> str:
    rows = data.loc[:, columns].copy()
    for column in rows.columns:
        if pd.api.types.is_float_dtype(rows[column]):
            rows[column] = rows[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.6f}")
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join("" if pd.isna(value) else str(value) for value in row) + " |"
        for row in rows.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *body])


if __name__ == "__main__":
    main()
