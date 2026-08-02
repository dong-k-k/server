HEDGE_RATIO_BY_PROFILE = {"STABILITY_FIRST": 90, "BALANCED": 65, "COST_OPPORTUNITY_FIRST": 35}
ACTION_BY_GRADE = {"HIGH": "IMMEDIATE_HEDGE", "MEDIUM": "PARTIAL_HEDGE_MONITOR", "LOW": "TARGET_ORDER"}

def decide_strategy_mix(risk_grade: str, profile_type: str, candidates: list[dict]) -> dict:
    target_ratio = HEDGE_RATIO_BY_PROFILE[profile_type]
    action = ACTION_BY_GRADE[risk_grade]

    full_cover = next((c for c in candidates if c.get("strategy_group") == "FX_HEDGING"), None)
    alt = next((c for c in candidates if c is not full_cover), None)

    mix = []
    if full_cover:
        mix.append({"strategyType": "FULL_COVER", "productId": full_cover["product_id"], "allocationRatio": target_ratio / 100})
    if alt:
        mix.append({"strategyType": "SUPPLEMENTARY", "productId": alt["product_id"], "allocationRatio": (100 - target_ratio) / 100})

    reason = f"위험등급 {risk_grade}, 성향 {profile_type} 기준 목표 헤지비율 {target_ratio}%로 {action} 권장"
    return {"recommendedAction": action, "recommendationMix": mix, "recommendationReason": reason}