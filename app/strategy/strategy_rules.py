# 성향별 기본 배분(baseline) — "이 성향 유형이 선호하는 상품 구성의 출발점"이다.
# 개별 기업의 실제 리스크 지표(ES%·BEP 안전여유율·결제일조정가능여부)로
# 아래 _adjust_for_risk_indicators()가 이 baseline을 조정한다.
BASE_STRATEGY_BY_PROFILE = {
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

# "확정형" 상품(선물환·환변동보험 일반형)으로 분류 — ES%가 높거나 BEP 여유가
# 없을수록 이 그룹의 비중을 늘린다. 옵션형/예금형은 반대로 줄인다.
CERTAINTY_STRATEGY_TYPES = {"FORWARD", "FX_INSURANCE_GENERAL"}

# TODO : 추후 변경할 수 있다.
HIGH_ES_PCT_THRESHOLD = 10.0        # ES%가 이보다 높으면 "위험이 크다"고 판단
LOW_BEP_MARGIN_PCT_THRESHOLD = 3.0  # BEP 안전여유율이 이보다 낮으면 "손익분기 임박"
SHIFT_STEP = 0.1                    # 조건 1개 충족 시 확정형 쪽으로 옮기는 비중


def _adjust_for_risk_indicators(
    strategies: list[tuple[str, float]],
    es_pct: float,
    bep_safety_margin_pct: float | None,
    is_payment_adjustable: bool,
) -> list[tuple[str, float]]:
    shift = 0.0
    if es_pct is not None and es_pct >= HIGH_ES_PCT_THRESHOLD:
        shift += SHIFT_STEP
    if bep_safety_margin_pct is not None and bep_safety_margin_pct <= LOW_BEP_MARGIN_PCT_THRESHOLD:
        shift += SHIFT_STEP
    if is_payment_adjustable:
        # 결제일 조정이 가능한 기업은 자연헤지 여력이 있으므로 확정형 비중을 줄여도 된다
        shift -= SHIFT_STEP

    if shift == 0.0:
        return strategies

    certainty = [(t, r) for t, r in strategies if t in CERTAINTY_STRATEGY_TYPES]
    other = [(t, r) for t, r in strategies if t not in CERTAINTY_STRATEGY_TYPES]
    if not certainty or not other:
        return strategies

    # other 쪽에서 shift만큼 떼어 certainty 쪽에 고르게 분배(음수면 반대 방향)
    per_other = shift / len(other)
    other_adjusted = [(t, max(0.0, r - per_other)) for t, r in other]
    actually_moved = sum(r for _, r in other) - sum(r for _, r in other_adjusted)
    per_certainty = actually_moved / len(certainty)
    certainty_adjusted = [(t, r + per_certainty) for t, r in certainty]

    combined = certainty_adjusted + other_adjusted
    total = sum(r for _, r in combined)
    return [(t, round(r / total, 2)) for t, r in combined]


def build_strategy_context(
    risk_grade: str,
    profile_type: str,
    target_ratio_min: float,
    target_ratio_max: float,
    es_pct: float,
    bep_safety_margin_pct: float | None,
    is_payment_adjustable: bool,
) -> dict:
    base = BASE_STRATEGY_BY_PROFILE[profile_type]
    strategies = _adjust_for_risk_indicators(base, es_pct, bep_safety_margin_pct, is_payment_adjustable)
    return {
        "hedgeTargetMin": target_ratio_min / 100,
        "hedgeTargetMax": target_ratio_max / 100,
        "groupTargets": [{"targetHedgeRatio": (target_ratio_min + target_ratio_max) / 200}],
        "strategies": [
            {"strategyType": st, "allocationRatio": ratio, "priority": i + 1}
            for i, (st, ratio) in enumerate(strategies)
        ],
    }