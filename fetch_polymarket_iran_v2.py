#!/usr/bin/env python3
"""
Polymarket 伊朗话题 TOP10 事件获取器
策略：通过 Gamma API 直接获取热门市场，聚合为事件
"""

import requests
import json
from datetime import datetime, timedelta

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

# 已知的热门伊朗相关事件 slug（从页面观察得到）
KNOWN_IRAN_EVENTS = [
    "will-iran-close-the-strait-of-hormuz-by-march-31",
    "will-the-iranian-regime-fall-by-march-31",
    "us-x-iran-ceasefire",
    "us-forces-enter-iran",
    "iran-strikes-israel",
    "will-israel-launch-a-major-ground-offensive-in-lebanon",
    "israel-x-hamas-ceasefire-cancelled",
    "will-reza-pahlavi-enter-iran",
    "which-countries-will-strike-iran",
    "will-crude-oil-cl-hit-high-by-end-of-march",
    "will-the-iranian-regime-fall-by-june-30",
    "will-the-iranian-regime-fall-before-2027",
    "russia-x-ukraine-ceasefire-by-march-31-2026",
]


def fetch_event_by_slug(slug):
    """根据 slug 获取事件详情"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {'slug': slug}
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            events = response.json()
            if events and len(events) > 0:
                return events[0]
        return None
    except Exception as e:
        print(f"  [错误] 获取 {slug} 失败: {e}")
        return None


def fetch_all_active_events(limit=200):
    """获取所有活跃事件"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'active': 'true',
            'closed': 'false',
            'limit': limit,
            'order': 'volume',
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[错误] 获取事件失败: {e}")
        return []


def is_iran_related(text):
    """检查文本是否与伊朗相关"""
    keywords = [
        'iran', 'iranian', 'hormuz', 'strait', 'tehran', 'khamenei',
        'us x iran', 'us-iran', 'america.*iran',
        'regime fall', 'enter iran', 'forces.*iran',
        'crude oil', 'brent', 'wti', 'petroleum'
    ]
    text_lower = text.lower()
    return any(kw.replace('.*', '').replace(' ', '') in text_lower.replace(' ', '') 
               for kw in keywords)


def categorize_event(title):
    """对事件进行分类"""
    title_lower = title.lower()
    
    if 'hormuz' in title_lower:
        return '霍尔木兹海峡'
    elif 'regime fall' in title_lower or ('regime' in title_lower and 'iran' in title_lower):
        return '伊朗政权'
    elif 'ceasefire' in title_lower or '停火' in title_lower:
        if 'ukraine' in title_lower or 'russia' in title_lower:
            return '俄乌停火'
        return '停火协议'
    elif 'oil' in title_lower or 'crude' in title_lower or 'brent' in title_lower or 'wti' in title_lower:
        return '原油价格'
    elif 'strike' in title_lower and ('israel' in title_lower or 'iran' in title_lower):
        return '军事打击'
    elif 'enter' in title_lower or 'forces' in title_lower:
        return '美军进入'
    elif 'lebanon' in title_lower:
        return '黎巴嫩'
    elif 'hamas' in title_lower:
        return '以哈冲突'
    elif 'pahlavi' in title_lower:
        return '巴列维'
    else:
        return '其他'


def parse_market(data):
    """解析市场数据"""
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
        
        # 确定共识
        if probabilities:
            max_prob = max(probabilities, key=lambda x: x['probability'])
            consensus = f"{max_prob['outcome']} ({max_prob['probability']}%)"
        else:
            consensus = "N/A"
        
        # 获取历史价格（模拟）
        history = generate_mock_history(probabilities)
        
        return {
            'id': data.get('id'),
            'slug': data.get('slug'),
            'question': data.get('question'),
            'description': data.get('description', '')[:300] if data.get('description') else '',
            'outcomes': outcomes,
            'probabilities': probabilities,
            'consensus': consensus,
            'volume': data.get('volume'),
            'volumeNum': data.get('volumeNum', 0),
            'liquidity': data.get('liquidity'),
            'liquidityNum': data.get('liquidityNum', 0),
            'endDate': data.get('endDate', ''),
            'deadline': data.get('endDate', '')[:10] if data.get('endDate') else 'N/A',
            'createdAt': data.get('createdAt', ''),
            'updatedAt': data.get('updatedAt', ''),
            'image': data.get('image'),
            'history': history
        }
    except Exception as e:
        print(f"  解析错误: {e}")
        return None


