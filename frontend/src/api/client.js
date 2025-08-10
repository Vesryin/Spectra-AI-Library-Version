// src/api/client.js

// Use the environment variable injected at build time
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function chatWithSpectra(message, history = []) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}