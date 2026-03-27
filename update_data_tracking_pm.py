#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 data-tracking.html 的 Polymarket tab
使用与 update_polymarket_html.py 相同的方法
"""

import requests
import json
import time
import re
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Any

# Polymarket APIs
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# 事件配置
EVENT_CONFIGS = [
    {
        "key": "trump-announces-end-of-military-operations-against-iran-by",
        "title": "特朗普宣布结束对伊朗军事行动",
        "subtitle": "不同截止日期的概率预测",
        "date_labels": ["March 15th", "March 31st", "April 30th", "June 30th"],
        "chart_id": "pm-chart-1"
    },
    {
        "key": "us-x-iran-ceasefire-by",
        "title": "美伊停火时间",
        "subtitle": "不同截止日期的概率预测",
        "date_labels": ["March 31", "April 30", "June 30"],
        "chart_id": "pm-chart-2"
    },
    {
        "key": "avg-of-ships-transiting-strait-of-hormuz-end-of-march",
        "title": "3月霍尔木兹海峡船舶数量",
        "subtitle": "平均每日通过船舶数量的概率分布 (Top 6)",
        "type": "ships",
        "chart_id": "pm-chart-3"
    },
    {
        "key": "strait-of-hormuz-traffic-returns-to-normal-by-april-30",
        "title": "霍尔木兹海峡恢复正常",
        "subtitle": "4月30日前恢复正常的概率",
        "type": "simple",
        "chart_id": "pm-chart-4"
    },
    {
        "key": "will-crude-oil-cl-hit-by-end-of-march",
        "title": "3月原油价格预测",
        "subtitle": "CL期货价格3月底前触碰概率 (Top 6)",
        "type": "oil",
        "chart_id": "pm-chart-5"
    },
    {
        "key": "cl-hit-jun-2026",
        "title": "6月原油价格预测",
        "subtitle": "CL期货价格6月底前触碰概率 (Top 6)",
        "type": "oil",
        "chart_id": "pm-chart-6"
    }
]

# 中期选举事件
MIDTERM_EVENT_ID = "32228"  # Balance of Power: 2026 Midterms

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}

# 颜色配置
COLORS = ['#2563eb', '#4f46e5', '#0ea5e9', '#10b981', '#059669', '#f59e0b', '#dc2626', '#8b5cf6']


def get_event_by_slug(slug: str, max_retries: int = 2) -> Dict:
    """通过slug获取事件数据"""
    url = f"{GAMMA_API}/events"
    params = {"slug": slug, "_s": "slug"}
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.3)
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                event = data[0]
                event_id = event.get("id")
                if event_id:
                    time.sleep(0.2)
                    detail_url = f"{GAMMA_API}/events/{event_id}"
                    detail_resp = requests.get(detail_url, headers=HEADERS, timeout=15)
                    if detail_resp.status_code == 200:
                        return detail_resp.json()
                return event
            return {}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print(f"  获取失败 {slug}: {e}")
                return {}


def get_event_by_id(event_id: str, max_retries: int = 2) -> Dict:
    """通过ID获取事件数据"""
    url = f"{GAMMA_API}/events/{event_id}"
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.3)
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print(f"  获取失败 event_id={event_id}: {e}")
                return {}


def get_price_history(token_id: str, interval: str = "all", max_retries: int = 1) -> List[Dict]:
    """获取价格历史数据"""
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.1)
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("history", [])
        except:
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            for alt_interval in ["max", "1d"]:
                try:
                    params["interval"] = alt_interval
                    resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data.get("history", [])
                except:
                    pass
            return []


def parse_json_field(field) -> List:
    """解析JSON字段"""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return []
    elif isinstance(field, list):
        return field
    return []


def fetch_event_data(config: Dict) -> Dict:
    """获取单个事件数据"""
    slug = config["key"]
    print(f"获取: {slug}")
    
    event = get_event_by_slug(slug)
    if not event:
        return None
    
    event_title = event.get("title", "")
    markets = event.get("markets", [])
    
    markets_data = []
    for m in markets:
        question = m.get("question", "")
        outcomes = parse_json_field(m.get("outcomes"))
        outcome_prices = parse_json_field(m.get("outcomePrices"))
        clob_token_ids = parse_json_field(m.get("clobTokenIds"))
        volume = m.get("volume", "0")
        
        market_info = {
            "question": question,
            "outcomes": {},
            "volume": volume,
            "closed": m.get("closed", False),
        }
        
        for i, outcome_name in enumerate(outcomes):
            token_id = clob_token_ids[i] if i < len(clob_token_ids) else ""
            current_price = 0.0
            if i < len(outcome_prices):
                try:
                    current_price = float(outcome_prices[i])
                except:
                    pass
            
            price_history = []
            if token_id and not m.get("closed", False):
                history = get_price_history(token_id)
                beijing_tz = ZoneInfo("Asia/Shanghai")
                for h in history:
                    try:
                        ts = h.get("t", 0)
                        price = h.get("p", 0)
                        dt = datetime.fromtimestamp(ts, tz=beijing_tz)
                        price_history.append({
                            "time": dt.strftime('%m-%d %H:%M'),
                            "timestamp": ts,
                            "price": round(price * 100, 2)
                        })
                    except:
                        pass
            
            market_info["outcomes"][outcome_name] = {
                "currentPrice": round(current_price * 100, 2),
                "priceHistory": price_history
            }
        
        markets_data.append(market_info)
    
    return {
        "title": event_title,
        "markets": markets_data
    }


def fetch_midterm_data() -> Dict:
    """获取中期选举数据"""
    print(f"获取中期选举数据 (event_id={MIDTERM_EVENT_ID})")
    
    event = get_event_by_id(MIDTERM_EVENT_ID)
    if not event:
        return None
    
    event_title = event.get("title", "")
    markets = event.get("markets", [])
    
    print(f"  找到 {len(markets)} 个市场")
    
    markets_data = []
    for m in markets:
        question = m.get("question", "")
        outcomes = parse_json_field(m.get("outcomes"))
        outcome_prices = parse_json_field(m.get("outcomePrices"))
        clob_token_ids = parse_json_field(m.get("clobTokenIds"))
        
        market_info = {
            "question": question,
            "outcomes": {},
            "closed": m.get("closed", False),
        }
        
        for i, outcome_name in enumerate(outcomes):
            token_id = clob_token_ids[i] if i < len(clob_token_ids) else ""
            current_price = 0.0
            if i < len(outcome_prices):
                try:
                    current_price = float(outcome_prices[i])
                except:
                    pass
            
            price_history = []
            if token_id and not m.get("closed", False):
                history = get_price_history(token_id)
                beijing_tz = ZoneInfo("Asia/Shanghai")
                for h in history:
                    try:
                        ts = h.get("t", 0)
                        price = h.get("p", 0)
                        dt = datetime.fromtimestamp(ts, tz=beijing_tz)
                        price_history.append({
                            "time": dt.strftime('%m-%d %H:%M'),
                            "timestamp": ts,
                            "price": round(price * 100, 2)
                        })
                    except:
                        pass
            
            market_info["outcomes"][outcome_name] = {
                "currentPrice": round(current_price * 100, 2),
                "priceHistory": price_history
            }
        
        markets_data.append(market_info)
    
    return {
        "title": event_title,
        "markets": markets_data
    }


def generate_event_chart_js(config: Dict, data: Dict) -> str:
    """生成事件图表的JavaScript代码"""
    chart_id = config["chart_id"]
    markets = data.get("markets", [])
    
    # 根据类型处理
    if config.get("type") == "ships":
        return generate_ships_chart_js(chart_id, markets)
    elif config.get("type") == "oil":
        return generate_oil_chart_js(chart_id, markets, config["title"], config["subtitle"])
    elif config.get("type") == "simple":
        return generate_simple_chart_js(chart_id, markets)
    else:
        return generate_date_chart_js(config, markets)


def generate_date_chart_js(config: Dict, markets: List[Dict]) -> str:
    """生成日期类型图表"""
    chart_id = config["chart_id"]
    date_labels = config.get("date_labels", [])
    
    # 匹配市场
    matched_markets = []
    for label in date_labels:
        for m in markets:
            q = m.get("question", "").lower()
            if label.lower() in q and not m.get("closed", False):
                yes_price = m.get("outcomes", {}).get("Yes", {}).get("currentPrice", 0)
                history = m.get("outcomes", {}).get("Yes", {}).get("priceHistory", [])
                matched_markets.append({
                    "label": label,
                    "price": yes_price,
                    "history": history
                })
                break
    
    if not matched_markets:
        return f"// 无数据 for {chart_id}"
    
    # 收集时间点和数据
    all_times = set()
    for m in matched_markets:
        for h in m["history"]:
            all_times.add(h["time"])
    sorted_times = sorted(list(all_times))
    
    # 生成数据集
    datasets = []
    for i, m in enumerate(matched_markets):
        color = COLORS[i % len(COLORS)]
        data_points = {h["time"]: h["price"] for h in m["history"]}
        data_arr = [data_points.get(t, None) for t in sorted_times]
        
        datasets.append({
            "label": m["label"],
            "data": data_arr,
            "borderColor": color,
            "backgroundColor": color + "20",
            "borderWidth": 2,
            "tension": 0.3,
            "pointRadius": 0,
            "pointHoverRadius": 4,
            "fill": False
        })
    
    return f'''
    // {chart_id} - 日期类型图表
    (function() {{
        const ctx = document.getElementById('{chart_id}');
        if (!ctx) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(sorted_times)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                spanGaps: true,
                interaction: {{ intersect: false, mode: 'index' }},
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 10, font: {{ size: 10 }} }} }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }}, callback: function(v) {{ return v + '%'; }} }}, min: 0, max: 100 }}
                }}
            }}
        }});
    }})();
'''


def generate_ships_chart_js(chart_id: str, markets: List[Dict]) -> str:
    """生成船舶数量图表"""
    all_markets = []
    for m in markets:
        q = m.get("question", "")
        yes_price = m.get("outcomes", {}).get("Yes", {}).get("currentPrice", 0)
        history = m.get("outcomes", {}).get("Yes", {}).get("priceHistory", [])
        
        match = re.search(r'between (\d+) and (\d+)', q.lower())
        if match:
            label = f"{match.group(1)}-{match.group(2)}"
        elif "60 or more" in q.lower():
            label = "60+"
        else:
            continue
        
        all_markets.append({
            "label": label,
            "price": yes_price,
            "history": history
        })
    
    if not all_markets:
        return f"// 无数据 for {chart_id}"
    
    # 按概率排序取前6
    all_markets.sort(key=lambda x: x["price"], reverse=True)
    top_markets = all_markets[:6]
    
    # 收集时间点和数据
    all_times = set()
    for m in top_markets:
        for h in m["history"]:
            all_times.add(h["time"])
    sorted_times = sorted(list(all_times))
    
    # 生成数据集
    datasets = []
    for i, m in enumerate(top_markets):
        color = COLORS[i % len(COLORS)]
        data_points = {h["time"]: h["price"] for h in m["history"]}
        data_arr = [data_points.get(t, None) for t in sorted_times]
        
        datasets.append({
            "label": m["label"],
            "data": data_arr,
            "borderColor": color,
            "backgroundColor": color + "20",
            "borderWidth": 2,
            "tension": 0.3,
            "pointRadius": 0,
            "pointHoverRadius": 4,
            "fill": False
        })
    
    return f'''
    // {chart_id} - 船舶数量图表
    (function() {{
        const ctx = document.getElementById('{chart_id}');
        if (!ctx) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(sorted_times)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                spanGaps: true,
                interaction: {{ intersect: false, mode: 'index' }},
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 10, font: {{ size: 10 }} }} }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }}, callback: function(v) {{ return v + '%'; }} }}, min: 0, max: 100 }}
                }}
            }}
        }});
    }})();
'''


def generate_oil_chart_js(chart_id: str, markets: List[Dict], title: str, subtitle: str) -> str:
    """生成原油价格图表"""
    all_prices = []
    for m in markets:
        q = m.get("question", "")
        yes_price = m.get("outcomes", {}).get("Yes", {}).get("currentPrice", 0)
        history = m.get("outcomes", {}).get("Yes", {}).get("priceHistory", [])
        
        match = re.search(r'\$(\d+)', q)
        if match:
            price_label = f"${match.group(1)}"
            if 0 < yes_price < 100:
                all_prices.append({
                    "label": price_label,
                    "price": yes_price,
                    "history": history
                })
    
    if not all_prices:
        return f"// 无数据 for {chart_id}"
    
    # 按概率排序取前6
    all_prices.sort(key=lambda x: x["price"], reverse=True)
    top_prices = all_prices[:6]
    
    # 收集时间点和数据
    all_times = set()
    for p in top_prices:
        for h in p["history"]:
            all_times.add(h["time"])
    sorted_times = sorted(list(all_times))
    
    # 生成数据集
    datasets = []
    for i, p in enumerate(top_prices):
        color = COLORS[i % len(COLORS)]
        data_points = {h["time"]: h["price"] for h in p["history"]}
        data_arr = [data_points.get(t, None) for t in sorted_times]
        
        datasets.append({
            "label": p["label"],
            "data": data_arr,
            "borderColor": color,
            "backgroundColor": color + "20",
            "borderWidth": 2,
            "tension": 0.3,
            "pointRadius": 0,
            "pointHoverRadius": 4,
            "fill": False
        })
    
    return f'''
    // {chart_id} - 原油价格图表
    (function() {{
        const ctx = document.getElementById('{chart_id}');
        if (!ctx) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(sorted_times)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                spanGaps: true,
                interaction: {{ intersect: false, mode: 'index' }},
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 10, font: {{ size: 10 }} }} }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }}, callback: function(v) {{ return v + '%'; }} }}, min: 0, max: 100 }}
                }}
            }}
        }});
    }})();
'''


def generate_simple_chart_js(chart_id: str, markets: List[Dict]) -> str:
    """生成简单Yes/No图表"""
    if not markets:
        return f"// 无数据 for {chart_id}"
    
    m = markets[0]
    outcomes = m.get("outcomes", {})
    yes_history = outcomes.get("Yes", {}).get("priceHistory", [])
    
    labels = [h["time"] for h in yes_history]
    data = [h["price"] for h in yes_history]
    
    color = COLORS[0]
    
    dataset_js = json.dumps([{
        "label": "Yes (%)",
        "data": data,
        "borderColor": color,
        "backgroundColor": color + "20",
        "borderWidth": 2,
        "tension": 0.3,
        "pointRadius": 0,
        "pointHoverRadius": 4,
        "fill": False
    }])
    
    return f'''
    // {chart_id} - 简单Yes/No图表
    (function() {{
        const ctx = document.getElementById('{chart_id}');
        if (!ctx) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: {dataset_js}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                spanGaps: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 10, font: {{ size: 10 }} }} }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }}, callback: function(v) {{ return v + '%'; }} }}, min: 0, max: 100 }}
                }}
            }}
        }});
    }})();
'''


def generate_midterm_chart_js(data: Dict) -> str:
    """生成中期选举图表 - 四个组合放在一张图"""
    chart_id = "pm-chart-midterm"
    markets = data.get("markets", [])
    
    # 定义四种组合的映射
    combo_map = {
        "D Senate, D House": "D+S D+H",
        "D Senate, R House": "D+S R+H",
        "R Senate, D House": "R+S D+H",
        "R Senate, R House": "R+S R+H"
    }
    
    combos = []
    for m in markets:
        q = m.get("question", "")
        for full_name, short_name in combo_map.items():
            if full_name in q:
                outcomes = m.get("outcomes", {})
                # 找到Yes或第一个outcome
                yes_outcome = outcomes.get("Yes", {})
                if not yes_outcome:
                    yes_outcome = list(outcomes.values())[0] if outcomes else {}
                
                price = yes_outcome.get("currentPrice", 0)
                history = yes_outcome.get("priceHistory", [])
                
                combos.append({
                    "label": short_name,
                    "full_label": full_name,
                    "price": price,
                    "history": history
                })
                break
    
    if not combos:
        return f"// 无中期选举数据"
    
    # 收集时间点和数据
    all_times = set()
    for c in combos:
        for h in c["history"]:
            all_times.add(h["time"])
    sorted_times = sorted(list(all_times))
    
    # 生成数据集
    datasets = []
    for i, c in enumerate(combos):
        color = COLORS[i % len(COLORS)]
        data_points = {h["time"]: h["price"] for h in c["history"]}
        data_arr = [data_points.get(t, None) for t in sorted_times]
        
        datasets.append({
            "label": c["label"],
            "data": data_arr,
            "borderColor": color,
            "backgroundColor": color + "20",
            "borderWidth": 2,
            "tension": 0.3,
            "pointRadius": 0,
            "pointHoverRadius": 4,
            "fill": False
        })
    
    return f'''
    // {chart_id} - 中期选举图表
    (function() {{
        const ctx = document.getElementById('{chart_id}');
        if (!ctx) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(sorted_times)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                spanGaps: true,
                interaction: {{ intersect: false, mode: 'index' }},
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 10, font: {{ size: 10 }} }} }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,0.1)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }}, callback: function(v) {{ return v + '%'; }} }}, min: 0, max: 100 }}
                }}
            }}
        }});
    }})();
'''


def main():
    print("=" * 60)
    print("Data Tracking Polymarket Tab 更新器")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取所有事件数据
    all_data = {}
    for config in EVENT_CONFIGS:
        data = fetch_event_data(config)
        if data:
            all_data[config["key"]] = data
        time.sleep(0.5)
    
    # 获取中期选举数据
    midterm_data = fetch_midterm_data()
    if midterm_data:
        all_data["midterm"] = midterm_data
    
    # 生成JavaScript代码
    print("\n生成图表代码...")
    chart_scripts = []
    
    for config in EVENT_CONFIGS:
        key = config["key"]
        if key in all_data:
            js = generate_event_chart_js(config, all_data[key])
            chart_scripts.append(js)
    
    # 中期选举图表
    if "midterm" in all_data:
        js = generate_midterm_chart_js(all_data["midterm"])
        chart_scripts.append(js)
    
    # 保存数据到JSON
    json_filename = "polymarket_tab_data.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "fetchedAt": datetime.now().isoformat(),
            "events": all_data
        }, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {json_filename}")
    
    # 更新HTML文件
    print("\n更新 data-tracking.html...")
    
    with open('data-tracking.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 生成新的图表脚本部分
    new_script = "\n".join(chart_scripts)
    
    # 替换旧的 initPolymarketCharts 函数
    pattern = r'// Polymarket 图表初始化[\s\S]*?function initPolymarketCharts\(\)[\s\S]*?^\}'
    
    replacement = f'''// Polymarket 图表初始化 - 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}
function initPolymarketCharts() {{
    {new_script}
}}'''
    
    import re
    html_content = re.sub(pattern, replacement, html_content, flags=re.MULTILINE)
    
    # 保存更新后的HTML
    with open('data-tracking.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML已更新: data-tracking.html")
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
