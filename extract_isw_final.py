#!/usr/bin/env python3
"""
Final ISW data extractor using correct selectors
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_war_data.json"

def translate(text):
    """Translate military terms"""
    if not text:
        return ""
    
    replacements = [
        (r'\bIran\b', '伊朗'),
        (r'\bIranian\b', '伊朗的'),
        (r'\bIsrael\b', '以色列'),
        (r'\bIsraeli\b', '以色列的'),
        (r'\bUnited States\b', '美国'),
        (r'\bUS\b', '美国'),
        (r'\bAmerican\b', '美国的'),
        (r'\bmissile\b', '导弹'),
        (r'\bballistic\b', '弹道'),
        (r'\battack\b', '袭击'),
        (r'\bmilitary\b', '军事'),
        (r'\bforces?\b', '部队'),
        (r'\bnuclear\b', '核'),
        (r'\bfacilities?\b', '设施'),
        (r'\baircraft carrier\b', '航空母舰'),
        (r'\bcarrier\b', '航母'),
        (r'\bdeplo(y|yed)\b', '部署'),
        (r'\btarget(ed|ing)\b', '针对'),
        (r'\bstrike(s|d)?\b', '打击'),
        (r'\bairstrike(s|d)?\b', '空袭'),
        (r'\bHezbollah\b', '真主党'),
        (r'\bHouthis?\b', '胡塞武装'),
        (r'\bproxy\b', '代理'),
        (r'\bescalation\b', '升级'),
        (r'\bceasefire\b', '停火'),
        (r'\bQatar\b', '卡塔尔'),
        (r'\bUAE\b', '阿联酋'),
        (r'\bSaudi Arabia\b', '沙特阿拉伯'),
        (r'\bPersian Gulf\b', '波斯湾'),
        (r'\bRed Sea\b', '红海'),
        (r'\bStrait of Hormuz\b', '霍尔木兹海峡'),
        (r'\bTehran\b', '德黑兰'),
        (r'\bNatanz\b', '纳坦兹'),
        (r'\bIsfahan\b', '伊斯法罕'),
        (r'\bIRGC\b', '伊斯兰革命卫队'),
        (r'\bintermediaries?\b', '中介'),
        (r'\bnegotiations?\b', '谈判'),
        (r'\bdiplomatic\b', '外交'),
        (r'\bconflict\b', '冲突'),
        (r'\bwar\b', '战争'),
        (r'\bdefense\b', '防御'),
        (r'\bair defense\b', '防空'),
        (r'\bintercepted\b', '拦截'),
        (r'\blaunched\b', '发射'),
        (r'\bdamage\b', '破坏'),
        (r'\bdestroyed\b', '摧毁'),
        (r'\bcasualties?\b', '伤亡'),
        (r'\bcivilians?\b', '平民'),
        (r'\bsanctions?\b', '制裁'),
        (r'\bhumanitarian\b', '人道主义'),
        (r'\brefugees?\b', '难民'),
        (r'\bcrisis\b', '危机'),
        (r'\bsignificant\b', '重大'),
        (r'\bconfirmed\b', '已确认'),
        (r'\breported\b', '据报道'),
        (r'\bofficials?\b', '官员'),
        (r'\bgovernment\b', '政府'),
        (r'\bregime\b', '政权'),
        (r'\bspecial forces\b', '特种部队'),
        (r'\bdrone(s|d)?\b', '无人机'),
        (r'\btanks?\b', '坦克'),
        (r'\bships?\b', '舰艇'),
        (r'\bsubmarines?\b', '潜艇'),
        (r'\bbases?\b', '基地'),
        (r'\boperations?\b', '行动'),
        (r'\bstrategy\b', '战略'),
        (r'\bLebanon\b', '黎巴嫩'),
        (r'\bSyria\b', '叙利亚'),
        (r'\bYemen\b', '也门'),
        (r'\bIraq\b', '伊拉克'),
        (r'\bGaza\b', '加沙'),
        (r'\bWest Bank\b', '约旦河西岸'),
        (r'\bJerusalem\b', '耶路撒冷'),
        (r'\bTel Aviv\b', '特拉维夫'),
        (r'\bDamascus\b', '大马士革'),
        (r'\bBeirut\b', '贝鲁特'),
        (r'\bBaghdad\b', '巴格达'),
        (r'\bSanaa\b', '萨那'),
        (r'\bRiyadh\b', '利雅得'),
        (r'\bAbu Dhabi\b', '阿布扎比'),
        (r'\bDoha\b', '多哈'),
        (r'\bKuwait\b', '科威特'),
        (r'\bDiego Garcia\b', '迭戈加西亚'),
        (r'\bCENTCOM\b', '中央司令部'),
        (r'\bPentagon\b', '五角大楼'),
        (r'\bWhite House\b', '白宫'),
        (r'\bCIA\b', '中情局'),
        (r'\bNATO\b', '北约'),
        (r'\bUnited Nations\b', '联合国'),
    ]
    
    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

async def extract_isw():
    url = "https://understandingwar.org/research/middle-east/iran-update-special-report-march-23-2026"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Loading {url}...")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(5)
        
        # Extract all data
        data = await page.evaluate("""
            () => {
                const result = { title: '', date: '', takeaways: [], charts: [] };
                
                // Title
                const h1 = document.querySelector('h1');
                if (h1) result.title = h1.innerText.trim();
                
                // Date
                const dateEl = document.querySelector('time');
                if (dateEl) result.date = dateEl.getAttribute('datetime');
                
                // Content paragraphs - look for bold/strong text which are takeaways
                const allP = document.querySelectorAll('p');
                for (let p of allP) {
                    const strong = p.querySelector('strong');
                    if (strong) {
                        const text = p.innerText.trim();
                        // Takeaways are typically 50-400 chars
                        if (text.length > 50 && text.length < 400) {
                            result.takeaways.push(text);
                        }
                    }
                }
                
                // Images
                const imgs = document.querySelectorAll('img');
                for (let img of imgs) {
                    const src = img.src || '';
                    if (src.includes('uploads') && src.includes('2026') && 
                        !src.includes('150x150') && !src.includes('avatar')) {
                        result.charts.push({
                            url: src,
                            alt: img.alt || ''
                        });
                    }
                }
                
                return result;
            }
        """)
        
        await browser.close()
        return data, url

def save_data(raw_data, url):
    # Process takeaways (deduplicate and limit)
    seen = set()
    takeaways = []
    for text in raw_data.get('takeaways', []):
        clean = re.sub(r'\s+', ' ', text).strip()
        if clean not in seen and len(clean) > 40:
            seen.add(clean)
            takeaways.append({
                "en": clean,
                "zh": translate(clean)
            })
        if len(takeaways) >= 6:
            break
    
    # Process charts (filter meaningful ones)
    charts = []
    seen_urls = set()
    for chart in raw_data.get('charts', []):
        src = chart.get('url', '')
        if src in seen_urls:
            continue
        seen_urls.add(src)
        
        alt = chart.get('alt', '')
        # Extract context from URL/filename
        context = ["ISW战略分析"]
        if 'Iranian' in src or 'iranian' in src.lower():
            context.append("伊朗军事行动")
        if 'US' in src or 'israeli' in src.lower():
            context.append("美以联军行动")
        if 'Strike' in src or 'strike' in src.lower():
            context.append("精确打击")
        if 'Launch' in src or 'launch' in src.lower():
            context.append("导弹发射")
        if 'Hezbollah' in src:
            context.append("真主党活动")
        if 'Bahrain' in src:
            context.append("巴林局势")
        if 'UAE' in src:
            context.append("阿联酋局势")
        if 'Kuwait' in src:
            context.append("科威特局势")
        if 'KSA' in src:
            context.append("沙特局势")
            
        charts.append({
            "url": src,
            "title": alt or "ISW Analysis",
            "title_zh": translate(alt) or "ISW战略分析",
            "context": context[:3]
        })
        
        if len(charts) >= 8:
            break
    
    result = {
        "updated": datetime.now().isoformat(),
        "source_url": url,
        "current_report": {
            "url": url,
            "title": raw_data.get('title', ''),
            "title_zh": translate(raw_data.get('title', '')),
            "date": raw_data.get('date', '2026-03-23'),
            "takeaways": takeaways,
            "charts": charts
        },
        "history": [
            {"date": "2026-03-21", "title": "Iran Update Special Report, March 21, 2026", "title_zh": "伊朗局势更新特别报告 - 2026年3月21日", "url": "https://understandingwar.org/backgrounder/iran-update-special-report-march-21-2026"},
            {"date": "2026-03-19", "title": "Iran Update, March 19, 2026", "title_zh": "伊朗局势更新 - 2026年3月19日", "url": "https://understandingwar.org/backgrounder/iran-update-march-19-2026"},
            {"date": "2026-03-17", "title": "Iran Update, March 17, 2026", "title_zh": "伊朗局势更新 - 2026年3月17日", "url": "https://understandingwar.org/backgrounder/iran-update-march-17-2026"}
        ]
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(takeaways)} takeaways, {len(charts)} charts")
    return result

async def main():
    raw_data, url = await extract_isw()
    print(f"Found {len(raw_data.get('takeaways', []))} takeaways")
    print(f"Found {len(raw_data.get('charts', []))} charts")
    
    if raw_data.get('takeaways') or raw_data.get('charts'):
        save_data(raw_data, url)
    else:
        print("No data found")

if __name__ == "__main__":
    asyncio.run(main())
