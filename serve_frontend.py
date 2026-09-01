#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend.
Serves index.html on http://localhost:8000
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
HANDLER = http.server.SimpleHTTPRequestHandler

# Change to project directory
os.chdir(Path(__file__).parent)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow requests to the API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend server running on http://localhost:{PORT}")
        print(f"📖 Open http://localhost:{PORT} in your browser")
        print(f"🔗 Make sure the API server is running on http://localhost:8000")
        print(f"⛔ Press Ctrl+C to stop the server\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")
