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

10 Structured elicitation questions (please answer / pick options)

1. Target users: (choose one or more)

   - [ ] Retail users
   - [ ] Internal research team
   - [ ] Automated alerts/batch processing
   - [ ] Other: ****\_\_****

2. Valuation methods at launch (pick minimum):

   - [ ] DCF (recommended mandatory)
   - [ ] Residual Income
   - [ ] Earnings Power Value
   - [ ] Multiples (sanity checks)

3. Input availability: where will historical financials come from?

   - [ ] Existing CSVs under `input/` (which files?)
   - [ ] Database (which DB / table?)
   - [ ] External API (ticker/data provider)
   - [ ] Manual entry/upload

4. Level of automation for MVP:

   - [ ] Manual per-company run (CLI / notebook)
   - [ ] Batch across a list of tickers (scheduled)
   - [ ] Real-time API endpoint

5. Output expectations:

   - Formats: (check) [ ] JSON [ ] CSV [ ] Markdown report [ ] HTML [ ] Charts
   - Mandatory fields: intrinsic value (total), per-share, market price, margin of safety, assumptions summary

6. Sensitivity configuration:

   - Which variables to expose for sensitivity matrix? (e.g., discount rate, terminal growth, margin)
   - Default ranges/steps for each variable.

7. Reproducibility & audit:

   - Persist assumptions with each run? (yes/no)
   - Version model & assumptions? (yes/no)
   - Store input hashes for audit? (yes/no)

8. Performance & scale:

   - Expected number of symbols per run and frequency.
   - Time target per symbol (e.g., < 1s, < 10s).

9. Acceptance criteria & tests:

   - Provide 2-3 validation cases (tickers + expected approximate values or known benchmarks).
   - Unit tests for numerical stability (small changes in inputs produce consistent output), error handling for missing data.

10. UX/Integration:

- Where will the feature live? (CLI script in `scripts/`, web UI under `src/`, notebook under `notebooks/`, API `src/api/`)
- Who approves the PR for merging to main? (names/roles)

Extras / Notes

- Suggested MVP scope: DCF implementation (baseline), CLI runner, basic report, and unit tests. Additional methods and UI can follow in subsequent sprints.
- If you want, I can prefill answers based on repo analysis and propose a concrete MVP plan.

Next steps

- You: answer the 10 questions inline in this file or tell me to prefill.
- Me: after answers, I will perform a repo data inventory and draft the `docs/valuation-spec.md` with formulas and I/O contracts.
