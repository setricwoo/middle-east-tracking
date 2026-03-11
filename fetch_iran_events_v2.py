#!/usr/bin/env python3
"""
获取 Polymarket 伊朗话题下的热门事件
策略：获取所有活跃事件，过滤出伊朗/中东相关的
"""

import requests
import json
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

def get_all_active_events(limit=100):
    """获取所有活跃事件"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'active': 'true',
            'closed': 'false',
            'limit': limit,
            'order': 'volume',  # 按交易量排序
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[错误] 获取事件失败: {e}")
        return []

def is_iran_related(text):
    """检查文本是否与伊朗/中东相关"""
    keywords = [
        'iran', 'iranian', 'hormuz', 'strait', 'tehran',
        'israel', 'gaza', 'palestine', 'hamas', 'hezbollah',
        'middle east', 'saudi', 'yemen', 'houthis', 'lebanon',
        'oil', 'crude', 'petroleum', 'wti', 'brent',
        'netanyahu', 'khamenei', 'pahlavi',
        'ceasefire', 'regime fall'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def parse_market(data):
    """解析市场数据"""
    try:
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
            prob = {
                'outcome': outcome_name,
                'price': float(price),
                'probability': round(float(price) * 100, 2)
            }
            probabilities.append(prob)
        
        if probabilities:
            max_prob = max(probabilities, key=lambda x: x['probability'])
            consensus = f"{max_prob['outcome']} ({max_prob['probability']}%)"
        else:
            consensus = "N/A"
        
        end_date = data.get('endDate', '')
        deadline = end_date[:10] if end_date else 'N/A'
        
        return {
            'id': data.get('id'),
            'slug': data.get('slug'),
            'question': data.get('question'),
            'outcomes': outcomes,
            'probabilities': probabilities,
            'consensus': consensus,
            'volume': data.get('volume'),
            'volumeNum': data.get('volumeNum', 0),
            'liquidity': data.get('liquidity'),
            'endDate': end_date,
            'deadline': deadline,
            'image': data.get('image'),
        }
    except Exception as e:
        return None

def categorize_event(title):
    """对事件进行分类"""
    title_lower = title.lower()
    
    if 'hormuz' in title_lower:
        return '霍尔木兹海峡'
    elif 'regime fall' in title_lower or 'regime' in title_lower:
        return '伊朗政权'
    elif 'ceasefire' in title_lower or '停火' in title_lower:
        return '停火协议'
    elif 'oil' in title_lower or 'crude' in title_lower or 'wti' in title_lower:
        return '原油价格'
    elif 'strike' in title_lower and 'israel' in title_lower:
        return '伊朗袭击以色列'
    elif 'enter iran' in title_lower or 'forces' in title_lower:
        return '美军进入伊朗'
    elif 'lebanon' in title_lower:
        return '黎巴嫩'
    elif 'hamas' in title_lower:
        return '以哈冲突'
    elif 'pahlavi' in title_lower:
        return '巴列维'
    else:
        return '其他'

def main():
    print("=== 获取 Polymarket 活跃事件 ===\n")
    
    events = get_all_active_events(limit=100)
    print(f"获取到 {len(events)} 个活跃事件\n")
    
    # 过滤伊朗相关事件
    iran_events = []
    for event in events:
        title = event.get('title', '')
        description = event.get('description', '')
        
        if is_iran_related(title + ' ' + description):
            category = categorize_event(title)
            iran_events.append({
                'event': event,
                'category': category,
                'relevance_score': 0
            })
    
    print(f"过滤后找到 {len(iran_events)} 个伊朗相关事件\n")
    
    # 处理每个事件
    processed_events = []
    
    for item in iran_events:
        event = item['event']
        category = item['category']
        
        title = event.get('title', 'N/A')
        print(f"处理: {title[:60]}...")
        
        # 获取市场
        markets_data = event.get('markets', [])
        markets = []
        
        for m in markets_data:
            market = parse_market(m)
            if market:
                markets.append(market)
        
        # 按交易量排序
        markets.sort(key=lambda x: x['volumeNum'], reverse=True)
        
        total_volume = sum(m['volumeNum'] for m in markets)
        
        processed_events.append({
            'id': event.get('id'),
            'slug': event.get('slug'),
            'title': title,
            'description': event.get('description', '')[:300] + '...' if event.get('description') else '',
            'category': category,
            'image': event.get('image'),
            'totalVolume': total_volume,
            'totalMarkets': len(markets),
            'markets': markets
        })
        
        print(f"       分类: {category}, 市场: {len(markets)}, 交易量: ${total_volume:,.0f}")
    
    # 按总交易量排序
    processed_events.sort(key=lambda x: x['totalVolume'], reverse=True)
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'topic': 'Iran/Middle East',
        'totalEvents': len(processed_events),
        'events': processed_events
    }
    
    with open('iran_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"共处理 {len(processed_events)} 个事件")
    print(f"数据保存: iran_events.json\n")
    
    # 按分类统计
    categories = {}
    for e in processed_events:
        cat = e['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(e)
    
    print("=== 按分类统计 ===")
    for cat, events in sorted(categories.items(), key=lambda x: sum(e['totalVolume'] for e in x[1]), reverse=True):
        print(f"{cat}: {len(events)} 个事件")
    
    print("\n=== TOP 10 热门事件 ===\n")
    for i, e in enumerate(processed_events[:10], 1):
        print(f"{i}. [{e['category']}] {e['title'][:70]}")
        print(f"   市场: {e['totalMarkets']}个, 交易量: ${e['totalVolume']:,.0f}")
        if e['markets']:
            print(f"   最高概率: {e['markets'][0]['consensus']}")

if __name__ == '__main__':
    main()
