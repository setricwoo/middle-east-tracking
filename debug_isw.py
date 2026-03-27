#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://understandingwar.org/research/middle-east/iran-update-special-report-march-23-2026', timeout=60000)
        await asyncio.sleep(3)
        
        # Get page info
        title = await page.title()
        print(f'Title: {title}')
        
        # Check content area
        content_html = await page.evaluate('() => { const el = document.querySelector(".entry-content"); return el ? el.innerHTML.slice(0, 2000) : "No content found"; }')
        print(f'Content preview: {content_html[:1500]}...')
        
        await browser.close()

asyncio.run(debug())
