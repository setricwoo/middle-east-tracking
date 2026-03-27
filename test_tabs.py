from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    page.goto('http://localhost:8080/data-tracking-static.html')
    page.wait_for_timeout(2000)
    
    # 测试点击每个tab
    tab_names = [
        ('polymarket', 'Polymarket'),
        ('commodities', '商品'),
        ('liquidity', '流动性'),
        ('financial', '金融'),
        ('war', '战局')
    ]
    
    for tab_id, tab_text in tab_names:
        try:
            # 点击tab按钮
            btn = page.locator(f'button[onclick*="{tab_id}"]')
            if btn.count() > 0:
                btn.click()
                page.wait_for_timeout(1000)
                
                # 检查tab是否显示
                is_visible = page.locator(f'#tab-{tab_id}').is_visible()
                has_active = page.locator(f'#tab-{tab_id}.active').count() > 0
                print(f'{tab_id}: visible={is_visible}, active={has_active}')
            else:
                print(f'{tab_id}: button not found')
        except Exception as e:
            print(f'{tab_id}: error - {e}')
    
    browser.close()
