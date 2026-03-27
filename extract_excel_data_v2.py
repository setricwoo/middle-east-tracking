#!/usr/bin/env python3
"""
Extract data from 全球市场.xlsx with proper grouping and ordering
"""

import pandas as pd
import json
from datetime import datetime

def extract_commodity_data(df):
    """Extract commodity price data and group by category"""
    
    # Row 1 contains commodity names, row 3 units, row 5 sources
    names = df.iloc[1, :].tolist()
    units = df.iloc[3, :].tolist()
    sources = df.iloc[5, :].tolist()
    
    commodities = []
    
    # Process each column (skip first which is date)
    for col_idx in range(1, min(14, len(df.columns))):
        name = names[col_idx] if col_idx < len(names) else f'商品{col_idx}'
        unit = units[col_idx] if col_idx < len(units) else ''
        source = sources[col_idx] if col_idx < len(sources) else ''
        
        if pd.isna(name) or name == '':
            continue
        
        # Skip financial condition index (金融状况指数)
        if '金融状况' in str(name) or '金融状况指数' in str(name):
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
        
        # Reverse to make chronological order (oldest first)
        dates.reverse()
        values.reverse()
        
        # Keep up to 2 years of data for time range selection
        if len(values) > 730:
            dates = dates[-730:]
            values = values[-730:]
        
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
        'oil': {
            'name': '原油价格',
            'unit': '美元/桶',
            'items': []
        },
        'gas': {
            'name': '天然气价格',
            'unit': '',
            'items': []
        },
        'naphtha_lpg': {
            'name': '石脑油与LPG',
            'unit': '',
            'items': []
        },
        'methanol_ethylene': {
            'name': '甲醇与乙烯',
            'unit': '',
            'items': []
        },
        'aluminum_urea': {
            'name': '铝与尿素',
            'unit': '',
            'items': []
        },
        'grains': {
            'name': '大豆与小麦',
            'unit': '',
            'items': []
        }
    }
    
    for comm in commodities:
        name = comm['name']
        if '原油' in name or '布伦特' in name or 'WTI' in name:
            groups['oil']['items'].append(comm)
        elif '天然气' in name or '气' in name:
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
    groups = {k: v for k, v in groups.items() if len(v['items']) > 0}
    
    return groups

def extract_liquidity_data(df):
    """Extract liquidity data, excluding specific items"""
    names = df.iloc[1, :].tolist()
    
    indicators = []
    
    for col_idx in range(1, min(12, len(df.columns))):
        name = names[col_idx] if col_idx < len(names) else f'指标{col_idx}'
        
        if pd.isna(name) or name == '' or 'Unnamed' in str(name):
            continue
        
        # Skip excluded items
        if '沙特' in str(name) or '美元兑沙特' in str(name):
            continue
        if '全球股市隐含波动率' in str(name) and ('VIX' not in str(name) and 'VSTOXX' not in str(name)):
            continue
        
        dates = []
        values = []
        
        for row_idx in range(2, len(df)):
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
                'unit': '',
                'dates': dates,
                'values': values
            })
    
    return indicators

def main():
    file_path = '全球市场.xlsx'
    
    print("Reading Excel file...")
    
    # Read commodity price sheet
    try:
        df_commodity = pd.read_excel(file_path, sheet_name=0, header=None)
        commodity_groups = extract_commodity_data(df_commodity)
        print(f"Extracted commodity groups:")
        for key, group in commodity_groups.items():
            print(f"  - {group['name']}: {len(group['items'])} items")
    except Exception as e:
        print(f"Error reading commodity sheet: {e}")
        commodity_groups = {}
    
    # Read liquidity sheet
    try:
        df_liquidity = pd.read_excel(file_path, sheet_name=1, header=None)
        liquidity_data = extract_liquidity_data(df_liquidity)
        print(f"Extracted {len(liquidity_data)} liquidity indicators")
        for l in liquidity_data[:5]:
            print(f"  - {l['name']}: {len(l['values'])} data points")
    except Exception as e:
        print(f"Error reading liquidity sheet: {e}")
        liquidity_data = []
    
    # Prepare output
    output = {
        'updated': datetime.now().isoformat(),
        'source': '全球市场.xlsx',
        'commodity_groups': commodity_groups,
        'liquidity': liquidity_data
    }
    
    # Save to JSON
    output_file = 'excel_market_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to {output_file}")
    
    # Generate JavaScript embedded data
    js_data = json.dumps(output, ensure_ascii=False, separators=(',', ':'))
    
    # Read existing HTML
    with open('data-tracking.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace STATIC_EXCEL_DATA
    import re
    pattern = r'let STATIC_EXCEL_DATA = \{.*?\};'
    replacement = f'let STATIC_EXCEL_DATA = {js_data};'
    
    if re.search(pattern, html_content):
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    else:
        # Add before STATIC_DATA_END
        insert_marker = '/* STATIC_DATA_END */'
        js_block = f'    let STATIC_EXCEL_DATA = {js_data};\n    /* STATIC_DATA_END */'
        html_content = html_content.replace(insert_marker, js_block)
    
    # Save modified HTML
    with open('data-tracking.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML updated with Excel data (grouped)")

if __name__ == '__main__':
    main()
