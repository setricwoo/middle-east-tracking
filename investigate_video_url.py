"""
调查金十数据霍尔木兹页面视频URL来源
视频URL: https://flash-scdn.jin10.com/8c1d2c82-79be-47cf-9284-34c6226e4dcc.mp4
"""
import asyncio
import json
import re
import urllib.request
from playwright.async_api import async_playwright

VIDEO_URL = "https://flash-scdn.jin10.com/8c1d2c82-79be-47cf-9284-34c6226e4dcc.mp4"
TARGET_PAGE = "https://qihuo.jin10.com/topic/strait_of_hormuz.html"

async def main():
    print("=" * 80)
    print("调查金十数据霍尔木兹页面视频URL来源")
    print("=" * 80)
    print(f"目标视频URL: {VIDEO_URL}")
    print(f"目标页面: {TARGET_PAGE}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 存储所有API响应
        api_responses = {}

        # 拦截所有网络请求
        async def handle_route(route, request):
            url = request.url
            # 只拦截 _vir_ API
            if '_vir_' in url:
                print(f"[拦截API] {url}")
                try:
                    response = await route.fetch()
                    body = await response.body()
                    try:
                        json_data = json.loads(body)
                        api_responses[url] = json_data
                        print(f"  -> 已保存响应，包含 {len(str(json_data))} 字符")
                    except:
                        api_responses[url] = body.decode('utf-8', errors='replace')[:500]
                        print(f"  -> 非JSON响应: {body[:200]}")
                    await route.fulfill(response=response)
                    return
                except Exception as e:
                    print(f"  -> 拦截失败: {e}")
            await route.continue_()

        page = await context.new_page()
        await page.route("**/*", handle_route)

        print("--- 1. 检查页面HTML源码中是否包含视频URL或flash-scdn域名 ---")
        print()

        # 访问页面
        print(f"正在访问: {TARGET_PAGE}")
        response = await page.goto(TARGET_PAGE, wait_until="networkidle", timeout=60000)
        print(f"页面加载完成，状态: {response.status}")
        print()

        # 获取页面HTML
        html = await page.content()
        print(f"HTML总长度: {len(html)} 字符")
        print()

        # 检查是否包含视频URL
        if VIDEO_URL in html:
            print(f"[发现] 视频URL直接硬编码在HTML中!")
            # 找到上下文
            idx = html.find(VIDEO_URL)
            context_start = max(0, idx - 200)
            context_end = min(len(html), idx + len(VIDEO_URL) + 200)
            print(f"上下文: ...{html[context_start:context_end]}...")
        else:
            print(f"[结果] 视频URL未直接出现在HTML源码中")
        print()

        # 检查flash-scdn域名
        if 'flash-scdn.jin10.com' in html:
            print(f"[发现] flash-scdn.jin10.com 域名出现在HTML中!")
            # 找出所有出现位置
            matches = re.findall(r'https?://flash-scdn\.jin10\.com/[^"\'\s<>]+', html)
            print(f"找到 {len(matches)} 个flash-scdn链接:")
            for m in matches[:10]:
                print(f"  - {m}")
        else:
            print(f"[结果] flash-scdn.jin10.com 域名未出现在HTML源码中")
        print()

        # 检查mp4链接
        mp4_matches = re.findall(r'https?://[^"\'\s<>]+\.mp4[^"\'\s<>]*', html)
        if mp4_matches:
            print(f"[发现] 找到 {len(mp4_matches)} 个.mp4链接:")
            for m in set(mp4_matches[:10]):
                print(f"  - {m}")
        else:
            print(f"[结果] HTML中未找到.mp4链接")
        print()

        # 等待一下让API请求完成
        print("等待API请求完成...")
        await asyncio.sleep(3)

        print("=" * 80)
        print("--- 2. 获取 _vir_107 和其他 _vir_ API的实际响应内容 ---")
        print("=" * 80)
        print()

        if api_responses:
            print(f"共拦截到 {len(api_responses)} 个API响应:")
            for url, data in api_responses.items():
                print(f"\nAPI: {url}")
                print("-" * 60)
                if isinstance(data, dict):
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    # 检查是否包含视频URL
                    data_str = json.dumps(data)
                    if VIDEO_URL in data_str:
                        print(f"\n[!!!] 此API响应包含目标视频URL!")
                    elif 'flash-scdn' in data_str:
                        print(f"\n[!!!] 此API响应包含flash-scdn域名!")
                else:
                    print(data[:1000])
        else:
            print("未拦截到任何 _vir_ API响应，尝试直接获取...")
            # 直接尝试获取已知的API
            vir_apis = [
                'https://cdn-l.jin10.com/topics/strait_of_hormuz.json',
                'https://datacenter-api.jin10.com/shipping/hormuz',
                'https://api.jin10.com/topic/data?topic=strait_of_hormuz',
            ]
            for api_url in vir_apis:
                try:
                    req = urllib.request.Request(api_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://qihuo.jin10.com/'
                    })
                    with urllib.request.urlopen(req, timeout=10) as r:
                        data = r.read().decode('utf-8', errors='replace')
                        print(f"\nAPI: {api_url}")
                        print("-" * 60)
                        try:
                            json_data = json.loads(data)
                            print(json.dumps(json_data, ensure_ascii=False, indent=2)[:2000])
                        except:
                            print(data[:1000])
                except Exception as e:
                    print(f"ERR {api_url}: {e}")
        print()

        await browser.close()

    print("=" * 80)
    print("--- 3. 尝试直接下载视频的前1MB验证MP4可访问性 ---")
    print("=" * 80)
    print()

    try:
        req = urllib.request.Request(
            VIDEO_URL,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Range': 'bytes=0-1000000',
                'Referer': 'https://qihuo.jin10.com/'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"Status: {r.status}")
            print(f"Content-Type: {r.headers.get('Content-Type')}")
            print(f"Content-Range: {r.headers.get('Content-Range')}")
            print(f"Content-Length: {r.headers.get('Content-Length')}")
            print(f"Accept-Ranges: {r.headers.get('Accept-Ranges')}")
            print()
            data = r.read(100)
            print(f"First 100 bytes (hex): {data.hex()}")
            print(f"First bytes as text: {data[:20]}")
            # MP4 magic bytes检查
            if data[:4].hex() == '00000020' or data[4:8] == b'ftyp':
                print("[确认] 这是有效的MP4文件 (ftyp标志 found)")
            elif b'ftyp' in data[:20]:
                print("[确认] 发现MP4 ftyp标志")
            else:
                print("[警告] 未找到标准MP4标志，可能是其他格式或加密内容")
    except Exception as e:
        print(f"下载失败: {e}")
    print()

    print("=" * 80)
    print("--- 4. 搜索页面JS代码中的flash-scdn或mp4关键词 ---")
    print("=" * 80)
    print()

    # 重新获取页面内容来检查JS
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TARGET_PAGE, wait_until="networkidle", timeout=60000)

        # 获取所有script标签内容
        scripts = await page.query_selector_all('script')
        print(f"页面共有 {len(scripts)} 个<script>标签")

        flash_scdn_found = False
        mp4_found = False
        video_generation_found = False

        for i, script in enumerate(scripts):
            try:
                content = await script.text_content()
                if not content:
                    continue

                # 检查flash-scdn
                if 'flash-scdn' in content:
                    print(f"\n[Script {i}] 包含 'flash-scdn':")
                    # 找到上下文
                    lines = content.split('\n')
                    for j, line in enumerate(lines):
                        if 'flash-scdn' in line:
                            print(f"  Line {j}: {line.strip()[:200]}")
                    flash_scdn_found = True

                # 检查mp4
                if '.mp4' in content:
                    print(f"\n[Script {i}] 包含 '.mp4':")
                    lines = content.split('\n')
                    for j, line in enumerate(lines):
                        if '.mp4' in line:
                            print(f"  Line {j}: {line.strip()[:200]}")
                    mp4_found = True

                # 检查视频生成逻辑
                if 'video' in content.lower() and ('url' in content.lower() or 'src' in content.lower()):
                    # 搜索视频相关代码
                    video_patterns = re.findall(r'video[^;]{0,200}url[^;]{0,200}', content, re.IGNORECASE)
                    if video_patterns:
                        print(f"\n[Script {i}] 可能的视频URL生成代码:")
                        for p in video_patterns[:3]:
                            print(f"  {p[:150]}")
                        video_generation_found = True

            except Exception as e:
                pass

        if not flash_scdn_found:
            print("[结果] 未在任何<script>标签中找到 'flash-scdn'")
        if not mp4_found:
            print("[结果] 未在任何<script>标签中找到 '.mp4'")
        if not video_generation_found:
            print("[结果] 未找到明显的视频URL生成代码")

        # 检查网络请求的JS文件
        print("\n检查外部JS文件...")
        js_files = await page.query_selector_all('script[src]')
        for js in js_files:
            src = await js.get_attribute('src')
            if src and ('jin10' in src or 'cdn' in src):
                print(f"  JS文件: {src}")

        await browser.close()

    print()
    print("=" * 80)
    print("调查完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
