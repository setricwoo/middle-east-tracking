#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW 数据提取脚本（仅提取，不翻译）
提取内容：
1. Key Takeaways（英文原文）
2. 所有图表（地图、分析图等）
3. 正文内容（用于图表上下文）
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_raw_data.json"
SCREENSHOT_DIR = WORKDIR / "isw_screenshots"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

MONTHS = {
    1: 'january', 2: 'february', 3: 'march', 4: 'april',
    5: 'may', 6: 'june', 7: 'july', 8: 'august',
    9: 'september', 10: 'october', 11: 'november', 12: 'december'
}


def ensure_dirs():
    SCREENSHOT_DIR.mkdir(exist_ok=True)


def get_chrome_path():
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.environ.get('LOCALAPPDATA', '') + r"\Google\Chrome\Application\chrome.exe",
    ]
    for path in possible_paths:
        if path and Path(path).exists():
            return path
    return None


async def find_latest_report_url(page):
    now = datetime.now(BEIJING_TZ)
    
    for days_back in range(7):
        d = now - __import__('datetime').timedelta(days=days_back)
        month_name = MONTHS[d.month]
        
        url = f"https://understandingwar.org/backgrounder/iran-update-special-report-{month_name}-{d.day}-{d.year}"
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            if response and response.status == 200:
                title = await page.title()
                if "404" not in title and "Not Found" not in title:
                    print(f"[找到] 最新报告: {url}")
                    return url
        except:
            pass
        
        url2 = f"https://understandingwar.org/backgrounder/iran-update-{month_name}-{d.day}-{d.year}"
        try:
            response = await page.goto(url2, wait_until="domcontentloaded", timeout=15000)
            if response and response.status == 200:
                title = await page.title()
                if "404" not in title and "Not Found" not in title:
                    print(f"[找到] 最新报告: {url2}")
                    return url2
        except:
            pass
    
    return None


async def extract_takeaways(page):
    return await page.evaluate("""
        () => {
            const results = [];
            const selectors = [
                '.field--name-field-key-takeaways .field__item',
                '.key-takeaways li',
                '.entry-content ul li',
                'article ul li'
            ];
            
            for (const selector of selectors) {
                const items = document.querySelectorAll(selector);
                if (items.length > 0) {
                    for (const item of items) {
                        const text = item.textContent.trim();
                        if (text && text.length > 30) {
                            results.push(text);
                        }
                    }
                    if (results.length > 0) break;
                }
            }
            return results;
        }
    """)


async def extract_all_images(page):
    return await page.evaluate("""
        () => {
            const results = [];
            const seen = new Set();
            
            const allImages = document.querySelectorAll('img');
            
            for (const img of allImages) {
                const src = img.src || img.getAttribute('data-src') || '';
                if (!src) continue;
                
                if (!src.includes('wp-content/uploads')) continue;
                if (!src.match(/\\/202[56]\\//)) continue;
                
                const width = parseInt(img.getAttribute('width')) || 0;
                if (width > 0 && width < 200) continue;
                
                const lowerSrc = src.toLowerCase();
                if (lowerSrc.includes('icon') || 
                    lowerSrc.includes('logo') || 
                    lowerSrc.includes('babel') ||
                    lowerSrc.includes('avatar')) continue;
                
                let fullSrc = src;
                fullSrc = fullSrc.replace(/-\\d+x\\d+\\.(webp|png|jpg|jpeg)$/i, '.$1');
                
                if (seen.has(fullSrc)) continue;
                seen.add(fullSrc);
                
                let title = '';
                const alt = img.alt || '';
                if (alt && alt !== 'Map Thumbnail') {
                    title = alt;
                } else {
                    const match = fullSrc.match(/\\/([^\\/]+)\\.(webp|png|jpg|jpeg)$/i);
                    if (match) {
                        title = match[1].replace(/-/g, ' ').replace(/\\bFINAL\\b/i, '').trim();
                    }
                }
                
                results.push({
                    src: fullSrc,
                    alt: alt,
                    title: title || 'Map/Chart'
                });
            }
            
            return results;
        }
    """)


async def extract_body_text(page):
    return await page.evaluate("""
        () => {
            const results = [];
            const selectors = [
                '.entry-content p',
                'article p',
                '#printable-area p',
                '.dynamic-entry-content p'
            ];
            
            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text && text.length > 50) {
                        results.push(text);
                    }
                }
                if (results.length > 0) break;
            }
            return results;
        }
    """)


async def capture_image_screenshot(page, img_url, index, date_str):
    try:
        img_element = await page.query_selector(f'img[src="{img_url}"]')
        if not img_element:
            all_imgs = await page.query_selector_all('img')
            for img in all_imgs:
                src = await img.get_attribute('src') or ''
                if img_url.split('/')[-1] in src:
                    img_element = img
                    break
        
        if not img_element:
            return None
        
        safe_name = f"chart_{date_str}_{index:02d}.png"
        screenshot_path = SCREENSHOT_DIR / safe_name
        
        await img_element.screenshot(path=str(screenshot_path))
        
        return str(screenshot_path.relative_to(WORKDIR))
    except Exception as e:
        print(f"  [截图失败] {img_url[:60]}: {e}")
        return None


async def fetch_isw_extract():
    ensure_dirs()
    
    print("=" * 70)
    print("ISW 最新报告提取（仅提取，不翻译）")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=get_chrome_path()
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("\n[步骤1/4] 查找最新报告...")
        latest_url = await find_latest_report_url(page)
        
        if not latest_url:
            print("[错误] 未找到最新报告")
            await browser.close()
            return False
        
        print(f"[成功] 报告URL: {latest_url}")
        
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        title = await page.title()
        print(f"[标题] {title}")
        
        date_match = re.search(r'(\\d{4})-(\\d{2})-(\\d{2})', latest_url)
        if date_match:
            article_date = date_match.group(0)
        else:
            article_date = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
        print(f"[日期] {article_date}")
        
        print("\n[步骤2/4] 提取Key Takeaways...")
        takeaways = await extract_takeaways(page)
        print(f"[成功] 提取 {len(takeaways)} 条Key Takeaways")
        
        print("\n[步骤3/4] 提取所有图片...")
        images = await extract_all_images(page)
        print(f"[成功] 找到 {len(images)} 张图片")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {img['title']}")
        
        print("\n[步骤4/4] 提取正文内容...")
        body_text = await extract_body_text(page)
        print(f"[成功] 提取 {len(body_text)} 段正文")
        
        print("\n[截图] 开始截取图片...")
        captured_images = []
        for i, img_info in enumerate(images):
            print(f"  [{i+1}/{len(images)}] {img_info['title'][:50]}...")
            screenshot_path = await capture_image_screenshot(
                page, img_info['src'], i+1, article_date.replace('-', '')
            )
            if screenshot_path:
                captured_images.append({
                    **img_info,
                    'screenshot': screenshot_path
                })
        
        print(f"[截图] 成功截取 {len(captured_images)} 张图片")
        
        await browser.close()
        
        data = {
            "url": latest_url,
            "title": title,
            "date": article_date,
            "takeaways_en": takeaways,
            "body_text": body_text,
            "images": captured_images,
            "fetched": datetime.now(BEIJING_TZ).isoformat()
        }
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n[保存] 原始数据已保存: {DATA_FILE}")
        print("=" * 70)
        print("提取完成! 请查看 isw_raw_data.json 并进行人工翻译")
        print("=" * 70)
        
        return True


if __name__ == "__main__":
    asyncio.run(fetch_isw_extract())
