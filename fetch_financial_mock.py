#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模拟金融市场数据（备用方案）
当 yfinance 限流时使用
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "data-tracking.html"
BEJING_TZ = ZoneInfo("Asia/Shanghai")


def generate_mock_data():
    """生成模拟数据"""
    end_date = datetime.now(BEJING_TZ)
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(180, 0, -1)]
    
    # 股票数据（基于近期真实范围的模拟）
    stocks = {
        'us_sp500': {
            'symbol': '^GSPC', 'name': '标普500', 'country': '美国',
            'latest': 5695.0, 'change_pct': 0.15, 'change_6m_pct': 8.5,
            'dates': dates,
            'values': [round(5400 + i*2 + random.uniform(-50, 50), 2) for i in range(180)]
        },
        'us_nasdaq': {
            'symbol': '^IXIC', 'name': '纳斯达克', 'country': '美国',
            'latest': 18095.0, 'change_pct': 0.32, 'change_6m_pct': 12.3,
            'dates': dates,
            'values': [round(16500 + i*10 + random.uniform(-150, 150), 2) for i in range(180)]
        },
        'us_dow': {
            'symbol': '^DJI', 'name': '道琼斯', 'country': '美国',
            'latest': 42500.0, 'change_pct': -0.08, 'change_6m_pct': 6.2,
            'dates': dates,
            'values': [round(40500 + i*12 + random.uniform(-150, 150), 2) for i in range(180)]
        },
        'japan_nikkei': {
            'symbol': '^N225', 'name': '日经225', 'country': '日本',
            'latest': 39000.0, 'change_pct': 0.45, 'change_6m_pct': -2.1,
            'dates': dates,
            'values': [round(40000 - i*8 + random.uniform(-300, 300), 2) for i in range(180)]
        },
        'hongkong_hsi': {
            'symbol': '^HSI', 'name': '恒生指数', 'country': '中国香港',
            'latest': 23500.0, 'change_pct': -0.25, 'change_6m_pct': 15.8,
            'dates': dates,
            'values': [round(20000 + i*25 + random.uniform(-200, 200), 2) for i in range(180)]
        },
        'china_shanghai': {
            'symbol': '000001.SS', 'name': '上证指数', 'country': '中国',
            'latest': 3380.0, 'change_pct': 0.12, 'change_6m_pct': 3.2,
            'dates': dates,
            'values': [round(3250 + i*1 + random.uniform(-30, 30), 2) for i in range(180)]
        },
    }
    
    # 债券数据
    bonds = {
        'us_10y': {
            'symbol': '^TNX', 'name': '美国10年期国债', 'country': '美国', 'maturity': '10年',
            'latest': 4.25, 'change_pct': -0.05,
            'dates': dates,
            'values': [round(4.2 + random.uniform(-0.15, 0.15), 2) for _ in range(180)]
        },
        'us_2y': {
            'symbol': '^IRX', 'name': '美国2年期国债', 'country': '美国', 'maturity': '2年',
            'latest': 4.15, 'change_pct': 0.02,
            'dates': dates,
            'values': [round(4.1 + random.uniform(-0.1, 0.1), 2) for _ in range(180)]
        },
        'us_5y': {
            'symbol': '^FVX', 'name': '美国5年期国债', 'country': '美国', 'maturity': '5年',
            'latest': 4.20, 'change_pct': -0.01,
            'dates': dates,
            'values': [round(4.15 + random.uniform(-0.12, 0.12), 2) for _ in range(180)]
        },
    }
    
    # 板块ETF
    sectors = {
        'tech': {
            'symbol': 'XLK', 'name': '科技', 'etf': 'XLK',
            'latest': 220.0, 'change_pct': 0.45, 'change_6m_pct': 15.2,
            'dates': dates,
            'values': [round(200 + i*0.15 + random.uniform(-3, 3), 2) for i in range(180)]
        },
        'financial': {
            'symbol': 'XLF', 'name': '金融', 'etf': 'XLF',
            'latest': 48.5, 'change_pct': -0.12, 'change_6m_pct': 8.1,
            'dates': dates,
            'values': [round(45 + i*0.03 + random.uniform(-0.5, 0.5), 2) for i in range(180)]
        },
        'energy': {
            'symbol': 'XLE', 'name': '能源', 'etf': 'XLE',
            'latest': 95.0, 'change_pct': 0.25, 'change_6m_pct': 5.8,
            'dates': dates,
            'values': [round(90 + i*0.04 + random.uniform(-2, 2), 2) for i in range(180)]
        },
        'healthcare': {
            'symbol': 'XLV', 'name': '医疗', 'etf': 'XLV',
            'latest': 142.0, 'change_pct': 0.18, 'change_6m_pct': 7.2,
            'dates': dates,
            'values': [round(135 + i*0.05 + random.uniform(-1.5, 1.5), 2) for i in range(180)]
        },
        'consumer': {
            'symbol': 'XLY', 'name': '消费', 'etf': 'XLY',
            'latest': 178.0, 'change_pct': 0.32, 'change_6m_pct': 9.5,
            'dates': dates,
            'values': [round(165 + i*0.1 + random.uniform(-2, 2), 2) for i in range(180)]
        },
        'industrial': {
            'symbol': 'XLI', 'name': '工业', 'etf': 'XLI',
            'latest': 125.0, 'change_pct': -0.08, 'change_6m_pct': 6.3,
            'dates': dates,
            'values': [round(118 + i*0.05 + random.uniform(-1.5, 1.5), 2) for i in range(180)]
        },
    }
    
    return {
        "updated": datetime.now(BEJING_TZ).isoformat(),
        "stocks": stocks,
        "bonds": bonds,
        "sectors": sectors,
    }


def update_html(data):
    """更新HTML"""
    if not DATA_FILE.exists():
        print(f"[错误] 找不到 {DATA_FILE}")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    import re
    pattern = r'let STATIC_FINANCIAL_DATA = \{[\s\S]*?\};'
    replacement = f'let STATIC_FINANCIAL_DATA = {data_json};'
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    print("=" * 60)
    print("生成金融市场模拟数据")
    print("=" * 60)
    
    data = generate_mock_data()
    
    if update_html(data):
        print("[完成] 数据已更新")
        print(f"  股票: {len(data['stocks'])} 个")
        print(f"  债券: {len(data['bonds'])} 个")
        print(f"  板块: {len(data['sectors'])} 个")
    else:
        print("[失败]")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
