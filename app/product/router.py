# app/product/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.product.repository import ProductRepository
from app.product.schemas import ProductMatchRequest, ProductMatchResponse
from app.core.db import get_db
from app.contract.repository import ContractRepository
from app.product.models import ProductMatchItem, ProductMatchResult
from app.risk.repository import RiskRepository
from app.risk_profile.repository import RiskProfileRepository
from app.strategy.strategy_rules import build_strategy_context
from app.clients.rag_client import call_recommend

router = APIRouter(tags=["product-matches"])


@router.post("/api/v1/product-matches", response_model=ProductMatchResponse, status_code=status.HTTP_201_CREATED)
async def create_product_match(payload: ProductMatchRequest, db: AsyncSession = Depends(get_db)):
    contract_repo = ContractRepository(db)
    settlement = await contract_repo.find_settlement_by_id(payload.settlement_id)
    assessment = await RiskRepository(db).find_by_id(payload.assessment_id)
    risk_profile = await RiskProfileRepository(db).find_by_id(payload.risk_profile_id)
    if not (settlement and assessment and risk_profile):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Required matching data not found")
    contract = await contract_repo.find_by_id(settlement.contract_id)

    net_exposure_krw = (
        float(settlement.amount) - float(contract.advance_settled_amount or 0)
        - float(contract.netting_offset_amount or 0)
    ) * float(assessment.current_rate)

    strategy_context = build_strategy_context(
        assessment.risk_grade, risk_profile.profile_type,
        risk_profile.target_hedge_ratio_min, risk_profile.target_hedge_ratio_max,
    )
    rag_response = await call_recommend(settlement, contract, net_exposure_krw, assessment, strategy_context)

    product_repo = ProductRepository(db)
    match = ProductMatchResult(
        settlement_id=payload.settlement_id, assessment_id=payload.assessment_id,
        risk_profile_id=payload.risk_profile_id,
        items=[
            ProductMatchItem(
                product_id=c["productId"], product_name=c["productName"], provider=c["provider"],
                fit_score=c["fitScore"], eligibility_status=c["eligibilityStatus"],
                reason_text="; ".join(c["recommendationReasons"]),
                recommended_hedge_amount_krw=c.get("recommendedHedgeAmountKrw"),
            ) for c in rag_response["cards"]
        ],
    )
    saved = await product_repo.save_match_result(match)
    return await product_repo.find_match_result_by_id(saved.match_id)


@router.get("/api/v1/product-matches/{match_id}", response_model=ProductMatchResponse)
async def get_product_match(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await ProductRepository(db).find_match_result_by_id(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product match not found")
    return match