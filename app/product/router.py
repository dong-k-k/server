# app/product/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.repository import ProductRepository
from app.product.schemas import ProductMasterCreate, ProductMasterResponse, ProductMatchRequest, ProductMatchResponse
from app.product.service import ProductService, ProductMatchService
from app.core.db import get_db
from app.clients.ai_service_client import get_ai_client
from app.contract.repository import ContractRepository
from app.product.models import ProductMatchItem, ProductMatchResult
from app.risk.repository import RiskRepository
from app.risk_profile.repository import RiskProfileRepository

router = APIRouter(tags=["Admin Product Master"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    repo = ProductRepository(db)
    return ProductService(repo)


@router.post(
    "/api/v1/admin/products",
    response_model=ProductMasterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="상품 마스터 등록 (관리자)",
)
async def create_product(
    payload: ProductMasterCreate,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(payload)


@router.get(
    "/api/v1/admin/products/{id}",
    response_model=ProductMasterResponse,
    status_code=status.HTTP_200_OK,
    summary="상품 마스터 단건 조회 (관리자)",
)
async def get_product(
    id: str, # product_id
    service: ProductService = Depends(get_product_service),
):
    product = await service.get_product(id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id} not found",
        )
    return product


@router.get("/api/v1/products", response_model=list[ProductMasterResponse])
async def list_products(
    strategy_group: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await ProductRepository(db).find_all_by_strategy_group(strategy_group)


@router.post(
    "/api/v1/product-matches",
    response_model=ProductMatchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_match(
    payload: ProductMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    settlement = await contract_repo.find_settlement_by_id(payload.settlement_id)
    assessment = await RiskRepository(db).find_by_id(payload.assessment_id)
    risk_profile = await RiskProfileRepository(db).find_by_id(payload.risk_profile_id)
    if not (settlement and assessment and risk_profile):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Required matching data not found")

    contract = await contract_repo.find_by_id(settlement.contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    product_repo = ProductRepository(db)
    matcher = ProductMatchService(product_repo, get_ai_client())
    items = await matcher.match(settlement, contract, assessment, risk_profile)
    match = ProductMatchResult(
        settlement_id=payload.settlement_id,
        assessment_id=payload.assessment_id,
        risk_profile_id=payload.risk_profile_id,
        items=[ProductMatchItem(**item) for item in items],
    )
    return await product_repo.save_match_result(match)


@router.get("/api/v1/product-matches/{match_id}", response_model=ProductMatchResponse)
async def get_product_match(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await ProductRepository(db).find_match_result_by_id(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product match not found")
    return match
