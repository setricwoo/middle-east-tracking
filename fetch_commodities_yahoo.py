#!/usr/bin/env python3
"""
Fetch commodity data from Yahoo Finance
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "commodities_data.json"

# Commodity configuration - grouped for display
COMMODITY_GROUPS = {
    "oil": {
        "name": "原油价格",
        "symbols": ["CL=F", "BZ=F"],  # WTI原油, 布伦特原油
        "labels": ["WTI原油", "布伦特原油"],
        "unit": "美元/桶"
    },
    "gas": {
        "name": "天然气价格",
        "symbols": ["NG=F", "TTF=F"],  # 美国天然气, TTF
        "labels": ["美国天然气", "TTF天然气"],
        "unit": "美元/百万英热"
    },
    "naphtha_propane": {
        "name": "石脑油与丙烷",
        "symbols": ["RB=F", "HO=F"],  # 汽油(RBOB), 取暖油(代替石脑油/丙烷)
        "labels": ["RBOB汽油", "取暖油"],
        "unit": "美元/加仑"
    },
    "methanol_ethanol": {
        "name": "甲醇与乙醇",
        "symbols": ["ZC=F", "ZL=F"],  # 玉米(乙醇原料), 大豆油
        "labels": ["玉米(乙醇原料)", "大豆油"],
        "unit": "美分/蒲式耳"
    },
    "aluminum_urea": {
        "name": "铝与尿素",
        "symbols": ["ALI=F", "ZN=F"],  # 铝期货, 锌(代替尿素)
        "labels": ["铝", "锌"],
        "unit": "美元/吨"
    },
    "soybean_wheat": {
        "name": "大豆与小麦",
        "symbols": ["ZS=F", "ZW=F"],  # 大豆, 小麦
        "labels": ["大豆", "小麦"],
        "unit": "美分/蒲式耳"
    }
}

def fetch_symbol_data(symbol):
    """Fetch historical data for a symbol"""
    try:
        print(f"  Fetching {symbol}...")
        ticker = yf.Ticker(symbol)
        # Get last 90 days
        hist = ticker.history(period="3mo")
        
        if hist.empty:
            print(f"    No data")
            return None
        
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        values = hist['Close'].tolist()
        
        print(f"    OK: got {len(values)} records")
        return {
            "dates": dates,
            "values": values
        }
    except Exception as e:
        print(f"    Error: {e}")
        return None

def fetch_all_commodities():
    """Fetch all commodity data"""
    print("=" * 60)
    print("Fetching commodity data from Yahoo Finance")
    print("=" * 60)
    
    result = {
        "updated": datetime.now().isoformat(),
        "source": "yahoo-finance",
        "groups": {}
    }
    
    for group_key, group_config in COMMODITY_GROUPS.items():
        print(f"\n{group_config['name']}:")
        group_data = {
            "name": group_config["name"],
            "unit": group_config["unit"],
            "symbols": []
        }
        
        for i, symbol in enumerate(group_config["symbols"]):
            data = fetch_symbol_data(symbol)
            if data:
                group_data["symbols"].append({
                    "symbol": symbol,
                    "label": group_config["labels"][i],
                    "dates": data["dates"],
                    "values": data["values"]
                })
        
        result["groups"][group_key] = group_data
    
    # Save data
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Data saved: {DATA_FILE}")
    print(f"{'=' * 60}")
    
    return result

if __name__ == "__main__":
    fetch_all_commodities()
