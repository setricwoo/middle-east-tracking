#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 数据更新脚本
通过 Gamma API 获取伊朗相关预测市场数据
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Gamma API 基础URL
GAMMA_API_BASE = "https://gamma-api.polymarket.com"

# 伊朗相关市场的事件ID（通过搜索获取）
IRAN_MARKET_SLUGS = [
    # 特朗普结束军事行动
    "trump-announces-end-military-action-iran",
    # 美伊停火
    "us-x-iran-ceasefire-by",
    # 霍尔木兹海峡
    "will-iran-close-the-strait-of-hormuz-by-2027",
    "hormuz-strait-traffic-resume",
    # 原油价格
    "will-crude-oil-cl-hit-by-end-of-march",
    "will-crude-oil-cl-hit-by-end-of-june",
    # 伊朗政权
    "will-the-iranian-regime-fall-by-march-31",
    "will-the-iranian-regime-fall-by-june-30",
    # 美军进入伊朗
    "us-forces-enter-iran-by",
    # 伊朗袭击以色列
    "iran-strikes-israel-on",
]

# 中文分类映射
CATEGORY_MAP = {
    "trump-announces-end-military-action-iran": "特朗普结束军事行动",
    "us-x-iran-ceasefire-by": "停火协议",
    "will-iran-close-the-strait-of-hormuz-by-2027": "霍尔木兹海峡",
    "hormuz-strait-traffic-resume": "霍尔木兹海峡",
    "will-crude-oil-cl-hit-by-end-of-march": "原油价格",
    "will-crude-oil-cl-hit-by-end-of-june": "原油价格",
    "will-the-iranian-regime-fall-by-march-31": "伊朗政权",
    "will-the-iranian-regime-fall-by-june-30": "伊朗政权",
    "us-forces-enter-iran-by": "美军进入伊朗",
    "iran-strikes-israel-on": "伊朗袭击以色列",
}


def search_events(query: str, limit: int = 20) -> List[Dict]:
    """搜索Polymarket事件"""
    url = f"{GAMMA_API_BASE}/events"
    params = {
        "search": query,
        "limit": limit,
        "active": "true",
        "order": "volume",
        "sort": "desc"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"搜索事件失败 {query}: {e}")
        return []


def get_event_markets(event_id: str) -> Dict:
    """获取事件的详细市场数据"""
    url = f"{GAMMA_API_BASE}/events/{event_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取事件详情失败 {event_id}: {e}")
        return {}


def get_market_price_history(market_id: str) -> List[Dict]:
    """获取市场价格历史"""
    url = f"{GAMMA_API_BASE}/markets/{market_id}/prices"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取价格历史失败 {market_id}: {e}")
        return []


def process_market_data(market: Dict) -> Dict:
    """处理市场数据，提取关键信息"""
    outcomes = market.get("outcomes", [])
    outcome_prices = market.get("outcomePrices", [])
    
    probabilities = []
    for i, outcome in enumerate(outcomes):
        price = outcome_prices[i] if i < len(outcome_prices) else "0"
        try:
            price_float = float(price)
            probability = price_float * 100
        except:
            price_float = 0
            probability = 0
            
        probabilities.append({
            "outcome": outcome,
            "price": price_float,
            "probability": round(probability, 2)
        })
    
    # 获取Yes的概率
    yes_prob = next((p for p in probabilities if p["outcome"] == "Yes"), None)
    consensus = f"Yes ({yes_prob['probability']}%)" if yes_prob else "N/A"
    
    return {
        "id": market.get("id"),
        "slug": market.get("slug"),
        "question": market.get("question"),
        "outcomes": outcomes,
        "probabilities": probabilities,
        "consensus": consensus,
        "volume": market.get("volume", "0"),
        "volumeNum": float(market.get("volumeNum", 0) or 0),
        "liquidity": market.get("liquidity"),
        "endDate": market.get("endDate", ""),
        "deadline": market.get("deadline", "N/A"),
        "image": market.get("image")
    }


