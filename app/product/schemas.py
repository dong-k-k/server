from pydantic import BaseModel, ConfigDict


class ProductMatchItemResponse(BaseModel):
    id: int
    product_id: str
    product_name: str
    provider: str
    fit_score: int
    eligibility_status: str
    reason_text: str | None = None
    recommended_hedge_amount_krw: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductMatchRequest(BaseModel):
    settlement_id: int
    assessment_id: int
    risk_profile_id: int


class ProductMatchResponse(BaseModel):
    match_id: int
    settlement_id: int
    assessment_id: int
    risk_profile_id: int
    items: list[ProductMatchItemResponse] = []

    model_config = ConfigDict(from_attributes=True)