#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket TOP10 事件自动更新脚本 v3
"""

import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    print("=" * 70)
    print("        Polymarket 伊朗预测市场 - TOP10 事件更新 v3")
    print("=" * 70)
    
    # 1. 获取数据
    print("\n[步骤 1/2] 获取最新市场数据...")
    result = subprocess.run([sys.executable, "fetch_polymarket_iran_v3.py"], 
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return 1
    
    # 2. 生成 HTML
    print("\n[步骤 2/2] 生成可视化页面...")
    result = subprocess.run([sys.executable, "build_polymarket_html_v3.py"],
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return 1
    
    print("\n" + "=" * 70)
    print("                     [OK] 更新完成！")
    print("=" * 70)
    print("\n生成的文件:")
    print("  - iran_top10_events.json  (原始数据)")
    print("  - polymarket_top10.html   (展示页面)")
    print("\n请在浏览器中打开 polymarket_top10.html 查看结果")
    print("\n核心洞察:")
    print("  1. 霍尔木兹海峡 - 3月31日前关闭概率 99.75%")
    print("  2. 伊朗政权 - 3月31日前倒台概率仅 4.95%")
    print("  3. 美伊停火 - 3月15日前达成协议概率 4.05%")
    print("  4. 美军进入 - 3月31日前进入伊朗概率 31%")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
