# Host Data Collection Guide

This guide is for the one-time host-side backlog data download. Do not run this
inside the Codex sandbox because network access is intentionally unavailable
there.

## Prerequisites

From the repo root:

```bash
.venv/bin/python -m pip show yfinance pykrx
```

If either package is missing on the host:

```bash
.venv/bin/python -m pip install yfinance pykrx
```

Do not add these dependencies to `requirements.txt` unless a future execution
ticket decides that host collection should become part of the reproducible test
environment.

## Run

```bash
.venv/bin/python scripts/host_data_collection.py
```

The script is verbose by design. It downloads all backlog datasets in one run:

- I003.6 long-history ETFs: QQQ, SPY, IEF, TLT, GLD.
- J-family EM ETFs: VWO, EWY, EWJ, EWZ, MCHI.
- K-family US sector ETFs: XLE, XLF, XLK, XLV, XLI, XLY, XLP, XLU, XLB, XLRE, XLC.
- L-family KOSDAQ150 pykrx panel.
- M-family crypto: BTC-USD, ETH-USD.
- FX hedge ETFs: FXY, FXE.

## Verify Downloads

Check the priority I003.6 files first:

```bash
ls research_input_data/inputs/global_etf/yf_QQQ_long.csv \
   research_input_data/inputs/global_etf/yf_SPY_long.csv \
   research_input_data/inputs/global_etf/yf_IEF_long.csv \
   research_input_data/inputs/global_etf/yf_TLT_long.csv \
   research_input_data/inputs/global_etf/yf_GLD_long.csv
```

Then verify the KOSDAQ panel:

```bash
ls research_input_data/inputs/equity_panels/pykrx_kosdaq150_panel.csv
```

Record newly created data files in:

```text
research_input_data/docs/DATA_CATALOG.md
```

## Run I003.6 Audit

After the long-history CSVs exist:

```bash
.venv/bin/python -m src.audit.i003_6_long_history
```

Expected output directory:

```text
reports/experiments/I003_6_long_history/
```

## Troubleshooting

- `missing dependency: install yfinance`: install yfinance in the host venv.
- `missing dependency: install pykrx`: install pykrx in the host venv.
- `yfinance returned no rows`: rerun after checking host network and Yahoo access.
- `pykrx KOSDAQ150 download failed`: rerun after checking pykrx availability and KRX access.
- Partial CSV files may exist after failure. Re-running the script overwrites the
  target CSV files.

Do not interpret audit results as strategy approval. I003.6 is a US-core stress
approximation, not a full pre-2010 reconstruction of `P08_IEF30`.
