#!/usr/bin/env bash
set -euo pipefail

echo "🛑 Stopping Spectra AI services"

# Kill FastAPI (main.py) & Flask (app.py) if any
pids=$(pgrep -f "main.py" || true)
if [ -n "$pids" ]; then
  echo "⚡ Stopping FastAPI: $pids"
  kill $pids || true
fi

fpids=$(pgrep -f "app.py" || true)
if [ -n "$fpids" ]; then
  echo "🧪 Stopping Flask (legacy): $fpids"
  kill $fpids || true
fi

# Kill frontend Vite dev server
vpids=$(pgrep -f "vite" || true)
if [ -n "$vpids" ]; then
  echo "⚛️ Stopping Vite dev server: $vpids"
  kill $vpids || true
fi

echo "(Optional) To stop Ollama, run: pkill -f 'ollama serve'"
echo "✅ All targeted services stopped"
