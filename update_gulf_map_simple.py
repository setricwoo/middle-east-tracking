#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版海湾原油图谱更新脚本 - 仅更新时间和基础数据
在GitHub Actions中每12小时运行
"""
import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

def get_today_info():
    """获取今日信息"""
    today = datetime.now()
    date_str = today.strftime("%Y年%m月%d日")
    return {
        "date": date_str,
        "today_iso": today.strftime("%Y-%m-%d")
    }

def update_html_time(filepath):
    """更新HTML文件中的时间"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = get_today_info()
    
    # 更新时间
    content = re.sub(
        r'更新时间:\s*\d{4}年\d{1,2}月\d{1,2}日',
        f'更新时间: {info["date"]}',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[成功] 已更新 {filepath} 的时间为 {info['date']}")

def main():
    print("="*60)
    print("海湾原油图谱 - 简化版更新")
    print("="*60)
    
    info = get_today_info()
    print(f"\n[信息] 当前日期: {info['date']}")
    
    # 更新 index.html
    update_html_time("index.html")
    
    print("\n[完成] 海湾原油图谱基础更新完成")
    print("提示：详细新闻内容需要手动搜索更新")

if __name__ == "__main__":
    main()
