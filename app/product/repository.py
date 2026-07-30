# app/product/schemas.py
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.product.rule_engine import Verdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.product.models import ProductMaster, ProductMatchResult

class EligibilityRuleCreate(BaseModel):
    field: str
    operator: str  # LTE, GTE, BETWEEN, IN
    value: dict[str, Any]


class EligibilityRuleResponse(BaseModel):
    rule_id: int
    product_id: str
    field: str
    operator: str
    value: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ProductMasterCreate(BaseModel):
    product_id: str
    name: str
    provider: str
    direction: str
    strategy_group: str
    cost_info: Optional[str] = None
    coverage_info: Optional[str] = None
    rules: list[EligibilityRuleCreate] = []


class ProductMasterResponse(BaseModel):
    product_id: str
    name: str
    provider: str
    direction: str
    strategy_group: str
    cost_info: Optional[str] = None
    coverage_info: Optional[str] = None
    rules: list[EligibilityRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProductEvaluationResult(BaseModel):
    product_id: str
    product_name: str
    verdict: Verdict
    fit_score: int

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_strategy_group(self, strategy_group: str) -> list[ProductMaster]:
        """
        전략 그룹별 상품 목록 조회 (자격 규칙 포함)
        """
        stmt = (
            select(ProductMaster)
            .options(selectinload(ProductMaster.rules))
            .where(ProductMaster.strategy_group == strategy_group)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save_match_result(self, match_result: ProductMatchResult) -> ProductMatchResult:
        """
        상품 매칭 결과 및 매칭 아이템 목록 DB 저장
        """
        self.db.add(match_result)
        await self.db.commit()
        await self.db.refresh(match_result)
        return match_result

    async def find_match_result_by_id(self, match_id: int) -> Optional[ProductMatchResult]:
        """
        매칭 결과 ID 기반 단건 조회 (N+1 방지 selectinload 적용)
        """
        stmt = (
            select(ProductMatchResult)
            .options(selectinload(ProductMatchResult.items))
            .where(ProductMatchResult.match_id == match_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()