#!/usr/bin/env python3
"""
启动本地HTTP服务器来正确查看HTML页面
解决file://协议下的跨域限制问题
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

os.chdir(Path(__file__).parent)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    url = f"http://localhost:{PORT}/war-situation.html"
    print(f"\n服务器已启动: {url}")
    print("按 Ctrl+C 停止服务器\n")
    
    # 自动打开浏览器
    webbrowser.open(url)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
