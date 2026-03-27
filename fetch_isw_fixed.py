#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版 ISW 战事更新抓取器
- 正确截取地图图片（使用完整viewport截图）
- 提取所有 Key Takeaways 并翻译
- 生成中文解读
"""

import asyncio
import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_data.json"
WAR_DATA_FILE = WORKDIR / "isw_war_data.json"
SCREENSHOT_DIR = WORKDIR / "isw_screenshots"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

ISW_INDEX_URL = "https://understandingwar.org/backgrounder/iran-updates"
MONTHS = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december",
}

# 翻译映射
TERM_MAPPING = {
    r'\bUS\b': '美国',
    r'\bUSA\b': '美国',
    r'\bUnited States\b': '美国',
    r'\bIran\b': '伊朗',
    r'\bIranian\b': '伊朗',
    r'\bIsrael\b': '以色列',
    r'\bIsraeli\b': '以色列',
    r'\bCENTCOM\b': '美国中央司令部',
    r'\bIRGC\b': '伊斯兰革命卫队',
    r'\bIRGC[- ]?GF\b': '伊斯兰革命卫队地面部队',
    r'\bHezbollah\b': '真主党',
    r'\bHamas\b': '哈马斯',
    r'\bHouthi\b': '胡塞武装',
    r'\bUAE\b': '阿联酋',
    r'\bSaudi Arabia\b': '沙特阿拉伯',
    r'\bKhamenei\b': '哈梅内伊',
    r'\bGhalibaf\b': '加利巴夫',
    r'\bIDF\b': '以色列国防军',
    r'\bTrump\b': '特朗普',
    r'\bNetanyahu\b': '内塔尼亚胡',
    r'\bwar\b': '战争',
    r'\bdrone\b': '无人机',
    r'\bmissile\b': '导弹',
    r'\bballistic missile\b': '弹道导弹',
    r'\bcruise missile\b': '巡航导弹',
    r'\bstrike\b': '打击',
    r'\battack\b': '攻击',
    r'\btarget\b': '目标',
    r'\blaunch\b': '发射',
    r'\bbase\b': '基地',
    r'\bmilitary\b': '军事',
    r'\bdefense\b': '国防',
    r'\bretaliatory\b': '报复性',
    r'\bnegotiation\b': '谈判',
    r'\bsanction\b': '制裁',
    r'\boil\b': '石油',
    r'\bGulf\b': '海湾',
    r'\bMiddle East\b': '中东',
    r'\bStrait of Hormuz\b': '霍尔木兹海峡',
    r'\bPersian Gulf\b': '波斯湾',
    r'\bIndian Ocean\b': '印度洋',
    r'\bDiego Garcia\b': '迭戈加西亚',
    r'\benrichment\b': '浓缩',
    r'\bstockpile\b': '库存',
    r'\bair defense\b': '防空',
    r'\bintelligence\b': '情报',
    r'\bsurveillance\b': '监视',
    r'\breconnaissance\b': '侦察',
}


def translate_text(text):
    """翻译英文到中文"""
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
                    result = _translate_single(current_chunk)
                    translated_parts.append(result)
                current_chunk = sent
            else:
                current_chunk += " " + sent if current_chunk else sent
        
        if current_chunk:
            result = _translate_single(current_chunk)
            translated_parts.append(result)
        
        return " ".join(translated_parts)
    
    return _translate_single(text)


def _translate_single(text):
    """单次翻译，先应用术语映射，再调用API"""
    # 先应用术语映射
    result = text
    for pattern, replacement in TERM_MAPPING.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 调用 MyMemory API
    for attempt in range(2):
        try:
            encoded = urllib.parse.quote(result[:500])
            url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh-CN"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method='GET')
            res = json.loads(urllib.request.urlopen(req, timeout=10).read())
            if res.get("responseStatus") == 200:
                translated = res["responseData"]["translatedText"]
                if "MYMEMORY WARNING" not in translated:
                    # 再次应用术语映射确保准确性
                    for pattern, replacement in TERM_MAPPING.items():
                        translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
                    return translated
        except Exception:
            if attempt < 1:
                time.sleep(1)
    
    return result


def clean_title(title):
    """清理标题翻译"""
    if not title:
        return title
    
    # 月份映射
    month_map = {
        'January': '1', 'February': '2', 'March': '3', 'April': '4',
        'May': '5', 'June': '6', 'July': '7', 'August': '8',
        'September': '9', 'October': '10', 'November': '11', 'December': '12'
    }
    
    result = title
    # 替换月份名称为数字
    for en_month, num in month_map.items():
        result = re.sub(r'\b' + en_month + r'\b', num + '月', result, flags=re.IGNORECASE)
    
    # 翻译其他术语
    result = re.sub(r'\bIran Update\b', '伊朗局势更新', result, flags=re.IGNORECASE)
    result = re.sub(r'\bSpecial Report\b', '特别报告', result, flags=re.IGNORECASE)
    result = re.sub(r'\bUpdate\b', '更新', result, flags=re.IGNORECASE)
    result = re.sub(r'\bReport\b', '报告', result, flags=re.IGNORECASE)
    
    # 格式化日期: "23, 2026" -> "2026年"
    result = re.sub(r'(\d{1,2}),\s*(\d{4})', r'\2年\1日', result)
    
    return result


def is_chart_image(img_info):
    """判断是否是图表图片"""
    url = img_info.get("url", "").lower()
    alt = img_info.get("alt", "").lower()
    
    chart_keywords = ['map', 'chart', 'graph', 'diagram', 'figure', 'overview', 'situation', 'assessment', 'strike', 'launch']
    exclude_patterns = ['headshot', 'avatar', 'author', 'profile', 'logo', 'icon', 'button', 'banner', 'babel', 'print']
    
    is_likely_chart = any(kw in url or kw in alt for kw in chart_keywords)
    should_exclude = any(pat in url or pat in alt for pat in exclude_patterns)
    
    return is_likely_chart and not should_exclude


def generate_chart_tags(chart_info):
    """生成图表标签/解读"""
    url = chart_info.get("url", "").lower()
    alt = chart_info.get("alt", "").lower()
    filename = url.split("/")[-1] if url else ""
    
    tags = []
    
    # 根据文件名和内容判断类型
    if "iranian" in filename or "iran" in alt:
        tags.append("伊朗军事行动")
    if "us" in filename or "israel" in filename or "combined" in filename:
        tags.append("美以联军行动")
    if "strike" in filename or "strike" in alt:
        tags.append("军事打击示意图")
    if "launch" in filename or "launch" in alt:
        tags.append("导弹发射轨迹")
    if "ground" in filename:
        tags.append("地面部队部署")
    if "diego" in filename or "garcia" in filename:
        tags.append("印度洋战区")
    if "ksa" in filename or "saudi" in filename:
        tags.append("沙特阿拉伯方向")
    if "bahrain" in filename:
        tags.append("巴林方向")
    if "uae" in filename:
        tags.append("阿联酋方向")
    if "hezbollah" in filename or "lebanon" in filename:
        tags.append("黎巴嫩/真主党")
    
    # 如果没有匹配到具体标签，使用通用标签
    if not tags:
        tags = ["战场态势图", "ISW战略分析"]
    
    return tags[:3]  # 最多3个标签


def get_chart_title(filename, alt):
    """根据文件名生成图表中文标题"""
    fn = filename.lower()
    alt_lower = alt.lower()
    
    # 根据文件名模式匹配
    if "diego garcia" in fn or "diego" in alt_lower:
        return "伊朗对迭戈加西亚基地导弹袭击示意图"
    if "us-and-israeli" in fn and "iran" in fn:
        return "美以联军在伊朗境内的军事打击"
    if "iranian-and-axis" in fn:
        return "伊朗及盟友报复性打击示意图"
    if "launch" in fn and "saudi" in fn:
        return "伊朗对沙特导弹/无人机发射情况"
    if "launch" in fn and "bahrain" in fn:
        return "伊朗对巴林导弹/无人机发射情况"
    if "launch" in fn and "uae" in fn:
        return "伊朗对阿联酋导弹/无人机发射情况"
    if "hezbollah" in fn:
        return "真主党对以色列袭击示意图"
    if "ground" in fn and "western" in fn:
        return "伊朗西部地面部队部署"
    if "ground" in fn and "southern" in fn:
        return "伊朗南部地面部队部署"
    if "ground" in fn and "northeastern" in fn:
        return "伊朗东北部地面部队部署"
    
    # 默认标题
    return "战场态势图"


async def capture_maps(page, images_info, article_date):
    """截取地图图片（改进版）"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    captured = []
    
    chart_images = [img for img in images_info if is_chart_image(img)]
    
    for idx, img_info in enumerate(chart_images):
        try:
            url = img_info["url"]
            
            # 在页面中查找图片
            img_element = await page.query_selector(f'img[src="{url}"]')
            if not img_element:
                # 尝试部分匹配
                img_element = await page.evaluate(f"""
                    () => {{
                        const imgs = document.querySelectorAll('img');
                        for (const img of imgs) {{
                            if (img.src && img.src.includes('{url.split('/')[-1][:30]}')) {{
                                return img;
                            }}
                        }}
                        return null;
                    }}
                """)
                if not img_element:
                    continue
            
            # 滚动到图片位置
            await img_element.scroll_into_view_if_needed()
            await asyncio.sleep(1)  # 等待图片加载
            
            # 获取图片的包围盒
            bbox = await img_element.bounding_box()
            if not bbox:
                continue
            
            # 截图文件名
            safe_name = f"chart_{article_date}_{idx:02d}.png"
            screenshot_path = SCREENSHOT_DIR / safe_name
            
            # 截取图片元素本身
            await img_element.screenshot(path=str(screenshot_path))
            
            # 验证截图是否有效（文件大小>10KB）
            if screenshot_path.exists() and screenshot_path.stat().st_size > 10000:
                filename = url.split("/")[-1]
                alt = img_info.get("alt", "")
                
                chart_data = {
                    "original_url": url,
                    "screenshot": str(screenshot_path.relative_to(WORKDIR)).replace("\\", "/"),
                    "filename": filename,
                    "alt": alt,
                    "title_zh": get_chart_title(filename, alt),
                    "tags": generate_chart_tags(img_info),
                }
                
                captured.append(chart_data)
                print(f"  [截图] {safe_name} - {chart_data['title_zh']}")
            else:
                # 截图太小，可能失败了
                print(f"  [警告] 截图可能无效: {safe_name}")
                
        except Exception as e:
            print(f"  [截图失败] {img_info.get('url', 'unknown')[:50]}...: {e}")
    
    return captured


