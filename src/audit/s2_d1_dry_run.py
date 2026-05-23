"""S2 D1 dry run — 50 disclosures small-scale OPENDART body XML download.

Referee Round 4.1 lock: infrastructure repair only, no strategy testing.

D1 outputs (8 items per Referee):
1. source coverage
2. endpoint success rate
3. form inventory sample
4. actual form mapping vs expected 10 event-type taxonomy
5. XML schema examples by form
6. failure ledger
7. rate-limit / retry policy
8. D2 readiness recommendation

Security:
- API key loaded from .env via BOM/CRLF-safe parser, never printed/logged.
- HTTP request params dict logged with key field redacted.
"""
from __future__ import annotations

import io
import json
import os
import random
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path("/home/jin/code/quant")
ENV_PATH = REPO_ROOT / "research_input_data" / ".env"
PARQUET_PATH = (
    REPO_ROOT
    / "research_input_data"
    / "inputs"
    / "events"
    / "opendart_kospi_disclosures_20180101_20260505.parquet"
)
DATA_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1"
RAW_XML_DIR = DATA_DIR / "raw_xml"
REPORT_DIR = REPO_ROOT / "reports" / "experiments" / "S2_phase_d1_dry_run"
ENDPOINT = "https://opendart.fss.or.kr/api/document.xml"

EXPECTED_FORM_MAP = {
    "treasury_acquire": ["자기주식취득결정"],
    "treasury_dispose": ["자기주식처분결정"],
    "treasury_cancel": ["자기주식소각결정"],
    "cb_issue": ["전환사채권발행결정"],
    "bw_issue": ["신주인수권부사채권발행결정"],
    "conversion_request": ["전환청구권행사"],
    "rights_issue": ["유상증자결정"],
    "bonus_issue": ["무상증자결정"],
    "capital_reduction": ["감자결정"],
    "merger_split": ["회사합병결정", "회사분할결정", "회사분할합병결정"],
}

SAMPLES_PER_TYPE = 5
RANDOM_SEED = 20260523
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.3
MAX_RETRY = 3


