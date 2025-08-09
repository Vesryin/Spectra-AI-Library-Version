"""FastAPI backend for Spectra AI.

Key protocol (enforced in code):
 - No static training data usage.
 - No long-lived cached model knowledge; model list & personality can reload.
 - Personality prompt hot-reloads on file change.
 - All runtime state is ephemeral and recomputed when needed.
"""
import asyncio
import hashlib
import os
import time
from datetime import datetime, timezone  # updated to include timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import ollama
import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing import Any as _Any
    structlog: _Any

# Configure structured logging
LOG_FORMAT = os.getenv('SPECTRA_LOG_FORMAT', 'json')
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if LOG_FORMAT == 'json' 
        else structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Pydantic models
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8192)
    # max_items deprecated in Pydantic v2; use max_length instead
    history: Optional[List[ChatMessage]] = Field(default_factory=list, max_length=50)

class ChatResponse(BaseModel):
    response: str
    model: str
    model_used: str  # backward compatible duplicate of 'model'
    timestamp: str
    processing_time: float

    @classmethod
    def build(cls, *, response: str, model: str, processing_time: float) -> "ChatResponse":
        """Factory ensuring UTC timestamp and model_used duplication."""
        return cls(
            response=response,
            model=model,
            model_used=model,
            timestamp=datetime.now(timezone.utc).isoformat(),
            processing_time=processing_time,
        )

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
    model: str

class ModelSelectResponse(BaseModel):
    status: str
    selected: str
    previous: str
    available: List[str]
    message: str
    timestamp: str

class ToggleAutoModelRequest(BaseModel):
    enabled: Optional[bool] = None

