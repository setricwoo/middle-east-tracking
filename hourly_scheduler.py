#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每小时定时执行任务：
1. 更新冲突每日简报
2. 更新实时新闻
3. 推送到GitHub
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
    timestamp = datetime.now().strftime("Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open('scheduler_log.txt', 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def run_briefing_update():
    """执行简报更新"""
    log_message("[执行] 更新冲突每日简报...")
    try:
        result = subprocess.run(
            [sys.executable, 'update_briefing_grok.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=300
        )
        
        output = result.stdout if result.stdout else ""
        for line in output.split('\n'):
            if any(keyword in line for keyword in ['[成功]', '[更新]', '冲突']):
                log_message(line.strip())
        
        if result.returncode == 0:
            log_message("[成功] 简报更新完成")
            return True
        else:
            log_message(f"[失败] 简报更新返回错误: {result.returncode}")
            return False
    except Exception as e:
        log_message(f"[异常] 简报更新时发生错误: {e}")
        return False

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
            ['git', 'commit', '-m', f'自动更新: {datetime.now().strftime("Y-%m-%d %H:%M")}'],
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
            log_message(f"[警告] GitHub推送可能失败: {push_result.stderr[:200]}")
            return False
    except Exception as e:
        log_message(f"[异常] GitHub推送时发生错误: {e}")
        return False

def run_hourly_update():
    """执行每小时更新任务"""
    log_message("="*60)
    log_message("定时触发：执行每小时自动更新")
    
    # 1. 更新简报
    briefing_ok = run_briefing_update()
    
    # 2. 更新新闻
    news_ok = run_news_update()
    
    # 3. 推送到GitHub
    git_ok = run_git_push()
    
    log_message("="*60)
    log_message(f"任务完成: 简报({'✓' if briefing_ok else '✗'}) | 新闻({'✓' if news_ok else '✗'}) | GitHub({'✓' if git_ok else '✗'})")
    log_message("下次执行时间: 1小时后")
    log_message("")

def main():
    log_message("="*60)
    log_message("每小时定时调度器已启动")
    log_message("执行频率: 每1小时")
    log_message("执行内容:")
    log_message("  1. 更新冲突每日简报")
    log_message("  2. 更新实时新闻")
    log_message("  3. 推送到GitHub")
    log_message("按 Ctrl+C 停止")
    log_message("="*60)
    
    # 立即执行一次
    run_hourly_update()
    
    # 每小时执行一次
    schedule.every(1).hours.do(run_hourly_update)
    
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
