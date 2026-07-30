from app.contract.models import Contract, SettlementItem
from app.contract.repository import ContractRepository
from app.contract.schemas import ContractCreateRequest, SettlementItemCreateRequest

class ContractService:
    def __init__(self, repo: ContractRepository):
        self.repo = repo

    async def create_contract(self, req: ContractCreateRequest) -> Contract:
        # 1. 계약 기본 정보 생성
        contract = Contract(
            profile_id=req.profile_id,
            title=req.title,
            total_amount=req.total_amount,
            currency=req.currency,
        )
        # 2. settlement_items 리스트를 순회하며 SettlementItem 객체 생성 후 채우기
        if req.settlement_items:
            contract.settlement_items = [
                SettlementItem(
                    amount=item.amount,
                    due_date=item.due_date,
                    item_type=item.item_type
                )
                for item in req.settlement_items
            ]
        
        return await self.repo.save(contract)

    async def get_contract(self, contract_id: int) -> Contract | None:
        return await self.repo.find_by_id(contract_id)

    # 추가 엔드포인트용 로직: 기존 계약에 정산 항목 단독 추가
    async def add_settlement_item_to_contract(
        self, contract_id: int, req: SettlementItemCreateRequest
    ) -> SettlementItem | None:
        contract = await self.repo.find_by_id(contract_id)
        if not contract:
            return None
        
        item = SettlementItem(
            contract_id=contract_id,
            amount=req.amount,
            due_date=req.due_date,
            item_type=req.item_type
        )
        return await self.repo.add_settlement_item(item)