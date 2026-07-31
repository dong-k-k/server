from enum import Enum

class Verdict(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    CONDITIONAL = "CONDITIONAL"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"

def evaluate_rule(rule, profile_value) -> str:
    if profile_value is None:
        return "NEEDS_CONFIRMATION"
    op, val = rule.operator, rule.value
    if op == "LTE":
        return "PASS" if profile_value <= val["value"] else "FAIL"
    if op == "GTE":
        return "PASS" if profile_value >= val["value"] else "FAIL"
    if op == "BETWEEN":
        return "PASS" if val["min"] <= profile_value <= val["max"] else "FAIL"
    if op == "IN":
        return "PASS" if profile_value in val["values"] else "FAIL"
    raise ValueError(f"알 수 없는 operator: {op}")

def evaluate_product(product, field_resolver) -> Verdict:
    results = [evaluate_rule(r, field_resolver(r.field)) for r in product.rules]
    if "FAIL" in results:
        return Verdict.NOT_ELIGIBLE
    if "NEEDS_CONFIRMATION" in results:
        return Verdict.CONDITIONAL
    return Verdict.ELIGIBLE

def calculate_fit_score(verdict: Verdict, matches_risk_grade: bool, unknown_field_count: int, is_low_cost: bool) -> int:
    score = {Verdict.ELIGIBLE: 3, Verdict.CONDITIONAL: 1, Verdict.NOT_ELIGIBLE: 0}[verdict]
    score += 2 if matches_risk_grade else 0
    score += 1 if unknown_field_count == 0 else 0
    score += 1 if is_low_cost else 0
    return score