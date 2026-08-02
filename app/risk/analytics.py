import statistics
from datetime import date, timedelta


def business_days_between(start: date, end: date) -> int:
    days, d = 0, start
    while d < end:
        d += timedelta(days=1)
        if d.weekday() < 5:
            days += 1
    return days


def _daily_returns(series: list[dict]) -> list[float]:
    rates = [p["rate"] for p in series]
    return [(rates[i] - rates[i - 1]) / rates[i - 1] for i in range(1, len(rates))]


def historical_es(series: list[dict], holding_days: int, direction: str, confidence: float = 0.975) -> float:
    """direction: EXPORT(하락이 불리) / IMPORT(상승이 불리). 반환값은 % 단위."""
    returns = _daily_returns(series)
    holding_days = min(max(holding_days, 1), max(len(returns), 1))

    cum_returns = []
    for i in range(len(returns) - holding_days + 1):
        cum = 1.0
        for r in returns[i:i + holding_days]:
            cum *= (1 + r)
        cum_returns.append(cum - 1)
    if not cum_returns:
        return 0.0

    cum_returns.sort()
    tail_size = max(1, int(len(cum_returns) * (1 - confidence)))
    tail = cum_returns[:tail_size] if direction == "EXPORT" else cum_returns[-tail_size:]
    return round(abs(statistics.mean(tail)) * 100, 2)


def confidence_band_pct(series: list[dict]) -> float:
    returns = _daily_returns(series)
    if len(returns) < 2:
        return 0.0
    vol = statistics.pstdev(returns)
    return round(vol * 1.96 * 100, 2)  # 97.5% 근사 z-score


def scenario_table(current_rate: float, net_exposure: float, direction: str) -> list[dict]:
    table = []
    for pct in (-10, -5, 0, 5, 10):
        projected = round(current_rate * (1 + pct / 100), 2)
        diff = (projected - current_rate) * net_exposure
        export_pl = diff if direction == "EXPORT" else -diff
        table.append({
            "scenarioPct": pct, "projectedRate": projected,
            "exportPlKrw": round(export_pl), "importPlKrw": round(-export_pl),
        })
    return table