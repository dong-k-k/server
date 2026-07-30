# app/risk_profile/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class RiskProfile(Base):
    __tablename__ = "risk_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    settlement_id = Column(Integer, index=True, nullable=False)
    
    # 문항별 점수 (0~2)
    q1_score = Column(Integer, nullable=False)
    q2_score = Column(Integer, nullable=False)
    q3_score = Column(Integer, nullable=False)
    
    # 산출 결과
    total_score = Column(Integer, nullable=False)
    profile_type = Column(String(50), nullable=False)
    target_hedge_ratio_min = Column(Integer, nullable=False)
    target_hedge_ratio_max = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)