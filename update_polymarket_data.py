#!/usr/bin/env python3
"""
自动更新 Polymarket 伊朗话题数据
可以设置为定时任务（如每小时运行一次）
"""

import requests
import json
from datetime import datetime
import os

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

def is_iran_related(text):
    """检查文本是否与伊朗/中东相关"""
    keywords = [
        'iran', 'iranian', 'hormuz', 'strait', 'tehran',
        'israel', 'gaza', 'palestine', 'hamas', 'hezbollah',
        'middle east', 'saudi', 'yemen', 'houthis',
        'oil', 'crude', 'petroleum',
        'netanyahu', 'khamenei'
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def get_events():
    """获取活跃事件"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'active': 'true',
            'closed': 'false',
            'limit': 100,
            'order': 'volume',
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[错误] 获取事件失败: {e}")
        return []

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

def update_data():
    """更新数据主函数"""
    print(f"[{datetime.now()}] 开始更新 Polymarket 数据...")
    
    events = get_events()
    
    # 过滤伊朗相关事件
    iran_events = []
    for event in events:
        title = event.get('title', '')
        slug = event.get('slug', '')
        description = event.get('description', '')
        if is_iran_related(title + ' ' + slug + ' ' + description):
            iran_events.append(event)
    
    print(f"[信息] 找到 {len(iran_events)} 个伊朗相关事件")
    
    # 提取市场
    all_markets = []
    seen_slugs = set()
    
    for event in iran_events:
        markets_data = event.get('markets', [])
        for m in markets_data:
            slug = m.get('slug')
            if slug and slug not in seen_slugs:
                market = parse_market(m)
                if market:
                    all_markets.append(market)
                    seen_slugs.add(slug)
    
    # 按交易量排序
    all_markets.sort(key=lambda x: x['volumeNum'], reverse=True)
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'topic': 'Iran/Middle East',
        'totalEvents': len(iran_events),
        'totalMarkets': len(all_markets),
        'markets': all_markets[:20]
    }
    
    # 保存到多个位置供网页使用
    files_to_save = [
        'iran_top20.json',
        'polymarket_data.json'
    ]
    
    for filename in files_to_save:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"[成功] 数据已保存到 {filename}")
        except Exception as e:
            print(f"[错误] 保存 {filename} 失败: {e}")
    
    print(f"[{datetime.now()}] 更新完成！共 {len(all_markets)} 个市场，保存前20")
    
    # 打印 TOP 5
    print("\n=== TOP 5 市场 ===")
    for i, m in enumerate(all_markets[:5], 1):
        print(f"{i}. {m['question'][:60]}")
        print(f"   概率: {m['consensus']}, 交易量: ${m['volumeNum']:,.0f}")

if __name__ == '__main__':
    update_data()
