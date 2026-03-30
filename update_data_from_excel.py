#!/usr/bin/env python3
"""
Update data-tracking.html with latest data from 全球市场.xlsx
Only updates data, does not change page layout or structure
"""

import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path

def extract_commodity_groups(df):
    """Extract commodity data grouped by category, including inflation data"""
    names = df.iloc[1, :].tolist()
    units = df.iloc[3, :].tolist()
    sources = df.iloc[5, :].tolist()
    
    commodities = []
    
    # Read all columns including inflation data (cols 13, 14)
    for col_idx in range(1, min(15, len(df.columns))):  # Changed from 14 to 15
        name = names[col_idx] if col_idx < len(names) else f'商品{col_idx}'
        unit = units[col_idx] if col_idx < len(units) else ''
        source = sources[col_idx] if col_idx < len(sources) else ''
        
        if pd.isna(name) or name == '':
            continue
        
        # Skip financial condition index
        if '金融状况' in str(name):
            continue
        
        dates = []
        values = []
        
        for row_idx in range(6, len(df)):
            date_val = df.iloc[row_idx, 0]
            price_val = df.iloc[row_idx, col_idx]
            
            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
                if pd.notna(price_val) and isinstance(price_val, (int, float)):
                    dates.append(date_str)
                    values.append(round(float(price_val), 2))
        
        # Reverse to chronological order
        dates.reverse()
        values.reverse()
        
        # Keep up to 10 years of data for long-term analysis
        if len(values) > 3650:
            dates = dates[-3650:]
            values = values[-3650:]
        
        if len(values) > 0:
            commodities.append({
                'name': str(name),
                'unit': str(unit) if pd.notna(unit) else '',
                'source': str(source) if pd.notna(source) else '',
                'dates': dates,
                'values': values
            })
    
    # Group commodities
    groups = {
        'oil': {'name': '原油价格', 'unit': '美元/桶', 'items': []},
        'gas': {'name': '天然气价格', 'unit': '', 'items': []},
        'naphtha_lpg': {'name': '石脑油与LPG', 'unit': '', 'items': []},
        'methanol_ethylene': {'name': '甲醇与乙烯', 'unit': '', 'items': []},
        'aluminum_urea': {'name': '铝与尿素', 'unit': '', 'items': []},
        'grains': {'name': '大豆与小麦', 'unit': '', 'items': []},
        'inflation': {'name': '盈亏平衡通胀率', 'unit': '%', 'items': []}  # New group for inflation
    }
    
    for comm in commodities:
        name = comm['name']
        if '盈亏平衡通胀' in name or '通胀' in name:
            groups['inflation']['items'].append(comm)
        elif '原油' in name or '布伦特' in name or 'WTI' in name:
            groups['oil']['items'].append(comm)
        elif '天然气' in name or ('气' in name and '通胀' not in name):
            groups['gas']['items'].append(comm)
        elif '石脑油' in name:
            groups['naphtha_lpg']['items'].append(comm)
        elif 'LPG' in name or '液化石油' in name:
            groups['naphtha_lpg']['items'].append(comm)
        elif '甲醇' in name:
            groups['methanol_ethylene']['items'].append(comm)
        elif '乙烯' in name:
            groups['methanol_ethylene']['items'].append(comm)
        elif '铝' in name and 'LME' in name:
            groups['aluminum_urea']['items'].append(comm)
        elif '尿素' in name:
            groups['aluminum_urea']['items'].append(comm)
        elif '大豆' in name:
            groups['grains']['items'].append(comm)
        elif '小麦' in name:
            groups['grains']['items'].append(comm)
    
    # Remove empty groups
    return {k: v for k, v in groups.items() if len(v['items']) > 0}

def extract_liquidity_indicators(df):
    """Extract liquidity indicators with units from Excel row 2"""
    names = df.iloc[1, :].tolist()
    units = df.iloc[2, :].tolist()  # 单位在第3行（index 2）
    indicators = []

    for col_idx in range(1, min(12, len(df.columns))):
        name = names[col_idx] if col_idx < len(names) else f'指标{col_idx}'
        unit = units[col_idx] if col_idx < len(units) else ''

        if pd.isna(name) or name == '' or 'Unnamed' in str(name):
            continue

        # Skip excluded items
        if '沙特' in str(name) or '美元兑沙特' in str(name):
            continue
        if '全球股市隐含波动率' in str(name) and ('VIX' not in str(name) and 'VSTOXX' not in str(name)):
            continue

        dates = []
        values = []

        for row_idx in range(3, len(df)):  # 数据从第4行（index 3）开始
            date_val = df.iloc[row_idx, 0]
            data_val = df.iloc[row_idx, col_idx]

            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
                if pd.notna(data_val) and isinstance(data_val, (int, float)):
                    dates.append(date_str)
                    values.append(round(float(data_val), 4))

        # Reverse to chronological order
        dates.reverse()
        values.reverse()

        if len(values) > 0:
            indicators.append({
                'name': str(name),
                'unit': str(unit) if pd.notna(unit) and unit else '',
                'dates': dates,
                'values': values
            })

    return indicators


