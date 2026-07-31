from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ConsultationRequest(Base):
    __tablename__ = "consultation_request"
    request_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("company_profile.profile_id"))
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("strategy_recommendation.recommendation_id"))
    status: Mapped[str] = mapped_column(String(15), default="REQUESTED")
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    selected_products: Mapped[list["ConsultationRequestProduct"]] = relationship(back_populates="request")


class ConsultationRequestProduct(Base):
    __tablename__ = "consultation_request_product"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("consultation_request.request_id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("product_master.product_id"))

    request: Mapped["ConsultationRequest"] = relationship(back_populates="selected_products")
