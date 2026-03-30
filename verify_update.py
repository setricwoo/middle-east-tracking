#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page.goto('http://127.0.0.1:8080/war-situation.html', wait_until='networkidle')
        await asyncio.sleep(2)
        await page.screenshot(path='debug_updated.png', full_page=True)
        print('[OK] 截图已保存到 debug_updated.png')
        await browser.close()

asyncio.run(verify())
