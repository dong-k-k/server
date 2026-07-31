from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.ai_service_client import get_ai_client
from app.contract.repository import ContractRepository
from app.core.db import get_db
from app.risk.repository import RiskRepository
from app.risk.schemas import RiskAssessmentResponse
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
