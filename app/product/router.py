# app/product/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.repository import ProductRepository
from app.product.schemas import ProductMasterCreate, ProductMasterResponse
from app.product.service import ProductService
from app.core.db import get_db
from app.clients.ai_service_client import get_ai_service__client
from app.product.models import ProductMatchItem, ProductMatchResult
from app.product.repository import ProductRepository
from app.product.schemas import ProductMatchRequest, ProductMatchResponse
from app.product.service import ProductMatchService

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