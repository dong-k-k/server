from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class StrategyRecommendationRequest(BaseModel):
    settlement_id: int
    match_id: int
    risk_profile_id: int


class StrategyRecommendationResponse(BaseModel):
    recommendation_id: int
    settlement_id: int
    match_id: int
    risk_profile_id: int
    recommendation_mix: list[dict[str, Any]]
    recommendation_reason: Optional[str] = None
    avoided_loss_by_product: Optional[list[dict[str, Any]]] = None
    pdf_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)