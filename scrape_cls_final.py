"""
使用 Playwright 爬取财联社中东冲突专题新闻
来源: https://www.cls.cn/subject/10986
"""
from playwright.sync_api import sync_playwright
import json
import re
from datetime import datetime, timedelta

def scrape_news():
    """爬取财联社新闻"""
    print("开始爬取财联社新闻...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)
        
        try:
            # 访问页面
            print("正在访问 https://www.cls.cn/subject/10986")
            page.goto("https://www.cls.cn/subject/10986", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            
            print(f"页面标题: {page.title()}")
            
            # 点击"加载更多"
            print("点击加载更多...")
            load_more_count = 0
            max_clicks = 25
            
            while load_more_count < max_clicks:
                load_more_selectors = [
                    'text=加载更多',
                    'text=查看更多',
                    '.load-more',
                    '[class*="load-more"]',
                ]
                
                found_button = None
                for selector in load_more_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            found_button = button
                            break
                    except:
                        continue
                
                if not found_button:
                    break
                
                try:
                    found_button.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    
                    links_before = len(page.query_selector_all('a[href*="/detail/"]'))
                    found_button.click()
                    load_more_count += 1
                    
                    page.wait_for_timeout(2000)
                    
                    links_after = len(page.query_selector_all('a[href*="/detail/"]'))
                    if links_after <= links_before:
                        break
                    
                    if links_after >= 250:
                        break
                        
                except:
                    break
            
            # 提取新闻 - 通过时间元素找到对应的新闻
            print("\n提取新闻数据...")
            news_list = []
            seen_urls = set()
            
            # 找到所有时间元素（class包含999的）
            time_elements = page.query_selector_all('[class*="999"]')
            print(f"找到 {len(time_elements)} 个时间元素")
            
            for time_el in time_elements:
                try:
                    time_text = time_el.inner_text()
                    
                    # 检查是否是有效的时间格式（包含年份）
                    if not re.search(r'\d{4}-\d{2}-\d{2}', time_text):
                        continue
                    
                    # 提取时间
                    time_str = extract_time(time_text)
                    if not time_str:
                        continue
                    
                    # 向上查找父元素
                    parent = time_el.query_selector('xpath=..')
                    if not parent:
                        continue
                    
                    # 在父元素中查找链接
                    link = parent.query_selector('a[href*="/detail/"]')
                    
                    # 如果没找到，尝试祖父元素
                    if not link:
                        grandparent = parent.query_selector('xpath=..')
                        if grandparent:
                            link = grandparent.query_selector('a[href*="/detail/"]')
                    
                    if not link:
                        continue
                    
                    # 获取标题
                    title = link.inner_text().strip().split('\n')[0]
                    if not title or len(title) < 5:
                        continue
                    
                    href = link.get_attribute('href') or ''
                    if not href or href in seen_urls:
                        continue
                    
                    seen_urls.add(href)
                    news_list.append({
                        'id': str(len(news_list) + 1),
                        'title': title[:120],
                        'summary': title[:200],
                        'time': time_str,
                        'url': 'https://www.cls.cn' + href if not href.startswith('http') else href,
                        'category': categorize(title)
                    })
                    
                    if len(news_list) >= 150:
                        break
                        
                except:
                    continue
            
            browser.close()
            
            print(f"\n成功提取 {len(news_list)} 条新闻")
            for n in news_list[:5]:
                print(f"  [{n['time']}] {n['title'][:40]}...")
            
            return news_list
            
        except Exception as e:
            print(f"错误: {e}")
            browser.close()
            return []

def extract_time(text):
    """从文本中提取时间"""
    if not text:
        return ''
    
    # 匹配格式: 2026-03-08 19:36
    match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', text)
    if match:
        return match.group(1)
    
    return ''

def categorize(text):
    """分类新闻"""
    text = (text or '').lower()
    
    if any(k in text for k in ['海峡', '霍尔木兹', '航运', '油轮', '船舶', '港口', '海运', '航道']):
        return 'shipping'
    if any(k in text for k in ['石油', '原油', '天然气', '能源', 'opec', '油价', '产量', '供应']):
        return 'energy'
    if any(k in text for k in ['外交', '谈判', '会谈', '制裁', '联合国', '欧盟', '协议', '停火']):
        return 'diplomacy'
    return 'military'

def load_existing_news():
    """从news.html加载现有新闻"""
    try:
        with open('news.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取CLS_NEWS_DATA数组
        match = re.search(r'const CLS_NEWS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            news_json = match.group(1)
            return json.loads(news_json)
    except Exception as e:
        print(f"读取现有新闻失败: {e}")
    
    return []

def merge_news(existing_news, new_news):
    """合并新闻，去重并按时间排序（最新的在前）"""
    # 创建URL到新闻的映射
    existing_urls = {item['url']: item for item in existing_news}
    
    # 添加新新闻（如果不存在）
    added_count = 0
    for item in new_news:
        if item['url'] not in existing_urls:
            existing_urls[item['url']] = item
            added_count += 1
    
    # 转换为列表并按时间排序（最新的在前）
    merged = list(existing_urls.values())
    merged.sort(key=lambda x: x['time'], reverse=True)
    
    # 重新分配ID
    for i, item in enumerate(merged, 1):
        item['id'] = str(i)
    
    return merged, added_count

def update_html(news_list):
    """更新 news.html（增量更新，保留旧新闻）"""
    if not news_list:
        print("没有新闻数据可更新")
        return 0, 0, 0
    
    # 加载现有新闻
    existing_news = load_existing_news()
    existing_count = len(existing_news)
    print(f"现有新闻: {existing_count} 条")
    
    # 合并新闻
    merged_news, added_count = merge_news(existing_news, news_list)
    total_count = len(merged_news)
    print(f"新增新闻: {added_count} 条")
    print(f"合并后共: {total_count} 条")
    
    # 读取HTML内容
    with open('news.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新新闻数据
    news_json = json.dumps(merged_news, ensure_ascii=False, indent=4)
    content = re.sub(r'const CLS_NEWS_DATA = \[.*?\];', f'const CLS_NEWS_DATA = {news_json};', content, flags=re.DOTALL)
    
    with open('news.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[统计] 原有: {existing_count} 条 | 新增: {added_count} 条 | 现有: {total_count} 条")
    return existing_count, added_count, total_count

def main():
    print("="*50)
    
    news_list = scrape_news()
    if news_list:
        existing, added, total = update_html(news_list)
        # 输出给父脚本解析的格式
        print(f"\n[RESULT] existing={existing} added={added} total={total}")
        print("\n完成!")
        return existing, added, total
    else:
        print("\n未能获取新闻")
        return 0, 0, 0

if __name__ == "__main__":
    main()
