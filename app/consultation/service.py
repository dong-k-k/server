from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from app.consultation.models import (
    ConsultationRequest,
    ConsultationRequestProduct,
)
from app.consultation.repository import ConsultationRepository
from app.consultation.schemas import ConsultationRequestCreate


class ConsultationService:
    def __init__(self, repo: ConsultationRepository):
        self.repo = repo

    async def create_request(
        self, payload: ConsultationRequestCreate
    ) -> ConsultationRequest:
        """
        상담 신청 및 선택 상품(selected_product_ids) 풀어서 엔티티 생성 후 저장
        """
        consultation_request = ConsultationRequest(
            profile_id=payload.profile_id,
            recommendation_id=payload.recommendation_id,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            contact_email=payload.contact_email,
            consultation_method=payload.consultation_method,
            preferred_time=payload.preferred_time,
            preferred_branch=payload.preferred_branch,
            memo=payload.memo,
            consented_at=datetime.utcnow(),
            policy_version=payload.policy_version,
        )

        if not payload.privacy_consent:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Privacy consent is required")

        for product_id in payload.selected_product_ids:
            request_product = ConsultationRequestProduct(product_id=product_id)
            consultation_request.selected_products.append(request_product)

        return await self.repo.save(consultation_request)

    async def get_request(self, request_id: int) -> Optional[ConsultationRequest]:
        """
        상담 신청 내역 단건 조회
        """
        return await self.repo.find_by_id(request_id)

    async def update_status(self, request_id: int, status_value: str) -> Optional[ConsultationRequest]:
        consultation_request = await self.repo.find_by_id(request_id)
        if not consultation_request:
            return None
        consultation_request.status = status_value
        return await self.repo.update(consultation_request)
