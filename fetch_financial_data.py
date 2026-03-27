#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取全球金融市场真实数据 (使用 yfinance)
- 股票指数：标普500、纳斯达克、道琼斯、欧洲、亚洲等
- 债券收益率：美债、德债、日债、中债等
- 板块ETF：科技、金融、能源、医疗等
"""

import json
import time
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# 设置重试策略
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "data-tracking.html"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

# 股票指数配置
STOCKS_CONFIG = {
    'us_sp500': {'symbol': '^GSPC', 'name': '标普500', 'country': '美国'},
    'us_nasdaq': {'symbol': '^IXIC', 'name': '纳斯达克', 'country': '美国'},
    'us_dow': {'symbol': '^DJI', 'name': '道琼斯', 'country': '美国'},
    'europe_stoxx': {'symbol': '^STOXX50E', 'name': '欧洲斯托克50', 'country': '欧洲'},
    'germany_dax': {'symbol': '^GDAXI', 'name': '德国DAX', 'country': '德国'},
    'uk_ftse': {'symbol': '^FTSE', 'name': '英国富时100', 'country': '英国'},
    'japan_nikkei': {'symbol': '^N225', 'name': '日经225', 'country': '日本'},
    'hongkong_hsi': {'symbol': '^HSI', 'name': '恒生指数', 'country': '中国香港'},
    'china_shanghai': {'symbol': '000001.SS', 'name': '上证指数', 'country': '中国'},
}

# 债券收益率配置 (使用ETF替代，因为yfinance对债券支持有限)
BONDS_CONFIG = {
    'us_10y': {'symbol': '^TNX', 'name': '美国10年期国债', 'country': '美国', 'maturity': '10年'},
    'us_2y': {'symbol': '^IRX', 'name': '美国2年期国债', 'country': '美国', 'maturity': '2年'},
    'us_5y': {'symbol': '^FVX', 'name': '美国5年期国债', 'country': '美国', 'maturity': '5年'},
}

# 板块ETF配置
SECTORS_CONFIG = {
    'tech': {'symbol': 'XLK', 'name': '科技', 'etf': 'XLK'},
    'financial': {'symbol': 'XLF', 'name': '金融', 'etf': 'XLF'},
    'energy': {'symbol': 'XLE', 'name': '能源', 'etf': 'XLE'},
    'healthcare': {'symbol': 'XLV', 'name': '医疗', 'etf': 'XLV'},
    'consumer': {'symbol': 'XLY', 'name': '消费', 'etf': 'XLY'},
    'industrial': {'symbol': 'XLI', 'name': '工业', 'etf': 'XLI'},
}


def fetch_stock_data(config):
    """获取股票数据"""
    try:
        time.sleep(0.5)  # 避免请求过快
        ticker = yf.Ticker(config['symbol'])
        # 获取6个月数据
        hist = ticker.history(period="6mo")
        
        if hist.empty:
            print(f"  [警告] {config['name']} 无数据")
            return None
        
        # 计算涨跌幅
        latest = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((latest - prev) / prev) * 100
        
        # 6个月涨跌幅
        start_price = hist['Close'].iloc[0]
        change_6m_pct = ((latest - start_price) / start_price) * 100
        
        return {
            'symbol': config['symbol'],
            'name': config['name'],
            'country': config['country'],
            'latest': round(latest, 2),
            'change_pct': round(change_pct, 2),
            'change_6m_pct': round(change_6m_pct, 2),
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'values': [round(v, 2) for v in hist['Close'].tolist()],
        }
    except Exception as e:
        print(f"  [错误] {config['name']}: {e}")
        return None


def fetch_bond_data(config):
    """获取债券收益率数据"""
    try:
        time.sleep(0.5)  # 避免请求过快
        ticker = yf.Ticker(config['symbol'])
        hist = ticker.history(period="6mo")
        
        if hist.empty:
            print(f"  [警告] {config['name']} 无数据")
            return None
        
        latest = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((latest - prev) / prev) * 100
        
        return {
            'symbol': config['symbol'],
            'name': config['name'],
            'country': config['country'],
            'maturity': config['maturity'],
            'latest': round(latest, 2),
            'change_pct': round(change_pct, 2),
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'values': [round(v, 2) for v in hist['Close'].tolist()],
        }
    except Exception as e:
        print(f"  [错误] {config['name']}: {e}")
        return None


def fetch_sector_data(config):
    """获取板块ETF数据"""
    try:
        time.sleep(0.5)  # 避免请求过快
        ticker = yf.Ticker(config['symbol'])
        hist = ticker.history(period="6mo")
        
        if hist.empty:
            print(f"  [警告] {config['name']} 无数据")
            return None
        
        latest = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change_pct = ((latest - prev) / prev) * 100
        
        # 6个月涨跌幅
        start_price = hist['Close'].iloc[0]
        change_6m_pct = ((latest - start_price) / start_price) * 100
        
        return {
            'symbol': config['symbol'],
            'name': config['name'],
            'etf': config['etf'],
            'latest': round(latest, 2),
            'change_pct': round(change_pct, 2),
            'change_6m_pct': round(change_6m_pct, 2),
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'values': [round(v, 2) for v in hist['Close'].tolist()],
        }
    except Exception as e:
        print(f"  [错误] {config['name']}: {e}")
        return None


def update_html_data(data):
    """更新HTML文件中的数据"""
    if not DATA_FILE.exists():
        print(f"[错误] 找不到HTML文件: {DATA_FILE}")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 STATIC_FINANCIAL_DATA
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    # 使用正则替换
    import re
    pattern = r'let STATIC_FINANCIAL_DATA = \{[\s\S]*?\};'
    replacement = f'let STATIC_FINANCIAL_DATA = {data_json};'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print("[警告] 未找到 STATIC_FINANCIAL_DATA，尝试插入新数据")
        # 在 STATIC_EXCEL_DATA 后插入
        pattern2 = r'(let STATIC_EXCEL_DATA = \{[\s\S]*?\};)'
        replacement2 = r'\1\n    let STATIC_FINANCIAL_DATA = ' + data_json + ';'
        new_content = re.sub(pattern2, replacement2, content)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    print("=" * 60)
    print("获取金融市场真实数据 (yfinance)")
    print("=" * 60)
    
    # 1. 获取股票数据
    print("\n[1/3] 获取股票指数...")
    stocks = {}
    for key, config in STOCKS_CONFIG.items():
        print(f"  获取 {config['name']}...", end=' ')
        data = fetch_stock_data(config)
        if data:
            stocks[key] = data
            print(f"[OK] 最新: {data['latest']}")
        else:
            print("[FAIL] 失败")
    
    # 2. 获取债券数据
    print("\n[2/3] 获取债券收益率...")
    bonds = {}
    for key, config in BONDS_CONFIG.items():
        print(f"  获取 {config['name']}...", end=' ')
        data = fetch_bond_data(config)
        if data:
            bonds[key] = data
            print(f"[OK] 最新: {data['latest']}%")
        else:
            print("[FAIL] 失败")
    
    # 3. 获取板块数据
    print("\n[3/3] 获取板块ETF...")
    sectors = {}
    for key, config in SECTORS_CONFIG.items():
        print(f"  获取 {config['name']}...", end=' ')
        data = fetch_sector_data(config)
        if data:
            sectors[key] = data
            print(f"[OK] 最新: ${data['latest']}")
        else:
            print("[FAIL] 失败")
    
    # 4. 构建数据结构
    financial_data = {
        "updated": datetime.now(BEIJING_TZ).isoformat(),
        "stocks": stocks,
        "bonds": bonds,
        "sectors": sectors,
    }
    
    # 5. 更新HTML
    print("\n[保存] 更新HTML文件...")
    if update_html_data(financial_data):
        print("[完成] 数据已更新")
        print(f"\n  股票: {len(stocks)} 个")
        print(f"  债券: {len(bonds)} 个")
        print(f"  板块: {len(sectors)} 个")
    else:
        print("[失败] 更新HTML失败")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
