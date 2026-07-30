from pydantic import BaseModel
from datetime import date

class SettlementItemCreate(BaseModel):
    amount: float
    currency: str
    price_fix_date: date
    settlement_date: date
    is_payment_adjustable: bool
    bep_rate: float | None = None

class ContractCreateRequest(BaseModel):
    profile_id: int
    contract_type: str
    payment_term: str
    advance_settled_amount: float | None = None
    netting_offset_amount: float | None = None
    settlement_items: list[SettlementItemCreate] = []  # 최소 1개(분할지급 시 여러 개)

class ContractResponse(BaseModel):
    contract_id: int
    settlement_ids: list[int]
