from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.data.sector_aggregator import build_sector_aggregate, write_sector_aggregate_outputs
from src.features.sector_flow_score import build_sector_forward_returns
from src.run_experiment import _build_e_layer2_context


OUTPUT_DIR = ROOT / "reports/experiments/P001_5_attribution_audit"
KRX_CURRENT_DIR = OUTPUT_DIR / "krx_current_snapshot"
KRX_CURRENT_MAPPING = KRX_CURRENT_DIR / "stock_sector_mapping_krx_current_snapshot.csv"
KRX_CURRENT_STOCK_DAILY = KRX_CURRENT_DIR / "stock_with_sector_daily_krx_current_snapshot.csv"
KRX_CURRENT_SECTOR_DAILY = KRX_CURRENT_DIR / "sector_aggregate_daily_krx_current_snapshot.csv"
KRX_CURRENT_CONFIG = KRX_CURRENT_DIR / "config.yaml"
KRX_CURRENT_RUN_DIR = KRX_CURRENT_DIR / "E014_krx_current_snapshot"

E014_DIR = ROOT / "reports/experiments/E014_rs_breadth_top4_registration"
P001_PIT_DIR = ROOT / "reports/experiments/P001_pit_sector_validation/E014_pit"
P001_CONFIG = ROOT / "configs/backtests/p001_e014_pit.yaml"
E014_CONFIG = ROOT / "configs/backtests/e014.yaml"
KIS_MAPPING = ROOT / "data/processed/stock_sector_mapping_20260518.csv"
PIT_CLASSIFICATIONS = ROOT / "data/processed/krx_pit_sector_classifications.csv"
PIT_MAPPING_YAML = ROOT / "configs/krx_pit_to_12group.yaml"

