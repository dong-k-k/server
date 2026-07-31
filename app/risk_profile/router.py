from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.risk_profile.repository import RiskProfileRepository
from app.risk_profile.schemas import RiskProfileCreate, RiskProfileResponse
from app.risk_profile.service import RiskProfileService

router = APIRouter(prefix="/api/v1", tags=["risk-profiles"])


def get_risk_profile_service(db: AsyncSession = Depends(get_db)) -> RiskProfileService:
    return RiskProfileService(RiskProfileRepository(db))


@router.put("/settlement-items/{settlement_id}/risk-profile", response_model=RiskProfileResponse)
async def submit_risk_profile(
    settlement_id: int,
    payload: RiskProfileCreate,
    service: RiskProfileService = Depends(get_risk_profile_service),
):
    return await service.submit(settlement_id, payload.q1, payload.q2, payload.q3)


@router.get("/settlement-items/{settlement_id}/risk-profile", response_model=RiskProfileResponse)
async def get_risk_profile_by_settlement(settlement_id: int, db: AsyncSession = Depends(get_db)):
    profile = await RiskProfileRepository(db).find_by_settlement_id(settlement_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk profile not found")
    return profile


@router.get("/risk-profiles/{risk_profile_id}", response_model=RiskProfileResponse)
async def get_risk_profile(risk_profile_id: int, db: AsyncSession = Depends(get_db)):
    profile = await RiskProfileRepository(db).find_by_id(risk_profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk profile not found")
    return profile
