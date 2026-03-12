#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试获取Polymarket网页内容
"""

import requests
import re
import json

url = "https://polymarket.com/zh/iran"

print(f"尝试获取: {url}")
print("=" * 60)

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    print(f"状态码: {resp.status_code}")
    print(f"内容长度: {len(resp.text)} 字符")
    
    if resp.status_code == 200:
        # 尝试提取JSON数据
        # Polymarket通常会在页面中嵌入JSON数据
        html = resp.text
        
        # 查找可能的市场数据
        # 查找slug模式
        slugs = re.findall(r'/event/([^/"\s]+)', html)
        print(f"\n找到 {len(slugs)} 个可能的slug:")
        for s in slugs[:10]:
            print(f"  - {s}")
        
        # 查找问题文本
        questions = re.findall(r'"question":\s*"([^"]+)"', html)
        print(f"\n找到 {len(questions)} 个问题:")
        for q in questions[:5]:
            print(f"  - {q}")
        
        # 保存HTML供分析
        with open("iran_page.html", "w", encoding="utf-8") as f:
            f.write(html[:50000])  # 只保存前50000字符
        print("\n已保存页面内容到 iran_page.html")
        
except Exception as e:
    print(f"错误: {e}")
