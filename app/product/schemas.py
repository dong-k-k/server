# app/product/schemas.py
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.product.rule_engine import Verdict


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