#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW 战事更新抓取器 V2
- 改进截图逻辑，正确捕获地图
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
MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 
             'july', 'august', 'september', 'october', 'november', 'december']

# 术语翻译映射
TERM_MAP = {
    'US': '美国', 'USA': '美国', 'United States': '美国',
    'Iran': '伊朗', 'Iranian': '伊朗',
    'Israel': '以色列', 'Israeli': '以色列',
    'CENTCOM': '美国中央司令部',
    'IRGC': '伊斯兰革命卫队',
    'IRGC Ground Force': '伊斯兰革命卫队地面部队',
    'Hezbollah': '真主党',
    'Hamas': '哈马斯',
    'Houthi': '胡塞武装',
    'UAE': '阿联酋',
    'Saudi Arabia': '沙特阿拉伯',
    'Khamenei': '哈梅内伊',
    'Ghalibaf': '加利巴夫',
    'IDF': '以色列国防军',
    'Trump': '特朗普',
    'Netanyahu': '内塔尼亚胡',
    'war': '战争',
    'drone': '无人机',
    'missile': '导弹',
    'ballistic missile': '弹道导弹',
    'cruise missile': '巡航导弹',
    'strike': '打击',
    'attack': '攻击',
    'target': '目标',
    'launch': '发射',
    'base': '基地',
    'military': '军事',
    'defense': '防御',
    'retaliatory': '报复性',
    'negotiation': '谈判',
    'sanction': '制裁',
    'oil': '石油',
    'Gulf': '海湾',
    'Middle East': '中东',
    'Strait of Hormuz': '霍尔木兹海峡',
    'Persian Gulf': '波斯湾',
    'Indian Ocean': '印度洋',
    'Diego Garcia': '迭戈加西亚',
    'enrichment': '浓缩',
    'stockpile': '库存',
    'air defense': '防空',
}


def apply_term_translation(text):
    """应用术语翻译"""
    if not text:
        return text
    result = text
    # 按长度降序排序，避免短词覆盖长词
    for en, zh in sorted(TERM_MAP.items(), key=lambda x: -len(x[0])):
        result = re.sub(r'\b' + re.escape(en) + r'\b', zh, result, flags=re.IGNORECASE)
    return result


def translate_text(text):
    """翻译英文到中文"""
    if not text or not text.strip():
        return text
    
    text = text.strip()
    
    # 先应用术语翻译
    text = apply_term_translation(text)
    
    # 短文本直接返回
    if len(text) < 100:
        return text
    
    # 长文本分段翻译
    max_len = 500
    if len(text) > max_len:
        sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        translated_parts = []
        current_chunk = ""
        
        for sent in sentences:
            if len(current_chunk) + len(sent) > max_len:
                if current_chunk:
                    result = _translate_api(current_chunk)
                    translated_parts.append(result)
                current_chunk = sent
            else:
                current_chunk += " " + sent if current_chunk else sent
        
        if current_chunk:
            result = _translate_api(current_chunk)
            translated_parts.append(result)
        
        result = " ".join(translated_parts)
    else:
        result = _translate_api(text)
    
    # 再次应用术语翻译确保准确性
    return apply_term_translation(result)


def _translate_api(text):
    """调用 MyMemory API 翻译"""
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


def clean_title(title):
    """清理标题"""
    if not title:
        return title
    
    # 替换月份
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    result = title
    for i, month in enumerate(months, 1):
        result = re.sub(r'\b' + month + r'\b', f'{i}月', result, flags=re.IGNORECASE)
    
    # 翻译其他
    result = re.sub(r'\bIran Update\b', '伊朗局势更新', result, flags=re.IGNORECASE)
    result = re.sub(r'\bSpecial Report\b', '特别报告', result, flags=re.IGNORECASE)
    result = re.sub(r'(\d{1,2}),?\s*(\d{4})', r'\2年\1日', result)
    
    return result


def parse_date(url):
    """从URL解析日期"""
    match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})', url.lower())
    if match:
        month_name, day, year = match.groups()
        month_num = MONTHS_EN.index(month_name) + 1
        return f"{year}-{month_num:02d}-{int(day):02d}"
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")


