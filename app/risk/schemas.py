from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ScenarioResponse(BaseModel):
    scenario_pct: Decimal
    projected_rate: Decimal
    export_pl_krw: Decimal
    import_pl_krw: Decimal
    remark: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentResponse(BaseModel):
    assessment_id: int
    settlement_id: int
    net_exposure: Decimal
    holding_days: int
    current_rate: Decimal
    contract_rate: Decimal
    valuation_pl: Decimal
    es_pct: Decimal
    expected_max_loss: Decimal
    bep_gap: Decimal | None = None
    bep_safety_margin_pct: Decimal | None = None
    risk_grade: str
    recommended_action: str
    data_confidence: str
    created_at: datetime
    scenarios: list[ScenarioResponse] = []

    model_config = ConfigDict(from_attributes=True)
