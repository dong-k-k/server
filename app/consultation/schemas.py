from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConsultationRequestProductResponse(BaseModel):
    id: int
    product_id: str

    model_config = ConfigDict(from_attributes=True)


class ConsultationRequestCreate(BaseModel):
    profile_id: int
    recommendation_id: int
    selected_product_ids: list[str]


class ConsultationRequestResponse(BaseModel):
    request_id: int
    profile_id: int
    recommendation_id: int
    status: str
    requested_at: datetime
    selected_products: list[ConsultationRequestProductResponse] = []

    model_config = ConfigDict(from_attributes=True)