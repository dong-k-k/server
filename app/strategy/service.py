from app.strategy.models import StrategyRecommendation
from app.strategy.hedge_calculator import compute_avoided_loss_for_cards


class StrategyService:
    def __init__(self, repo, ai_client):
        self.repo = repo
        self.ai_client = ai_client

    async def recommend(
        self, settlement_id, match_id, risk_profile_id, assessment, risk_profile, candidates,
        settlement, direction,
    ) -> "StrategyRecommendation":
        ai_result = await self.ai_client.get_strategy_mix({
            "riskGrade": assessment.risk_grade, "esPct": assessment.es_pct,
            "riskProfileType": risk_profile.profile_type,
            "candidateProducts": [
                {"productId": c.product_id, "eligibilityStatus": c.eligibility_status, "fitScore": c.fit_score}
                for c in candidates
            ],
        })

        cards = [
            {
                "productId": c.product_id, "productName": c.product_name, "provider": c.provider,
                "recommendedHedgeAmountKrw": float(c.recommended_hedge_amount_krw) if c.recommended_hedge_amount_krw is not None else None,
            }
            for c in candidates
        ]
        cards_with_avoided_loss = await compute_avoided_loss_for_cards(
            cards, float(assessment.current_rate), direction, settlement, self.ai_client,
        )

        rec = StrategyRecommendation(
            settlement_id=settlement_id, match_id=match_id, risk_profile_id=risk_profile_id,
            recommendation_mix=ai_result["recommendationMix"],
            recommendation_reason=ai_result["recommendationReason"],
            avoided_loss_by_product=cards_with_avoided_loss,
        )
        return await self.repo.save(rec)