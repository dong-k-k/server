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
            counterparty_country=req.counterparty_country,
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
        saved = await self.repo.save(contract)
        return await self.repo.find_by_id(saved.contract_id)

    async def get_contract(self, contract_id: int) -> Contract | None:
        return await self.repo.find_by_id(contract_id)

    async def get_contracts_by_profile(self, profile_id: int) -> list[Contract]:
        return await self.repo.find_by_profile_id(profile_id)

    async def update_contract(self, contract_id: int, req: ContractCreateRequest) -> Contract | None:
        contract = await self.repo.find_by_id(contract_id)
        if not contract:
            return None
        contract.profile_id = req.profile_id
        contract.contract_type = req.contract_type
        contract.payment_term = req.payment_term
        contract.counterparty_country = req.counterparty_country
        contract.advance_settled_amount = req.advance_settled_amount
        contract.netting_offset_amount = req.netting_offset_amount

        # 기존 정산 항목은 삭제 후 재생성하지 않고 값만 덮어씀 —
        # 이미 리스크 진단/상품매칭이 이 settlement_id를 참조 중이면
        # 삭제 시 FK 제약 위반(500)이 나기 때문.
        existing_items = list(contract.settlement_items)
        for i, item in enumerate(req.settlement_items):
            if i < len(existing_items):
                existing = existing_items[i]
                existing.amount = item.amount
                existing.currency = item.currency
                existing.price_fix_date = item.price_fix_date
                existing.settlement_date = item.settlement_date
                existing.is_payment_adjustable = item.is_payment_adjustable
                existing.bep_rate = item.bep_rate
            else:
                contract.settlement_items.append(
                    SettlementItem(
                        amount=item.amount, currency=item.currency,
                        price_fix_date=item.price_fix_date, settlement_date=item.settlement_date,
                        is_payment_adjustable=item.is_payment_adjustable, bep_rate=item.bep_rate,
                    )
                )
        # 요청에 항목 수가 줄어든 경우, 남는 기존 항목은 지금은 삭제하지 않고 그대로 둠
        # (이미 분석 결과가 붙어있을 수 있어 안전 우선)

        saved = await self.repo.save(contract)
        return await self.repo.find_by_id(saved.contract_id)

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
