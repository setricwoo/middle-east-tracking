#!/usr/bin/env python3
"""
Generate demo financial data based on current market levels
Uses realistic market data as of March 2025
"""

import json
import random
from datetime import datetime, timedelta

def generate_price_series(start_price, days, volatility, trend=0):
    """Generate realistic price series"""
    values = []
    price = start_price
    for _ in range(days):
        change = random.gauss(trend, volatility)
        price = price * (1 + change)
        values.append(round(price, 2))
    return values

def generate_demo_data():
    """Generate demo financial market data"""
    
    # Generate last 180 days of dates
    end_date = datetime(2025, 3, 24)
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(179, -1, -1)]
    
    # Stock indices - realistic levels as of March 2025
    stocks = {
        'us_sp500': {
            'symbol': '^GSPC',
            'name': '标普500',
            'country': '美国',
            'dates': dates,
            'values': generate_price_series(5700, 180, 0.008, 0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'us_nasdaq': {
            'symbol': '^IXIC',
            'name': '纳斯达克',
            'country': '美国',
            'dates': dates,
            'values': generate_price_series(18000, 180, 0.012, 0.0003),
            'latest': 0,
            'change_pct': 0
        },
        'europe_stoxx50': {
            'symbol': '^STOXX50E',
            'name': '欧洲STOXX 50',
            'country': '欧洲',
            'dates': dates,
            'values': generate_price_series(5200, 180, 0.009, 0.0001),
            'latest': 0,
            'change_pct': 0
        },
        'germany_dax': {
            'symbol': '^GDAXI',
            'name': '德国DAX',
            'country': '德国',
            'dates': dates,
            'values': generate_price_series(22800, 180, 0.010, 0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'uk_ftse': {
            'symbol': '^FTSE',
            'name': '英国富时100',
            'country': '英国',
            'dates': dates,
            'values': generate_price_series(8600, 180, 0.007, 0.0001),
            'latest': 0,
            'change_pct': 0
        },
        'japan_nikkei': {
            'symbol': '^N225',
            'name': '日经225',
            'country': '日本',
            'dates': dates,
            'values': generate_price_series(37500, 180, 0.011, 0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'china_shanghai': {
            'symbol': '000001.SS',
            'name': '上证指数',
            'country': '中国',
            'dates': dates,
            'values': generate_price_series(3350, 180, 0.009, -0.0001),
            'latest': 0,
            'change_pct': 0
        },
        'china_hangseng': {
            'symbol': '^HSI',
            'name': '恒生指数',
            'country': '中国香港',
            'dates': dates,
            'values': generate_price_series(21000, 180, 0.013, 0.0003),
            'latest': 0,
            'change_pct': 0
        },
        'korea_kospi': {
            'symbol': '^KS11',
            'name': '韩国KOSPI',
            'country': '韩国',
            'dates': dates,
            'values': generate_price_series(2650, 180, 0.010, -0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'india_nifty': {
            'symbol': '^NSEI',
            'name': '印度Nifty50',
            'country': '印度',
            'dates': dates,
            'values': generate_price_series(22500, 180, 0.009, 0.0004),
            'latest': 0,
            'change_pct': 0
        }
    }
    
    # Calculate latest and change for stocks
    for key, data in stocks.items():
        values = data['values']
        data['latest'] = values[-1]
        data['change_pct'] = round(((values[-1] - values[0]) / values[0]) * 100, 2)
    
    # Treasury yields (in percentage points)
    bonds = {
        'us_10y': {
            'symbol': '^TNX',
            'name': '美国10年期国债',
            'country': '美国',
            'maturity': '10Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(430, 180, 0.015, 0.0001)],
            'latest': 0,
            'change_pct': 0
        },
        'us_2y': {
            'symbol': '^IRX',
            'name': '美国2年期国债',
            'country': '美国',
            'maturity': '2Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(400, 180, 0.018, 0.0001)],
            'latest': 0,
            'change_pct': 0
        },
        'germany_10y': {
            'symbol': 'GDBR10',
            'name': '德国10年期国债',
            'country': '德国',
            'maturity': '10Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(280, 180, 0.012, 0.00005)],
            'latest': 0,
            'change_pct': 0
        },
        'uk_10y': {
            'symbol': 'GUKG10',
            'name': '英国10年期国债',
            'country': '英国',
            'maturity': '10Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(460, 180, 0.014, 0.0001)],
            'latest': 0,
            'change_pct': 0
        },
        'japan_10y': {
            'symbol': 'GJGB10',
            'name': '日本10年期国债',
            'country': '日本',
            'maturity': '10Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(150, 180, 0.008, 0.00002)],
            'latest': 0,
            'change_pct': 0
        },
        'china_10y': {
            'symbol': 'CN10YT',
            'name': '中国10年期国债',
            'country': '中国',
            'maturity': '10Y',
            'dates': dates,
            'values': [round(v/100, 2) for v in generate_price_series(180, 180, 0.010, -0.00005)],
            'latest': 0,
            'change_pct': 0
        }
    }
    
    # Calculate latest and change for bonds
    for key, data in bonds.items():
        values = data['values']
        data['latest'] = values[-1]
        data['change_pct'] = round(((values[-1] - values[0]) / values[0]) * 100, 2)
    
    # Sector ETFs
    sectors = {
        'technology': {
            'symbol': 'XLK',
            'name': '科技板块',
            'etf': 'XLK',
            'dates': dates,
            'values': generate_price_series(220, 180, 0.015, 0.0005),
            'latest': 0,
            'change_pct': 0
        },
        'financials': {
            'symbol': 'XLF',
            'name': '金融板块',
            'etf': 'XLF',
            'dates': dates,
            'values': generate_price_series(48, 180, 0.012, 0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'energy': {
            'symbol': 'XLE',
            'name': '能源板块',
            'etf': 'XLE',
            'dates': dates,
            'values': generate_price_series(92, 180, 0.018, 0.0001),
            'latest': 0,
            'change_pct': 0
        },
        'healthcare': {
            'symbol': 'XLV',
            'name': '医疗保健',
            'etf': 'XLV',
            'dates': dates,
            'values': generate_price_series(140, 180, 0.010, 0.0002),
            'latest': 0,
            'change_pct': 0
        },
        'consumer_discretionary': {
            'symbol': 'XLY',
            'name': '非必需消费',
            'etf': 'XLY',
            'dates': dates,
            'values': generate_price_series(190, 180, 0.013, 0.0003),
            'latest': 0,
            'change_pct': 0
        },
        'industrials': {
            'symbol': 'XLI',
            'name': '工业板块',
            'etf': 'XLI',
            'dates': dates,
            'values': generate_price_series(125, 180, 0.011, 0.0002),
            'latest': 0,
            'change_pct': 0
        }
    }
    
    # Calculate latest and change for sectors
    for key, data in sectors.items():
        values = data['values']
        data['latest'] = values[-1]
        data['change_pct'] = round(((values[-1] - values[0]) / values[0]) * 100, 2)
    
    result = {
        'updated': datetime.now().isoformat(),
        'stocks': stocks,
        'bonds': bonds,
        'sectors': sectors
    }
    
    return result

def save_and_embed(data):
    """Save data and embed in HTML"""
    import re
    
    # Save to JSON
    output_file = 'financial_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {output_file}")
    
    # Convert to JS
    js_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    
    # Update HTML
    html_path = 'data-tracking.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace or add STATIC_FINANCIAL_DATA
    pattern = r'let STATIC_FINANCIAL_DATA = \{.*?\};'
    replacement = f'let STATIC_FINANCIAL_DATA = {js_data};'
    
    if re.search(pattern, html_content, re.DOTALL):
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        print(f"Updated STATIC_FINANCIAL_DATA in {html_path}")
    else:
        marker = '/* STATIC_DATA_END */'
        new_marker = f'let STATIC_FINANCIAL_DATA = {js_data};\n    /* STATIC_DATA_END */'
        html_content = html_content.replace(marker, new_marker)
        print(f"Added STATIC_FINANCIAL_DATA to {html_path}")
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    print("Generating demo financial data...")
    data = generate_demo_data()
    
    print("\nSummary:")
    print(f"  Stock indices: {len(data['stocks'])}")
    print(f"  Bond yields: {len(data['bonds'])}")
    print(f"  Sector ETFs: {len(data['sectors'])}")
    
    save_and_embed(data)
    print("\nDone! Data embedded in data-tracking.html")

if __name__ == '__main__':
    main()
