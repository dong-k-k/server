import httpx
from app.risk.models import FxRiskAssessment, ScenarioResult
from app.risk.repository import RiskRepository
from app.contract.repository import ContractRepository
from app.clients.ai_service_client import AIServiceClient
from app.risk import analytics


class RiskAssessmentService:
    def __init__(self, repo: RiskRepository, contract_repo: ContractRepository, ai_client: AIServiceClient):
        self.repo = repo
        self.contract_repo = contract_repo
        self.ai_client = ai_client

    async def assess(self, settlement_id: int) -> FxRiskAssessment:
        settlement = await self.contract_repo.find_settlement_by_id(settlement_id)
        if not settlement:
            return None
        contract = await self.contract_repo.find_by_id(settlement.contract_id)

        holding_days = analytics.business_days_between(settlement.price_fix_date, settlement.settlement_date)
        direction = "EXPORT" if contract.contract_type == "EXPORT" else "IMPORT"
        net_exposure = float(settlement.amount)

        result = await self._try_ai(settlement, direction, net_exposure, holding_days)
        if result is None:
            result = await self._fallback(settlement, direction, net_exposure, holding_days)

        assessment = FxRiskAssessment(settlement_id=settlement_id, **result["fields"])
        assessment.scenarios = [ScenarioResult(**s) for s in result["scenarios"]]
        saved = await self.repo.save(assessment)
        return await self.repo.find_by_id(saved.assessment_id)

    async def _try_ai(self, settlement, direction, net_exposure, holding_days):
        if settlement.currency != "USD" or holding_days > 20:
            return None  # AI 서비스 지원범위 밖 → 바로 폴백, 호출조차 안 함
        try:
            ai_result = await self.ai_client.get_risk_assessment({
                "amount": net_exposure, "currency": settlement.currency,
                "priceFixDate": str(settlement.price_fix_date), "settlementDate": str(settlement.settlement_date),
                "bepRate": float(settlement.bep_rate) if settlement.bep_rate else None,
                "direction": direction,
            })
        except (httpx.HTTPError, httpx.TimeoutException):
            return None  # AI 서비스 다운/타임아웃 → 폴백
        if not ai_result.get("supported", True):
            return None
        return {
            "fields": dict(
                net_exposure=ai_result["netExposure"], holding_days=ai_result["holdingDays"],
                current_rate=ai_result["currentRate"], contract_rate=ai_result["contractRate"],
                valuation_pl=(ai_result["currentRate"] - ai_result["contractRate"]) * ai_result["netExposure"],
                es_pct=ai_result["esPct"], expected_max_loss=ai_result["expectedMaxLoss"],
                bep_gap=ai_result.get("bepGap"), bep_safety_margin_pct=ai_result.get("bepSafetyMarginPct"),
                risk_grade=ai_result["riskGrade"], recommended_action=self._map_action(ai_result["riskGrade"]),
                data_confidence="HIGH",  # 실제 예측모델 기반
            ),
            "scenarios": [
                {"scenario_pct": s["scenarioPct"], "projected_rate": s["projectedRate"],
                 "export_pl_krw": s["exportPlKrw"], "import_pl_krw": s["importPlKrw"]}
                for s in ai_result["scenarioTable"]
            ],
        }

    async def _fallback(self, settlement, direction, net_exposure, holding_days):
        current = await self.ai_client.get_current_rate(settlement.currency)
        history = await self.ai_client.get_rate_history(settlement.currency, days=1095)
        current_rate = current["rate"]

        es_pct = analytics.historical_es(history["series"], holding_days, direction)
        expected_max_loss = round(net_exposure * current_rate * es_pct / 100)
        bep_gap = abs(current_rate - float(settlement.bep_rate)) if settlement.bep_rate else None
        bep_safety_margin_pct = round(bep_gap / current_rate * 100, 2) if bep_gap else None
        risk_grade = "LOW" if es_pct < 2 else "MEDIUM" if es_pct < 5 else "HIGH"

        return {
            "fields": dict(
                net_exposure=net_exposure, holding_days=holding_days,
                current_rate=current_rate,
                contract_rate=float(settlement.bep_rate) if settlement.bep_rate else current_rate,
                valuation_pl=(current_rate - (float(settlement.bep_rate) if settlement.bep_rate else current_rate)) * net_exposure,
                es_pct=es_pct, expected_max_loss=expected_max_loss,
                bep_gap=bep_gap, bep_safety_margin_pct=bep_safety_margin_pct,
                risk_grade=risk_grade, recommended_action=self._map_action(risk_grade),
                data_confidence="BASIC",  # 자체 통계 폴백이라는 걸 명시적으로 표시
            ),
            "scenarios": [
                {"scenario_pct": s["scenarioPct"], "projected_rate": s["projectedRate"],
                 "export_pl_krw": s["exportPlKrw"], "import_pl_krw": s["importPlKrw"]}
                for s in analytics.scenario_table(current_rate, net_exposure, direction)
            ],
        }

    @staticmethod
    def _map_action(risk_grade: str) -> str:
        return {"LOW": "TARGET_ORDER", "MEDIUM": "PARTIAL_HEDGE_MONITOR", "HIGH": "IMMEDIATE_HEDGE"}[risk_grade]