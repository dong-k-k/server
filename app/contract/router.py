from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.contract.repository import ContractRepository
from app.contract.service import ContractService
from app.contract.schemas import (
    ContractCreateRequest,
    ContractResponse,
    SettlementItemCreateRequest,
    SettlementItemResponse
)

router = APIRouter(prefix="/api/v1/contracts", tags=["contract"])

def get_contract_service(db: AsyncSession = Depends(get_db)) -> ContractService:
    return ContractService(ContractRepository(db))


# 1. 계약 전체 생성 (정산 항목 포함 가능)
@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    req: ContractCreateRequest,
    service: ContractService = Depends(get_contract_service)
):
    contract = await service.create_contract(req)
    return contract


# 2. 계약 단건 조회
@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="계약을 찾을 수 없습니다.")
    return contract


# 3. 추가 엔드포인트: 기존 계약에 정산 항목 나중에 추가하기
@router.post("/{contract_id}/settlement-items", response_model=SettlementItemResponse, status_code=status.HTTP_201_CREATED)
async def add_settlement_item(
    contract_id: int,
    req: SettlementItemCreateRequest,
    service: ContractService = Depends(get_contract_service)
):
    item = await service.add_settlement_item_to_contract(contract_id, req)
    if not item:
        raise HTTPException(status_code=404, detail="해당 계약을 찾을 수 없어 정산 항목을 추가할 수 없습니다.")
    return item