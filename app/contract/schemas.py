from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SettlementItemCreate(BaseModel):
    amount: Decimal
    currency: str
    price_fix_date: date
    settlement_date: date
    is_payment_adjustable: bool
    bep_rate: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class SettlementItemResponse(SettlementItemCreate):
    settlement_id: int
    contract_id: int


class ContractCreateRequest(BaseModel):
    profile_id: int
    contract_type: str
    payment_term: str
    advance_settled_amount: Decimal | None = None
    netting_offset_amount: Decimal | None = None
    settlement_items: list[SettlementItemCreate] = Field(default_factory=list)


class ContractResponse(BaseModel):
    contract_id: int
    profile_id: int
    contract_type: str
    payment_term: str
    advance_settled_amount: Decimal | None = None
    netting_offset_amount: Decimal | None = None
    settlement_items: list[SettlementItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
