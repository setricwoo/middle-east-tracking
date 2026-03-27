#!/usr/bin/env python3
"""
Extract data from 全球市场.xlsx and prepare for HTML embedding
"""

import pandas as pd
import json
from datetime import datetime

def extract_commodity_data(df):
    """Extract commodity price data from dataframe"""
    # Row 1 contains commodity names
    # Row 3 contains units
    # Row 6 onwards contains date and values
    
    commodities = []
    
    # Get commodity info from rows 1, 3, 5
    names = df.iloc[1, :].tolist()
    units = df.iloc[3, :].tolist()
    sources = df.iloc[5, :].tolist()
    
    # Get data rows (from row 6 onwards)
    data_rows = df.iloc[6:, :].copy()
    
    # Process each commodity column (skip first column which is date)
    for col_idx in range(1, min(14, len(df.columns))):
        name = names[col_idx] if col_idx < len(names) else f'商品{col_idx}'
        unit = units[col_idx] if col_idx < len(units) else ''
        source = sources[col_idx] if col_idx < len(sources) else ''
        
        # Skip if no name
        if pd.isna(name) or name == '':
            continue
        
        # Get dates and values
        dates = []
        values = []
        
        for row_idx in range(6, len(df)):
            date_val = df.iloc[row_idx, 0]
            price_val = df.iloc[row_idx, col_idx]
            
            # Check if date is valid
            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
                # Check if price is valid number
                if pd.notna(price_val) and isinstance(price_val, (int, float)):
                    dates.append(date_str)
                    values.append(round(float(price_val), 2))
        
        # Only add if we have data
        if len(values) > 0:
            commodities.append({
                'name': str(name),
                'unit': str(unit) if pd.notna(unit) else '',
                'source': str(source) if pd.notna(source) else '',
                'dates': dates[:90],  # Last 90 days
                'values': values[:90]
            })
    
    return commodities

def extract_liquidity_data(df):
    """Extract liquidity data from dataframe"""
    # Row 1 contains indicator names (Row 0 is 'Wind')
    names = df.iloc[1, :].tolist()
    
    indicators = []
    
    # Process each column (skip first which is date/index column)
    for col_idx in range(1, min(12, len(df.columns))):
        name = names[col_idx] if col_idx < len(names) else f'指标{col_idx}'
        
        # Skip if no valid name
        if pd.isna(name) or name == '' or 'Unnamed' in str(name):
            continue
        
        dates = []
        values = []
        
        # Start from row 2 (after header rows)
        for row_idx in range(2, len(df)):
            date_val = df.iloc[row_idx, 0]
            data_val = df.iloc[row_idx, col_idx]
            
            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
                if pd.notna(data_val) and isinstance(data_val, (int, float)):
                    dates.append(date_str)
                    values.append(round(float(data_val), 4))
        
        if len(values) > 0:
            indicators.append({
                'name': str(name),
                'unit': '',
                'dates': dates[:90],
                'values': values[:90]
            })
    
    return indicators

def main():
    file_path = '全球市场.xlsx'
    
    print("Reading Excel file...")
    
    # Read commodity price sheet
    try:
        df_commodity = pd.read_excel(file_path, sheet_name=0, header=None)
        commodity_data = extract_commodity_data(df_commodity)
        print(f"Extracted {len(commodity_data)} commodities")
        for c in commodity_data[:5]:
            print(f"  - {c['name']}: {len(c['values'])} data points")
    except Exception as e:
        print(f"Error reading commodity sheet: {e}")
        commodity_data = []
    
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
        'commodities': commodity_data,
        'liquidity': liquidity_data
    }
    
    # Save to JSON
    output_file = 'excel_market_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to {output_file}")
    
    # Also generate JavaScript embedded data
    js_data = json.dumps(output, ensure_ascii=False, separators=(',', ':'))
    
    # Read existing HTML
    with open('data-tracking.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace or add STATIC_EXCEL_DATA
    if 'STATIC_EXCEL_DATA' in html_content:
        # Replace existing
        import re
        pattern = r'let STATIC_EXCEL_DATA = \{.*?\};'
        replacement = f'let STATIC_EXCEL_DATA = {js_data};'
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    else:
        # Add before STATIC_DATA_END
        insert_marker = '/* STATIC_DATA_END */'
        js_block = f'    let STATIC_EXCEL_DATA = {js_data};\n    /* STATIC_DATA_END */'
        html_content = html_content.replace(insert_marker, js_block)
    
    # Save modified HTML
    with open('data-tracking.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML updated with Excel data")

if __name__ == '__main__':
    main()
