#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有数据：商品价格、全球流动性、全球金融市场
"""

import subprocess
import sys
import json
import os
from datetime import datetime

def run_script(script_name, timeout=300):
    """运行脚本并返回结果"""
    print(f"\n{'='*60}")
    print(f"运行: {script_name}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"超时: {script_name}")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def check_data_files():
    """检查数据文件状态"""
    print(f"\n{'='*60}")
    print("数据文件检查")
    print(f"{'='*60}")
    
    files = {
        'market_data.json': ['commodities', 'financial', 'gscpi'],
        'liquidity_data.json': ['fci', 'credit_spread', 'vix', 'ois', 'mideast_fx', 'sovereign_cds', 'yield_curve'],
        'strait_data.json': ['realtime', 'daily'],
        'polymarket_real_data.json': [],
        'polymarket_history_data.json': []
    }
    
    for filename, required_keys in files.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if required_keys:
                    missing = [k for k in required_keys if k not in data]
                    if missing:
                        print(f"⚠️  {filename}: 缺少键 {missing}")
                    else:
                        print(f"✓ {filename}: 正常 ({len(data)} 个键)")
                else:
                    print(f"✓ {filename}: 正常")
            except Exception as e:
                print(f"✗ {filename}: 读取错误 - {e}")
        else:
            print(f"✗ {filename}: 不存在")

def main():
    print(f"{'='*60}")
    print("数据更新工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 按顺序运行各个数据获取脚本
    scripts = [
        ('fetch_market_data.py', 300),      # 商品价格和全球金融
        ('fetch_liquidity_data.py', 120),   # 全球流动性
        ('fetch_midterm_data.py', 60),      # 中期选举
        ('fetch_polymarket_data.py', 300),  # Polymarket历史
        ('update_polymarket.py', 60),       # Polymarket实时
    ]
    
    for script, timeout in scripts:
        if os.path.exists(script):
            run_script(script, timeout)
        else:
            print(f"脚本不存在: {script}")
    
    # 检查数据文件
    check_data_files()
    
    print(f"\n{'='*60}")
    print("更新完成！请刷新页面查看数据。")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