def fetch_iran_events() -> Dict[str, Any]:
    """获取所有伊朗相关事件数据"""
    events_data = []
    
    # 搜索关键词列表
    search_queries = [
        "iran military action trump",
        "us iran ceasefire",
        "hormuz strait",
        "crude oil CL",
        "iranian regime fall",
        "us forces enter iran",
        "iran strikes israel"
    ]
    
    seen_ids = set()
    
    for query in search_queries:
        print(f"搜索: {query}")
        events = search_events(query, limit=10)
        
        for event in events:
            event_id = event.get("id")
            if not event_id or event_id in seen_ids:
                continue
            seen_ids.add(event_id)
            
            print(f"  获取事件: {event.get('title', 'N/A')[:50]}...")
            
            # 获取详细数据
            detail = get_event_markets(event_id)
            if not detail:
                continue
            
            # 处理市场数据
            markets = []
            for market in detail.get("markets", []):
                market_data = process_market_data(market)
                markets.append(market_data)
            
            if not markets:
                continue
            
            # 确定分类
            slug = detail.get("slug", "")
            category = "其他"
            for key, cat in CATEGORY_MAP.items():
                if key in slug:
                    category = cat
                    break
            
            event_data = {
                "id": event_id,
                "slug": slug,
                "title": detail.get("title", ""),
                "description": detail.get("description", ""),
                "category": category,
                "image": detail.get("image"),
                "totalVolume": sum(m.get("volumeNum", 0) for m in markets),
                "totalMarkets": len(markets),
                "markets": markets
            }
            events_data.append(event_data)
    
    result = {
        "updatedAt": datetime.now().isoformat(),
        "topic": "Iran/Middle East",
        "totalEvents": len(events_data),
        "events": events_data
    }
    
    return result


def merge_with_existing(new_data: Dict, existing_file: str) -> Dict:
    """与现有数据合并，保留历史价格数据"""
    if not os.path.exists(existing_file):
        return new_data
    
    try:
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # 创建事件映射
        existing_events = {e["id"]: e for e in existing.get("events", [])}
        
        # 合并事件
        for new_event in new_data["events"]:
            event_id = new_event["id"]
            if event_id in existing_events:
                # 保留历史数据，更新当前数据
                old_event = existing_events[event_id]
                # 可以在这里添加价格历史追踪
        
        print(f"与现有数据合并完成")
        return new_data
        
    except Exception as e:
        print(f"合并数据失败: {e}")
        return new_data


def save_data(data: Dict, filename: str):
    """保存数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("Polymarket 伊朗事件数据更新")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取数据
    print("\n正在从 Gamma API 获取数据...")
    data = fetch_iran_events()
    
    print(f"\n获取到 {data['totalEvents']} 个事件")
    
    # 按分类统计
    categories = {}
    for event in data["events"]:
        cat = event["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n分类统计:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} 个事件")
    
    # 与现有数据合并
    existing_file = "iran_events.json"
    merged_data = merge_with_existing(data, existing_file)
    
    # 保存数据
    save_data(merged_data, existing_file)
    
    # 同时生成一个简化的polymarket数据文件供页面使用
    generate_simple_data(merged_data)
    
    print("\n" + "=" * 60)
    print("更新完成!")
    print("=" * 60)


def generate_simple_data(data: Dict):
    """生成简化的数据文件供前端使用"""
    simple_data = {
        "updatedAt": data["updatedAt"],
        "markets": []
    }
    
    for event in data.get("events", []):
        for market in event.get("markets", []):
            yes_prob = next((p for p in market.get("probabilities", []) 
                           if p["outcome"] == "Yes"), None)
            
            simple_data["markets"].append({
                "event": event["title"],
                "category": event["category"],
                "question": market["question"],
                "probability": yes_prob["probability"] if yes_prob else 0,
                "volume": market["volumeNum"],
                "deadline": market["deadline"]
            })
    
    # 按交易量排序
    simple_data["markets"].sort(key=lambda x: x["volume"], reverse=True)
    
    with open("polymarket_data.json", 'w', encoding='utf-8') as f:
        json.dump(simple_data, f, ensure_ascii=False, indent=2)
    
    print(f"简化数据已保存到: polymarket_data.json ({len(simple_data['markets'])} 个市场)")


if __name__ == "__main__":
    main()
