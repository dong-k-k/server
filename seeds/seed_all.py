import asyncio

from seeds.seed_country_risk import seed as seed_country_risk
from seeds.seed_products import seed as seed_products


async def main():
    print("Populating Product Master seed data...")
    await seed_products()
    print("Populating Country Risk seed data...")
    await seed_country_risk()
    print("All seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(main())