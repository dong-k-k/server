import httpx
from app.core.config import settings

class AIServiceClient:
    def __init__(self):
        self.base_url = settings.ai_service_base_url
        self.mock_mode = settings.ai_service_mock_mode

    async def get_risk_assessment(self, payload: dict) -> dict:
        if self.mock_mode:
            return {
                "netExposure": 300000000, "holdingDays": 45, "currentRate": 1350.0,
                "contractRate": 1330.0, "esPct": 6.2, "expectedMaxLoss": 6750000,
                "bepGap": 15, "bepSafetyMarginPct": 1.1, "riskGrade": "HIGH",
                "scenarioTable": [
                    {"scenarioPct": -10, "projectedRate": 1215.0, "exportPlKrw": -13500000, "importPlKrw": 13500000, "remark": "심각한 역마진(수출)"},
                    {"scenarioPct": 0, "projectedRate": 1350.0, "exportPlKrw": 0, "importPlKrw": 0, "remark": "현재 기준"},
                ],
            }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10) as client:
            resp = await client.post("/internal/risk-assessment", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_product_reason(self, payload: dict) -> dict:
        if self.mock_mode:
            return {"reasonText": "(Mock) 대상통화·헤지기간 조건 충족"}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10) as client:
            resp = await client.post("/internal/product-reason", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_strategy_mix(self, payload: dict) -> dict:
        if self.mock_mode:
            return {
                "recommendationMix": [
                    {"strategyType": "FULL_COVER_INSURANCE", "productId": "KSURE-FX-001", "allocationRatio": 0.5},
                    {"strategyType": "FORWARD", "productId": "KB-FWD-001", "allocationRatio": 0.5},
                ],
                "recommendationReason": "(Mock) 리스크등급 HIGH, ES 6.2% 기준 혼합헤지 추천",
            }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10) as client:
            resp = await client.post("/internal/strategy-mix", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_current_rate(self, currency: str) -> dict:
        if self.mock_mode:
            return {"currency": currency, "rate": 1350.0}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10) as client:
            resp = await client.get("/internal/fx-rate/current", params={"currency": currency})
            resp.raise_for_status()
            return resp.json()

def get_ai_client() -> AIServiceClient:
    return AIServiceClient()