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

class SpectraAI:
    """Modern SpectraAI class with comprehensive error handling and type hints"""
    
    def __init__(self):
        self.preferred_model = os.getenv('OLLAMA_MODEL', 'openhermes:7b-mistral-v2.5-q4_K_M')
        self.available_models = self._get_available_models()
        self.model = self._select_best_model()
        self.personality_prompt = self._load_personality()
        
        logger.info(f"🌟 Spectra AI initialized with model: {self.model}")
        
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
        """Auto-select best available model with smart fallback"""
        if not self.available_models:
            logger.error("⚠️ No Ollama models available!")
            return self.preferred_model
            
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
    
    async def generate_response(self, message: str, history: List[ChatMessage] = None) -> Dict[str, Any]:
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
            
            # Generate response with optimized parameters
            logger.info("🤖 Calling Ollama...")
            response = ollama.chat(
                model=self.model,
                messages=conversation,
                stream=False,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512  # Limit response length
                }
            )
            
            logger.info("✅ Response generated successfully")
            
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
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I'm having trouble processing your message right now. Please try again. 💜"
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
