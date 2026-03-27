#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto('https://understandingwar.org/research/middle-east/iran-update-special-report-march-23-2026', wait_until='networkidle', timeout=60000)
        await asyncio.sleep(5)
        
        # Screenshot
        await page.screenshot(path='isw_page_check.png')
        print('Screenshot saved')
        
        # Try different selectors
        selectors = ['.entry-content', '.content', 'article', 'main', '.post-content', '#content']
        for sel in selectors:
            exists = await page.evaluate(f'() => document.querySelector("{sel}") !== null')
            print(f'{sel}: {exists}')
        
        await browser.close()

asyncio.run(debug())