def get_chart_info(url, alt):
    """根据URL和alt生成图表信息"""
    fn = url.lower()
    alt_l = alt.lower()
    
    # 标题映射
    titles = {
        'diego garcia': ('伊朗对迭戈加西亚基地导弹袭击示意图', ['印度洋战区', '导弹袭击', '战略打击']),
        'us-and-israeli': ('美以联军在伊朗境内的军事打击', ['美以联军行动', '军事打击', '精确打击']),
        'iranian-and-axis': ('伊朗及盟友报复性打击示意图', ['伊朗军事行动', '报复性打击', '地区冲突']),
        'saudi': ('伊朗对沙特导弹/无人机发射情况', ['沙特阿拉伯方向', '导弹发射', '伊朗军事行动']),
        'bahrain': ('伊朗对巴林导弹/无人机发射情况', ['巴林方向', '导弹发射', '伊朗军事行动']),
        'uae': ('伊朗对阿联酋导弹/无人机发射情况', ['阿联酋方向', '导弹发射', '伊朗军事行动']),
        'kuwait': ('伊朗对科威特导弹发射情况', ['科威特方向', '导弹发射', '伊朗军事行动']),
        'hezbollah': ('真主党对以色列袭击示意图', ['黎巴嫩/真主党', '对以袭击', '地区冲突']),
        'ground force': ('伊朗地面部队部署图', ['地面部队', '军事部署', '战场态势']),
    }
    
    for key, (title, tags) in titles.items():
        if key in fn or key in alt_l:
            return {'title': title, 'tags': tags}
    
    # 默认
    return {'title': '战场态势图', 'tags': ['ISW战略分析', '战场态势']}


