#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量获取金融市场数据 (使用 yfinance.download)
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "data-tracking.html"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

# 所有 symbol 列表
ALL_SYMBOLS = {
    # 股票
    '^GSPC': {'key': 'us_sp500', 'name': '标普500', 'country': '美国', 'type': 'stock'},
    '^IXIC': {'key': 'us_nasdaq', 'name': '纳斯达克', 'country': '美国', 'type': 'stock'},
    '^DJI': {'key': 'us_dow', 'name': '道琼斯', 'country': '美国', 'type': 'stock'},
    '^N225': {'key': 'japan_nikkei', 'name': '日经225', 'country': '日本', 'type': 'stock'},
    '^HSI': {'key': 'hongkong_hsi', 'name': '恒生指数', 'country': '中国香港', 'type': 'stock'},
    '000001.SS': {'key': 'china_shanghai', 'name': '上证指数', 'country': '中国', 'type': 'stock'},
    # 债券
    '^TNX': {'key': 'us_10y', 'name': '美国10年期国债', 'country': '美国', 'type': 'bond', 'maturity': '10年'},
    '^IRX': {'key': 'us_2y', 'name': '美国2年期国债', 'country': '美国', 'type': 'bond', 'maturity': '2年'},
    '^FVX': {'key': 'us_5y', 'name': '美国5年期国债', 'country': '美国', 'type': 'bond', 'maturity': '5年'},
    # 板块
    'XLK': {'key': 'tech', 'name': '科技', 'type': 'sector', 'etf': 'XLK'},
    'XLF': {'key': 'financial', 'name': '金融', 'type': 'sector', 'etf': 'XLF'},
    'XLE': {'key': 'energy', 'name': '能源', 'type': 'sector', 'etf': 'XLE'},
    'XLV': {'key': 'healthcare', 'name': '医疗', 'type': 'sector', 'etf': 'XLV'},
    'XLY': {'key': 'consumer', 'name': '消费', 'type': 'sector', 'etf': 'XLY'},
    'XLI': {'key': 'industrial', 'name': '工业', 'type': 'sector', 'etf': 'XLI'},
}


def fetch_all_data():
    """批量获取所有数据"""
    symbols = list(ALL_SYMBOLS.keys())
    
    try:
        print("[下载] 批量获取数据...")
        data = yf.download(symbols, period="6mo", progress=False, threads=True)
        return data
    except Exception as e:
        print(f"[错误] 下载失败: {e}")
        return None


def process_data(data):
    """处理下载的数据"""
    stocks = {}
    bonds = {}
    sectors = {}
    
    if data is None or data.empty:
        return stocks, bonds, sectors
    
    for symbol, config in ALL_SYMBOLS.items():
        try:
            if symbol not in data['Close'].columns:
                print(f"  [跳过] {symbol} 无数据")
                continue
            
            closes = data['Close'][symbol].dropna()
            if closes.empty:
                continue
            
            latest = closes.iloc[-1]
            prev = closes.iloc[-2]
            start = closes.iloc[0]
            
            change_pct = ((latest - prev) / prev) * 100
            change_6m_pct = ((latest - start) / start) * 100
            
            result = {
                'symbol': symbol,
                'name': config['name'],
                'latest': round(latest, 2),
                'change_pct': round(change_pct, 2),
                'change_6m_pct': round(change_6m_pct, 2),
                'dates': closes.index.strftime('%Y-%m-%d').tolist(),
                'values': [round(v, 2) for v in closes.tolist()],
            }
            
            if config['type'] == 'stock':
                result['country'] = config['country']
                stocks[config['key']] = result
            elif config['type'] == 'bond':
                result['country'] = config['country']
                result['maturity'] = config['maturity']
                bonds[config['key']] = result
            elif config['type'] == 'sector':
                result['etf'] = config['etf']
                sectors[config['key']] = result
                
            print(f"  [OK] {config['name']}: {result['latest']}")
            
        except Exception as e:
            print(f"  [错误] {config['name']}: {e}")
    
    return stocks, bonds, sectors


def update_html(stocks, bonds, sectors):
    """更新HTML"""
    if not DATA_FILE.exists():
        print(f"[错误] 找不到 {DATA_FILE}")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    financial_data = {
        "updated": datetime.now(BEIJING_TZ).isoformat(),
        "stocks": stocks,
        "bonds": bonds,
        "sectors": sectors,
    }
    
    data_json = json.dumps(financial_data, ensure_ascii=False, indent=2)
    
    import re
    pattern = r'let STATIC_FINANCIAL_DATA = \{[\s\S]*?\};'
    replacement = f'let STATIC_FINANCIAL_DATA = {data_json};'
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    print("=" * 60)
    print("获取金融市场数据")
    print("=" * 60)
    
    data = fetch_all_data()
    stocks, bonds, sectors = process_data(data)
    
    print("\n[保存] 更新HTML...")
    if update_html(stocks, bonds, sectors):
        print("[完成]")
        print(f"  股票: {len(stocks)} 个")
        print(f"  债券: {len(bonds)} 个")
        print(f"  板块: {len(sectors)} 个")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
