from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationRequestProductResponse(BaseModel):
    id: int
    product_id: str
    model_config = ConfigDict(from_attributes=True)


class ConsultationRequestCreate(BaseModel):
    profile_id: int
    recommendation_id: int
    selected_product_ids: list[str] = Field(default_factory=list)
    contact_name: str = Field(min_length=1, max_length=100)
    contact_phone: str = Field(min_length=1, max_length=20)
    contact_email: str = Field(min_length=3, max_length=100)
    consultation_method: str = Field(pattern="^(PHONE|EMAIL|BRANCH_VISIT)$")
    preferred_time: str | None = Field(default=None, max_length=100)
    preferred_branch: str | None = Field(default=None, max_length=100)
    memo: str | None = Field(default=None, max_length=1000)
    privacy_consent: bool
    policy_version: str = Field(min_length=1, max_length=30)


class ConsultationRequestResponse(BaseModel):
    request_id: int
    profile_id: int
    recommendation_id: int
    status: str
    contact_name: str
    contact_phone: str
    contact_email: str
    consultation_method: str
    preferred_time: str | None = None
    preferred_branch: str | None = None
    memo: str | None = None
    consented_at: datetime
    policy_version: str
    requested_at: datetime
    selected_products: list[ConsultationRequestProductResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class ConsultationStatusUpdate(BaseModel):
    status: str = Field(pattern="^(REQUESTED|MATCHING|ASSIGNED|COMPLETED|CANCELLED)$")
