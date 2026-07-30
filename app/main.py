from fastapi import FastAPI
from app.profile.router import router as profile_router
from app.contract.router import router as contract_router

app = FastAPI(title="FX Meta Backend")
app.include_router(profile_router)
app.include_router(contract_router)

@app.get("/health")
async def health():
    return {"status": "ok"}