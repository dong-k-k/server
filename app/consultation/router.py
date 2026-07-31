from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.consultation.repository import ConsultationRepository
from app.consultation.schemas import (
    ConsultationRequestCreate,
    ConsultationRequestResponse,
    ConsultationStatusUpdate,
)
from app.consultation.service import ConsultationService

router = APIRouter(tags=["Consultation Request"])


def get_consultation_service(
    db: AsyncSession = Depends(get_db),
) -> ConsultationService:
    repo = ConsultationRepository(db)
    return ConsultationService(repo)


@router.post(
    "/api/v1/consultation-requests",
    response_model=ConsultationRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="상담 신청 등록",
)
async def create_consultation_request(
    payload: ConsultationRequestCreate,
    service: ConsultationService = Depends(get_consultation_service),
):
    return await service.create_request(payload)


@router.get(
    "/api/v1/consultation-requests/{id}",
    response_model=ConsultationRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="상담 신청 내역 조회",
)
async def get_consultation_request(
    id: int,  # request_id
    service: ConsultationService = Depends(get_consultation_service),
):
    consultation = await service.get_request(id)
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation request with ID {id} not found",
        )
    return consultation


@router.patch(
    "/api/v1/consultation-requests/{id}/status",
    response_model=ConsultationRequestResponse,
)
async def update_consultation_status(
    id: int,
    payload: ConsultationStatusUpdate,
    service: ConsultationService = Depends(get_consultation_service),
):
    consultation = await service.update_status(id, payload.status)
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation request not found")
    return consultation
