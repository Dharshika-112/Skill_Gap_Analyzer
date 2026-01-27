#!/usr/bin/env python3
"""
Quick Server for Skill Gap Analyzer
Serves the quick analyzer on port 3001
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3001

class QuickHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/quick_skill_analyzer.html'
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), QuickHandler) as httpd:
        print(f"🚀 Quick Skill Gap Analyzer Server")
        print(f"📍 URL: http://localhost:{PORT}")
        print(f"🎯 Features: All ATS features in one fast interface")
        print(f"⚡ Ready for testing!")
        print("-" * 60)
        
        # Auto-open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n✅ Server stopped")