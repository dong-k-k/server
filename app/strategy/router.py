from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.ai_service_client import get_ai_client
from app.contract.repository import ContractRepository
from app.core.db import get_db
from app.product.repository import ProductRepository
from app.risk.repository import RiskRepository
from app.risk_profile.repository import RiskProfileRepository
from app.strategy.pdf_report import render_report_pdf
from app.strategy.repository import StrategyRepository
from app.strategy.schemas import StrategyRecommendationRequest, StrategyRecommendationResponse
from app.strategy.service import StrategyService

router = APIRouter(prefix="/api/v1/strategy-recommendations", tags=["strategy-recommendations"])


def get_strategy_service(db: AsyncSession = Depends(get_db)) -> StrategyService:
    return StrategyService(StrategyRepository(db), get_ai_client())


@router.post("", response_model=StrategyRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy_recommendation(
    payload: StrategyRecommendationRequest,
    service: StrategyService = Depends(get_strategy_service),
    db: AsyncSession = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    assessment = await RiskRepository(db).find_by_settlement_id(payload.settlement_id)
    risk_profile = await RiskProfileRepository(db).find_by_id(payload.risk_profile_id)
    match_result = await ProductRepository(db).find_match_result_by_id(payload.match_id)
    settlement = await contract_repo.find_settlement_by_id(payload.settlement_id)
    if not (assessment and risk_profile and match_result and settlement):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Required analysis data not found")
    contract = await contract_repo.find_by_id(settlement.contract_id)
    direction = "EXPORT" if contract.contract_type == "EXPORT" else "IMPORT"

    return await service.recommend(
        settlement_id=payload.settlement_id,
        match_id=payload.match_id,
        risk_profile_id=payload.risk_profile_id,
        assessment=assessment,
        risk_profile=risk_profile,
        candidates=match_result.items,
        settlement=settlement,
        direction=direction,
    )


@router.get("/{recommendation_id}", response_model=StrategyRecommendationResponse)
async def get_strategy_recommendation(recommendation_id: int, db: AsyncSession = Depends(get_db)):
    recommendation = await StrategyRepository(db).find_by_id(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return recommendation


@router.get("/{recommendation_id}/report")
async def download_report(recommendation_id: int, db: AsyncSession = Depends(get_db)):
    recommendation = await StrategyRepository(db).find_by_id(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    assessment = await RiskRepository(db).find_by_settlement_id(recommendation.settlement_id)
    match_result = await ProductRepository(db).find_match_result_by_id(recommendation.match_id)
    if not (assessment and match_result):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report data not found")
    pdf_bytes = await render_report_pdf(assessment, match_result.items, recommendation)
    return Response(content=pdf_bytes, media_type="application/pdf")