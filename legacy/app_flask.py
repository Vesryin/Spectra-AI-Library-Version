"""Legacy Flask backend for Spectra AI (deprecated).

Retained only for backward compatibility during migration to FastAPI.
Prefer running `python main.py`.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import signal
import atexit
from datetime import datetime
import ollama
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
	log_dir = "logs"
	os.makedirs(log_dir, exist_ok=True)
	fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler = RotatingFileHandler(os.path.join(log_dir, 'spectra_ai.log'), maxBytes=5*1024*1024, backupCount=3)
	file_handler.setFormatter(fmt)
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(fmt)
	logger = logging.getLogger('legacy_flask')
	logger.setLevel(logging.INFO)
	if not logger.handlers:
		logger.addHandler(file_handler)
		logger.addHandler(console_handler)
	return logger

logger = setup_logging()

app = Flask(__name__)
CORS(app)

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))

class SpectraAI:
	def __init__(self):
		self.preferred_model = os.getenv('OLLAMA_MODEL', 'openhermes:7b-mistral-v2.5-q4_K_M')
		self.available_models = self._get_available_models()
		self.model = self._select_best_model()

	def _get_available_models(self):
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
			return models
		except Exception:
			return []

	def _select_best_model(self):
		if not self.available_models:
			return self.preferred_model
		if self.preferred_model in self.available_models:
			return self.preferred_model
		matches = [m for m in self.available_models if m.startswith(self.preferred_model+':')]
		if matches:
			return sorted(matches)[0]
		for cand in ['phi:latest','qwen2:0.5b','mistral:7b','openhermes:7b-mistral-v2.5-q4_K_M']:
			if cand in self.available_models:
				return cand
		return self.available_models[0]

	def generate_response(self, message, history=None):
		try:
			convo = [{"role":"system","content":"You are Spectra (legacy Flask)."}]
			if history:
				for msg in history[-5:]:
					if msg.get('content'):
						convo.append({"role": msg.get('role','user'), "content": msg['content']})
			convo.append({"role":"user","content":message})
			result = ollama.chat(model=self.model, messages=convo, stream=False)
			return {"response": result['message']['content'], "model_used": self.model, "status": "success", "timestamp": datetime.now().isoformat()}
		except Exception as e:
			return {"response": f"Error: {e}", "model_used": self.model, "status": "error", "timestamp": datetime.now().isoformat()}

spectra = SpectraAI()

@app.route('/api/health')
def health():
	return jsonify({"status":"healthy","timestamp":datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
	data = request.get_json() or {}
	msg = data.get('message')
	if not msg:
		return jsonify({"error":"message required"}), 400
	history = data.get('history', [])
	return jsonify(spectra.generate_response(msg, history))

def _shutdown(*_):
	logger.info('Legacy Flask shutting down')
	sys.exit(0)

signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)
atexit.register(lambda: logger.info('Legacy Flask exited'))

if __name__ == '__main__':  # pragma: no cover
	print('[DEPRECATED] Starting legacy Flask app; prefer FastAPI main.py')
	app.run(host=HOST, port=PORT)

