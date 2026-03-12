#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Polymarket获取指定事件的概率数据及历史序列
使用正确的CLOB API参数
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Polymarket APIs
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# 事件slug列表
EVENT_SLUGS = [
    "trump-announces-end-of-military-operations-against-iran-by",
    "us-x-iran-ceasefire-by",
    "avg-of-ships-transiting-strait-of-hormuz-end-of-march",
    "strait-of-hormuz-traffic-returns-to-normal-by-april-30",
    "will-crude-oil-cl-hit-by-end-of-march",
    "cl-hit-jun-2026",
]

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}


def get_event_by_slug(slug: str) -> Dict:
    """通过slug获取事件数据（包含markets）"""
    url = f"{GAMMA_API}/events"
    params = {"slug": slug, "_s": "slug"}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and len(data) > 0:
            event = data[0]
            event_id = event.get("id")
            if event_id:
                # 获取完整事件详情（包含markets）
                detail_url = f"{GAMMA_API}/events/{event_id}"
                detail_resp = requests.get(detail_url, headers=HEADERS, timeout=30)
                if detail_resp.status_code == 200:
                    return detail_resp.json()
            return event
        elif isinstance(data, dict):
            return data
        return {}
    except Exception as e:
        print(f"  获取事件失败 {slug}: {e}")
        return {}


def get_price_history(token_id: str, interval: str = "all") -> List[Dict]:
    """获取价格历史数据"""
    # 使用正确的API参数: market 和 interval
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("history", [])
    except Exception as e:
        # 尝试其他interval值
        for alt_interval in ["max", "1d"]:
            try:
                params["interval"] = alt_interval
                resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("history", [])
            except:
                pass
        print(f"      价格历史获取失败: {e}")
        return []


def parse_json_field(field) -> List:
    """解析JSON字段"""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return []
    elif isinstance(field, list):
        return field
    return []


def fetch_event_data(slug: str) -> Dict:
    """获取单个事件的完整数据（包含历史）"""
    print(f"\n{'='*60}")
    print(f"获取事件: {slug}")
    print(f"{'='*60}")

    event = get_event_by_slug(slug)

    if not event:
        print(f"  未找到事件")
        return None

    event_id = event.get("id")
    event_title = event.get("title", "")
    print(f"  事件ID: {event_id}")
    print(f"  标题: {event_title}")

    # 从事件直接获取市场数据
    markets = event.get("markets", [])
    print(f"  市场数量: {len(markets)}")

    markets_data = []
    for m in markets:
        question = m.get("question", "")
        market_id = m.get("id", "")
        condition_id = m.get("conditionId", "")

        # 解析选项和价格
        outcomes = parse_json_field(m.get("outcomes"))
        outcome_prices = parse_json_field(m.get("outcomePrices"))
        clob_token_ids = parse_json_field(m.get("clobTokenIds"))

        market_info = {
            "question": question,
            "id": market_id,
            "conditionId": condition_id,
            "outcomes": {},
            "volume": m.get("volume", "0"),
            "active": m.get("active", False),
            "closed": m.get("closed", False),
            "endDate": m.get("endDateIso", ""),
        }

        print(f"\n  市场: {question[:60]}...")

        # 处理每个选项
        for i, outcome_name in enumerate(outcomes):
            token_id = ""
            if i < len(clob_token_ids):
                token_id = clob_token_ids[i]

            current_price = 0.0
            if i < len(outcome_prices):
                try:
                    current_price = float(outcome_prices[i])
                except:
                    pass

            print(f"    选项: {outcome_name}")
            print(f"      Token: {token_id[:20] if token_id else 'N/A'}...")
            print(f"      当前价格: {current_price * 100:.2f}%")

            # 获取价格历史
            price_history = []
            if token_id:
                history = get_price_history(token_id)
                for h in history:
                    try:
                        ts = h.get("t", 0)
                        price = h.get("p", 0)
                        dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                        price_history.append({
                            "time": dt,
                            "timestamp": ts,
                            "price": round(price * 100, 2)
                        })
                    except:
                        pass
                print(f"      历史数据点: {len(price_history)}")
                time.sleep(0.15)

            market_info["outcomes"][outcome_name] = {
                "tokenId": token_id,
                "currentPrice": round(current_price * 100, 2),
                "priceHistory": price_history
            }

        markets_data.append(market_info)

    return {
        "slug": slug,
        "id": event_id,
        "title": event_title,
        "markets": markets_data,
        "fetchedAt": datetime.now().isoformat()
    }


def main():
    print("="*70)
    print("Polymarket 历史数据获取器 v6")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    all_events = {}

    for slug in EVENT_SLUGS:
        event_data = fetch_event_data(slug)
        if event_data:
            all_events[slug] = event_data
        time.sleep(0.2)

    # 保存数据
    output = {
        "fetchedAt": datetime.now().isoformat(),
        "events": all_events
    }

    filename = "polymarket_history_data.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n历史数据已保存: {filename}")

    # 打印摘要
    print("\n" + "="*70)
    print("数据摘要")
    print("="*70)

    for slug, event in all_events.items():
        print(f"\n事件: {event.get('title', slug)}")
        for market in event.get("markets", []):
            q = market.get('question', '')[:40]
            print(f"  市场: {q}...")
            for outcome, info in market.get("outcomes", {}).items():
                current = info.get("currentPrice", 0)
                history_count = len(info.get("priceHistory", []))
                print(f"    {outcome}: {current}% (历史: {history_count}点)")

    print("\n" + "="*70)
    print("完成!")
    print("="*70)


if __name__ == "__main__":
    main()
