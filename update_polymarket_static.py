#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 静态网页数据更新脚本
从 Gamma API 获取数据，更新 polymarket_static.html
"""

import requests
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# ==================== 配置 ====================
GAMMA_API = "https://gamma-api.polymarket.com"
HTML_FILE = "polymarket_static.html"

# 事件配置
EVENT_CONFIG = {
    "trump_military": {
        "search_queries": ["trump military action iran", "trump end military iran"],
        "title_keywords": ["trump", "military", "iran"],
        "date_labels": {
            "march 31": "3月31日",
            "april 30": "4月30日",
            "june 30": "6月30日"
        },
        "colors": ["#3b82f6", "#10b981", "#f59e0b"]
    },
    "ceasefire": {
        "search_queries": ["us iran ceasefire", "iran ceasefire"],
        "title_keywords": ["ceasefire", "iran"],
        "date_labels": {
            "march 31": "3月31日",
            "april 30": "4月30日",
            "may 31": "5月31日",
            "june 30": "6月30日"
        },
        "colors": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
    },
    "hormuz": {
        "search_queries": ["hormuz strait traffic", "hormuz strait resume"],
        "title_keywords": ["hormuz", "strait"],
        "date_labels": {
            "april 30": "4月30日"
        },
        "colors": ["#3b82f6"]
    },
    "oil_march": {
        "search_queries": ["crude oil march", "oil price march"],
        "title_keywords": ["crude", "oil", "march"],
        "price_labels": [90, 100, 110, 120, 130],
        "colors": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
    },
    "oil_june": {
        "search_queries": ["crude oil june", "oil price june"],
        "title_keywords": ["crude", "oil", "june"],
        "price_labels": [100, 110, 120, 130, 150],
        "colors": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
    }
}


def search_events(query: str, limit: int = 20) -> List[Dict]:
    """搜索事件"""
    url = f"{GAMMA_API}/events"
    params = {
        "search": query,
        "active": "true",
        "limit": limit,
        "order": "volume",
        "sort": "desc"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  搜索失败 {query}: {e}")
        return []


def get_event_details(event_id: str) -> Dict:
    """获取事件详情"""
    url = f"{GAMMA_API}/events/{event_id}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取事件详情失败 {event_id}: {e}")
        return {}


def get_price_history(market_id: str) -> List[Dict]:
    """获取价格历史"""
    url = f"{GAMMA_API}/markets/{market_id}/prices"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取价格历史失败 {market_id}: {e}")
        return []


def extract_yes_probability(market: Dict) -> float:
    """提取Yes概率"""
    outcome_prices = market.get("outcomePrices", [])
    if outcome_prices and isinstance(outcome_prices, list) and len(outcome_prices) > 0:
        try:
            return float(outcome_prices[0]) * 100
        except:
            pass
    return 0


def match_date_in_question(question: str, date_labels: Dict) -> Optional[tuple]:
    """匹配问题中的日期"""
    q = question.lower()
    for key, label in date_labels.items():
        if key in q:
            return (key, label)
    return None


def match_price_in_question(question: str, price_labels: List[int]) -> Optional[int]:
    """匹配问题中的价格"""
    match = re.search(r'\$(\d+)', question)
    if match:
        price = int(match.group(1))
        if price in price_labels:
            return price
    return None


def format_volume(vol: float) -> str:
    """格式化交易量"""
    if vol >= 1000000:
        return f"${vol/1000000:.1f}M"
    elif vol >= 1000:
        return f"${vol/1000:.0f}K"
    else:
        return f"${vol:.0f}"


def get_value_class(prob: float) -> str:
    """根据概率获取样式类"""
    if prob >= 60:
        return "high"
    elif prob >= 30:
        return "medium"
    return "low"


def process_event(event_key: str, config: Dict) -> Dict:
    """处理单个事件，获取所有市场数据"""
    print(f"\n{'='*50}")
    print(f"处理事件: {event_key}")
    print(f"{'='*50}")

    result = {
        "prob_cards": [],
        "chart_datasets": [],
        "chart_labels": [],
        "total_volume": 0,
        "markets": []
    }

    is_price_event = "price_labels" in config
    date_labels = config.get("date_labels", {})
    price_labels = config.get("price_labels", [])
    colors = config.get("colors", [])

    # 搜索事件
    for query in config["search_queries"]:
        print(f"  搜索: {query}")
        events = search_events(query)

        for event in events:
            title = event.get("title", "").lower()
            # 检查是否匹配关键词
            if not all(kw in title for kw in config["title_keywords"]):
                continue

            event_id = event.get("id")
            print(f"  找到事件: {event.get('title', 'N/A')[:60]}...")

            # 获取详情
            details = get_event_details(event_id)
            markets = details.get("markets", [])

            for market in markets:
                question = market.get("question", "")
                prob = extract_yes_probability(market)
                volume = float(market.get("volumeNum", 0) or 0)
                market_id = market.get("id")

                # 匹配日期或价格
                if is_price_event:
                    price = match_price_in_question(question, price_labels)
                    if price:
                        result["prob_cards"].append({
                            "label": f"${price}",
                            "prob": prob,
                            "volume": volume,
                            "match_key": price,
                            "market_id": market_id
                        })
                else:
                    date_match = match_date_in_question(question, date_labels)
                    if date_match:
                        key, label = date_match
                        result["prob_cards"].append({
                            "label": label,
                            "prob": prob,
                            "volume": volume,
                            "match_key": key,
                            "market_id": market_id
                        })

                result["total_volume"] += volume

            break  # 找到一个匹配的事件就够了
        else:
            continue
        break

    # 去重并排序
    seen = set()
    unique_cards = []
    for card in result["prob_cards"]:
        if card["match_key"] not in seen:
            seen.add(card["match_key"])
            unique_cards.append(card)

    if is_price_event:
        unique_cards.sort(key=lambda x: x["match_key"])
    else:
        # 按日期顺序排序
        date_order = list(date_labels.keys())
        unique_cards.sort(key=lambda x: date_order.index(x["match_key"]) if x["match_key"] in date_order else 999)

    result["prob_cards"] = unique_cards

    # 获取价格历史（只取前几个市场）
    print(f"  获取价格历史...")
    for i, card in enumerate(unique_cards[:5]):  # 最多5条线
        market_id = card.get("market_id")
        if not market_id:
            continue

        print(f"    获取 {card['label']} 的历史数据...")
        history = get_price_history(market_id)

        if history and len(history) > 0:
            # 提取时间和价格
            labels = []
            prices = []

            for p in history:
                ts = p.get("timestamp") or p.get("time")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        labels.append(dt.strftime("%m-%d %H:%M"))
                    except:
                        continue

                # 提取Yes价格
                outcome_prices = p.get("outcomePrices", {})
                if isinstance(outcome_prices, dict):
                    yes_price = outcome_prices.get("Yes", 0)
                else:
                    yes_price = p.get("price", 0)

                try:
                    prices.append(float(yes_price) * 100)
                except:
                    prices.append(0)

            if labels and prices:
                if not result["chart_labels"]:
                    result["chart_labels"] = labels

                result["chart_datasets"].append({
                    "label": card["label"],
                    "data": prices,
                    "borderColor": colors[i % len(colors)],
                    "backgroundColor": colors[i % len(colors)] + "20",
                    "borderWidth": 2,
                    "fill": True,
                    "tension": 0.4,
                    "pointRadius": 0,
                    "pointHoverRadius": 4
                })

        # 避免请求过快
        import time
        time.sleep(0.3)

    return result


def generate_prob_cards_html(cards: List[Dict]) -> str:
    """生成概率卡片HTML"""
    html = ""
    for card in cards:
        value_class = get_value_class(card["prob"])
        volume_str = format_volume(card.get("volume", 0))
        html += f'''
            <div class="prob-card">
                <div class="label">{card["label"]}</div>
                <div class="value {value_class}">{card["prob"]:.1f}%</div>
                <div class="volume">{volume_str}</div>
            </div>'''
    return html


def update_html(all_data: Dict) -> bool:
    """更新HTML文件"""
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"无法读取HTML文件: {e}")
        return False

    # 1. 更新时间
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = re.sub(
        r'<div class="header-right" id="updateTime">[^<]*</div>',
        f'<div class="header-right" id="updateTime">更新时间: {now}</div>',
        html
    )

    # 2. 更新每个事件
    for event_key, data in all_data.items():
        # 更新概率卡片
        cards_html = generate_prob_cards_html(data["prob_cards"])
        cards_pattern = rf'(<div class="prob-grid" id="{event_key}_cards">)(.*?)(</div>)'
        html = re.sub(cards_pattern, f'\\1{cards_html}\\3', html, flags=re.DOTALL)

        # 更新交易量
        volume_str = format_volume(data["total_volume"])
        volume_pattern = rf'(<div class="volume-amount" id="{event_key}_volume">)[^<]*(</div>)'
        html = re.sub(volume_pattern, f'\\1{volume_str}\\2', html)

    # 3. 更新图表数据
    # 找到 chartData 对象并替换
    chart_data_js = "const chartData = {\n"
    for event_key, data in all_data.items():
        datasets_json = json.dumps(data["chart_datasets"], ensure_ascii=False, indent=12)
        labels_json = json.dumps(data["chart_labels"], ensure_ascii=False)
        chart_data_js += f"            {event_key}: {{ labels: {labels_json}, datasets: {datasets_json} }},\n"
    chart_data_js += "        };"

    html = re.sub(
        r'const chartData = \{[^}]+\};',
        chart_data_js,
        html,
        flags=re.DOTALL
    )

    # 保存文件
    try:
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    except Exception as e:
        print(f"保存HTML失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Polymarket 静态网页数据更新")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_data = {}

    for event_key, config in EVENT_CONFIG.items():
        try:
            data = process_event(event_key, config)
            all_data[event_key] = data

            print(f"\n  结果: {len(data['prob_cards'])} 个概率卡片, {len(data['chart_datasets'])} 条历史曲线")
            for card in data["prob_cards"]:
                print(f"    {card['label']}: {card['prob']:.1f}%")

        except Exception as e:
            print(f"处理 {event_key} 失败: {e}")
            all_data[event_key] = {
                "prob_cards": [],
                "chart_datasets": [],
                "chart_labels": [],
                "total_volume": 0
            }

    # 更新HTML
    print("\n" + "=" * 60)
    print("更新HTML文件...")
    if update_html(all_data):
        print(f"[OK] 已更新: {HTML_FILE}")
    else:
        print("[FAIL] 更新失败")

    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    main()
