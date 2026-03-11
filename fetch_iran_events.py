#!/usr/bin/env python3
"""
获取 Polymarket 伊朗话题下的热门事件（Events）
一个事件可能包含多个相关市场
"""

import requests
import json
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

def get_iran_events():
    """获取活跃事件，过滤伊朗相关的"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'active': 'true',
            'closed': 'false',
            'limit': 100,  # 获取较多事件以便过滤
            'order': 'volume',
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取事件失败: {e}")
        return []

def get_markets_by_condition(condition_id):
    """通过 condition_id 获取市场"""
    try:
        url = f"{GAMMA_API_BASE}/markets"
        params = {
            'condition_id': condition_id,
            'active': 'true',
            'limit': 10
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return []

def is_iran_related(text):
    """检查文本是否与伊朗/中东相关"""
    keywords = [
        'iran', 'iranian', 'hormuz', 'strait', 'tehran',
        'israel', 'gaza', 'palestine', 'hamas', 'hezbollah',
        'middle east', 'saudi', 'yemen', 'houthis',
        'oil', 'crude', 'petroleum',
        ' Netanyahu', 'khamenei'
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
        
        return {
            'id': data.get('id'),
            'slug': data.get('slug'),
            'question': data.get('question'),
            'description': data.get('description', '')[:200] + '...' if data.get('description') else '',
            'outcomes': outcomes,
            'probabilities': probabilities,
            'consensus': consensus,
            'volume': data.get('volume'),
            'volumeNum': data.get('volumeNum', 0),
            'liquidity': data.get('liquidity'),
            'endDate': data.get('endDate'),
            'image': data.get('image'),
            'updatedAt': datetime.now().isoformat()
        }
    except Exception as e:
        return None

def main():
    print("=== 获取 Polymarket 活跃事件 ===\n")
    
    events = get_iran_events()
    print(f"获取到 {len(events)} 个活跃事件\n")
    
    # 过滤伊朗/中东相关事件
    iran_events = []
    for event in events:
        title = event.get('title', '')
        slug = event.get('slug', '')
        description = event.get('description', '')
        
        if is_iran_related(title + ' ' + slug + ' ' + description):
            iran_events.append(event)
    
    print(f"过滤后找到 {len(iran_events)} 个伊朗/中东相关事件\n")
    
    # 从事件中提取市场
    all_markets = []
    seen_slugs = set()
    
    for event in iran_events:
        print(f"处理事件: {event.get('title', 'N/A')[:60]}")
        
        # 获取事件下的市场
        markets_data = event.get('markets', [])
        
        if not markets_data and event.get('conditionId'):
            # 如果没有嵌入市场，尝试通过 condition_id 获取
            markets_data = get_markets_by_condition(event.get('conditionId'))
        
        for m in markets_data:
            slug = m.get('slug')
            if slug and slug not in seen_slugs:
                market = parse_market(m)
                if market:
                    all_markets.append(market)
                    seen_slugs.add(slug)
                    print(f"  + {market['question'][:50]}")
    
    # 按交易量排序
    all_markets.sort(key=lambda x: x['volumeNum'], reverse=True)
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'topic': 'Iran/Middle East',
        'totalEvents': len(iran_events),
        'totalMarkets': len(all_markets),
        'markets': all_markets[:20]  # 只保留前20
    }
    
    with open('iran_top20.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"共找到 {len(all_markets)} 个市场")
    print(f"保存前20到: iran_top20.json\n")
    
    # 打印 TOP 20
    print("=== TOP 20 伊朗相关预测市场 ===\n")
    for i, m in enumerate(all_markets[:20], 1):
        print(f"{i}. {m['question']}")
        print(f"   概率: {m['consensus']}")
        print(f"   交易量: ${m['volumeNum']:,.0f}")
        print()

if __name__ == '__main__':
    main()