async def capture_all_maps(page, article_date):
    """截取所有地图（改进版 - 使用 viewport 截图）"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    captured = []
    
    # 获取所有图片元素及其位置
    images_data = await page.evaluate("""
        () => {
            const results = [];
            const imgs = document.querySelectorAll('img');
            const year = new Date().getFullYear().toString();
            
            imgs.forEach((img, idx) => {
                const src = img.src || '';
                if (!src.includes('wp-content/uploads')) return;
                if (!src.includes(year)) return;
                
                // 排除非地图图片
                const exclude = /headshot|avatar|author|profile|logo|babel|print|icon|button/i;
                if (exclude.test(src)) return;
                
                // 检查是否是地图（通过文件名或尺寸）
                const isMap = /map|chart|strike|launch|iran|israel|saudi|bahrain|uae|hezbollah/i.test(src);
                if (!isMap) return;
                
                const rect = img.getBoundingClientRect();
                if (rect.width < 300 || rect.height < 200) return;  // 太小的不是地图
                
                results.push({
                    index: idx,
                    src: src,
                    alt: img.alt || '',
                    width: rect.width,
                    height: rect.height,
                    top: rect.top + window.scrollY,
                    left: rect.left + window.scrollX,
                });
            });
            
            return results;
        }
    """)
    
    print(f"[发现] {len(images_data)} 张可能的地图")
    
    for idx, img_data in enumerate(images_data):
        try:
            # 滚动到图片位置并截取 viewport
            await page.evaluate(f"window.scrollTo(0, {img_data['top'] - 100})")
            await asyncio.sleep(1.5)  # 等待图片加载
            
            # 生成文件名
            safe_name = f"chart_{article_date}_{idx:02d}.png"
            screenshot_path = SCREENSHOT_DIR / safe_name
            
            # 截取 viewport（这样可以包含地图的完整上下文）
            await page.screenshot(path=str(screenshot_path), full_page=False)
            
            # 检查截图有效性
            if screenshot_path.exists() and screenshot_path.stat().st_size > 50000:
                info = get_chart_info(img_data['src'], img_data['alt'])
                
                captured.append({
                    'original_url': img_data['src'],
                    'screenshot': str(screenshot_path.relative_to(WORKDIR)).replace('\\', '/'),
                    'title_zh': info['title'],
                    'tags': info['tags'],
                })
                print(f"  [截图] {safe_name} - {info['title']}")
            else:
                screenshot_path.unlink(missing_ok=True)
                
        except Exception as e:
            print(f"  [失败] 截图 {idx}: {e}")
    
    return captured


async def extract_takeaways(page):
    """提取 Key Takeaways"""
    return await page.evaluate("""
        () => {
            const results = [];
            
            // 找 Key Takeaways 标题
            const headings = Array.from(document.querySelectorAll('h2, h3, h4, strong, b'));
            for (const h of headings) {
                if (/key takeaway|key points|highlights/i.test(h.textContent)) {
                    // 找后面的列表
                    let el = h.nextElementSibling;
                    while (el) {
                        if (el.tagName === 'OL' || el.tagName === 'UL') {
                            const items = Array.from(el.querySelectorAll('li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                            results.push(...items);
                            return results;
                        }
                        if (el.tagName.match(/^H[1-6]$/)) break;
                        el = el.nextElementSibling;
                    }
                    
                    // 检查父元素
                    const parent = h.closest('div, section, article');
                    if (parent) {
                        const list = parent.querySelector('ol, ul');
                        if (list) {
                            const items = Array.from(list.querySelectorAll('li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                            results.push(...items);
                            return results;
                        }
                    }
                }
            }
            
            // 回退：找第一个有序列表
            const ol = document.querySelector('.entry-content ol, .post-content ol, article ol');
            if (ol) {
                const items = Array.from(ol.querySelectorAll('li'))
                    .map(li => li.textContent.trim())
                    .filter(t => t.length > 20 && t.length < 1000);
                results.push(...items);
            }
            
            return results.slice(0, 15);
        }
    """)


async def find_article_url(page):
    """查找最新文章URL"""
    now = datetime.now(BEIJING_TZ)
    
    # 尝试日期构造
    for days_back in range(7):
        d = now - timedelta(days=days_back)
        month = MONTHS_EN[d.month - 1]
        url = f"https://understandingwar.org/backgrounder/iran-update-special-report-{month}-{d.day}-{d.year}"
        
        for candidate in [url, url + "/"]:
            try:
                resp = await page.goto(candidate, wait_until="domcontentloaded", timeout=15000)
                if resp and resp.status < 400:
                    length = await page.evaluate("document.body.innerText.length")
                    if length > 1000:
                        return candidate
            except:
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
                    if (/iran-update.*20\\d\\d/.test(a.href)) return a.href;
                }
                return null;
            }
        """)
    except:
        return None


async def fetch_isw():
    """主抓取函数"""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900},
            ignore_https_errors=True,
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = await context.new_page()
        
        # 查找文章
        print("[查找] 最新文章...")
        url = await find_article_url(page)
        if not url:
            print("[错误] 未找到文章")
            await browser.close()
            return None
        
        print(f"[找到] {url}")
        
        # 加载页面
        await page.goto(url, wait_until="load", timeout=45000)
        await asyncio.sleep(3)
        
        # 提取信息
        date = parse_date(url)
        
        title = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1.entry-title, h1.post-title, h1');
                return h1 ? h1.textContent.trim() : document.title.split('|')[0].trim();
            }
        """)
        
        print("[提取] Key Takeaways...")
        takeaways_en = await extract_takeaways(page)
        print(f"[提取] {len(takeaways_en)} 条")
        
        # 翻译
        print("[翻译] 内容...")
        takeaways = []
        for text in takeaways_en:
            zh = translate_text(text)
            takeaways.append({"en": text, "zh": zh})
            time.sleep(0.2)
        
        # 截图地图
        print("[截图] 地图...")
        charts = await capture_all_maps(page, date)
        print(f"[截图] {len(charts)} 张")
        
        await browser.close()
        
        return {
            "url": url,
            "title": title,
            "title_zh": clean_title(title),
            "date": date,
            "takeaways": takeaways,
            "charts": charts,
        }


def save(data):
    """保存数据"""
    now = datetime.now(BEIJING_TZ)
    
    # 保存完整数据
    existing = {"updated": "", "articles": []}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            pass
    
    record = {
        **data,
        "fetched": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "takeaways_en": [t["en"] for t in data["takeaways"]],
        "takeaways_zh": [t["zh"] for t in data["takeaways"]],
    }
    
    articles = [a for a in existing.get("articles", []) if a["url"] != data["url"]]
    articles.insert(0, record)
    existing["articles"] = articles[:30]
    existing["updated"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # 保存 war-situation 格式
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
                    "title": "",
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
            for a in articles[1:4]
        ],
    }
    
    with open(WAR_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(war_data, f, ensure_ascii=False, indent=2)
    
    print(f"[保存] {DATA_FILE}")
    print(f"[保存] {WAR_DATA_FILE}")


async def main():
    print("=" * 60)
    print("ISW 战事更新抓取器 V2")
    print("=" * 60)
    
    data = await fetch_isw()
    if data:
        save(data)
        print(f"\n[完成] {data['title_zh']}")
        print(f"  日期: {data['date']}")
        print(f"  Takeaways: {len(data['takeaways'])}")
        print(f"  图表: {len(data['charts'])}")
    else:
        print("[失败]")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
