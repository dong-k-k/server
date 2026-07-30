from app.risk_profile.models import RiskProfile
from app.risk_profile.scoring import classify_profile_type, resolve_target_hedge_ratio

class RiskProfileService:
    def __init__(self, repo):
        self.repo = repo

    async def submit(self, settlement_id: int, q1: int, q2: int, q3: int) -> RiskProfile:
        total = q1 + q2 + q3
        profile_type = classify_profile_type(total)
        ratio_min, ratio_max = resolve_target_hedge_ratio(profile_type)
        rp = RiskProfile(
            settlement_id=settlement_id, q1_score=q1, q2_score=q2, q3_score=q3,
            total_score=total, profile_type=profile_type,
            target_hedge_ratio_min=ratio_min, target_hedge_ratio_max=ratio_max,
        )
        return await self.repo.save(rp)