def extract_financial_data(df):
    """Extract financial market data (stocks, bonds, etc.)

    全球市场sheet结构：
    - Row 0: "Wind"
    - Row 1: 指标名称
    - Row 2: 更新日期
    - Row 3-28985: 数据（最新在前，日期递减）
    - Row 28986+: 重复数据（跳过）
    """
    names = df.iloc[1, :].tolist() if len(df) > 1 else []

    stocks = {}
    bonds = {}

    # 找到日期开始递增的位置（重复数据的开始）
    cutoff_row = len(df)
    prev_date = None
    for i in range(3, len(df)):
        d = df.iloc[i, 0]
        if isinstance(d, datetime):
            if prev_date and d > prev_date:
                cutoff_row = i
                break
            prev_date = d

    print(f"  [INFO] Financial data cutoff at row {cutoff_row}")

    for col_idx in range(1, len(df.columns)):
        name = names[col_idx] if col_idx < len(names) else f'指标{col_idx}'

        if pd.isna(name) or name == '' or 'Unnamed' in str(name):
            continue

        dates = []
        values = []

        # 只读取到cutoff_row，避免重复数据
        for row_idx in range(3, cutoff_row):
            date_val = df.iloc[row_idx, 0]
            data_val = df.iloc[row_idx, col_idx]

            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
                if pd.notna(data_val) and isinstance(data_val, (int, float)):
                    dates.append(date_str)
                    values.append(round(float(data_val), 2))

        # 数据在Excel中是最新在前，需要反转为时间顺序（旧→新）
        dates.reverse()
        values.reverse()

        if len(values) > 0:
            # Determine if stock or bond based on name
            name_str = str(name)
            data_obj = {
                'name': name_str,
                'unit': '',
                'dates': dates,
                'values': values,
                'latest': values[-1] if values else None,  # 最新值在最后一位（反转后）
                'latest_date': dates[-1] if dates else None
            }

            # Classify as stock or bond
            if any(kw in name_str for kw in ['国债', '美债', '收益率', '债券']):
                key = f'bond_{col_idx}'
                bonds[key] = data_obj
            else:
                key = f'stock_{col_idx}'
                stocks[key] = data_obj

    return {'stocks': stocks, 'bonds': bonds}

def update_html_data():
    """Update data in HTML file"""
    excel_path = '全球市场.xlsx'
    html_path = 'data-tracking.html'
    json_path = 'data/excel_history.json'
    
    print(f"Reading {excel_path}...")
    
    # Read Excel data
    try:
        df_commodity = pd.read_excel(excel_path, sheet_name=0, header=None)
        commodity_groups = extract_commodity_groups(df_commodity)
        print(f"[OK] Extracted {sum(len(g['items']) for g in commodity_groups.values())} commodities in {len(commodity_groups)} groups")
    except Exception as e:
        print(f"[ERROR] Error reading commodity sheet: {e}")
        return False
    
    try:
        df_liquidity = pd.read_excel(excel_path, sheet_name=1, header=None)
        liquidity_data = extract_liquidity_indicators(df_liquidity)
        print(f"[OK] Extracted {len(liquidity_data)} liquidity indicators")
    except Exception as e:
        print(f"[ERROR] Error reading liquidity sheet: {e}")
        return False
    
    # Read financial market data (third sheet)
    try:
        df_financial = pd.read_excel(excel_path, sheet_name=2, header=None)
        financial_data = extract_financial_data(df_financial)
        print(f"[OK] Extracted {len(financial_data['stocks'])} stocks and {len(financial_data['bonds'])} bonds")
    except Exception as e:
        print(f"[WARNING] Error reading financial sheet: {e}")
        financial_data = {'stocks': {}, 'bonds': {}}
    
    # Prepare data object
    data = {
        'updated': datetime.now().isoformat(),
        'source': '全球市场.xlsx',
        'commodity_groups': commodity_groups,
        'liquidity': liquidity_data,
        'financial': financial_data
    }
    
    # Convert to JSON string
    js_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    
    # Step 1: Write to separate JSON file
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(js_data)
        print(f"[OK] Data written to {json_path} ({len(js_data)/1024:.1f} KB)")
    except Exception as e:
        print(f"[ERROR] Failed to write JSON file: {e}")
        return False
    
    # Step 2: Update HTML to use fetch instead of embedded data
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace embedded STATIC_EXCEL_DATA with null (data will be loaded via fetch)
    pattern = r'let STATIC_EXCEL_DATA = \{.*?\};'
    replacement = 'let STATIC_EXCEL_DATA = null; // 数据将通过 fetch 加载'
    
    if re.search(pattern, html_content, re.DOTALL):
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        print(f"[OK] Updated {html_path} to use external JSON")
    else:
        # Check if already using null (maybe already converted)
        if 'STATIC_EXCEL_DATA = null' in html_content:
            print(f"[OK] {html_path} already using external JSON")
        else:
            print(f"[WARNING] STATIC_EXCEL_DATA pattern not found, may need manual check")
    
    # Write back HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n[DONE] Data update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"       JSON: {json_path}")
    print(f"       HTML: {html_path}")
    return True

if __name__ == '__main__':
    success = update_html_data()
    exit(0 if success else 1)
