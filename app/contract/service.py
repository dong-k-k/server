from app.contract.models import Contract, SettlementItem
from app.contract.repository import ContractRepository
from app.contract.schemas import ContractCreateRequest, SettlementItemCreate


class ContractService:
    def __init__(self, repo: ContractRepository):
        self.repo = repo

    async def create_contract(self, req: ContractCreateRequest) -> Contract:
        contract = Contract(
            profile_id=req.profile_id,
            contract_type=req.contract_type,
            payment_term=req.payment_term,
            advance_settled_amount=req.advance_settled_amount,
            netting_offset_amount=req.netting_offset_amount,
        )
        contract.settlement_items = [
            SettlementItem(
                amount=item.amount,
                currency=item.currency,
                price_fix_date=item.price_fix_date,
                settlement_date=item.settlement_date,
                is_payment_adjustable=item.is_payment_adjustable,
                bep_rate=item.bep_rate,
            )
            for item in req.settlement_items
        ]
        return await self.repo.save(contract)

    async def get_contract(self, contract_id: int) -> Contract | None:
        return await self.repo.find_by_id(contract_id)

    async def update_contract(self, contract_id: int, req: ContractCreateRequest) -> Contract | None:
        contract = await self.repo.find_by_id(contract_id)
        if not contract:
            return None
        contract.profile_id = req.profile_id
        contract.contract_type = req.contract_type
        contract.payment_term = req.payment_term
        contract.advance_settled_amount = req.advance_settled_amount
        contract.netting_offset_amount = req.netting_offset_amount
        contract.settlement_items = [
            SettlementItem(
                amount=item.amount,
                currency=item.currency,
                price_fix_date=item.price_fix_date,
                settlement_date=item.settlement_date,
                is_payment_adjustable=item.is_payment_adjustable,
                bep_rate=item.bep_rate,
            )
            for item in req.settlement_items
        ]
        return await self.repo.update(contract)

    async def add_settlement_item_to_contract(
        self, contract_id: int, req: SettlementItemCreate
    ) -> SettlementItem | None:
        contract = await self.repo.find_by_id(contract_id)
        if not contract:
            return None

        return await self.repo.add_settlement_item(
            SettlementItem(
                contract_id=contract_id,
                amount=req.amount,
                currency=req.currency,
                price_fix_date=req.price_fix_date,
                settlement_date=req.settlement_date,
                is_payment_adjustable=req.is_payment_adjustable,
                bep_rate=req.bep_rate,
            )
        )
