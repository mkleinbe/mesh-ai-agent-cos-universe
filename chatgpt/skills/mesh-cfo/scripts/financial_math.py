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


def npv(rate: float, cash_flows: Sequence[float]) -> float:
    rate = _number(rate, "rate")
    if rate <= -1:
        raise FinanceInputError("rate must be greater than -1")
    flows = _cash_flows(cash_flows)
    return sum(value / ((1 + rate) ** period) for period, value in enumerate(flows))


def irr(cash_flows: Sequence[float], *, tolerance: float = 1e-10, max_iterations: int = 256) -> float:
    flows = _cash_flows(cash_flows)
    if not any(value < 0 for value in flows) or not any(value > 0 for value in flows):
        raise FinanceInputError("IRR requires at least one negative and one positive cash flow")

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

    if operation == "npv":
        result: Any = {"npv": npv(inputs.get("rate"), inputs.get("cash_flows"))}
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
    elif operation == "runway":
        result = runway(inputs.get("available_cash"), inputs.get("net_burn_per_period"))
    elif operation == "contribution_margin":
        result = contribution_margin(inputs.get("revenue"), inputs.get("variable_costs"))
    elif operation == "ltv_cac":
        result = {"ltv_cac": ltv_cac(inputs.get("ltv"), inputs.get("cac"))}
    else:
        raise FinanceInputError(f"unsupported operation: {operation}")
    return {"ok": True, "operation": operation, "result": result}


def main() -> int:
    try:
        request = json.load(sys.stdin)
        response = execute(request)
    except (FinanceInputError, json.JSONDecodeError, TypeError) as exc:
        response = {"ok": False, "error": "invalid_input", "message": str(exc)}
        sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
        return 2
    sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