async def extract_takeaways(page):
    """提取所有 Key Takeaways"""
    return await page.evaluate("""
        () => {
            const results = [];
            
            // 方法1: 找 Key Takeaways 标题后的列表
            const headings = Array.from(document.querySelectorAll('h2, h3, h4, strong, b'));
            for (const h of headings) {
                const text = h.textContent.trim();
                if (/key takeaway|key points|highlights/i.test(text)) {
                    // 找紧随其后的列表
                    let el = h.nextElementSibling;
                    while (el) {
                        if (el.tagName === 'OL' || el.tagName === 'UL') {
                            const items = Array.from(el.querySelectorAll('li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                            results.push(...items);
                            break;
                        }
                        // 检查是否是另一个标题
                        if (el.tagName.match(/^H[1-6]$/)) break;
                        el = el.nextElementSibling;
                    }
                    
                    // 如果没找到，检查父元素
                    if (results.length === 0) {
                        const parent = h.closest('div, section, article');
                        if (parent) {
                            const list = parent.querySelector('ol, ul');
                            if (list) {
                                const items = Array.from(list.querySelectorAll('li'))
                                    .map(li => li.textContent.trim())
                                    .filter(t => t.length > 10);
                                results.push(...items);
                            }
                        }
                    }
                    break;
                }
            }
            
            // 方法2: 找有序列表（通常是 takeaways）
            if (results.length === 0) {
                const ols = document.querySelectorAll('.entry-content ol, .post-content ol, article ol');
                for (const ol of ols) {
                    const items = Array.from(ol.querySelectorAll('li'))
                        .map(li => li.textContent.trim())
                        .filter(t => t.length > 20 && t.length < 1000);
                    if (items.length >= 2) {
                        results.push(...items);
                        break;
                    }
                }
            }
            
            return results.slice(0, 20);  // 最多20条
        }
    """)


