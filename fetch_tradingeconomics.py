#!/usr/bin/env python3
"""
Fetch commodity historical data from tradingeconomics.com
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "commodities_data.json"

# Commodity configuration - grouped for display
COMMODITY_GROUPS = {
    "oil": {
        "name": "Crude Oil Prices",
        "symbols": ["CL1:COM", "CO1:COM"],  # WTI, Brent
        "labels": ["WTI Crude", "Brent Crude"],
        "unit": "USD/barrel"
    },
    "gas": {
        "name": "Natural Gas Prices",
        "symbols": ["NG1:COM", "TTFMF:COM", "NBP:COM"],
        "labels": ["US Natural Gas", "TTF", "UK NBP"],
        "unit": "USD/MMBtu"
    },
    "naphtha_propane": {
        "name": "Naphtha & Propane",
        "symbols": ["NAP:COM", "PROP:COM"],
        "labels": ["Naphtha", "Propane"],
        "unit": "USD/ton"
    },
    "methanol_ethanol": {
        "name": "Methanol & Ethanol",
        "symbols": ["METH:COM", "ETH:COM"],
        "labels": ["Methanol", "Ethanol"],
        "unit": "USD/gallon"
    },
    "aluminum_urea": {
        "name": "Aluminum & Urea",
        "symbols": ["ALU:COM", "UREA:COM"],
        "labels": ["Aluminum", "Urea"],
        "unit": "USD/ton"
    },
    "soybean_wheat": {
        "name": "Soybean & Wheat",
        "symbols": ["S1:COM", "W1:COM"],
        "labels": ["Soybean", "Wheat"],
        "unit": "cents/bushel"
    }
}

async def fetch_commodity_data(page, symbol):
    """Fetch historical data for a single commodity"""
    url = f"https://tradingeconomics.com/commodity/{symbol.lower().replace(':', '-')}"
    
    try:
        print(f"  Fetching {symbol}...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)
        
        # Extract historical data from page
        data = await page.evaluate("""
            () => {
                const result = { dates: [], values: [] };
                
                // Try to extract from Highcharts config
                const scripts = document.querySelectorAll('script');
                for (let script of scripts) {
                    const text = script.textContent || '';
                    
                    // Match Highcharts series data
                    const match = text.match(/series:\\s*\\[\\s*{[^}]*data:\\s*(\\[[^\\]]+\\])/);
                    if (match) {
                        try {
                            const dataStr = match[1].replace(/'/g, '"');
                            const data = JSON.parse(dataStr);
                            if (Array.isArray(data) && data.length > 0) {
                                // Get last 90 days
                                const recent = data.slice(-90);
                                recent.forEach(point => {
                                    if (Array.isArray(point) && point.length >= 2) {
                                        result.dates.push(new Date(point[0]).toISOString().slice(0, 10));
                                        result.values.push(parseFloat(point[1]));
                                    }
                                });
                                return result;
                            }
                        } catch(e) {}
                    }
                }
                
                // Fallback: extract from table
                const rows = document.querySelectorAll('table tr');
                for (let row of rows) {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const dateText = cells[0].textContent.trim();
                        const valueText = cells[1].textContent.trim().replace(/,/g, '');
                        const value = parseFloat(valueText);
                        if (!isNaN(value) && dateText.match(/\\d{4}/)) {
                            result.dates.push(dateText);
                            result.values.push(value);
                        }
                    }
                }
                
                return result;
            }
        """)
        
        if data and len(data.get('values', [])) > 0:
            print(f"    OK: got {len(data['values'])} records")
            return data
        else:
            print(f"    No data")
            return None
            
    except Exception as e:
        print(f"    Error: {e}")
        return None

async def fetch_all_commodities():
    """Fetch all commodity data"""
    print("=" * 60)
    print("Fetching commodity data from tradingeconomics.com")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        result = {
            "updated": datetime.now().isoformat(),
            "source": "tradingeconomics.com",
            "groups": {}
        }
        
        for group_key, group_config in COMMODITY_GROUPS.items():
            print(f"\\n{group_config['name']}:")
            group_data = {
                "name": group_config["name"],
                "unit": group_config["unit"],
                "symbols": []
            }
            
            for i, symbol in enumerate(group_config["symbols"]):
                data = await fetch_commodity_data(page, symbol)
                if data:
                    group_data["symbols"].append({
                        "symbol": symbol,
                        "label": group_config["labels"][i],
                        "dates": data["dates"],
                        "values": data["values"]
                    })
                await asyncio.sleep(1)
            
            result["groups"][group_key] = group_data
        
        await browser.close()
    
    # Save data
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\\n{'=' * 60}")
    print(f"Data saved: {DATA_FILE}")
    print(f"{'=' * 60}")
    
    return result

if __name__ == "__main__":
    asyncio.run(fetch_all_commodities())
