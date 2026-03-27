#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test_fetch():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Try WTI crude oil
        url = 'https://tradingeconomics.com/commodity/cl1-com'
        print(f'Fetching {url}...')
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Get current price
            price = await page.evaluate("""() => {
                const el = document.querySelector('.table-commodity-price');
                return el ? el.textContent.trim() : null;
            }""")
            print(f'Price found: {price}')
            
            # Try to get chart data
            data = await page.evaluate("""() => {
                const scripts = document.querySelectorAll('script');
                for (let script of scripts) {
                    const text = script.textContent || '';
                    if (text.includes('series') && text.includes('data:')) {
                        return 'Found chart data in script';
                    }
                }
                return 'No chart data found';
            }""")
            print(f'Data: {data}')
            
            # Check page title
            title = await page.title()
            print(f'Page title: {title}')
            
        except Exception as e:
            print(f'Error: {e}')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_fetch())