async def find_latest_article(page):
    """查找最新文章URL"""
    now = datetime.now(BEIJING_TZ)
    
    # 尝试构造日期URL
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
                        return candidate
            except Exception:
                pass
        await asyncio.sleep(0.3)
    
    # 回退到索引页
    try:
        await page.goto(ISW_INDEX_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        
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
    except Exception:
        return None


async def fetch_isw():
    """主抓取函数"""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 1000},
            ignore_https_errors=True,
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = await context.new_page()
        
        # 查找最新文章
        print("[查找] 最新文章...")
        latest_url = await find_latest_article(page)
        if not latest_url:
            print("[错误] 未找到文章")
            await browser.close()
            return None
        
        print(f"[找到] {latest_url}")
        
        # 确保页面完全加载
        await page.goto(latest_url, wait_until="load", timeout=45000)
        await asyncio.sleep(3)
        
        # 提取标题
        title = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1.entry-title, h1.post-title, h1');
                if (h1) return h1.textContent.trim();
                const og = document.querySelector('meta[property=\"og:title\"]');
                if (og) return og.getAttribute('content').trim();
                return document.title.split('|')[0].trim();
            }
        """)
        
        # 提取日期
        date_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})', latest_url.lower())
        if date_match:
            month, day, year = date_match.groups()
            article_date = f"{year}-{month.capitalize()}-{int(day):02d}"
        else:
            article_date = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
        
        # 提取 Key Takeaways
        print("[提取] Key Takeaways...")
        takeaways_en = await extract_takeaways(page)
        print(f"[提取] {len(takeaways_en)} 条")
        
        # 翻译 Takeaways
        print("[翻译] Takeaways...")
        takeaways = []
        for i, text in enumerate(takeaways_en):
            zh = translate_text(text)
            takeaways.append({"en": text, "zh": zh})
            if i < len(takeaways_en) - 1:
                time.sleep(0.3)
        
        # 提取图片
        print("[提取] 图片...")
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
                    if (/headshot|avatar|author|profile|logo|babel|print/i.test(src)) return;
                    if (seen.has(src)) return;
                    seen.add(src);
                    result.push({{ url: src, alt: img.alt || '' }});
                }});
                return result;
            }}
        """)
        print(f"[提取] {len(images)} 张图片")
        
        # 截图地图
        print("[截图] 地图图表...")
        charts = await capture_maps(page, images, article_date)
        print(f"[截图] {len(charts)} 张")
        
        await browser.close()
        
        return {
            "url": latest_url,
            "title": title,
            "title_zh": clean_title(title),
            "date": article_date,
            "takeaways": takeaways,
            "charts": charts,
        }


