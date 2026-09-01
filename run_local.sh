#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "❌ .venv not found. Create it first: python3 -m venv .venv"
  exit 1
fi

echo "🧹 Stopping stale project servers..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "python serve_frontend.py" 2>/dev/null || true
pkill -f "python serve_frontend_ai.py" 2>/dev/null || true
sleep 1

echo "🔎 Checking Ollama..."
if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "✓ Ollama is running"
else
  echo "⚠️ Ollama is not running. Starting ollama serve..."
  if ! command -v ollama >/dev/null 2>&1; then
    echo "❌ Ollama is not installed. Install Ollama, then run this script again."
    exit 1
  fi
  nohup ollama serve >/tmp/ai-document-intelligence-ollama.log 2>&1 &
  for _ in {1..20}; do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then break; fi
    sleep 1
  done
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags | grep -q 'llama3.2:3b'; then
  echo "⬇️ llama3.2:3b is missing. Pulling it now..."
  ollama pull llama3.2:3b
fi

echo "🚀 Starting API on http://127.0.0.1:8000"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 >/tmp/ai-document-intelligence-api.log 2>&1 &

echo "🌐 Starting frontend on http://127.0.0.1:3000"
nohup python serve_frontend_ai.py >/tmp/ai-document-intelligence-frontend.log 2>&1 &

sleep 2
curl -fsS http://127.0.0.1:8000/health | python -m json.tool

echo ""
echo "✅ AI Document Intelligence is ready"
echo "   Open: http://localhost:3000"
echo "   API:  http://localhost:8000/docs"
echo "   ✨ AI Actions: enabled"
echo ""
echo "Logs:"
echo "   API:      /tmp/ai-document-intelligence-api.log"
echo "   Frontend: /tmp/ai-document-intelligence-frontend.log"
echo "   Ollama:   /tmp/ai-document-intelligence-ollama.log"
