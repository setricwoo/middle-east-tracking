#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整提取ISW报告所有Key Takeaways和图表
"""
import asyncio
import re
import json
from html import unescape
from playwright.async_api import async_playwright

REPORT_URL = "https://understandingwar.org/backgrounder/iran-update-special-report-march-29-2026"

async def extract_full_content():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            print(f"[访问] {REPORT_URL}")
            await page.goto(REPORT_URL, wait_until='networkidle', timeout=90000)
            await asyncio.sleep(5)
            
            # 保存HTML
            html = await page.content()
            with open('isw_report_full.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("[保存] HTML已保存")
            
            # 提取所有段落文本
            texts = await page.evaluate('''() => {
                const results = [];
                const elements = document.querySelectorAll('p, li');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text.length > 50 && text.length < 3000) {
                        results.push(text);
                    }
                }
                return results;
            }''')
            
            print(f"[提取] {len(texts)} 个段落")
            
            # 查找所有编号段落（可能是Key Takeaways）
            numbered = []
            for text in texts:
                # 匹配编号开头（1. 2. 等）
                if re.match(r'^\d+[\.\)]\s', text):
                    numbered.append(text)
            
            print(f"\n[找到] {len(numbered)} 条编号段落（可能的Key Takeaways）:")
            for i, t in enumerate(numbered[:15], 1):  # 显示前15条
                preview = t[:150].replace('\n', ' ')
                print(f"\n{i}. {preview}...")
            
            # 提取图表信息
            charts = await page.evaluate('''() => {
                const results = [];
                const imgs = document.querySelectorAll('img');
                for (const img of imgs) {
                    const src = img.src || '';
                    if (src.includes('understandingwar.org/wp-content/uploads/2026/03/') && 
                        (src.includes('NEW-') || src.includes('Hezbollah') || src.includes('Iranian'))) {
                        results.push({
                            src: src,
                            alt: img.alt || '',
                            title: img.title || ''
                        });
                    }
                }
                return results;
            }''')
            
            print(f"\n[图表] 找到 {len(charts)} 张相关图表:")
            for i, c in enumerate(charts, 1):
                print(f"{i}. {c['src'].split('/')[-1]}")
                
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(extract_full_content())
