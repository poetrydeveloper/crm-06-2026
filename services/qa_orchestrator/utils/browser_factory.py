# services/qa_orchestrator/utils/browser_factory.py
import asyncio
from playwright.async_api import async_playwright, Browser, Page

class QAUIBrowserFactory:
    """🏗️ Архитектурный провайдер headless-браузера Chromium для BDD-тестов фронтенда"""
    _playwright = None
    _browser = None

    @classmethod
    async def get_page(cls) -> Page:
        if cls._playwright is None:
            cls._playwright = await async_playwright().start()
        if cls._browser is None:
            # Запуск в режиме headless внутри Docker-контейнера оркестратора
            cls._browser = await cls._playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            
        context = await cls._browser.new_context(viewport={"width": 1280, "height": 800})
        return await context.new_page()

    @classmethod
    async def close_all(cls):
        if cls._browser:
            await cls._browser.close()
        if cls._playwright:
            await cls._playwright.stop()
