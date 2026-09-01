/* AI readiness + query UX patch.
   Loaded by serve_frontend.py after index.html so the existing UI stays intact. */
(function () {
  const wait = (fn) => {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once: true });
    else fn();
  };

  wait(function () {
    const originalHealth = window.health;

    window.health = async function () {
      try {
        const r = await fetch(window.API + '/health', { cache: 'no-store' });
        const j = await r.json();
        const ai = j.ai || {};
        const dot = document.getElementById('healthDot');
        const text = document.getElementById('healthText');

        if (!r.ok) throw new Error(j.detail || 'Health check failed');

        dot.className = ai.ready ? 'dot ok' : 'dot';
        text.textContent = ai.ready ? 'AI ready' : 'Backend connected · AI offline';
        text.title = ai.ready ? ('Model: ' + (ai.model || 'local AI')) : (ai.message || 'Start Ollama and ensure the configured model is installed.');
      } catch (e) {
        const dot = document.getElementById('healthDot');
        const text = document.getElementById('healthText');
        dot.className = 'dot bad';
        text.textContent = 'Backend offline';
        text.title = 'Cannot reach the FastAPI server.';
      }
    };

    // Replace the query flow so backend/LLM failures are visible in the chat,
    // not hidden behind a generic toast.
    window.ask = async function (q) {
      q = String(q || '').trim();
      if (!q) return;
      if (!window.docs || !window.docs.length) {
        toast('Upload a document first');
        document.getElementById('uploadModal').classList.add('show');
        return;
      }

      addMessage('user', q);
      document.getElementById('send').disabled = true;
      document.getElementById('input').disabled = true;
      const id = messages.length;
      addMessage('ai', '');
      const el = document.getElementById('messages').lastElementChild;
      el.querySelector('.bubble').innerHTML = '<span class="spin"></span> Searching your documents and generating a grounded answer…';

      try {
        const r = await fetch(window.API + '/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q })
        });
        const raw = await r.text();
        let j = {};
        try { j = raw ? JSON.parse(raw) : {}; } catch (_) {}
        if (!r.ok) throw new Error(j.detail || ('Request failed (' + r.status + ')'));

        const answer = String(j.answer || '').trim();
        if (!answer) throw new Error('The AI returned an empty answer. Check that Ollama is running and the configured model is installed.');
        messages[id] = { role: 'ai', text: answer, retrieved: j.retrieved_docs || [] };
        renderMessages();
        saveHistory();
      } catch (e) {
        messages[id] = {
          role: 'ai',
          text: 'I could not generate the answer.\n\n' + e.message,
          retrieved: []
        };
        renderMessages();
        toast('AI request failed — see the answer for details');
      } finally {
        document.getElementById('send').disabled = false;
        document.getElementById('input').disabled = false;
        document.getElementById('input').focus();
        window.health();
      }
    };

    // The original script already bound buttons to the global ask() function;
    // re-bind prompt cards here as well to guarantee the patched function is used.
    document.querySelectorAll('.prompt').forEach((b) => {
      b.onclick = () => window.ask(b.dataset.q || '');
    });

    window.health();
  });
})();
