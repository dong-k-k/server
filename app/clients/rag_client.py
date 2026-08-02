import httpx
from app.core.config import settings


async def call_recommend(settlement, contract, net_exposure_krw, assessment, strategy_context) -> dict:
    payload = {
        "companyProfile": {"tradeDirection": contract.contract_type, "currencies": [settlement.currency],
                            "paymentTerms": [contract.payment_term]},
        "contracts": [{"tradeDirection": contract.contract_type, "foreignAmount": float(settlement.amount),
                        "currency": settlement.currency, "settlementDate": str(settlement.settlement_date),
                        "exposureKrw": net_exposure_krw}],
        "riskContext": {"breakEvenRate": float(settlement.bep_rate) if settlement.bep_rate else None,
                         "remainingBusinessDays": assessment.holding_days,
                         "expectedLossRate": float(assessment.es_pct) / 100,
                         "expectedShortfallKrw": float(assessment.expected_max_loss),
                         "riskLevel": assessment.risk_grade},
        "strategyContext": strategy_context,
        "options": {"maxCards": 3, "includeConditional": True},
    }
    async with httpx.AsyncClient(base_url=settings.rag_base_url, timeout=10) as client:
        resp = await client.post("/recommend", json=payload)
        if resp.status_code >= 400:
            # RAG가 준 422 detail을 그대로 로그에 남겨서 원인을 바로 보이게 함
            raise RuntimeError(f"RAG /recommend {resp.status_code} 응답: {resp.text}")
        return resp.json()