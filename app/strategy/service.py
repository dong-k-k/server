from app.strategy.models import StrategyRecommendation


class StrategyService:
    def __init__(self, repo, ai_client):
        self.repo = repo
        self.ai_client = ai_client

    async def recommend(self, settlement_id, match_id, risk_profile_id, assessment, risk_profile, candidates) -> "StrategyRecommendation":
        ai_result = await self.ai_client.get_strategy_mix({
            "riskGrade": assessment.risk_grade, "esPct": assessment.es_pct,
            "riskProfileType": risk_profile.profile_type,
            "candidateProducts": candidates,
        })
        rec = StrategyRecommendation(
            settlement_id=settlement_id, match_id=match_id, risk_profile_id=risk_profile_id,
            recommendation_mix=ai_result["recommendationMix"],
            recommendation_reason=ai_result["recommendationReason"],
        )
        return await self.repo.save(rec)
