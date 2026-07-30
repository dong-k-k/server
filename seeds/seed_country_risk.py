import asyncio
import json

from app.core.db import SessionLocal
from app.country_risk.models import CountryRisk


async def seed():
    with open("seeds/country_risk.json", encoding="utf-8") as f:
        data = json.load(f)

    async with SessionLocal() as db:
        for item in data:
            country_risk = CountryRisk(
                country_code=item["country_code"],
                country_name=item["country_name"],
                risk_grade=item["risk_grade"],
                score=item["score"],
            )
            db.add(country_risk)
        await db.commit()
        print("Country Risk seed data populated successfully.")


if __name__ == "__main__":
    asyncio.run(seed())