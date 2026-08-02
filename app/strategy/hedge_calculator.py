import asyncio
from datetime import date, timedelta

SIDE_BY_DIRECTION = {"EXPORT": "RECEIVABLE", "IMPORT": "PAYABLE"}

SCENARIO_LABEL_AI = {
    "point": "AI 예상 환율",
    "lower": "환율이 낮을 때",
    "median": "환율이 중간일 때",
    "upper": "환율이 높을 때",
}

def _fx_lookup_date(settlement_date: date) -> date:
    """fx-chronos는 평일 예측만 지원 -> 토요일이면 금요일, 일요일이면 월요일 값을 대신 조회."""
    if settlement_date.weekday() == 5:  # 토요일
        return settlement_date - timedelta(days=1)
    if settlement_date.weekday() == 6:  # 일요일
        return settlement_date + timedelta(days=1)
    return settlement_date

async def compute_avoided_loss_for_cards(
    cards: list[dict], current_rate: float, direction: str,
    settlement, ai_client,
) -> list[dict]:
    """RAG 카드마다 '이 상품 안 썼을 때 대비 손실 회피액'을 fx-chronos hedge-analysis로 계산해서 붙인다.
    결제일이 주말이면 가장 가까운 평일(토→금, 일→월) 예측값으로 대체해서 계산한다."""
    side = SIDE_BY_DIRECTION[direction]
    lookup_date = _fx_lookup_date(settlement.settlement_date)

    async def _fetch(card: dict) -> dict:
        hedged_amount_krw = card.get("recommendedHedgeAmountKrw")
        if not hedged_amount_krw:
            card["avoidedLossScenarios"] = None
            return card

        result = await ai_client.get_hedge_analysis(
            currency_pair=f"{settlement.currency}/KRW",
            side=side,
            foreign_amount=float(settlement.amount),
            settlement_date=str(lookup_date),
            reference_rate=current_rate,
            hedged_amount=hedged_amount_krw / current_rate,
            hedge_rate=current_rate,
        )
        if result is None:
            card["avoidedLossScenarios"] = None
        else:
            card["avoidedLossScenarios"] = [
                {"scenarioName": SCENARIO_LABEL_AI.get(s["scenario_name"], s["scenario_name"]),
                 "avoidedLossKrw": round(s["hedge_effect_vs_unhedged_krw"])}
                for s in result["scenarios"]
            ]
        return card

    return list(await asyncio.gather(*(_fetch(card) for card in cards)))