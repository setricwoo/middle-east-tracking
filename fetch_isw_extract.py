#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW 数据提取脚本（仅提取原文，不翻译）
提取内容：
1. Key Takeaways（英文原文）
2. 所有图表（地图、分析图等）
3. 每段正文内容（用于图表上下文）
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
DATA_FILE = WORKDIR / "isw_data_raw.json"  # 原始英文数据
SCREENSHOT_DIR = WORKDIR / "isw_screenshots"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

ISW_INDEX_URL = "https://understandingwar.org/backgrounder/iran-updates"


def ensure_dirs():
    """确保目录存在"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)


def get_chrome_path():
    """获取Chrome路径"""
    possible_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.environ.get('LOCALAPPDATA', '') + "\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for path in possible_paths:
        if path and Path(path).exists():
            return path
    return None


async def fetch_isw_raw():
    """抓取ISW原始数据（英文）"""
    ensure_dirs()
    
    async with async_playwright() as p:
        chrome_path = get_chrome_path()
        if chrome_path:
            browser = await p.chromium.launch(
                executable_path=chrome_path,
                headless=True
            )
        else:
            browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36'
        )
        
        page = await context.new_page()
        
        try:
            print("[访问] ISW index page...")
            await page.goto(ISW_INDEX_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            
            # 找到最新报告链接
            latest_link = await page.evaluate('''() => {
                // 方法1: 查找包含iran-update的链接
                const links = document.querySelectorAll('a[href*="iran-update"]');
                for (let link of links) {
                    const href = link.getAttribute('href');
                    if (href && href.includes('backgrounder')) {
                        return href.startsWith('http') ? href : 'https://understandingwar.org' + href;
                    }
                }
                
                // 方法2: 查找任何包含backgrounder的链接
                const allLinks = document.querySelectorAll('a[href*="backgrounder"]');
                for (let link of allLinks) {
                    const href = link.getAttribute('href');
                    if (href && href.includes('iran')) {
                        return href.startsWith('http') ? href : 'https://understandingwar.org' + href;
                    }
                }
                
                // 方法3: 直接构造今天的日期URL
                return null;
            }''')
            
            # 如果没有找到，尝试直接访问最近几天的报告
            if not latest_link:
                from datetime import datetime, timedelta
                
                # 尝试最近5天
                for days_back in range(0, 5):
                    date = datetime.now() - timedelta(days=days_back)
                    month_name = date.strftime("%B").lower()
                    day = date.day
                    year = date.year
                    
                    # 尝试多种日期格式
                    possible_urls = [
                        f"https://understandingwar.org/backgrounder/iran-update-{month_name}-{day}-{year}",
                        f"https://understandingwar.org/backgrounder/iran-update-special-report-{month_name}-{day}-{year}",
                    ]
                    
                    print(f"[尝试] {date.strftime('%Y-%m-%d')} 的URL...")
                    for url in possible_urls:
                        try:
                            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                            await asyncio.sleep(2)
                            
                            # 检查是否是真的报告页面（不是404）
                            title = await page.title()
                            if title and "not found" not in title.lower() and "404" not in title.lower():
                                latest_link = page.url
                                print(f"[找到] {latest_link}")
                                break
                        except:
                            continue
                    
                    if latest_link:
                        break
            
            if not latest_link:
                print("[错误] 未找到报告链接")
                return None
            
            print(f"[找到] {latest_link}")
            
            # 提取历史报告列表（从当前页面）
            print("[提取] 历史报告列表...")
            history_reports = await extract_history_reports(page)
            print(f"[提取] {len(history_reports)} 条历史记录")
            
            # 访问报告页面
            await page.goto(latest_link, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            
            # 提取基础信息
            title = await page.title()
            
            # 从URL提取日期
            date_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})', latest_link.lower())
            if date_match:
                month_num = ['january', 'february', 'march', 'april', 'may', 'june', 
                           'july', 'august', 'september', 'october', 'november', 'december'].index(date_match.group(1)) + 1
                report_date = f"{date_match.group(3)}-{month_num:02d}-{date_match.group(2).zfill(2)}"
            else:
                report_date = datetime.now().strftime("%Y-%m-%d")
            
            print(f"[日期] {report_date}")
            
            # 提取Key Takeaways（英文原文）
            print("[提取] Key Takeaways...")
            takeaways = await extract_takeaways_raw(page)
            print(f"[提取] {len(takeaways)} 条Takeaways")
            
            # 提取正文段落（用于图表上下文）
            print("[提取] 正文段落...")
            paragraphs = await extract_paragraphs_raw(page)
            print(f"[提取] {len(paragraphs)} 段正文")
            
            # 捕获所有图表
            print("[截图] 图表...")
            charts = await capture_all_charts(page, report_date, paragraphs)
            print(f"[截图] {len(charts)} 张图表")
            
            result = {
                "updated": datetime.now(BEIJING_TZ).isoformat(),
                "source_url": latest_link,
                "report": {
                    "title": title,
                    "date": report_date,
                    "takeaways": takeaways,  # 英文原文
                    "paragraphs": paragraphs,  # 英文原文段落
                    "charts": charts
                },
                "history": history_reports  # 历史报告列表
            }
            
            # 保存原始数据
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[保存] {DATA_FILE}")
            
            return result
            
        except Exception as e:
            print(f"[错误] {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()


async def extract_history_reports(page):
    """提取历史报告列表（从Iran Updates主页）"""
    reports = await page.evaluate('''() => {
        const results = [];
        const seen = new Set();
        
        // 方法1: 查找所有包含iran-update的链接
        const links = document.querySelectorAll('a[href*="iran-update"]');
        
        for (let link of links) {
            const href = link.getAttribute('href');
            if (!href || seen.has(href)) continue;
            
            // 只处理backgrounder链接
            if (!href.includes('backgrounder')) continue;
            
            // 提取日期
            const dateMatch = href.match(/(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})/i);
            if (!dateMatch) continue;
            
            // 解析日期
            const months = ['january', 'february', 'march', 'april', 'may', 'june', 
                           'july', 'august', 'september', 'october', 'november', 'december'];
            const monthNum = months.indexOf(dateMatch[1].toLowerCase()) + 1;
            const day = dateMatch[2].padStart(2, '0');
            const year = dateMatch[3];
            const dateStr = `${year}-${monthNum.toString().padStart(2, '0')}-${day}`;
            
            // 获取标题
            let title = link.textContent.trim();
            if (!title) {
                // 尝试从父元素获取
                const parent = link.closest('article, .view-content, .item-list, li, .views-row');
                if (parent) {
                    title = parent.textContent.trim().substring(0, 100);
                }
            }
            if (!title) {
                title = `Iran Update - ${dateStr}`;
            }
            
            // 构造完整URL
            const fullUrl = href.startsWith('http') ? href : 'https://understandingwar.org' + href;
            
            seen.add(href);
            results.push({
                date: dateStr,
                title: title,
                url: fullUrl
            });
        }
        
        // 按日期降序排序
        results.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // 只返回最近30条
        return results.slice(0, 30);
    }'''
    
    return reports


async def extract_takeaways_raw(page):
    """提取Key Takeaways（英文原文）"""
    takeaways = await page.evaluate('''() => {
        const results = [];
        
        // 方法1: 查找Key Takeaways标题后的列表
        const headings = document.querySelectorAll('h2, h3, h4, strong, p');
        for (let h of headings) {
            const text = h.textContent.trim().toLowerCase();
            if (/^(key\s+takeaway|key\s+points|highlights|executive\s+summary|summary)/i.test(text)) {
                // 查找后续的ul/ol列表
                let el = h.parentElement;
                for (let i = 0; i < 5 && el; i++) {
                    const list = el.querySelector('ul, ol');
                    if (list) {
                        const items = list.querySelectorAll('li');
                        for (let item of items) {
                            const content = item.textContent.trim();
                            if (content.length > 20) {
                                results.push({
                                    type: 'list_item',
                                    content: content
                                });
                            }
                        }
                        break;
                    }
                    el = el.nextElementSibling || h.nextElementSibling;
                }
                break;
            }
        }
        
        // 方法2: 如果没找到，尝试查找包含特定关键词的段落
        if (results.length === 0) {
            const allParagraphs = document.querySelectorAll('p');
            for (let p of allParagraphs) {
                const text = p.textContent.trim();
                // 查找看起来像takeaway的段落（较长、包含军事术语）
                if (text.length > 100 && text.length < 800) {
                    const hasMilitaryTerms = /\b(strike|attack|force|military|iran|israel|defense|operation)\b/i.test(text);
                    if (hasMilitaryTerms) {
                        results.push({
                            type: 'paragraph',
                            content: text
                        });
                    }
                }
                if (results.length >= 8) break;
            }
        }
        
        return results;
    }''')
    
    return takeaways


async def extract_paragraphs_raw(page):
    """提取正文段落（英文原文）"""
    paragraphs = await page.evaluate('''() => {
        const results = [];
        const allParagraphs = document.querySelectorAll('p');
        
        for (let p of allParagraphs) {
            const text = p.textContent.trim();
            // 过滤掉太短的段落
            if (text.length > 80 && text.length < 2000) {
                // 排除导航、版权等无关内容
                if (!text.includes('Copyright') && 
                    !text.includes('All rights reserved') &&
                    !text.includes('Click here') &&
                    !text.startsWith('Fig.') &&
                    !text.startsWith('Figure')) {
                    results.push(text);
                }
            }
        }
        
        return results;
    }''')
    
    return paragraphs


async def capture_all_charts(page, report_date, paragraphs):
    """捕获所有图表 - 改进版"""
    charts = []
    
    # 滚动到页面顶部
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(1)
    
    # 获取所有图片（滚动到可见区域后重新获取）
    for scroll_attempt in range(3):
        images = await page.evaluate('''() => {
            const results = [];
            const imgs = document.querySelectorAll('img');
            
            for (let img of imgs) {
                // 滚动到图片位置
                img.scrollIntoView({ behavior: 'instant', block: 'center' });
                
                const rect = img.getBoundingClientRect();
                // 过滤小图标和logo
                if (rect.width > 400 && rect.height > 250) {
                    // 检查是否是地图或图表
                    const isMap = img.src.toLowerCase().includes('map') || 
                                 img.alt.toLowerCase().includes('map');
                    const isChart = img.src.toLowerCase().includes('chart') || 
                                   img.alt.toLowerCase().includes('chart') ||
                                   img.alt.toLowerCase().includes('figure');
                    
                    if (isMap || isChart || rect.width > 600) {
                        results.push({
                            src: img.src,
                            alt: img.alt || '',
                            width: rect.width,
                            height: rect.height,
                            isMap: isMap,
                            isChart: isChart
                        });
                    }
                }
            }
            
            return results;
        }''')
        
        if len(images) > 0:
            break
        
        # 向下滚动继续查找
        await page.evaluate(f'window.scrollTo(0, {(scroll_attempt + 1) * 1000})')
        await asyncio.sleep(1)
    
    # 去重
    seen_src = set()
    unique_images = []
    for img in images:
        if img['src'] not in seen_src:
            seen_src.add(img['src'])
            unique_images.append(img)
    
    images = unique_images[:8]  # 最多8张
    print(f"  找到 {len(images)} 张有效图表")
    
    # 截图每张图片
    for idx, img_info in enumerate(images):
        try:
            filename = f"chart_{report_date}_{idx:02d}.png"
            filepath = SCREENSHOT_DIR / filename
            
            # 滚动到图片位置并等待加载
            await page.evaluate(f'''() => {{
                const imgs = document.querySelectorAll('img');
                for (let img of imgs) {{
                    if (img.src === '{img_info['src']}') {{
                        img.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                        break;
                    }}
                }}
            }}''')
            await asyncio.sleep(2)
            
            # 使用全页截图然后裁剪
            await page.screenshot(path=str(filepath), full_page=False)
            
            # 获取实际截图尺寸
            from PIL import Image
            with Image.open(filepath) as im:
                width, height = im.size
                # 如果图片太小，可能是截图失败
                if width < 400 or height < 300:
                    continue
            
            # 查找与图片相关的正文
            related_text = find_related_paragraphs(img_info['alt'], paragraphs)
            
            charts.append({
                "filename": filename,
                "path": str(filepath.relative_to(WORKDIR)),
                "alt": img_info['alt'],
                "size": {"width": width, "height": height},
                "is_map": img_info.get('isMap', False),
                "is_chart": img_info.get('isChart', False),
                "related_paragraphs": related_text[:2]  # 最相关的2段
            })
            
            print(f"  [截图] {filename}")
            
        except Exception as e:
            print(f"  [错误] 截图失败: {e}")
    
    return charts


def find_related_paragraphs(alt_text, paragraphs):
    """查找与图片相关的段落（基于关键词匹配）"""
    if not alt_text:
        return []
    
    # 从alt文本提取关键词
    keywords = re.findall(r'\b[A-Za-z]{4,}\b', alt_text.lower())
    
    related = []
    for para in paragraphs:
        para_lower = para.lower()
        # 计算匹配的关键词数量
        matches = sum(1 for kw in keywords if kw in para_lower)
        if matches >= 2 or any(kw in para_lower for kw in ['map', 'figure', 'chart', 'strike', 'attack']):
            related.append(para[:300] + "..." if len(para) > 300 else para)
    
    return related[:3]  # 返回最相关的3段


async def main():
    print("=" * 60)
    print("ISW 数据提取（英文原文）")
    print("=" * 60)
    
    data = await fetch_isw_raw()
    
    if data:
        print("\n" + "=" * 60)
        print("提取完成!")
        print(f"  报告: {data['report']['title']}")
        print(f"  日期: {data['report']['date']}")
        print(f"  Takeaways: {len(data['report']['takeaways'])}")
        print(f"  正文段落: {len(data['report']['paragraphs'])}")
        print(f"  图表: {len(data['report']['charts'])}")
        print(f"\n数据文件: {DATA_FILE}")
        print("=" * 60)
    else:
        print("[失败]")


if __name__ == "__main__":
    asyncio.run(main())
