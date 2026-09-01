#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend.
Serves the workspace on http://localhost:3000
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000

os.chdir(Path(__file__).parent)

QUIZ_NAV = r'''
<style id="quiz-nav-style">
#quizNavButton{height:34px;padding:0 12px;border:1px solid #7c6cff55;border-radius:9px;background:linear-gradient(135deg,#635bff,#8b5cf6);color:#fff;font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;box-shadow:0 6px 16px #635bff22;cursor:pointer;transition:.15s}
#quizNavButton:hover{transform:translateY(-1px);box-shadow:0 9px 22px #635bff35}
#quizNavButton svg{width:13px;height:13px}
</style>
<script>
(function(){
  function addQuizButton(){
    if(document.getElementById('quizNavButton')) return;
    const actions=document.querySelector('.headactions');
    if(!actions) return;
    const button=document.createElement('button');
    button.id='quizNavButton';
    button.type='button';
    button.title='Create a quiz from your indexed documents';
    button.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg><span>Quiz me</span>';
    button.onclick=function(){ window.location.href='/quiz.html'; };
    actions.insertBefore(button, actions.firstChild);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',addQuizButton);
  else addQuizButton();
  new MutationObserver(addQuizButton).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Inject the Quiz Me action into the existing workspace without changing
        # index.html. This keeps the current UI/functionality intact while making
        # the new quiz feature discoverable from the main navigation.
        if self.path in ('/', '/index.html'):
            try:
                html = Path('index.html').read_text(encoding='utf-8')
                if 'id="quiz-nav-style"' not in html:
                    html = html.replace('</body>', QUIZ_NAV + '</body>')
                body = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception:
                pass
        super().do_GET()


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
