from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    
    logs = []
    def handle_console(msg):
        logs.append(f'{msg.type}: {msg.text}')
    page.on('console', handle_console)
    
    page.goto('http://localhost:8080/data-tracking-static.html')
    page.wait_for_timeout(3000)
    
    # 点击Polymarket tab
    page.click('button:has-text("Polymarket")')
    page.wait_for_timeout(2000)
    
    for log in logs[-10:]:
        print(log)
    
    browser.close()
