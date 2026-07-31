from sqlalchemy import BigInteger, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.db import Base

class FxRiskAssessment(Base):
    __tablename__ = "fx_risk_assessment"
    assessment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    settlement_id: Mapped[int] = mapped_column(ForeignKey("settlement_item.settlement_id"))
    net_exposure: Mapped[float] = mapped_column(Numeric(18, 2))
    holding_days: Mapped[int] = mapped_column(Integer)
    current_rate: Mapped[float] = mapped_column(Numeric(10, 2))
    contract_rate: Mapped[float] = mapped_column(Numeric(10, 2))
    valuation_pl: Mapped[float] = mapped_column(Numeric(18, 2))
    es_pct: Mapped[float] = mapped_column(Numeric(6, 3))
    expected_max_loss: Mapped[float] = mapped_column(Numeric(18, 2))
    bep_gap: Mapped[float | None] = mapped_column(Numeric(10, 2))
    bep_safety_margin_pct: Mapped[float | None] = mapped_column(Numeric(6, 3))
    risk_grade: Mapped[str] = mapped_column(String(10))
    recommended_action: Mapped[str] = mapped_column(String(30))
    data_confidence: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scenarios: Mapped[list["ScenarioResult"]] = relationship(back_populates="assessment")


class ScenarioResult(Base):
    __tablename__ = "scenario_result"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("fx_risk_assessment.assessment_id"))
    scenario_pct: Mapped[float] = mapped_column(Numeric(5, 2))
    projected_rate: Mapped[float] = mapped_column(Numeric(10, 2))
    export_pl_krw: Mapped[float] = mapped_column(Numeric(18, 2))
    import_pl_krw: Mapped[float] = mapped_column(Numeric(18, 2))
    remark: Mapped[str | None] = mapped_column(String(100))

    assessment: Mapped["FxRiskAssessment"] = relationship(back_populates="scenarios")