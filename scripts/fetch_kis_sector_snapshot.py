#!/usr/bin/env python3
"""Fetch a KIS sector mapping snapshot for E000 layer-2 data inventory."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.kis_sector_fetcher import (  # noqa: E402
    SECTOR_FIELD_NAMES,
    KISSectorClient,
    listing_related_fields,
    normalize_ticker,
    parse_env_file,
)


PANEL_PATHS = [
    ROOT / "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv",
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv",
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
]
REPORT_DIR = ROOT / "reports/experiments/E000_layer2_data_inventory"
PROCESSED_DIR = ROOT / "data/processed"
ENV_PATH = ROOT / "research_input_data/.env"


def load_panel_universe(panel_path: Path) -> pd.DataFrame:
    usecols = [
        "날짜",
        "종목코드",
        "종목명",
        "동적유니버스포함",
        "시가총액추정",
        "KRX종가",
        "외국인순매매량",
        "외국인순매수금액추정",
    ]
    available = pd.read_csv(panel_path, nrows=0).columns.tolist()
    existing_usecols = [col for col in usecols if col in available]
    dtype = {"종목코드": "string"} if "종목코드" in existing_usecols else None
    frame = pd.read_csv(panel_path, usecols=existing_usecols, dtype=dtype)
    universe_flag = frame["동적유니버스포함"]
    if universe_flag.dtype == object:
        universe_flag = universe_flag.astype(str).str.lower().isin({"true", "1", "yes"})
    frame = frame[universe_flag.astype(bool)].copy()
    frame["panel"] = panel_path.name
    frame["종목코드"] = frame["종목코드"].map(normalize_ticker)
    frame["날짜"] = pd.to_datetime(frame["날짜"]).dt.strftime("%Y-%m-%d")
    return frame


def load_all_panel_rows(panel_paths: list[Path]) -> pd.DataFrame:
    frames = [load_panel_universe(path) for path in panel_paths]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def latest_names_by_ticker(rows: pd.DataFrame) -> dict[str, str]:
    if rows.empty:
        return {}
    names = rows.sort_values("날짜").dropna(subset=["종목명"])
    return names.groupby("종목코드")["종목명"].last().to_dict()


def build_snapshot_rows(
    tickers: list[str],
    client: KISSectorClient,
    *,
    rate_sleep_seconds: float,
    abort_after_consecutive_failures: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    consecutive_network_failures = 0
    for index, ticker in enumerate(tickers, start=1):
        result = client.fetch_stock_info(ticker)
        fetched_at = datetime.now(timezone.utc).isoformat()
        output = result.output
        row: dict[str, Any] = {
            "pdno": output.get("pdno", ticker),
            "fetch_status": result.fetch_status,
            "fetch_timestamp": fetched_at,
            "http_status_code": result.http_status_code,
            "error_message": result.error_message,
        }
        for field_name in SECTOR_FIELD_NAMES:
            row[field_name] = output.get(field_name, row.get(field_name, ""))
        row.update(listing_related_fields(output))
        rows.append(row)

        print(
            f"[{index}/{len(tickers)}] {ticker} {result.fetch_status} "
            f"http={result.http_status_code}",
            flush=True,
        )
        if result.fetch_status == "fail" and result.http_status_code is None:
            consecutive_network_failures += 1
            if consecutive_network_failures >= abort_after_consecutive_failures:
                raise RuntimeError(
                    "KIS API calls failed without HTTP status for "
                    f"{consecutive_network_failures} consecutive tickers"
                )
        else:
            consecutive_network_failures = 0
        if index < len(tickers):
            time.sleep(rate_sleep_seconds)
    return rows


def write_snapshot(rows: list[dict[str, Any]], snapshot_path: Path) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    stable_columns = [
        *SECTOR_FIELD_NAMES,
        *sorted(
            col
            for col in frame.columns
            if col not in {*SECTOR_FIELD_NAMES, "fetch_status", "fetch_timestamp", "http_status_code", "error_message"}
        ),
        "fetch_status",
        "fetch_timestamp",
        "http_status_code",
        "error_message",
    ]
    stable_columns = list(dict.fromkeys(stable_columns))
    frame = frame.reindex(columns=stable_columns)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(snapshot_path, index=False)
    return frame


def compute_coverage(panel_rows: pd.DataFrame, snapshot: pd.DataFrame) -> pd.DataFrame:
    success_tickers = set(
        snapshot.loc[snapshot["fetch_status"].eq("success"), "pdno"].map(normalize_ticker)
    )
    rows = panel_rows.copy()
    rows["has_sector_mapping"] = rows["종목코드"].isin(success_tickers)
    rows["시가총액추정"] = pd.to_numeric(rows["시가총액추정"], errors="coerce")

    coverage_rows: list[dict[str, Any]] = []
    grouped = rows.groupby(["panel", "날짜"], sort=True)
    for (panel_name, date), group in grouped:
        top100_count = int(group["종목코드"].nunique())
        matched_count = int(group.loc[group["has_sector_mapping"], "종목코드"].nunique())
        total_mcap = group.drop_duplicates("종목코드")["시가총액추정"].sum(min_count=1)
        matched_mcap = (
            group.loc[group["has_sector_mapping"]]
            .drop_duplicates("종목코드")["시가총액추정"]
            .sum(min_count=1)
        )
        coverage_rows.append(
            {
                "panel": panel_name,
                "rebalance_date": date,
                "top100_count": top100_count,
                "sector_matched_count": matched_count,
                "count_coverage_pct": matched_count / top100_count * 100 if top100_count else 0.0,
                "mcap_coverage_pct": matched_mcap / total_mcap * 100 if total_mcap else 0.0,
            }
        )
    return pd.DataFrame(coverage_rows)


def compute_missing_report(panel_rows: pd.DataFrame, snapshot: pd.DataFrame) -> pd.DataFrame:
    success_tickers = set(
        snapshot.loc[snapshot["fetch_status"].eq("success"), "pdno"].map(normalize_ticker)
    )
    rows = panel_rows.copy()
    rows["시가총액추정"] = pd.to_numeric(rows["시가총액추정"], errors="coerce")
    rows["mcap_rank"] = rows.groupby(["panel", "날짜"])["시가총액추정"].rank(
        ascending=False,
        method="min",
    )
    rows["has_price_data"] = pd.to_numeric(rows.get("KRX종가"), errors="coerce").notna()
    foreign_cols = [col for col in ["외국인순매매량", "외국인순매수금액추정"] if col in rows.columns]
    if foreign_cols:
        rows["has_foreign_flow_data"] = rows[foreign_cols].notna().any(axis=1)
    else:
        rows["has_foreign_flow_data"] = False

    missing = rows[~rows["종목코드"].isin(success_tickers)]
    if missing.empty:
        return pd.DataFrame(
            columns=[
                "종목코드",
                "종목명",
                "appearing_panels",
                "top100_appearance_count",
                "best_mcap_rank",
                "has_price_data",
                "has_foreign_flow_data",
            ]
        )

    report_rows: list[dict[str, Any]] = []
    for ticker, group in missing.groupby("종목코드", sort=True):
        latest = group.sort_values("날짜").iloc[-1]
        report_rows.append(
            {
                "종목코드": ticker,
                "종목명": latest.get("종목명", ""),
                "appearing_panels": ";".join(sorted(group["panel"].unique())),
                "top100_appearance_count": int(group[["panel", "날짜"]].drop_duplicates().shape[0]),
                "best_mcap_rank": int(group["mcap_rank"].min()) if group["mcap_rank"].notna().any() else "",
                "has_price_data": bool(group["has_price_data"].any()),
                "has_foreign_flow_data": bool(group["has_foreign_flow_data"].any()),
            }
        )
    return pd.DataFrame(report_rows).sort_values(
        ["top100_appearance_count", "best_mcap_rank"],
        ascending=[False, True],
    )


def verdict(count_coverage_pct: float, mcap_coverage_pct: float) -> str:
    if count_coverage_pct >= 95.0 and mcap_coverage_pct >= 97.0:
        return "PROCEED"
    if count_coverage_pct >= 90.0 or mcap_coverage_pct >= 90.0:
        return "PROCEED WITH BIAS FLAG"
    return "STOP"


def write_log(
    *,
    log_path: Path,
    snapshot_path: Path,
    coverage_path: Path,
    missing_path: Path,
    total_unique: int,
    success_count: int,
    fail_count: int,
    count_coverage_pct: float,
    mcap_coverage_pct: float,
    decision: str,
    snapshot: pd.DataFrame,
    missing: pd.DataFrame,
) -> None:
    middle_col = "idx_bztp_mcls_cd_name"
    middle_nonempty = 0
    if middle_col in snapshot.columns:
        middle_nonempty = int(
            snapshot.loc[snapshot["fetch_status"].eq("success"), middle_col]
            .fillna("")
            .astype(str)
            .str.len()
            .gt(0)
            .sum()
        )
    distribution = (
        snapshot.loc[snapshot["fetch_status"].eq("success"), middle_col]
        .fillna("")
        .replace("", "(blank)")
        .value_counts()
        .sort_index()
        if middle_col in snapshot.columns
        else pd.Series(dtype=int)
    )
    top_missing = missing.head(10)

    lines = [
        "# E000 KIS Sector Snapshot Log",
        "",
        f"- run_timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
        f"- snapshot_path: {snapshot_path.relative_to(ROOT)}",
        f"- coverage_path: {coverage_path.relative_to(ROOT)}",
        f"- missing_path: {missing_path.relative_to(ROOT)}",
        f"- total_unique_tickers: {total_unique}",
        f"- kis_api_success_count: {success_count}",
        f"- kis_api_fail_count: {fail_count}",
        f"- count_coverage_pct: {count_coverage_pct:.6f}",
        f"- mcap_weighted_coverage_pct: {mcap_coverage_pct:.6f}",
        f"- verdict: {decision}",
        "",
        "## Sector Field Sanity",
        "",
        f"- Recommended middle-class column: `{middle_col}`",
        f"- Non-empty successful rows: {middle_nonempty} / {success_count}",
        "",
        "## Missing Top 10",
        "",
    ]
    if top_missing.empty:
        lines.append("No missing tickers.")
    else:
        lines.extend(markdown_table(top_missing).splitlines())

    lines.extend(["", "## KIS Middle-Class Distribution", ""])
    if distribution.empty:
        lines.append("No successful sector distribution available.")
    else:
        distribution_frame = distribution.rename("ticker_count").reset_index()
        distribution_frame.columns = [middle_col, "ticker_count"]
        lines.extend(markdown_table(distribution_frame).splitlines())

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    output = [
        "| " + " | ".join(str(col) for col in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _idx, row in frame.iterrows():
        output.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Skip KIS API calls and write questions file.")
    parser.add_argument("--rate-sleep-seconds", type=float, default=0.5)
    parser.add_argument("--abort-after-consecutive-network-failures", type=int, default=5)
    args = parser.parse_args()

    panel_rows = load_all_panel_rows(PANEL_PATHS)
    tickers = sorted(panel_rows["종목코드"].unique())
    print(f"unique_tickers={len(tickers)}")

    if args.dry_run:
        return 0

    env_values = parse_env_file(str(ENV_PATH))
    app_key = env_values.get("KIS_APP_KEY", "")
    app_secret = env_values.get("KIS_APP_SECRET", "")
    if not app_key or not app_secret:
        question_path = REPORT_DIR / "E000_codex_questions.md"
        question_path.write_text(
            "# E000 Codex Questions\n\n"
            "- `research_input_data/.env`에서 `KIS_APP_KEY` 또는 `KIS_APP_SECRET`을 찾지 못했습니다.\n",
            encoding="utf-8",
        )
        return 2

    client = KISSectorClient(app_key, app_secret)
    snapshot_date = datetime.now().strftime("%Y%m%d")
    snapshot_path = PROCESSED_DIR / f"sector_membership_kis_snapshot_{snapshot_date}.csv"
    try:
        snapshot_rows = build_snapshot_rows(
            tickers,
            client,
            rate_sleep_seconds=args.rate_sleep_seconds,
            abort_after_consecutive_failures=args.abort_after_consecutive_network_failures,
        )
    except RuntimeError as exc:
        question_path = REPORT_DIR / "E000_codex_questions.md"
        question_path.write_text(
            "# E000 Codex Questions\n\n"
            f"- KIS API 호출이 HTTP status 없이 연속 실패했습니다: `{exc}`\n"
            "- 현재 Codex 실행 샌드박스의 네트워크가 제한되어 KIS endpoint에 연결하지 못하는 것으로 보입니다.\n"
            "- 로컬 터미널에서 같은 스크립트를 실행하거나, Codex 세션에 KIS endpoint outbound 접근이 가능한 환경을 제공해 주세요.\n"
            "- credential 값은 출력하거나 저장하지 않았습니다.\n",
            encoding="utf-8",
        )
        print(f"question_file={question_path}")
        return 3
    snapshot = write_snapshot(snapshot_rows, snapshot_path)

    coverage = compute_coverage(panel_rows, snapshot)
    coverage_path = REPORT_DIR / "kis_sector_coverage.csv"
    coverage.to_csv(coverage_path, index=False)

    missing = compute_missing_report(panel_rows, snapshot)
    missing_path = REPORT_DIR / "missing_sector_names.csv"
    missing.to_csv(missing_path, index=False)

    success_count = int(snapshot["fetch_status"].eq("success").sum())
    fail_count = int(snapshot["fetch_status"].eq("fail").sum())
    count_coverage_pct = success_count / len(tickers) * 100 if tickers else 0.0
    dedup = panel_rows.drop_duplicates(["panel", "날짜", "종목코드"]).copy()
    success_tickers = set(snapshot.loc[snapshot["fetch_status"].eq("success"), "pdno"].map(normalize_ticker))
    total_mcap = pd.to_numeric(dedup["시가총액추정"], errors="coerce").sum(min_count=1)
    matched_mcap = pd.to_numeric(
        dedup.loc[dedup["종목코드"].isin(success_tickers), "시가총액추정"],
        errors="coerce",
    ).sum(min_count=1)
    mcap_coverage_pct = matched_mcap / total_mcap * 100 if total_mcap else 0.0
    decision = verdict(count_coverage_pct, mcap_coverage_pct)

    write_log(
        log_path=REPORT_DIR / "api_fetch_log.md",
        snapshot_path=snapshot_path,
        coverage_path=coverage_path,
        missing_path=missing_path,
        total_unique=len(tickers),
        success_count=success_count,
        fail_count=fail_count,
        count_coverage_pct=count_coverage_pct,
        mcap_coverage_pct=mcap_coverage_pct,
        decision=decision,
        snapshot=snapshot,
        missing=missing,
    )
    print(f"snapshot={snapshot_path}")
    print(f"coverage={coverage_path}")
    print(f"missing={missing_path}")
    print(f"verdict={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
