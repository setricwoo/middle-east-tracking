#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 ISW 战事更新抓取器
功能：
1. 获取Key Takeaways并翻译
2. 使用Playwright截取所有重要图表
3. 翻译图表标题和关键图例
4. 摘录文章中对应描述图片的文字（总结图表含义）
"""

import asyncio
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_data.json"
SCREENSHOT_DIR = WORKDIR / "isw_screenshots"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

ISW_INDEX_URL = "https://understandingwar.org/backgrounder/iran-updates"
MONTHS = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december",
}
MONTHS_STR = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def load_existing():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"updated": "", "articles": []}


def save_data(data):
    data["updated"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {DATA_FILE.name} 已更新")


def parse_date_from_url(url):
    slug = url.rstrip("/").split("/")[-1]
    parts = slug.split("-")
    for i, p in enumerate(parts):
        if p in MONTHS_STR and i + 2 < len(parts):
            try:
                year = parts[i + 2]
                day = f"{int(parts[i + 1]):02d}"
                return f"{year}-{MONTHS_STR[p]}-{day}"
            except (ValueError, IndexError):
                pass
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")


def translate_text(text):
    """翻译英文到中文（使用MyMemory API）"""
    if not text or not text.strip():
        return text
    
    text = text.strip()
    max_len = 500
    
    if len(text) > max_len:
        sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        translated_parts = []
        current_chunk = ""
        
        for sent in sentences:
            if len(current_chunk) + len(sent) > max_len:
                if current_chunk:
                    result = _translate_single_mymemory(current_chunk)
                    translated_parts.append(result)
                current_chunk = sent
            else:
                current_chunk += " " + sent if current_chunk else sent
        
        if current_chunk:
            result = _translate_single_mymemory(current_chunk)
            translated_parts.append(result)
        
        return " ".join(translated_parts)
    
    return _translate_single_mymemory(text)


def _translate_single_mymemory(text):
    for attempt in range(2):
        try:
            encoded = urllib.parse.quote(text[:500])
            url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh-CN"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method='GET')
            res = json.loads(urllib.request.urlopen(req, timeout=10).read())
            if res.get("responseStatus") == 200:
                translated = res["responseData"]["translatedText"]
                if "MYMEMORY WARNING" not in translated:
                    return translated
        except Exception:
            if attempt < 1:
                time.sleep(1)
    return text


def is_chart_image(img_info):
    """判断图片是否是图表（基于URL、文件名、alt文本等）"""
    url = img_info.get("url", "").lower()
    alt = img_info.get("alt", "").lower()
    
    # 图表关键词
    chart_keywords = ['map', 'chart', 'graph', 'diagram', 'figure', 'overview', 'situation', 'assessment']
    
    # 排除的头像/标志类图片
    exclude_patterns = ['headshot', 'avatar', 'author', 'profile', 'logo', 'icon', 'button', 'banner']
    
    # 检查是否包含图表关键词
    is_likely_chart = any(kw in url or kw in alt for kw in chart_keywords)
    
    # 检查是否应排除
    should_exclude = any(pat in url or pat in alt for pat in exclude_patterns)
    
    return is_likely_chart and not should_exclude


async def extract_image_context(page, img_element):
    """提取图片在文章中的上下文描述"""
    context = await page.evaluate("""
        (img) => {
            // 获取图片周围的文本
            const results = [];
            
            // 1. 获取图片的alt文本
            if (img.alt) results.push({type: 'alt', text: img.alt});
            
            // 2. 获取图片标题/说明（通常在figcaption或紧跟在后面的em/small元素）
            let parent = img.parentElement;
            for (let i = 0; i < 3 && parent; i++) {
                // 检查figcaption
                const figcaption = parent.querySelector('figcaption');
                if (figcaption) {
                    results.push({type: 'caption', text: figcaption.textContent.trim()});
                }
                
                // 检查紧跟图片的说明文字
                const nextText = img.nextElementSibling;
                if (nextText && /^(em|small|span|div)$/i.test(nextText.tagName)) {
                    results.push({type: 'following', text: nextText.textContent.trim()});
                }
                
                parent = parent.parentElement;
            }
            
            // 3. 获取图片前面的段落文字（通常是描述）
            let prevEl = img.previousElementSibling;
            for (let i = 0; i < 2 && prevEl; i++) {
                if (/^(p|div)$/i.test(prevEl.tagName) && prevEl.textContent.length > 20) {
                    results.push({type: 'preceding', text: prevEl.textContent.trim().substring(0, 300)});
                    break;
                }
                prevEl = prevEl.previousElementSibling;
            }
            
            // 4. 如果没有找到说明，尝试从文章正文中找到引用该图片的段落
            if (results.length === 0) {
                const allParagraphs = document.querySelectorAll('p');
                for (const p of allParagraphs) {
                    const text = p.textContent.toLowerCase();
                    const imgSrc = img.src.toLowerCase();
                    const imgFile = imgSrc.split('/').pop().replace(/\.(webp|png|jpg|jpeg)$/, '');
                    
                    // 检查段落是否提到这张图片
                    if (imgFile && (text.includes(imgFile) || text.includes('figure') || text.includes('map'))) {
                        if (p.textContent.length > 30) {
                            results.push({type: 'referenced', text: p.textContent.trim().substring(0, 300)});
                            break;
                        }
                    }
                }
            }
            
            return results;
        }
    """, img_element)
    
    return context


async def capture_chart_screenshots(page, images_info, article_date):
    """截取图表图片"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    captured_charts = []
    
    for idx, img_info in enumerate(images_info):
        if not is_chart_image(img_info):
            continue
        
        try:
            # 获取图片元素
            img_element = await page.query_selector(f'img[src="{img_info["url"]}"]')
            if not img_element:
                continue
            
            # 提取图片上下文
            context = await extract_image_context(page, img_element)
            
            # 生成截图文件名
            safe_name = f"chart_{article_date}_{idx:02d}.png"
            screenshot_path = SCREENSHOT_DIR / safe_name
            
            # 截取图片元素
            await img_element.screenshot(path=str(screenshot_path))
            
            # 翻译alt文本和上下文
            alt_en = img_info.get("alt", "")
            alt_zh = translate_text(alt_en) if alt_en else ""
            
            # 翻译上下文描述
            context_zh = []
            for ctx in context:
                ctx_text = ctx.get("text", "")
                if ctx_text and len(ctx_text) > 10:
                    translated = translate_text(ctx_text[:300])
                    context_zh.append({
                        "type": ctx["type"],
                        "text_en": ctx_text,
                        "text_zh": translated
                    })
            
            # 生成图表含义总结
            description_summary = ""
            if context_zh:
                # 优先使用caption或referenced类型的描述
                best_desc = next((c for c in context_zh if c["type"] in ["caption", "referenced", "preceding"]), None)
                if best_desc:
                    description_summary = best_desc["text_zh"]
            
            chart_info = {
                "original_url": img_info["url"],
                "screenshot": str(screenshot_path.relative_to(WORKDIR)),
                "alt_en": alt_en,
                "alt_zh": alt_zh,
                "is_chart": True,
                "context": context_zh,
                "description_summary": description_summary or alt_zh or "战场态势图"
            }
            
            captured_charts.append(chart_info)
            print(f"  [截图] {safe_name} - {alt_zh[:50] if alt_zh else '无标题'}...")
            
        except Exception as e:
            print(f"  [截图失败] {img_info.get('url', 'unknown')[:60]}: {e}")
    
    return captured_charts


