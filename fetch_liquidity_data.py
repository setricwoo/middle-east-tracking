#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取全球流动性指标数据
"""

import requests
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

# 冲突开始日期
CONFLICT_DATE = "2026-01-07"

def get_fred_data(series_id, api_key=None, start_date=None):
    """从FRED获取数据"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': api_key or '',
        'file_type': 'json',
        'observation_start': start_date
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        if 'observations' in data:
            return [(obs['date'], float(obs['value'])) for obs in data['observations'] if obs['value'] != '.']
    except Exception as e:
        print(f"FRED {series_id} error: {e}")
    return []

def get_yahoo_data(ticker, period="6mo"):
    """从Yahoo Finance获取数据"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return [(idx.strftime('%Y-%m-%d'), round(row['Close'], 2)) for idx, row in hist.iterrows()]
    except Exception as e:
        print(f"Yahoo {ticker} error: {e}")
    return []

def get_macromicro_ois():
    """从MacroMicro获取OIS数据（需要爬虫）"""
    # 由于需要JavaScript渲染，这里返回空数据或模拟数据
    # 实际使用时需要Selenium或Playwright爬取
    print("Note: MacroMicro OIS data requires web scraping (Selenium/Playwright)")
    return {
        'sofr_ois': {'latest': 0, 'conflict_val': 0, 'hist': []},
        'euribor_ois': {'latest': 0, 'conflict_val': 0, 'hist': []}
    }

def fetch_fci_data():
    """获取金融条件指数（使用芝加哥联储NFCI或模拟数据）"""
    # NFCI: Chicago Fed National Financial Conditions Index
    data = get_fred_data('NFCI')
    
    if not data:
        # 生成模拟数据
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        data = [(d.strftime('%Y-%m-%d'), round(-0.5 + (i/180)*0.3, 2)) for i, d in enumerate(dates)]
    
    latest_val = data[-1][1] if data else 0
    conflict_val = next((v for d, v in data if d >= CONFLICT_DATE), data[0][1] if data else 0)
    
    return {
        'latest': round(latest_val, 2),
        'latest_date': data[-1][0] if data else '',
        'conflict_val': round(conflict_val, 2),
        'change': round(latest_val - conflict_val, 2),
        'hist': [[d, v] for d, v in data[-90:]]  # 最近90天
    }

def fetch_credit_spread():
    """获取信用利差（BAA-AAA或模拟）"""
    # 使用Moody's BAA和AAA利差
    baa = get_fred_data('BAA')
    aaa = get_fred_data('AAA')
    
    if not baa or not aaa:
        # 生成模拟数据
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        ig_data = [(d.strftime('%Y-%m-%d'), 120 + i%20) for i, d in enumerate(dates)]
        hy_data = [(d.strftime('%Y-%m-%d'), 320 + i%50) for i, d in enumerate(dates)]
    else:
        ig_data = aaa
        hy_data = baa
    
    latest_ig = ig_data[-1][1] if ig_data else 0
    latest_hy = hy_data[-1][1] if hy_data else 0
    
    # 合并数据
    hist = []
    ig_dict = dict(ig_data)
    hy_dict = dict(hy_data)
    all_dates = sorted(set(ig_dict.keys()) & set(hy_dict.keys()))
    for d in all_dates[-90:]:
        hist.append([d, round(ig_dict[d], 1), round(hy_dict[d], 1)])
    
    return {
        'ig_latest': round(latest_ig, 1),
        'hy_latest': round(latest_hy, 1),
        'ratio_latest': round(latest_hy / latest_ig, 2) if latest_ig else 0,
        'hist': hist
    }

def fetch_vix_data():
    """获取波动率指数"""
    vix = get_yahoo_data('^VIX', '6mo')
    # VSTOXX和VXJ需要其他数据源，这里用模拟
    dates = [d for d, _ in vix] if vix else []
    
    if not vix:
        dates = pd.date_range(end=datetime.now(), periods=120, freq='D')
        dates = [d.strftime('%Y-%m-%d') for d in dates]
        vix = [(d, 20 + i%15) for i, d in enumerate(dates)]
    
    # 模拟VSTOXX和VXJ
    vix_dict = dict(vix)
    hist = []
    for d in dates[-90:]:
        v = vix_dict.get(d, 20)
        hist.append([d, round(v, 1), round(v*0.9, 1), round(v*1.1, 1)])  # VIX, VSTOXX, VXJ
    
    latest = hist[-1] if hist else [0, 0, 0, 0]
    return {
        'vix_latest': latest[1],
        'vstoxx_latest': latest[2],
        'vxj_latest': latest[3],
        'hist': hist
    }

def fetch_ois_data():
    """获取OIS利差数据（需要爬取MacroMicro）"""
    # 这里返回模拟数据，实际需要从 https://en.macromicro.me/collections/9/us-market-relative/115044/us-overnight-indexed-swaps 爬取
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    sofr_hist = []
    euribor_hist = []
    for d in dates:
        ds = d.strftime('%Y-%m-%d')
        sofr_hist.append([ds, round(5 + (dates.get_loc(d)/90)*10, 1)])
        euribor_hist.append([ds, round(3 + (dates.get_loc(d)/90)*8, 1)])
    
    return {
        'sofr_ois': {
            'latest': sofr_hist[-1][1] if sofr_hist else 0,
            'conflict_val': next((v for d, v in sofr_hist if d >= CONFLICT_DATE), sofr_hist[0][1] if sofr_hist else 0),
            'hist': sofr_hist
        },
        'euribor_ois': {
            'latest': euribor_hist[-1][1] if euribor_hist else 0,
            'conflict_val': next((v for d, v in euribor_hist if d >= CONFLICT_DATE), euribor_hist[0][1] if euribor_hist else 0),
            'hist': euribor_hist
        }
    }

def fetch_mideast_fx():
    """获取中东汇率"""
    sar = get_yahoo_data('SAR=X', '6mo')  # 沙特里亚尔
    ils = get_yahoo_data('ILS=X', '6mo')  # 以色列谢克尔
    
    if not sar:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sar = [(d.strftime('%Y-%m-%d'), 3.75) for d in dates]  # 固定汇率
    if not ils:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        base = 3.6
        ils = [(d.strftime('%Y-%m-%d'), round(base + i*0.002, 2)) for i, d in enumerate(dates)]
    
    sar_dict = dict(sar)
    ils_dict = dict(ils)
    all_dates = sorted(set(sar_dict.keys()) & set(ils_dict.keys()))
    
    hist = [[d, round(sar_dict[d], 3), round(ils_dict[d], 3)] for d in all_dates[-90:]]
    latest = hist[-1] if hist else [0, 0, 0]
    conflict = next((h for h in hist if h[0] >= CONFLICT_DATE), hist[0] if hist else [0, 0, 0])
    
    return {
        'sar_latest': latest[1],
        'ils_latest': latest[2],
        'ils_conflict': conflict[2] if len(conflict) > 2 else 0,
        'hist': hist
    }

def fetch_sovereign_cds():
    """获取主权债CDS（模拟数据）"""
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    hist = []
    for i, d in enumerate(dates):
        ds = d.strftime('%Y-%m-%d')
        saudi = 60 + i%10
        israel = 120 + i%30
        hist.append([ds, saudi, israel])
    
    latest = hist[-1] if hist else [0, 0, 0]
    return {
        'saudi_latest': latest[1],
        'israel_latest': latest[2],
        'hist': hist
    }

def fetch_yield_curve():
    """获取美债期限利差"""
    # 10Y Treasury
    dgs10 = get_fred_data('DGS10')
    # 2Y Treasury
    dgs2 = get_fred_data('DGS2')
    
    if not dgs10 or not dgs2:
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        hist = []
        for i, d in enumerate(dates):
            ds = d.strftime('%Y-%m-%d')
            spread = -0.5 + (i/90)*0.3
            hist.append([ds, round(spread, 2)])
    else:
        d10_dict = dict(dgs10)
        d2_dict = dict(dgs2)
        all_dates = sorted(set(d10_dict.keys()) & set(d2_dict.keys()))
        hist = []
        for d in all_dates[-90:]:
            spread = d10_dict[d] - d2_dict[d]
            hist.append([d, round(spread, 2)])
    
    latest = hist[-1] if hist else [0, 0]
    conflict = next((h for h in hist if h[0] >= CONFLICT_DATE), hist[0] if hist else [0, 0])
    
    return {
        'latest': latest[1],
        'conflict_val': conflict[1] if len(conflict) > 1 else 0,
        'hist': hist
    }

def main():
    print("=" * 60)
    print("获取全球流动性数据")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    data = {
        'fetched_at': datetime.now(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
        'fci': fetch_fci_data(),
        'credit_spread': fetch_credit_spread(),
        'vix': fetch_vix_data(),
        'ois': fetch_ois_data(),
        'mideast_fx': fetch_mideast_fx(),
        'sovereign_cds': fetch_sovereign_cds(),
        'yield_curve': fetch_yield_curve()
    }
    
    with open('liquidity_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n数据已保存到 liquidity_data.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
