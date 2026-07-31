from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.contract.models import Contract, SettlementItem
from app.risk.models import FxRiskAssessment


class RiskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, assessment: FxRiskAssessment) -> FxRiskAssessment:
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def find_by_id(self, assessment_id: int) -> FxRiskAssessment | None:
        result = await self.db.execute(
            select(FxRiskAssessment)
            .options(selectinload(FxRiskAssessment.scenarios))
            .where(FxRiskAssessment.assessment_id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def find_by_settlement_id(self, settlement_id: int) -> FxRiskAssessment | None:
        result = await self.db.execute(
            select(FxRiskAssessment)
            .options(selectinload(FxRiskAssessment.scenarios))
            .where(FxRiskAssessment.settlement_id == settlement_id)
            .order_by(FxRiskAssessment.created_at.desc())
        )
        return result.scalars().first()

    async def find_latest_by_profile(self, profile_id: int) -> FxRiskAssessment | None:
        result = await self.db.execute(
            select(FxRiskAssessment)
            .join(SettlementItem, FxRiskAssessment.settlement_id == SettlementItem.settlement_id)
            .join(Contract, SettlementItem.contract_id == Contract.contract_id)
            .where(Contract.profile_id == profile_id)
            .order_by(FxRiskAssessment.created_at.desc())
        )
        return result.scalars().first()