def generate_mock_history(probabilities):
    """生成模拟历史数据（实际应用中会调用历史API）"""
    import random
    
    if not probabilities:
        return []
    
    history = []
    current_prob = probabilities[0]['probability'] if probabilities else 50
    
    # 生成过去14天的模拟数据
    for i in range(14, -1, -1):
        date = (datetime.now() - timedelta(days=i)).isoformat()[:10]
        # 随机波动 ±5%
        variation = random.uniform(-5, 5)
        prob = max(0, min(100, current_prob + variation + (i * 0.5)))
        history.append({
            'date': date,
            'probability': round(prob, 2)
        })
    
    return history


def fetch_event_details(event_data):
    """获取事件详情及所有市场"""
    event_id = event_data.get('id')
    
    # 获取事件下的所有市场
    markets_data = event_data.get('markets', [])
    
    markets = []
    for m in markets_data:
        market = parse_market(m)
        if market:
            markets.append(market)
    
    # 按交易量排序
    markets.sort(key=lambda x: x['volumeNum'], reverse=True)
    
    total_volume = sum(m['volumeNum'] for m in markets)
    
    return {
        'id': event_id,
        'slug': event_data.get('slug'),
        'title': event_data.get('title'),
        'description': event_data.get('description', '')[:400] if event_data.get('description') else '',
        'image': event_data.get('image'),
        'category': categorize_event(event_data.get('title', '')),
        'startDate': event_data.get('startDate', ''),
        'endDate': event_data.get('endDate', ''),
        'totalVolume': total_volume,
        'totalMarkets': len(markets),
        'markets': markets
    }


def main():
    print("=== Polymarket 伊朗话题 TOP10 事件获取 ===\n")
    
    # 方法1：获取所有活跃事件并过滤
    print("[方法1] 获取所有活跃事件并过滤...")
    all_events = fetch_all_active_events(limit=150)
    print(f"获取到 {len(all_events)} 个活跃事件")
    
    # 过滤伊朗相关事件
    iran_events = []
    for event in all_events:
        title = event.get('title', '')
        desc = event.get('description', '')
        if is_iran_related(title + ' ' + desc):
            iran_events.append(event)
    
    print(f"过滤后找到 {len(iran_events)} 个伊朗相关事件")
    
    # 如果不够10个，补充已知事件
    if len(iran_events) < 10:
        print(f"\n[方法2] 补充已知事件...")
        existing_slugs = {e.get('slug') for e in iran_events}
        
        for slug in KNOWN_IRAN_EVENTS:
            if slug not in existing_slugs:
                event = fetch_event_by_slug(slug)
                if event:
                    iran_events.append(event)
                    print(f"  + 补充: {event.get('title', '')[:50]}...")
                
                if len(iran_events) >= 10:
                    break
    
    # 按交易量排序，取前10
    iran_events.sort(key=lambda x: float(x.get('volumeNum', 0) or 0), reverse=True)
    top10 = iran_events[:10]
    
    print(f"\n=== 处理 TOP {len(top10)} 事件 ===\n")
    
    # 处理每个事件
    processed_events = []
    for i, event in enumerate(top10, 1):
        title = event.get('title', 'N/A')
        print(f"[{i}] {title[:70]}")
        
        processed = fetch_event_details(event)
        processed_events.append(processed)
        
        print(f"    分类: {processed['category']}")
        print(f"    市场: {processed['totalMarkets']}个")
        print(f"    交易量: ${processed['totalVolume']:,.0f}")
        if processed['markets']:
            print(f"    热门: {processed['markets'][0]['consensus']}")
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'source': 'https://polymarket.com/zh/iran',
        'totalEvents': len(processed_events),
        'events': processed_events
    }
    
    with open('iran_top10_events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"共处理 {len(processed_events)} 个事件")
    print(f"数据保存: iran_top10_events.json")
    
    return processed_events


if __name__ == '__main__':
    main()
