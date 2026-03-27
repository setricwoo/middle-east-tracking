from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    
    # 收集所有控制台消息
    logs = []
    def handle_console(msg):
        logs.append(f'{msg.type}: {msg.text}')
    page.on('console', handle_console)
    
    # 收集JavaScript错误
    errors = []
    def handle_page_error(error):
        errors.append(f'Page error: {error}')
    page.on('pageerror', handle_page_error)
    
    page.goto('http://localhost:8080/data-tracking-static.html')
    page.wait_for_timeout(2000)
    
    # 尝试点击Polymarket tab
    try:
        page.click('button:has-text("Polymarket")')
        page.wait_for_timeout(1000)
    except Exception as e:
        print(f'Click error: {e}')
    
    print('Console logs:')
    for log in logs:
        print(f'  {log}')
    
    print('\nPage errors:')
    for err in errors:
        print(f'  {err}')
    
    browser.close()
