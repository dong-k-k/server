from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.profile.models import CompanyProfile, CounterpartCountry

class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, profile: CompanyProfile) -> CompanyProfile:
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def find_by_id(self, profile_id: int) -> CompanyProfile | None:
        result = await self.db.execute(
            select(CompanyProfile).where(CompanyProfile.profile_id == profile_id)
        )
        return result.scalar_one_or_none()