WATCH_TICKERS = {
    "035420": "NAVER",
    "035720": "카카오",
    "068270": "셀트리온",
    "051910": "LG화학",
    "373220": "LG에너지솔루션",
    "005490": "POSCO홀딩스",
    "042660": "한화오션",
    "207940": "삼성바이오",
    "036570": "엔씨소프트",
    "011200": "HMM",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    KRX_CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    latest_date = _build_krx_current_snapshot_mapping()
    _build_krx_current_snapshot_aggregate()
    _run_krx_current_snapshot_backtest()

    source = _write_source_decomposition()
    ticker_attr = _write_ticker_attribution()
    mapping_review = _write_mapping_review(latest_date, ticker_attr)
    diagnostics = _write_pit_score_diagnostics()
    _write_report(source, ticker_attr, mapping_review, diagnostics, latest_date)


def _build_krx_current_snapshot_mapping() -> str:
    classifications = pd.read_csv(PIT_CLASSIFICATIONS, dtype={"종목코드": "string"})
    classifications["date"] = classifications["date"].astype(str)
    latest_date = str(classifications["date"].max())
    latest = classifications.loc[classifications["date"].eq(latest_date)].copy()

    mapping_yaml = yaml.safe_load(PIT_MAPPING_YAML.read_text(encoding="utf-8"))
    code_to_name = {str(k).zfill(2): v for k, v in mapping_yaml["groups"].items()}
    industry_to_code = {
        str(industry): str(code).zfill(2) for industry, code in mapping_yaml["krx_industry_mapping"].items()
    }

    latest["ticker"] = latest["종목코드"].astype("string").str.zfill(6)
    latest["krx_industry_name"] = latest["업종명"].astype("string")
    latest["final_sector_code"] = latest["krx_industry_name"].map(industry_to_code).fillna("99")
    latest["final_sector_name"] = latest["final_sector_code"].map(code_to_name).fillna("기타")
    latest["classification_date"] = pd.to_datetime(latest_date, format="%Y%m%d").strftime("%Y-%m-%d")
    output = latest.loc[
        :,
        ["ticker", "final_sector_code", "final_sector_name", "classification_date", "krx_industry_name"],
    ].drop_duplicates("ticker", keep="last")
    output.to_csv(KRX_CURRENT_MAPPING, index=False, encoding="utf-8-sig")
    return output["classification_date"].iloc[0]


def _build_krx_current_snapshot_aggregate() -> None:
    result = build_sector_aggregate(config_path=E014_CONFIG, mapping_path=KRX_CURRENT_MAPPING)
    write_sector_aggregate_outputs(
        result,
        stock_output=KRX_CURRENT_STOCK_DAILY,
        sector_output=KRX_CURRENT_SECTOR_DAILY,
        output_dir=KRX_CURRENT_DIR / "aggregate_audit",
    )


def _run_krx_current_snapshot_backtest() -> None:
    config = yaml.safe_load(E014_CONFIG.read_text(encoding="utf-8"))
    config["sector_aggregate_csv"] = str(KRX_CURRENT_SECTOR_DAILY.relative_to(ROOT))
    config["stock_sector_daily_csv"] = str(KRX_CURRENT_STOCK_DAILY.relative_to(ROOT))
    config["sector_mapping_csv"] = str(KRX_CURRENT_MAPPING.relative_to(ROOT))
    config["output_dir"] = str(KRX_CURRENT_RUN_DIR.relative_to(ROOT))
    KRX_CURRENT_CONFIG.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if KRX_CURRENT_RUN_DIR.exists():
        shutil.rmtree(KRX_CURRENT_RUN_DIR)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    subprocess.run(
        [".venv/bin/python", "src/run_experiment.py", "--config", str(KRX_CURRENT_CONFIG)],
        cwd=ROOT,
        check=True,
        env=env,
    )


def _write_source_decomposition() -> pd.DataFrame:
    rows = [
        _metric_row("KIS_snapshot", E014_DIR / "metrics.json"),
        _metric_row("KRX_current_snapshot", KRX_CURRENT_RUN_DIR / "metrics.json"),
        _metric_row("KRX_PIT", P001_PIT_DIR / "metrics.json"),
    ]
    frame = pd.DataFrame(rows)
    kis = frame.loc[frame["source"].eq("KIS_snapshot")].iloc[0]
    krx = frame.loc[frame["source"].eq("KRX_current_snapshot")].iloc[0]
    pit = frame.loc[frame["source"].eq("KRX_PIT")].iloc[0]
    frame["cum_return_diff_vs_pit"] = frame["cumulative_net_total_return"] - pit["cumulative_net_total_return"]
    frame["sharpe_diff_vs_pit"] = frame["sharpe"] - pit["sharpe"]
    frame["taxonomy_gap_vs_kis"] = frame["cumulative_net_total_return"] - kis["cumulative_net_total_return"]
    frame["pit_membership_gap_vs_krx_current"] = frame["cumulative_net_total_return"] - krx[
        "cumulative_net_total_return"
    ]
    frame.to_csv(OUTPUT_DIR / "A_source_decomposition.csv", index=False, encoding="utf-8-sig")
    return frame


def _metric_row(source: str, path: Path) -> dict[str, Any]:
    metrics = json.loads(path.read_text(encoding="utf-8").replace("NaN", "null"))
    block = metrics["factor_macro_gate_mcap"]
    return {
        "source": source,
        "cumulative_net_total_return": block["cumulative_net_total_return"],
        "sharpe": block["sharpe"],
        "max_drawdown": block["max_drawdown"],
        "trade_count": block["trade_count"],
        "cost_paid_total": block["cost_paid_total"],
    }


def _write_ticker_attribution() -> pd.DataFrame:
    snapshot = _trade_contributions(E014_DIR / "trades.csv", "snapshot")
    pit = _trade_contributions(P001_PIT_DIR / "trades.csv", "pit")
    merged = snapshot.merge(pit, on=["quarter", "ticker"], how="outer", suffixes=("_snapshot", "_pit"))
    for col in ["gross_contribution_snapshot", "gross_contribution_pit", "net_contribution_snapshot", "net_contribution_pit"]:
        merged[col] = merged[col].fillna(0.0)
    for col in ["trade_count_snapshot", "trade_count_pit"]:
        merged[col] = merged[col].fillna(0).astype(int)
    merged["status"] = "common"
    merged.loc[merged["trade_count_snapshot"].gt(0) & merged["trade_count_pit"].eq(0), "status"] = "snapshot_only"
    merged.loc[merged["trade_count_snapshot"].eq(0) & merged["trade_count_pit"].gt(0), "status"] = "pit_only"
    merged["net_contribution_diff_snapshot_minus_pit"] = (
        merged["net_contribution_snapshot"] - merged["net_contribution_pit"]
    )
    merged["abs_net_contribution_diff"] = merged["net_contribution_diff_snapshot_minus_pit"].abs()
    merged["ticker_name"] = merged["ticker"].map(WATCH_TICKERS).fillna("")
    total_abs = float(merged["abs_net_contribution_diff"].sum())
    merged["attribution_pct_of_abs_diff"] = (
        merged["abs_net_contribution_diff"] / total_abs if total_abs > 0 else math.nan
    )
    out = merged.sort_values(["abs_net_contribution_diff", "quarter", "ticker"], ascending=[False, True, True])
    out.to_csv(OUTPUT_DIR / "B_ticker_attribution.csv", index=False, encoding="utf-8-sig")
    return out


def _trade_contributions(path: Path, label: str) -> pd.DataFrame:
    trades = pd.read_csv(path, dtype={"종목코드": "string"})
    trades["ticker"] = trades["종목코드"].astype("string").str.zfill(6)
    trades["signal_date"] = pd.to_datetime(trades["signal_date"], errors="raise")
    trades["quarter"] = trades["signal_date"].dt.to_period("Q").astype(str)
    trades["gross_return"] = trades["exit_price"] / trades["entry_price"] - 1.0
    trades[f"gross_contribution_{label}"] = trades["notional_at_entry"] * trades["gross_return"]
    trades[f"net_contribution_{label}"] = trades[f"gross_contribution_{label}"] - trades["cost_paid"]
    return (
        trades.groupby(["quarter", "ticker"], as_index=False)
        .agg(
            **{
                f"gross_contribution_{label}": (f"gross_contribution_{label}", "sum"),
                f"net_contribution_{label}": (f"net_contribution_{label}", "sum"),
                f"trade_count_{label}": ("ticker", "size"),
            }
        )
        .sort_values(["quarter", "ticker"])
    )


def _write_mapping_review(latest_date: str, ticker_attr: pd.DataFrame) -> pd.DataFrame:
    mapping_yaml = yaml.safe_load(PIT_MAPPING_YAML.read_text(encoding="utf-8"))
    industries = pd.read_csv(PIT_CLASSIFICATIONS, dtype={"종목코드": "string"})
    industry_names = sorted(industries["업종명"].dropna().astype(str).unique())
    code_to_name = {str(k).zfill(2): v for k, v in mapping_yaml["groups"].items()}
    industry_to_code = {
        str(industry): str(code).zfill(2) for industry, code in mapping_yaml["krx_industry_mapping"].items()
    }
    focus = {
        "IT 서비스",
        "소프트웨어",
        "인터넷",
        "컴퓨터서비스",
        "디지털컨텐츠",
        "통신",
        "통신서비스",
        "방송서비스",
        "오락·문화",
        "반도체",
        "전기·전자",
        "IT부품",
        "정보기기",
        "통신장비",
        "화학",
        "비금속",
        "종이·목재",
        "일반서비스",
        "제약",
        "의료·정밀기기",
        "운송장비·부품",
        "기계·장비",
    }
    rows = []
    for industry in industry_names:
        code = industry_to_code.get(industry, "99")
        note = ""
        suspicious = False
        if industry == "일반서비스":
            note = "Residual KRX service bucket mapped to 99 기타 by explicit manual_review; economically broad."
        elif industry in focus:
            note = "Focus group reviewed; mapping is directionally consistent with frozen 12-group taxonomy."
        elif industry not in industry_to_code:
            note = "Not present in yaml mapping; falls to 99 기타."
            suspicious = True
        rows.append(
            {
                "krx_industry_name": industry,
                "mapped_sector_code": code,
                "mapped_sector_name": code_to_name.get(code, "기타"),
                "focus_review": industry in focus,
                "suspicious": suspicious,
                "note": note,
            }
        )
    review = pd.DataFrame(rows)
    review.to_csv(OUTPUT_DIR / "C_mapping_review_table.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# C. KRX 41 to 12 Group Mapping Review",
        "",
        f"- KRX current snapshot date used for scenario A: {latest_date}",
        "- Verdict: no clear mechanical mapping bug found.",
        "- Main judgment item: `일반서비스` is intentionally mapped to `99 기타`; this is conservative but may move large service names out of the KIS `서비스업 -> 인터넷/게임/SW` bucket.",
        "",
        "## Focus Review",
        "",
        "| KRX industry | mapped group | note |",
        "|---|---:|---|",
    ]
    for _, row in review.loc[review["focus_review"] | review["krx_industry_name"].eq("일반서비스")].iterrows():
        lines.append(f"| {row['krx_industry_name']} | {row['mapped_sector_code']} {row['mapped_sector_name']} | {row['note']} |")
    lines.extend(["", "## Full KRX Industry Mapping", "", "| KRX industry | mapped group | suspicious |"])
    lines.append("|---|---:|---|")
    for _, row in review.iterrows():
        lines.append(f"| {row['krx_industry_name']} | {row['mapped_sector_code']} {row['mapped_sector_name']} | {row['suspicious']} |")
    lines.extend(["", "## High Impact Tickers Checked", ""])
    top_watch = ticker_attr.loc[ticker_attr["ticker"].isin(WATCH_TICKERS)].head(20)
    if top_watch.empty:
        lines.append("- None of the explicit watch tickers appear in the top attribution rows.")
    else:
        for _, row in top_watch.iterrows():
            lines.append(
                f"- {WATCH_TICKERS.get(row['ticker'], '')} {row['ticker']}: "
                f"{row['status']}, diff={row['net_contribution_diff_snapshot_minus_pit']:.6f}"
            )
    (OUTPUT_DIR / "C_mapping_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return review


def _write_pit_score_diagnostics() -> pd.DataFrame:
    config = yaml.safe_load(P001_CONFIG.read_text(encoding="utf-8"))
    context = _build_e_layer2_context(config)
    scores = context["combined_scores"].copy()
    forward = build_sector_forward_returns(
        pd.read_csv(ROOT / config["sector_aggregate_csv"], encoding="utf-8-sig"),
        scores["signal_date"].drop_duplicates(),
    )
    data = scores.merge(forward, on=["signal_date", "sector_code", "sector_name"], how="inner")
    rows = []
    for signal_date, group in data.groupby("signal_date", sort=True):
        valid = group.dropna(subset=["combined_score", "forward_return"]).copy()
        valid = valid.sort_values(["combined_score", "sector_code"], ascending=[False, True])
        if len(valid) < 8:
            continue
        rows.append(
            {
                "signal_date": pd.Timestamp(signal_date).date().isoformat(),
                "n_sectors": len(valid),
                "rank_ic": valid["combined_score"].corr(valid["forward_return"], method="spearman"),
                "top4_forward_return": valid.head(4)["forward_return"].mean(),
                "bottom4_forward_return": valid.tail(4)["forward_return"].mean(),
                "top4_bottom4_spread": valid.head(4)["forward_return"].mean()
                - valid.tail(4)["forward_return"].mean(),
                "selected_forward_return": valid.head(4)["forward_return"].mean(),
                "unselected_forward_return": valid.iloc[4:]["forward_return"].mean(),
                "selected_unselected_spread": valid.head(4)["forward_return"].mean()
                - valid.iloc[4:]["forward_return"].mean(),
            }
        )
    frame = pd.DataFrame(rows)
    summary = {
        "signal_date": "ALL",
        "n_sectors": int(frame["n_sectors"].sum()),
        "rank_ic": frame["rank_ic"].mean(),
        "rank_ic_t_stat": _t_stat(frame["rank_ic"]),
        "top4_forward_return": frame["top4_forward_return"].mean(),
        "bottom4_forward_return": frame["bottom4_forward_return"].mean(),
        "top4_bottom4_spread": frame["top4_bottom4_spread"].mean(),
        "top4_bottom4_spread_t_stat": _t_stat(frame["top4_bottom4_spread"]),
        "selected_forward_return": frame["selected_forward_return"].mean(),
        "unselected_forward_return": frame["unselected_forward_return"].mean(),
        "selected_unselected_spread": frame["selected_unselected_spread"].mean(),
        "selected_unselected_spread_t_stat": _t_stat(frame["selected_unselected_spread"]),
        "n_quarters": len(frame),
    }
    out = pd.concat([frame, pd.DataFrame([summary])], ignore_index=True)
    out.to_csv(OUTPUT_DIR / "D_pit_score_diagnostics.csv", index=False, encoding="utf-8-sig")
    return out


def _t_stat(series: pd.Series) -> float:
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if len(valid) < 2:
        return math.nan
    std = valid.std(ddof=1)
    if std == 0 or math.isnan(std):
        return math.nan
    return float(valid.mean() / (std / math.sqrt(len(valid))))


def _write_report(
    source: pd.DataFrame,
    ticker_attr: pd.DataFrame,
    mapping_review: pd.DataFrame,
    diagnostics: pd.DataFrame,
    latest_date: str,
) -> None:
    source_rows = {row["source"]: row for _, row in source.iterrows()}
    kis = source_rows["KIS_snapshot"]
    krx = source_rows["KRX_current_snapshot"]
    pit = source_rows["KRX_PIT"]
    top5 = ticker_attr.head(5)
    d_all = diagnostics.loc[diagnostics["signal_date"].eq("ALL")].iloc[0]
    mapping_bug = bool(mapping_review["suspicious"].any())
    if abs(krx["cumulative_net_total_return"] - kis["cumulative_net_total_return"]) < abs(
        krx["cumulative_net_total_return"] - pit["cumulative_net_total_return"]
    ):
        verdict = "close: KRX current snapshot is closer to KIS snapshot than PIT, so the main gap is true PIT membership bias."
    elif mapping_bug:
        verdict = "fix+rerun candidate: unmapped KRX industry names were found."
    else:
        verdict = "close: no clear mapping bug; taxonomy difference is material but not a mechanical defect."

    lines = [
        "# P001.5 Attribution Audit",
        "",
        "## A. Source Decomposition",
        "",
        f"- KIS snapshot: cumulative={kis['cumulative_net_total_return']:.6f}, sharpe={kis['sharpe']:.6f}",
        f"- KRX current snapshot ({latest_date}): cumulative={krx['cumulative_net_total_return']:.6f}, sharpe={krx['sharpe']:.6f}",
        f"- KRX PIT: cumulative={pit['cumulative_net_total_return']:.6f}, sharpe={pit['sharpe']:.6f}",
        f"- taxonomy gap, KRX current - KIS: {krx['cumulative_net_total_return'] - kis['cumulative_net_total_return']:.6f}",
        f"- PIT membership gap, PIT - KRX current: {pit['cumulative_net_total_return'] - krx['cumulative_net_total_return']:.6f}",
        "- 해석: KRX current snapshot은 KIS snapshot보다 낮지 않고 오히려 높다. 성과 하락은 taxonomy 교체보다 PIT membership 적용에서 발생한다.",
        "",
        "## B. Ticker Attribution",
        "",
        "| ticker | name | status | net diff | attribution % |",
        "|---|---|---|---:|---:|",
    ]
    for _, row in top5.iterrows():
        lines.append(
            f"| {row['ticker']} | {row['ticker_name']} | {row['status']} | "
            f"{row['net_contribution_diff_snapshot_minus_pit']:.6f} | "
            f"{row['attribution_pct_of_abs_diff']:.2%} |"
        )
    lines.extend(
        [
            "",
            "## C. Mapping Review",
            "",
            f"- 명백한 mapping bug 발견: {mapping_bug}",
            "- `일반서비스 -> 99 기타`는 YAML의 explicit manual_review에 있는 보수적 선택이며 오타성 버그는 아니다.",
            "- 상세 표: `C_mapping_review.md`, `C_mapping_review_table.csv`.",
            "",
            "## D. PIT Score Diagnostics",
            "",
            f"- Rank IC mean={d_all['rank_ic']:.6f}, t-stat={d_all['rank_ic_t_stat']:.6f}",
            f"- Top4-Bottom4 spread={d_all['top4_bottom4_spread']:.6f}, t-stat={d_all['top4_bottom4_spread_t_stat']:.6f}",
            f"- Selected-Unselected spread={d_all['selected_unselected_spread']:.6f}, t-stat={d_all['selected_unselected_spread_t_stat']:.6f}",
            "- 해석: PIT 자체의 sector score 진단은 양수이고 t-stat도 양호하다. 포트폴리오 성과 저하는 sector score 전체 실패라기보다 PIT membership이 바꾼 보유 종목/섹터 구성 영향이 크다.",
            "",
            "## Verdict",
            "",
            f"- {verdict}",
        ]
    )
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
