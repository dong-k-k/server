from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.contract.models import Contract, SettlementItem
from app.product.models import ProductMatchResult, ProductMatchItem


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_match_result(self, match_result: ProductMatchResult) -> ProductMatchResult:
        self.db.add(match_result)
        await self.db.commit()
        await self.db.refresh(match_result)
        return match_result

    async def find_match_result_by_id(self, match_id: int) -> Optional[ProductMatchResult]:
        stmt = (
            select(ProductMatchResult)
            .options(selectinload(ProductMatchResult.items))
            .where(ProductMatchResult.match_id == match_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def find_latest_match_by_profile(self, profile_id: int) -> Optional[ProductMatchResult]:
        stmt = (
            select(ProductMatchResult)
            .join(SettlementItem, ProductMatchResult.settlement_id == SettlementItem.settlement_id)
            .join(Contract, SettlementItem.contract_id == Contract.contract_id)
            .where(Contract.profile_id == profile_id)
            .order_by(ProductMatchResult.match_id.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()