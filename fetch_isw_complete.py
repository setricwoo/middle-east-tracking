#!/usr/bin/env python3
"""
Enhanced ISW data fetcher with better extraction
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_war_data.json"

def translate_to_chinese(text):
    """Translate common military terms"""
    if not text:
        return ""
    
    # Common military/geopolitical terms
    translations = {
        r'\bIran\b': '伊朗',
        r'\bIranian\b': '伊朗的',
        r'\bIsrael\b': '以色列',
        r'\bIsraeli\b': '以色列的',
        r'\bUnited States\b': '美国',
        r'\bUS\b': '美国',
        r'\bAmerican\b': '美国的',
        r'\bmissile\b': '导弹',
        r'\bballistic\b': '弹道',
        r'\battack\b': '袭击',
        r'\battacked\b': '袭击了',
        r'\bmilitary\b': '军事',
        r'\bforces?\b': '部队',
        r'\bnuclear\b': '核',
        r'\bfacilities?\b': '设施',
        r'\baircraft carrier\b': '航空母舰',
        r'\bcarrier\b': '航母',
        r'\bdeplo(y|yed|ying)\b': '部署',
        r'\btarget(ed|ing)\b': '针对',
        r'\bstrike(s|d)?\b': '打击',
        r'\bairstrike(s|d)?\b': '空袭',
        r'\bHezbollah\b': '真主党',
        r'\bHouthis?\b': '胡塞武装',
        r'\bproxy\b': '代理',
        r'\bescalation\b': '升级',
        r'\bde-escalation\b': '降级',
        r'\bceasefire\b': '停火',
        r'\bQatar\b': '卡塔尔',
        r'\bUAE\b': '阿联酋',
        r'\bSaudi Arabia\b': '沙特阿拉伯',
        r'\bPersian Gulf\b': '波斯湾',
        r'\bRed Sea\b': '红海',
        r'\bStrait of Hormuz\b': '霍尔木兹海峡',
        r'\bTehran\b': '德黑兰',
        r'\bNatanz\b': '纳坦兹',
        r'\bIsfahan\b': '伊斯法罕',
        r'\bIRGC\b': '伊斯兰革命卫队',
        r'\bintermediaries?\b': '中介',
        r'\bnegotiations?\b': '谈判',
        r'\bdiplomatic\b': '外交',
        r'\bconflict\b': '冲突',
        r'\bwar\b': '战争',
        r'\bdefense\b': '防御',
        r'\bair defense\b': '防空',
        r'\bintercepted\b': '拦截',
        r'\blaunched\b': '发射',
        r'\bdamage\b': '破坏',
        r'\bdestroyed\b': '摧毁',
        r'\bcasualties?\b': '伤亡',
        r'\bcivilians?\b': '平民',
        r'\binfrastructure\b': '基础设施',
        r'\boil\b': '石油',
        r'\bsanctions?\b': '制裁',
        r'\bexport\b': '出口',
        r'\bimport\b': '进口',
        r'\bhumanitarian\b': '人道主义',
        r'\brefugees?\b': '难民',
        r'\bcrisis\b': '危机',
        r'\burgent\b': '紧急',
        r'\bsignificant\b': '重大',
        r'\bsubstantial\b': '大量',
        r'\bconfirmed\b': '已确认',
        r'\breported\b': '据报道',
        r'\bofficials?\b': '官员',
        r'\bgovernment\b': '政府',
        r'\bregime\b': '政权',
        r'\bspecial forces\b': '特种部队',
        r'\bdrone(s|d)?\b': '无人机',
        r'\bUAV\b': '无人机',
        r'\btanks?\b': '坦克',
        r'\bships?\b': '舰艇',
        r'\bsubmarines?\b': '潜艇',
        r'\bbases?\b': '基地',
        r'\boperations?\b': '行动',
        r'\bstrategy\b': '战略',
        r'\btactics?\b': '战术',
        r'\bintelligence\b': '情报',
        r'\bLebanon\b': '黎巴嫩',
        r'\bSyria\b': '叙利亚',
        r'\bYemen\b': '也门',
        r'\bIraq\b': '伊拉克',
        r'\bJordan\b': '约旦',
        r'\bEgypt\b': '埃及',
        r'\bGaza\b': '加沙',
        r'\bWest Bank\b': '约旦河西岸',
        r'\bJerusalem\b': '耶路撒冷',
        r'\bTel Aviv\b': '特拉维夫',
        r'\bDamascus\b': '大马士革',
        r'\bBeirut\b': '贝鲁特',
        r'\bBaghdad\b': '巴格达',
        r'\bSanaa\b': '萨那',
        r'\bRiyadh\b': '利雅得',
        r'\bAbu Dhabi\b': '阿布扎比',
        r'\bDoha\b': '多哈',
        r'\bKuwait\b': '科威特',
        r'\bManama\b': '麦纳麦',
        r'\bMuscat\b': '马斯喀特',
        r'\bDiego Garcia\b': '迭戈加西亚',
        r'\bCENTCOM\b': '中央司令部',
        r'\bPentagon\b': '五角大楼',
        r'\bWhite House\b': '白宫',
        r'\bState Department\b': '国务院',
        r'\bDefense Department\b': '国防部',
        r'\bCIA\b': '中情局',
        r'\bNATO\b': '北约',
        r'\bUnited Nations\b': '联合国',
        r'\bUN\b': '联合国',
        r'\bSecurity Council\b': '安理会',
    }
    
    result = text
    for pattern, replacement in translations.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

async def fetch_isw_enhanced(url):
    """Fetch ISW report with enhanced extraction"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print(f"Fetching {url}...")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(3)
        
        # Get page content
        content = await page.content()
        
        # Extract data using JavaScript
        data = await page.evaluate("""
            () => {
                const result = {
                    title: '',
                    date: '',
                    takeaways: [],
                    charts: []
                };
                
                // Get title
                const titleEl = document.querySelector('h1.entry-title');
                if (titleEl) result.title = titleEl.textContent.trim();
                
                // Get date from time element
                const timeEl = document.querySelector('time[datetime]');
                if (timeEl) result.date = timeEl.getAttribute('datetime');
                
                // Extract takeaways - look for bold text in the first several paragraphs
                const content = document.querySelector('.entry-content');
                if (content) {
                    // Method 1: Look for paragraphs starting with bold text
                    const allParagraphs = content.querySelectorAll('p');
                    let foundTakeaways = false;
                    
                    for (let p of allParagraphs.slice(0, 15)) {  // Check first 15 paragraphs
                        const text = p.textContent.trim();
                        const hasBold = p.querySelector('strong, b');
                        
                        // Takeaways are usually short, bold, meaningful sentences
                        if (hasBold && text.length > 40 && text.length < 400 && 
                            !text.includes('Note:') && 
                            !text.includes('Click here') &&
                            !text.includes('Read the full')) {
                            result.takeaways.push(text);
                            foundTakeaways = true;
                        }
                    }
                    
                    // Method 2: If no bold paragraphs, look for bullet points
                    if (!foundTakeaways) {
                        const lists = content.querySelectorAll('ul li');
                        for (let li of lists.slice(0, 10)) {
                            const text = li.textContent.trim();
                            if (text.length > 30 && text.length < 300) {
                                result.takeaways.push(text);
                            }
                        }
                    }
                }
                
                // Get ALL chart images - maps, charts, graphs, diagrams
                const images = document.querySelectorAll('.entry-content img');
                const seenUrls = new Set();
                
                for (let img of images) {
                    const src = img.src || '';
                    const alt = img.alt || '';
                    
                    // Skip if already added
                    if (seenUrls.has(src)) continue;
                    
                    // Include all content images from uploads with date patterns
                    // This includes: maps, charts, graphs, diagrams, bar charts, etc.
                    if (src.includes('uploads') && 
                        (src.includes('2026') || src.includes('2025')) &&
                        !src.includes('150x150') &&  // Skip thumbnails
                        !src.includes('avatar') &&
                        !src.includes('Babel_Street') &&  // Skip logo
                        !src.includes('Print-Img') &&  // Skip print icon
                        !src.endsWith('.svg')) {  // Skip SVG icons
                        
                        seenUrls.add(src);
                        result.charts.push({
                            url: src,
                            alt: alt || 'ISW Chart'
                        });
                    }
                }
                
                return result;
            }
        """)
        
        await browser.close()
        return data