class SpectraAI:
    def __init__(self) -> None:
        """Initialize with performance optimizations."""
        # Environment configuration
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
        self.model_cache_ttl = int(os.getenv('MODEL_CACHE_TTL', '300'))
        self.personality_check_interval = int(os.getenv('PERSONALITY_CHECK_INTERVAL', '5'))
        
        # Model management
        self.preferred_model = os.getenv('OLLAMA_MODEL', 'openhermes:7b-mistral-v2.5-q4_K_M')
        self._model_cache: Optional[List[str]] = None
        self._model_cache_time: Optional[float] = None
        self.available_models = self._get_available_models()
        self.model = self._select_best_model()
        
        # Personality management
        self._personality_path = Path(__file__).parent / 'spectra_prompt.md'
        self._personality_mtime: Optional[float] = None
        self._last_personality_check: Optional[float] = None
        self.personality_prompt = self._load_personality()
        self.personality_hash = self._hash_personality(self.personality_prompt)
        
        # Runtime state
        self.failed_models: set[str] = set()
        self.auto_model_enabled = os.getenv('SPECTRA_AUTO_MODEL', 'true').lower() in ('1', 'true', 'yes', 'on')
        self.request_count = 0
        self.total_processing_time = 0.0
        
        logger.info(
            "spectra_initialized",
            model=self.model,
            available_models=len(self.available_models),
            auto_model=self.auto_model_enabled,
            cache_ttl=self.model_cache_ttl
        )

    def _get_available_models(self) -> List[str]:
        """Get available models with caching."""
        current_time = time.time()
        
        # Return cached models if valid
        if (self._model_cache and self._model_cache_time and 
            current_time - self._model_cache_time < self.model_cache_ttl):
            return self._model_cache
        
        try:
            client = ollama.Client(host=self.ollama_host, timeout=self.ollama_timeout)
            response = client.list()
            
            models = []
            for model in response.get('models', []):
                if isinstance(model, dict):
                    name = model.get('name') or model.get('model')
                    if name:
                        models.append(name)
            
            # Update cache
            self._model_cache = models
            self._model_cache_time = current_time
            
            logger.debug("models_refreshed", count=len(models))
            return models
            
        except Exception as e:
            logger.warning("model_fetch_failed", error=str(e))
            return self._model_cache or []

    def _normalize(self, name: str) -> Optional[str]:
        """Normalize model name with fuzzy matching."""
        if not name or not self.available_models:
            return None
            
        name_lower = name.lower()
        
        # Exact match
        for model in self.available_models:
            if model.lower() == name_lower:
                return model
        
        # Partial match
        matches = [m for m in self.available_models if name_lower in m.lower()]
        return matches[0] if matches else None

    def _select_best_model(self) -> str:
        """Select best available model with fallback strategy."""
        if not self.available_models:
            logger.warning("no_models_available")
            return self.preferred_model
        
        # Try preferred model
        normalized = self._normalize(self.preferred_model)
        if normalized and normalized not in self.failed_models:
            return normalized
        
        # Fallback to first available non-failed model
        for model in self.available_models:
            if model not in self.failed_models:
                return model
        
        # Last resort
        return self.available_models[0]

    def refresh_models(self) -> None:
        """Force refresh of model cache."""
        self._model_cache = None
        self._model_cache_time = None
        self.available_models = self._get_available_models()
        
        if self.model not in self.available_models:
            self.model = self._select_best_model()

    def set_model(self, desired: str) -> str:
        """Set active model with validation."""
        resolved = self._normalize(desired)
        if resolved:
            self.model = resolved
            logger.info("model_changed", from_model=self.model, to_model=resolved)
        return self.model

    def _load_personality(self) -> str:
        """Load personality prompt from file."""
        try:
            if self._personality_path.exists():
                content = self._personality_path.read_text(encoding='utf-8')
                self._personality_mtime = self._personality_path.stat().st_mtime
                return content.strip()
        except Exception as e:
            logger.warning("personality_load_failed", error=str(e))
        
        return "You are Spectra AI, an emotionally intelligent assistant."

    def _maybe_reload_personality(self) -> None:
        """Reload personality with rate limiting."""
        current_time = time.time()
        
        # Rate limit checks
        if (self._last_personality_check and 
            current_time - self._last_personality_check < self.personality_check_interval):
            return
        
        self._last_personality_check = current_time
        
        try:
            if not self._personality_path.exists():
                return
                
            current_mtime = self._personality_path.stat().st_mtime
            if self._personality_mtime and current_mtime <= self._personality_mtime:
                return
                
            content = self._personality_path.read_text(encoding='utf-8')
            new_hash = self._hash_personality(content)
            
            if new_hash != self.personality_hash:
                self.personality_prompt = content.strip()
                self.personality_hash = new_hash
                self._personality_mtime = current_mtime
                logger.info("personality_reloaded", hash=self.personality_hash)
                
        except Exception as e:
            logger.warning("personality_reload_failed", error=str(e))

    def _hash_personality(self, text: str) -> str:
        """Generate hash for personality content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

    def _classify_intent(self, message: str) -> str:
        """Classify user intent for model selection."""
        message_lower = message.lower()
        
        creative_keywords = {'write', 'create', 'story', 'poem', 'creative', 'imagine', 'art'}
        technical_keywords = {'code', 'program', 'debug', 'fix', 'technical', 'algorithm'}
        
        if any(keyword in message_lower for keyword in creative_keywords):
            return 'creative'
        elif any(keyword in message_lower for keyword in technical_keywords):
            return 'technical'
        
        return 'concise'

    def _choose_context_model(self, message: str) -> str:
        """Choose optimal model based on context."""
        if not self.auto_model_enabled:
            return self.model
        
        intent = self._classify_intent(message)
        
        # Model preferences by intent
        preferences = {
            'creative': ['openhermes', 'mistral', 'llama'],
            'technical': ['mistral', 'openhermes', 'llama'],
            'concise': ['mistral', 'openhermes']
        }
        
        for preferred in preferences.get(intent, ['mistral']):
            for model in self.available_models:
                if preferred in model.lower() and model not in self.failed_models:
                    return model
        
        return self.model

    async def generate_response(self, message: str, history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """Generate AI response with performance tracking."""
        start_time = time.time()
        
        try:
            self._maybe_reload_personality()
            selected_model = self._choose_context_model(message)
            
            # Build conversation context
            messages = [{"role": "system", "content": self.personality_prompt}]
            
            if history:
                for msg in history[-10:]:  # Limit context window
                    messages.append({"role": msg.role, "content": msg.content})
            
            messages.append({"role": "user", "content": message})
            
            # Generate response
            client = ollama.Client(host=self.ollama_host, timeout=self.ollama_timeout)
            response = await asyncio.to_thread(
                client.chat,
                model=selected_model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048,
                    "stop": ["Human:", "User:"]
                }
            )
            
            processing_time = time.time() - start_time
            
            # Update metrics
            self.request_count += 1
            self.total_processing_time += processing_time
            
            # Remove from failed models if successful
            self.failed_models.discard(selected_model)
            
            logger.info(
                "response_generated",
                model=selected_model,
                processing_time=processing_time,
                message_length=len(message),
                response_length=len(response['message']['content'])
            )
            
            return {
                "response": response['message']['content'],
                "model": selected_model,
                "model_used": selected_model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Mark model as failed for resource/memory errors
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ('resource', 'memory', 'timeout', 'overload')):
                self.failed_models.add(selected_model)
                logger.warning("model_marked_failed", model=selected_model, error=str(e))
            
            logger.error(
                "response_generation_failed",
                model=selected_model,
                error=str(e),
                processing_time=processing_time
            )
            
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Failed to generate response",
                    "error": str(e),
                    "model": selected_model,
                    "processing_time": processing_time
                }
            )

    def metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return {
            "active_model": self.model,
            "preferred_model": self.preferred_model,
            "available_models": self.available_models,
            "failed_models": sorted(self.failed_models),
            "auto_model_enabled": self.auto_model_enabled,
            "personality_hash": self.personality_hash,
            "request_count": self.request_count,
            "avg_processing_time": round(avg_processing_time, 3),
            "cache_ttl": self.model_cache_ttl,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def toggle_auto_model(self, enabled: Optional[bool] = None) -> bool:
        """Toggle auto model selection."""
        if enabled is not None:
            self.auto_model_enabled = enabled
        else:
            self.auto_model_enabled = not self.auto_model_enabled
        return self.auto_model_enabled

spectra = SpectraAI()

app = FastAPI(
    title="Spectra AI API",
    description="Emotionally intelligent AI assistant backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

allowed_origins = [o.strip() for o in os.getenv('ALLOWED_ORIGINS','http://localhost:3000').split(',') if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get('/', response_model=Dict[str, Any])
async def root():
    """API info endpoint"""
    return {
        "service": "Spectra AI Backend API",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frontend_url": f"http://localhost:3000",
        "model": spectra.model,
        "available_models": spectra.available_models,
        "docs": "/docs",
        "health": "/health"
    }

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "personality_hash": spectra.personality_hash}

@app.get('/api/status', response_model=StatusResponse)
async def get_status():
    """Get system status"""
    try:
        current_models = spectra._get_available_models()
        ollama_status = "connected" if current_models else "disconnected"
        
        return StatusResponse(
            status="healthy",
            ai_provider="ollama",
            ollama_status=ollama_status,
            model=spectra.model,
            available_models=current_models,
            timestamp=datetime.now(timezone.utc).isoformat(),
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', 8000))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/models', response_model=ModelListResponse)
async def list_models():
    spectra.refresh_models()
    return ModelListResponse(
        current=spectra.model,
        available=spectra.available_models,
        preferred=spectra.preferred_model,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post('/api/models/select', response_model=ModelSelectResponse)
async def select_model(payload: ModelSelectRequest):
    prev = spectra.model
    selected = spectra.set_model(payload.model)
    msg = 'model updated' if selected != prev else 'model unchanged'
    return ModelSelectResponse(
        status='ok',
        selected=selected,
        previous=prev,
        available=spectra.available_models,
        message=msg,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post('/api/models/refresh', response_model=ModelListResponse)
async def refresh_models_endpoint():
    """Force a refresh of the model list (dynamic, no static caching)."""
    spectra.refresh_models()
    return ModelListResponse(
        current=spectra.model,
        available=spectra.available_models,
        preferred=spectra.preferred_model,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post('/api/chat', response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Chat with Spectra AI"""
    try:
        logger.info("chat_request", preview=chat_request.message[:50], history=len(chat_request.history))
        result = await spectra.generate_response(chat_request.message, chat_request.history)
        return ChatResponse.build(
            response=result["response"],
            model=result["model"],
            processing_time=result["processing_time"],
        )
    except Exception as e:  # noqa: BLE001
        logger.error("chat_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "response": "I'm having trouble processing your message right now. Please try again. 💜",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@app.get('/api/metrics', response_model=Dict[str, Any])
async def metrics_endpoint():
    return spectra.metrics()

@app.post('/api/auto-model', response_model=Dict[str, Any])
async def toggle_auto_model(req: ToggleAutoModelRequest):
    new_value = spectra.toggle_auto_model(req.enabled)
    return {"auto_model_enabled": new_value, "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get('/api/personality/hash', response_model=Dict[str,str])
async def personality_hash():
    return {"personality_hash": spectra.personality_hash}

@app.post('/api/personality/reload', response_model=Dict[str,str])
async def personality_reload():
    """Force reload of personality file (if changed)."""
    before = spectra.personality_hash
    spectra._maybe_reload_personality()  # noqa: SLF001 (intentional internal call)
    changed = before != spectra.personality_hash
    return {"personality_hash": spectra.personality_hash, "changed": str(changed).lower()}

@app.get('/api/debug/state', response_model=Dict[str, Any])
async def debug_state():
    """Debug snapshot (no static caches – all values are current)."""
    spectra.refresh_models()
    spectra._maybe_reload_personality()  # noqa: SLF001
    base = spectra.metrics()
    base.update({
        "auto_model_enabled": spectra.auto_model_enabled,
        "failed_models_count": len(spectra.failed_models),
        "preferred_model": spectra.preferred_model,
    })
    return base

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
    content={"error": "Endpoint not found", "timestamp": datetime.now(timezone.utc).isoformat()}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
    content={"error": "Internal server error", "timestamp": datetime.now(timezone.utc).isoformat()}
    )

if __name__ == '__main__':
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    logger.info("startup", host=HOST, port=PORT, model=spectra.model, available_models=spectra.available_models, log_format=os.getenv('SPECTRA_LOG_FORMAT', 'json'))
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv('ENVIRONMENT') == 'development',
        log_level="info"
    )
