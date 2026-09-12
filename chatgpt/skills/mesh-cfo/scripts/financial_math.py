from __future__ import annotations

import json
import math
import sys
from collections.abc import Sequence
from typing import Any


class FinanceInputError(ValueError):
    """Raised when a deterministic finance calculation receives invalid inputs."""


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FinanceInputError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise FinanceInputError(f"{name} must be a finite number")
    return result


def _cash_flows(values: Any) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or len(values) < 2:
        raise FinanceInputError("cash_flows must contain at least two periods")
    return [_number(value, f"cash_flows[{index}]") for index, value in enumerate(values)]


def _sign_changes(values: Sequence[float]) -> int:
    nonzero = [value for value in values if value != 0]
    return sum((left < 0) != (right < 0) for left, right in zip(nonzero, nonzero[1:], strict=False))


def roi(net_benefit: float, investment_cost: float) -> float:
    benefit = _number(net_benefit, "net_benefit")
    cost = _number(investment_cost, "investment_cost")
    if cost <= 0:
        raise FinanceInputError("investment_cost must be greater than zero")
    return benefit / cost


def npv(rate: float, cash_flows: Sequence[float]) -> float:
    rate = _number(rate, "rate")
    if rate <= -1:
        raise FinanceInputError("rate must be greater than -1")
    flows = _cash_flows(cash_flows)
    try:
        result = sum(value / ((1 + rate) ** period) for period, value in enumerate(flows))
    except (OverflowError, ZeroDivisionError) as exc:
        raise FinanceInputError("rate and cash-flow horizon produce an unstable NPV calculation") from exc
    if not math.isfinite(result):
        raise FinanceInputError("NPV result is not finite")
    return result


def irr(cash_flows: Sequence[float], *, tolerance: float = 1e-10, max_iterations: int = 256) -> float:
    flows = _cash_flows(cash_flows)
    if not any(value < 0 for value in flows) or not any(value > 0 for value in flows):
        raise FinanceInputError("IRR requires at least one negative and one positive cash flow")
    if _sign_changes(flows) != 1:
        raise FinanceInputError(
            "IRR is ambiguous for non-conventional cash flows with multiple sign changes; use an NPV profile or scenario analysis"
        )

    low = -0.999999999
    high = 1.0
    low_value = npv(low, flows)
    high_value = npv(high, flows)
    while low_value * high_value > 0 and high < 1_000_000:
        high = high * 2 + 1
        high_value = npv(high, flows)
    if low_value * high_value > 0:
        raise FinanceInputError("cash flows do not yield a bracketed IRR")

    for _ in range(max_iterations):
        midpoint = (low + high) / 2
        midpoint_value = npv(midpoint, flows)
        if abs(midpoint_value) <= tolerance or abs(high - low) <= tolerance:
            return midpoint
        if low_value * midpoint_value <= 0:
            high = midpoint
        else:
            low = midpoint
            low_value = midpoint_value
    return (low + high) / 2


def payback_period(cash_flows: Sequence[float], *, discount_rate: float | None = None) -> float | None:
    flows = _cash_flows(cash_flows)
    rate = None if discount_rate is None else _number(discount_rate, "discount_rate")
    if rate is not None and rate <= -1:
        raise FinanceInputError("discount_rate must be greater than -1")

    cumulative = flows[0]
    if cumulative >= 0:
        return 0.0
    for period in range(1, len(flows)):
        flow = flows[period]
        if rate is not None:
            flow = flow / ((1 + rate) ** period)
        previous = cumulative
        cumulative += flow
        if cumulative >= 0:
            if flow <= 0:
                return float(period)
            fraction = -previous / flow
            return (period - 1) + fraction
    return None


