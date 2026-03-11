#!/usr/bin/env python3
"""
Polymarket Gamma API 数据获取脚本
获取中东地缘相关预测市场的概率数据
"""

import requests
import json
import os
from datetime import datetime

# API 基础配置
GAMMA_API_BASE = "https://gamma-api.polymarket.com"
CLOB_API_BASE = "https://clob.polymarket.com"

# 搜索关键词（中东地缘相关）
SEARCH_QUERIES = [
    "iran hormuz",
    "iran war", 
    "israel iran",
    "strait of hormuz",
    "middle east",
    "oil price"
]

# 已知的热门市场 Slug（可以手动添加确认的市场）
KNOWN_MARKETS = [
    "will-iran-close-the-strait-of-hormuz-by-march-31",  # 3月31日关闭海峡
    "will-iran-close-the-strait-of-hormuz-by-june-30",   # 6月30日关闭海峡
    "will-iran-close-the-strait-of-hormuz-before-2027",  # 年底前关闭海峡
    "will-crude-oil-cl-wti-hit-100-by-end-of-march",     # 油价$100
    "will-crude-oil-cl-wti-hit-110-by-end-of-march",     # 油价$110
    "will-the-us-iran-war-end-by-april",                 # 战争4月前结束
]

class PolymarketFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_market_by_slug(self, slug):
        """通过 slug 获取特定市场数据"""
        try:
            url = f"{GAMMA_API_BASE}/markets"
            params = {'slug': slug}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                return self._parse_market(data[0])
            return None
        except Exception as e:
            print(f"[错误] 获取市场 {slug} 失败: {e}")
            return None
    
    def search_markets(self, query, limit=10):
        """搜索市场"""
        try:
            url = f"{GAMMA_API_BASE}/search"
            params = {'query': query, 'limit': limit}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            markets = []
            for item in data:
                market = self._parse_market(item)
                if market:
                    markets.append(market)
            return markets
        except Exception as e:
            print(f"[错误] 搜索 '{query}' 失败: {e}")
            return []
    
    def get_active_markets(self, tag_id=None, limit=50):
        """获取活跃市场列表"""
        try:
            url = f"{GAMMA_API_BASE}/markets"
            params = {
                'active': 'true',
                'closed': 'false',
                'limit': limit,
                'order': 'volumeNum',
                'ascending': 'false'
            }
            if tag_id:
                params['tag_id'] = tag_id
                
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            markets = []
            for item in data:
                market = self._parse_market(item)
                if market:
                    markets.append(market)
            return markets
        except Exception as e:
            print(f"[错误] 获取活跃市场失败: {e}")
            return []
    
    def _parse_market(self, data):
        """解析市场数据，提取关键字段"""
        try:
            # 获取 outcomePrices（概率）
            outcome_prices_str = data.get('outcomePrices', '[]')
            if isinstance(outcome_prices_str, str):
                outcome_prices = json.loads(outcome_prices_str)
            else:
                outcome_prices = outcome_prices_str
            
            # 获取 outcomes（选项）
            outcomes_str = data.get('outcomes', '[]')
            if isinstance(outcomes_str, str):
                outcomes = json.loads(outcomes_str)
            else:
                outcomes = outcomes_str
            
            # 获取 clobTokenIds
            clob_token_ids_str = data.get('clobTokenIds', '[]')
            if isinstance(clob_token_ids_str, str):
                try:
                    clob_token_ids = json.loads(clob_token_ids_str)
                except:
                    clob_token_ids = []
            else:
                clob_token_ids = clob_token_ids_str or []
            
            # 计算概率
            probabilities = []
            for i, price in enumerate(outcome_prices):
                outcome_name = outcomes[i] if i < len(outcomes) else f'Option {i+1}'
                prob = {
                    'outcome': outcome_name,
                    'price': float(price),
                    'probability': round(float(price) * 100, 2)
                }
                probabilities.append(prob)
            
            # 确定最高概率选项
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
                'active': data.get('active', False),
                'closed': data.get('closed', False),
                'clobTokenIds': clob_token_ids,
                'image': data.get('image'),
                'updatedAt': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[警告] 解析市场数据失败: {e}")
            return None
    
    def fetch_clob_price(self, token_id):
        """从 CLOB API 获取实时价格（备用）"""
        try:
            url = f"{CLOB_API_BASE}/midpoint"
            params = {'token_id': token_id}
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return None


def main():
    """主函数：获取数据并保存"""
    fetcher = PolymarketFetcher()
    all_markets = []
    
    print("开始获取 Polymarket 中东地缘市场数据...\n")
    
    # 1. 获取已知的热门市场
    print("[1/3] 获取已知热门市场...")
    for slug in KNOWN_MARKETS:
        market = fetcher.fetch_market_by_slug(slug)
        if market:
            all_markets.append(market)
            print(f"  [OK] {market['question'][:60]}...")
            print(f"     共识: {market['consensus']}, 交易量: ${market['volumeNum']:,.0f}")
    
    # 2. 搜索相关市场
    print("\n[2/3] 搜索相关市场...")
    seen_slugs = {m['slug'] for m in all_markets}
    
    for query in SEARCH_QUERIES:
        markets = fetcher.search_markets(query, limit=5)
        for market in markets:
            if market['slug'] not in seen_slugs:
                all_markets.append(market)
                seen_slugs.add(market['slug'])
                print(f"  [OK] [{query}] {market['question'][:50]}...")
    
    # 3. 按交易量排序
    all_markets.sort(key=lambda x: x['volumeNum'], reverse=True)
    
    # 4. 保存数据
    output = {
        'updatedAt': datetime.now().isoformat(),
        'totalMarkets': len(all_markets),
        'markets': all_markets
    }
    
    # 保存完整数据
    with open('polymarket_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 保存简化版（供网页直接使用）
    simplified = []
    for m in all_markets:
        simplified.append({
            'slug': m['slug'],
            'question': m['question'],
            'consensus': m['consensus'],
            'probabilities': m['probabilities'],
            'volume': m['volume'],
            'endDate': m['endDate'],
            'image': m['image']
        })
    
    with open('polymarket_simple.json', 'w', encoding='utf-8') as f:
        json.dump({
            'updatedAt': datetime.now().isoformat(),
            'markets': simplified
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[完成] 数据获取完成！")
    print(f"       共获取 {len(all_markets)} 个市场")
    print(f"       完整数据: polymarket_data.json")
    print(f"       简化数据: polymarket_simple.json")
    
    # 打印摘要
    print("\n=== 热门市场摘要 ===")
    for i, m in enumerate(all_markets[:5], 1):
        print(f"{i}. {m['question'][:70]}")
        print(f"   概率: {m['consensus']}")
        print(f"   交易量: ${m['volumeNum']:,.0f}")
        print()


if __name__ == '__main__':
    main()
