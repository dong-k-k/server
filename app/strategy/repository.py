from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.strategy.models import StrategyRecommendation


class StrategyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self, recommendation: StrategyRecommendation
    ) -> StrategyRecommendation:
        """
        종합 전략 추천 엔티티 저장
        """
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        return recommendation

    async def find_by_id(self, recommendation_id: int) -> Optional[StrategyRecommendation]:
        """
        추천 ID 기반 단건 조회
        """
        stmt = select(StrategyRecommendation).where(
            StrategyRecommendation.recommendation_id == recommendation_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()