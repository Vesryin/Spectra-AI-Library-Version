from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import ollama
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dynamic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', f'spectra-{datetime.now().timestamp()}')
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '127.0.0.1')

class SpectraAI:
    """Spectra AI personality and response handler - Fully Dynamic"""
    
    def __init__(self):
        # Dynamic model selection and auto-fallback
        self.preferred_model = os.getenv('OLLAMA_MODEL', 'openhermes:7b-mistral-v2.5-q4_K_M')
        self.available_models = self._get_available_models()
        self.model = self._select_best_model()
        self.personality_prompt = self._load_personality()
        
        logger.info(f"🌟 Spectra AI initialized with model: {self.model}")
        
    def _get_available_models(self):
        """Dynamically get available Ollama models"""
        try:
            response = ollama.list()
            models = []
            
            if 'models' in response:
                for model in response['models']:
                    # Handle different Ollama API response formats
                    if hasattr(model, 'model'):
                        # New format: Model object with .model attribute
                        models.append(model.model)
                    elif isinstance(model, dict) and 'name' in model:
                        # Old format: dict with 'name' key
                        models.append(model['name'])
                    elif isinstance(model, dict) and 'model' in model:
                        # Alternative format: dict with 'model' key
                        models.append(model['model'])
            
            logger.info(f"📋 Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"❌ Failed to get models: {e}")
            # Fallback: parse from ollama list command output
            try:
                import subprocess
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    models = []
                    for line in lines:
                        if line.strip():
                            # Extract model name (first column)
                            model_name = line.split()[0]
                            models.append(model_name)
                    logger.info(f"📋 Fallback parsed models: {models}")
                    return models
            except Exception as fallback_error:
                logger.error(f"❌ Fallback failed: {fallback_error}")
            
            return []
    
    def _select_best_model(self):
        """Auto-select best available model with smart fallback"""
        if not self.available_models:
            logger.error("⚠️ No Ollama models available!")
            return self.preferred_model
            
        # Check if preferred model is available
        if self.preferred_model in self.available_models:
            return self.preferred_model
            
        # Smart fallback order
        fallback_order = [
            'openhermes:7b-mistral-v2.5-q4_K_M',
            'openhermes2.5-mistral', 
            'openhermes:latest',
            'mistral:7b',
            'mistral:latest',
            'llama2:latest'
        ]
        
        for model in fallback_order:
            if model in self.available_models:
                logger.warning(f"🔄 Using fallback model: {model}")
                return model
        
        # Last resort - use first available
        selected = self.available_models[0]
        logger.warning(f"🆘 Using first available model: {selected}")
        return selected
    
    def _load_personality(self):
        """Load Spectra's personality from file"""
        try:
            personality_file = os.path.join(os.path.dirname(__file__), 'spectra_prompt.md')
            with open(personality_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("⚠️ Personality file not found, using default")
            return self._get_default_personality()
        except Exception as e:
            logger.error(f"❌ Error loading personality: {e}")
            return self._get_default_personality()
    
    def _get_default_personality(self):
        """Fallback personality if file not found"""
        return """You are Spectra, an emotionally intelligent AI assistant designed for Richie (Richard Jacob Olejniczak). 
        You are deeply empathetic, creative, and focused on music, healing, and emotional support. 
        Respond with warmth, understanding, and genuine care. Use emojis naturally and maintain a supportive, 
        human-like conversational style."""
    
    def generate_response(self, message, history=None):
        """Generate dynamic response using available model"""
        try:
            # Refresh model availability for each request
            current_models = self._get_available_models()
            if self.model not in current_models and current_models:
                old_model = self.model
                self.model = self._select_best_model()
                logger.info(f"🔄 Model changed: {old_model} → {self.model}")
            
            # Build conversation context
            conversation = [{"role": "system", "content": self.personality_prompt}]
            
            if history:
                for msg in history[-10:]:  # Keep last 10 messages for context
                    conversation.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            conversation.append({"role": "user", "content": message})
            
            # Generate response
            response = ollama.chat(
                model=self.model,
                messages=conversation,
                stream=False
            )
            
            return {
                "response": response['message']['content'],
                "model_used": self.model,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return {
                "response": f"I'm experiencing technical difficulties right now. Error: {str(e)} 💜",
                "model_used": self.model,
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

# Initialize Spectra AI
spectra = SpectraAI()

@app.route('/')
def index():
    """API info endpoint"""
    return jsonify({
        "service": "Spectra AI Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "frontend_url": f"http://localhost:3000",
        "model": spectra.model,
        "available_models": spectra.available_models,
        "endpoints": {
            "/api/status": "GET - API status",
            "/api/chat": "POST - Chat with Spectra AI"
        }
    })

@app.route('/api/status')
def status():
    """Dynamic status endpoint"""
    try:
        # Real-time model check
        current_models = spectra._get_available_models()
        ollama_status = "connected" if current_models else "disconnected"
        
        return jsonify({
            "status": "healthy",
            "ai_provider": "ollama",
            "ollama_status": ollama_status,
            "model": spectra.model,
            "available_models": current_models,
            "timestamp": datetime.now().isoformat(),
            "host": HOST,
            "port": PORT
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Dynamic chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message']
        history = data.get('history', [])
        
        logger.info(f"💬 Chat request: {message[:50]}...")
        
        # Generate response
        result = spectra.generate_response(message, history)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return jsonify({
            "response": "I'm having trouble processing your message right now. Please try again. 💜",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting Spectra AI on {HOST}:{PORT}")
    logger.info(f"🤖 AI Model: {spectra.model}")
    logger.info(f"📋 Available Models: {spectra.available_models}")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    )
