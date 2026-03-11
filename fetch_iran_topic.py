#!/usr/bin/env python3
"""
获取 Polymarket 伊朗话题下的热门预测市场
"""

import requests
import json
from datetime import datetime

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

def get_tags():
    """获取所有标签列表"""
    try:
        url = f"{GAMMA_API_BASE}/tags"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取标签失败: {e}")
        return []

def get_markets_by_tag(tag_id, limit=20):
    """通过标签ID获取市场"""
    try:
        url = f"{GAMMA_API_BASE}/markets"
        params = {
            'tag_id': tag_id,
            'active': 'true',
            'closed': 'false',
            'limit': limit,
            'order': 'volumeNum',  # 按交易量排序
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取市场失败: {e}")
        return []

def get_events_by_tag(tag_id, limit=20):
    """通过标签ID获取事件（话题）"""
    try:
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'tag_id': tag_id,
            'active': 'true',
            'closed': 'false',
            'limit': limit,
            'order': 'volume',
            'ascending': 'false'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取事件失败: {e}")
        return []

def parse_market(data):
    """解析市场数据"""
    try:
        outcome_prices_str = data.get('outcomePrices', '[]')
        if isinstance(outcome_prices_str, str):
            outcome_prices = json.loads(outcome_prices_str)
        else:
            outcome_prices = outcome_prices_str
        
        outcomes_str = data.get('outcomes', '[]')
        if isinstance(outcomes_str, str):
            outcomes = json.loads(outcomes_str)
        else:
            outcomes = outcomes_str
        
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
            'description': data.get('description', '')[:150] + '...' if data.get('description') else '',
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
        print(f"解析失败: {e}")
        return None

def main():
    print("=== 查找伊朗话题标签 ===\n")
    
    # 1. 获取所有标签，查找伊朗
    tags = get_tags()
    iran_tag = None
    
    for tag in tags:
        tag_name = tag.get('label', '').lower()
        if 'iran' in tag_name or '伊朗' in tag_name:
            iran_tag = tag
            print(f"找到标签: {tag.get('label')} (ID: {tag.get('id')})")
            break
    
    if not iran_tag:
        print("未找到伊朗标签，尝试搜索...")
        # 尝试常见ID
        # Politics 通常是 2, Crypto 是 21
        # 尝试一些可能的ID
        for test_id in [2, 21, 100639, 1401, 596]:
            markets = get_markets_by_tag(test_id, limit=5)
            if markets:
                print(f"ID {test_id} 有 {len(markets)} 个市场")
                for m in markets[:2]:
                    print(f"  - {m.get('question', '')[:50]}")
    
    if iran_tag:
        tag_id = iran_tag.get('id')
        print(f"\n=== 获取伊朗话题市场 (Tag ID: {tag_id}) ===\n")
        
        # 获取市场
        markets_data = get_markets_by_tag(tag_id, limit=20)
        markets = []
        for m in markets_data:
            parsed = parse_market(m)
            if parsed:
                markets.append(parsed)
        
        # 保存数据
        output = {
            'updatedAt': datetime.now().isoformat(),
            'tag': iran_tag.get('label'),
            'tagId': tag_id,
            'totalMarkets': len(markets),
            'markets': markets
        }
        
        with open('iran_topic_markets.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"成功获取 {len(markets)} 个市场")
        print(f"数据已保存到: iran_topic_markets.json\n")
        
        # 打印摘要
        print("=== 热门预测 TOP 10 ===")
        for i, m in enumerate(markets[:10], 1):
            print(f"{i}. {m['question'][:70]}")
            print(f"   共识: {m['consensus']}")
            print(f"   交易量: ${m['volumeNum']:,.0f}")
            print()

if __name__ == '__main__':
    main()
