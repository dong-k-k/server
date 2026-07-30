from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.profile.repository import ProfileRepository
from app.profile.service import ProfileService
from app.profile.schemas import ProfileCreateRequest, ProfileResponse

router = APIRouter(prefix="/api/v1/profiles", tags=["profile"])

# Service 의존성 주입 함수
def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    req: ProfileCreateRequest, 
    service: ProfileService = Depends(get_profile_service)
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
    service: ProfileService = Depends(get_profile_service)
):
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="프로필을 찾을 수 없습니다."
        )
    return ProfileResponse(
        profile_id=profile.profile_id,
        business_type=profile.business_type,
        counterpart_countries=[c.country_code for c in profile.countries],
    )