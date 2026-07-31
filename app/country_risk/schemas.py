from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    country_code: str
    country_name: str
    risk_grade: str
    score: int

    model_config = ConfigDict(from_attributes=True)
