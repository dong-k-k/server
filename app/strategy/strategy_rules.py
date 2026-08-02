STRATEGY_BY_PROFILE = {
    # TODO : 비율조정하기
    "STABILITY_FIRST": [
        ("FORWARD", 0.5),
        ("FX_INSURANCE_GENERAL", 0.3),
        ("FX_INSURANCE_OPTION", 0.2),
    ],
    "BALANCED": [
        ("FX_INSURANCE_OPTION", 0.4),
        ("FORWARD", 0.4),
        ("FOREIGN_CURRENCY_DEPOSIT", 0.2),
    ],
    "COST_OPPORTUNITY_FIRST": [
        ("FX_INSURANCE_OPTION", 0.5),
        ("FOREIGN_CURRENCY_DEPOSIT", 0.3),
        ("FORWARD", 0.2),
    ],
}


def build_strategy_context(risk_grade: str, profile_type: str, target_ratio_min: float, target_ratio_max: float) -> dict:
    strategies = STRATEGY_BY_PROFILE[profile_type]
    return {
        "hedgeTargetMin": target_ratio_min / 100,
        "hedgeTargetMax": target_ratio_max / 100,
        "groupTargets": [{"targetHedgeRatio": (target_ratio_min + target_ratio_max) / 200}],
        "strategies": [
            {"strategyType": st, "allocationRatio": ratio, "priority": i + 1}
            for i, (st, ratio) in enumerate(strategies)
        ],
    }