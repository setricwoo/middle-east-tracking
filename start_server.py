#!/usr/bin/env python3
"""
启动本地HTTP服务器并自动打开浏览器
"""

import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 8000

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """支持CORS的请求处理器"""
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # 简化日志输出
        pass

def start_server():
    """启动HTTP服务器"""
    server = HTTPServer(('localhost', PORT), CORSRequestHandler)
    print(f"服务器已启动: http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器")
    server.serve_forever()

def open_browser():
    """延迟2秒后打开浏览器"""
    time.sleep(2)
    url = f"http://localhost:{PORT}/data-tracking.html"
    print(f"正在打开浏览器: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 50)
    print("启动本地开发服务器")
    print("=" * 50)
    
    # 在新线程打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动服务器
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n服务器已停止")
