"""W000 item 6 — KRX securities-lending (borrow) data acquisition (autonomous track).

Authorized 2026-05-26 (W000 download/API pre-approval). Source = DATA.GO.KR 금융위원회
주식대차정보 `GetStocLendBorrInfoService_V2 / getStItemLendAndBorrStatu_V2` (per-ticker
daily lending/borrow status). One call per trading date returns all listed stocks
(~2,400 rows, single page). The API is ~3s/call, so the full 2018-2026 daily pull is
~100 min — hence this script CHECKPOINTS per date (append-only CSV + manifest rewrite)
and is RESUMABLE (skips dates already in the manifest). Killing it loses nothing.

COVERAGE SCOPE (honest / partial): BORROW-BALANCE side only — lnbCclStckCnt (대차체결),
lnbRmanStckCnt (대차잔여=outstanding borrow balance), lnbRdptStckCnt (상환). It does NOT
provide borrow FEE / short-rebate / short-sale-restriction list / forced buy-in — those
remain a residual W000 item-6 gap requiring a different source.

HARD LOCKS (W000 track): raw under data/acquired/** (gitignored) + committed lineage; no
data/raw or research_input_data modification; DATA INFRASTRUCTURE only (W000 Hard Rule:
does NOT reopen the closed Korean long-short research); no strategy/execution use; no P08
weight change. DATA_GO_KR_API_KEY is read in-process and never printed/committed.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import pandas as pd
import requests

REPO = Path("/home/jin/code/quant")
PRICES = REPO / "data/acquired/w000_korean_total_return/kr_total_return_prices_2018_2026.csv"
OUT = REPO / "data/acquired/w000_kr_borrow"
CSV_PATH = OUT / "kr_borrow_balance_2018_2026.csv"
MAN_PATH = OUT / "acquisition_manifest.csv"
BASE = "http://apis.data.go.kr/1160100/GetStocLendBorrInfoService_V2/getStItemLendAndBorrStatu_V2"
FIELDS = ["date", "ticker", "isin", "name",
          "borrow_contracted_shares", "borrow_balance_shares", "borrow_repaid_shares"]


def _key() -> str:
    for line in (REPO / "research_input_data/.env").read_text().splitlines():
        if line.startswith("DATA_GO_KR_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError("DATA_GO_KR_API_KEY not found")


def trading_dates() -> list[str]:
    d = pd.read_csv(PRICES, usecols=["date"])
    return sorted(d["date"].astype(str).str.replace("-", "", regex=False).unique())


def done_dates() -> set[str]:
    if not MAN_PATH.exists():
        return set()
    m = pd.read_csv(MAN_PATH, dtype={"basDt": str})
    return set(m.loc[m["status"].isin(["ok", "empty"]), "basDt"].astype(str))


def fetch_date(key: str, basdt: str, session: requests.Session):
    try:
        r = session.get(BASE, params={"serviceKey": key, "resultType": "json",
                                       "numOfRows": 10000, "pageNo": 1, "basDt": basdt}, timeout=30)
        if r.status_code != 200:
            return None, f"http_{r.status_code}"
        body = r.json()["response"]["body"]
        items = body.get("items")
        if not items:
            return [], "empty"
        it = items.get("item", [])
        return ([it] if isinstance(it, dict) else it), "ok"
    except Exception as e:
        return None, f"err_{type(e).__name__}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.18)
    ap.add_argument("--fresh", action="store_true", help="ignore + overwrite existing checkpoints")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    key = _key()
    dates = trading_dates()
    if args.limit:
        dates = dates[-args.limit:]

    if args.fresh:
        CSV_PATH.unlink(missing_ok=True)
        MAN_PATH.unlink(missing_ok=True)
    done = done_dates()
    todo = [d for d in dates if d not in done]
    print(f"[w000-borrow] {len(dates)} dates total; {len(done)} already done; {len(todo)} to fetch", flush=True)

    # append-only CSV (write header once)
    new_file = not CSV_PATH.exists()
    csv_f = open(CSV_PATH, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_f, fieldnames=FIELDS, lineterminator="\n")
    if new_file:
        writer.writeheader()

    manifest: dict[str, dict] = {}
    if MAN_PATH.exists():
        for r in pd.read_csv(MAN_PATH, dtype={"basDt": str}).to_dict("records"):
            manifest[str(r["basDt"])] = r

    sess = requests.Session()
    ok = 0
    for i, bd in enumerate(todo, 1):
        items, status = fetch_date(key, bd, sess)
        kr = 0
        if items:
            for x in items:
                isin = str(x.get("isinCd", ""))
                if not isin.startswith("KR7"):
                    continue
                writer.writerow({
                    "date": f"{bd[:4]}-{bd[4:6]}-{bd[6:]}", "ticker": isin[3:9], "isin": isin,
                    "name": x.get("isinCdNm", ""),
                    "borrow_contracted_shares": x.get("lnbCclStckCnt"),
                    "borrow_balance_shares": x.get("lnbRmanStckCnt"),
                    "borrow_repaid_shares": x.get("lnbRdptStckCnt"),
                })
                kr += 1
            if status == "ok":
                ok += 1
        csv_f.flush()  # durable per date
        manifest[bd] = {"basDt": bd, "status": status, "kr_stock_rows": kr}
        if i % 25 == 0 or i == len(todo):
            pd.DataFrame(sorted(manifest.values(), key=lambda r: r["basDt"])).to_csv(
                MAN_PATH, index=False, lineterminator="\n")
            print(f"[w000-borrow] {i}/{len(todo)} (ok={ok})", flush=True)
        time.sleep(args.sleep)

    csv_f.close()
    pd.DataFrame(sorted(manifest.values(), key=lambda r: r["basDt"])).to_csv(MAN_PATH, index=False, lineterminator="\n")
    print(f"[w000-borrow] DONE: {ok}/{len(todo)} new dates ok; total manifest dates={len(manifest)}", flush=True)


if __name__ == "__main__":
    main()
