#!/usr/bin/env bash
set -euo pipefail

echo "🌟 Setting up Spectra AI (Linux/macOS)"
echo "======================================"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

need() { command -v "$1" >/dev/null 2>&1 || { echo "❌ Missing: $1"; MISSING=1; }; }
MISSING=0

echo "🔍 Checking prerequisites"
need python
need node
need npm
need ollama || true  # Allow continuing without immediate Ollama install

if [ "$MISSING" -eq 1 ]; then
	echo "❌ Install missing prerequisites then rerun."; exit 1; fi
echo "✅ Core tools present"

if [ ! -d .venv ]; then
	echo "🐍 Creating virtual environment (.venv)"; python -m venv .venv; fi
source .venv/bin/activate

echo "📦 Installing Python dependencies (latest)"
python -m pip install --upgrade pip setuptools wheel >/dev/null
pip install --no-cache-dir -r requirements.txt
echo "✅ Python dependencies installed"

echo "📱 Installing frontend dependencies"
pushd frontend >/dev/null
npm install
popd >/dev/null
echo "✅ Frontend dependencies installed"

if [ ! -f .env ]; then
	cp .env.example .env
	echo "✅ Created .env from template (edit as needed)"
else
	echo "ℹ️ .env already exists"
fi

cat <<NOTE
--------------------------------------------------
🤖 Ollama Models (run manually if not present):
	ollama pull openhermes:7b-mistral-v2.5-q4_K_M
	ollama pull mistral:7b

🚀 Start development stack:
	./start.sh

🛑 Stop services:
	./stop.sh

🧠 Tabnine (AI code completion) enabled via .vscode/extensions.json
	Install recommended extensions when prompted in VS Code.
--------------------------------------------------
NOTE

echo "🎉 Setup complete"

