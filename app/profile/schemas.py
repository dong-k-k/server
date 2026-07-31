from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpsertRequest(BaseModel):
    business_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    business_type: str = Field(pattern="^(EXPORT|IMPORT|BOTH)$")
    annual_export_amount: Decimal | None = None
    annual_import_amount: Decimal | None = None
    annual_revenue: Decimal | None = None
    operating_profit: Decimal | None = None
    credit_grade: str | None = Field(default=None, max_length=10)
    counterpart_countries: list[str] = Field(default_factory=list)


class ProfileCreateRequest(ProfileUpsertRequest):
    pass


class ProfileResponse(ProfileUpsertRequest):
    profile_id: int

    model_config = ConfigDict(from_attributes=True)
