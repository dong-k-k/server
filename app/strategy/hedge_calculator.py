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