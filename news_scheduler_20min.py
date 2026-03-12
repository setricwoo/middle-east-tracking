#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每20分钟定时更新实时新闻
"""
import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

# 设置工作目录
os.chdir(r'D:\python_code\海湾以来-最新')

def log_message(msg):
    """打印并记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open('scheduler_log.txt', 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def run_news_update():
    """执行新闻更新"""
    log_message("[执行] 更新实时新闻...")
    try:
        result = subprocess.run(
            [sys.executable, 'scrape_cls_final.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=300
        )
        
        output = result.stdout if result.stdout else ""
        for line in output.split('\n'):
            if any(keyword in line for keyword in ['[统计]', '新增', '原有', '现有', 'RESULT']):
                log_message(line.strip())
        
        if result.returncode == 0:
            log_message("[成功] 新闻更新完成")
            return True
        else:
            log_message(f"[失败] 新闻更新返回错误: {result.returncode}")
            return False
    except Exception as e:
        log_message(f"[异常] 新闻更新时发生错误: {e}")
        return False

def run_polymarket_update():
    """执行Polymarket数据更新"""
    log_message("[执行] 更新Polymarket预测数据...")
    try:
        result = subprocess.run(
            [sys.executable, 'update_polymarket_html.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=300
        )
        
        output = result.stdout if result.stdout else ""
        for line in output.split('\n'):
            if any(keyword in line for keyword in ['[成功]', '[更新]', '[完成]', 'RESULT']):
                log_message(line.strip())
        
        if result.returncode == 0:
            log_message("[成功] Polymarket数据更新完成")
            return True
        else:
            log_message(f"[失败] Polymarket更新返回错误: {result.returncode}")
            return False
    except Exception as e:
        log_message(f"[异常] Polymarket更新时发生错误: {e}")
        return False

def run_git_push():
    """推送到GitHub"""
    log_message("[执行] 推送到GitHub...")
    try:
        # 先添加所有更改
        add_result = subprocess.run(
            ['git', 'add', '-A'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        
        # 提交更改
        commit_result = subprocess.run(
            ['git', 'commit', '-m', f'自动更新新闻: {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        
        # 推送到GitHub
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )
        
        if push_result.returncode == 0:
            log_message("[成功] GitHub推送完成")
            return True
        else:
            stderr = push_result.stderr if push_result.stderr else ""
            if "nothing to commit" in stderr.lower() or "nothing to commit" in str(commit_result.stderr):
                log_message("[信息] 无新内容需要推送")
                return True
            log_message(f"[警告] GitHub推送可能失败: {stderr[:200]}")
            return False
    except Exception as e:
        log_message(f"[异常] GitHub推送时发生错误: {e}")
        return False

def run_20min_update():
    """执行20分钟更新任务"""
    log_message("="*60)
    log_message("【20分钟定时】执行新闻自动更新")
    
    # 更新新闻
    news_ok = run_news_update()
    
    # 更新Polymarket数据
    polymarket_ok = run_polymarket_update()
    
    # 推送到GitHub
    git_ok = run_git_push()
    
    log_message("="*60)
    log_message(f"任务完成: 新闻({'OK' if news_ok else 'FAIL'}) | Polymarket({'OK' if polymarket_ok else 'FAIL'}) | GitHub({'OK' if git_ok else 'FAIL'})")
    log_message("下次执行时间: 20分钟后")
    log_message("")

def main():
    log_message("="*60)
    log_message("20分钟新闻定时调度器已启动")
    log_message("执行频率: 每20分钟")
    log_message("执行内容: 更新实时新闻 + Polymarket数据 + 推送到GitHub")
    log_message("按 Ctrl+C 停止")
    log_message("="*60)
    
    # 立即执行一次
    run_20min_update()
    
    # 每20分钟执行一次
    schedule.every(20).minutes.do(run_20min_update)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("[停止] 用户中断，调度器已停止")
    except Exception as e:
        log_message(f"[错误] 调度器异常: {e}")
