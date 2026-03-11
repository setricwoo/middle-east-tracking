#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 数据自动更新脚本
运行: python update_polymarket_data.py
"""

import subprocess
import sys
import io

# 设置 stdout 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    print("=== 开始更新 Polymarket 数据 ===\n")
    
    # 1. 获取最新数据
    print("[1/2] 获取伊朗相关事件...")
    result = subprocess.run([sys.executable, "fetch_iran_events_v2.py"], 
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return 1
    
    # 2. 生成 HTML
    print("[2/2] 生成 HTML 页面...")
    result = subprocess.run([sys.executable, "build_polymarket_html_v2.py"],
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return 1
    
    print("\n=== 更新完成 ===")
    print("生成的文件:")
    print("  - iran_events.json (数据文件)")
    print("  - polymarket_events.html (展示页面)")
    print("\n在浏览器中打开 polymarket_events.html 查看最新数据")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
