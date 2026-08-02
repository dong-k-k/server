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
        resp.raise_for_status()
        return resp.json()