#!/usr/bin/env python3
"""
Fetch ISW (Institute for the Study of War) Iran Update reports
Extract takeaways, translate to Chinese, and download charts
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_war_data.json"

def simple_translate(text):
    """Simple translation for common military terms"""
    replacements = {
        'Iran': '伊朗',
        'Iranian': '伊朗的',
        'Israel': '以色列',
        'Israeli': '以色列的',
        'United States': '美国',
        'US': '美国',
        'missile': '导弹',
        'ballistic missile': '弹道导弹',
        'attack': '袭击',
        'military': '军事',
        'forces': '部队',
        'nuclear': '核',
        'facilities': '设施',
        'aircraft carrier': '航空母舰',
        'carrier': '航母',
        'deployed': '部署',
        'deployment': '部署',
        'targeted': '针对',
        'strikes': '打击',
        'airstrikes': '空袭',
        'Hezbollah': '真主党',
        'Houthis': '胡塞武装',
        'proxy': '代理',
        'escalation': '升级',
        'de-escalation': '降级',
        'ceasefire': '停火',
        'Qatar': '卡塔尔',
        'UAE': '阿联酋',
        'Saudi Arabia': '沙特阿拉伯',
        'Persian Gulf': '波斯湾',
        'Red Sea': '红海',
        'Strait of Hormuz': '霍尔木兹海峡',
        'Tehran': '德黑兰',
        'Natanz': '纳坦兹',
        'Isfahan': '伊斯法罕',
        'IRGC': '伊斯兰革命卫队',
        'Revolutionary Guards': '革命卫队',
        'intermediaries': '中介',
        'negotiations': '谈判',
        'diplomatic': '外交',
        'conflict': '冲突',
        'war': '战争',
        'defense': '防御',
        'offense': '进攻',
        'intelligence': '情报',
        'surveillance': '监视',
        'reconnaissance': '侦察',
        'air defense': '防空',
        'missile defense': '导弹防御',
        'intercepted': '拦截',
        'launched': '发射',
        'damage': '破坏',
        'destroyed': '摧毁',
        'casualties': '伤亡',
        'civilians': '平民',
        'infrastructure': '基础设施',
        'oil': '石油',
        'energy': '能源',
        'sanctions': '制裁',
        'export': '出口',
        'import': '进口',
        'blockade': '封锁',
        'no-fly zone': '禁飞区',
        'humanitarian': '人道主义',
        'aid': '援助',
        'refugees': '难民',
        'displaced': '流离失所',
        'emergency': '紧急',
        'alert': '警报',
        'threat': '威胁',
        'risk': '风险',
        'crisis': '危机',
        'urgent': '紧急',
        'critical': '关键',
        'significant': '重大',
        'substantial': '大量',
        'major': '主要',
        'minor': '次要',
        'limited': '有限',
        'extensive': '广泛',
        'severe': '严重',
        'moderate': '中度',
        'light': '轻微',
        'heavy': '沉重',
        'intense': '激烈',
        'fierce': '猛烈',
        'violent': '暴力',
        'peaceful': '和平',
        'stable': '稳定',
        'unstable': '不稳定',
        'volatile': '动荡',
        'uncertain': '不确定',
        'likely': '可能',
        'unlikely': '不太可能',
        'possible': '可能',
        'impossible': '不可能',
        'probable': '很可能',
        'improbable': '不太可能发生',
        'confirmed': '已确认',
        'unconfirmed': '未确认',
        'reported': '据报道',
        'claimed': '宣称',
        'denied': '否认',
        'admitted': '承认',
        'announced': '宣布',
        'stated': '表示',
        'said': '说',
        'according to': '根据',
        'sources': '消息来源',
        'officials': '官员',
        'spokesperson': '发言人',
        'leadership': '领导层',
        'government': '政府',
        'regime': '政权',
        'administration': '政府',
        'military': '军方',
        'army': '陆军',
        'navy': '海军',
        'air force': '空军',
        'marines': '海军陆战队',
        'special forces': '特种部队',
        'commandos': '突击队',
        'infantry': '步兵',
        'armor': '装甲',
        'artillery': '炮兵',
        'aircraft': '飞机',
        'fighter jets': '战斗机',
        'bombers': '轰炸机',
        'drones': '无人机',
        'UAV': '无人机',
        'helicopters': '直升机',
        'tanks': '坦克',
        'vehicles': '车辆',
        'ships': '舰艇',
        'vessels': '船只',
        'submarines': '潜艇',
        'destroyers': '驱逐舰',
        'frigates': '护卫舰',
        'bases': '基地',
        'headquarters': '总部',
        'command center': '指挥中心',
        'operations': '行动',
        'mission': '任务',
        'objective': '目标',
        'strategy': '战略',
        'tactics': '战术',
        'plan': '计划',
        'operation': '作战',
        'exercise': '演习',
        'patrol': '巡逻',
        'surveillance': '监视',
        'reconnaissance': '侦察',
        'intelligence gathering': '情报收集',
        'special operation': '特种作战',
        'covert': '秘密',
        'clandestine': '隐秘',
        'overt': '公开',
        'announced': '宣布的',
        'unannounced': '未宣布的',
    }
    
    # Replace whole words only
    result = text
    for en, zh in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        result = re.sub(r'\b' + re.escape(en) + r'\b', zh, result, flags=re.IGNORECASE)
    return result

async def fetch_isw_report(url):
    """Fetch and parse ISW report"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print(f"Fetching {url}...")
        try:
            await page.goto(url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Error loading page: {e}")
            await browser.close()
            return None
        
        # Extract data
        data = await page.evaluate("""
            () => {
                const result = {
                    title: '',
                    date: '',
                    takeaways: [],
                    charts: []
                };
                
                // Get title
                const titleEl = document.querySelector('h1.entry-title, h1.article-title, .page-title');
                if (titleEl) result.title = titleEl.textContent.trim();
                
                // Get date
                const dateEl = document.querySelector('.entry-date, .published, time');
                if (dateEl) {
                    result.date = dateEl.getAttribute('datetime') || dateEl.textContent.trim();
                }
                
                // Get takeaways - look for bold/strong paragraphs at the start
                const content = document.querySelector('.entry-content, .article-content, .content');
                if (content) {
                    // Try to find takeaway section
                    const allElements = content.querySelectorAll('p, li');
                    let inTakeaways = false;
                    let takeawayCount = 0;
                    
                    for (let el of allElements) {
                        const text = el.textContent.trim();
                        
                        // Check if this is the start of takeaways
                        if (text.toLowerCase().includes('key takeaway') || 
                            text.toLowerCase().includes('iran update')) {
                            inTakeaways = true;
                            continue;
                        }
                        
                        // Collect takeaways (usually bold/strong or bullet points)
                        if (inTakeaways && takeawayCount < 10) {
                            if (text.length > 50 && text.length < 500) {
                                result.takeaways.push(text);
                                takeawayCount++;
                            }
                        }
                        
                        // Stop if we hit a section header
                        if (text.includes('Forecast') || text.includes('Note:')) {
                            break;
                        }
                    }
                }
                
                // Get chart images
                const images = document.querySelectorAll('img');
                for (let img of images) {
                    const src = img.src || img.getAttribute('data-src');
                    if (src && (src.includes('uploads') || src.includes('wp-content'))) {
                        if (src.includes('.jpg') || src.includes('.png') || src.includes('.webp')) {
                            const caption = img.alt || img.title || '';
                            result.charts.push({
                                url: src,
                                caption: caption
                            });
                        }
                    }
                }
                
                return result;
            }
        """)
        
        await browser.close()
        return data

def save_data(data, url):
    """Save fetched data to JSON"""
    result = {
        "updated": datetime.now().isoformat(),
        "source_url": url,
        "current_report": {
            "url": url,
            "title": data.get('title', ''),
            "title_zh": simple_translate(data.get('title', '')),
            "date": data.get('date', datetime.now().strftime('%Y-%m-%d')),
            "takeaways": [],
            "charts": []
        }
    }
    
    # Process takeaways
    for i, takeaway in enumerate(data.get('takeaways', [])):
        result["current_report"]["takeaways"].append({
            "en": takeaway,
            "zh": simple_translate(takeaway)
        })
    
    # Process charts
    for chart in data.get('charts', []):
        result["current_report"]["charts"].append({
            "url": chart.get('url', ''),
            "title": chart.get('caption', 'Chart'),
            "title_zh": simple_translate(chart.get('caption', '图表')),
            "description": "ISW analysis chart",
            "description_zh": "ISW分析图表",
            "context": ["详细分析待补充"]
        })
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to {DATA_FILE}")
    return result

async def main():
    # Default URL - can be changed to fetch different reports
    url = "https://understandingwar.org/research/middle-east/iran-update-special-report-march-23-2026"
    
    data = await fetch_isw_report(url)
    if data:
        print(f"Found {len(data.get('takeaways', []))} takeaways")
        print(f"Found {len(data.get('charts', []))} charts")
        save_data(data, url)
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    asyncio.run(main())
