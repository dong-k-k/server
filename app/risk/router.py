# router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 프로젝트 구조에 맞게 import 경로 조정
# from database import get_db
# from repository import RiskAssessmentRepository
# from schemas import RiskAssessmentCreate, RiskAssessmentResponse
# from models import RiskAssessment

router = APIRouter(tags=["Risk Assessment"])


@router.post(
    "/api/v1/settlement-items/{id}/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_risk_assessment(
    id: str, # 정산 아이템 ID (settlement_item_id)
    payload: RiskAssessmentCreate, # 평가에 필요한 추가 데이터가 있다면 활용
    db: Session = Depends(get_db),
):
    repo = RiskAssessmentRepository(db)

    # 1. (선택) 정산 아이템이 존재하는지 확인하거나 위험도 평가 로직 수행
    # risk_score, risk_level = evaluate_risk(id, payload)

    # 2. 엔티티 생성
    new_assessment = RiskAssessment(
        settlement_item_id=id,
        risk_score=payload.risk_score,
        status=payload.status,
    )

    # 3. Repository의 save() 호출
    saved_assessment = repo.save(new_assessment)
    return saved_assessment


@router.get(
    "/api/v1/risk-assessments/{id}",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_risk_assessment(
    id: str, # Risk Assessment ID
    db: Session = Depends(get_db),
):
    repo = RiskAssessmentRepository(db)

    # 1. Repository의 find_by_id() 호출
    assessment = repo.find_by_id(id)

    # 2. 데이터가 없을 경우 404 예외 처리
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk Assessment with ID {id} not found",
        )

    return assessment