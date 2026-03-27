from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    
    page.goto('http://localhost:8080/data-tracking-static.html')
    page.wait_for_timeout(2000)
    
    # 测试所有tab
    tabs = [
        ('strait', '海峡'),
        ('commodities', '商品'),
        ('liquidity', '流动性'),
        ('financial', '金融')
    ]
    
    for tab_id, tab_name in tabs:
        # 点击tab
        page.click(f'button:has-text("{tab_name}")')
        page.wait_for_timeout(1000)
        
        # 检查是否可见
        is_visible = page.locator(f'#tab-{tab_id}').is_visible()
        is_active = page.locator(f'#tab-{tab_id}.active').count() > 0
        print(f'{tab_id}: visible={is_visible}, active={is_active}')
        
        # 截图
        page.screenshot(path=f'final_{tab_id}.png')
    
    browser.close()
