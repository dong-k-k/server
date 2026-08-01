from sqlalchemy import BigInteger, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.db import Base

class CompanyProfile(Base):
    __tablename__ = "company_profile"
    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    business_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    business_type: Mapped[str] = mapped_column(String(10))
    annual_export_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    annual_import_amount: Mapped[float | None] = mapped_column(Numeric(18, 2))
    annual_revenue: Mapped[float | None] = mapped_column(Numeric(18, 2))
    operating_profit: Mapped[float | None] = mapped_column(Numeric(18, 2))
    credit_grade: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    countries: Mapped[list["CounterpartCountry"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )

class CounterpartCountry(Base):
    __tablename__ = "counterpart_country"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("company_profile.profile_id"))
    country_code: Mapped[str] = mapped_column(String(5))

    profile: Mapped["CompanyProfile"] = relationship(back_populates="countries")