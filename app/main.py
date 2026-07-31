from fastapi import FastAPI

from app.consultation.router import router as consultation_router
from app.contract.router import router as contract_router
from app.product.router import router as product_router
from app.profile.router import router as profile_router
from app.risk.router import router as risk_router
from app.risk_profile.router import router as risk_profile_router
from app.strategy.router import router as strategy_router

app = FastAPI(title="FX Mate Backend", version="0.1.0")

app.include_router(profile_router)
app.include_router(contract_router)
app.include_router(risk_router)
app.include_router(risk_profile_router)
app.include_router(product_router)
app.include_router(strategy_router)
app.include_router(consultation_router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
