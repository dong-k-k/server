def hedge_pnl(net_exposure, current_rate, scenario_table, hedge_ratio_pct, product_cost_pct, direction):
    hedged = net_exposure * (hedge_ratio_pct / 100)
    unhedged = net_exposure - hedged
    cost = hedged * (product_cost_pct / 100) * current_rate

    results = []
    for s in scenario_table:
        rate_diff = (s["projectedRate"] - current_rate) if direction == "EXPORT" else (current_rate - s["projectedRate"])
        unhedged_pl = unhedged * rate_diff
        no_hedge_pl = net_exposure * rate_diff
        total_pl = unhedged_pl - cost  # 헤지 부분은 확정이라 0, 비용만 차감

        results.append({
            "scenarioPct": s["scenarioPct"], "totalPlKrw": round(total_pl),
            "noHedgePlKrw": round(no_hedge_pl),
            "hedgeEffectPct": round((1 - abs(total_pl) / abs(no_hedge_pl)) * 100, 1) if no_hedge_pl else 0,
        })
    return results

def avoided_loss_per_card(card: dict, scenarios: list[dict], current_rate: float, direction: str) -> list[dict]:
    """
    card: RAG가 준 카드(recommendedHedgeAmountKrw 포함)
    scenarios: fx-chronos 또는 폴백 analytics.py가 준 시나리오 테이블(환율값 리스트)
    반환: 시나리오별 '이 상품 안 썼을 때 대비 손실 회피액'
    """
    hedged_amount_krw = card.get("recommendedHedgeAmountKrw") or 0
    results = []
    for s in scenarios:
        rate_diff = (s["projectedRate"] - current_rate) if direction == "EXPORT" else (current_rate - s["projectedRate"])
        fully_unhedged_pl = 0  # 기준(변동없음) 대비 무헤지 시 손익 — rate_diff 자체가 이미 그 값
        # 헤지된 부분(hedged_amount_krw)은 환율 변동 무관하게 고정 → 그 금액만큼은 rate_diff 영향 안 받음
        hedge_ratio_of_krw = hedged_amount_krw  # 이미 원화 환산 헤지금액
        avoided_loss = hedge_ratio_of_krw * (rate_diff / current_rate)  # 헤지된 비율만큼 회피한 손익
        results.append({
            "scenarioPct": s["scenarioPct"],
            "noProductPlKrw": round(rate_diff * (hedged_amount_krw / current_rate + 0)),  # 상품 안 썼을 때 이 노출분 손익
            "avoidedLossKrw": round(avoided_loss),
        })
    return results

async def compute_avoided_loss_for_cards(
    cards: list[dict], current_rate: float, direction: str,
    settlement, hedge_analysis_client,
) -> list[dict]:
    """RAG 카드마다 '이 상품 안 썼을 때 대비 손실 회피액'을 계산해서 카드에 붙인다."""
    for card in cards:
        hedged_amount_krw = card.get("recommendedHedgeAmountKrw")
        if not hedged_amount_krw:
            card["avoidedLossScenarios"] = None
            continue

        try:
            result = await hedge_analysis_client.analyze(
                currency_pair=f"{settlement.currency}/KRW",
                side="receipt" if direction == "EXPORT" else "payment",
                foreign_amount=float(settlement.amount),
                settlement_date=str(settlement.settlement_date),
                reference_rate=current_rate,
                hedged_amount=hedged_amount_krw / current_rate,  # 원화→외화 환산
                hedge_rate=current_rate,  # 상품별 고정환율 없음 → 스팟환율로 근사
            )
        except (httpx.HTTPError, httpx.TimeoutException):
            # API 응답 없으면 폴백
            result = local_hedge_analysis_fallback(
                hedged_amount_krw, current_rate, settlement, direction,
            )

        card["avoidedLossScenarios"] = [
            {"scenarioPct": s["scenarioPct"], "avoidedLossKrw": s["hedge_effect_vs_unhedged_krw"]}
            for s in result["scenarios"]
        ]
    return cards