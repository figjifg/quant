# Q000 Data Audit Guide

Status: host-run guide. Network is required.

Codex sandbox must not call SEC EDGAR or any other external endpoint for this
ticket. Run the audit on the user host.

## Purpose

Q000 decides whether the Q-family can proceed. The gate is PIT financial data
plus survivorship-free universe feasibility. If either fails, stop individual
stock Q-family work and use ETF proxy diagnostics instead.

## SEC Endpoint

Companyfacts endpoint:

```text
https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json
```

SEC requires a descriptive `User-Agent` header. Use a name and email.

Rate limit: stay at or below 10 requests per second.

## Sample Companies

Initial 10-name sample:

- `AAPL`
- `MSFT`
- `GOOGL`
- `AMZN`
- `META`
- `NVDA`
- `BRK.B`
- `JPM`
- `V`
- `JNJ`

CIKs can be checked through SEC company search:

```text
https://www.sec.gov/cgi-bin/browse-edgar
```

## Run Command

From repo root on the user host:

```bash
python scripts/q000_sec_edgar_audit.py --user-agent "Your Name your.email@example.com"
```

Expected output:

```text
research_input_data/inputs/us_fundamentals/sec_edgar_sample.json
```

After creating the file, record it in:

```text
research_input_data/docs/DATA_CATALOG.md
```

## Audit Checklist

1. Download `companyfacts` JSON for the 10 sample names.
2. Confirm each relevant fact has a `filed` date.
3. Confirm 10-K and 10-Q forms are represented.
4. Check XBRL tag availability for ROIC, FCF margin, leverage, FCF yield,
   earnings yield, buyback, dividend, and share-count inputs.
5. Record unstable or missing tags by company and fiscal year.
6. Separately evaluate whether delisted companies and historical Russell 1000
   or S&P 1500 membership can be sourced without survivorship bias.

## Hard Gates

- Current S&P 500 constituents cannot be used as a historical universe.
- Financial statement data cannot be used before SEC filing date.
- Many factor combinations cannot be searched to find the highest Sharpe.

## Alternatives If SEC API Fails

These sources are fallbacks only, and each has PIT or licensing risk:

- `yfinance`: simple financials, timestamp accuracy weak.
- Financial Modeling Prep API: paid/free tiers, must verify PIT terms.
- Alpha Vantage: limited coverage.
- Stock Analysis: web scraping risk and timestamp uncertainty.

If no source can satisfy PIT and survivorship requirements, Q-family stops and
ETF proxy diagnostics may use `QUAL`, `VLUE`, `MTUM`, `USMV`, `SCHD`, and
`COWZ`.

