AI_ACTIONS_NAV = r'''
<style id="ai-actions-nav-style">
#aiActionsWrap{position:relative;display:inline-flex}
#aiActionsButton{height:34px;padding:0 12px;border:1px solid #7c6cff55;border-radius:9px;background:linear-gradient(135deg,#635bff,#8b5cf6);color:#fff;font-size:9px;font-weight:900;display:inline-flex;align-items:center;gap:6px;box-shadow:0 6px 16px #635bff22;cursor:pointer;transition:.15s}
#aiActionsButton:hover{transform:translateY(-1px);box-shadow:0 9px 22px #635bff35}
#aiActionsButton svg{width:13px;height:13px}
#aiActionsMenu{position:absolute;right:0;top:42px;width:245px;padding:7px;background:var(--panel);border:1px solid var(--line);border-radius:13px;box-shadow:var(--shadow);z-index:95;display:none}
#aiActionsMenu.show{display:block}
.ai-action{width:100%;border:0;background:transparent;border-radius:9px;padding:9px 10px;display:flex;align-items:center;gap:9px;text-align:left;color:var(--text);cursor:pointer}
.ai-action:hover{background:var(--panel2)}
.ai-action:disabled{opacity:.45;cursor:not-allowed}
.ai-action-icon{width:27px;height:27px;flex:0 0 27px;border-radius:8px;background:var(--brandSoft);color:var(--brand);display:grid;place-items:center;font-size:12px;font-weight:900}
.ai-action-main{min-width:0;flex:1}.ai-action-main b{display:block;font-size:9px}.ai-action-main span{display:block;color:var(--muted);font-size:7.5px;margin-top:2px;line-height:1.35}
.ai-action-divider{height:1px;background:var(--line);margin:5px 4px}
.ai-action-note{padding:7px 10px;color:var(--muted);font-size:7.5px;line-height:1.4}
@media(max-width:700px){#aiActionsButton{padding:0 9px}#aiActionsMenu{right:auto;left:0}}
</style>
<script>
(function(){
  const ACTIONS=[
    ['≡','Summarize','Create a concise overview of the indexed documents.','Summarize the indexed documents.'],
    ['◆','Key findings','Surface the most important findings and conclusions.','Identify the key findings, conclusions, and important facts in the indexed documents.'],
    ['#','Extract details','Pull out names, dates, numbers, metrics, and requirements.','Extract the important names, dates, numbers, metrics, requirements, and other concrete details from the indexed documents.'],
    ['✓','Action items','Turn the documents into clear tasks, owners, and next steps when supported.','Identify actionable tasks, responsibilities, deadlines, and next steps stated or clearly supported by the indexed documents.'],
    ['Aa','Explain simply','Explain the document in plain, easy-to-understand language.','Explain the indexed documents in simple language, preserving important facts and terminology.'],
    ['↔','Compare documents','Compare the indexed documents and highlight meaningful differences.','Compare the indexed documents. Highlight agreements, differences, conflicting claims, and important distinctions.'],
    ['?','Generate questions','Suggest useful questions that the indexed documents can answer.','Generate useful questions that can be answered from the indexed documents, grouped by topic.']
  ];
  const byId=id=>document.getElementById(id);
  function hasDocs(){const n=byId('docCount');return !!n && Number(n.textContent||0)>0}
  function closeMenu(){byId('aiActionsMenu')?.classList.remove('show')}
  function run(prompt){
    if(!hasDocs()){
      window.alert('Upload and index a document first.');
      return;
    }
    closeMenu();
    const input=byId('input');
    if(input){input.value=prompt;input.dispatchEvent(new Event('input',{bubbles:true}));}
    if(typeof window.ask==='function') window.ask(prompt);
    else if(byId('send')) byId('send').click();
  }
  function update(){const wrap=byId('aiActionsWrap');if(!wrap)return;const disabled=!hasDocs();wrap.querySelectorAll('.ai-action').forEach(b=>b.disabled=disabled)}
  function add(){
    if(byId('aiActionsWrap')){update();return}
    const actions=document.querySelector('.headactions');if(!actions)return;
    const wrap=document.createElement('div');wrap.id='aiActionsWrap';
    wrap.innerHTML='<button id="aiActionsButton" type="button" title="Run a grounded AI action"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v4M12 17v4M4.2 5.2l2.8 2.8M17 16l2.8 2.8M3 12h4M17 12h4M4.2 18.8L7 16M17 8l2.8-2.8"/><circle cx="12" cy="12" r="4"/></svg><span>AI Actions</span></button><div id="aiActionsMenu"></div>';
    const menu=wrap.querySelector('#aiActionsMenu');
    ACTIONS.forEach((a,i)=>{
      if(i===4)menu.insertAdjacentHTML('beforeend','<div class="ai-action-divider"></div>');
      const b=document.createElement('button');b.className='ai-action';b.type='button';b.innerHTML='<span class="ai-action-icon">'+a[0]+'</span><span class="ai-action-main"><b>'+a[1]+'</b><span>'+a[2]+'</span></span>';b.onclick=()=>run(a[3]);menu.appendChild(b);
    });
    menu.insertAdjacentHTML('beforeend','<div class="ai-action-note">Runs against your indexed local context. No outside web knowledge is used.</div>');
    wrap.querySelector('#aiActionsButton').onclick=e=>{e.stopPropagation();menu.classList.toggle('show');update()};
    document.addEventListener('click',e=>{if(!wrap.contains(e.target))closeMenu()});
    actions.insertBefore(wrap,actions.firstChild);update();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',add);else add();
  new MutationObserver(()=>{add();update()}).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
