#!/usr/bin/env python3
"""
每小时抓取金十期货霍尔木兹海峡数据
直接提取金十页面中的实时快照图片URL
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "jin10_strait_data.json"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


async def fetch_jin10_data():
    """抓取金十期货霍尔木兹海峡数据"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        result = {
            "updated": datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "金十数据",
            "url": "https://qihuo.jin10.com/topic/strait_of_hormuz.html",
            "industry_pressure": {},
            "ship_counts": {},
            "snapshots": []  # 直接存储金十的图片URL
        }
        
        try:
            print("正在访问金十期货霍尔木兹海峡页面...")
            
            url = "https://qihuo.jin10.com/topic/strait_of_hormuz.html"
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            
            if response.status != 200:
                print(f"页面访问失败: HTTP {response.status}")
                return None
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 获取页面标题确认
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 1. 提取行业通行压力系数
            print("\n提取行业通行压力系数...")
            
            pressure_data = await page.evaluate("""
                () => {
                    const result = {};
                    
                    // 查找综合通行压力系数
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {
                        const text = el.textContent || '';
                        
                        if (text.includes('行业通行压力系数') || text.includes('通行压力系数')) {
                            const match = text.match(/(\d+\.?\d*)%/);
                            if (match && !result.total) {
                                result.total = parseFloat(match[1]);
                            }
                        }
                    }
                    
                    return result;
                }
            """)
            
            if pressure_data.get('total'):
                result["industry_pressure"]["total"] = pressure_data["total"]
                print(f"  综合通行压力系数: {pressure_data['total']}%")
            
            # 2. 提取各品类数据
            print("\n提取各品类封锁率...")
            
            categories = await page.evaluate("""
                () => {
                    const categories = [];
                    const elements = document.querySelectorAll('*');
                    const categoryKeywords = [
                        {key: 'oil', name: '原油及成品油', keywords: ['原油', '石油']},
                        {key: 'lpg', name: '液化石油气', keywords: ['液化石油', 'LPG']},
                        {key: 'lng', name: '液化天然气', keywords: ['液化天然', 'LNG']},
                        {key: 'fertilizer', name: '化肥', keywords: ['化肥', '尿素', '磷肥']},
                        {key: 'aluminum', name: '铝材', keywords: ['铝', '铝材']},
                        {key: 'methanol', name: '甲醇', keywords: ['甲醇']}
                    ];
                    
                    for (let el of elements) {
                        const text = el.textContent || '';
                        
                        for (let cat of categoryKeywords) {
                            for (let kw of cat.keywords) {
                                if (text.includes(kw)) {
                                    const match = text.match(/(\d+\.?\d*)%/);
                                    if (match) {
                                        categories.push({
                                            key: cat.key,
                                            name: cat.name,
                                            value: parseFloat(match[1])
                                        });
                                    }
                                }
                            }
                        }
                    }
                    
                    return categories;
                }
            """)
            
            seen = set()
            for cat in categories:
                if cat['key'] not in seen:
                    seen.add(cat['key'])
                    result["industry_pressure"][cat['key']] = {
                        "name": cat['name'],
                        "value": cat['value']
                    }
                    print(f"  {cat['name']}: {cat['value']}%")
            
            # 3. 提取船只数量统计（参照金十页面格式）
            print("\n提取船只数量统计...")
            
            ship_data = await page.evaluate("""
                () => {
                    const result = {
                        hormuz: 0,          // 霍尔木兹海峡
                        hormuz_passing: 0,  // 正在通过
                        oman: 0,            // 阿曼湾
                        persian: 0,         // 波斯湾
                        sailing: 0,         // 航行中
                        anchored: 0         // 锚泊/停靠
                    };
                    
                    const elements = document.querySelectorAll('*');
                    
                    for (let el of elements) {
                        const text = el.textContent || '';
                        
                        // 当前通过霍尔木兹海峡（左侧大数字）
                        if (text.includes('当前通过') && text.includes('霍尔木兹')) {
                            // 查找相邻的大数字
                            const parent = el.parentElement;
                            if (parent) {
                                const numbers = parent.textContent.match(/(\d+)\s*艘/);
                                if (numbers) {
                                    result.hormuz_passing = parseInt(numbers[1]);
                                }
                            }
                        }
                        
                        // 航行中 速度≥1节
                        if (text.includes('航行中') && text.includes('速度')) {
                            const match = text.match(/(\d+)\s*艘/);
                            if (match) result.sailing = parseInt(match[1]);
                        }
                        
                        // 锚泊/停靠 速度<1节
                        if ((text.includes('锚泊') || text.includes('停靠')) && text.includes('速度')) {
                            const match = text.match(/(\d+)\s*艘/);
                            if (match) result.anchored = parseInt(match[1]);
                        }
                        
                        // 海域内总数
                        if (text.includes('阿曼湾') && text.includes('波斯湾')) {
                            const numbers = text.match(/(\d{1,3}(?:,\d{3})*)\s*艘/);
                            if (numbers) {
                                const total = parseInt(numbers[1].replace(/,/g, ''));
                                // 如果还没有分别的数据，先存总数
                                if (result.oman === 0 && result.persian === 0) {
                                    result.total_in_area = total;
                                }
                            }
                        }
                    }
                    
                    // 如果没有分别的数据但有总数，估算分配
                    if (result.sailing > 0 && result.anchored > 0) {
                        const total = result.sailing + result.anchored;
                        if (result.oman === 0 && result.persian === 0) {
                            result.oman = Math.floor(total * 0.4);  // 估算
                            result.persian = Math.floor(total * 0.6);
                        }
                    }
                    
                    return result;
                }
            """)
            
            if ship_data:
                result["ship_counts"] = ship_data
                print(f"  正在通过霍尔木兹海峡: {ship_data.get('hormuz_passing', 'N/A')}艘")
                print(f"  航行中(速度≥1节): {ship_data.get('sailing', 'N/A')}艘")
                print(f"  锚泊/停靠(速度<1节): {ship_data.get('anchored', 'N/A')}艘")
                print(f"  海域内总数: {ship_data.get('oman', 0) + ship_data.get('persian', 0)}艘")
            
            # 4. 提取金十页面中的实时快照图片URL
            print("\n提取金十实时快照图片...")
            
            snapshot_urls = await page.evaluate("""
                () => {
                    const snapshots = [];
                    
                    // 方法1: 查找带有特定class的图片
                    const imgSelectors = [
                        '.snapshot img',
                        '.realtime-map img',
                        '.strait-map img',
                        '.marine-map img',
                        '[class*="snapshot"] img',
                        '[class*="map"] img',
                        'img[src*="strait"]',
                        'img[src*="hormuz"]',
                        'img[src*="marine"]'
                    ];
                    
                    for (let selector of imgSelectors) {
                        const imgs = document.querySelectorAll(selector);
                        imgs.forEach(img => {
                            if (img.src && img.src.startsWith('http')) {
                                snapshots.push({
                                    url: img.src,
                                    type: 'snapshot',
                                    alt: img.alt || '实时快照'
                                });
                            }
                        });
                    }
                    
                    // 方法2: 查找所有背景图片
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        const bgImage = style.backgroundImage;
                        if (bgImage && bgImage.includes('url(')) {
                            const url = bgImage.match(/url\(["']?([^"')]+)["']?\)/);
                            if (url && url[1].startsWith('http')) {
                                snapshots.push({
                                    url: url[1],
                                    type: 'background',
                                    alt: '背景地图'
                                });
                            }
                        }
                    });
                    
                    // 方法3: 从canvas中提取（如果页面使用canvas渲染地图）
                    const canvases = document.querySelectorAll('canvas');
                    canvases.forEach((canvas, index) => {
                        try {
                            const dataUrl = canvas.toDataURL('image/png');
                            if (dataUrl && dataUrl.startsWith('data:image')) {
                                snapshots.push({
                                    url: dataUrl,
                                    type: 'canvas',
                                    alt: 'Canvas地图' + index
                                });
                            }
                        } catch (e) {
                            // Canvas可能受污染，无法导出
                        }
                    });
                    
                    return snapshots;
                }
            """)
            
            # 去重并保存URL
            seen_urls = set()
            for snap in snapshot_urls:
                if snap['url'] not in seen_urls:
                    seen_urls.add(snap['url'])
                    result["snapshots"].append(snap)
                    print(f"  找到图片: {snap['type']} - {snap['url'][:80]}...")
            
            # 5. 如果没有找到图片，尝试监控网络请求中的图片
            if len(result["snapshots"]) == 0:
                print("\n尝试从网络请求中提取图片...")
                
                # 重新加载页面并监听图片请求
                await page.close()
                page = await context.new_page()
                
                image_urls = []
                
                def handle_route(route, request):
                    url = request.url
                    if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']):
                        if 'strait' in url.lower() or 'hormuz' in url.lower() or 'map' in url.lower():
                            image_urls.append(url)
                    route.continue_()
                
                await page.route("**/*", handle_route)
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(2)
                
                for img_url in image_urls[:5]:  # 只取前5个
                    if img_url not in seen_urls:
                        seen_urls.add(img_url)
                        result["snapshots"].append({
                            "url": img_url,
                            "type": "network",
                            "alt": "网络图片"
                        })
                        print(f"  网络图片: {img_url[:80]}...")
            
            print(f"\n共找到 {len(result['snapshots'])} 张图片")
            
            return result
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            await browser.close()


async def main():
    print("=" * 60)
    print("抓取金十期货霍尔木兹海峡数据")
    print(f"北京时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    data = await fetch_jin10_data()
    
    if not data:
        print("\n抓取失败")
        return 1
    
    # 保存数据
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存: {DATA_FILE}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
