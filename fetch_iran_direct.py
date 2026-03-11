#!/usr/bin/env python3
"""
直接获取 Polymarket 伊朗相关热门市场
通过多种方式尝试获取
"""

import requests
import json
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

# 已知的伊朗相关市场 slugs（根据之前搜索结果和常见市场）
IRAN_MARKET_SLUGS = [
    "will-iran-close-the-strait-of-hormuz-by-march-31",
    "will-iran-close-the-strait-of-hormuz-by-june-30", 
    "will-iran-close-the-strait-of-hormuz-before-2027",
    "will-the-us-iran-war-end-by-april",
    "will-iran-strike-israel-by-march-31",
    "will-the-us-strike-iran-by-march-31",
    "will-irans-supreme-leader-be-removed-by-march-31",
    "will-iran-announce-a-nuclear-test-by-march-31",
    "will-israel-strike-iran-by-march-31",
    "will-there-be-a-ceasefire-in-gaza-by-march-31",
    "will-saudi-arabia-normalize-relations-with-israel-by-march-31",
    "will-hezbollah-strike-israel-by-march-31",
    "will-yemen-houthis-strike-a-us-ship-by-march-31",
    "will-egypt-join-the-conflict-by-march-31",
    "will-jordan-join-the-conflict-by-march-31",
    "will-lebanon-join-the-conflict-by-march-31",
    "will-the-us-deploy-ground-troops-to-the-middle-east-by-march-31",
    "will-oil-prices-hit-120-by-march-31",
    "will-oil-prices-hit-130-by-march-31",
    "will-the-un-impose-sanctions-on-iran-by-march-31",
]

def fetch_market_by_slug(slug):
    """通过 slug 获取市场"""
    try:
        url = f"{GAMMA_API_BASE}/markets"
        params = {'slug': slug}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
        return None
    except:
        return None

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
        
        # 提取标签
        tags = data.get('tags', [])
        tag_names = [t.get('label', '') for t in tags] if isinstance(tags, list) else []
        
        return {
            'id': data.get('id'),
            'slug': data.get('slug'),
            'question': data.get('question'),
            'description': data.get('description', '')[:200] + '...' if data.get('description') else '',
            'conditionId': data.get('conditionId'),
            'outcomes': outcomes,
            'probabilities': probabilities,
            'consensus': consensus,
            'volume': data.get('volume'),
            'volumeNum': data.get('volumeNum', 0),
            'liquidity': data.get('liquidity'),
            'liquidityNum': data.get('liquidityNum', 0),
            'endDate': data.get('endDate'),
            'startDate': data.get('startDate'),
            'image': data.get('image'),
            'tags': tag_names,
            'active': data.get('active', False),
            'updatedAt': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"解析错误: {e}")
        return None

def main():
    print("=== 获取 Polymarket 伊朗相关市场 ===\n")
    
    all_markets = []
    success_count = 0
    
    for slug in IRAN_MARKET_SLUGS:
        print(f"获取: {slug[:50]}...", end=" ")
        data = fetch_market_by_slug(slug)
        if data:
            market = parse_market(data)
            if market:
                all_markets.append(market)
                success_count += 1
                print(f"[OK] - {market['question'][:40]}")
        else:
            print("[未找到]")
    
    # 按交易量排序
    all_markets.sort(key=lambda x: x['volumeNum'], reverse=True)
    
    # 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'topic': 'Iran/Middle East',
        'totalMarkets': len(all_markets),
        'markets': all_markets
    }
    
    with open('iran_topic_top20.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"成功获取: {success_count} 个市场")
    print(f"数据保存: iran_topic_top20.json\n")
    
    # 打印 TOP 20
    print("=== TOP 20 伊朗相关预测市场 ===\n")
    for i, m in enumerate(all_markets[:20], 1):
        print(f"{i}. {m['question']}")
        print(f"   概率: {m['consensus']}")
        print(f"   交易量: ${m['volumeNum']:,.0f}")
        print(f"   截止: {m['endDate'][:10]}")
        print()

if __name__ == '__main__':
    main()
