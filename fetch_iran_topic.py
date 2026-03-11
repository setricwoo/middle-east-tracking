#!/usr/bin/env python3
"""
获取 Polymarket 伊朗话题 (https://polymarket.com/zh/iran) 下的热门事件
并获取每个事件下的所有市场数据
"""

import requests
import json
import re
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

# 伊朗话题下的热门 Event IDs（通过网页分析获得）
# 可以通过访问 https://gamma-api.polymarket.com/events?active=true&tag_id=2&limit=20 获取政治类热门事件
IRAN_EVENT_SLUGS = [
    "will-iran-close-the-strait-of-hormuz",  # 伊朗关闭霍尔木兹海峡
    "will-the-iranian-regime-fall",           # 伊朗政权倒台
    "us-x-iran-ceasefire",                    # 美伊停火
    "us-forces-enter-iran",                   # 美军进入伊朗
    "iran-strikes-israel",                    # 伊朗袭击以色列
    "will-israel-launch-a-major-ground-offensive-in-lebanon",  # 以色列地面进攻黎巴嫩
    "israel-x-hamas-ceasefire-cancelled",     # 以哈停火取消
    "will-reza-pahlavi-enter-iran",           # 礼萨·巴列维进入伊朗
    "which-countries-will-strike-iran",       # 哪些国家会袭击伊朗
    "will-crude-oil-cl-hit-high-by-end-of-march",  # 原油价格
]

def get_event_by_slug(slug):
    """通过 slug 获取事件详情"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {'slug': slug}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
        return None
    except Exception as e:
        print(f"[错误] 获取事件 {slug} 失败: {e}")
        return None

def get_event_markets(event_id):
    """获取事件下的所有市场"""
    try:
        url = f"{GAMMA_API_BASE}/markets"
        params = {
            'event_id': event_id,
            'active': 'true',
            'limit': 20
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[错误] 获取市场失败: {e}")
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
        
        # 提取截止日期（从标题或 endDate）
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
            'updatedAt': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[警告] 解析市场失败: {e}")
        return None

def main():
    print("=== 获取 Polymarket 伊朗话题热门事件 ===\n")
    
    all_events = []
    
    for slug in IRAN_EVENT_SLUGS:
        print(f"获取事件: {slug}...", end=" ")
        
        event = get_event_by_slug(slug)
        if not event:
            print("[未找到]")
            continue
        
        event_title = event.get('title', 'N/A')
        event_id = event.get('id')
        
        print(f"[OK] {event_title[:50]}")
        
        # 获取该事件下的所有市场
        markets_data = event.get('markets', [])
        if not markets_data and event_id:
            markets_data = get_event_markets(event_id)
        
        markets = []
        for m in markets_data:
            market = parse_market(m)
            if market:
                markets.append(market)
        
        # 按交易量排序
        markets.sort(key=lambda x: x['volumeNum'], reverse=True)
        
        # 计算事件总交易量
        total_volume = sum(m['volumeNum'] for m in markets)
        
        event_summary = {
            'id': event_id,
            'slug': slug,
            'title': event_title,
            'description': event.get('description', '')[:200] + '...' if event.get('description') else '',
            'image': event.get('image'),
            'totalVolume': total_volume,
            'totalMarkets': len(markets),
            'markets': markets
        }
        
        all_events.append(event_summary)
        print(f"       包含 {len(markets)} 个市场, 总交易量: ${total_volume:,.0f}")
    
    # 按总交易量排序事件
    all_events.sort(key=lambda x: x['totalVolume'], reverse=True)
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'topic': 'Iran',
        'totalEvents': len(all_events),
        'events': all_events
    }
    
    with open('iran_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"共获取 {len(all_events)} 个事件")
    print(f"数据保存: iran_events.json\n")
    
    # 打印摘要
    print("=== 热门事件摘要 ===\n")
    for i, event in enumerate(all_events[:10], 1):
        print(f"{i}. {event['title']}")
        print(f"   市场数: {event['totalMarkets']}, 总交易量: ${event['totalVolume']:,.0f}")
        if event['markets']:
            print(f"   主要预测: {event['markets'][0]['consensus']}")
        print()

if __name__ == '__main__':
    main()
