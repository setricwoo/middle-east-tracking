#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每12小时抓取 ISW 伊朗战事更新（understandingwar.org）
1. 先尝试按日期构造 URL（最可靠），回退到索引页搜索
2. 提取 Key Takeaways（英文列表）
3. 用 MyMemory API 翻译为中文
4. 提取战场地图图片（含 alt_zh 中文说明）
5. 保存到 isw_data.json
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

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_data.json"
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


def load_existing() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"updated": "", "articles": []}


def save_data(data: dict):
    data["updated"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {DATA_FILE.name} 已更新")


def parse_date_from_url(url: str) -> str:
    """从 URL 末段提取日期，如 iran-update-special-report-march-20-2026 → 2026-03-20"""
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


def translate_text(text: str) -> str:
    """用 MyMemory 免费 API 翻译英文到中文，失败静默返回原文"""
    if not text or not text.strip():
        return text
    try:
        encoded = urllib.parse.quote(text[:800])
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh-CN"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if res.get("responseStatus") == 200:
            translated = res["responseData"]["translatedText"]
            # MyMemory 在配额超限时会返回 MYMEMORY WARNING
            if "MYMEMORY WARNING" not in translated:
                return translated
    except Exception:
        pass
    return text


def translate_image_name(url: str) -> str:
    """将图片文件名转为可读说明，如 iran-map-2026-03-20.webp → iran map 2026 03 20"""
    name = url.rstrip("/").split("/")[-1]
    name = re.sub(r"\.(webp|png|jpg|jpeg)$", "", name, flags=re.I)
    name = name.replace("-", " ").replace("_", " ")
    return name.title()


async def find_latest_url_by_date(page) -> str | None:
    """优先按日期构造 URL 直接访问，最多往回找7天"""
    now = datetime.now(BEIJING_TZ)
    for days_back in range(7):
        d = now - timedelta(days=days_back)
        month_name = MONTHS[d.month]
        url = (
            f"https://understandingwar.org/backgrounder/"
            f"iran-update-special-report-{month_name}-{d.day}-{d.year}"
        )
        # 也试带斜线的版本
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
        # 短暂等待避免过快
        await asyncio.sleep(0.3)
    return None


async def find_latest_url_from_index(page) -> str | None:
    """回退：从索引页找最新文章"""
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


async def extract_takeaways(page) -> list[str]:
    """提取 Key Takeaways 有序列表"""
    return await page.evaluate("""
        () => {
            // 找 Key Takeaway(s) 标题
            const headings = Array.from(document.querySelectorAll('h2,h3,h4,[class*="headline"],[class*="entry"]'));
            for (const h of headings) {
                if (/key takeaway/i.test(h.textContent)) {
                    // 找兄弟节点中的 ol/ul
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
                    // 也尝试父容器的子列表
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
            // 回退：找第一个有内容的 ol
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


async def fetch_isw(data: dict) -> bool:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True,
        )
        await context.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )
        page = await context.new_page()

        # ── 1. 找最新文章 URL ──────────────────────────────
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

        # ── 2. 访问文章页面 ────────────────────────────────
        # 如果已在文章页（日期URL直接访问），不重复跳转
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

        # ── 3. 提取标题 ───────────────────────────────────
        title = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1.entry-title, h1.post-title, h1');
                if (h1) return h1.textContent.trim();
                const og = document.querySelector('meta[property="og:title"]');
                if (og) return og.getAttribute('content').trim();
                return document.title.split('|')[0].trim();
            }
        """)

        # ── 4. 提取 Key Takeaways ─────────────────────────
        takeaways_en = await extract_takeaways(page)
        print(f"[提取] Key Takeaways: {len(takeaways_en)} 条")
        if takeaways_en:
            print(f"  第1条: {takeaways_en[0][:80]}...")

        # ── 5. 提取战场地图图片 ───────────────────────────
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

        await context.close()
        await browser.close()

    # ── 6. 翻译 ──────────────────────────────────────────
    article_date = parse_date_from_url(latest_url)

    takeaways_zh = []
    if takeaways_en:
        print(f"[翻译] 翻译 {len(takeaways_en)} 条 Key Takeaways...")
        for i, text in enumerate(takeaways_en):
            zh = translate_text(text)
            takeaways_zh.append(zh)
            if i < len(takeaways_en) - 1:
                time.sleep(0.5)  # 避免触发速率限制

    # 翻译图片说明（使用文件名生成可读说明）
    for img in images:
        img_name = translate_image_name(img["url"])
        img["alt_zh"] = translate_text(img_name) if img_name else (img.get("alt", "") or "战场地图")

    article = {
        "url": latest_url,
        "title": title or latest_url,
        "date": article_date,
        "takeaways_en": takeaways_en,
        "takeaways_zh": takeaways_zh,
        "images": images,
        "fetched": datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    print(f"[提取] 标题: {title}")
    print(f"[提取] 日期: {article_date}")

    # 更新/插入文章（最新在前，保留最近 30 篇）
    articles = [a for a in data.get("articles", []) if a["url"] != latest_url]
    data["articles"] = [article] + articles
    data["articles"] = data["articles"][:30]
    data["latest_url"] = latest_url
    data["latest_title"] = title
    data["latest_date"] = article_date

    return True


async def main():
    print("=" * 60)
    print("ISW 战事更新抓取器")
    print(f"时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.chdir(WORKDIR)
    data = load_existing()

    ok = await fetch_isw(data)
    print(f"[ISW] {'成功' if ok else '失败'}")

    if ok:
        save_data(data)

    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    asyncio.run(main())
