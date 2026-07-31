# app/risk_profile/repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.risk_profile.models import RiskProfile


class RiskProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, risk_profile: RiskProfile) -> RiskProfile:
        """
        RiskProfile 엔티티를 DB에 저장
        """
        self.db.add(risk_profile)
        await self.db.commit()
        await self.db.refresh(risk_profile)
        return risk_profile

    async def find_by_id(self, profile_id: int) -> Optional[RiskProfile]:
        """
        RiskProfile ID로 단건 조회
        """
        result = await self.db.execute(
            select(RiskProfile).where(RiskProfile.id == profile_id)
        )
        return result.scalars().first()

    async def find_by_settlement_id(self, settlement_id: int) -> Optional[RiskProfile]:
        """
        (선택) settlement_id 기준 단건 조회 메서드
        """
        result = await self.db.execute(
            select(RiskProfile).where(RiskProfile.settlement_id == settlement_id)
        )
        return result.scalars().first()

    async def update(self, risk_profile: RiskProfile) -> RiskProfile:
        await self.db.commit()
        await self.db.refresh(risk_profile)
        return risk_profile
