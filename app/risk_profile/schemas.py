# app/risk_profile/schemas.py
from datetime import datetime
from pydantic import BaseModel, Field


class RiskProfileCreate(BaseModel):
    # q3 배점 기준 확정 전이지만 검증 범위는 0~2로 설정
    q1: int = Field(..., ge=0, le=2, description="문항 1 점수 (0~2)")
    q2: int = Field(..., ge=0, le=2, description="문항 2 점수 (0~2)")
    q3: int = Field(..., ge=0, le=2, description="문항 3 점수 (0~2)")


class RiskProfileResponse(BaseModel):
    id: int
    settlement_id: int
    q1_score: int
    q2_score: int
    q3_score: int
    total_score: int
    profile_type: str
    target_hedge_ratio_min: int
    target_hedge_ratio_max: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (v1의 경우 orm_mode = True)