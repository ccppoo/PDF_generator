from fastapi.templating import Jinja2Templates
from jinja2 import Template
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from datetime import datetime

import os
import pathlib

HTML_TEMPLATE = Jinja2Templates(directory="./templates")

HTML_for_PDF = "template_filled.html"

HTML_SAMPLE_TEMPLATE = "sample.html"


class Time:
    @staticmethod
    def get_year() -> int:
        return datetime.now().year

    @staticmethod
    def get_month() -> int:
        return datetime.now().month

    @staticmethod
    def get_month_day() -> int:
        return datetime.now().day


class Params(BaseModel):
    place: str = Field("103", description="place")
    year: int = Field(default_factory=Time.get_year)
    month: int = Field(default_factory=Time.get_month)
    day: int = Field(default_factory=Time.get_month_day)
    name: str = Field("John", description="user")
    user_department: str = Field("SW Univ", description="department")
    phone_number: str = Field("000-00000-0000", description="contact")
    email: str = Field("example@example.com", description="email")
    usage: str = Field("seminar", description="usage")
    participants: int = Field(10, description="participants")
    managed_by: str = Field("manager", description="managed_by")


def get_uri() -> str:
    curdir = os.path.curdir
    abspath = os.path.abspath(curdir)
    _uri = pathlib.Path(abspath, HTML_for_PDF).as_uri()

    # file://C:/Users/ ... /template_filled.html
    return _uri


def generate_html(params: Params):
    template: Template = HTML_TEMPLATE.get_template(HTML_SAMPLE_TEMPLATE)
    rendered_template = template.render(**params.model_dump())

    with open(HTML_for_PDF, mode="w", encoding="utf-8") as fp:
        fp.write(rendered_template)


async def generate_pdf(playwright, HTML_URI: str):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()

    await page.goto(HTML_URI)
    await page.emulate_media(media="print")
    await page.pdf(path="page.pdf", header_template="date", print_background=True)
    await browser.close()


async def main():
    params = Params()
    generate_html(params)
    html_URI = get_uri()
    async with async_playwright() as playwright:
        await generate_pdf(playwright, html_URI)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
