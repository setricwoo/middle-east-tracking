#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI 专用截图脚本（用于 GitHub Actions）
增强反检测能力，避免被 MarineTraffic 屏蔽
"""

import asyncio
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import random
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

# 更真实的 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
]

STEALTH_SCRIPT = """
// 完整的反检测脚本
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });

// 覆盖 Canvas 指纹
defaults = {};
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type) {
    if (this.width > 0 && this.height > 0) {
        const ctx = this.getContext('2d');
        if (ctx) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] += Math.random() > 0.5 ? 1 : -1;
            }
            ctx.putImageData(imageData, 0, 0);
        }
    }
    return originalToDataURL.apply(this, arguments);
};

// 覆盖 WebGL
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris Xe Graphics';
    }
    return getParameter.apply(this, arguments);
};

// 禁用 Notifications
window.Notification = undefined;

// 覆盖 Permissions
const originalQuery = navigator.permissions.query;
navigator.permissions.query = function(parameters) {
    return Promise.resolve({
        state: 'prompt',
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => {},
    });
};
"""


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
    
    if "snapshots" not in data:
        data["snapshots"] = []
    
    # 扫描现有截图文件，同步记录
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
            print(f"[视频] ffmpeg 失败")
    except Exception as e:
        print(f"[视频] 生成失败: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def screenshot_marinetraffic(data: dict):
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(UTC_TZ)
    filename = now.strftime("%Y%m%d_%H%M") + ".png"
    filepath = SNAPSHOTS_DIR / filename

    # 随机选择 User-Agent
    user_agent = random.choice(USER_AGENTS)
    
    async with async_playwright() as pw:
        # 使用更多反检测选项
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280 + random.randint(-50, 50), "height": 800 + random.randint(-30, 30)},
            device_scale_factor=1,
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
            color_scheme='light',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        # 注入完整的反检测脚本
        await context.add_init_script(STEALTH_SCRIPT)
        
        page = await context.new_page()

        print(f"[截图] 正在加载 MarineTraffic...")
        print(f"[截图] UA: {user_agent[:50]}...")
        
        try:
            # 先访问主页获取 cookies
            await page.goto("https://www.marinetraffic.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2 + random.random() * 2)
            
            # 再访问目标页面
            await page.goto(MARINE_URL, wait_until="domcontentloaded", timeout=45000)
            
            # 随机延迟，等待地图渲染
            await asyncio.sleep(8 + random.random() * 4)
            
            # 检查是否被屏蔽
            content = await page.content()
            if "you have been blocked" in content.lower() or "sorry" in content.lower():
                print("[警告] 检测到被 MarineTraffic 屏蔽，跳过本次截图")
                # 删除被屏蔽的截图
                await context.close()
                await browser.close()
                return False
            
            # 检查是否加载成功（是否有地图元素）
            if "ais" in content.lower() or "vessel" in content.lower():
                await page.screenshot(path=str(filepath), full_page=False)
                size_kb = filepath.stat().st_size / 1024
                print(f"[截图] 已保存: {filename} ({size_kb:.0f} KB)")

                snap = {"ts": now.strftime("%Y-%m-%d %H:%M"), "file": f"strait_snapshots/{filename}"}
                data["snapshots"].append(snap)
                data["snapshots"] = data["snapshots"][-MAX_SNAPSHOTS:]
                return True
            else:
                print("[警告] 页面内容异常，可能未正确加载")
                return False

        except PlaywrightTimeout:
            print("[警告] MarineTraffic 截图超时")
            return False
        except Exception as e:
            print(f"[警告] MarineTraffic 截图失败: {e}")
            return False
        finally:
            await context.close()
            await browser.close()


async def main():
    print("=" * 60)
    print("CI 截图脚本（GitHub Actions 专用）")
    print("增强反检测版本")
    print(f"时间: {datetime.now(UTC_TZ).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 60)

    os.chdir(WORKDIR)
    data = load_data()

    # 截图
    success = await screenshot_marinetraffic(data)
    
    if success:
        # 生成延时视频
        create_timelapse(data)
    else:
        print("[跳过] 截图失败，不生成视频")

    # 保存
    save_data(data)
    cleanup_snapshots()
    
    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    asyncio.run(main())
