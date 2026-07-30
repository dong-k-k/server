from sqlalchemy import String, JSON, ForeignKey, BigInteger
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

    product: Mapped["ProductMaster"] = relationship(back_populates="rules")