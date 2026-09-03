#!/usr/bin/env python3
"""Simple HTTP server to serve the frontend with feature navigation."""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
os.chdir(Path(__file__).parent)

QUIZ_NAV = r'''
<style id="quiz-nav-style">
#quizNavButton{height:34px;padding:0 12px;border:1px solid #7c6cff55;border-radius:9px;background:linear-gradient(135deg,#635bff,#8b5cf6);color:#fff;font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;box-shadow:0 6px 16px #635bff22;cursor:pointer}
#quizNavButton:hover{transform:translateY(-1px);box-shadow:0 9px 22px #635bff35}#quizNavButton svg{width:13px;height:13px}
</style>
<script>(function(){function add(){if(document.getElementById('quizNavButton'))return;const a=document.querySelector('.headactions');if(!a)return;const b=document.createElement('button');b.id='quizNavButton';b.type='button';b.title='Create a quiz from your indexed documents';b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3h8a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M9 8h6M9 12h6M9 16h4"/></svg><span>Quiz me</span>';b.onclick=()=>location.href='/quiz.html';a.insertBefore(b,a.firstChild)}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',add);else add();new MutationObserver(add).observe(document.documentElement,{childList:true,subtree:true})})();</script>
'''

AI_ACTIONS = r'''
<style id="ai-actions-style">
#aiActionsWrap{position:relative;display:inline-flex}#aiActionsButton{height:34px;padding:0 12px;border:1px solid #7c6cff66;border-radius:9px;background:linear-gradient(135deg,#635bff,#8b5cf6);color:#fff;font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;box-shadow:0 6px 16px #635bff22;cursor:pointer}#aiActionsButton:hover{transform:translateY(-1px);box-shadow:0 9px 22px #635bff35}#aiActionsButton svg{width:13px;height:13px}#aiActionsMenu{position:absolute;right:0;top:41px;width:250px;background:var(--panel);border:1px solid var(--line);border-radius:13px;box-shadow:0 18px 45px rgba(0,0,0,.25);padding:6px;z-index:80;display:none}#aiActionsMenu.show{display:block}.ai-action{width:100%;border:0;background:transparent;border-radius:9px;padding:9px 10px;text-align:left;display:flex;align-items:center;gap:9px;color:var(--text);cursor:pointer}.ai-action:hover{background:var(--panel2)}.ai-action-icon{width:28px;height:28px;border-radius:8px;background:var(--brandSoft);color:var(--brand);display:grid;place-items:center;font-size:13px;flex:0 0 28px}.ai-action b{display:block;font-size:9px}.ai-action span{display:block;color:var(--muted);font-size:7.5px;margin-top:2px}.ai-modal-overlay{position:fixed;inset:0;background:#0f172a80;backdrop-filter:blur(5px);display:none;place-items:center;padding:18px;z-index:100}.ai-modal-overlay.show{display:grid}.ai-modal{width:min(760px,94vw);max-height:88vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow);padding:20px}.ai-modal-head{display:flex;justify-content:space-between;gap:15px}.ai-modal h2{font-size:16px;margin:0}.ai-modal-desc{font-size:9px;color:var(--muted);line-height:1.55;margin:5px 0 15px}.ai-close{width:29px;height:29px;border:0;background:transparent;border-radius:7px;color:var(--muted);font-size:18px}.ai-close:hover{background:var(--soft)}.ai-result{font-size:11px;line-height:1.7;white-space:pre-wrap}.ai-loading{text-align:center;color:var(--muted);padding:35px;font-size:9px}.ai-error{padding:12px;border-radius:9px;background:#f0443812;color:var(--danger);font-size:9px}.ai-empty{text-align:center;padding:28px;color:var(--muted);font-size:9px;border:1px dashed var(--line);border-radius:11px}.ai-meta{margin-top:13px;padding-top:10px;border-top:1px solid var(--line);color:var(--muted);font-size:7.5px}
</style>
<div id="aiActionsOverlay" class="ai-modal-overlay"><div class="ai-modal" role="dialog" aria-modal="true"><div class="ai-modal-head"><div><h2 id="aiActionsTitle">AI Actions</h2><p id="aiActionsDesc" class="ai-modal-desc">Run a grounded action against your indexed documents.</p></div><button class="ai-close" id="aiActionsClose">×</button></div><div id="aiActionsContent"></div></div></div>
<script>
(function(){
const ACTIONS={
 summary:{label:'Summarize',icon:'✦',desc:'Get a concise overview of the indexed documents.',prompt:'Summarize the indexed documents. Give the main purpose, key ideas, important facts, and conclusions. Keep it concise and grounded only in the provided documents.'},
 findings:{label:'Key findings',icon:'◆',desc:'Surface the most important conclusions and facts.',prompt:'Identify the most important findings across the indexed documents. Use clear bullets and include important evidence or numbers when available. Stay grounded in the documents.'},
 details:{label:'Extract details',icon:'#',desc:'Pull out names, dates, numbers, metrics, and useful facts.',prompt:'Extract the most useful concrete details from the indexed documents, including names, dates, numbers, metrics, requirements, and other notable facts. Organize them clearly and do not invent information.'},
 actions:{label:'Action items',icon:'→',desc:'Find tasks, deadlines, requirements, and next steps.',prompt:'Find all actionable items in the indexed documents. List tasks, owners if stated, deadlines if stated, requirements, and recommended next steps. If an item is not explicitly stated, label it as an inference.'},
 explain:{label:'Explain simply',icon:'?',desc:'Turn difficult document content into plain language.',prompt:'Explain the indexed documents in simple language for a non-expert. Define important terms and explain the main ideas without losing important details. Use only information grounded in the documents.'},
 compare:{label:'Compare documents',icon:'⇄',desc:'Find agreements, differences, and conflicting claims.',prompt:'Compare the indexed documents. Identify agreements, differences, important changes, and any potentially conflicting claims. Cite document names and pages when the retrieved context provides them.'},
 questions:{label:'Generate questions',icon:'Q',desc:'Create useful questions that the documents can answer.',prompt:'Generate 10 useful questions that can be answered from the indexed documents. Mix factual, analytical, and practical questions. Do not include questions requiring information outside the documents.'}
};
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function hasDocs(){const n=document.getElementById('docCount');return n&&Number(n.textContent||0)>0}
function openAction(key){const a=ACTIONS[key];document.getElementById('aiActionsMenu')?.classList.remove('show');const o=document.getElementById('aiActionsOverlay'),c=document.getElementById('aiActionsContent');document.getElementById('aiActionsTitle').textContent=a.label;document.getElementById('aiActionsDesc').textContent=a.desc;o.classList.add('show');if(!hasDocs()){c.innerHTML='<div class="ai-empty">📄<br><b>Upload and index a document first.</b><br>AI Actions use the grounded document retrieval pipeline.</div>';return}c.innerHTML='<div class="ai-loading">✦ Running '+esc(a.label.toLowerCase())+' against your indexed documents…</div>';fetch('http://localhost:8000/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:a.prompt,top_k:6})}).then(async r=>{const j=await r.json();if(!r.ok)throw new Error(j.detail||'AI action failed');return j}).then(j=>{const answer=j.answer||j.response||j.result||'No grounded answer was returned.';c.innerHTML='<div class="ai-result">'+esc(answer)+'</div><div class="ai-meta">Grounded response · '+esc((j.sources||[]).length||0)+' source(s) returned</div>'}).catch(e=>{c.innerHTML='<div class="ai-error">'+esc(e.message)+'</div>'})}
function close(){document.getElementById('aiActionsOverlay')?.classList.remove('show')}
function addButton(){if(document.getElementById('aiActionsWrap'))return;const a=document.querySelector('.headactions');if(!a)return;const wrap=document.createElement('div');wrap.id='aiActionsWrap';const b=document.createElement('button');b.id='aiActionsButton';b.type='button';b.title='AI-powered actions for your documents';b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z"/></svg><span>AI Actions</span><span>⌄</span>';const menu=document.createElement('div');menu.id='aiActionsMenu';Object.entries(ACTIONS).forEach(([key,x])=>{const item=document.createElement('button');item.className='ai-action';item.type='button';item.innerHTML='<span class="ai-action-icon">'+esc(x.icon)+'</span><span><b>'+esc(x.label)+'</b><span>'+esc(x.desc)+'</span></span>';item.onclick=()=>openAction(key);menu.appendChild(item)});b.onclick=e=>{e.stopPropagation();menu.classList.toggle('show')};wrap.appendChild(b);wrap.appendChild(menu);a.insertBefore(wrap,a.firstChild)}
document.getElementById('aiActionsClose').onclick=close;document.getElementById('aiActionsOverlay').addEventListener('click',e=>{if(e.target.id==='aiActionsOverlay')close()});document.addEventListener('keydown',e=>{if(e.key==='Escape'){close();document.getElementById('aiActionsMenu')?.classList.remove('show')}});document.addEventListener('click',e=>{if(!e.target.closest('#aiActionsWrap'))document.getElementById('aiActionsMenu')?.classList.remove('show')});if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',addButton);else addButton();new MutationObserver(addButton).observe(document.documentElement,{childList:true,subtree:true})
})();
</script>
'''

