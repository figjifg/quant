# Hard-Lock Compliance Check (Table-Context Design Proof)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0

| hard lock | status |
|---|---|
| Target = exactly 170 needs_table_context_design rows (0 attachment) | PASS (asserted) |
| Read local artifacts + cached bodies READ-ONLY only | PASS |
| NO download / API / credentials / source recovery / body reacquisition / cache repair | PASS |
| NO parser code/rule/version change; NO edits under src/parsers/ | PASS (parser imported read-only; not invoked to change outputs) |
| NO parser/candidate-linkage/body-confirmation rerun changing accepted outputs | PASS |
| Candidate date evidence is HYPOTHETICAL/PROOF-ONLY (named hypothetical_*, not effective_date/parsed_date) | PASS |
| NO effective date accepted/finalized; NO rcept_dt as effective date | PASS |
| NO manual adjudication/validation/approval | PASS |
| NO row marked parsed/recovered/executable/safe/authoritative/validated/approved/ready | PASS |
| Every row fail-closed | PASS |
| NO downstream / C2-C3 / event-log / executable-status table / strategy / execution | PASS |
| CSVs use LF line endings; git show --check must pass | PASS (lineterminator="\n") |
| Outputs separate design proof from approved parser behavior | PASS |
| No self-close; no CLOSE_NOTE; not moved to Closed/Frozen | PASS |
