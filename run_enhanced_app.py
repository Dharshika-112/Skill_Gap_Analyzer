#!/usr/bin/env python3
"""
Enhanced Skill Gap Analyzer Application Server
Serves the improved application with all new features
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3003

class EnhancedAppHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/skill_gap_analyzer_complete.html'
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), EnhancedAppHandler) as httpd:
        print("🚀 CareerBoost AI - Enhanced Application")
        print("=" * 70)
        print(f"📍 Frontend URL: http://localhost:{PORT}")
        print(f"🎯 NEW ENHANCED FEATURES:")
        print("   ✅ Auto-analyze ALL jobs in dataset")
        print("   ✅ Show suitable jobs based on skills")
        print("   ✅ Experience level consideration")
        print("   ✅ Comprehensive job matching")
        print("   ✅ Multiple role comparison")
        print("   ✅ Enhanced UI with job cards")
        print("   ✅ Smart filtering and search")
        print("=" * 70)
        print("🧠 IMPROVED WORKFLOW:")
        print("   1. Select skills → 2. Choose experience → 3. Find suitable jobs")
        print("   4. Browse all available roles → 5. Compare multiple roles")
        print("=" * 70)
        
        # Auto-open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n✅ Enhanced application stopped")
            print("Thank you for using CareerBoost AI Enhanced!")