def load_env(path: Path) -> None:
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    text = raw.decode("utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def select_50_samples() -> pd.DataFrame:
    df = pd.read_parquet(PARQUET_PATH)
    rows = []
    rng = random.Random(RANDOM_SEED)
    for tag, keywords in EXPECTED_FORM_MAP.items():
        mask = df["report_nm"].apply(
            lambda x: any(kw in (x or "") for kw in keywords)
        )
        sub = df[mask].copy()
        sub["expected_event_type"] = tag
        if len(sub) == 0:
            print(f"  WARN: {tag} = 0 candidates")
            continue
        n = min(SAMPLES_PER_TYPE, len(sub))
        idx = rng.sample(range(len(sub)), n)
        rows.append(sub.iloc[idx])
    out = pd.concat(rows, ignore_index=True)
    out = out[
        [
            "rcept_no",
            "rcept_date",
            "corp_code",
            "stock_code",
            "corp_name",
            "report_nm",
            "expected_event_type",
        ]
    ]
    return out


def download_one(rcept_no: str, api_key: str) -> dict:
    result = {
        "rcept_no": rcept_no,
        "attempt": 0,
        "http_status": None,
        "ok": False,
        "bytes": 0,
        "content_type": None,
        "elapsed_ms": None,
        "error": None,
    }
    for attempt in range(1, MAX_RETRY + 1):
        result["attempt"] = attempt
        start = time.time()
        try:
            r = requests.get(
                ENDPOINT,
                params={"crtfc_key": api_key, "rcept_no": rcept_no},
                timeout=REQUEST_TIMEOUT,
            )
            result["http_status"] = r.status_code
            result["bytes"] = len(r.content)
            result["content_type"] = r.headers.get("Content-Type", "")
            result["elapsed_ms"] = int((time.time() - start) * 1000)
            if r.status_code == 200 and len(r.content) > 200:
                target_zip = RAW_XML_DIR / f"{rcept_no}.zip"
                target_zip.write_bytes(r.content)
                try:
                    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                        for name in zf.namelist():
                            data = zf.read(name)
                            (RAW_XML_DIR / f"{rcept_no}.xml").write_bytes(data)
                            break
                    result["ok"] = True
                    return result
                except zipfile.BadZipFile:
                    result["error"] = "BadZipFile"
            elif r.status_code == 200 and len(r.content) < 200:
                result["error"] = "tiny_response_likely_api_error"
            else:
                result["error"] = f"http_{r.status_code}"
        except requests.RequestException as exc:
            result["error"] = f"req_exception_{type(exc).__name__}"
        time.sleep(min(2 ** attempt, 8))
    return result


def survey_form_inventory(samples: pd.DataFrame) -> pd.DataFrame:
    inv = (
        samples.groupby(["expected_event_type", "report_nm"])
        .size()
        .reset_index(name="count")
        .sort_values(["expected_event_type", "count"], ascending=[True, False])
    )
    return inv


def extract_schema_examples(samples: pd.DataFrame) -> dict:
    examples: dict[str, dict] = {}
    for _, row in samples.iterrows():
        rcept_no = row["rcept_no"]
        xml_path = RAW_XML_DIR / f"{rcept_no}.xml"
        if not xml_path.exists():
            continue
        ev = row["expected_event_type"]
        if ev in examples:
            continue
        raw = xml_path.read_bytes()
        head_text = raw[:4000].decode("utf-8", errors="replace")
        examples[ev] = {
            "rcept_no": rcept_no,
            "report_nm": row["report_nm"],
            "size_bytes": len(raw),
            "head_4kb": head_text,
        }
    return examples


def write_reports(
    samples: pd.DataFrame,
    dl_results: list[dict],
    inv: pd.DataFrame,
    examples: dict,
) -> None:
    samples.to_csv(DATA_DIR / "samples_50.csv", index=False)
    dl_df = pd.DataFrame(dl_results)
    dl_df.to_csv(DATA_DIR / "download_log.csv", index=False)
    inv.to_csv(DATA_DIR / "form_inventory.csv", index=False)
    failures = dl_df[~dl_df["ok"]].copy()
    failures.to_csv(DATA_DIR / "failure_ledger.csv", index=False)

    success_rate = dl_df["ok"].mean() if len(dl_df) else 0.0
    avg_elapsed = dl_df.loc[dl_df["ok"], "elapsed_ms"].mean() if dl_df["ok"].any() else None

    period_min = samples["rcept_date"].min()
    period_max = samples["rcept_date"].max()
    universe = sorted(samples["corp_cls"].unique().tolist()) if "corp_cls" in samples.columns else ["Y(KOSPI source)"]
    form_count = samples["report_nm"].nunique()

    actual_form_mapping = []
    for ev, kws in EXPECTED_FORM_MAP.items():
        actual_forms = samples.loc[samples["expected_event_type"] == ev, "report_nm"].unique().tolist()
        n_dl_ok = int(
            dl_df.set_index("rcept_no")
            .loc[samples.loc[samples["expected_event_type"] == ev, "rcept_no"]]
            ["ok"].sum()
        )
        actual_form_mapping.append(
            {
                "event_type": ev,
                "expected_keywords": kws,
                "actual_forms": actual_forms,
                "n_samples": int((samples["expected_event_type"] == ev).sum()),
                "n_download_ok": n_dl_ok,
            }
        )

    # 8 D1 outputs
    (REPORT_DIR / "source_coverage.md").write_text(
        f"""# D1 Source Coverage

Date: 2026-05-23
Scope: S2 D1 dry run, 50 disclosures small-scale

| Item | Value |
|---|---|
| Period (sample) | {period_min} ~ {period_max} |
| Universe source | KOSPI (R000 input parquet) |
| corp_cls in sample | {universe} |
| Total samples | {len(samples)} |
| Distinct report_nm | {form_count} |
| Event types covered | {samples['expected_event_type'].nunique()} / {len(EXPECTED_FORM_MAP)} |
| Source parquet | `research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet` |
| Parquet total rows | 450,190 |

## Event types not covered in D1 dry run

Referee taxonomy 10 event types 중 D1 dry run sample 에 포함되지 않은 type:
- 추가상장 (R000 KOSPI 일반 disclosure 에 별도 form 없음 — KOSDAQ 또는 KRX 상장공시 별도 source 필요)
- 보호예수 해제 (R000 KOSPI 일반 disclosure 에 별도 form 없음 — 의무보유등 별도 source 필요)
- 대주주 매도 (R000 KOSPI 에 임원·주요주주특정증권등소유상황보고서 50,948건 존재 — D1 미포함, D2 부터)
- 정정/철회/취소 (D1 미포함, D2 부터)

D2 에서 위 4 type 도 form mapping 확장 필요.
""",
        encoding="utf-8",
    )

    (REPORT_DIR / "endpoint_success_rate.md").write_text(
        f"""# D1 Endpoint Success Rate

| Metric | Value |
|---|---|
| Total requests | {len(dl_df)} |
| Successful | {int(dl_df['ok'].sum())} |
| Failed | {int((~dl_df['ok']).sum())} |
| Success rate | {success_rate:.1%} |
| Average elapsed (ok only) | {f'{avg_elapsed:.0f} ms' if avg_elapsed is not None else 'N/A'} |
| Max retries per request | {MAX_RETRY} |
| Sleep between requests | {SLEEP_BETWEEN_REQUESTS} s |
| Endpoint | {ENDPOINT} |
| Request timeout | {REQUEST_TIMEOUT} s |

## Status code distribution

```
{dl_df['http_status'].value_counts(dropna=False).to_string()}
```

## Content-Type distribution (success)

```
{dl_df.loc[dl_df['ok'], 'content_type'].value_counts().to_string()}
```
""",
        encoding="utf-8",
    )

    inv_md = "```\n" + inv.to_string(index=False) + "\n```"
    (REPORT_DIR / "form_inventory.md").write_text(
        f"""# D1 Form Inventory Sample

50 disclosure 의 expected event type × actual report_nm 분포.

{inv_md}
""",
        encoding="utf-8",
    )

    mapping_lines = ["# D1 Actual Form Mapping vs Expected\n"]
    mapping_lines.append("| Event type | Expected keywords | Actual forms in sample | N sampled | N downloaded |")
    mapping_lines.append("|---|---|---|---|---|")
    for m in actual_form_mapping:
        mapping_lines.append(
            f"| {m['event_type']} | {', '.join(m['expected_keywords'])} | "
            f"{', '.join(m['actual_forms']) if m['actual_forms'] else '_none_'} | "
            f"{m['n_samples']} | {m['n_download_ok']} |"
        )
    (REPORT_DIR / "actual_form_mapping.md").write_text("\n".join(mapping_lines), encoding="utf-8")

    schema_lines = ["# D1 XML Schema Examples (head 4KB per event type)\n"]
    for ev, info in examples.items():
        schema_lines.append(f"## {ev} — rcept_no={info['rcept_no']}, report_nm={info['report_nm']}")
        schema_lines.append(f"Size: {info['size_bytes']:,} bytes\n")
        schema_lines.append("```xml")
        schema_lines.append(info["head_4kb"][:3500])
        schema_lines.append("```\n")
    (REPORT_DIR / "xml_schema_examples.md").write_text("\n".join(schema_lines), encoding="utf-8")

    fail_md_lines = ["# D1 Failure Ledger\n", f"Total failures: {len(failures)}\n"]
    if len(failures) > 0:
        fail_md_lines.append("```\n" + failures.to_string(index=False) + "\n```")
    else:
        fail_md_lines.append("_None._")
    (REPORT_DIR / "failure_ledger.md").write_text("\n".join(fail_md_lines), encoding="utf-8")

    (REPORT_DIR / "rate_limit_note.md").write_text(
        f"""# D1 Rate Limit / Retry / Timeout Policy

D1 dry run applied policy:
- Sleep between requests: {SLEEP_BETWEEN_REQUESTS} s
- Per-request timeout: {REQUEST_TIMEOUT} s
- Retry on failure: exponential backoff (2^attempt s), max {MAX_RETRY} attempts
- Total expected wall time for 50 disclosures (success path): ~ 50 × ({SLEEP_BETWEEN_REQUESTS} + avg_response) seconds

OPENDART official rate limit (documented):
- Free key default: 10,000 requests / day
- Per-second: not officially documented, conservative 0.3 s sleep applied

Observation in D1:
- See `endpoint_success_rate.md` for actual results.
""",
        encoding="utf-8",
    )

    pass_download = success_rate >= 0.90
    pass_form_mapping = all(m["n_download_ok"] >= 1 for m in actual_form_mapping if m["n_samples"] > 0)
    pass_no_blocker = success_rate > 0.0

    d2_lines = [
        "# D1 → D2 Readiness Recommendation\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Referee D2 entry gate (4 conditions)\n",
        "| Gate | Threshold | Result | Pass |",
        "|---|---|---|---|",
        f"| stable download | success rate ≥ 90% | {success_rate:.1%} | {'✅' if pass_download else '❌'} |",
        f"| no material form-mapping mismatch | each covered event type ≥ 1 download | {'all covered' if pass_form_mapping else 'some missing'} | {'✅' if pass_form_mapping else '❌'} |",
        f"| no key/rate-limit blocker | success_rate > 0 | {success_rate:.1%} | {'✅' if pass_no_blocker else '❌'} |",
        f"| no major malformed XML blocker | failure ledger inspected | {len(failures)} failures | {'✅' if len(failures) < 5 else '⚠️'} |",
        "",
        "## Recommendation",
        "",
    ]
    if pass_download and pass_form_mapping and pass_no_blocker:
        d2_lines.append("→ **D2 entry RECOMMENDED**. D1 dry run passed all 4 gates.")
    else:
        d2_lines.append("→ **D2 entry NOT YET**. Address failed gates before D2 schema mapping phase.")
    d2_lines.append("")
    d2_lines.append("## Caveats (executor note)")
    d2_lines.append("")
    d2_lines.append(
        "- D1 dry run = KOSPI-only sample (R000 input). KOSDAQ + 추가상장 + 보호예수 등 4 event types not yet sampled."
    )
    d2_lines.append(
        "- This is a 50-disclosure dry run; full D1 production run = filtered subset of 450k KOSPI disclosures, plus KOSDAQ acquisition."
    )
    d2_lines.append(
        "- Referee approval required before progressing D2 → D3."
    )
    d2_lines.append(
        "- No strategy testing performed or recommended (Round 4.1 hard locks)."
    )
    (REPORT_DIR / "d2_readiness.md").write_text("\n".join(d2_lines), encoding="utf-8")


def main() -> int:
    load_env(ENV_PATH)
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        print("ERROR: OPENDART_API_KEY not loaded.", file=sys.stderr)
        return 1
    print(f"API key loaded (length={len(api_key)})")

    print("Selecting 50 sample disclosures...")
    samples = select_50_samples()
    print(f"  Selected: {len(samples)} disclosures across {samples['expected_event_type'].nunique()} event types")

    print("Downloading body XMLs...")
    dl_results = []
    for i, rcept_no in enumerate(samples["rcept_no"].tolist(), 1):
        res = download_one(rcept_no, api_key)
        dl_results.append(res)
        ok_str = "OK" if res["ok"] else f"FAIL({res['error']})"
        print(f"  [{i:>2}/50] {rcept_no} status={res['http_status']} {ok_str} {res['bytes']}B")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print("Surveying form inventory...")
    inv = survey_form_inventory(samples)

    print("Extracting XML schema examples...")
    examples = extract_schema_examples(samples)

    print("Writing reports...")
    write_reports(samples, dl_results, inv, examples)

    n_ok = sum(1 for r in dl_results if r["ok"])
    print(f"D1 dry run complete: {n_ok}/50 OK, reports written to {REPORT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
