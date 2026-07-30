from app.risk.repository import RiskRepository
from app.risk_profile.repository import RiskProfileRepository
from app.product.repository import ProductRepository

@router.post(
    "/api/v1/strategy-recommendations",
    response_model=StrategyRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="종합 전략 추천 생성",
)
async def create_strategy_recommendation(
    payload: StrategyRecommendationRequest,
    service: StrategyService = Depends(get_strategy_service),
    db: AsyncSession = Depends(get_db),
):
    assessment = await RiskRepository(db).find_by_settlement_id(payload.settlement_id)
    risk_profile = await RiskProfileRepository(db).find_by_id(payload.risk_profile_id)
    match_result = await ProductRepository(db).find_match_by_id(payload.match_id)

    if not (assessment and risk_profile and match_result):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "연관 데이터(진단/성향/매칭) 중 일부가 없습니다")

    return await service.recommend(
        settlement_id=payload.settlement_id,
        match_id=payload.match_id,
        risk_profile_id=payload.risk_profile_id,
        assessment=assessment,
        risk_profile=risk_profile,
        candidates=match_result.items,
    )