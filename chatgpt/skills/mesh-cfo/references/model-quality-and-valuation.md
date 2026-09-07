# Financial Model Quality and Valuation

Use this reference for management-finance model review, supported financial-statement analysis, valuation, and capital-allocation questions. It does not grant enterprise accounting, audit, trading, tax, treasury, or balance-sheet authority.

## Model integrity principles

1. Distinguish source inputs, assumptions, formulas, links, and outputs.
2. Prefer formulas over hardcoded derived values in forecast models so scenarios remain traceable.
3. Preserve the model's established units, signs, period definitions, and source lineage.
4. Never overwrite an existing formula or source value without making the change explicit.
5. Test the model at the driver, subtotal, cross-statement, and scenario levels.
6. Label analytical QA as model review, not audited assurance.

## Model quality checks

When applicable, test:
- formula consistency across periods;
- inputs versus derived values;
- broken or stale links;
- unit and sign consistency;
- period alignment;
- circularity and whether it is intentional;
- subtotal and roll-forward integrity;
- scenario toggles and hierarchy;
- missing or unexplained hardcodes;
- source comments or provenance for material assumptions.

For an integrated statement model, useful checks include:
- `Assets = Liabilities + Equity` for each period;
- cash tie-out between the cash-flow statement and balance sheet;
- net income linkage between the income statement and cash flow;
- retained-earnings roll-forward where supported;
- debt and working-capital schedules tying to the statements.

A passing model check means the tested model mechanics are internally consistent. It does not mean the numbers are audited, complete, GAAP-authoritative, or current.

## Financial statement analysis

Within approved source scope, analyze trends such as:
- revenue growth and mix;
- gross, contribution, EBITDA, EBIT, and net margins where available;
- operating leverage;
- cash conversion and working-capital movement;
- free cash flow;
- capital intensity;
- leverage and coverage metrics when supported;
- return metrics when source definitions are sufficiently reliable.

Every metric must identify the source period and definition. Do not infer enterprise ledger truth from an unsupported management artifact.

## Valuation method selection

Use valuation only when it serves an authorized business, capital-allocation, transaction, or strategic-analysis purpose. Do not provide autonomous trading recommendations or personal investment advice.

Select methods based on the economics and data quality:
- **DCF** for businesses with sufficiently supportable future cash flows;
- **Comparable-company analysis** for market-relative valuation using comparable definitions and periods;
- **Precedent transactions** when relevant transaction evidence is sufficiently comparable;
- **Sum-of-parts** for businesses with materially distinct economic segments;
- **Asset or other specialized methods** only when the business model and evidence justify them.

Triangulate methods when doing so improves decision quality. Do not average incompatible methods merely to create precision.

## DCF

A DCF should make the economic bridge visible:
1. historical base and normalization;
2. operating drivers and projected revenue;
3. margins and taxes appropriate to the analytical scope;
4. D&A, capital expenditure, and working capital when supported;
5. unlevered free cash flow;
6. WACC or other supported discount rate;
7. terminal value;
8. enterprise-to-equity bridge where authorized and supported;
9. sensitivity and scenario analysis.

### WACC

When WACC is used, state the source and date for:
- risk-free rate;
- equity risk premium;
- beta or other risk measure;
- cost of debt;
- tax assumption;
- capital structure weights.

Do not substitute an unsourced market default for a company-specific fact without labeling it as an explicit assumption.

### Terminal value

Use a defensible perpetuity-growth or exit-multiple approach. Terminal growth must remain below the discount rate for a Gordon-growth model. Show how much of enterprise value comes from terminal value and flag overreliance on terminal assumptions.

## Comparable analysis

For a comparable set:
- explain why each company or transaction is comparable;
- align periods and metric definitions;
- prefer medians when outliers can distort the group;
- separate observed market multiples from analyst adjustments;
- explain any premium or discount rather than embedding it invisibly.

## Sum-of-parts

Use sum-of-parts when operating segments have genuinely different economics or peer groups. Value each segment with a fit-for-purpose method, reconcile corporate or unallocated items, then bridge to the supported total. Do not invent segment data that the source does not provide.

## Sensitivity and scenarios

At minimum, expose the assumptions most capable of changing the conclusion. For DCF this commonly includes WACC, terminal growth or exit multiple, revenue growth, margin, and working-capital or capital-intensity assumptions.

A sensitivity table should contain a true base case and clearly identify the supported base assumptions. Bull, base, and bear cases are analytical scenarios, not probabilities unless evidence supports probability assignments.

## Output and confidence

Report:
- valuation purpose;
- methods used and why;
- source freshness;
- assumptions and normalization;
- range rather than false precision where appropriate;
- sensitivity and break points;
- confidence and unresolved data gaps;
- decision or approval owner.
