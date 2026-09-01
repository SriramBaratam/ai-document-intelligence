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

CONTRADICTION_NAV = r'''
<style id="contradiction-nav-style">
#contradictionNavButton{height:34px;padding:0 12px;border:1px solid #f0443844;border-radius:9px;background:var(--panel);color:var(--text);font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;cursor:pointer;transition:.15s}
#contradictionNavButton:hover{transform:translateY(-1px);background:var(--panel2);border-color:#f0443880;box-shadow:0 7px 18px rgba(240,68,56,.12)}
#contradictionNavButton svg{width:13px;height:13px;color:#f04438}
#contradictionNavButton:disabled{opacity:.45;cursor:not-allowed;transform:none;box-shadow:none}
#contradictionOverlay{position:fixed;inset:0;background:#0f172a80;backdrop-filter:blur(5px);display:none;place-items:center;padding:18px;z-index:90}
#contradictionOverlay.show{display:grid}
#contradictionModal{width:min(1000px,96vw);max-height:88vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);padding:20px}
.cd-head{display:flex;align-items:flex-start;justify-content:space-between;gap:15px}.cd-head h2{font-size:17px;margin:0}.cd-desc{font-size:9px;color:var(--muted);line-height:1.55;margin:5px 0 0}.cd-close{width:30px;height:30px;border:0;background:transparent;border-radius:7px;color:var(--muted);font-size:20px}.cd-close:hover{background:var(--soft)}
.cd-summary{display:flex;gap:8px;flex-wrap:wrap;margin:17px 0 13px}.cd-chip{padding:6px 9px;border:1px solid var(--line);border-radius:999px;background:var(--panel2);font-size:8px;font-weight:850;color:var(--muted)}.cd-chip strong{color:var(--text)}
.cd-list{display:flex;flex-direction:column;gap:10px}.cd-card{border:1px solid var(--line);border-radius:13px;background:var(--panel2);overflow:hidden}.cd-card-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 13px;border-bottom:1px solid var(--line)}.cd-title{font-size:10px;font-weight:900}.cd-confidence{font-size:8px;font-weight:900;padding:4px 7px;border-radius:999px;background:#f0443815;color:#f04438}.cd-confidence.medium{background:#f7900915;color:#b54708}.cd-confidence.low{background:#66708515;color:#667085}.cd-body{padding:12px 13px}.cd-evidence{display:grid;grid-template-columns:1fr 1fr;gap:9px}.cd-side{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:10px}.cd-label{font-size:7px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}.cd-source{font-size:8px;font-weight:850;margin-top:4px}.cd-page{font-size:7px;color:var(--muted);margin-top:2px}.cd-claim{font-size:9px;line-height:1.55;margin-top:8px}.cd-why{margin-top:10px;padding:10px;border-radius:9px;background:var(--brandSoft);color:var(--text);font-size:9px;line-height:1.55}.cd-why strong{font-size:8px}.cd-empty{padding:32px 15px;text-align:center;border:1px dashed var(--line);border-radius:12px;background:var(--panel2)}.cd-empty-icon{font-size:25px}.cd-empty b{display:block;font-size:11px;margin-top:8px}.cd-empty span{display:block;color:var(--muted);font-size:8px;margin-top:5px}.cd-loading{padding:38px;text-align:center;color:var(--muted);font-size:9px}.cd-spinner{display:inline-block;width:17px;height:17px;border:2px solid #635bff30;border-top-color:var(--brand);border-radius:50%;animation:cdspin .7s linear infinite;vertical-align:-4px;margin-right:7px}@keyframes cdspin{to{transform:rotate(360deg)}}
@media(max-width:700px){.cd-evidence{grid-template-columns:1fr}#contradictionNavButton{padding:0 9px}.cd-card-head{align-items:flex-start}}
</style>
<div id="contradictionOverlay"><div id="contradictionModal" role="dialog" aria-modal="true" aria-labelledby="contradictionTitle"><div class="cd-head"><div><h2 id="contradictionTitle">Contradiction detector</h2><p class="cd-desc">Cross-checks semantically related evidence in your indexed documents and flags only claims that cannot both be true under the same context.</p></div><button class="cd-close" id="contradictionClose" aria-label="Close">×</button></div><div id="contradictionContent"></div></div></div>
<script>
(function(){
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const byId=id=>document.getElementById(id);
  function hasDocs(){const n=byId('docCount');return !!n && Number(n.textContent||0)>0}
  function updateButton(){const b=byId('contradictionNavButton');if(b)b.disabled=!hasDocs()}
  function close(){byId('contradictionOverlay')?.classList.remove('show')}
  function open(){
    const overlay=byId('contradictionOverlay');
    const content=byId('contradictionContent');
    overlay.classList.add('show');
    if(!hasDocs()){
      content.innerHTML='<div class="cd-empty"><div class="cd-empty-icon">📄</div><b>Upload documents first</b><span>Contradiction analysis needs at least two indexed evidence chunks.</span></div>';
      return;
    }
    content.innerHTML='<div class="cd-loading"><span class="cd-spinner"></span>Comparing grounded evidence…</div>';
    fetch('http://localhost:8000/contradictions',{method:'POST'})
      .then(async r=>{const j=await r.json();if(!r.ok)throw new Error(j.detail||'Analysis failed');return j})
      .then(render)
      .catch(err=>{content.innerHTML='<div class="cd-empty"><div class="cd-empty-icon">⚠️</div><b>Analysis could not be completed</b><span>'+esc(err.message)+'</span></div>'})
  }
  function render(data){
    const items=Array.isArray(data.contradictions)?data.contradictions:[];
    const summary='<div class="cd-summary"><span class="cd-chip">Pairs analyzed <strong>'+esc(data.pairs_analyzed||0)+'</strong></span><span class="cd-chip">Potential contradictions <strong>'+esc(items.length)+'</strong></span><span class="cd-chip">Grounded in indexed evidence</span></div>';
    if(!items.length){
      byId('contradictionContent').innerHTML=summary+'<div class="cd-empty"><div class="cd-empty-icon">✓</div><b>No contradictions found</b><span>'+esc(data.message||'No reliable contradictions were identified in the indexed documents.')+'</span></div>';
      return;
    }
    const cards=items.map((x,i)=>{
      const conf=String(x.confidence||'Medium').toLowerCase();
      const pageA=x.page_a?'Page '+esc(x.page_a):'Page not available';
      const pageB=x.page_b?'Page '+esc(x.page_b):'Page not available';
      return '<article class="cd-card"><div class="cd-card-head"><div class="cd-title">'+esc(x.title||('Potential contradiction '+(i+1)))+'</div><span class="cd-confidence '+esc(conf)+'">'+esc(x.confidence||'Medium')+' confidence</span></div><div class="cd-body"><div class="cd-evidence"><div class="cd-side"><div class="cd-label">Evidence A</div><div class="cd-source">'+esc(x.document_a||'Unknown document')+'</div><div class="cd-page">'+pageA+'</div><div class="cd-claim">'+esc(x.claim_a||'')+'</div></div><div class="cd-side"><div class="cd-label">Evidence B</div><div class="cd-source">'+esc(x.document_b||'Unknown document')+'</div><div class="cd-page">'+pageB+'</div><div class="cd-claim">'+esc(x.claim_b||'')+'</div></div></div><div class="cd-why"><strong>WHY THIS MAY CONFLICT</strong><br>'+esc(x.explanation||'')+'</div></div></article>';
    }).join('');
    byId('contradictionContent').innerHTML=summary+'<div class="cd-list">'+cards+'</div>';
  }
  function addButton(){
    if(byId('contradictionNavButton')){updateButton();return}
    const actions=document.querySelector('.headactions');
    if(!actions)return;
    const b=document.createElement('button');
    b.id='contradictionNavButton';b.type='button';b.title='Find contradictions across indexed documents';
    b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 4h6M9 20h6M7 7l-2 2 2 2M17 13l2 2-2 2M5 9h7M12 15h7"/><path d="M12 3v18"/></svg><span>Find conflicts</span>';
    b.onclick=open;actions.insertBefore(b,actions.firstChild);updateButton();
  }
  byId('contradictionClose').onclick=close;
  byId('contradictionOverlay').addEventListener('click',e=>{if(e.target.id==='contradictionOverlay')close()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addButton);else addButton();
  new MutationObserver(()=>{addButton();updateButton()}).observe(document.documentElement,{childList:true,subtree:true});
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
        # Inject feature navigation into the existing workspace without changing
        # index.html. This keeps the current UI/functionality intact while making
        # the quiz and contradiction analysis features discoverable.
        if self.path in ('/', '/index.html'):
            try:
                html = Path('index.html').read_text(encoding='utf-8')
                if 'id="quiz-nav-style"' not in html:
                    html = html.replace('</body>', QUIZ_NAV + '</body>')
                if 'id="contradiction-nav-style"' not in html:
                    html = html.replace('</body>', CONTRADICTION_NAV + '</body>')
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
