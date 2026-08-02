import random
from datetime import date, timedelta
from typing import Optional

import httpx
from app.core.config import settings


class AIServiceClient:
    def __init__(self):
        self.base_url = settings.ai_service_base_url
        self.mock_mode = settings.ai_service_mock_mode
        # HTTP 커넥션 재활용을 위해 단일 Client 관리 (timeout 10초)
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def close(self):
        """클라이언트 리소스 해제"""
        await self.client.aclose()

    async def get_hedge_analysis(
        self, currency_pair: str, side: str, foreign_amount: float,
        settlement_date: str, reference_rate: float,
        hedged_amount: float = 0.0, hedge_rate: float | None = None,
    ) -> dict | None:

        payload = {
            "currency_pair": currency_pair,
            "side": side,  # "payment" 또는 "receipt"
            "foreign_amount": foreign_amount,
            "settlement_date": settlement_date,
            "reference_rate": reference_rate,
            "hedged_amount": hedged_amount,
        }
        if hedged_amount > 0:
            payload["hedge_rate"] = hedge_rate

        try:
            resp = await self.client.post("/internal/hedge-analysis", json=payload)
        except (httpx.HTTPError, httpx.TimeoutException):
            return None
        if resp.status_code == 422:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_current_rate(self, currency: str) -> dict:
        if self.mock_mode:
            return {"currency": currency, "rate": 1350.0}

        search_date = date.today()
        rows = None

        # 주말/공휴일 대응: 최근 영업일을 찾을 때까지 최대 5일 전까지 거슬러 조회
        for _ in range(5):
            resp = await self.client.get(
                "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON",
                params={
                    "authkey": settings.exim_api_key,
                    "searchdate": search_date.strftime("%Y%m%d"),
                    "data": "AP01",
                },
            )
            resp.raise_for_status()
            candidate = resp.json()
            if candidate and candidate[0].get("result") == 1:
                rows = candidate
                break
            search_date -= timedelta(days=1)

        if rows is None:
            raise RuntimeError("최근 5일간 환율 데이터를 가져오지 못했습니다.")

        # JPY(100) 등 괄호가 포함된 통화코드 매칭 대응
        row = next((r for r in rows if r["cur_unit"].split("(")[0] == currency), None)
        if row is None:
            raise ValueError(f"지원하지 않는 통화코드: {currency}")

        rate = float(row["deal_bas_r"].replace(",", ""))
        if "(100)" in row["cur_unit"]:
            rate /= 100  # 100단위 고시 통화는 1단위로 환산

        return {
            "currency": currency,
            "rate": rate,
            "asOf": str(search_date),
            "source": "한국수출입은행",
        }

    async def get_rate_history(self, currency: str, days: int = 180) -> dict:
        if currency != "USD":
            raise ValueError(f"ECOS 실계열은 현재 USD만 지원: {currency}")

        end = date.today()
        start = end - timedelta(days=int(days * 1.6))  # 주말/공휴일 감안 여유분

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://ecos.bok.or.kr/api/StatisticSearch/{settings.ecos_api_key}"
                f"/json/kr/1/{days + 50}/731Y001/D/{start.strftime('%Y%m%d')}/{end.strftime('%Y%m%d')}/0000001"
            )
            resp.raise_for_status()
            payload = resp.json()

        if "StatisticSearch" not in payload:
            raise RuntimeError(f"ECOS 응답 오류: {payload}")

        rows = payload["StatisticSearch"]["row"]
        series = [
            {"date": f"{r['TIME'][:4]}-{r['TIME'][4:6]}-{r['TIME'][6:]}", "rate": float(r["DATA_VALUE"])}
            for r in rows
        ][-days:]

        return {
            "currency": currency, "series": series, "confidenceBandPct": None,
            "source": "한국은행 ECOS(731Y001)", "asOf": series[-1]["date"] if series else str(end),
        }


# 싱글톤 패턴 또는 의존성 주입용 팩토리 함수
_ai_client_instance: Optional[AIServiceClient] = None


def get_ai_client() -> AIServiceClient:
    global _ai_client_instance
    if _ai_client_instance is None:
        _ai_client_instance = AIServiceClient()
    return _ai_client_instance