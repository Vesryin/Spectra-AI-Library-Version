"""
Spectra AI - Modern FastAPI Backend
Production-ready with async support, type hints, and comprehensive error handling
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import ollama

# Load environment variables
load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app with metadata
app = FastAPI(
    title="Spectra AI API",
    description="Emotionally intelligent AI assistant backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    history: List[ChatMessage] = Field(default=[], description="Conversation history")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    model_used: str = Field(..., description="Model that generated the response")
    status: str = Field(..., description="Response status")
    timestamp: str = Field(..., description="Response timestamp")

class StatusResponse(BaseModel):
    status: str
    ai_provider: str
    ollama_status: str
    model: str
    available_models: List[str]
    timestamp: str
    host: str
    port: int

class ModelListResponse(BaseModel):
    current: str
    available: List[str]
    preferred: str
    timestamp: str

class ModelSelectRequest(BaseModel):
    model: str = Field(..., description="Exact model name or shorthand (e.g., 'phi')")

class ModelSelectResponse(BaseModel):
    status: str
    selected: str
    previous: str
    available: List[str]
    message: str
    timestamp: str

class SpectraAI:
    """Modern SpectraAI class with comprehensive error handling and type hints"""
    
    def __init__(self):
        """Initialize model preferences and personality."""
        # Allow shorthand like 'phi' to match 'phi:latest'
        self.preferred_model: str = os.getenv('OLLAMA_MODEL', 'openhermes:7b-mistral-v2.5-q4_K_M')
        self.available_models: List[str] = self._get_available_models()
        self.model: str = self._select_best_model()
        self.personality_prompt: str = self._load_personality()

        logger.info(f"🌟 Spectra AI initialized with model: {self.model}")
        # Track models that failed due to resource limits to avoid repeat attempts
        self.failed_models: set[str] = set()
        self.auto_model_enabled: bool = os.getenv('SPECTRA_AUTO_MODEL', 'true').lower() in ('1','true','yes','on')

    # -------------------- Dynamic / Contextual Model Logic --------------------
    def _normalize_model_name(self, name: str) -> Optional[str]:
        """Return the exact available model name matching a shorthand or exact name, else None."""
        if not self.available_models:
            return None
        if name in self.available_models:
            return name
        # Shorthand resolution
        matches = [m for m in self.available_models if m.startswith(name + ':') or m.startswith(name)]
        return sorted(matches)[0] if matches else None

    def _ranked_models(self, preference: str) -> List[str]:
        """Return ordered list of candidate models based on preference ('creative'|'concise').
        Filters out models previously marked as failed for memory/resource reasons.
        Order from most capable to least for creative, reversed for concise.
        """
        # Capability order (approximate: larger / more tuned earlier)
        capability_order = [
            'openhermes:7b-mistral-v2.5-q4_K_M',
            'mistral:7b',
            'phi:latest',
            'qwen2:0.5b'
        ]
        # Keep only those actually available (normalized)
        normalized_available = {m: self._normalize_model_name(m) for m in capability_order}
        # Replace with actual names if available
        ordered = [normalized_available[m] for m in capability_order if normalized_available[m]]
        # Remove failed models
        ordered = [m for m in ordered if m not in self.failed_models]
        if preference == 'concise':
            # For concise / quick tasks prefer smallest first
            ordered = list(reversed(ordered))
        return ordered or [self.model]

    def _classify_intent(self, message: str) -> str:
        """Classify message into a simple intent guiding model size."""
        text = message.lower()
        creative_keywords = [
            'story','poem','lyrics','song','script','analyze','analysis','explain','refactor','improve','creative','narrative','write','compose'
        ]
        if any(k in text for k in creative_keywords) or len(message) > 240:
            return 'creative'
        return 'concise'

    def _choose_context_model(self, message: str) -> str:
        """Determine best model for this message (does NOT permanently change self.model)."""
        if not self.auto_model_enabled:
            return self.model
        preference = self._classify_intent(message)
        candidates = self._ranked_models('creative' if preference=='creative' else 'concise')
        # Return first candidate; fallback handled in retry logic
        chosen = candidates[0]
        if chosen != self.model:
            logger.info(f"🧠 Contextual selection ({preference}) -> {chosen}")
        return chosen
        
    def _get_available_models(self) -> List[str]:
        """Dynamically get available Ollama models with robust error handling"""
        try:
            response = ollama.list()
            models = []
            
            if 'models' in response:
                for model in response['models']:
                    if hasattr(model, 'model'):
                        models.append(model.model)
                    elif isinstance(model, dict) and 'name' in model:
                        models.append(model['name'])
                    elif isinstance(model, dict) and 'model' in model:
                        models.append(model['model'])
            
            logger.info(f"📋 Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"❌ Failed to get models: {e}")
            return []
    
    def _select_best_model(self) -> str:
        """Auto-select best available model with smart fallback and shorthand matching"""
        if not self.available_models:
            logger.error("⚠️ No Ollama models available!")
            return self.preferred_model

        # Exact match first
        if self.preferred_model in self.available_models:
            return self.preferred_model

        # Try shorthand (e.g., 'phi' -> 'phi:latest')
        shorthand_matches = [m for m in self.available_models if m.startswith(self.preferred_model + ':')]
        if shorthand_matches:
            chosen = sorted(shorthand_matches)[0]
            logger.info(f"✨ Resolved shorthand '{self.preferred_model}' to '{chosen}'")
            return chosen

        # Memory-aware ordering: prefer smallest parameter size when low memory
        ordered_candidates = [
            'phi:latest',
            'phi2:latest',
            'qwen2:0.5b',
            'llama3.2:1b',
            'mistral:7b',
            'openhermes:7b-mistral-v2.5-q4_K_M',
            'openhermes2.5-mistral',
            'openhermes:latest',
            'mistral:latest',
            'llama2:latest'
        ]
        for cand in ordered_candidates:
            if cand in self.available_models:
                logger.warning(f"🔄 Using fallback model: {cand}")
                return cand

        # Last resort - first available
        selected = self.available_models[0]
        logger.warning(f"🆘 Using first available model: {selected}")
        return selected

    def refresh_models(self) -> None:
        """Refresh available models list (e.g., after pulling/removing)."""
        self.available_models = self._get_available_models()

    def set_model(self, desired: str) -> str:
        """Attempt to set active model; supports shorthand.

        Returns the model actually set (may be resolved or fallback).
        """
        self.refresh_models()
        previous = self.model

        # Exact
        if desired in self.available_models:
            self.model = desired
        else:
            # Shorthand
            shorthand = [m for m in self.available_models if m.startswith(desired + ':')]
            if shorthand:
                self.model = sorted(shorthand)[0]
                logger.info(f"✨ Shorthand '{desired}' resolved to '{self.model}'")
            else:
                logger.warning(f"⚠️ Requested model '{desired}' not found; keeping '{self.model}'")
        if previous != self.model:
            logger.info(f"🔁 Model changed: {previous} → {self.model}")
        return self.model
    
    def _load_personality(self) -> str:
        """Load Spectra's personality from file with fallback"""
        try:
            personality_file = Path(__file__).parent / 'spectra_prompt.md'
            with open(personality_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info("✅ Personality prompt loaded from file")
                return content
        except FileNotFoundError:
            logger.warning("⚠️ Personality file not found, using default")
            return self._get_default_personality()
        except Exception as e:
            logger.error(f"❌ Error loading personality: {e}")
            return self._get_default_personality()
    
    def _get_default_personality(self) -> str:
        """Fallback personality if file not found"""
        return """You are Spectra, an emotionally intelligent AI assistant designed for Richie. 
        You are deeply empathetic, creative, and focused on music, healing, and emotional support. 
        Respond with warmth, understanding, and genuine care. Use emojis naturally and maintain a supportive, 
        human-like conversational style."""
    
    async def generate_response(self, message: str, history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """Generate dynamic response using available model with async support"""
        try:
            logger.info(f"🔄 Starting response generation for: {message[:50]}...")
            
            # Refresh model availability for each request
            current_models = self._get_available_models()
            if self.model not in current_models and current_models:
                old_model = self.model
                self.available_models = current_models
                self.model = self._select_best_model()
                logger.info(f"🔄 Model changed: {old_model} → {self.model}")
            
            # Build conversation context with simplified personality prompt
            personality_summary = """You are Spectra, an emotionally intelligent AI assistant for Richie. 
            You are empathetic, creative, supportive, and focus on music, healing, and emotional connection. 
            Respond with warmth and genuine care. Use emojis naturally."""
            
            conversation = [{"role": "system", "content": personality_summary}]
            
            if history:
                for msg in history[-5:]:  # Keep last 5 messages to prevent token overflow
                    if msg.content.strip():
                        conversation.append({
                            "role": msg.role,
                            "content": msg.content
                        })
            
            conversation.append({"role": "user", "content": message})
            
            logger.info(f"💭 Conversation context: {len(conversation)} messages")
            
            # Decide request-scoped model (contextual) but allow fallback retries
            request_model = self._choose_context_model(message)
            attempt_models = [request_model]
            # If contextual pick differs from persistent model, allow persistent model as a fallback (unless same)
            if self.model not in attempt_models:
                attempt_models.append(self.model)
            # Add decreasing capability order as last resort
            for m in self._ranked_models('concise'):
                if m not in attempt_models:
                    attempt_models.append(m)

            last_error = None
            response = None
            for idx, model_name in enumerate(attempt_models):
                try:
                    logger.info(f"🤖 Attempt {idx+1}/{len(attempt_models)} with model: {model_name}")
                    response = ollama.chat(
                        model=model_name,
                        messages=conversation,
                        stream=False,
                        options={
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 512
                        }
                    )
                    # Persist chosen model if successful and different
                    if model_name != self.model:
                        logger.info(f"✅ Updating active model to {model_name} after success")
                        self.model = model_name
                    break
                except Exception as inner_e:
                    err_text = str(inner_e)
                    last_error = inner_e
                    logger.warning(f"⚠️ Model {model_name} failed: {err_text}")
                    # Mark memory related failures so we deprioritize model for future
                    if 'memory' in err_text.lower() or 'terminated' in err_text.lower():
                        self.failed_models.add(model_name)
                        logger.warning(f"📉 Marking model '{model_name}' as resource-failed")
                    continue

            if response is None:
                raise last_error if last_error else RuntimeError("No model produced a response")
            
            logger.info("✅ Response generated successfully")
            
            return {
                "response": response['message']['content'],
                "model_used": response.get('model', self.model),
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

# API Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    """API info endpoint"""
    return {
        "service": "Spectra AI Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "frontend_url": "http://localhost:3000",
        "model": spectra.model,
        "available_models": spectra.available_models,
        "endpoints": {
            "/api/status": "GET - API status",
            "/api/chat": "POST - Chat with Spectra AI",
            "/api/health": "GET - Health check"
        }
    }

@app.get("/api/health", response_model=Dict[str, str])
async def health():
    """Quick health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Spectra AI"
    }

@app.get("/api/status", response_model=StatusResponse)
async def status():
    """Dynamic status endpoint with real-time model check"""
    try:
        current_models = spectra._get_available_models()
        ollama_status = "connected" if current_models else "disconnected"
        
        return StatusResponse(
            status="healthy",
            ai_provider="ollama",
            ollama_status=ollama_status,
            model=spectra.model,
            available_models=current_models,
            timestamp=datetime.now().isoformat(),
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', 5000))
        )
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Modern async chat endpoint with comprehensive validation"""
    try:
        logger.info(f"💬 Chat request: {request.message[:50]}...")
        
        # Generate response
        result = await spectra.generate_response(request.message, request.history)
        
        logger.info("✅ Response sent successfully")
        return ChatResponse(**result)
        
    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request format: {str(e)}"
        )

@app.get("/api/models", response_model=ModelListResponse)
async def list_models():
    """List current and available models."""
    spectra.refresh_models()
    return ModelListResponse(
        current=spectra.model,
        available=spectra.available_models,
        preferred=spectra.preferred_model,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/models/select", response_model=ModelSelectResponse)
async def select_model(payload: ModelSelectRequest):
    """Select a different model dynamically without restart."""
    previous = spectra.model
    selected = spectra.set_model(payload.model)
    msg = "Model updated" if selected != previous else "Model unchanged"
    return ModelSelectResponse(
        status="success",
        selected=selected,
        previous=previous,
        available=spectra.available_models,
        message=msg,
        timestamp=datetime.now().isoformat()
    )

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == '__main__':
    import uvicorn
    
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 Starting Spectra AI FastAPI on {HOST}:{PORT}")
    logger.info(f"🤖 AI Model: {spectra.model}")
    logger.info(f"📋 Available Models: {spectra.available_models}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv('FASTAPI_RELOAD', 'True').lower() == 'true',
        log_level="info"
    )