async def find_latest_url_by_date(page):
    now = datetime.now(BEIJING_TZ)
    for days_back in range(7):
        d = now - timedelta(days=days_back)
        month_name = MONTHS[d.month]
        url = f"https://understandingwar.org/backgrounder/iran-update-special-report-{month_name}-{d.day}-{d.year}"
        
        for candidate in [url, url + "/"]:
            try:
                resp = await page.goto(candidate, wait_until="domcontentloaded", timeout=15000)
                if resp and resp.status < 400:
                    length = await page.evaluate("document.body.innerText.length")
                    if length > 1000:
                        print(f"[日期URL] 找到文章: {candidate}")
                        return candidate
            except Exception:
                pass
        await asyncio.sleep(0.3)
    return None


async def find_latest_url_from_index(page):
    print(f"[访问] ISW 更新列表: {ISW_INDEX_URL}")
    for wait_mode in ("load", "domcontentloaded", "commit"):
        try:
            await page.goto(ISW_INDEX_URL, wait_until=wait_mode, timeout=30000)
            await asyncio.sleep(2)
            break
        except Exception as e:
            print(f"[警告] 列表页 wait_until={wait_mode} 失败: {type(e).__name__}")
    
    return await page.evaluate("""
        () => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            for (const a of links) {
                const href = a.href || '';
                if (/iran-update.*20\\d\\d/.test(href)) return href;
            }
            return null;
        }
    """)


async def extract_takeaways(page):
    return await page.evaluate("""
        () => {
            const headings = Array.from(document.querySelectorAll('h2,h3,h4,[class*="headline"],[class*="entry"]'));
            for (const h of headings) {
                if (/key takeaway/i.test(h.textContent)) {
                    let el = h.nextElementSibling;
                    while (el) {
                        if (el.tagName === 'OL' || el.tagName === 'UL') {
                            return Array.from(el.querySelectorAll('li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                        }
                        if (el.tagName === 'H2' || el.tagName === 'H3') break;
                        el = el.nextElementSibling;
                    }
                    const parent = h.closest('div,section,article');
                    if (parent) {
                        const list = parent.querySelector('ol,ul');
                        if (list) {
                            return Array.from(list.querySelectorAll('li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                        }
                    }
                }
            }
            const ol = document.querySelector('.entry-content ol, .post-content ol');
            if (ol) {
                return Array.from(ol.querySelectorAll('li'))
                    .map(li => li.textContent.trim())
                    .filter(t => t.length > 10)
                    .slice(0, 15);
            }
            return [];
        }
    """)


