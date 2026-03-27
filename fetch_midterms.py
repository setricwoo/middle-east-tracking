#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单独获取中期选举数据并合并到历史数据中"""

import requests
import json
import time
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}

def parse_json_field(field):
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return []
    elif isinstance(field, list):
        return field
    return []

def get_event_by_slug(slug):
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
                detail_url = f"{GAMMA_API}/events/{event_id}"
                detail_resp = requests.get(detail_url, headers=HEADERS, timeout=30)
                if detail_resp.status_code == 200:
                    return detail_resp.json()
            return event
        return {}
    except Exception as e:
        print(f"  获取失败 {slug}: {e}")
        return {}

def get_price_history(token_id, interval="all"):
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("history", [])
    except:
        for alt_interval in ["max", "1d"]:
            try:
                params["interval"] = alt_interval
                resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("history", [])
            except:
                pass
        return []

def fetch_event_data(slug):
    print(f"\n获取: {slug}")
    event = get_event_by_slug(slug)
    if not event:
        print(f"  未找到")
        return None
    
    event_id = event.get("id")
    event_title = event.get("title", "")
    print(f"  标题: {event_title[:50]}...")
    
    markets = event.get("markets", [])
    print(f"  市场数: {len(markets)}")
    
    markets_data = []
    for m in markets:
        question = m.get("question", "")
        outcomes = parse_json_field(m.get("outcomes"))
        outcome_prices = parse_json_field(m.get("outcomePrices"))
        clob_token_ids = parse_json_field(m.get("clobTokenIds"))
        
        market_info = {
            "question": question,
            "id": m.get("id", ""),
            "conditionId": m.get("conditionId", ""),
            "outcomes": {},
            "volume": m.get("volume", "0"),
            "active": m.get("active", False),
            "closed": m.get("closed", False),
            "endDate": m.get("endDateIso", ""),
        }
        
        for i, outcome_name in enumerate(outcomes):
            token_id = clob_token_ids[i] if i < len(clob_token_ids) else ""
            current_price = 0.0
            if i < len(outcome_prices):
                try:
                    current_price = float(outcome_prices[i])
                except:
                    pass
            
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
    # 加载现有数据
    with open('polymarket_history_data.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # 获取中期选举数据
    for slug in ["which-party-will-control-the-senate-after-2026-midterms",
                 "which-party-will-control-the-house-after-2026-midterms"]:
        event_data = fetch_event_data(slug)
        if event_data:
            existing_data["events"][slug] = event_data
        time.sleep(0.5)
    
    # 保存合并后的数据
    existing_data["fetchedAt"] = datetime.now().isoformat()
    with open('polymarket_history_data.json', 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print("\n✓ 数据已更新并保存")
    print(f"事件数: {len(existing_data['events'])}")

if __name__ == "__main__":
    main()
