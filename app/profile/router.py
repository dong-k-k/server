from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.product.repository import ProductRepository
from app.profile.repository import ProfileRepository
from app.profile.schemas import ProfileCreateRequest, ProfileResponse, ProfileUpsertRequest
from app.profile.service import ProfileService
from app.risk.repository import RiskRepository
from app.strategy.repository import StrategyRepository

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(ProfileRepository(db))


def to_response(profile) -> ProfileResponse:
    return ProfileResponse(
        profile_id=profile.profile_id,
        business_name=profile.business_name,
        email=profile.email,
        phone=profile.phone,
        business_type=profile.business_type,
        annual_export_amount=profile.annual_export_amount,
        annual_import_amount=profile.annual_import_amount,
        annual_revenue=profile.annual_revenue,
        operating_profit=profile.operating_profit,
        credit_grade=profile.credit_grade,
        counterpart_countries=[country.country_code for country in profile.countries],
    )


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(req: ProfileCreateRequest, service: ProfileService = Depends(get_profile_service)):
    return to_response(await service.create_profile(req))


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, service: ProfileService = Depends(get_profile_service)):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return to_response(profile)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int, req: ProfileUpsertRequest, service: ProfileService = Depends(get_profile_service)
):
    profile = await service.update_profile(profile_id, req)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return to_response(profile)


@router.get("/{profile_id}/summary")
async def get_summary(profile_id: int, db: AsyncSession = Depends(get_db), service: ProfileService = Depends(get_profile_service)):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {
        "profile": {"profileId": profile.profile_id, "businessType": profile.business_type},
        "latestAssessment": await RiskRepository(db).find_latest_by_profile(profile_id),
        "latestMatch": await ProductRepository(db).find_latest_match_by_profile(profile_id),
        "latestRecommendation": await StrategyRepository(db).find_latest_by_profile(profile_id),
    }
