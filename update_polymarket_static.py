#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 polymarket.html 提取数据并生成浅色主题的 polymarket_static.html
"""

import re
import json
from datetime import datetime

def extract_chart_data(html_content):
    """从HTML中提取图表数据"""
    charts = {}

    # 提取特朗普军事行动图表
    trump_match = re.search(
        r'new Chart\(document\.getElementById\([\'"]chart_trump_end_military[\'"]\).*?'
        r'labels:\s*\[(.*?)\].*?'
        r'datasets:\s*(\[.*?\])\s*\}',
        html_content, re.DOTALL
    )
    if trump_match:
        labels_str = trump_match.group(1)
        datasets_str = trump_match.group(2)

        # 解析labels
        labels = re.findall(r'"([^"]+)"', labels_str)

        # 解析datasets
        datasets = []
        for ds_match in re.finditer(r'\{[^}]*"label":\s*"([^"]+)"[^}]*"data":\s*\[([^\]]+)\][^}]*\}', datasets_str, re.DOTALL):
            label = ds_match.group(1)
            data_str = ds_match.group(2)
            data = [float(x) for x in re.findall(r'[\d.]+', data_str)]
            datasets.append({"label": label, "data": data})

        if labels and datasets:
            charts["trump_military"] = {"labels": labels, "datasets": datasets}

    return charts

def extract_prob_data(html_content):
    """从HTML中提取概率数据"""
    probs = {}

    # 提取特朗普军事行动概率
    trump_section = re.search(
        r'<!-- 特朗普宣布结束对伊朗军事行动 -->(.*?)</div>\s*</div>\s*<div class="chart-container">',
        html_content, re.DOTALL
    )
    if trump_section:
        section_html = trump_section.group(1)
        items = []
        for match in re.finditer(
            r'<span[^>]*text-slate-300[^>]*>([^<]+):</span>\s*'
            r'<span[^>]*font-bold[^>]*>([^<]+)%</span>\s*'
            r'<span[^>]*text-slate-500[^>]*>\(([^)]+)\)</span>',
            section_html
        ):
            label = match.group(1).strip()
            prob = float(match.group(2))
            volume = match.group(3).strip()
            items.append({"label": label, "prob": prob, "volume": volume})
        if items:
            probs["trump_military"] = items

    return probs

def main():
    print("=" * 60)
    print("从 polymarket.html 提取数据")
    print("=" * 60)

    try:
        with open("polymarket.html", 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"无法读取 polymarket.html: {e}")
        return

    # 提取数据
    chart_data = extract_chart_data(html_content)
    prob_data = extract_prob_data(html_content)

    print(f"\n提取到 {len(chart_data)} 个图表数据")
    print(f"提取到 {len(prob_data)} 个概率数据")

    for key, data in prob_data.items():
        print(f"\n[{key}]")
        for item in data:
            print(f"  {item['label']}: {item['prob']}% ({item['volume']})")

    # 保存提取的数据
    extracted = {
        "charts": chart_data,
        "probs": prob_data,
        "extractedAt": datetime.now().isoformat()
    }

    with open("extracted_polymarket_data.json", 'w', encoding='utf-8') as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: extracted_polymarket_data.json")

if __name__ == "__main__":
    main()
