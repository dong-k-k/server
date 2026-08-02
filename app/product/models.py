from sqlalchemy import String, JSON, ForeignKey, BigInteger, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

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