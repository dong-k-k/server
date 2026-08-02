from app.strategy.models import StrategyRecommendation
from app.strategy.hedge_calculator import compute_avoided_loss_for_cards

ACTION_LABELS = {
    "LOW": "목표환율 알림 설정",
    "MEDIUM": "부분 헤지 및 환율 추이 모니터링",
    "HIGH": "즉시 헤지 실행 권장",
}

MIX_ELIGIBLE_STATUSES = ("RECOMMENDED", "CONDITIONAL")
MAX_STRATEGY_CARDS = 3


class StrategyService:
    def __init__(self, repo, ai_client):
        self.repo = repo
        self.ai_client = ai_client

    async def recommend(
        self, settlement_id, match_id, risk_profile_id, assessment, risk_profile, candidates,
        settlement, direction,
    ) -> "StrategyRecommendation":
        # 적합도 상위 3개까지만 전략 카드 후보로 사용 — "추천 금융상품" 섹션과
        # 동일한 정렬 기준을 적용해 두 섹션의 순위가 어긋나지 않게 한다.
        ranked_candidates = sorted(candidates, key=lambda c: c.fit_score, reverse=True)[:MAX_STRATEGY_CARDS]

        confirmed = [c for c in ranked_candidates if c.eligibility_status in MIX_ELIGIBLE_STATUSES]
        needs_review = [c for c in ranked_candidates if c.eligibility_status not in MIX_ELIGIBLE_STATUSES]
        if not confirmed:
            # 전부 RM_REVIEW_REQUIRED뿐이면(기존 동작 유지) 전체를 배분 대상으로 취급
            confirmed, needs_review = ranked_candidates, []

        total_hedge_krw = sum(float(c.recommended_hedge_amount_krw or 0) for c in confirmed)
        recommendation_mix = []
        for c in confirmed:
            hedge_krw = float(c.recommended_hedge_amount_krw or 0)
            if total_hedge_krw > 0:
                allocation_ratio = round(hedge_krw / total_hedge_krw, 2)
            else:
                allocation_ratio = round(1 / len(confirmed), 2)
            recommendation_mix.append({
                "productId": c.product_id,
                "productName": c.product_name,
                "provider": c.provider,
                "eligibilityStatus": c.eligibility_status,
                "allocationRatio": allocation_ratio,
            })

        for c in needs_review:
            recommendation_mix.append({
                "productId": c.product_id,
                "productName": c.product_name,
                "provider": c.provider,
                "eligibilityStatus": c.eligibility_status,
                "allocationRatio": None,
                "note": "직원 확인 후 배분비율이 반영됩니다.",
            })

        recommendation_reason = (
            f"위험등급 {assessment.risk_grade}(ES {assessment.es_pct}%), "
            f"{risk_profile.profile_type} 성향 기준 목표 헤지비율 "
            f"{risk_profile.target_hedge_ratio_min}~{risk_profile.target_hedge_ratio_max}% — "
            f"{ACTION_LABELS[assessment.risk_grade]}. "
            f"추천 상품 {len(recommendation_mix)}건은 RAG 적합도·자격 판정 결과를 기준으로 산정."
        )

        cards = [
            {
                "productId": c.product_id, "productName": c.product_name, "provider": c.provider,
                "recommendedHedgeAmountKrw": float(c.recommended_hedge_amount_krw) if c.recommended_hedge_amount_krw is not None else None,
            }
            for c in ranked_candidates
        ]
        cards_with_avoided_loss = await compute_avoided_loss_for_cards(
            cards, float(assessment.current_rate), direction, settlement, self.ai_client,
        )

        rec = StrategyRecommendation(
            settlement_id=settlement_id, match_id=match_id, risk_profile_id=risk_profile_id,
            recommendation_mix=recommendation_mix,
            recommendation_reason=recommendation_reason,
            avoided_loss_by_product=cards_with_avoided_loss,
        )
        return await self.repo.save(rec)