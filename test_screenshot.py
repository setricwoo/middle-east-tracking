from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    
    page.goto('http://localhost:8080/data-tracking-static.html')
    page.wait_for_timeout(2000)
    
    # 截图 - 默认在strait tab
    page.screenshot(path='test1_strait.png')
    
    # 点击Polymarket tab
    page.click('button:has-text("Polymarket")')
    page.wait_for_timeout(2000)
    page.screenshot(path='test2_polymarket.png')
    
    # 点击商品 tab
    page.click('button:has-text("商品")')
    page.wait_for_timeout(2000)
    page.screenshot(path='test3_commodities.png')
    
    print('Screenshots saved')
    browser.close()
