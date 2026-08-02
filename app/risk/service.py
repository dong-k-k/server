from datetime import date
from app.risk.models import FxRiskAssessment, ScenarioResult
from app.risk.repository import RiskRepository
from app.contract.repository import ContractRepository
from app.clients.ai_service_client import AIServiceClient
from app.risk import analytics

AI_MAX_HORIZON_DAYS = 90
SIDE_BY_DIRECTION = {"EXPORT": "RECEIVABLE", "IMPORT": "PAYABLE"}


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

        holding_days = analytics.business_days_between(
            max(settlement.price_fix_date, date.today()), settlement.settlement_date
        )
        direction = "EXPORT" if contract.contract_type == "EXPORT" else "IMPORT"
        net_exposure = (
            float(settlement.amount) - float(contract.advance_settled_amount or 0)
            - float(contract.netting_offset_amount or 0)
        )

        result = await self._try_ai(settlement, direction, net_exposure, holding_days)
        if result is None:
            result = await self._fallback(settlement, direction, net_exposure, holding_days)

        assessment = FxRiskAssessment(settlement_id=settlement_id, **result["fields"])
        assessment.scenarios = [ScenarioResult(**s) for s in result["scenarios"]]
        saved = await self.repo.save(assessment)
        return await self.repo.find_by_id(saved.assessment_id)

    async def _try_ai(self, settlement, direction, net_exposure, holding_days):
        if settlement.currency != "USD":
            return None
        if (settlement.settlement_date - date.today()).days > AI_MAX_HORIZON_DAYS:
            return None

        current = await self.ai_client.get_current_rate(settlement.currency)
        ai_result = await self.ai_client.get_hedge_analysis(
            currency_pair=f"{settlement.currency}/KRW",
            side=SIDE_BY_DIRECTION[direction],
            foreign_amount=net_exposure,
            settlement_date=str(settlement.settlement_date),
            reference_rate=current["rate"],
            hedged_amount=0.0,
        )
        if ai_result is None:
            return None

        scenarios_by_name = {s["scenario_name"]: s for s in ai_result["scenarios"]}
        tail_scenario = scenarios_by_name.get("lower") if direction == "EXPORT" else scenarios_by_name.get("upper")
        if tail_scenario is None:
            return None

        reference_rate = current["rate"]
        es_pct = round(abs(tail_scenario["fx_rate"] - reference_rate) / reference_rate * 100, 2)
        expected_max_loss = round(abs(tail_scenario["favorable_pnl_vs_reference_krw"]))
        risk_grade = "LOW" if es_pct < 2 else "MEDIUM" if es_pct < 5 else "HIGH"
        bep_gap = abs(reference_rate - float(settlement.bep_rate)) if settlement.bep_rate else None
        bep_safety_margin_pct = round(bep_gap / reference_rate * 100, 2) if bep_gap else None

        scenarios = []
        for s in scenarios_by_name.values():
            pct = round((s["fx_rate"] / reference_rate - 1) * 100, 2)
            export_pl = s["favorable_pnl_vs_reference_krw"] if direction == "EXPORT" else -s["favorable_pnl_vs_reference_krw"]
            scenarios.append({
                "scenario_pct": pct, "projected_rate": s["fx_rate"],
                "export_pl_krw": round(export_pl), "import_pl_krw": round(-export_pl),
            })

        return {
            "fields": dict(
                net_exposure=net_exposure, holding_days=holding_days,
                current_rate=reference_rate,
                contract_rate=float(settlement.bep_rate) if settlement.bep_rate else reference_rate,
                valuation_pl=(reference_rate - (float(settlement.bep_rate) if settlement.bep_rate else reference_rate)) * net_exposure,
                es_pct=es_pct, expected_max_loss=expected_max_loss,
                bep_gap=bep_gap, bep_safety_margin_pct=bep_safety_margin_pct,
                risk_grade=risk_grade, recommended_action=self._map_action(risk_grade),
                data_confidence="HIGH",
            ),
            "scenarios": scenarios,
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
                data_confidence="BASIC",
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