#!/usr/bin/env python3
"""
从 tradingeconomics.com 获取商品历史数据
使用 Playwright 点击历史数据按钮并提取今年以来数据
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "commodities_data.json"

# 商品配置 - 分组显示
COMMODITY_GROUPS = {
    "oil": {
        "name": "原油价格",
        "urls": [
            ("WTI原油", "https://tradingeconomics.com/commodity/wti-crude-oil"),
            ("布伦特原油", "https://tradingeconomics.com/commodity/brent-crude-oil")
        ],
        "unit": "美元/桶"
    },
    "gas": {
        "name": "天然气价格",
        "urls": [
            ("美国天然气", "https://tradingeconomics.com/commodity/natural-gas"),
            ("欧洲TTF", "https://tradingeconomics.com/commodity/eu-natural-gas"),
        ],
        "unit": "美元/百万英热"
    },
    "naphtha_propane": {
        "name": "石脑油与丙烷",
        "urls": [
            ("新加坡石脑油", "https://tradingeconomics.com/commodity/naphtha"),
            ("蒙特贝尔维尤丙烷", "https://tradingeconomics.com/commodity/propane"),
        ],
        "unit": "美元/吨"
    },
    "methanol_ethanol": {
        "name": "甲醇与乙醇",
        "urls": [
            ("中国甲醇", "https://tradingeconomics.com/commodity/methanol"),
            ("美国乙醇", "https://tradingeconomics.com/commodity/ethanol"),
        ],
        "unit": "美元/加仑"
    },
    "aluminum_urea": {
        "name": "铝与尿素",
        "urls": [
            ("铝", "https://tradingeconomics.com/commodity/aluminum"),
            ("尿素", "https://tradingeconomics.com/commodity/urea"),
        ],
        "unit": "美元/吨"
    },
    "soybean_wheat": {
        "name": "大豆与小麦",
        "urls": [
            ("大豆", "https://tradingeconomics.com/commodity/soybeans"),
            ("小麦", "https://tradingeconomics.com/commodity/wheat"),
        ],
        "unit": "美分/蒲式耳"
    }
}

async def fetch_historical_data(page, name, url):
    """获取单个商品的历史数据"""
    try:
        print(f"  Fetching {name}...")
        
        # 访问页面
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        # 点击 "Historical" 或 "Data" 按钮（如果有）
        try:
            # 尝试点击 Historical 标签
            hist_tab = await page.query_selector('text=Historical')
            if hist_tab:
                await hist_tab.click()
                await asyncio.sleep(2)
                print(f"    Clicked Historical tab")
        except:
            pass
        
        # 等待数据加载
        await asyncio.sleep(2)
        
        # 提取历史数据
        data = await page.evaluate("""
            () => {
                const result = { dates: [], values: [], latest: null };
                
                // 尝试从 Highcharts 图表中提取
                const chartDiv = document.querySelector('#chart-container');
                if (chartDiv && window.Highcharts && window.Highcharts.charts) {
                    const charts = window.Highcharts.charts;
                    for (let chart of charts) {
                        if (chart && chart.series && chart.series[0]) {
                            const series = chart.series[0];
                            const points = series.points || series.data || [];
                            for (let point of points) {
                                if (point.x && point.y) {
                                    const date = new Date(point.x);
                                    const dateStr = date.toISOString().slice(0, 10);
                                    result.dates.push(dateStr);
                                    result.values.push(parseFloat(point.y));
                                }
                            }
                            if (result.values.length > 0) {
                                result.latest = result.values[result.values.length - 1];
                            }
                            return result;
                        }
                    }
                }
                
                // 从表格中提取数据
                const tables = document.querySelectorAll('table');
                for (let table of tables) {
                    const rows = table.querySelectorAll('tr');
                    for (let row of rows) {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 2) {
                            const dateText = cells[0].textContent.trim();
                            const valueText = cells[1].textContent.trim().replace(/,/g, '');
                            
                            // 解析日期
                            let dateMatch = dateText.match(/(\\d{4})[\\/-](\\d{1,2})[\\/-](\\d{1,2})/);
                            if (!dateMatch) {
                                dateMatch = dateText.match(/(\\d{1,2})[\\/-](\\d{1,2})[\\/-](\\d{4})/);
                            }
                            
                            const value = parseFloat(valueText);
                            if (dateMatch && !isNaN(value)) {
                                const dateStr = `${dateMatch[1]}-${dateMatch[2].padStart(2, '0')}-${dateMatch[3].padStart(2, '0')}`;
                                result.dates.unshift(dateStr);  // 表格通常是倒序
                                result.values.unshift(value);
                            }
                        }
                    }
                    if (result.values.length > 0) break;
                }
                
                if (result.values.length > 0) {
                    result.latest = result.values[result.values.length - 1];
                }
                
                return result;
            }
        """)
        
        if data and len(data.get('values', [])) > 0:
            print(f"    OK: got {len(data['values'])} records, latest: {data['latest']}")
            return data
        else:
            print(f"    No data found")
            return None
            
    except Exception as e:
        print(f"    Error: {e}")
        return None

async def fetch_all_commodities():
    """获取所有商品数据"""
    print("=" * 60)
    print("Fetching commodity data from tradingeconomics.com")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
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
            
            for name, url in group_config["urls"]:
                data = await fetch_historical_data(page, name, url)
                if data and len(data.get('values', [])) > 0:
                    # 只保留今年以来的数据
                    current_year = datetime.now().year
                    filtered_dates = []
                    filtered_values = []
                    
                    for i, date_str in enumerate(data['dates']):
                        if date_str.startswith(str(current_year)):
                            filtered_dates.append(date_str)
                            filtered_values.append(data['values'][i])
                    
                    if len(filtered_values) > 0:
                        group_data["symbols"].append({
                            "symbol": name,
                            "label": name,
                            "dates": filtered_dates,
                            "values": filtered_values,
                            "latest": filtered_values[-1] if filtered_values else None
                        })
                
                await asyncio.sleep(2)  # 避免请求过快
            
            result["groups"][group_key] = group_data
        
        await browser.close()
    
    # 保存数据
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\\n{'=' * 60}")
    print(f"Data saved: {DATA_FILE}")
    print(f"{'=' * 60}")
    
    return result

if __name__ == "__main__":
    asyncio.run(fetch_all_commodities())
