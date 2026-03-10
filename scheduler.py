#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每20分钟定时执行新闻更新任务
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

def run_update():
    """执行更新任务"""
    log_message("="*60)
    log_message("定时触发：执行自动更新")
    
    try:
        log_message("[执行] 启动 auto_update_news.py ...")
        result = subprocess.run(
            [sys.executable, 'auto_update_news.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=600  # 增加到10分钟超时
        )
        
        # 解析并显示输出中的统计信息
        output = result.stdout if result.stdout else ""
        for line in output.split('\n'):
            # 显示统计相关的行
            if any(keyword in line for keyword in ['[更新]', '[统计]', '新增', '原有', '现有']):
                log_message(line.strip())
        
        if result.returncode == 0:
            log_message("[成功] 更新任务执行完成")
        else:
            log_message(f"[失败] 更新任务返回错误: {result.returncode}")
            if result.stderr:
                log_message(f"[错误信息] {result.stderr[:200]}")
    except Exception as e:
        log_message(f"[异常] 执行更新时发生错误: {e}")
    
    log_message("="*60)
    log_message("下次执行时间: 20分钟后")
    log_message("")

def main():
    log_message("="*60)
    log_message("定时调度器已启动")
    log_message("执行频率: 每20分钟")
    log_message("按 Ctrl+C 停止")
    log_message("="*60)
    
    # 立即执行一次
    run_update()
    
    # 每20分钟执行一次
    schedule.every(20).minutes.do(run_update)
    
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
