"""Simple static file server for frontend with CORS headers"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import sys

PORT = 3000

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(__file__) or '.')
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║       SKILL GAP ANALYZER - FRONTEND SERVER                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    ✅ Frontend Server Running:
    → Main App: http://localhost:{PORT}/index.html
    → Legacy Upload: http://localhost:{PORT}/app.html
    
    ⚠️  IMPORTANT: Use the URL above, NOT file:// protocol!
    
    Backend should be running at: http://localhost:8000
    
    Press Ctrl+C to stop the server.
    """)
    try:
        with socketserver.TCPServer(('0.0.0.0', PORT), CORSRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped')
        sys.exit(0)
    except OSError as e:
        if e.errno == 98 or 'Address already in use' in str(e):
            print(f'\n❌ ERROR: Port {PORT} is already in use!')
            print(f'   Solution: Close other server or change PORT in server.py')
        else:
            print(f'\n❌ ERROR: {e}')
        sys.exit(1)