def break_even_units(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
    fixed = _number(fixed_costs, "fixed_costs")
    price = _number(price_per_unit, "price_per_unit")
    variable = _number(variable_cost_per_unit, "variable_cost_per_unit")
    if fixed < 0:
        raise FinanceInputError("fixed_costs cannot be negative")
    contribution = price - variable
    if contribution <= 0:
        raise FinanceInputError("price_per_unit must exceed variable_cost_per_unit")
    return fixed / contribution


def break_even_revenue(fixed_costs: float, contribution_margin_ratio: float) -> float:
    fixed = _number(fixed_costs, "fixed_costs")
    ratio = _number(contribution_margin_ratio, "contribution_margin_ratio")
    if fixed < 0:
        raise FinanceInputError("fixed_costs cannot be negative")
    if ratio <= 0 or ratio > 1:
        raise FinanceInputError("contribution_margin_ratio must be greater than zero and no greater than one")
    return fixed / ratio


def runway(available_cash: float, net_burn_per_period: float) -> dict[str, float | bool | None]:
    cash = _number(available_cash, "available_cash")
    burn = _number(net_burn_per_period, "net_burn_per_period")
    if cash < 0:
        raise FinanceInputError("available_cash cannot be negative")
    if burn <= 0:
        return {"cash_generative": True, "runway_periods": None}
    return {"cash_generative": False, "runway_periods": cash / burn}


def contribution_margin(revenue: float, variable_costs: float) -> dict[str, float | None]:
    revenue_value = _number(revenue, "revenue")
    variable = _number(variable_costs, "variable_costs")
    contribution = revenue_value - variable
    ratio = None if revenue_value == 0 else contribution / revenue_value
    return {"contribution": contribution, "contribution_margin_ratio": ratio}


def ltv_cac(ltv: float, cac: float) -> float:
    ltv_value = _number(ltv, "ltv")
    cac_value = _number(cac, "cac")
    if cac_value <= 0:
        raise FinanceInputError("cac must be greater than zero")
    return ltv_value / cac_value


def cash_conversion_cycle(dio: float, dso: float, dpo: float) -> float:
    return _number(dio, "dio") + _number(dso, "dso") - _number(dpo, "dpo")


def deal_discount_economics(
    list_price: float,
    fixed_cost_to_serve: float,
    discount_rate: float,
) -> dict[str, float]:
    """Return deal economics under an explicit fixed-cost-to-serve assumption.

    A price discount reduces revenue, not the supported fixed cost-to-serve. This avoids
    the donor deal-desk defect that proportionally scaled cost with the discount and
    understated margin-dollar loss.
    """

    price = _number(list_price, "list_price")
    cost = _number(fixed_cost_to_serve, "fixed_cost_to_serve")
    discount = _number(discount_rate, "discount_rate")
    if price <= 0:
        raise FinanceInputError("list_price must be greater than zero")
    if cost < 0:
        raise FinanceInputError("fixed_cost_to_serve cannot be negative")
    if discount < 0 or discount >= 1:
        raise FinanceInputError("discount_rate must be at least zero and less than one")

    post_revenue = price * (1 - discount)
    pre_margin = price - cost
    post_margin = post_revenue - cost
    pre_margin_ratio = pre_margin / price
    post_margin_ratio = post_margin / post_revenue
    margin_dollar_loss_ratio = 0.0 if pre_margin == 0 else (pre_margin - post_margin) / abs(pre_margin)

    return {
        "pre_discount_revenue": price,
        "post_discount_revenue": post_revenue,
        "pre_discount_margin_dollars": pre_margin,
        "post_discount_margin_dollars": post_margin,
        "pre_discount_margin_ratio": pre_margin_ratio,
        "post_discount_margin_ratio": post_margin_ratio,
        "margin_dollar_loss_ratio": margin_dollar_loss_ratio,
    }


def execute(request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise FinanceInputError("request must be an object")
    allowed = {"operation", "inputs"}
    if set(request) - allowed:
        raise FinanceInputError("request contains unsupported fields")
    operation = request.get("operation")
    inputs = request.get("inputs", {})
    if not isinstance(operation, str) or not operation:
        raise FinanceInputError("operation is required")
    if not isinstance(inputs, dict):
        raise FinanceInputError("inputs must be an object")

    if operation == "roi":
        result: Any = {"roi": roi(inputs.get("net_benefit"), inputs.get("investment_cost"))}
    elif operation == "npv":
        result = {"npv": npv(inputs.get("rate"), inputs.get("cash_flows"))}
    elif operation == "irr":
        result = {"irr": irr(inputs.get("cash_flows"))}
    elif operation == "payback":
        result = {"payback_periods": payback_period(inputs.get("cash_flows"))}
    elif operation == "discounted_payback":
        result = {
            "discounted_payback_periods": payback_period(
                inputs.get("cash_flows"), discount_rate=inputs.get("discount_rate")
            )
        }
    elif operation == "break_even":
        result = {
            "break_even_units": break_even_units(
                inputs.get("fixed_costs"),
                inputs.get("price_per_unit"),
                inputs.get("variable_cost_per_unit"),
            )
        }
    elif operation == "break_even_revenue":
        result = {
            "break_even_revenue": break_even_revenue(
                inputs.get("fixed_costs"), inputs.get("contribution_margin_ratio")
            )
        }
    elif operation == "runway":
        result = runway(inputs.get("available_cash"), inputs.get("net_burn_per_period"))
    elif operation == "contribution_margin":
        result = contribution_margin(inputs.get("revenue"), inputs.get("variable_costs"))
    elif operation == "ltv_cac":
        result = {"ltv_cac": ltv_cac(inputs.get("ltv"), inputs.get("cac"))}
    elif operation == "cash_conversion_cycle":
        result = {
            "cash_conversion_cycle": cash_conversion_cycle(
                inputs.get("dio"), inputs.get("dso"), inputs.get("dpo")
            )
        }
    elif operation == "deal_discount_economics":
        result = deal_discount_economics(
            inputs.get("list_price"),
            inputs.get("fixed_cost_to_serve"),
            inputs.get("discount_rate"),
        )
    else:
        raise FinanceInputError(f"unsupported operation: {operation}")
    return {"ok": True, "operation": operation, "result": result}


def main() -> int:
    try:
        request = json.load(sys.stdin)
        response = execute(request)
    except (FinanceInputError, json.JSONDecodeError, TypeError, OverflowError, ZeroDivisionError) as exc:
        response = {"ok": False, "error": "invalid_input", "message": str(exc)}
        sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
        return 2
    sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
