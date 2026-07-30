from pydantic import BaseModel

class ProfileCreateRequest(BaseModel):
    business_name: str
    email: str | None = None
    phone: str | None = None
    business_type: str
    annual_export_amount: float | None = None
    annual_import_amount: float | None = None
    annual_revenue: float | None = None
    operating_profit: float | None = None
    credit_grade: str | None = None
    counterpart_countries: list[str] = []

class ProfileResponse(BaseModel):
    profile_id: int
    business_type: str
    counterpart_countries: list[str]