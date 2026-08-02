import asyncio

SIDE_BY_DIRECTION = {"EXPORT": "RECEIVABLE", "IMPORT": "PAYABLE"}


async def compute_avoided_loss_for_cards(
    cards: list[dict], current_rate: float, direction: str,
    settlement, ai_client,
) -> list[dict]:
    """RAG 카드마다 '이 상품 안 썼을 때 대비 손실 회피액'을 fx-chronos hedge-analysis로 계산해서 붙인다."""
    side = SIDE_BY_DIRECTION[direction]

    async def _fetch(card: dict) -> dict:
        hedged_amount_krw = card.get("recommendedHedgeAmountKrw")
        if not hedged_amount_krw:
            card["avoidedLossScenarios"] = None
            return card
        result = await ai_client.get_hedge_analysis(
            currency_pair=f"{settlement.currency}/KRW",
            side=side,
            foreign_amount=float(settlement.amount),
            settlement_date=str(settlement.settlement_date),
            reference_rate=current_rate,
            hedged_amount=hedged_amount_krw / current_rate,
            hedge_rate=current_rate,
        )
        if result is None:
            card["avoidedLossScenarios"] = None
        else:
            card["avoidedLossScenarios"] = [
                {"scenarioName": s["scenario_name"], "avoidedLossKrw": round(s["hedge_effect_vs_unhedged_krw"])}
                for s in result["scenarios"]
            ]
        return card

    return list(await asyncio.gather(*(_fetch(card) for card in cards)))