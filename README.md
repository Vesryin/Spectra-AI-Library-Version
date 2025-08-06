# Spectra AI - Emotionally Intelligent Assistant

## 🌟 About Spectra

Spectra is an emotionally intelligent AI assistant designed to help with expression through music, conversation, healing, and creativity. Built specifically for Richie (Richard Jacob Olejniczak), Spectra provides a deeply personal and empathetic AI companion experience.

Here's a PDF setup guide as well. 
https://drive.google.com/file/d/1dWWR8l-LcfpB5ljmEDokUWmQIpomlP3R/view?usp=drivesdk

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Ollama (for local AI models)

### Automatic Setup (Recommended)

**Windows:**

```bash
setup.bat
```

**Linux/Mac:**

```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Install Ollama:**

   - Download from: https://ollama.ai/download
   - Or: `winget install Ollama.Ollama` (Windows)

2. **Pull AI models:**

   ```bash
   ollama pull openhermes:7b-mistral-v2.5-q4_K_M
   ollama pull mistral:7b
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies:**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Configure environment:**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

### Running Spectra

**Option 1: Using batch files (Windows)**

- Start Ollama: `ollama serve`
- `start-backend.bat` - Starts the Python backend
- `start-frontend.bat` - Starts the React frontend

**Option 2: Manual**

```bash
# Terminal 1 - Ollama
ollama serve

# Terminal 2 - Backend
python app.py

# Terminal 3 - Frontend
cd frontend
npm run dev
```

**Then open:** `http://localhost:3000`

### Stopping Spectra

**Option 1: Quick Stop (Fastest)**

```bash
quick-stop.bat
```

**Option 2: Graceful Shutdown (Recommended)**

```bash
stop-all.bat
```

**Option 3: Smart Shutdown (Tries graceful first, then force)**

```bash
smart-stop.bat
```

**Manual Stop:**

- Press `Ctrl+C` in each terminal running the services
- Or use Task Manager to end Python, Node.js, and Ollama processes

## 🏗️ Project Structure

```
spectra-ai/
├── app.py                 # Flask backend API
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── frontend/             # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── App.tsx       # Main React app
│   │   ├── components/   # React components
│   │   └── api/          # API utilities
│   ├── package.json      # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS config
├── .vscode/              # VS Code workspace settings
├── start-backend.bat     # Backend startup script
├── start-frontend.bat    # Frontend startup script
├── start-ollama.bat      # Ollama startup script
├── stop-all.bat          # Graceful shutdown
├── quick-stop.bat        # Fast shutdown
├── smart-stop.bat        # Smart shutdown
└── test_integration.html # System testing interface
```

Spectra AI/
├── app.py # Main Flask application (Ollama integration)
├── requirements.txt # Python dependencies (latest versions)
├── .env # Environment variables (Ollama model config)
├── spectra_prompt.md # Spectra's personality definition
├── setup.bat/.sh # Automated setup scripts
├── start-backend.bat # Quick backend launcher
├── start-frontend.bat # Quick frontend launcher
├── frontend/ # React + TypeScript + Tailwind frontend
│ ├── src/
│ │ ├── App.tsx # Main React app
│ │ ├── components/ # React components
│ │ ├── api/ # API integration
│ │ └── types.ts # TypeScript types
│ ├── package.json # Frontend dependencies
│ └── vite.config.ts # Vite configuration
├── templates/ # Flask templates (fallback UI)
├── .vscode/ # VS Code settings (Pylance, formatting)
├── .github/ # GitHub configuration
│ └── copilot-instructions.md
└── README.md # This file

````

## 🤖 AI Configuration

### Ollama Models

- **Default**: `openhermes:7b-mistral-v2.5-q4_K_M` (optimized for emotional intelligence)
- **Alternative**: `mistral:7b` (faster responses)
- **Custom**: Set `OLLAMA_MODEL` in `.env`

### Model Management

```bash
ollama list                                    # See installed models
ollama pull openhermes:7b-mistral-v2.5-q4_K_M # Install Spectra's model
ollama pull mistral:7b                        # Install alternative model
ollama rm openhermes:7b-mistral-v2.5-q4_K_M  # Remove Spectra's model
ollama serve                                  # Start Ollama server
````

## 🎭 Spectra's Personality

Spectra's personality and traits are defined in `spectra_prompt.md`. This file contains her emotional intelligence, conversation style, and core characteristics that make her uniquely suited to help with creative expression and emotional support.

## 🔧 Configuration

### API Providers

- **Claude (Anthropic)**: Set `AI_PROVIDER=claude` in `.env`
- **OpenAI**: Set `AI_PROVIDER=openai` in `.env`

### Customization

- Modify `spectra_prompt.md` to adjust Spectra's personality
- Update frontend files in `static/` and `templates/` for UI changes
- Add new endpoints in `app.py` for additional features

## 🌈 Features (Planned)

- [x] Basic chat interface
- [x] Emotional intelligence and empathy
- [ ] Music generation integration
- [ ] Mood tracking
- [ ] Creative writing tools
- [ ] Healing and mindfulness features
- [ ] Voice interaction
- [ ] Memory and conversation history

## 🤝 Contributing

This is a personal project for Richie, but suggestions and improvements are welcome!

## 📝 License

Private project - All rights reserved.
