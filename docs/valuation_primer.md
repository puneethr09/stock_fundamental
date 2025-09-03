# Intrinsic Valuation — Primer (Chapter 10)

Purpose

- Give a concise, practical summary of intrinsic valuation approaches from Chapter 10 and related common methods.
- Provide quick checks, assumptions, and a short Q&A to drive requirements.

Summary
Intrinsic valuation estimates the "true" value of a business based on fundamentals (cash flows, earnings, balance sheet) rather than market sentiment. Common approaches:

1. Discounted Cash Flow (DCF)

- Project free cash flows (FCF) for a forecast horizon (typically 5–10 years).
- Choose a terminal value (perpetuity growth or exit multiple).
- Discount projected cash flows and terminal value to present value using a discount rate (WACC or required return).
- Sum PVs and divide by diluted shares to get intrinsic price per share.

2. Residual Income / Abnormal Earnings

- Start from book value and forecast residual earnings (earnings minus required return on equity).
- Discount residual incomes; add to current book value for intrinsic value.
- Useful when FCF is noisy or when accounting earnings capture firm economics better.

3. Earnings Power Value (EPV)

- Capitalize current normalized earnings by cost of capital to estimate value under zero growth.
- Good for stable businesses with predictable earnings.

4. Comparative / Multiple-based Checks

- Use P/E, EV/EBITDA, P/FCF as sanity checks or short-cuts.
- Not a replacement for intrinsic methods but helpful for triangulation.

Key inputs

- Historical financials: revenue, margins, capex, working capital, depreciation, tax rate.
- Forecast assumptions: revenue growth rates, margin trajectory, capex intensity, working capital behavior.
- Discount rate: WACC (needs market cap, debt, cost of equity, cost of debt) or required return for equity-only models.
- Terminal value method and assumptions (g, multiple).
- Shares outstanding / dilution schedule.

Common assumptions & pitfalls

- Small changes in discount rate or terminal growth produce large value swings — require sensitivity analysis.
- Forecast horizon: short horizons with conservative terminal assumptions reduce forecasting noise.
- One-off items and accounting noise must be normalized.
- Use rolling shares and non-operating assets/liabilities adjustments.

Outputs to present

- Intrinsic value (total, per-share).
- Price vs market comparison and margin of safety.
- Sensitivity table (value vs discount rate and terminal growth).
- Key drivers list (which inputs drive most of the variance).

Simple validation checks

- Check implied terminal multiple (terminal value / terminal-year EBIT or FCF) and compare to peers.
- Check implied growth from Gordon growth formula given the value; if implied growth > plausible economic growth, flag.
- Recompute value using conservative/optimistic scenarios.

Quick worked example (toy)

- Latest FCF: 100
- Forecast FCFs: Year1..5 = 110, 121, 133, 146, 161 (10% growth)
- Terminal growth g = 3%, discount r = 10%
- Terminal value (perpetuity): TV = FCF5 * (1 + g) / (r - g) = 161*1.03 / 0.07 ≈ 2371
- Discount PVs of FCF1..5 and TV to present value → sum → divide by shares to get price.

Suggested minimal feature contracts (what to implement first)

- Function: compute_dcf(historical_financials, forecasts, discount_rate, terminal_method, terminal_param, shares) -> {total_value, per_share, sensitivities, diagnostics}
- Inputs: plain numeric arrays / pandas DataFrame; explicit contract for missing data handling.
- Diagnostics: implied multiples, flagged assumptions, normalization log.

Starter Q&A (to use in requirements elicitation)

1. Who are the target users of this feature? (retail, research team, automated alerts?)
2. Which valuation methods should be supported at launch (DCF mandatory?)
3. Required inputs available in repo or external sources? (I.e., historical income statement / cash flow data)
4. Level of automation: manual input per-company, batch processing, or API-driven?
5. UI expectations: CLI/script/report/interactive notebook/web UI/charting?
6. Desired output formats: JSON, CSV, PDF report, HTML, interactive charts?
7. Sensitivity analysis: which variables to expose (discount rate, terminal growth, margin)?
8. Auditing & reproducibility: do we need to persist assumptions, model versions, and input hashes?
9. Performance needs: real-time single-symbol compute vs batch across universe?
10. Acceptance criteria: tolerated error ranges, test cases, dataset used for validation.

Next steps (my recommendation)

- Run the 10-question requirements elicitation and capture answers to `docs/requirements_intrinsic_valuation.md`.
- Then perform a repo data inventory to confirm available inputs.

References / further reading

- Standard corporate finance texts: Damodaran (valuation), Pratt, Koller.
- Chapter 10 of the book (your copy) — use examples and assumptions there.

---

(End of primer)
