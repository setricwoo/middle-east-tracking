#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动截图脚本 - 通过CDP连接用户浏览器截取MarineTraffic
需要用户先以调试模式启动Edge浏览器:
  msedge.exe --remote-debugging-port=9222

使用方式:
1. 运行 "启动MarineTraffic截图.bat" 启动调试模式Edge
2. 在Edge中打开MarineTraffic网站
3. 此脚本会自动连接并截图
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("[ERROR] 请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

# 配置
WORKDIR = Path(__file__).parent.resolve()
SNAPSHOTS_DIR = WORKDIR / "strait_snapshots"
DATA_FILE = WORKDIR / "strait_data.json"
MARINE_URL = "https://www.marinetraffic.com/en/ais/home/centerx:55.8/centery:25.7/zoom:8"
MAX_SNAPSHOTS = 144  # 保留最近144条（约2天）


def load_data():
    """加载现有数据"""
    data = {"updated": "", "realtime": {}, "daily": [], "direction": [],
            "fleet_type": [], "snapshots": [], "video_url": ""}

    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                data.update(loaded)
        except Exception:
            pass

    if "snapshots" not in data:
        data["snapshots"] = []

    return data


def save_data(data):
    """保存数据"""
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def take_screenshot():
    """连接用户浏览器截图MarineTraffic"""
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M") + ".png"
    filepath = SNAPSHOTS_DIR / filename

    print(f"[{now.strftime('%H:%M:%S')}] 正在连接浏览器...")

    async with async_playwright() as pw:
        try:
            # 连接到用户的Edge浏览器
            browser = await pw.chromium.connect_over_cdp("http://localhost:9222")

            # 查找MarineTraffic页面
            target_page = None
            for ctx in browser.contexts:
                for page in ctx.pages:
                    url = page.url.lower()
                    if "marinetraffic" in url:
                        target_page = page
                        print(f"[{now.strftime('%H:%M:%S')}] 找到MarineTraffic页面")
                        break
                if target_page:
                    break

            if target_page:
                # 刷新页面获取最新数据
                print(f"[{now.strftime('%H:%M:%S')}] 正在刷新页面...")
                await target_page.reload(wait_until="domcontentloaded", timeout=30000)

                # 等待地图加载
                print(f"[{now.strftime('%H:%M:%S')}] 等待地图加载...")
                await asyncio.sleep(5)

                # 截图
                target_page.set_default_timeout(60000)
                await target_page.screenshot(path=str(filepath), timeout=60000)

                size_kb = filepath.stat().st_size / 1024
                print(f"[{now.strftime('%H:%M:%S')}] 截图成功: {filename} ({size_kb:.0f} KB)")

                # 更新数据
                data = load_data()
                snap = {
                    "ts": now.strftime("%Y-%m-%d %H:%M"),
                    "file": f"strait_snapshots/{filename}"
                }
                data["snapshots"].append(snap)
                data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]
                data["updated"] = now.strftime("%Y-%m-%d %H:%M")
                save_data(data)

                print(f"[{now.strftime('%H:%M:%S')}] 数据已更新，共 {len(data['snapshots'])} 条截图记录")
                return True
            else:
                print(f"[{now.strftime('%H:%M:%S')}] 未找到MarineTraffic页面")
                print(f"[{now.strftime('%H:%M:%S')}] 请确保Edge浏览器已打开MarineTraffic网站")

                # 列出当前打开的页面
                for i, ctx in enumerate(browser.contexts):
                    for j, page in enumerate(ctx.pages):
                        print(f"  [{i}-{j}] {page.url[:60]}...")

                return False

        except Exception as e:
            print(f"[{now.strftime('%H:%M:%S')}] 错误: {e}")
            return False


def cleanup_old_snapshots():
    """清理旧截图文件"""
    if not SNAPSHOTS_DIR.exists():
        return

    # 获取所有png文件
    files = sorted(SNAPSHOTS_DIR.glob("*.png"), key=lambda f: f.name, reverse=True)

    # 只保留最新的MAX_SNAPSHOTS个文件
    if len(files) > MAX_SNAPSHOTS:
        for f in files[MAX_SNAPSHOTS:]:
            try:
                f.unlink()
                print(f"[清理] 删除旧截图: {f.name}")
            except Exception:
                pass


if __name__ == "__main__":
    print("=" * 50)
    print("MarineTraffic 自动截图脚本")
    print("=" * 50)
    print(f"截图目录: {SNAPSHOTS_DIR}")
    print(f"数据文件: {DATA_FILE}")
    print()

    success = asyncio.run(take_screenshot())

    if success:
        cleanup_old_snapshots()
        print()
        print("截图完成!")
    else:
        print()
        print("截图失败!")
        print("请确保:")
        print("1. 已运行 '启动MarineTraffic截图.bat' 启动Edge调试模式")
        print("2. Edge浏览器已打开MarineTraffic网站")
        sys.exit(1)
