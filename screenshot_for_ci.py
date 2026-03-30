#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI 专用截图脚本（用于 GitHub Actions）
1. Playwright 截图 MarineTraffic 霍尔木兹海峡公开页面
2. 追加截图记录到 strait_data.json["snapshots"]
3. 从最近本地 PNG 生成延时视频 strait_timelapse.mp4（imageio-ffmpeg）
4. 清理超过 144 张的旧截图
"""

import asyncio
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)

WORKDIR = Path(__file__).parent.resolve()
SNAPSHOTS_DIR = WORKDIR / "strait_snapshots"
DATA_FILE = WORKDIR / "strait_data.json"
MARINE_URL = "https://www.marinetraffic.com/en/ais/home/centerx:55.8/centery:25.7/zoom:8"
MAX_SNAPSHOTS = 144  # 约2天
UTC_TZ = ZoneInfo("UTC")


def _get_ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def load_data() -> dict:
    data = {"updated": "", "realtime": {}, "daily": [], "direction": [],
            "fleet_type": [], "snapshots": [], "video_url": ""}
    
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                data.update(loaded)
        except Exception:
            pass
    
    # 确保snapshots字段存在
    if "snapshots" not in data:
        data["snapshots"] = []
    
    # 扫描现有截图文件，同步记录（确保所有文件都有记录）
    existing_files = sorted(glob.glob(str(SNAPSHOTS_DIR / "*.png")))
    existing_set = {s.get("file", "").split("/")[-1] for s in data["snapshots"]}
    
    added = 0
    for filepath in existing_files:
        fname = Path(filepath).name
        if fname not in existing_set:
            try:
                ts = f"{fname[0:4]}-{fname[4:6]}-{fname[6:8]} {fname[9:11]}:{fname[11:13]}"
                data["snapshots"].append({"ts": ts, "file": f"strait_snapshots/{fname}"})
                added += 1
            except:
                pass
    
    if added > 0:
        print(f"[同步] 新增 {added} 条截图记录，总计 {len(data['snapshots'])} 条")
    
    # 限制记录数量
    data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]
    
    return data


def save_data(data: dict):
    data["updated"] = datetime.now(UTC_TZ).strftime("%Y-%m-%dT%H:%M:%S")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {DATA_FILE.name} 已更新")


def cleanup_snapshots():
    files = sorted(glob.glob(str(SNAPSHOTS_DIR / "*.png")))
    if len(files) > MAX_SNAPSHOTS:
        for old in files[: len(files) - MAX_SNAPSHOTS]:
            os.remove(old)
            print(f"[清理] 删除旧快照: {Path(old).name}")


def create_timelapse(data: dict):
    """从最近本地 PNG 生成延时视频"""
    # 收集本地截图（只用 file 字段的快照）
    local_snaps = [s for s in data.get("snapshots", []) if s.get("file")]
    if len(local_snaps) < 3:
        print(f"[视频] 本地快照不足({len(local_snaps)})，跳过视频生成")
        return

    recent = local_snaps[-72:]  # 最近72张（约24h）
    tmpdir = Path(tempfile.mkdtemp(prefix="strait_ci_video_"))
    try:
        copied = []
        for i, snap in enumerate(recent):
            src = WORKDIR / snap["file"]
            if src.exists():
                dst = tmpdir / f"{i:04d}.png"
                shutil.copy2(src, dst)
                copied.append(dst)

        if len(copied) < 3:
            print(f"[视频] 可用本地帧不足({len(copied)})，跳过")
            return

        ffmpeg_exe = _get_ffmpeg()
        if not ffmpeg_exe:
            print("[视频] 未找到 ffmpeg，请安装: pip install imageio-ffmpeg")
            return

        out_video = WORKDIR / "strait_timelapse.mp4"
        cmd = [
            ffmpeg_exe, "-y",
            "-framerate", "2",
            "-i", str(tmpdir / "%04d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(out_video),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size_mb = out_video.stat().st_size / 1024 / 1024
            data["timelapse_video"] = "strait_timelapse.mp4"
            print(f"[视频] 合成完成: {size_mb:.1f} MB，{len(copied)} 帧")
        else:
            print(f"[视频] ffmpeg 失败: {result.stderr[-200:]}")
    except Exception as e:
        print(f"[视频] 生成失败: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def screenshot_marinetraffic(data: dict):
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(UTC_TZ)
    filename = now.strftime("%Y%m%d_%H%M") + ".png"
    filepath = SNAPSHOTS_DIR / filename

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        # 隐藏 webdriver 特征
        await context.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )
        page = await context.new_page()

        print(f"[截图] 正在加载 MarineTraffic...")
        try:
            await page.goto(MARINE_URL, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(6)  # 等待地图瓦片渲染
            await page.screenshot(path=str(filepath), full_page=False)
            size_kb = filepath.stat().st_size / 1024
            print(f"[截图] 已保存: {filename} ({size_kb:.0f} KB)")

            snap = {"ts": now.strftime("%Y-%m-%d %H:%M"), "file": f"strait_snapshots/{filename}"}
            data["snapshots"].append(snap)
            data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]

        except PlaywrightTimeout:
            print("[警告] MarineTraffic 截图超时，跳过")
        except Exception as e:
            print(f"[警告] MarineTraffic 截图失败: {e}")
        finally:
            await context.close()
            await browser.close()

    cleanup_snapshots()


async def main():
    print("=" * 60)
    print("CI 截图脚本（GitHub Actions 专用）")
    print(f"时间: {datetime.now(UTC_TZ).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 60)

    os.chdir(WORKDIR)
    data = load_data()

    # 1. 截图
    await screenshot_marinetraffic(data)

    # 2. 生成延时视频
    create_timelapse(data)

    # 3. 保存
    save_data(data)
    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    asyncio.run(main())
