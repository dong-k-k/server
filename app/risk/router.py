from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.ai_service_client import get_ai_client
from app.contract.repository import ContractRepository
from app.core.db import get_db
from app.risk.repository import RiskRepository
from app.risk.schemas import RiskAssessmentResponse, RateHistoryResponse, RatePoint, RateForecastResponse
from app.risk.service import RiskAssessmentService

router = APIRouter(prefix="/api/v1", tags=["risk-assessments"])


def get_risk_service(db: AsyncSession = Depends(get_db)) -> RiskAssessmentService:
    return RiskAssessmentService(RiskRepository(db), ContractRepository(db), get_ai_client())


@router.post(
    "/settlement-items/{settlement_id}/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_risk_assessment(
    settlement_id: int,
    service: RiskAssessmentService = Depends(get_risk_service),
):
    assessment = await service.assess(settlement_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement item not found")
    return assessment


@router.get("/risk-assessments/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(assessment_id: int, db: AsyncSession = Depends(get_db)):
    assessment = await RiskRepository(db).find_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk assessment not found")
    return assessment


@router.get("/settlement-items/{settlement_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def get_latest_risk_assessment(settlement_id: int, db: AsyncSession = Depends(get_db)):
    assessment = await RiskRepository(db).find_by_settlement_id(settlement_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk assessment not found")
    return assessment

@router.get("/settlement-items/{settlement_id}/rate-history", response_model=RateHistoryResponse)
async def get_rate_history(
    settlement_id: int,
    days: int = 180,
    db: AsyncSession = Depends(get_db),
):
    settlement = await ContractRepository(db).find_settlement_by_id(settlement_id)
    if not settlement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement item not found")
    history = await get_ai_client().get_rate_history(settlement.currency, days=days)
    return RateHistoryResponse(
        settlement_id=settlement_id,
        currency=history["currency"],
        bep_rate=settlement.bep_rate,
        confidence_band_pct=history.get("confidenceBandPct"),
        source=history["source"],
        as_of=history["asOf"],
        series=[RatePoint(**p) for p in history["series"]],
    )

@router.get("/settlement-items/{settlement_id}/rate-forecast", response_model=RateForecastResponse)
async def get_rate_forecast(settlement_id: int, db: AsyncSession = Depends(get_db)):
    settlement = await ContractRepository(db).find_settlement_by_id(settlement_id)
    if not settlement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement item not found")
    if settlement.currency != "USD":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"현재 환율 예측은 USD만 지원합니다: {settlement.currency}",
        )
    forecast = await get_ai_client().get_fx_forecast()
    if forecast is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="환율 예측 서비스(fx-chronos)에서 응답을 받지 못했습니다",
        )
    return RateForecastResponse(settlement_id=settlement_id, **forecast)