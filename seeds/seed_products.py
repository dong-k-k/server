import asyncio, json
from app.core.db import SessionLocal
from app.product.models import ProductMaster, EligibilityRule

async def seed():
    with open("seeds/products.json", encoding="utf-8") as f:
        data = json.load(f)
    async with SessionLocal() as db:
        for p in data:
            product = ProductMaster(
                product_id=p["product_id"], name=p["name"], provider=p["provider"],
                direction=p["direction"], strategy_group=p["strategy_group"],
            )
            product.rules = [EligibilityRule(field=r["field"], operator=r["operator"], value=r["value"]) for r in p["rules"]]
            db.add(product)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed())