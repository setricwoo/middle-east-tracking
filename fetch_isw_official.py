#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从ISW官网提取3月29日报告的最新内容
"""
import asyncio
import re
import json
from html import unescape
from playwright.async_api import async_playwright

REPORT_URL = "https://understandingwar.org/research/middle-east/iran-update-special-report-march-29-2026/"

async def extract_official_content():
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
            
            # 获取页面标题
            title = await page.title()
            print(f"[标题] {title}")
            
            # 提取Key Takeaways
            print("\n[提取] Key Takeaways...")
            takeaways = await page.evaluate('''() => {
                const results = [];
                
                // 找到Key Takeaways部分
                let startEl = null;
                const headings = document.querySelectorAll('h2, h3, h4, strong, b, li');
                for (const h of headings) {
                    if (h.textContent.includes('Key Takeaways')) {
                        startEl = h;
                        break;
                    }
                }
                
                if (!startEl) return [];
                
                // 获取后续内容直到Toplines
                let current = startEl;
                while (current) {
                    current = current.nextElementSibling;
                    if (!current) break;
                    
                    // 检查是否是下一个章节
                    const text = current.textContent.trim();
                    if (text.includes('Toplines') || text.includes('US and Israeli') || 
                        text.includes('Iranian Response') || text.includes('Endnotes')) {
                        break;
                    }
                    
                    // 提取段落或列表项
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        const cleanText = text.replace(/\\s+/g, ' ').trim();
                        if (cleanText.length > 50) {
                            results.push(cleanText);
                        }
                    }
                }
                
                return results;
            }''')
            
            print(f"[找到] {len(takeaways)} 条Key Takeaways")
            for i, tk in enumerate(takeaways, 1):
                print(f"\n{i}. {tk[:200]}...")
            
            # 提取所有图表URL
            print("\n[提取] 图表...")
            chart_urls = await page.evaluate('''() => {
                const results = [];
                const imgs = document.querySelectorAll('img');
                
                for (const img of imgs) {
                    const src = img.src || img.getAttribute('data-src') || '';
                    // 只提取2026年3月的图表
                    if (src.includes('understandingwar.org/wp-content/uploads/2026/03/')) {
                        const filename = src.split('/').pop();
                        // 排除图标和小图片
                        if (filename.includes('Iranian') || filename.includes('Hezbollah') || 
                            filename.includes('Strikes') || filename.includes('Attacks')) {
                            results.push({
                                url: src,
                                alt: img.alt || '',
                                filename: filename
                            });
                        }
                    }
                }
                return results;
            }''')
            
            print(f"[找到] {len(chart_urls)} 张图表:")
            for i, c in enumerate(chart_urls, 1):
                print(f"  {i}. {c['filename']}")
            
            # 截图每张图表
            print("\n[截图] 开始截图图表...")
            screenshot_dir = "isw_screenshots"
            import os
            os.makedirs(screenshot_dir, exist_ok=True)
            
            chart_data = []
            for i, chart_info in enumerate(chart_urls, 1):
                try:
                    # 查找图片元素
                    img_selector = f'img[src="{chart_info["url"]}"]'
                    img = await page.query_selector(img_selector)
                    
                    if not img:
                        # 尝试模糊匹配
                        all_imgs = await page.query_selector_all('img')
                        for img_el in all_imgs:
                            src = await img_el.get_attribute('src') or ''
                            if chart_info['filename'] in src:
                                img = img_el
                                break
                    
                    if img:
                        # 滚动到图片
                        await img.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        
                        # 截图
                        filename = f"chart_20260329_{i:02d}.png"
                        filepath = f"{screenshot_dir}/{filename}"
                        await img.screenshot(path=filepath)
                        print(f"  [成功] {filename} - {chart_info['filename'][:50]}")
                        
                        chart_data.append({
                            'index': i,
                            'filename': filename,
                            'original_url': chart_info['url'],
                            'title_en': chart_info['alt'] or chart_info['filename']
                        })
                    else:
                        print(f"  [失败] 未找到图片: {chart_info['filename']}")
                        
                except Exception as e:
                    print(f"  [失败] {chart_info['filename']}: {e}")
            
            # 保存结果
            result = {
                'url': REPORT_URL,
                'title': title,
                'date': '2026-03-29',
                'takeaways_en': takeaways,
                'charts': chart_data
            }
            
            with open('isw_official_extract.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n[保存] 已保存到 isw_official_extract.json")
            print(f"[统计] {len(takeaways)} 条Key Takeaways, {len(chart_data)} 张图表")
            
            return result
                
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(extract_official_content())
