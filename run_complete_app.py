#!/usr/bin/env python3
"""
Complete Skill Gap Analyzer Application Server
Serves the comprehensive application on port 3002
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3002

class AppHandler(http.server.SimpleHTTPRequestHandler):
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
    
    with socketserver.TCPServer(("", PORT), AppHandler) as httpd:
        print("🚀 CareerBoost AI - Complete Application")
        print("=" * 60)
        print(f"📍 Frontend URL: http://localhost:{PORT}")
        print(f"🎯 Features Available:")
        print("   ✅ Skill Gap Analyzer")
        print("   ✅ ATS Resume Scoring") 
        print("   ✅ Improvement Suggestions")
        print("   ✅ Profile Management")
        print("   ✅ Beautiful UI/UX with Animations")
        print("   ✅ Responsive Design")
        print("=" * 60)
        print("🧠 AI Features:")
        print("   • Real dataset analysis (1000+ jobs)")
        print("   • ML-based ATS scoring")
        print("   • Intelligent skill matching")
        print("   • Personalized suggestions")
        print("=" * 60)
        
        # Auto-open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n✅ Application stopped")
            print("Thank you for using CareerBoost AI!")