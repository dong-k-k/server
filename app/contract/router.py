from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.contract.repository import ContractRepository
from app.contract.schemas import (
    ContractCreateRequest,
    ContractResponse,
    SettlementItemCreate,
    SettlementItemResponse,
)
from app.contract.service import ContractService
from app.core.db import get_db

router = APIRouter(prefix="/api/v1/contracts", tags=["contracts"])


def get_contract_service(db: AsyncSession = Depends(get_db)) -> ContractService:
    return ContractService(ContractRepository(db))


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    req: ContractCreateRequest,
    service: ContractService = Depends(get_contract_service),
):
    return await service.create_contract(req)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service),
):
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.get("", response_model=list[ContractResponse])
async def list_contracts(profile_id: int, service: ContractService = Depends(get_contract_service)):
    return await service.get_contracts_by_profile(profile_id)


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    req: ContractCreateRequest,
    service: ContractService = Depends(get_contract_service),
):
    contract = await service.update_contract(contract_id, req)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.post(
    "/{contract_id}/settlement-items",
    response_model=SettlementItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_settlement_item(
    contract_id: int,
    req: SettlementItemCreate,
    service: ContractService = Depends(get_contract_service),
):
    item = await service.add_settlement_item_to_contract(contract_id, req)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return item
