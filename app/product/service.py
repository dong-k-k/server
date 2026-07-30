# app/product/service.py
from typing import Any, Callable, Optional
from app.product.models import EligibilityRule, ProductMaster
from app.product.repository import ProductRepository
from app.product.rule_engine import (
    calculate_fit_score,
    evaluate_product,
)
from app.product.schemas import (
    EligibilityRuleCreate,
    ProductEvaluationResult,
    ProductMasterCreate,
)


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def create_product(self, payload: ProductMasterCreate) -> ProductMaster:
        """
        상품 마스터 및 자격 규칙 등록
        """
        product = ProductMaster(
            product_id=payload.product_id,
            name=payload.name,
            provider=payload.provider,
            direction=payload.direction,
            strategy_group=payload.strategy_group,
            cost_info=payload.cost_info,
            coverage_info=payload.coverage_info,
        )

        for rule_data in payload.rules:
            rule = EligibilityRule(
                field=rule_data.field,
                operator=rule_data.operator,
                value=rule_data.value,
            )
            product.rules.append(rule)

        return await self.repo.save(product)

    async def get_product(self, product_id: str) -> Optional[ProductMaster]:
        """
        상품 마스터 단건 조회
        """
        return await self.repo.find_by_id(product_id)

    async def evaluate_all_products(
        self,
        field_resolver: Callable[[str], Any],
        matches_risk_grade: bool = False,
        unknown_field_count: int = 0,
        is_low_cost: bool = False,
    ) -> list[ProductEvaluationResult]:
        """
        전체 상품에 대해 규칙 엔진 평가 수행 및 Fit Score 산출
        """
        products = await self.repo.find_all()
        results = []

        for product in products:
            verdict = evaluate_product(product, field_resolver)
            fit_score = calculate_fit_score(
                verdict=verdict,
                matches_risk_grade=matches_risk_grade,
                unknown_field_count=unknown_field_count,
                is_low_cost=is_low_cost,
            )
            results.append(
                ProductEvaluationResult(
                    product_id=product.product_id,
                    product_name=product.name,
                    verdict=verdict,
                    fit_score=fit_score,
                )
            )

        return results

from app.product.rule_engine import evaluate_product, calculate_fit_score

STRATEGY_GROUP_VISIBILITY = {
    "EXPORT": ["FX_HEDGING", "EXPORT_LEAD"],
    "IMPORT": ["FX_HEDGING", "IMPORT_LEAD"],
    "BOTH": ["FX_HEDGING", "EXPORT_LEAD", "IMPORT_LEAD"],  # + FX_MATCHING은 상계여부 확인 후 추가
}

class ProductMatchService:
    def __init__(self, product_repo, ai_client):
        self.product_repo = product_repo
        self.ai_client = ai_client

    async def match(self, settlement, contract, assessment, risk_profile) -> list[dict]:
        groups = STRATEGY_GROUP_VISIBILITY[contract.contract_type if contract.contract_type != "BOTH" else "BOTH"]
        if contract.contract_type == "BOTH" and getattr(contract, "netting_offset_amount", None):
            groups.append("FX_MATCHING")

        items = []
        for group in groups:
            candidates = await self.product_repo.find_by_strategy_group(group)
            for product in candidates:
                verdict = evaluate_product(product, lambda f: getattr(settlement, f, None))
                fit_score = calculate_fit_score(
                    verdict, matches_risk_grade=(assessment.risk_grade in ("HIGH",)),
                    unknown_field_count=0, is_low_cost=True,
                )
                reason = await self.ai_client.get_product_reason({
                    "productId": product.product_id, "verdict": verdict.value,
                })
                items.append({
                    "product_id": product.product_id, "strategy_group": group,
                    "verdict": verdict.value, "fit_score": fit_score,
                    "reason_text": reason["reasonText"],
                })
        return items