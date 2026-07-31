def classify_profile_type(total_score: int) -> str:
    if total_score <= 2:
        return "STABILITY_FIRST"
    if total_score <= 4:
        return "BALANCED"
    return "COST_OPPORTUNITY_FIRST"

def resolve_target_hedge_ratio(profile_type: str) -> tuple[int, int]:
    return {
        "STABILITY_FIRST": (80, 100),
        "BALANCED": (50, 80),
        "COST_OPPORTUNITY_FIRST": (20, 50),
    }[profile_type]