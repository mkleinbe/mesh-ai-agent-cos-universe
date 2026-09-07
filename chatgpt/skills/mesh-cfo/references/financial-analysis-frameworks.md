# Financial Analysis Frameworks

Use these methods inside the CFO's existing Engagement Finance / FP&A authority. Select the smallest set that materially improves the decision. Do not treat any framework output as approval for a consequential action.

## Decision hierarchy

1. **NPV** for cash-flow decisions where time value of money matters.
2. **IRR** as a comparative return metric when cash-flow patterns make it meaningful.
3. **Payback** as a liquidity and recovery-speed constraint.
4. **ROI** as a simple supplementary return measure.
5. **Break-even** for price, volume, contribution, and fixed-cost questions.
6. **Sensitivity and Scenario** analysis to expose decision fragility and assumption dependence.

A positive metric is evidence, not automatic authorization. Do not automatically accept an initiative solely because one metric clears a threshold.

## ROI

Use ROI for a simple comparison of net benefit to investment cost.

`ROI = Net Benefit / Investment Cost`

State the period, included benefits, included costs, and whether benefits are cash, accounting, or estimated economic value. ROI does not account for time value of money unless explicitly adjusted.

## NPV

Use NPV for multi-period cash-flow decisions.

`NPV = sum(Cash Flow_t / (1 + discount_rate)^t) - Initial Investment`

Document the discount rate source, cash-flow timing, terminal assumptions if any, and whether cash flows are nominal or real. NPV explicitly incorporates the time value of money.

## IRR

IRR is the discount rate that makes NPV equal zero. Compare it with an explicitly supported hurdle rate. Flag non-conventional cash flows that can create multiple or misleading IRRs. For mutually exclusive alternatives, prefer NPV when IRR and NPV conflict.

## Payback

Simple payback identifies when cumulative undiscounted cash inflows recover the initial investment. Discounted payback uses present values. Payback is useful for liquidity and risk framing, but it ignores value after the recovery point.

## Break-even

For a unit model:

`Break-even Units = Fixed Costs / (Price per Unit - Variable Cost per Unit)`

`Break-even Revenue = Fixed Costs / Contribution Margin Ratio`

Use supported fixed, variable, price, utilization, and volume assumptions. If engagement economics are non-unit based, translate the same concept into billable capacity, utilization, contribution dollars, or another supported operational driver.

## Sensitivity analysis

Test the variables most likely to change the recommendation. Typical drivers include price, utilization, delivery cost, labor mix, volume, timing, discount rate, churn, acquisition cost, collections timing, and forecast conversion.

Prefer decision-relevant ranges supported by evidence. If a range is hypothetical, label it as an assumption. Identify the break point at which the recommendation changes.

## Scenario analysis

Maintain at least a base case and meaningful downside when uncertainty can affect a material decision. Add upside only when it improves decision quality. Do not assign probabilities without evidence.

For each scenario show:
- driver changes;
- economic outcome;
- liquidity or working-capital impact where supported;
- decision threshold or trigger;
- major unresolved uncertainty.

## Business-case structure

A decision-ready business case should contain:
1. decision and alternatives;
2. current-state economics or cost of inaction;
3. source-backed assumptions;
4. ROI/NPV/IRR/payback/break-even methods that are actually relevant;
5. sensitivity and scenario results;
6. qualitative benefits that are clearly separated from quantified benefits;
7. risks and mitigations;
8. recommendation, confidence, approval status, and next owner.

## Guardrails

- Never invent a discount rate, hurdle rate, probability, or benefit and present it as fact.
- Never convert donor rules of thumb or industry benchmark ranges into Mesh policy.
- Never approve price, discount, spend, investment, contract, or capital commitment.
- Preserve source provenance and explicit assumptions for every material number.