def save_data(data):
    """保存数据到两个JSON文件"""
    now = datetime.now(BEIJING_TZ)
    
    # 1. 保存到 isw_data.json (完整数据)
    existing = {"updated": "", "articles": []}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            pass
    
    article_record = {
        **data,
        "fetched": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "takeaways_en": [t["en"] for t in data["takeaways"]],
        "takeaways_zh": [t["zh"] for t in data["takeaways"]],
        "all_images": [{"url": c["original_url"], "alt": c.get("alt", "")} for c in data["charts"]],
    }
    
    articles = [a for a in existing.get("articles", []) if a["url"] != data["url"]]
    articles.insert(0, article_record)
    existing["articles"] = articles[:30]
    existing["updated"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # 2. 保存到 isw_war_data.json (war-situation.html 使用的格式)
    war_data = {
        "updated": now.isoformat(),
        "source_url": data["url"],
        "current_report": {
            "url": data["url"],
            "title": data["title"],
            "title_zh": data["title_zh"],
            "date": data["date"],
            "takeaways": data["takeaways"],
            "charts": [
                {
                    "url": c["screenshot"],
                    "title": c.get("alt", ""),
                    "title_zh": c["title_zh"],
                    "context": c["tags"],
                }
                for c in data["charts"]
            ],
        },
        "history": [
            {
                "date": a.get("date", ""),
                "title": a.get("title", ""),
                "title_zh": clean_title(a.get("title", "")),
                "url": a.get("url", ""),
            }
            for a in articles[1:4]  # 最多3条历史
        ],
    }
    
    with open(WAR_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(war_data, f, ensure_ascii=False, indent=2)
    
    print(f"[保存] {DATA_FILE}")
    print(f"[保存] {WAR_DATA_FILE}")


async def main():
    print("=" * 70)
    print("ISW 战事更新抓取器 (修复版)")
    print("=" * 70)
    
    data = await fetch_isw()
    if data:
        save_data(data)
        print(f"\n[完成]")
        print(f"  标题: {data['title_zh']}")
        print(f"  日期: {data['date']}")
        print(f"  Takeaways: {len(data['takeaways'])} 条")
        print(f"  图表: {len(data['charts'])} 张")
    else:
        print("[失败]")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
