"""P0-1 KR-FIELD-METADATA-CONTRACT-A0-001 build script.

Produces 6 artifacts in reports/experiments/measurement_A0/KR_FIELD_METADATA_CONTRACT_A0/.

Measurement-layer A0 only. No strategy testing. No return / NAV / alpha / MDD.

Required outputs:
  1. field_metadata_contract.md
  2. dataset_inventory.csv
  3. column_contract_table.csv
  4. field_allowlist_denylist.csv
  5. undocumented_field_defect_ledger.csv
  6. downstream_field_usage_audit.md

Scope = KR equity strategy-relevant datasets only. Non-KR (US ETF / macro / futures /
US fundamentals) listed in inventory as out-of-scope marker, not column-contracted.

Rules:
  - Each column receives (source, unit, raw_or_adjusted, timestamp_semantics,
    PIT_status, identifier_key, upstream_dependency).
  - Missing core metadata → quarantine + defect entry.
  - "PIT_status" = available_PIT | available_with_lookahead_risk | uncertain | n/a.
  - "raw_or_adjusted" = raw | adjusted | derived | n/a.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
OUT = REPO / "reports/experiments/measurement_A0/KR_FIELD_METADATA_CONTRACT_A0"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Dataset inventory (KR equity strategy-relevant + processed)
# ---------------------------------------------------------------------------

@dataclass
class Dataset:
    dataset_id: str
    path: str
    role: str            # equity_panel | market_flow | event | universe_lifecycle | sector | derived_panel | reconciliation_sample
    scope: str           # KR_in_scope | KR_in_scope_processed | out_of_scope
    rowcount: int = 0
    columns: list = field(default_factory=list)
    notes: str = ""

@dataclass
class Column:
    dataset_id: str
    column_name: str
    source: str                  # vendor / origin
    unit: str
    raw_or_adjusted: str
    timestamp_semantics: str     # T_trade_day | T+1_publish | event_time | snapshot | derived | n/a
    pit_status: str
    identifier_key: str          # n/a if not key
    upstream_dependency: str     # n/a or column name(s)
    notes: str = ""


KR_DATASETS = [
    # ---- equity panels (4) ----
    Dataset(
        dataset_id="equity_panel_kiwoom_2010_2016",
        path="research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv",
        role="equity_panel",
        scope="KR_in_scope",
        notes="Kiwoom vendor flow estimation + price; pre-NXT (integrated-market flags all False); 25 cols",
    ),
    Dataset(
        dataset_id="equity_panel_dynamic_top100_2017_2024",
        path="research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv",
        role="equity_panel",
        scope="KR_in_scope",
        notes="20 cols; pre-NXT; KRX종가 column not native (synthesised from 종가)",
    ),
    Dataset(
        dataset_id="equity_panel_dynamic_top100_2018_2024",
        path="research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
        role="equity_panel",
        scope="KR_in_scope",
        notes="20 cols; pre-NXT; overlap with 2017_2024",
    ),
    Dataset(
        dataset_id="equity_panel_krx_2025_2026",
        path="research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
        role="equity_panel",
        scope="KR_in_scope",
        notes="26 cols; post-NXT integrated-market flags present; native KRX종가",
    ),
    # ---- market flow (3) ----
    Dataset(
        dataset_id="market_flow_kiwoom_2010_2017",
        path="research_input_data/inputs/market_flow/kiwoom_market_flow_2010_2017_krx_trading_days.csv",
        role="market_flow",
        scope="KR_in_scope",
    ),
    Dataset(
        dataset_id="market_flow_kiwoom_2018_2026_integrated",
        path="research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv",
        role="market_flow",
        scope="KR_in_scope",
    ),
    Dataset(
        dataset_id="market_flow_kiwoom_2025_2026_krx",
        path="research_input_data/inputs/market_flow/kiwoom_market_flow_2025_2026_krx.csv",
        role="market_flow",
        scope="KR_in_scope",
    ),
    # ---- events (1 parquet) ----
    Dataset(
        dataset_id="opendart_kospi_disclosures_20180101_20260505",
        path="research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet",
        role="event",
        scope="KR_in_scope",
        notes="OPENDART list.json metadata only (no body parse); 26 cols; flags derived from report_nm patterns (regex-based, not authoritative)",
    ),
    # ---- W001 v2 derived (5) ----
    Dataset(
        dataset_id="w001_v2_panel_with_adjusted_ohlc_2018_2026",
        path="data/processed/w001_v2/panel_with_adjusted_ohlc_2018_2026.csv",
        role="derived_panel",
        scope="KR_in_scope_processed",
        notes="Panel + pykrx adjusted OHLC join; adj_* columns added",
    ),
    Dataset(
        dataset_id="w001_v2_panel_with_tradable_state",
        path="data/processed/w001_v2/panel_with_tradable_state.csv",
        role="derived_panel",
        scope="KR_in_scope_processed",
        notes="Above + tradable_state column",
    ),
    Dataset(
        dataset_id="w001_v2_permanent_id_master",
        path="data/processed/w001_v2/permanent_id_master.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="w001_v2_listing_status_events",
        path="data/processed/w001_v2/listing_status_events.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="w001_v2_listing_status_terminal",
        path="data/processed/w001_v2/listing_status_terminal.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
    ),
    # ---- S1 adjusted OHLC ----
    Dataset(
        dataset_id="s1_adjusted_ohlc_all_tickers_2018_2026",
        path="data/acquired/round4/s1_adjusted_ohlc/adjusted_ohlc_all_tickers_2018_2026.csv",
        role="derived_panel",
        scope="KR_in_scope_processed",
        notes="pykrx get_market_ohlcv(adjusted=True) per-ticker concatenated",
    ),
    # ---- S3 KRX status ----
    Dataset(
        dataset_id="s3_krx_status_events_2018_2026",
        path="data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
        notes="OPENDART pblntfty=I filtered to status-relevant report names",
    ),
    Dataset(
        dataset_id="s3_dart_pblntfty_I_all_2018_2026",
        path="data/acquired/round4/s3_krx_status/dart_pblntfty_I_all_2018_2026.csv",
        role="event",
        scope="KR_in_scope_processed",
        notes="Raw 425k OPENDART pblntfty=I (거래소공시) records",
    ),
    # ---- S4 listed companies ----
    Dataset(
        dataset_id="s4_krx_ever_listed_table",
        path="data/acquired/round4/s4_listed_companies/krx_ever_listed_table.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
        notes="5-snapshot sample union; NOT full daily listed universe",
    ),
    Dataset(
        dataset_id="s4_krx_listed_companies_master",
        path="data/acquired/round4/s4_listed_companies/krx_listed_companies_master.csv",
        role="universe_lifecycle",
        scope="KR_in_scope_processed",
    ),
    # ---- S6 reconciliation sample ----
    Dataset(
        dataset_id="s6_reconciliation_sample_2024_01",
        path="data/acquired/round4/s6_flow_reconciliation/s6_reconciliation_sample_2024_01.csv",
        role="reconciliation_sample",
        scope="KR_in_scope_processed",
        notes="20 ticker × 22 day sample only; NOT full reconciliation",
    ),
    # ---- processed sector ----
    Dataset(
        dataset_id="krx_pit_sector_classifications",
        path="data/processed/krx_pit_sector_classifications.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="sector_aggregate_daily",
        path="data/processed/sector_aggregate_daily.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="sector_aggregate_daily_pit",
        path="data/processed/sector_aggregate_daily_pit.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="stock_sector_mapping_20260518",
        path="data/processed/stock_sector_mapping_20260518.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="stock_sector_mapping_pit_daily",
        path="data/processed/stock_sector_mapping_pit_daily.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="sector_membership_kis_snapshot_20260518",
        path="data/processed/sector_membership_kis_snapshot_20260518.csv",
        role="sector",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="stock_with_sector_daily",
        path="data/processed/stock_with_sector_daily.csv",
        role="derived_panel",
        scope="KR_in_scope_processed",
    ),
    Dataset(
        dataset_id="stock_with_sector_daily_pit",
        path="data/processed/stock_with_sector_daily_pit.csv",
        role="derived_panel",
        scope="KR_in_scope_processed",
    ),
]

# Non-KR (out-of-scope) marker only (no column contract built)
OUT_OF_SCOPE_DIRS = [
    ("us_equity_prices", "research_input_data/inputs/us_equity_prices/"),
    ("us_fundamentals", "research_input_data/inputs/us_fundamentals/"),
    ("global_etf", "research_input_data/inputs/global_etf/"),
    ("macro_features", "research_input_data/inputs/macro_features/"),
    ("futures", "research_input_data/inputs/futures/"),
]


# ---------------------------------------------------------------------------
# Column metadata templates per dataset
# ---------------------------------------------------------------------------
# Authoritative source per the panel header documentation in
# docs/data_schema_2010_2017.md + Round 4 ACQUISITION_SUMMARY.md +
# round3 referee lock + AGENTS.md.

DATE_COL = ("date_col", "vendor_panel", "ISO_date", "raw", "T_trade_day",
            "available_PIT", "date_key", "n/a",
            "trade date; per-row execution timestamp = same day after close")
TICKER_COL = ("ticker_col", "vendor_panel", "krx_ticker_6digit", "raw", "snapshot",
              "available_PIT", "ticker_key", "n/a",
              "KRX 6-digit code; not corp_code (DART); not permanent_id (W001 v2)")

# Panel columns (4 equity panels share most columns)
PANEL_COLUMN_SPEC = {
    "날짜": ("date_col", "vendor_kiwoom_or_krx", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "종목코드": ("ticker_col", "vendor_kiwoom_or_krx", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX 6-digit code"),
    "종목명": ("name_col", "vendor_kiwoom_or_krx", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "n/a", "name as of panel build snapshot; rename history not preserved → lookahead risk on cross-time joins"),
    "시가": ("price_col", "vendor_kiwoom_or_krx", "KRW", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "RAW unadjusted open; corporate-action split makes pre-action history artifactual"),
    "고가": ("price_col", "vendor_kiwoom_or_krx", "KRW", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "RAW unadjusted high"),
    "저가": ("price_col", "vendor_kiwoom_or_krx", "KRW", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "RAW unadjusted low"),
    "종가": ("price_col", "vendor_kiwoom_or_krx", "KRW", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "RAW unadjusted close; same as KRX종가 by definition in pre-NXT period"),
    "거래량": ("volume_col", "vendor_kiwoom_or_krx", "shares", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "RAW unadjusted shares; split-day artifactual"),
    "Change": ("derived", "vendor_kiwoom_or_krx", "ratio_decimal", "raw_unadjusted", "T_trade_day", "available_with_lookahead_risk", "n/a", "종가", "vendor-derived 1-day return from raw close; corporate-action distorted; not suitable as performance metric"),
    "기관순매매량": ("flow_col", "vendor_kiwoom_estimation", "shares", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "institution net shares; available T+0 after close, must shift +1 for execution"),
    "외국인순매매량": ("flow_col", "vendor_kiwoom_estimation", "shares", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "foreign net shares; same T+0-after-close timing"),
    "기관순매수금액추정": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매매량", "Kiwoom estimation (per FLOW_000007 finding: 95% within 5% of official KRX); 100% flagged via 수급금액추정여부"),
    "외국인순매수금액추정": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매매량", "same estimation rule"),
    "거래대금추정": ("derived", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day", "available_PIT", "n/a", "종가,거래량", "vendor approximation = close × volume; 100% flagged via 거래대금추정여부"),
    "시가총액추정": ("derived", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day", "available_PIT", "n/a", "종가,상장주식수", "vendor approximation = close × shares_outstanding; flagged via 시가총액추정여부"),
    "상장주식수": ("static_field", "vendor_kiwoom_or_krx", "shares", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "n/a", "shares-outstanding snapshot; corporate-action transitions not delineated within row history → PIT risk on capital events"),
    "수급금액추정여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "flag: 100% True per FLOW_000007"),
    "거래대금추정여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "flag: indicates close × volume estimation rather than KRX trading_value"),
    "시가총액추정여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "flag: indicates close × shares_outstanding estimation"),
    "동적유니버스포함": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "n/a", "vendor universe flag; selection rule NOT documented → cannot certify survivorship safety from this field alone"),
    "통합거래량반영여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "NXT integrated-market metadata; all False in pre-NXT files"),
    "통합종가반영여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "NXT integrated-market metadata"),
    "통합종가제외여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "NXT integrated-market metadata"),
    "가격범위후보정여부": ("flag", "vendor_kiwoom_or_krx", "bool", "raw", "snapshot", "available_PIT", "n/a", "n/a", "NXT post-correction flag"),
    "KRX종가": ("price_col", "krx_official_or_synth", "KRW", "raw_unadjusted", "T_trade_day", "available_PIT", "n/a", "종가", "native in 2010-2016/2025-2026; synthesised from 종가 (pre-NXT) in 2017-2024/2018-2024 — krx_close_source flag required"),
    "키움거래대금순위": ("rank_col", "vendor_kiwoom_estimation", "rank_int", "raw", "T_trade_day", "available_with_lookahead_risk", "n/a", "거래대금추정", "Kiwoom in-house liquidity rank; selection rule undocumented"),
}

# Market flow shared schema (kiwoom 2018+ integrated and 2025+ krx have same cols)
MARKET_FLOW_COLUMN_SPEC = {
    "date": ("date_col", "vendor_kiwoom_or_krx", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "kospi_foreign_net": ("flow_col", "vendor_kiwoom_estimation", "KRW_mil_or_count", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "KOSPI foreign net; unit ambiguous (mil KRW vs count) — see KR_OHLCV_UNIT_INVARIANT_A0 plausibility check"),
    "kospi_institution_net": ("flow_col", "vendor_kiwoom_estimation", "KRW_mil_or_count", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "institution net; same unit ambiguity"),
    "kospi_individual_net": ("flow_col", "vendor_kiwoom_estimation", "KRW_mil_or_count", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "individual net; same unit ambiguity"),
    "kospi_trade_volume": ("volume_col", "vendor_kiwoom_or_krx", "shares_or_count", "raw", "T_trade_day", "available_PIT", "n/a", "n/a", "trade volume; unit ambiguous"),
    "large_foreign_net": ("flow_col", "vendor_kiwoom_estimation", "KRW_mil_or_count", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "large-cap foreign net"),
    "large_institution_net": ("flow_col", "vendor_kiwoom_estimation", "KRW_mil_or_count", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "large-cap institution net"),
    "program_total_net_mil": ("flow_col", "vendor_kiwoom_or_krx", "KRW_mil", "raw", "T_trade_day", "available_PIT", "n/a", "n/a", "program trading total net (million KRW)"),
    "program_arb_net_mil": ("flow_col", "vendor_kiwoom_or_krx", "KRW_mil", "raw", "T_trade_day", "available_PIT", "n/a", "n/a", "arbitrage net"),
    "program_nonarb_net_mil": ("flow_col", "vendor_kiwoom_or_krx", "KRW_mil", "raw", "T_trade_day", "available_PIT", "n/a", "n/a", "non-arbitrage net"),
    "program_kospi200": ("index_col", "vendor_kiwoom_or_krx", "index_pt", "raw", "T_trade_day", "available_PIT", "n/a", "n/a", "KOSPI200 close (referenced by program flow)"),
    "program_basis": ("derived", "vendor_kiwoom_or_krx", "index_pt_or_pct", "raw", "T_trade_day", "available_with_lookahead_risk", "n/a", "n/a", "futures basis; unit ambiguous"),
}

# OPENDART list parquet schema
OPENDART_COLUMN_SPEC = {
    "rcept_no": ("identifier", "opendart_api", "14digit_string", "raw", "event_time", "available_PIT", "rcept_no_key", "n/a", "DART receipt number; primary identifier"),
    "rcept_dt": ("date_col", "opendart_api", "YYYYMMDD_string", "raw", "event_time", "available_PIT", "n/a", "n/a", "receipt date string"),
    "rcept_date": ("date_col", "opendart_api", "ISO_date", "raw", "event_time", "available_PIT", "date_key", "rcept_dt", "ISO normalisation of rcept_dt"),
    "corp_cls": ("category", "opendart_api", "enum_YKEN", "raw", "snapshot", "available_PIT", "n/a", "n/a", "Y=KOSPI K=KOSDAQ E=KONEX N=etc"),
    "corp_code": ("identifier", "opendart_api", "8digit_string", "raw", "snapshot", "available_PIT", "corp_code_key", "n/a", "DART corporate code (not KRX ticker)"),
    "stock_code": ("identifier", "opendart_api", "krx_ticker_6digit_or_null", "raw", "snapshot", "available_with_lookahead_risk", "ticker_key", "corp_code", "KRX ticker; can be null for unlisted; corp_code→stock_code mapping is current-snapshot, not historical PIT"),
    "corp_name": ("name_col", "opendart_api", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "corp_code", "current corporate name; rename history not preserved"),
    "report_nm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "free-text disclosure title"),
    "flr_nm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "filer name"),
    "rm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "remark field"),
    "pblntf_ty_query": ("static_field", "derived_query_param", "string", "derived", "snapshot", "n/a", "n/a", "n/a", "the pblntf_ty query parameter used at fetch time"),
    "query_bgn_de": ("static_field", "derived_query_param", "YYYYMMDD_string", "derived", "snapshot", "n/a", "n/a", "n/a", "fetch query start"),
    "query_end_de": ("static_field", "derived_query_param", "YYYYMMDD_string", "derived", "snapshot", "n/a", "n/a", "n/a", "fetch query end"),
    "dart_url": ("derived", "derived", "url", "derived", "event_time", "available_PIT", "n/a", "rcept_no", "constructed DART viewer URL"),
    "flag_capital_raise": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex over report_nm; NOT authoritative — S2 body parse required"),
    "flag_cb_bw": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_capital_reduction": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_audit_issue": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_trading_halt": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_litigation": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_large_holder": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_treasury_stock": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_merger_split": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_earnings": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_contract": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex; not authoritative"),
    "flag_event_risk": ("flag", "derived_regex", "bool", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "regex composite; not authoritative"),
}

# S1 adjusted OHLC schema (pykrx)
S1_ADJUSTED_COLUMN_SPEC = {
    "date": ("date_col", "pykrx_official", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "adj_open": ("price_col", "pykrx_adjusted", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "pykrx get_market_ohlcv(adjusted=True); cumulative factor embedded"),
    "adj_high": ("price_col", "pykrx_adjusted", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "adjusted high"),
    "adj_low": ("price_col", "pykrx_adjusted", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "adjusted low"),
    "adj_close": ("price_col", "pykrx_adjusted", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "adjusted close"),
    "adj_volume": ("volume_col", "pykrx_adjusted", "shares", "adjusted", "T_trade_day", "available_PIT", "n/a", "n/a", "adjusted volume"),
    "adj_return_pct": ("derived", "pykrx_adjusted", "ratio_decimal", "adjusted", "T_trade_day", "available_PIT", "n/a", "adj_close", "1-day return from adjusted close; cannot be used as performance metric in this phase"),
    "종목코드": ("ticker_col", "pykrx_official", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
}

# W001 v2 panel_with_adjusted_ohlc = panel + adj_* + adjusted_source flag (joins on date,종목코드)
W001_V2_ADJUSTED_COLUMN_SPEC = dict(PANEL_COLUMN_SPEC)
W001_V2_ADJUSTED_COLUMN_SPEC.update({
    "adj_open": ("price_col", "pykrx_adjusted_join", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "종목코드,날짜", "S1 join"),
    "adj_high": ("price_col", "pykrx_adjusted_join", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "종목코드,날짜", "S1 join"),
    "adj_low": ("price_col", "pykrx_adjusted_join", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "종목코드,날짜", "S1 join"),
    "adj_close": ("price_col", "pykrx_adjusted_join", "KRW", "adjusted", "T_trade_day", "available_PIT", "n/a", "종목코드,날짜", "S1 join"),
    "adj_volume": ("volume_col", "pykrx_adjusted_join", "shares", "adjusted", "T_trade_day", "available_PIT", "n/a", "종목코드,날짜", "S1 join"),
    "adj_return_pct": ("derived", "pykrx_adjusted_join", "ratio_decimal", "adjusted", "T_trade_day", "available_PIT", "n/a", "adj_close", "derived; not strategy-ready"),
    "adjusted_source": ("flag", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "n/a", "vendor_pykrx | missing"),
})

W001_V2_TRADABLE_COLUMN_SPEC = dict(W001_V2_ADJUSTED_COLUMN_SPEC)
W001_V2_TRADABLE_COLUMN_SPEC["tradable_state"] = (
    "category", "derived_w001_v2", "enum_string", "derived", "T_trade_day",
    "available_with_lookahead_risk", "n/a",
    "거래량,거래대금추정,KRX종가,s3_status_events",
    "v1.x derivation; panel_absence != officially_delisted (TRAD_000001 critical defect); v2 wiring uses S3 status events",
)

W001_V2_PERMANENT_ID_COLUMN_SPEC = {
    "ticker": ("identifier", "krx_official", "krx_ticker_6digit", "raw", "snapshot", "available_with_lookahead_risk", "ticker_key", "n/a", "KRX 6-digit; reused across delisting → new listing"),
    "permanent_id": ("identifier", "derived_w001_v2", "string", "derived", "snapshot", "available_PIT", "permanent_id_key", "corp_code_dart,ticker", "derived ID; DART corp_code primary, ticker fallback"),
    "permanent_id_source": ("flag", "derived_w001_v2", "string", "derived", "snapshot", "available_PIT", "n/a", "permanent_id", "dart_corp_code | krx_ticker_fallback"),
    "corp_code_dart": ("identifier", "opendart_api", "8digit_string_or_null", "raw", "snapshot", "available_with_lookahead_risk", "corp_code_key", "n/a", "DART corp code; null if no DART match"),
    "corp_name_dart": ("name_col", "opendart_api", "string_or_null", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "corp_code_dart", "DART name"),
    "name_krx": ("name_col", "krx_official", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "ticker", "KRX latest name"),
    "krx_first_snapshot": ("date_col", "derived_w001_v2", "YYYYMMDD_int", "derived", "snapshot", "available_PIT", "n/a", "ticker", "earliest KRX snapshot containing ticker"),
    "krx_last_snapshot": ("date_col", "derived_w001_v2", "YYYYMMDD_int", "derived", "snapshot", "available_with_lookahead_risk", "n/a", "ticker", "latest KRX snapshot containing ticker; reveals future delisting if read naively"),
    "krx_markets": ("category", "krx_official", "enum_string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KOSPI | KOSDAQ | KONEX"),
}

W001_V2_LISTING_STATUS_EVENTS_COLUMN_SPEC = {
    "ticker": ("identifier", "opendart_api_mapped", "krx_ticker_6digit", "raw", "event_time", "available_PIT", "ticker_key", "n/a", "mapped from corp_code"),
    "rcept_dt": ("date_col", "opendart_api", "ISO_date", "raw", "event_time", "available_PIT", "date_key", "n/a", "disclosure date"),
    "report_nm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "report title"),
    "category": ("category", "derived_w001_v2", "enum_string", "derived", "event_time", "available_with_lookahead_risk", "n/a", "report_nm", "suspension|resumption|delisting|managed|surveillance|none; derived from report_nm patterns"),
    "rcept_no": ("identifier", "opendart_api", "14digit_string", "raw", "event_time", "available_PIT", "rcept_no_key", "n/a", "DART receipt"),
}

W001_V2_LISTING_STATUS_TERMINAL_COLUMN_SPEC = {
    "ticker": ("identifier", "derived_w001_v2", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "terminal_status": ("category", "derived_w001_v2", "enum_string", "derived", "snapshot", "available_PIT", "n/a", "listing_status_events", "delisted | suspended_last_known | none"),
    "terminal_date": ("date_col", "derived_w001_v2", "ISO_date", "derived", "snapshot", "available_PIT", "n/a", "listing_status_events", "date of terminal event"),
}

# S3 KRX status events (filtered) + raw 425k
S3_STATUS_EVENTS_COLUMN_SPEC = {
    "corp_code": ("identifier", "opendart_api", "string", "raw", "snapshot", "available_PIT", "corp_code_key", "n/a", "DART corp_code"),
    "corp_name": ("name_col", "opendart_api", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "corp_code", "current name"),
    "stock_code": ("identifier", "opendart_api", "krx_ticker_or_null_float", "raw", "snapshot", "available_with_lookahead_risk", "ticker_key", "corp_code", "stored as float in raw CSV → null becomes NaN; type cast required"),
    "corp_cls": ("category", "opendart_api", "enum_YKEN", "raw", "snapshot", "available_PIT", "n/a", "n/a", "Y/K/E/N"),
    "report_nm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "report title"),
    "rcept_no": ("identifier", "opendart_api", "14digit_string", "raw", "event_time", "available_PIT", "rcept_no_key", "n/a", "DART receipt"),
    "flr_nm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "filer"),
    "rcept_dt": ("date_col", "opendart_api", "ISO_date", "raw", "event_time", "available_PIT", "date_key", "n/a", "disclosure date"),
    "rm": ("string_field", "opendart_api", "string", "raw", "event_time", "available_PIT", "n/a", "n/a", "remark"),
    "stock_code_str": ("identifier", "derived", "krx_ticker_6digit_str", "derived", "snapshot", "available_PIT", "ticker_key", "stock_code", "string cast of stock_code"),
}

# S4 listed companies master (snapshot rows) + ever_listed_table
S4_LISTED_MASTER_COLUMN_SPEC = {
    "snapshot_date": ("date_col", "pykrx_official", "YYYYMMDD_int", "raw", "snapshot", "available_PIT", "snapshot_key", "n/a", "pykrx get_market_ticker_list date"),
    "ticker": ("identifier", "pykrx_official", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "market": ("category", "pykrx_official", "enum_string", "raw", "snapshot", "available_PIT", "n/a", "n/a", "KOSPI | KOSDAQ"),
    "name": ("name_col", "pykrx_official", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "name at snapshot"),
}

S4_EVER_LISTED_COLUMN_SPEC = {
    "ticker": ("identifier", "pykrx_official", "krx_ticker_6digit", "raw", "snapshot", "available_with_lookahead_risk", "ticker_key", "n/a", "KRX ticker"),
    "first_snapshot": ("date_col", "derived", "YYYYMMDD_int", "derived", "snapshot", "available_with_lookahead_risk", "n/a", "snapshot_date", "earliest sample snapshot — NOT actual listing date; 5-snapshot sample only"),
    "last_snapshot": ("date_col", "derived", "YYYYMMDD_int", "derived", "snapshot", "available_with_lookahead_risk", "n/a", "snapshot_date", "latest sample snapshot — NOT actual delisting date"),
    "snapshot_count": ("count_col", "derived", "int", "derived", "snapshot", "available_with_lookahead_risk", "n/a", "n/a", "count across 5 samples"),
    "markets": ("category", "derived", "enum_string", "derived", "snapshot", "available_with_lookahead_risk", "n/a", "market", "set of markets across snapshots"),
    "name": ("name_col", "pykrx_official", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "ticker", "latest sample name"),
}

# S6 reconciliation sample (mostly diagnostic columns)
S6_RECON_COLUMN_SPEC_PLACEHOLDER = {}  # introspected at runtime

# Processed sector
SECTOR_PIT_COLUMN_SPEC = {
    "ticker": ("identifier", "kis_or_krx", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "date": ("date_col", "kis_or_krx", "ISO_date", "raw", "snapshot", "available_PIT", "date_key", "n/a", "snapshot date"),
    "sector_code": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "ticker", "sector code"),
    "sector_name": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "ticker", "sector name"),
}

SECTOR_AGGREGATE_COLUMN_SPEC = {
    "date": ("date_col", "derived", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "sector_code": ("category", "kis_or_krx", "string", "raw", "snapshot", "available_PIT", "sector_key", "n/a", "sector code"),
    "sector_name": ("category", "kis_or_krx", "string", "raw", "snapshot", "available_PIT", "n/a", "sector_code", "sector name"),
    "n_stocks": ("count_col", "derived", "int", "derived", "T_trade_day", "available_PIT", "n/a", "n/a", "count of stocks in sector that day"),
    "sum_market_cap": ("derived", "derived", "KRW", "derived", "T_trade_day", "available_PIT", "n/a", "시가총액추정", "sum of est market cap"),
    "sum_traded_value": ("derived", "derived", "KRW", "derived", "T_trade_day", "available_PIT", "n/a", "거래대금추정", "sum of est trading value"),
    "sum_foreign_net_buy_amount": ("derived", "derived", "KRW", "derived", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매수금액추정", "sum of vendor estimation"),
    "sum_foreign_net_buy_shares": ("derived", "derived", "shares", "derived", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매매량", "sum of foreign net shares"),
    "sum_institution_net_buy_amount": ("derived", "derived", "KRW", "derived", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매수금액추정", "sum of institution net"),
    "sum_institution_net_buy_shares": ("derived", "derived", "shares", "derived", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매매량", "sum"),
    "cap_weighted_return": ("derived", "derived", "ratio_decimal", "derived", "T_trade_day", "available_with_lookahead_risk", "n/a", "Change,시가총액추정", "cap-weighted Change; vendor Change is raw → distorted on split days"),
    "top1_market_cap_pct": ("derived", "derived", "ratio_decimal", "derived", "T_trade_day", "available_PIT", "n/a", "시가총액추정", "concentration metric"),
    "top2_market_cap_pct": ("derived", "derived", "ratio_decimal", "derived", "T_trade_day", "available_PIT", "n/a", "시가총액추정", "concentration metric"),
}

STOCK_SECTOR_MAPPING_COLUMN_SPEC = {
    "pdno": ("identifier", "kis_api", "12digit_string", "raw", "snapshot", "available_PIT", "n/a", "n/a", "KIS pdno (full code)"),
    "ticker": ("identifier", "kis_api", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "pdno", "KRX 6-digit slice"),
    "prdt_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KIS product name"),
    "kis_mcls": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KIS mid-classification"),
    "ksic": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KSIC code"),
    "final_sector_code": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "kis_mcls,ksic", "post-mapping sector"),
    "final_sector_name": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "final_sector_code", "post-mapping sector name"),
    "mapping_source": ("flag", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "n/a", "kis_mcls | ksic | manual"),
    "date": ("date_col", "kis_or_krx", "ISO_date", "raw", "snapshot", "available_PIT", "date_key", "n/a", "snapshot date"),
    "classification_date": ("date_col", "derived", "ISO_date", "derived", "snapshot", "available_PIT", "n/a", "n/a", "date the classification became effective"),
    "krx_industry_name": ("category", "krx_official", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KRX 업종명"),
}

# KIS sector membership snapshot - raw KIS API fields
SECTOR_MEMBERSHIP_KIS_COLUMN_SPEC = {
    "pdno": ("identifier", "kis_api", "12digit_string", "raw", "snapshot", "available_PIT", "n/a", "n/a", "KIS pdno"),
    "prdt_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "product name"),
    "mket_id_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "KIS market id"),
    "scty_grp_id_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "security group id"),
    "idx_bztp_lcls_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "KIS industry large class code"),
    "idx_bztp_lcls_cd_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "idx_bztp_lcls_cd", "large class name"),
    "idx_bztp_mcls_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "mid class code"),
    "idx_bztp_mcls_cd_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "idx_bztp_mcls_cd", "mid class name"),
    "idx_bztp_scls_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "small class code"),
    "idx_bztp_scls_cd_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "idx_bztp_scls_cd", "small class name"),
    "std_idst_clsf_cd": ("category", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "KSIC code"),
    "std_idst_clsf_cd_name": ("name_col", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "std_idst_clsf_cd", "KSIC name"),
    "lstg_abol_dt": ("date_col", "kis_api", "YYYYMMDD_string_or_null", "raw", "event_time", "available_with_lookahead_risk", "n/a", "pdno", "listing abolition date; null if still listed; latest snapshot only → PIT risk if read as historical truth"),
    "lstg_cptl_amt": ("derived", "kis_api", "KRW", "raw", "snapshot", "available_PIT", "n/a", "pdno", "listed capital amount"),
    "lstg_rqsr_issu_istt_cd": ("identifier", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "issuer code"),
    "lstg_rqsr_item_cd": ("identifier", "kis_api", "string", "raw", "snapshot", "available_PIT", "n/a", "pdno", "item code"),
    "lstg_stqt": ("static_field", "kis_api", "shares", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "pdno", "listed share quantity; current snapshot only"),
    "fetch_status": ("flag", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "n/a", "OK | ERROR"),
    "fetch_timestamp": ("date_col", "derived", "ISO_datetime", "derived", "snapshot", "available_PIT", "n/a", "n/a", "fetch wallclock time"),
    "http_status_code": ("flag", "derived", "int", "derived", "snapshot", "available_PIT", "n/a", "n/a", "HTTP status"),
    "error_message": ("string_field", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "n/a", "error string"),
}

# Processed: stock_with_sector_daily / pit
STOCK_WITH_SECTOR_DAILY_COLUMN_SPEC = {
    "date": ("date_col", "derived", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "ticker": ("identifier", "derived", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "sector_code": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "ticker", "sector code at row date"),
    "sector_name": ("category", "derived", "string", "derived", "snapshot", "available_PIT", "n/a", "sector_code", "sector name"),
    "classification_date": ("date_col", "derived", "ISO_date", "derived", "snapshot", "available_PIT", "n/a", "ticker", "effective date of classification used (PIT variant only)"),
    "업종명": ("category", "krx_official", "string", "raw", "snapshot", "available_PIT", "n/a", "ticker", "KRX 업종명 (PIT variant only)"),
    "market_cap": ("derived", "derived", "KRW", "derived", "T_trade_day", "available_PIT", "n/a", "시가총액추정", "alias of 시가총액추정 in panel"),
    "traded_value": ("derived", "derived", "KRW", "derived", "T_trade_day", "available_PIT", "n/a", "거래대금추정", "alias of 거래대금추정 in panel"),
    "foreign_net_buy_amount": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매수금액추정", "alias of panel column"),
    "foreign_net_buy_shares": ("flow_col", "vendor_kiwoom_estimation", "shares", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매매량", "alias"),
    "institution_net_buy_amount": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매수금액추정", "alias"),
    "institution_net_buy_shares": ("flow_col", "vendor_kiwoom_estimation", "shares", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매매량", "alias"),
    "daily_return": ("derived", "derived", "ratio_decimal", "raw_unadjusted", "T_trade_day", "available_with_lookahead_risk", "n/a", "Change", "alias of vendor Change column; raw-unadjusted distortion on split days"),
}

# krx_pit_sector_classifications
KRX_PIT_SECTOR_COLUMN_SPEC = {
    "date": ("date_col", "krx_official", "ISO_date", "raw", "snapshot", "available_PIT", "date_key", "n/a", "classification snapshot date"),
    "market": ("category", "krx_official", "string", "raw", "snapshot", "available_PIT", "n/a", "n/a", "KOSPI | KOSDAQ"),
    "종목코드": ("identifier", "krx_official", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "종목명": ("name_col", "krx_official", "string", "raw", "snapshot", "available_with_lookahead_risk", "n/a", "종목코드", "KRX name at snapshot"),
    "업종명": ("category", "krx_official", "string", "raw", "snapshot", "available_PIT", "n/a", "종목코드", "KRX 업종명"),
}

# S6 reconciliation sample
S6_RECONCILIATION_COLUMN_SPEC = {
    "ticker": ("identifier", "pykrx_official", "krx_ticker_6digit", "raw", "snapshot", "available_PIT", "ticker_key", "n/a", "KRX ticker"),
    "date": ("date_col", "pykrx_official", "ISO_date", "raw", "T_trade_day", "available_PIT", "date_key", "n/a", "trade date"),
    "krx_foreign": ("flow_col", "pykrx_official", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "KRX official foreign net buy amount"),
    "panel_foreign": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "외국인순매수금액추정", "panel estimation"),
    "krx_institution": ("flow_col", "pykrx_official", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "n/a", "KRX official institution net"),
    "panel_institution": ("flow_col", "vendor_kiwoom_estimation", "KRW", "raw", "T_trade_day_post_close", "available_with_lookahead_risk", "n/a", "기관순매수금액추정", "panel estimation"),
    "foreign_diff_pct": ("derived", "derived", "ratio_decimal", "derived", "T_trade_day", "available_PIT", "n/a", "krx_foreign,panel_foreign", "reconciliation gap"),
    "institution_diff_pct": ("derived", "derived", "ratio_decimal", "derived", "T_trade_day", "available_PIT", "n/a", "krx_institution,panel_institution", "reconciliation gap"),
}

# Dataset → column spec dispatcher
DATASET_SPEC_MAP = {
    "equity_panel_kiwoom_2010_2016": PANEL_COLUMN_SPEC,
    "equity_panel_dynamic_top100_2017_2024": PANEL_COLUMN_SPEC,
    "equity_panel_dynamic_top100_2018_2024": PANEL_COLUMN_SPEC,
    "equity_panel_krx_2025_2026": PANEL_COLUMN_SPEC,
    "market_flow_kiwoom_2010_2017": MARKET_FLOW_COLUMN_SPEC,
    "market_flow_kiwoom_2018_2026_integrated": MARKET_FLOW_COLUMN_SPEC,
    "market_flow_kiwoom_2025_2026_krx": MARKET_FLOW_COLUMN_SPEC,
    "opendart_kospi_disclosures_20180101_20260505": OPENDART_COLUMN_SPEC,
    "s1_adjusted_ohlc_all_tickers_2018_2026": S1_ADJUSTED_COLUMN_SPEC,
    "w001_v2_panel_with_adjusted_ohlc_2018_2026": W001_V2_ADJUSTED_COLUMN_SPEC,
    "w001_v2_panel_with_tradable_state": W001_V2_TRADABLE_COLUMN_SPEC,
    "w001_v2_permanent_id_master": W001_V2_PERMANENT_ID_COLUMN_SPEC,
    "w001_v2_listing_status_events": W001_V2_LISTING_STATUS_EVENTS_COLUMN_SPEC,
    "w001_v2_listing_status_terminal": W001_V2_LISTING_STATUS_TERMINAL_COLUMN_SPEC,
    "s3_krx_status_events_2018_2026": S3_STATUS_EVENTS_COLUMN_SPEC,
    "s3_dart_pblntfty_I_all_2018_2026": S3_STATUS_EVENTS_COLUMN_SPEC,  # same OPENDART list shape
    "s4_krx_ever_listed_table": S4_EVER_LISTED_COLUMN_SPEC,
    "s4_krx_listed_companies_master": S4_LISTED_MASTER_COLUMN_SPEC,
    "krx_pit_sector_classifications": SECTOR_PIT_COLUMN_SPEC,
    "sector_aggregate_daily": SECTOR_AGGREGATE_COLUMN_SPEC,
    "sector_aggregate_daily_pit": SECTOR_AGGREGATE_COLUMN_SPEC,
    "stock_sector_mapping_20260518": STOCK_SECTOR_MAPPING_COLUMN_SPEC,
    "stock_sector_mapping_pit_daily": STOCK_SECTOR_MAPPING_COLUMN_SPEC,
    "sector_membership_kis_snapshot_20260518": SECTOR_MEMBERSHIP_KIS_COLUMN_SPEC,
    "stock_with_sector_daily": STOCK_WITH_SECTOR_DAILY_COLUMN_SPEC,
    "stock_with_sector_daily_pit": STOCK_WITH_SECTOR_DAILY_COLUMN_SPEC,
    "s6_reconciliation_sample_2024_01": S6_RECONCILIATION_COLUMN_SPEC,
    "krx_pit_sector_classifications": KRX_PIT_SECTOR_COLUMN_SPEC,
}


# ---------------------------------------------------------------------------
# Filesystem inspection
# ---------------------------------------------------------------------------

def read_header(path: Path) -> list[str]:
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
        return list(df.columns)
    enc_candidates = ("utf-8-sig", "utf-8", "cp949", "euc-kr")
    for enc in enc_candidates:
        try:
            with open(path, newline="", encoding=enc) as f:
                reader = csv.reader(f)
                header = next(reader)
            return [h.strip("﻿") for h in header]
        except (UnicodeDecodeError, StopIteration):
            continue
    raise RuntimeError(f"could not decode header: {path}")


def count_rows(path: Path) -> int:
    if path.suffix == ".parquet":
        return len(pd.read_parquet(path))
    enc_candidates = ("utf-8-sig", "utf-8", "cp949", "euc-kr")
    for enc in enc_candidates:
        try:
            with open(path, encoding=enc) as f:
                return sum(1 for _ in f) - 1
        except UnicodeDecodeError:
            continue
    return -1


def inspect_datasets() -> list[Dataset]:
    enriched = []
    for ds in KR_DATASETS:
        abspath = REPO / ds.path
        if not abspath.exists():
            ds.rowcount = -1
            ds.notes = (ds.notes + " | MISSING_PATH").strip(" |")
            enriched.append(ds)
            continue
        try:
            cols = read_header(abspath)
            ds.columns = cols
        except Exception as e:  # noqa: BLE001
            ds.columns = []
            ds.notes = (ds.notes + f" | header_error={e}").strip(" |")
        try:
            ds.rowcount = count_rows(abspath)
        except Exception as e:  # noqa: BLE001
            ds.rowcount = -1
            ds.notes = (ds.notes + f" | rowcount_error={e}").strip(" |")
        enriched.append(ds)
    return enriched


# ---------------------------------------------------------------------------
# Column contract build
# ---------------------------------------------------------------------------

CONTRACT_FIELDS = (
    "source", "unit", "raw_or_adjusted",
    "timestamp_semantics", "pit_status",
    "identifier_key", "upstream_dependency",
)


def build_column_records(datasets: list[Dataset]) -> tuple[list[Column], list[dict]]:
    """Build column contract rows + defect ledger rows for undocumented OR ambiguous-metadata columns."""
    column_rows: list[Column] = []
    defect_rows: list[dict] = []
    defect_id = 1
    for ds in datasets:
        spec = DATASET_SPEC_MAP.get(ds.dataset_id, {})
        cols = ds.columns or []
        for col in cols:
            if col in spec:
                kind, source, unit, raw_or_adj, ts, pit, idk, up, notes = (
                    spec[col][0], spec[col][1], spec[col][2], spec[col][3],
                    spec[col][4], spec[col][5], spec[col][6], spec[col][7],
                    spec[col][8] if len(spec[col]) > 8 else "",
                )
                column_rows.append(Column(
                    dataset_id=ds.dataset_id, column_name=col,
                    source=source, unit=unit, raw_or_adjusted=raw_or_adj,
                    timestamp_semantics=ts, pit_status=pit,
                    identifier_key=idk, upstream_dependency=up, notes=notes,
                ))
                # Detect ambiguous unit / source / raw_or_adjusted as measurement defect
                ambiguities = []
                if "_or_" in unit or "UNKNOWN" in unit:
                    ambiguities.append(("unit_ambiguous", f"unit='{unit}'"))
                if "UNKNOWN" in source:
                    ambiguities.append(("source_unknown", f"source='{source}'"))
                if "UNKNOWN" in raw_or_adj:
                    ambiguities.append(("raw_or_adjusted_unknown", f"raw_or_adjusted='{raw_or_adj}'"))
                if pit == "uncertain":
                    ambiguities.append(("pit_uncertain", "pit_status='uncertain'"))
                if "synth" in source and raw_or_adj == "raw_unadjusted":
                    ambiguities.append(("synthesised_value", f"source='{source}' — synthesis rule must be documented at use site"))
                for code, detail in ambiguities:
                    defect_rows.append({
                        "defect_id": f"FMC_{defect_id:06d}",
                        "severity": "high" if code in ("source_unknown","raw_or_adjusted_unknown","pit_uncertain") else "medium",
                        "defect_class": code,
                        "dataset_id": ds.dataset_id,
                        "column_name": col,
                        "detail": detail,
                        "quarantine_action": (
                            "QUARANTINE — no strategy or feature usage until resolved"
                            if code in ("source_unknown","raw_or_adjusted_unknown","pit_uncertain")
                            else "ALLOW_WITH_GUARD — usage requires unit/synthesis annotation at call site"
                        ),
                        "remediation": "Update column spec in src/audit/measurement_a0/p0_1_field_metadata_contract.py with disambiguated value, re-run, and re-commit all 6 artifacts",
                    })
                    defect_id += 1
            else:
                column_rows.append(Column(
                    dataset_id=ds.dataset_id, column_name=col,
                    source="UNKNOWN", unit="UNKNOWN", raw_or_adjusted="UNKNOWN",
                    timestamp_semantics="UNKNOWN", pit_status="uncertain",
                    identifier_key="n/a", upstream_dependency="UNKNOWN",
                    notes="undocumented — see defect ledger",
                ))
                defect_rows.append({
                    "defect_id": f"FMC_{defect_id:06d}",
                    "severity": "high",
                    "defect_class": "undocumented_column",
                    "dataset_id": ds.dataset_id,
                    "column_name": col,
                    "detail": "source,unit,raw_or_adjusted,timestamp_semantics,pit_status,upstream_dependency all missing",
                    "quarantine_action": "QUARANTINE — no strategy or feature usage allowed",
                    "remediation": "Add column spec entry in src/audit/measurement_a0/p0_1_field_metadata_contract.py and re-run",
                })
                defect_id += 1
    return column_rows, defect_rows


def build_allowlist_denylist(column_rows: list[Column]) -> list[dict]:
    rows = []
    for c in column_rows:
        if c.source == "UNKNOWN":
            decision = "QUARANTINE"
            reason = "undocumented metadata"
        elif c.pit_status == "uncertain":
            decision = "QUARANTINE"
            reason = "PIT status uncertain"
        elif "_or_" in c.unit:
            decision = "ALLOW_WITH_GUARD"
            reason = f"unit ambiguous ({c.unit}) — call site must annotate via plausibility check"
        elif c.pit_status == "available_with_lookahead_risk":
            decision = "ALLOW_WITH_GUARD"
            reason = "PIT lookahead risk — must shift/lag at use site"
        elif c.raw_or_adjusted == "raw_unadjusted" and c.column_name in {"종가","시가","고가","저가","Change","거래량"}:
            decision = "ALLOW_WITH_GUARD"
            reason = "RAW unadjusted price/volume; use only with corporate-action handling — see KR_OHLCV_UNIT_INVARIANT_A0 / W001 v2 adjusted overlay"
        elif "regex" in c.source:
            decision = "ALLOW_WITH_GUARD"
            reason = "regex-derived flag; not authoritative; downstream may not treat as confirmed event"
        elif "estimation" in c.source:
            decision = "ALLOW_WITH_GUARD"
            reason = "vendor estimation; reconciliation gap acceptable (FLOW_000007 closure) but flag required at usage"
        elif "synth" in c.source:
            decision = "ALLOW_WITH_GUARD"
            reason = "synthesised value; synthesis rule must be documented at use site"
        else:
            decision = "ALLOW"
            reason = "metadata complete; usage permitted within phase-allowed scope"
        rows.append({
            "dataset_id": c.dataset_id, "column_name": c.column_name,
            "decision": decision, "reason": reason,
            "source": c.source, "pit_status": c.pit_status,
            "raw_or_adjusted": c.raw_or_adjusted,
        })
    return rows


# ---------------------------------------------------------------------------
# Downstream usage audit
# ---------------------------------------------------------------------------

USAGE_SCAN_DIRS = ("src/", "scripts/", "configs/", "research/")
USAGE_KEYWORDS = [
    # Korean panel cols
    "종가", "시가", "고가", "저가", "거래량", "Change",
    "기관순매매량", "외국인순매매량", "기관순매수금액추정", "외국인순매수금액추정",
    "거래대금추정", "시가총액추정", "상장주식수",
    "동적유니버스포함", "KRX종가", "키움거래대금순위",
    # Adjusted
    "adj_open", "adj_high", "adj_low", "adj_close", "adj_volume", "adj_return_pct", "adjusted_source",
    # Flow english
    "kospi_foreign_net", "kospi_institution_net", "kospi_individual_net",
    "program_total_net_mil", "program_arb_net_mil", "program_nonarb_net_mil",
    # OPENDART
    "rcept_no", "rcept_dt", "rcept_date", "corp_code", "stock_code", "report_nm",
    "flag_treasury_stock", "flag_cb_bw", "flag_capital_reduction", "flag_merger_split",
    # Sector
    "final_sector_code", "final_sector_name",
    # tradable / lifecycle
    "tradable_state", "permanent_id", "terminal_status", "terminal_date",
    "krx_first_snapshot", "krx_last_snapshot",
]


def grep_count(keyword: str) -> int:
    try:
        out = subprocess.run(
            ["grep", "-r", "--include=*.py", "-l", "-F", keyword]
            + [str(REPO / d) for d in USAGE_SCAN_DIRS if (REPO / d).exists()],
            capture_output=True, text=True, check=False,
        )
        if out.returncode > 1:
            return -1
        files = [l for l in out.stdout.splitlines() if l.strip()]
        return len(files)
    except Exception:
        return -1


def usage_audit() -> list[dict]:
    rows = []
    for kw in USAGE_KEYWORDS:
        rows.append({"keyword": kw, "files_referencing": grep_count(kw)})
    return rows


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_dataset_inventory(datasets: list[Dataset]) -> None:
    path = OUT / "dataset_inventory.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "path", "role", "scope", "rowcount", "n_columns", "notes"])
        for ds in datasets:
            w.writerow([ds.dataset_id, ds.path, ds.role, ds.scope, ds.rowcount, len(ds.columns), ds.notes])
        for tag, d in OUT_OF_SCOPE_DIRS:
            w.writerow([f"out_of_scope:{tag}", d, "non_KR", "out_of_scope", "n/a", "n/a", "non-Korean — not column-contracted in this A0"])


def write_column_contract(column_rows: list[Column]) -> None:
    path = OUT / "column_contract_table.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "column_name", "source", "unit", "raw_or_adjusted",
                    "timestamp_semantics", "pit_status", "identifier_key",
                    "upstream_dependency", "notes"])
        for c in column_rows:
            w.writerow([c.dataset_id, c.column_name, c.source, c.unit, c.raw_or_adjusted,
                        c.timestamp_semantics, c.pit_status, c.identifier_key,
                        c.upstream_dependency, c.notes])


def write_allowlist_denylist(rows: list[dict]) -> None:
    path = OUT / "field_allowlist_denylist.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset_id","column_name","decision","reason","source","pit_status","raw_or_adjusted"])
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_defect_ledger(defect_rows: list[dict]) -> None:
    path = OUT / "undocumented_field_defect_ledger.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["defect_id","severity","defect_class","dataset_id","column_name","detail","quarantine_action","remediation"])
        w.writeheader()
        for r in defect_rows:
            w.writerow(r)


def write_usage_audit_md(rows: list[dict], allow_rows: list[dict]) -> None:
    path = OUT / "downstream_field_usage_audit.md"
    quarantined = {(r["dataset_id"], r["column_name"]) for r in allow_rows if r["decision"] == "QUARANTINE"}
    quarantined_cols = sorted({c for _, c in quarantined})
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Downstream Field Usage Audit\n\n")
        f.write("Source-file count per keyword across `src/`, `scripts/`, `configs/`, `research/`.\n")
        f.write("Counts measure presence as substring, not authoritative call-graph reach.\n\n")
        f.write("## Usage counts\n\n")
        f.write("| keyword | files_referencing |\n|---|---:|\n")
        for r in sorted(rows, key=lambda r: -r["files_referencing"]):
            f.write(f"| `{r['keyword']}` | {r['files_referencing']} |\n")
        f.write("\n## Quarantined columns referenced in code\n\n")
        if not quarantined_cols:
            f.write("No quarantined columns appear in this keyword scan.\n")
        else:
            f.write("Each row below = a column with QUARANTINE decision in field_allowlist_denylist.csv.\n")
            f.write("Strategy / feature code MUST NOT use these until metadata is filled.\n\n")
            f.write("| column | files_referencing |\n|---|---:|\n")
            kw_index = {r["keyword"]: r["files_referencing"] for r in rows}
            for c in quarantined_cols:
                f.write(f"| `{c}` | {kw_index.get(c, 'not_scanned')} |\n")
        f.write("\n## Notes\n\n")
        f.write("- This scan is presence-only; semantic correctness of usage requires per-callsite review.\n")
        f.write("- No strategy reopen is implied by these counts.\n")


def write_contract_md(datasets: list[Dataset], col_rows: list[Column],
                      defect_rows: list[dict], allow_rows: list[dict]) -> None:
    path = OUT / "field_metadata_contract.md"
    n_ds = len([d for d in datasets if d.scope != "out_of_scope"])
    n_cols = len(col_rows)
    n_unknown = sum(1 for c in col_rows if c.source == "UNKNOWN")
    n_defects = len(defect_rows)
    n_allow = sum(1 for r in allow_rows if r["decision"] == "ALLOW")
    n_allow_guard = sum(1 for r in allow_rows if r["decision"] == "ALLOW_WITH_GUARD")
    n_quarantine = sum(1 for r in allow_rows if r["decision"] == "QUARANTINE")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# KR Field Metadata Contract — A0 Audit\n\n")
        f.write("Date: 2026-05-23\n")
        f.write("Scope: KR equity strategy-relevant datasets (raw + processed). ")
        f.write("Non-KR datasets (US prices, US fundamentals, macro, futures, global ETF) ")
        f.write("listed only as out-of-scope markers.\n\n")
        f.write("## Verdict\n\n")
        f.write("Measurement-layer A0 ONLY. No strategy testing. No return / NAV / Sharpe.\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Datasets contracted: {n_ds}\n")
        f.write(f"- Columns evaluated: {n_cols}\n")
        f.write(f"- Columns flagged UNKNOWN (undocumented): {n_unknown}\n")
        f.write(f"- Undocumented-field defects: {n_defects}\n")
        f.write(f"- Allowlist breakdown: ALLOW={n_allow} / ALLOW_WITH_GUARD={n_allow_guard} / QUARANTINE={n_quarantine}\n\n")
        f.write("## Contract fields\n\n")
        for fld in CONTRACT_FIELDS:
            f.write(f"- `{fld}`\n")
        f.write("\n## Dataset list\n\n")
        f.write("| dataset_id | role | scope | rowcount | n_cols |\n|---|---|---|---:|---:|\n")
        for ds in datasets:
            if ds.scope == "out_of_scope":
                continue
            f.write(f"| `{ds.dataset_id}` | {ds.role} | {ds.scope} | {ds.rowcount} | {len(ds.columns)} |\n")
        f.write("\nNon-KR markers in `dataset_inventory.csv` (US prices, fundamentals, macro, futures, global ETF) ")
        f.write("are NOT column-contracted in this phase.\n\n")
        f.write("## Decision policy applied\n\n")
        f.write("- `UNKNOWN` source → QUARANTINE + defect entry.\n")
        f.write("- `available_with_lookahead_risk` → ALLOW_WITH_GUARD.\n")
        f.write("- `uncertain` PIT status → QUARANTINE.\n")
        f.write("- Vendor regex-derived flags → ALLOW_WITH_GUARD (not authoritative for event truth).\n")
        f.write("- Vendor estimation columns → ALLOW_WITH_GUARD (reconciliation gap noted in FLOW_000007).\n")
        f.write("- RAW unadjusted price/volume columns → ALLOW_WITH_GUARD (corporate-action handling required).\n")
        f.write("- Else → ALLOW.\n\n")
        f.write("## Cross references\n\n")
        f.write("- `dataset_inventory.csv`\n- `column_contract_table.csv`\n- `field_allowlist_denylist.csv`\n")
        f.write("- `undocumented_field_defect_ledger.csv`\n- `downstream_field_usage_audit.md`\n\n")
        f.write("## Hard locks\n\n")
        f.write("- No field with `QUARANTINE` decision may be used in any strategy code path.\n")
        f.write("- No `ALLOW_WITH_GUARD` field may be used as a strategy signal without the guard documented.\n")
        f.write("- No metadata change without re-running this script and re-committing all 6 artifacts.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    datasets = inspect_datasets()
    col_rows, defect_rows = build_column_records(datasets)
    allow_rows = build_allowlist_denylist(col_rows)
    usage_rows = usage_audit()
    write_dataset_inventory(datasets)
    write_column_contract(col_rows)
    write_allowlist_denylist(allow_rows)
    write_defect_ledger(defect_rows)
    write_usage_audit_md(usage_rows, allow_rows)
    write_contract_md(datasets, col_rows, defect_rows, allow_rows)
    print(json.dumps({
        "datasets_inspected": len(datasets),
        "datasets_in_scope": sum(1 for d in datasets if d.scope != "out_of_scope"),
        "columns": len(col_rows),
        "unknown_columns": sum(1 for c in col_rows if c.source == "UNKNOWN"),
        "defects": len(defect_rows),
        "allow": sum(1 for r in allow_rows if r["decision"] == "ALLOW"),
        "allow_with_guard": sum(1 for r in allow_rows if r["decision"] == "ALLOW_WITH_GUARD"),
        "quarantine": sum(1 for r in allow_rows if r["decision"] == "QUARANTINE"),
    }, indent=2))


if __name__ == "__main__":
    main()