def save_enhanced_data(raw_data, url):
    """Save data with translations"""
    
    # Process takeaways
    takeaways = []
    for i, text in enumerate(raw_data.get('takeaways', [])[:8]):  # Limit to 8
        # Clean up text
        clean_text = re.sub(r'\s+', ' ', text).strip()
        takeaways.append({
            "en": clean_text,
            "zh": translate_to_chinese(clean_text)
        })
    
    # Process charts - extract ALL charts (maps, bar charts, line charts, etc.)
    charts = []
    for chart in raw_data.get('charts', []):  # No limit - extract all charts
        alt_text = chart.get('alt', '')
        url = chart.get('url', '')
        
        # Extract context from alt text or URL
        context_items = []
        if 'Iranian' in alt_text or 'iranian' in url.lower():
            context_items.append("伊朗方面的军事行动")
        if 'US' in alt_text or 'israeli' in url.lower():
            context_items.append("美以联军行动")
        if 'Strike' in alt_text or 'strikes' in url.lower():
            context_items.append("精确打击行动")
        if 'Launch' in alt_text or 'launches' in url.lower():
            context_items.append("导弹发射活动")
        if 'Hezbollah' in alt_text:
            context_items.append("真主党相关活动")
        
        if not context_items:
            context_items = ["ISW战略分析"]
        
        charts.append({
            "url": url,
            "title": alt_text or "ISW Analysis",
            "title_zh": translate_to_chinese(alt_text) or "ISW战略分析",
            "description": "ISW战场态势分析",
            "description_zh": "ISW战场态势分析",
            "context": context_items
        })
    
    result = {
        "updated": datetime.now().isoformat(),
        "source_url": url,
        "current_report": {
            "url": url,
            "title": raw_data.get('title', ''),
            "title_zh": translate_to_chinese(raw_data.get('title', '')),
            "date": raw_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            "takeaways": takeaways,
            "charts": charts
        },
        "history": [
            {
                "date": "2026-03-21",
                "title": "Iran Update Special Report, March 21, 2026",
                "title_zh": "伊朗局势更新特别报告 - 2026年3月21日",
                "url": "https://understandingwar.org/backgrounder/iran-update-special-report-march-21-2026"
            },
            {
                "date": "2026-03-19",
                "title": "Iran Update, March 19, 2026",
                "title_zh": "伊朗局势更新 - 2026年3月19日",
                "url": "https://understandingwar.org/backgrounder/iran-update-march-19-2026"
            },
            {
                "date": "2026-03-17",
                "title": "Iran Update, March 17, 2026",
                "title_zh": "伊朗局势更新 - 2026年3月17日",
                "url": "https://understandingwar.org/backgrounder/iran-update-march-17-2026"
            }
        ]
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(takeaways)} takeaways and {len(charts)} charts")
    return result

async def main():
    url = "https://understandingwar.org/research/middle-east/iran-update-special-report-march-23-2026"
    
    raw_data = await fetch_isw_enhanced(url)
    print(f"Found {len(raw_data.get('takeaways', []))} raw takeaways")
    print(f"Found {len(raw_data.get('charts', []))} charts")
    
    if raw_data.get('takeaways') or raw_data.get('charts'):
        save_enhanced_data(raw_data, url)
        print(f"Data saved to {DATA_FILE}")
    else:
        print("No data extracted")

if __name__ == "__main__":
    asyncio.run(main())
