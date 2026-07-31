from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

env = Environment(loader=FileSystemLoader("app/strategy/templates"))

async def render_report_pdf(assessment, match_items, recommendation) -> bytes:
    template = env.get_template("report.html")
    html_content = template.render(
        assessment=assessment, match_items=match_items, recommendation=recommendation,
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = await page.pdf(format="A4", print_background=True)
        await browser.close()
    return pdf_bytes