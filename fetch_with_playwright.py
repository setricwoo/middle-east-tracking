#!/usr/bin/env python3
"""使用Playwright获取Polymarket伊朗页面并提取市场数据"""
import json
import re
from playwright.sync_api import sync_playwright

url = "https://polymarket.com/zh/iran"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()
    
    # 拦截图片和字体以加速加载
    page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda route: route.abort())
    
    print("Loading page...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"Load error (continuing): {e}")
    
    # 获取页面HTML
    html = page.content()
    print(f"HTML length: {len(html)}")
    
    # 查找包含市场数据的JSON
    next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', html, re.DOTALL)
    if next_data_match:
        print("Found __NEXT_DATA__")
        try:
            data = json.loads(next_data_match.group(1))
            with open('next_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("Saved to next_data.json")
            
            # 尝试提取市场数据
            if 'props' in data and 'pageProps' in data['props']:
                print("Found pageProps!")
                page_props = data['props']['pageProps']
                print(f"Keys: {list(page_props.keys())[:10]}")
        except Exception as e:
            print(f"Parse error: {e}")
    else:
        print("No __NEXT_DATA__ found")
    
    # 保存完整HTML
    with open('iran_page_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved full HTML to iran_page_full.html")
    
    browser.close()

print("Done!")
