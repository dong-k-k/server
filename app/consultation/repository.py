from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.consultation.models import ConsultationRequest


class ConsultationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self, consultation_request: ConsultationRequest
    ) -> ConsultationRequest:
        """
        상담 신청 및 선택된 상품 목록 DB 저장
        """
        self.db.add(consultation_request)
        await self.db.commit()
        await self.db.refresh(consultation_request)
        return consultation_request

    async def find_by_id(self, request_id: int) -> Optional[ConsultationRequest]:
        """
        상담 신청 ID 기반 단건 조회 (N+1 방지를 위한 selectinload 적용)
        """
        stmt = (
            select(ConsultationRequest)
            .options(selectinload(ConsultationRequest.selected_products))
            .where(ConsultationRequest.request_id == request_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update(self, consultation_request: ConsultationRequest) -> ConsultationRequest:
        await self.db.commit()
        await self.db.refresh(consultation_request)
        return consultation_request
