#!/usr/bin/env python3
"""BX01: Download KRX board MDCINFO005 attachments via the two-step OTP flow.

Step 1: POST to /comm/fileDn/GenerateHp/requestUrlFileUrl.cmd with
   name=fileDown & filetype=att & url=COM%2Fboard_attach_down
   & bbsId=MKD01040000 & bbsSeq=<seq> & attachFileSeq=<aseq>
   -> JSON {fileUrl, code}
Step 2: POST to fileUrl with code -> binary file body

Reads kospi200_notice_index.json + writes raw files + manifest.csv with sha256.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
RAW = ROOT / "raw"
INDEX = RAW / "kospi200_notice_index.json"
MANIFEST = ROOT / "manifest.csv"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 BX01-research"
REFERER = "https://data.krx.co.kr/contents/MDC/COMS/board/MDCCOMS010_S1.cmd?boardId=MDCINFO005"
OTP_URL = "https://data.krx.co.kr/comm/fileDn/GenerateHp/requestUrlFileUrl.cmd"


def http_post(url: str, data: dict, *, accept_json: bool = False, referer: str = REFERER, cookies: dict | None = None) -> tuple[bytes, dict]:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Referer", referer)
    req.add_header("X-Requested-With", "XMLHttpRequest")
    if accept_json:
        req.add_header("Accept", "application/json, text/javascript, */*; q=0.01")
    req.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
    if cookies:
        ck = "; ".join(f"{k}={v}" for k, v in cookies.items())
        if ck:
            req.add_header("Cookie", ck)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), dict(r.headers.items())


def parse_attach(s: str) -> list[dict]:
    """ATTACH_FILE_INFO format:
       COUNT:ATTACH_FILE_SEQ|ORGN_FILE_NM|SAVE_FILE_NM|FILE_PATH[,ATTACH_FILE_SEQ|...]
    """
    out = []
    if not s:
        return out
    # leading "1:" or "2:" is the COUNT marker
    m = re.match(r"^(\d+):(.*)$", s, re.DOTALL)
    payload = m.group(2) if m else s
    for token in payload.split(","):
        token = token.strip()
        if not token:
            continue
        parts = token.split("|")
        if len(parts) < 4:
            continue
        attach_seq, orgn_nm, save_nm, file_path = parts[:4]
        out.append({
            "attach_file_seq": attach_seq,
            "orgn_file_nm": orgn_nm,
            "save_file_nm": save_nm,
            "file_path": file_path,
        })
    return out


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    notices = json.load(INDEX.open(encoding="utf-8"))
    print(f"loaded {len(notices)} notices")

    # Open manifest
    is_new = not MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as mf:
        w = csv.writer(mf, lineterminator="\n")
        if is_new:
            w.writerow([
                "bbs_seq", "cm_bbs_id", "attach_file_seq", "orgn_file_nm",
                "save_file_nm", "file_path_remote", "url_step1", "url_step2",
                "retrieved_at_utc", "local_path", "bytes", "sha256",
                "file_type_ext", "source_license_note", "parse_status",
            ])

        downloaded = 0
        skipped = 0
        failed = []

        for n in notices:
            atts = parse_attach(n["attach_file_info"])
            for att in atts:
                bbs_seq = n["bbs_seq"]
                cm_bbs_id = n["cm_bbs_id"]
                aseq = att["attach_file_seq"]
                local_name = f"bbsSeq{bbs_seq}_seq{aseq}__{att['save_file_nm']}"
                local_path = RAW / local_name
                if local_path.exists():
                    skipped += 1
                    continue

                # Step 1: get OTP code + fileUrl
                # The param string format expected per JS:
                # name=fileDown&filetype=att&url=COM%2Fboard_attach_down&bbsId=...&bbsSeq=...&attachFileSeq=...
                step1_data = {
                    "name": "fileDown",
                    "filetype": "att",
                    "url": "COM/Fboard_attach_down",
                    "bbsId": cm_bbs_id,
                    "bbsSeq": bbs_seq,
                    "attachFileSeq": aseq,
                }
                try:
                    body, _hdrs = http_post(OTP_URL, step1_data, accept_json=True)
                    resp = json.loads(body.decode("utf-8"))
                except Exception as e:
                    failed.append((bbs_seq, aseq, f"OTP step1 fail: {e}"))
                    continue

                file_url = resp.get("fileUrl") or resp.get("FILE_URL")
                code = resp.get("code") or resp.get("CODE")
                if not file_url or not code:
                    # Some variants use a different shape
                    failed.append((bbs_seq, aseq, f"OTP step1 missing fileUrl/code; resp keys={list(resp.keys())[:6]}"))
                    continue

                # Step 2: download the file
                try:
                    fbody, fhdrs = http_post(file_url, {"code": code})
                except Exception as e:
                    failed.append((bbs_seq, aseq, f"step2 fail: {e}"))
                    continue

                # Sanity check: small + html = error page
                if len(fbody) < 1024 and b"<html" in fbody[:512].lower():
                    failed.append((bbs_seq, aseq, f"step2 returned HTML error page ({len(fbody)}B)"))
                    continue

                local_path.write_bytes(fbody)
                downloaded += 1
                sha = sha256_file(local_path)
                ext = att["orgn_file_nm"].rsplit(".", 1)[-1].lower() if "." in att["orgn_file_nm"] else ""
                retrieved_at = datetime.now(timezone.utc).isoformat()
                w.writerow([
                    bbs_seq, cm_bbs_id, aseq, att["orgn_file_nm"],
                    att["save_file_nm"], att["file_path"], OTP_URL, file_url,
                    retrieved_at, str(local_path), len(fbody), sha,
                    ext,
                    "KRX public press notice — non-commercial research/reconciliation use; full provenance kept",
                    "downloaded",
                ])
                mf.flush()
                # Be polite — small pause between downloads
                time.sleep(0.3)

        print(f"\ndownloaded={downloaded}  skipped(exist)={skipped}  failed={len(failed)}")
        if failed:
            print("First 10 failures:")
            for bs, aseq, msg in failed[:10]:
                print(f"  bbsSeq={bs} aseq={aseq} :: {msg}")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
