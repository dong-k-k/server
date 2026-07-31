from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.country_risk.models import CountryRisk
from app.country_risk.schemas import CountryResponse

router = APIRouter(prefix="/api/v1/countries", tags=["countries"])


@router.get("", response_model=list[CountryResponse])
async def list_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CountryRisk).order_by(CountryRisk.country_name))
    return list(result.scalars().all())