CONTRADICTION_NAV = r'''
<style id="contradiction-nav-style">
#contradictionNavButton{height:34px;padding:0 12px;border:1px solid #f0443844;border-radius:9px;background:var(--panel);color:var(--text);font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;cursor:pointer}#contradictionNavButton:hover{background:var(--panel2);border-color:#f0443880}#contradictionNavButton svg{width:13px;height:13px;color:#f04438}#contradictionNavButton:disabled{opacity:.45;cursor:not-allowed}
</style>
<script>(function(){function add(){if(document.getElementById('contradictionNavButton'))return;const a=document.querySelector('.headactions');if(!a)return;const b=document.createElement('button');b.id='contradictionNavButton';b.type='button';b.innerHTML='⚠ <span>Find conflicts</span>';b.onclick=()=>location.href='/';a.insertBefore(b,a.firstChild)}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',add);else add();new MutationObserver(add).observe(document.documentElement,{childList:true,subtree:true})})();</script>
'''

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(200);self.end_headers()
    def do_GET(self):
        if self.path in ('/','/index.html'):
            try:
                html=Path('index.html').read_text(encoding='utf-8')
                for marker,block in [('quiz-nav-style',QUIZ_NAV),('ai-actions-style',AI_ACTIONS),('contradiction-nav-style',CONTRADICTION_NAV)]:
                    if marker not in html: html=html.replace('</body>',block+'</body>')
                body=html.encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body);return
            except Exception:
                pass
        super().do_GET()

if __name__=='__main__':
    with socketserver.TCPServer(("",PORT),MyHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend server running on http://localhost:{PORT}")
        print(f"🔗 API server expected on http://localhost:8000")
        try:httpd.serve_forever()
        except KeyboardInterrupt:print("\n✓ Server stopped")
