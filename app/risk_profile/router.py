# app/risk_profile/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.risk_profile.repository import RiskProfileRepository
from app.risk_profile.schemas import RiskProfileCreate, RiskProfileResponse
from app.risk_profile.service import RiskProfileService

router = APIRouter(tags=["Risk Profile"])


def get_risk_profile_service(db: AsyncSession = Depends(get_db)) -> RiskProfileService:
    repo = RiskProfileRepository(db)
    return RiskProfileService(repo)


@router.post(
    "/api/v1/settlement-items/{id}/risk-profile",
    response_model=RiskProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="위험성향 테스트 제출 및 결과 생성",
)
async def submit_risk_profile(
    id: int,  # settlement_id
    payload: RiskProfileCreate,
    service: RiskProfileService = Depends(get_risk_profile_service),
):
    return await service.submit(
        settlement_id=id,
        q1=payload.q1,
        q2=payload.q2,
        q3=payload.q3,
    )


@router.get(
    "/api/v1/risk-profiles/{id}",
    response_model=RiskProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="위험성향 테스트 결과 조회",
)
async def get_risk_profile(
    id: int,  # profile_id
    db: AsyncSession = Depends(get_db),
):
    repo = RiskProfileRepository(db)
    profile = await repo.find_by_id(id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk Profile with ID {id} not found",
        )

    return profile