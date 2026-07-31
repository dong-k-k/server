from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.profile.repository import ProfileRepository
from app.profile.schemas import ProfileCreateRequest, ProfileResponse
from app.profile.service import ProfileService

from app.product.repository import ProductRepository
from app.risk.repository import RiskRepository
from app.strategy.repository import StrategyRepository

router = APIRouter(prefix="/api/v1/profiles", tags=["profile"])

def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    req: ProfileCreateRequest,
    service: ProfileService = Depends(get_profile_service),
):
    profile = await service.create_profile(req)
    return ProfileResponse(
        profile_id=profile.profile_id,
        business_type=profile.business_type,
        counterpart_countries=[c.country_code for c in profile.countries],
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다.",
        )
    return ProfileResponse(
        profile_id=profile.profile_id,
        business_type=profile.business_type,
        counterpart_countries=[c.country_code for c in profile.countries],
    )

@router.get("/{profile_id}/summary")
async def get_summary(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    service: ProfileService = Depends(get_profile_service),
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다.",
        )

    # 각 도메인 repository 객체 생성
    risk_repo = RiskRepository(db)
    product_repo = ProductRepository(db)
    strategy_repo = StrategyRepository(db)

    # 최신 진단/매칭/추천 데이터 조합
    latest_assessment = await risk_repo.find_latest_by_profile(profile_id)
    latest_match = await product_repo.find_latest_match_by_profile(profile_id)
    latest_recommendation = await strategy_repo.find_latest_by_profile(profile_id)

    return {
        "profile": {
            "profileId": profile.profile_id,
            "businessType": profile.business_type,
        },
        "latestAssessment": latest_assessment,
        "latestMatch": latest_match,
        "latestRecommendation": latest_recommendation,
    }
