#!/usr/bin/env python3
"""
自动更新实时新闻网页并上传至GitHub
每小时执行一次
"""
import subprocess
import sys
import time
from datetime import datetime

def run_command(cmd, timeout=180):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"

def log_message(msg):
    """打印日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def main():
    log_message("="*60)
    log_message("开始自动更新实时新闻")
    log_message("="*60)
    
    # 1. 运行财联社爬虫
    log_message("[步骤1] 运行财联社新闻爬虫...")
    success, stdout, stderr = run_command("python scrape_cls_final.py", timeout=180)
    if success:
        log_message("[成功] 新闻爬虫执行完成")
        # 显示爬取的新闻数量
        if "成功爬取" in stdout:
            for line in stdout.split('\n'):
                if "成功爬取" in line:
                    log_message(f"[信息] {line.strip()}")
                    break
    else:
        log_message(f"[失败] 新闻爬虫执行失败: {stderr}")
        return False
    
    # 2. 检查是否有更新
    log_message("[步骤2] 检查文件变更...")
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        log_message(f"[失败] Git状态检查失败: {stderr}")
        return False
    
    if not stdout.strip():
        log_message("[信息] 没有文件变更，无需更新")
        return True
    
    changed_files = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
    log_message(f"[信息] 发现 {len(changed_files)} 个文件变更")
    
    # 3. Git add
    log_message("[步骤3] 添加文件到暂存区...")
    success, stdout, stderr = run_command("git add -A")
    if not success:
        log_message(f"[失败] Git add失败: {stderr}")
        return False
    log_message("[成功] 文件已添加")
    
    # 4. Git commit
    log_message("[步骤4] 提交变更...")
    commit_msg = f"自动更新实时新闻 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if not success:
        log_message(f"[失败] Git commit失败: {stderr}")
        return False
    log_message("[成功] 变更已提交")
    
    # 5. Git push（带重试）
    max_retries = 3
    retry_delay = 1200  # 20分钟 = 1200秒
    
    for attempt in range(1, max_retries + 1):
        log_message(f"[步骤5] 推送到GitHub (尝试 {attempt}/{max_retries})...")
        success, stdout, stderr = run_command("git push origin main", timeout=120)
        
        if success:
            log_message("[成功] 已成功推送到GitHub!")
            log_message("="*60)
            return True
        else:
            log_message(f"[失败] 推送失败: {stderr}")
            if attempt < max_retries:
                log_message(f"[等待] {retry_delay//60}分钟后重试...")
                time.sleep(retry_delay)
    
    log_message("[错误] 已达到最大重试次数，推送失败")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        log_message(f"[错误] 发生异常: {e}")
        sys.exit(1)
