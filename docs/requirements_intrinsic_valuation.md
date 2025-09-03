# Requirements — Intrinsic Valuation Feature

Status: Draft
Branch: feature/intrinsic-valuation

Purpose

- Capture the initial requirements for implementing Chapter 10 (intrinsic valuation) as a brownfield feature in this repository.

Checklist (requirements from the conversation)

- Move current docs to a folder — Done (committed to branch).
- Create domain primer — Done (`docs/valuation_primer.md`).
- Create requirements elicitation document — In progress (this file).
- Inventory data sources in repo — Pending.
- Define minimal valuation contract & API — Pending.
- Prototype implementation (PoC) — Pending.
- Tests, sensitivity, diagnostics, and docs — Pending.

Assumptions

- Work will continue on `feature/intrinsic-valuation` branch.
- Initial MVP will implement a DCF-based intrinsic valuation with sensitivity analysis.
- Input financials will be provided as CSVs or via existing repo data sources; if missing, a small ingestion script will be added.

Primary deliverables for MVP

1. `compute_dcf` function with clear input/output contract and tests.
2. CLI/script to run valuation for a single symbol and produce a report (JSON + markdown).
3. Sensitivity analysis matrix and small chart (optional notebook).
4. Documentation: primer, requirements, spec, and example run.

10 Structured elicitation questions (prefilled answers - review and adjust)

1. Target users: (choose one or more)

   - [x] Retail users
   - [x] Internal research team
   - [x] Automated alerts/batch processing
   - [ ] Other: ****\_\_****

2. Valuation methods at launch (pick minimum):

   - [x] DCF (mandatory for MVP)
   - [ ] Residual Income (later)
   - [ ] Earnings Power Value (later)
   - [x] Multiples (sanity checks / triangulation)

3. Input availability: where will historical financials come from?

   - [x] Existing CSVs under `input/` (example: `Indian_stocks_all_market.csv`, `Indian_stocks_nifty_200.csv` — need per-company financials CSVs)
   - [ ] Database (none currently configured for valuations)
   - [x] External API (optional: used to supplement or refresh data)
   - [ ] Manual entry/upload

Notes: repo contains ticker lists but not detailed per-year income statement / cash flow CSVs for all companies; data inventory step will confirm exact files.

4. Level of automation for MVP:

   - [x] Manual per-company run (CLI / notebook) — MVP
   - [ ] Batch across a list of tickers (scheduled) — follow-up
   - [ ] Real-time API endpoint — future

5. Output expectations:

   - Formats: (check) [x] JSON [ ] CSV [x] Markdown report [ ] HTML [x] Charts (png/svg)
   - Mandatory fields: intrinsic value (total), per-share, market price, margin of safety, assumptions summary, implied terminal multiple, run-id / assumptions hash

6. Sensitivity configuration:

   - Variables exposed: discount rate (r), terminal growth (g), revenue growth / margin assumptions (aggregate growth), capex intensity.
   - Default ranges/steps (MVP):
     - discount rate r: 8% to 12% step 0.5%
     - terminal growth g: 0% to 4% step 0.5%
     - revenue CAGR: baseline ± 200bps step 100bps
     - operating margin: baseline ± 300bps step 100bps

Rationale: small deltas in r/g create large swings; narrow ranges for sensible sensitivity table.

7. Reproducibility & audit:

   - Persist assumptions with each run? Yes
   - Version model & assumptions? Yes (simple versioning e.g., v0.1)
   - Store input hashes for audit? Yes

Implementation note: persist a small run metadata record (run-id, timestamp, git-ref, assumptions JSON, input checksums) alongside output.

8. Performance & scale:

   - Expected number of symbols per run and frequency: MVP — single-symbol interactive; later — batches of 100s nightly.
   - Time target per symbol: goal < 2s for compute-only (no network fetch); allow longer for data ingestion.

9. Acceptance criteria & tests:

   - Validation cases (example tickers in repo context; replace with canonical test fixtures):
     1. `RELIANCE` — sanity check vs public estimates (value should be in same order-of-magnitude; terminal implied growth should be reasonable).
     2. `TCS` / `TCS.NS` — large-cap stable earnings (EPV comparison should be plausible).
     3. `INFY` / `INFY.NS` — consistent margins and growth checks.
   - Unit tests:
     - compute_dcf returns stable numeric result for fixed inputs
     - sensitivity matrix shapes and monotonicity checks
     - error handling for missing critical inputs (raise clear exceptions)
   - Acceptance: all unit tests pass; example run produces report and sensitivity chart; diagnostics flags not more than 2 critical issues on canonical tickers.

10. UX/Integration:

- Where will the feature live? MVP: CLI script in `scripts/valuation_run.py` and an exploratory notebook in `notebooks/valuation_poc.ipynb`. Integration: API and web UI later under `src/api/` and `src/ui/`.
- Who approves the PR for merging to main? Repo owner / maintainer (Puneeth) and one reviewer from eng or data team.

Extras / Notes

- Suggested MVP scope: DCF implementation (baseline), CLI runner, basic report, and unit tests. Additional methods and UI can follow in subsequent sprints.

Next steps

- You: review & adjust the prefilled answers above. Mark changes inline or tell me which items to change.
- Me: after your confirmation, I'll perform a repo data inventory, create `docs/valuation-spec.md` with formulas and a minimal `compute_dcf` contract, then scaffold the MVP files (`scripts/valuation_run.py`, tests).

Discussion kickoff: once you confirm the targets above, I'll teach the key math in Chapter 10 focused on the DCF mechanics, discount rates (WACC vs required return), terminal value choices, normalization of financials, and sensitivity interpretation. Then we map each concept to concrete code/data tasks.
