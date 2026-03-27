#!/usr/bin/env python3
"""
从 MacroMicro 获取 OIS 历史数据
使用 Playwright 抓取 Highcharts 图表数据
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "ois_data.json"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

MACROMICRO_URL = "https://en.macromicro.me/collections/9/us-market-relative/115044/us-overnight-indexed-swaps"


async def fetch_ois_data():
    """获取 OIS 历史数据"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            print("Loading MacroMicro OIS page...")
            
            response = await page.goto(MACROMICRO_URL, wait_until="domcontentloaded", timeout=60000)
            
            if response.status != 200:
                print(f"Error: HTTP {response.status}")
                return None
            
            # 等待图表加载
            await asyncio.sleep(5)
            
            # 从 Highcharts 提取数据
            chart_data = await page.evaluate("""
                () => {
                    const results = [];
                    
                    if (typeof Highcharts !== 'undefined' && Highcharts.charts) {
                        Highcharts.charts.forEach((chart, idx) => {
                            if (!chart) return;
                            
                            const series_data = chart.series?.map(s => {
                                // 获取完整历史数据
                                const data = s.data?.map(point => ({
                                    timestamp: point.x,
                                    date: new Date(point.x).toISOString().split('T')[0],
                                    value: point.y
                                })) || [];
                                
                                return {
                                    name: s.name,
                                    data: data
                                };
                            }) || [];
                            
                            results.push({
                                index: idx,
                                title: chart.options?.title?.text || 'No title',
                                series: series_data
                            });
                        });
                    }
                    
                    return results;
                }
            """)
            
            if not chart_data or len(chart_data) == 0:
                print("No chart data found")
                return None
            
            # 解析数据
            ois_chart = chart_data[0]
            
            result = {
                "updated": datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
                "source": "MacroMicro",
                "url": MACROMICRO_URL,
                "title": ois_chart.get("title", "US Overnight Index Swaps"),
                "tenors": {}
            }
            
            for series in ois_chart.get("series", []):
                tenor_name = series["name"]
                data = series.get("data", [])
                
                if data:
                    latest = data[-1]
                    result["tenors"][tenor_name] = {
                        "latest_rate": latest["value"],
                        "latest_date": latest["date"],
                        "unit": "%",
                        "history": [[d["date"], d["value"]] for d in data]
                    }
            
            # 计算 OIS 利差 (长期 - 短期)
            if "1 Month" in result["tenors"] and "10 Years" in result["tenors"]:
                short_rate = result["tenors"]["1 Month"]["latest_rate"]
                long_rate = result["tenors"]["10 Years"]["latest_rate"]
                result["curve_spread"] = {
                    "value": round(long_rate - short_rate, 4),
                    "short_tenor": "1 Month",
                    "long_tenor": "10 Years",
                    "unit": "%",
                    "interpretation": "正值表示陡峭的OIS曲线"
                }
            
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return None
            
        finally:
            await browser.close()


def calculate_ois_spreads(ois_data: dict) -> dict:
    """计算 OIS 利差"""
    spreads = {}
    
    tenors = ois_data.get("tenors", {})
    
    # 常见的 OIS 利差计算
    spread_configs = [
        ("1 Month", "3 Months", "1M-3M"),
        ("3 Months", "6 Months", "3M-6M"),
        ("6 Months", "1 Year", "6M-1Y"),
        ("1 Year", "2 Years", "1Y-2Y"),
        ("2 Years", "10 Years", "2Y-10Y"),
    ]
    
    for short, long, name in spread_configs:
        if short in tenors and long in tenors:
            short_rate = tenors[short]["latest_rate"]
            long_rate = tenors[long]["latest_rate"]
            spread = long_rate - short_rate
            
            spreads[name] = {
                "spread": round(spread, 4),
                "short_rate": short_rate,
                "long_rate": long_rate,
                "unit": "%",
                "note": f"{long} OIS - {short} OIS"
            }
    
    return spreads


async def main():
    print("=" * 60)
    print("Fetch OIS Data from MacroMicro")
    print(f"Beijing Time: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    data = await fetch_ois_data()
    
    if not data:
        print("\nFailed to fetch OIS data")
        return 1
    
    print(f"\nFound {len(data['tenors'])} OIS tenors:")
    for tenor, info in data["tenors"].items():
        print(f"  {tenor}: {info['latest_rate']}% @ {info['latest_date']}")
    
    # 计算利差
    print("\nCalculating OIS spreads...")
    data["spreads"] = calculate_ois_spreads(data)
    
    for name, spread_data in data["spreads"].items():
        print(f"  {name}: {spread_data['spread']:+.4f}%")
    
    # 保存数据
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to: {DATA_FILE}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
