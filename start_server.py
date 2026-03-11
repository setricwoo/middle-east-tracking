#!/usr/bin/env python3
"""
启动本地 HTTP 服务器，解决 CORS 问题
"""

import http.server
import socketserver
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"服务器已启动: http://localhost:{PORT}")
    print(f"请访问: http://localhost:{PORT}/polymarket.html")
    print("按 Ctrl+C 停止服务器")
    httpd.serve_forever()
