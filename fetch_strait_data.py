#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取霍尔木兹海峡数据：
1. 通过 Playwright 访问金十数据页面，拦截 _vir_106~_vir_110 API 响应
2. 提取金十页面中的视频 URL（flash-scdn.jin10.com/*.mp4）
3. 截图 MarineTraffic 公开页面（每20分钟），保存至 strait_snapshots/
4. 更新 strait_data.json
"""

import asyncio
import json
import os
import re
import sys
import glob
import shutil
import tempfile
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

def _get_ffmpeg():
    """优先用系统 ffmpeg，否则用 imageio_ffmpeg 内置二进制"""
    import shutil as _shutil
    if _shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

WORKDIR = Path(r"D:\python_code\海湾以来-最新")
SNAPSHOTS_DIR = WORKDIR / "strait_snapshots"
DATA_FILE = WORKDIR / "strait_data.json"
MAX_SNAPSHOTS = 144  # 约2天

JIN10_URL = "https://qihuo.jin10.com/topic/strait_of_hormuz.html"
MARINE_URL = "https://www.marinetraffic.com/en/ais/home/centerx:55.8/centery:25.7/zoom:8"
VIR_APIS = ["_vir_106", "_vir_107", "_vir_108", "_vir_109", "_vir_110"]

BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def load_existing_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "updated": "",
        "realtime": {},
        "daily": [],
        "direction": [],
        "fleet_type": [],
        "snapshots": [],
        "video_url": "",
    }


def save_data(data: dict):
    data["updated"] = datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {DATA_FILE.name} 已更新")


def cleanup_snapshots():
    """保留最新的 MAX_SNAPSHOTS 张截图"""
    files = sorted(glob.glob(str(SNAPSHOTS_DIR / "*.png")))
    if len(files) > MAX_SNAPSHOTS:
        for old in files[: len(files) - MAX_SNAPSHOTS]:
            os.remove(old)
            print(f"[清理] 删除旧快照: {Path(old).name}")


async def fetch_jin10_data(data: dict):
    """访问金十页面，拦截 _vir_ API 响应，提取视频 URL"""
    api_results = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        # 拦截 _vir_ API 响应
        async def handle_response(response):
            url = response.url
            for vir in VIR_APIS:
                if vir in url and "mp-api.jin10.com" in url:
                    try:
                        body = await response.json()
                        api_results[vir] = body
                        print(f"[拦截] {vir}: {len(str(body))} 字节")
                    except Exception as e:
                        print(f"[警告] 解析 {vir} 失败: {e}")

        page.on("response", handle_response)

        print(f"[访问] {JIN10_URL}")
        try:
            await page.goto(JIN10_URL, wait_until="domcontentloaded", timeout=30000)
        except PlaywrightTimeout:
            print("[警告] 页面 domcontentloaded 超时，继续等待 API...")

        # 等待 API 响应：每秒检查一次，最多等 25 秒，5 个都到就提前退出
        for i in range(25):
            await asyncio.sleep(1)
            if len(api_results) >= len(VIR_APIS):
                print(f"[快速] {i+1}s 内已拦截全部 {len(VIR_APIS)} 个 API")
                break
        else:
            print(f"[等待结束] 共拦截到 {len(api_results)}/{len(VIR_APIS)} 个 API: {list(api_results.keys())}")

        # 提取视频 URL
        try:
            video_src = await page.evaluate("""
                () => {
                    const v = document.querySelector('video[src]');
                    return v ? v.getAttribute('src') || v.getAttribute('data-src') : null;
                }
            """)
            if video_src and "flash-scdn.jin10.com" in video_src:
                data["video_url"] = video_src
                print(f"[视频] 获取到 URL: {video_src[:60]}...")
            else:
                # 尝试从 HTML 源码中正则提取
                html = await page.content()
                matches = re.findall(r"https://flash-scdn\.jin10\.com/[a-f0-9-]+\.mp4", html)
                if matches:
                    data["video_url"] = matches[0]
                    print(f"[视频] 从HTML提取 URL: {matches[0][:60]}...")
        except Exception as e:
            print(f"[警告] 提取视频URL失败: {e}")

        await context.close()
        await browser.close()

    # 解析 _vir_107（金十快照 PNG URLs）
    if "_vir_107" in api_results:
        rows = api_results["_vir_107"].get("data", [])
        if rows:
            existing_ts = {s.get("ts") for s in data.get("snapshots", [])}
            new_snaps = []
            for r in rows:
                ts = r.get("date", "")[:16]  # "2026-03-21 11:00"
                url = r.get("url", "")
                if ts and url and ts not in existing_ts:
                    new_snaps.append({"ts": ts, "url": url})
                    existing_ts.add(ts)
            if new_snaps:
                data["snapshots"] = sorted(
                    data.get("snapshots", []) + new_snaps,
                    key=lambda x: x.get("ts", "")
                )
                # 保留最近 MAX_SNAPSHOTS 条
                data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]
                print(f"[快照] 新增 {len(new_snaps)} 张 Jin10 快照，共 {len(data['snapshots'])} 张")

    # 解析 _vir_106（实时）
    if "_vir_106" in api_results:
        rows = api_results["_vir_106"].get("data", [])
        if rows:
            latest = rows[0] if isinstance(rows, list) else rows
            data["realtime"] = {
                "ship_now": latest.get("ship_now"),
                "ship_avg": latest.get("ship_avg"),
                "tpc": latest.get("tpc"),
                "oil": latest.get("oil"),
                "lng": latest.get("lng"),
                "lpg": latest.get("lpg"),
                "meoh": latest.get("meoh"),
                "npk": latest.get("npk"),
                "al": latest.get("al"),
                "car": latest.get("car"),
                "overall": latest.get("overall"),
                "stationary": latest.get("stationary"),
                "underway": latest.get("underway"),
                "updated": latest.get("date", ""),
            }
            print(f"[实时] ship_now={data['realtime'].get('ship_now')}, tpc={data['realtime'].get('tpc')}")

    # 解析 _vir_108（日统计: tanker/cargo/total/chg）
    if "_vir_108" in api_results:
        rows = api_results["_vir_108"].get("data", [])
        if rows:
            data["daily"] = [
                {
                    "date": r.get("date", ""),
                    "tanker": r.get("tanker"),
                    "cargo": r.get("cargo"),
                    "total": r.get("total"),
                    "chg": r.get("chg"),
                }
                for r in rows
                if r.get("date")
            ]
            print(f"[日统计] {len(data['daily'])} 条记录")

    # 解析 _vir_109（方向: inbound/outbound/total）
    if "_vir_109" in api_results:
        rows = api_results["_vir_109"].get("data", [])
        if rows:
            data["direction"] = [
                {
                    "date": r.get("date", ""),
                    "inbound": r.get("inbound"),
                    "outbound": r.get("outbound"),
                    "total": r.get("total"),
                }
                for r in rows
                if r.get("date")
            ]
            print(f"[方向] {len(data['direction'])} 条记录")

    # 解析 _vir_110（船队性质: sanctioned/shadow/regular）
    if "_vir_110" in api_results:
        rows = api_results["_vir_110"].get("data", [])
        if rows:
            data["fleet_type"] = [
                {
                    "date": r.get("date", ""),
                    "sanctioned": r.get("sanctioned"),
                    "shadow": r.get("shadow"),
                    "regular": r.get("regular"),
                }
                for r in rows
                if r.get("date")
            ]
            print(f"[船队] {len(data['fleet_type'])} 条记录")

    return bool(api_results)


async def screenshot_marinetraffic(data: dict):
    """截图 MarineTraffic 公开页面"""
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(BEIJING_TZ)
    filename = now.strftime("%Y%m%d_%H%M") + ".png"
    filepath = SNAPSHOTS_DIR / filename

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        print(f"[截图] 正在加载 MarineTraffic...")
        try:
            await page.goto(MARINE_URL, wait_until="networkidle", timeout=45000)
            await asyncio.sleep(4)  # 等待地图瓦片加载
            await page.screenshot(path=str(filepath), full_page=False)
            print(f"[截图] 已保存: {filename}")

            # 记录到 snapshots 列表
            snap = {"ts": now.strftime("%Y-%m-%d %H:%M"), "file": f"strait_snapshots/{filename}"}
            data["snapshots"].append(snap)
            # 只保留最近 MAX_SNAPSHOTS 条记录
            data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]

        except PlaywrightTimeout:
            print(f"[警告] MarineTraffic 截图超时，跳过")
        except Exception as e:
            print(f"[警告] MarineTraffic 截图失败: {e}")
        finally:
            await context.close()
            await browser.close()

    cleanup_snapshots()


def create_snapshot_video(data: dict):
    """将最近24h快照（_vir_107 URL或本地文件）合成延时视频，保存为 strait_timelapse.mp4"""
    snapshots = data.get("snapshots", [])
    if not snapshots:
        print("[视频] 无快照数据，跳过视频生成")
        return

    # 取最近48条（约24h，每小时一张）
    recent = snapshots[-48:]
    if len(recent) < 3:
        print(f"[视频] 快照数量不足({len(recent)}张)，跳过视频生成")
        return

    tmpdir = Path(tempfile.mkdtemp(prefix="strait_video_"))
    try:
        downloaded = []
        for i, snap in enumerate(recent):
            dst = tmpdir / f"{i:04d}.png"
            url = snap.get("url", "")
            local = snap.get("file", "")

            if url:
                try:
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        dst.write_bytes(resp.read())
                    downloaded.append(dst)
                except Exception as e:
                    print(f"[视频] 下载失败 {url[:60]}: {e}")
            elif local:
                src = WORKDIR / local
                if src.exists():
                    shutil.copy2(src, dst)
                    downloaded.append(dst)

        if len(downloaded) < 3:
            print(f"[视频] 可用帧数不足({len(downloaded)})，跳过视频生成")
            return

        print(f"[视频] 已下载 {len(downloaded)} 帧，开始合成...")

        ffmpeg_exe = _get_ffmpeg()
        if not ffmpeg_exe:
            print("[视频] 未找到 ffmpeg，请安装: pip install imageio-ffmpeg")
            return

        out_video = WORKDIR / "strait_timelapse.mp4"
        # ffmpeg: 每帧显示0.5秒（2fps），输出 H.264 MP4（web可用）
        cmd = [
            ffmpeg_exe, "-y",
            "-framerate", "2",
            "-i", str(tmpdir / "%04d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # 确保偶数尺寸
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_video),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size_mb = out_video.stat().st_size / 1024 / 1024
            data["timelapse_video"] = "strait_timelapse.mp4"
            print(f"[视频] 合成完成: strait_timelapse.mp4 ({size_mb:.1f} MB, {len(downloaded)} 帧)")
        else:
            print(f"[视频] ffmpeg 失败: {result.stderr[-300:]}")

    except Exception as e:
        print(f"[视频] 生成失败: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def main():
    print("=" * 60)
    print("霍尔木兹数据抓取器")
    print(f"时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.chdir(WORKDIR)
    data = load_existing_data()

    # 1. 金十数据
    jin10_ok = await fetch_jin10_data(data)
    print(f"[金十] {'成功' if jin10_ok else '失败/部分成功'}")

    # 2. MarineTraffic 截图
    await screenshot_marinetraffic(data)

    # 3. 合成延时视频
    create_snapshot_video(data)

    # 4. 保存
    save_data(data)
    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    asyncio.run(main())
