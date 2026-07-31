from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.contract.models import Contract, SettlementItem

class ContractRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, contract: Contract) -> Contract:
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def find_by_id(self, contract_id: int) -> Contract | None:
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.settlement_items))  # 연관된 정산 항목 함께 로드
            .where(Contract.contract_id == contract_id)
        )
        return result.scalar_one_or_none()

    async def add_settlement_item(self, item: SettlementItem) -> SettlementItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def find_settlement_by_id(self, settlement_id: int) -> SettlementItem | None:
        result = await self.db.execute(
            select(SettlementItem).where(SettlementItem.settlement_id == settlement_id)
        )
        return result.scalar_one_or_none()
