from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

env = Environment(loader=FileSystemLoader("app/strategy/templates"))

RISK_GRADE_LABELS = {"LOW": "낮음", "MEDIUM": "중간", "HIGH": "높음"}
ACTION_LABELS = {
    "TARGET_ORDER": "목표환율 알림 설정",
    "PARTIAL_HEDGE_MONITOR": "부분 헤지 및 환율 추이 모니터링",
    "IMMEDIATE_HEDGE": "즉시 헤지 실행 권장",
}
ELIGIBILITY_LABELS = {
    "RECOMMENDED": "추천",
    "CONDITIONAL": "조건부 추천",
    "RM_REVIEW_REQUIRED": "RM 확인 필요",
    "NOT_RECOMMENDED": "비추천",
}

async def render_report_pdf(assessment, match_items, recommendation) -> bytes:
    template = env.get_template("report.html")
    html_content = template.render(
        assessment=assessment,
        match_items=match_items,
        recommendation=recommendation,
        risk_grade_labels=RISK_GRADE_LABELS,
        action_labels=ACTION_LABELS,
        eligibility_labels=ELIGIBILITY_LABELS,
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = await page.pdf(format="A4", print_background=True)
        await browser.close()
    return pdf_bytes