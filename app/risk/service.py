from app.risk.models import FxRiskAssessment, ScenarioResult
from app.risk.repository import RiskRepository
from app.contract.repository import ContractRepository
from app.clients.ai_service_client import AIServiceClient

class RiskAssessmentService:
    def __init__(self, repo: RiskRepository, contract_repo: ContractRepository, ai_client: AIServiceClient):
        self.repo = repo
        self.contract_repo = contract_repo
        self.ai_client = ai_client

    async def assess(self, settlement_id: int) -> FxRiskAssessment:
        settlement = await self.contract_repo.find_settlement_by_id(settlement_id)
        if not settlement:
            return None
        payload = {
            "amount": float(settlement.amount), "currency": settlement.currency,
            "priceFixDate": str(settlement.price_fix_date), "settlementDate": str(settlement.settlement_date),
            "bepRate": settlement.bep_rate,
        }
        ai_result = await self.ai_client.get_risk_assessment(payload)

        assessment = FxRiskAssessment(
            settlement_id=settlement_id,
            net_exposure=ai_result["netExposure"], holding_days=ai_result["holdingDays"],
            current_rate=ai_result["currentRate"], contract_rate=ai_result["contractRate"],
            valuation_pl=(ai_result["currentRate"] - ai_result["contractRate"]) * ai_result["netExposure"],
            es_pct=ai_result["esPct"], expected_max_loss=ai_result["expectedMaxLoss"],
            bep_gap=ai_result.get("bepGap"), bep_safety_margin_pct=ai_result.get("bepSafetyMarginPct"),
            risk_grade=ai_result["riskGrade"], recommended_action=self._map_action(ai_result["riskGrade"]),
            data_confidence="HIGH" if settlement.bep_rate else "BASIC",
        )
        assessment.scenarios = [
            ScenarioResult(
                scenario_pct=s["scenarioPct"], projected_rate=s["projectedRate"],
                export_pl_krw=s["exportPlKrw"], import_pl_krw=s["importPlKrw"], remark=s.get("remark"),
            ) for s in ai_result["scenarioTable"]
        ]
        return await self.repo.save(assessment)

    @staticmethod
    def _map_action(risk_grade: str) -> str:
        return {"LOW": "TARGET_ORDER", "MEDIUM": "PARTIAL_HEDGE_MONITOR", "HIGH": "IMMEDIATE_HEDGE"}[risk_grade]
