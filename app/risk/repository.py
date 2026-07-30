# repository.py
from typing import Optional
from sqlalchemy.orm import Session
# from models import RiskAssessment  # 실제 정의한 DB Model 객체 import

class RiskAssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, risk_assessment) -> "RiskAssessment":
        """
        위험도 평가 엔티티를 DB에 저장 (또는 업데이트)
        """
        self.db.add(risk_assessment)
        self.db.commit()
        self.db.refresh(risk_assessment)
        return risk_assessment

    def find_by_id(self, assessment_id: str) -> Optional["RiskAssessment"]:
        """
        Risk Assessment ID로 단건 조회
        """
        return (
            self.db.query(RiskAssessment)
            .filter(RiskAssessment.id == assessment_id)
            .first()
        )