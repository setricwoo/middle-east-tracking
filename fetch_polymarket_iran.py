#!/usr/bin/env python3
"""
使用 Playwright 访问 Polymarket Iran 页面，获取前10个事件及其子市场
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

async def fetch_iran_events():
    """获取前10个事件及其子市场"""
    
    events_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        try:
            print("正在访问 https://polymarket.com/zh/iran ...")
            await page.goto('https://polymarket.com/zh/iran', wait_until='networkidle')
            await asyncio.sleep(3)  # 等待页面加载
            
            # 获取前10个事件链接
            print("获取事件列表...")
            event_links = await page.evaluate('''() => {
                const links = [];
                const eventCards = document.querySelectorAll('a[href^="/event/"]');
                eventCards.forEach(card => {
                    const href = card.getAttribute('href');
                    const slug = href.replace('/event/', '');
                    if (!links.find(l => l.slug === slug)) {
                        const titleEl = card.querySelector('h2, h3, .title, [class*="title"]');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        links.push({slug, href, title});
                    }
                });
                return links.slice(0, 10);
            }''')
            
            print(f"找到 {len(event_links)} 个事件")
            
            # 遍历每个事件，点击进入获取子市场
            for i, event_info in enumerate(event_links, 1):
                try:
                    print(f"\n[{i}/10] 处理事件: {event_info['title'][:50]}...")
                    
                    # 点击事件进入详情页
                    await page.goto(f"https://polymarket.com{event_info['href']}", wait_until='networkidle')
                    await asyncio.sleep(2)
                    
                    # 获取事件详情
                    event_detail = await page.evaluate('''() => {
                        const titleEl = document.querySelector('h1, [class*="title"], .event-title');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        
                        const descEl = document.querySelector('[class*="description"], .description, p');
                        const description = descEl ? descEl.textContent.trim() : '';
                        
                        // 获取市场列表
                        const markets = [];
                        const marketCards = document.querySelectorAll('[class*="market"], [data-testid*="market"], a[href*="market"], .outcome-card');
                        
                        marketCards.forEach(card => {
                            const questionEl = card.querySelector('h3, h4, [class*="question"], [class*="title"]');
                            const question = questionEl ? questionEl.textContent.trim() : '';
                            
                            // 获取概率
                            const probEl = card.querySelector('[class*="probability"], [class*="percent"], [class*="odds"]');
                            const probability = probEl ? probEl.textContent.trim() : '';
                            
                            // 获取市场链接
                            const marketHref = card.getAttribute('href') || '';
                            const marketSlug = marketHref.replace('/market/', '').split('?')[0];
                            
                            if (question) {
                                markets.push({question, probability, marketSlug});
                            }
                        });
                        
                        return {title, description, markets};
                    }''')
                    
                    # 合并数据
                    event_data = {
                        'slug': event_info['slug'],
                        'title': event_detail.get('title') or event_info['title'],
                        'description': event_detail.get('description', ''),
                        'markets': event_detail.get('markets', []),
                        'index': i
                    }
                    
                    events_data.append(event_data)
                    print(f"       找到 {len(event_data['markets'])} 个子市场")
                    
                except Exception as e:
                    print(f"       [错误] {e}")
                    continue
            
        finally:
            await browser.close()
    
    return events_data


def fetch_market_data_from_api(slug):
    """从 Gamma API 获取市场详细数据"""
    import requests
    
    try:
        # 先搜索获取 market ID
        url = f"{GAMMA_API_BASE}/markets"
        params = {'slug': slug, 'active': 'true'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            markets = response.json()
            if markets and len(markets) > 0:
                market = markets[0]
                return parse_market_detail(market)
        
        return None
    except Exception as e:
        print(f"       API 获取失败: {e}")
        return None


def parse_market_detail(data):
    """解析市场详细数据"""
    try:
        # 解析概率
        outcome_prices_str = data.get('outcomePrices', '[]')
        if isinstance(outcome_prices_str, str):
            outcome_prices = json.loads(outcome_prices_str)
        else:
            outcome_prices = outcome_prices_str or []
        
        outcomes_str = data.get('outcomes', '[]')
        if isinstance(outcomes_str, str):
            outcomes = json.loads(outcomes_str)
        else:
            outcomes = outcomes_str or []
        
        probabilities = []
        for i, price in enumerate(outcome_prices):
            outcome_name = outcomes[i] if i < len(outcomes) else f'Option {i+1}'
            probabilities.append({
                'outcome': outcome_name,
                'price': float(price),
                'probability': round(float(price) * 100, 2)
            })
        
        # 确定共识结果
        if probabilities:
            max_prob = max(probabilities, key=lambda x: x['probability'])
            consensus = f"{max_prob['outcome']} ({max_prob['probability']}%)"
        else:
            consensus = "N/A"
        
        # 解析历史数据（如果有）
        history = []
        
        return {
            'id': data.get('id'),
            'slug': data.get('slug'),
            'question': data.get('question'),
            'description': data.get('description', '')[:200],
            'probabilities': probabilities,
            'consensus': consensus,
            'volume': data.get('volume'),
            'volumeNum': data.get('volumeNum', 0),
            'liquidity': data.get('liquidity'),
            'endDate': data.get('endDate', '')[:10] if data.get('endDate') else 'N/A',
            'createdAt': data.get('createdAt', ''),
            'updatedAt': data.get('updatedAt', ''),
            'history': history
        }
    except Exception as e:
        print(f"解析错误: {e}")
        return None


def fetch_price_history(market_id, slug):
    """获取价格历史数据"""
    import requests
    
    try:
        # 尝试获取价格历史
        url = f"{GAMMA_API_BASE}/history"
        params = {'market': slug, 'interval': '1d'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            history = []
            for point in data.get('history', [])[:30]:  # 最近30个点
                history.append({
                    'timestamp': point.get('timestamp'),
                    'price': point.get('price'),
                    'volume': point.get('volume')
                })
            return history
        
        return []
    except:
        return []


async def main():
    print("=== Polymarket 伊朗话题 TOP10 事件获取 ===\n")
    
    # 1. 获取事件列表
    events = await fetch_iran_events()
    print(f"\n成功获取 {len(events)} 个事件")
    
    # 2. 获取每个市场的详细数据
    print("\n正在获取市场详细数据...")
    enriched_events = []
    
    for event in events:
        print(f"\n处理: {event['title'][:60]}...")
        
        enriched_markets = []
        for market in event.get('markets', []):
            slug = market.get('marketSlug', '')
            if not slug:
                # 尝试从问题文本构建 slug
                continue
            
            # 获取 API 数据
            api_data = fetch_market_data_from_api(slug)
            if api_data:
                # 获取历史数据
                if api_data.get('id'):
                    history = fetch_price_history(api_data['id'], slug)
                    api_data['priceHistory'] = history
                
                enriched_markets.append(api_data)
                print(f"  ✓ {api_data['question'][:50]}... - {api_data['consensus']}")
            else:
                # 使用页面抓取的数据
                enriched_markets.append({
                    'question': market.get('question', 'N/A'),
                    'consensus': market.get('probability', 'N/A'),
                    'probabilities': [],
                    'volume': 0
                })
                print(f"  ⚠ 使用页面数据: {market.get('question', 'N/A')[:50]}...")
        
        # 按交易量排序
        enriched_markets.sort(key=lambda x: x.get('volumeNum', 0), reverse=True)
        
        event['markets'] = enriched_markets
        event['totalVolume'] = sum(m.get('volumeNum', 0) for m in enriched_markets)
        event['totalMarkets'] = len(enriched_markets)
        
        enriched_events.append(event)
    
    # 3. 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'source': 'https://polymarket.com/zh/iran',
        'totalEvents': len(enriched_events),
        'events': enriched_events
    }
    
    with open('iran_top10_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"共处理 {len(enriched_events)} 个事件")
    print(f"数据保存: iran_top10_events.json")
    
    # 打印摘要
    print("\n=== TOP10 事件摘要 ===")
    for i, e in enumerate(enriched_events, 1):
        print(f"\n{i}. {e['title'][:70]}")
        print(f"   市场数: {e['totalMarkets']}, 总交易量: ${e['totalVolume']:,.0f}")
        if e['markets']:
            print(f"   热门: {e['markets'][0]['question'][:60]}...")
            print(f"   共识: {e['markets'][0]['consensus']}")


if __name__ == '__main__':
    asyncio.run(main())
