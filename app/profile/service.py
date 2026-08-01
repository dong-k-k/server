from app.profile.models import CompanyProfile, CounterpartCountry
from app.profile.repository import ProfileRepository
from app.profile.schemas import ProfileCreateRequest, ProfileUpsertRequest

class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    async def create_profile(self, req: ProfileCreateRequest) -> CompanyProfile:
        profile = CompanyProfile(
            business_name=req.business_name, email=req.email, phone=req.phone,
            business_type=req.business_type,
            annual_export_amount=req.annual_export_amount,
            annual_import_amount=req.annual_import_amount,
            annual_revenue=req.annual_revenue,
            operating_profit=req.operating_profit,
            credit_grade=req.credit_grade,
        )
        profile.countries = [CounterpartCountry(country_code=c) for c in req.counterpart_countries]
        saved = await self.repo.save(profile)
        return await self.repo.find_by_id(saved.profile_id)

    async def get_profile(self, profile_id: int) -> CompanyProfile | None:
      return await self.repo.find_by_id(profile_id)
    
    async def update_profile(self, profile_id: int, req: ProfileUpsertRequest) -> CompanyProfile | None:
        profile = await self.repo.find_by_id(profile_id)
        if not profile:
            return None
        for field in (
            "business_name", "email", "phone", "business_type", "annual_export_amount",
            "annual_import_amount", "annual_revenue", "operating_profit", "credit_grade",
        ):
            setattr(profile, field, getattr(req, field))
        profile.countries = [CounterpartCountry(country_code=country) for country in req.counterpart_countries]
        return await self.repo.update(profile)
