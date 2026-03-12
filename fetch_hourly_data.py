#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Gamma API获取市场每小时历史价格数据
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

GAMMA_API = "https://gamma-api.polymarket.com"

# 市场配置 - 填入从Polymarket获取的市场ID或Slug
# 格式: "事件名称": "market-slug-or-id"
MARKETS = {
    "trump_march_31": "",  # 填入: trump-announces-end-military-action-iran-march-31
    "trump_april_30": "",  # 填入: trump-announces-end-military-action-iran-april-30
    "trump_june_30": "",   # 填入: trump-announces-end-military-action-iran-june-30
    
    "ceasefire_march_31": "",  # 填入: us-x-iran-ceasefire-by-march-31
    "ceasefire_april_30": "",  # 填入: us-x-iran-ceasefire-by-april-30
    "ceasefire_may_31": "",    # 填入: us-x-iran-ceasefire-by-may-31
    "ceasefire_june_30": "",   # 填入: us-x-iran-ceasefire-by-june-30
    
    "hormuz_april_30": "",  # 填入: hormuz-strait-traffic-resume-april-30
}


def get_market_by_slug(slug: str) -> Optional[Dict]:
    """通过slug获取市场信息"""
    if not slug:
        return None
    
    url = f"{GAMMA_API}/markets/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  错误: {e}")
        return None


def get_price_history(market_id: str) -> List[Dict]:
    """获取价格历史数据"""
    if not market_id:
        return []
    
    url = f"{GAMMA_API}/markets/{market_id}/prices"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  获取价格历史失败: {e}")
        return []


def fetch_all_hourly_data():
    """获取所有配置的每小时数据"""
    results = {}
    
    print("=" * 70)
    print("获取Polymarket每小时历史数据")
    print("=" * 70)
    
    for name, slug in MARKETS.items():
        if not slug:
            print(f"\n跳过 {name}: 未配置slug")
            continue
        
        print(f"\n获取: {name} ({slug})")
        
        # 获取市场信息
        market = get_market_by_slug(slug)
        if not market:
            print(f"  未找到市场")
            continue
        
        market_id = market.get("id")
        question = market.get("question", "N/A")
        print(f"  问题: {question[:50]}...")
        
        # 获取价格历史
        prices = get_price_history(market_id)
        print(f"  获取到 {len(prices)} 个价格数据点")
        
        if prices:
            # 提取Yes方的价格
            yes_prices = []
            for p in prices:
                # 价格数据格式: { "timestamp": "...", "price": 0.25 }
                # 或者: { "timestamp": "...", "outcomePrices": {"Yes": 0.25, "No": 0.75} }
                if "outcomePrices" in p:
                    yes_price = p["outcomePrices"].get("Yes", 0)
                else:
                    yes_price = p.get("price", 0)
                yes_prices.append(yes_price * 100)  # 转换为百分比
            
            results[name] = {
                "slug": slug,
                "question": question,
                "timestamps": [p.get("timestamp") for p in prices],
                "yes_prices": yes_prices,
                "current_probability": yes_prices[-1] if yes_prices else 0
            }
            
            print(f"  当前概率: {results[name]['current_probability']:.2f}%")
        
        time.sleep(0.5)  # 避免请求过快
    
    return results


def save_data(data: Dict):
    """保存数据到文件"""
    filename = f"hourly_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到: {filename}")


def export_for_webpage(data: Dict):
    """导出为网页可用的格式"""
    web_data = {}
    
    for key, market_data in data.items():
        web_data[key] = market_data["yes_prices"]
    
    with open("hourly_data_for_web.json", 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)
    
    print("网页数据已保存到: hourly_data_for_web.json")


def print_instructions():
    """打印使用说明"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                        使用说明                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. 访问 Polymarket (polymarket.com)                                 ║
║                                                                      ║
║  2. 找到目标市场，例如:                                              ║
║     "Will Trump announce end to military action against Iran          ║
║      by March 31?"                                                   ║
║                                                                      ║
║  3. 复制市场URL中的slug，例如:                                       ║
║     https://polymarket.com/event/xxx-xxx/                            ║
║     slug = xxx-xxx (最后一部分)                                       ║
║                                                                      ║
║  4. 编辑本脚本，填入 MARKETS 配置                                    ║
║                                                                      ║
║  5. 运行: python fetch_hourly_data.py                                ║
║                                                                      ║
║  6. 将获取的数据填入 generate_with_june_oil.py 的                    ║
║     REAL_DATA 中的 hourly_history 字段                               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def main():
    print("\n")
    
    # 检查是否配置了市场
    has_config = any(slug for slug in MARKETS.values())
    
    if not has_config:
        print_instructions()
        return
    
    # 获取数据
    data = fetch_all_hourly_data()
    
    if data:
        save_data(data)
        export_for_webpage(data)
        
        print("\n" + "=" * 70)
        print("获取完成!")
        print("=" * 70)
        print("\n下一步:")
        print("  1. 查看 hourly_data_for_web.json")
        print("  2. 将数据复制到 generate_with_june_oil.py 的 REAL_DATA 中")
        print("  3. 运行 python generate_with_june_oil.py 生成网页")
    else:
        print("\n未获取到任何数据，请检查市场slug配置")


if __name__ == "__main__":
    main()
