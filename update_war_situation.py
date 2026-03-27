#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 war-situation 页面数据
- 运行 fetch_isw_v2.py 抓取最新数据
- 验证截图质量
- 更新 isw_war_data.json
"""

import subprocess
import json
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("更新 War Situation 数据")
    print("=" * 60)
    
    # 1. 运行抓取脚本
    print("\n[1/3] 抓取 ISW 最新数据...")
    result = subprocess.run([sys.executable, "fetch_isw_v2.py"], 
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print(f"[错误] 抓取失败: {result.stderr}")
        return
    print("[OK] 抓取完成")
    
    # 2. 验证数据文件
    print("\n[2/3] 验证数据...")
    war_data_file = Path("isw_war_data.json")
    if not war_data_file.exists():
        print("[错误] 数据文件不存在")
        return
    
    with open(war_data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    report = data.get("current_report", {})
    charts = report.get("charts", [])
    takeaways = report.get("takeaways", [])
    
    print(f"  报告标题: {report.get('title_zh', 'N/A')}")
    print(f"  报告日期: {report.get('date', 'N/A')}")
    print(f"  Takeaways: {len(takeaways)} 条")
    print(f"  图表: {len(charts)} 张")
    
    # 3. 验证截图
    print("\n[3/3] 验证截图...")
    screenshot_dir = Path("isw_screenshots")
    valid_count = 0
    
    for chart in charts:
        url = chart.get("url", "")
        screenshot_path = Path(url)
        if screenshot_path.exists():
            size = screenshot_path.stat().st_size
            if size > 50000:  # 大于50KB认为有效
                valid_count += 1
            else:
                print(f"  [警告] {url} 文件太小 ({size/1024:.1f}KB)")
        else:
            print(f"  [警告] {url} 不存在")
    
    print(f"[OK] 有效截图: {valid_count}/{len(charts)}")
    
    print("\n" + "=" * 60)
    print("更新完成!")
    print(f"  - 数据文件: isw_war_data.json")
    print(f"  - 截图目录: isw_screenshots/")
    print("=" * 60)

if __name__ == "__main__":
    main()
