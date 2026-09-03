#!/usr/bin/env python3
"""Frontend server with injected professional AI Actions navigation."""

import http.server
import socketserver
from pathlib import Path

from serve_frontend import QUIZ_NAV, CONTRADICTION_NAV
from ai_actions_nav import AI_ACTIONS_NAV

PORT = 3000
ROOT = Path(__file__).parent


class AIFrontendHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            try:
                html = (ROOT / 'index.html').read_text(encoding='utf-8')
                html = html.replace('</body>', QUIZ_NAV + CONTRADICTION_NAV + AI_ACTIONS_NAV + '</body>')
                body = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as exc:
                self.send_error(500, f'Could not render frontend: {exc}')
                return
        super().do_GET()


if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), AIFrontendHandler) as httpd:
        print(f"🌐 Frontend server running on http://localhost:{PORT}")
        print("✨ AI Actions menu enabled")
        print("📖 Open http://localhost:3000 in your browser")
        print("🔗 API should be running on http://localhost:8000")
        print("⛔ Press Ctrl+C to stop the server\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")
