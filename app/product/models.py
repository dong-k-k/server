from sqlalchemy import String, JSON, ForeignKey, BigInteger, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class ProductMaster(Base):
    __tablename__ = "product_master"
    product_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(20))       # KB/KSURE/GOVERNMENT
    direction: Mapped[str] = mapped_column(String(10))       # 수출/수입
    strategy_group: Mapped[str] = mapped_column(String(20))  # FX_HEDGING/EXPORT_LEAD/IMPORT_LEAD/FX_MATCHING
    cost_info: Mapped[str | None] = mapped_column(String(200))
    coverage_info: Mapped[str | None] = mapped_column(String(200))

    rules: Mapped[list["EligibilityRule"]] = relationship(back_populates="product")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rule"
    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("product_master.product_id"))
    field: Mapped[str] = mapped_column(String(50))
    operator: Mapped[str] = mapped_column(String(10))  # LTE/GTE/BETWEEN/IN
    value: Mapped[dict] = mapped_column(JSON)

class ProductMatchResult(Base):
    __tablename__ = "product_match_result"
    match_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    settlement_id: Mapped[int] = mapped_column(ForeignKey("settlement_item.settlement_id"))
    assessment_id: Mapped[int] = mapped_column(ForeignKey("fx_risk_assessment.assessment_id"))
    risk_profile_id: Mapped[int] = mapped_column(ForeignKey("risk_profiles.id"))
    items: Mapped[list["ProductMatchItem"]] = relationship(
        back_populates="match_result", cascade="all, delete-orphan"
    )


class ProductMatchItem(Base):
    __tablename__ = "product_match_item"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("product_match_result.match_id"))
    product_id: Mapped[str] = mapped_column(String(30))       # RAG productId 그대로 저장(FK 아님)
    product_name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50))
    fit_score: Mapped[int] = mapped_column()
    eligibility_status: Mapped[str] = mapped_column(String(20))   # RECOMMENDED/CONDITIONAL/RM_REVIEW_REQUIRED/NOT_RECOMMENDED
    reason_text: Mapped[str | None] = mapped_column(String(1000))
    recommended_hedge_amount_krw: Mapped[float | None] = mapped_column(Numeric(18, 2))
    match_result: Mapped["ProductMatchResult"] = relationship(back_populates="items")