from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class CountryRisk(Base):
    __tablename__ = "country_risk"
    country_code: Mapped[str] = mapped_column(String(5), primary_key=True)
    country_name: Mapped[str] = mapped_column(String(50))
    risk_grade: Mapped[str] = mapped_column(String(10))  # LOW/MEDIUM/HIGH
    score: Mapped[int] = mapped_column(Integer)