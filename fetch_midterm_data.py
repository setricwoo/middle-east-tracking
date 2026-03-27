#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取中期选举数据并添加到 polymarket_real_data.json"""

import requests
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}

def get_event_by_id(event_id):
    """通过ID获取事件"""
    url = f"{GAMMA_API}/events/{event_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_price_history(token_id):
    """获取价格历史"""
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": "all"}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("history", [])
    except:
        # 尝试其他interval
        for alt in ["max", "1d"]:
            try:
                params["interval"] = alt
                resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    return resp.json().get("history", [])
            except:
                pass
        return []

def parse_json_field(field):
    """解析JSON字段"""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return []
    elif isinstance(field, list):
        return field
    return []

def fetch_midterm_data():
    """获取中期选举数据"""
    event_id = "32228"  # Balance of Power: 2026 Midterms
    
    print(f"Fetching midterm data (event_id={event_id})...")
    event = get_event_by_id(event_id)
    if not event:
        print("Failed to fetch event")
        return None
    
    print(f"Event: {event.get('title', '')}")
    markets = event.get("markets", [])
    print(f"Found {len(markets)} markets")
    
    markets_data = []
    for m in markets:
        question = m.get("question", "")
        outcomes = parse_json_field(m.get("outcomes"))
        outcome_prices = parse_json_field(m.get("outcomePrices"))
        clob_token_ids = parse_json_field(m.get("clobTokenIds"))
        
        # 找到Yes outcome或第一个
        yes_price = 0
        token_id = ""
        for i, outcome in enumerate(outcomes):
            if outcome == "Yes" or i == 0:
                if i < len(outcome_prices):
                    try:
                        yes_price = float(outcome_prices[i]) * 100
                    except:
                        pass
                if i < len(clob_token_ids):
                    token_id = clob_token_ids[i]
                break
        
        # 获取历史数据
        history = []
        if token_id:
            raw_history = get_price_history(token_id)
            beijing_tz = ZoneInfo("Asia/Shanghai")
            for h in raw_history:
                try:
                    ts = h.get("t", 0)
                    price = h.get("p", 0)
                    dt = datetime.fromtimestamp(ts, tz=beijing_tz)
                    history.append({
                        "time": dt.strftime('%m-%d %H:%M'),
                        "timestamp": ts,
                        "probability": round(price * 100, 2)
                    })
                except:
                    pass
        
        markets_data.append({
            "question": question,
            "current_probability": round(yes_price, 2),
            "history": history
        })
        print(f"  - {question[:50]}... ({len(history)} points)")
    
    return {
        "title": event.get("title", "2026 Midterms"),
        "markets": markets_data
    }

def main():
    # 获取中期选举数据
    midterm_data = fetch_midterm_data()
    if not midterm_data:
        return
    
    # 加载现有数据
    data_file = "polymarket_real_data.json"
    all_data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except:
            pass
    
    # 添加中期选举数据
    all_data["balance-of-power-2026-midterms"] = midterm_data
    
    # 保存
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to {data_file}")
    print("Done!")

if __name__ == "__main__":
    main()