async def fetch_isw(data):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True,
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = await context.new_page()
        
        print("[策略] 优先尝试日期构造URL...")
        latest_url = await find_latest_url_by_date(page)
        if not latest_url:
            print("[策略] 回退到索引页搜索...")
            latest_url = await find_latest_url_from_index(page)
        
        if not latest_url:
            print("[错误] 未找到最新文章链接")
            await context.close()
            await browser.close()
            return False
        
        print(f"[找到] 最新文章: {latest_url}")
        
        current = page.url
        if not current.rstrip("/").endswith(latest_url.rstrip("/").split("/")[-1]):
            print("[访问] 文章页面...")
            for wait_mode in ("load", "domcontentloaded", "commit"):
                try:
                    await page.goto(latest_url, wait_until=wait_mode, timeout=45000)
                    await asyncio.sleep(4)
                    break
                except Exception as e:
                    print(f"[警告] wait_until={wait_mode} 失败: {type(e).__name__}")
        else:
            await asyncio.sleep(2)
        
        # 提取标题
        title = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1.entry-title, h1.post-title, h1');
                if (h1) return h1.textContent.trim();
                const og = document.querySelector('meta[property="og:title"]');
                if (og) return og.getAttribute('content').trim();
                return document.title.split('|')[0].trim();
            }
        """)
        
        # 提取 Key Takeaways
        takeaways_en = await extract_takeaways(page)
        print(f"[提取] Key Takeaways: {len(takeaways_en)} 条")
        
        # 提取所有图片
        year = str(datetime.now(BEIJING_TZ).year)
        images = await page.evaluate(f"""
            () => {{
                const imgs = Array.from(document.querySelectorAll('img'));
                const seen = new Set();
                const result = [];
                imgs.forEach(img => {{
                    const src = img.src || img.dataset.src || '';
                    if (!src.includes('wp-content/uploads')) return;
                    if (!src.includes('{year}')) return;
                    if (/headshot|avatar|author|profile|edit|logo/i.test(src)) return;
                    if (seen.has(src)) return;
                    seen.add(src);
                    result.push({{ url: src, alt: img.alt || '' }});
                }});
                return result;
            }}
        """)
        print(f"[提取] 图片: {len(images)} 张")
        
        # 截取图表并提取上下文
        article_date = parse_date_from_url(latest_url)
        print(f"[截图] 开始截取图表...")
        charts = await capture_chart_screenshots(page, images, article_date)
        print(f"[截图] 成功截取 {len(charts)} 张图表")
        
        await context.close()
        await browser.close()
    
    # 翻译 Key Takeaways
    takeaways_zh = []
    if takeaways_en:
        print(f"[翻译] 翻译 {len(takeaways_en)} 条 Key Takeaways...")
        for i, text in enumerate(takeaways_en):
            zh = translate_text(text)
            takeaways_zh.append(zh)
            if i < len(takeaways_en) - 1:
                time.sleep(0.5)
    
    article = {
        "url": latest_url,
        "title": title or latest_url,
        "date": article_date,
        "takeaways_en": takeaways_en,
        "takeaways_zh": takeaways_zh,
        "charts": charts,
        "all_images": images,
        "fetched": datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
    }
    
    print(f"[提取] 标题: {title}")
    print(f"[提取] 日期: {article_date}")
    print(f"[提取] 图表: {len(charts)} 张")
    
    # 更新数据
    articles = [a for a in data.get("articles", []) if a["url"] != latest_url]
    data["articles"] = [article] + articles
    data["articles"] = data["articles"][:30]
    data["latest_url"] = latest_url
    data["latest_title"] = title
    data["latest_date"] = article_date
    
    return True


async def main():
    print("=" * 70)
    print("ISW 战事更新抓取器 (增强版)")
    print("功能：Key Takeaways翻译 + 图表截图 + 上下文提取")
    print(f"时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    os.chdir(WORKDIR)
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    data = load_existing()
    
    ok = await fetch_isw(data)
    print(f"[ISW] {'成功' if ok else '失败'}")
    
    if ok:
        save_data(data)
        print(f"\n[截图保存位置] {SCREENSHOT_DIR}")
    
    print("=" * 70)
    print("完成!")


if __name__ == "__main__":
    asyncio.run(main())
