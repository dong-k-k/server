from sqlalchemy import BigInteger, String, Numeric, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from app.core.db import Base

class Contract(Base):
    __tablename__ = "contract"
    contract_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("company_profile.profile_id"))
    contract_type: Mapped[str] = mapped_column(String(10))  # EXPORT/IMPORT
    payment_term: Mapped[str] = mapped_column(String(5))    # TT/LC/DP/DA
    counterparty_country: Mapped[str] = mapped_column(String(5))  # 거래국가, 국가코드 (예: US)
    advance_settled_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    netting_offset_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    settlement_items: Mapped[list["SettlementItem"]] = relationship(
        back_populates="contract", cascade="all, delete-orphan"
    )


class SettlementItem(Base):
    __tablename__ = "settlement_item"
    settlement_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.contract_id"))
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(5))
    price_fix_date: Mapped[date] = mapped_column(Date)
    settlement_date: Mapped[date] = mapped_column(Date)
    is_payment_adjustable: Mapped[bool] = mapped_column(Boolean)
    bep_rate: Mapped[float | None] = mapped_column(Numeric(10, 2))

    contract: Mapped["Contract"] = relationship(back_populates="settlement_items")
