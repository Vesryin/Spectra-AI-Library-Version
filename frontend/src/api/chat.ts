import axios from 'axios';
import { Message, ChatResponse } from '../types';

// Dynamic API configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // Increased timeout for AI responses
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - AI is taking too long to respond');
    }
    if (error.response?.status === 500) {
      throw new Error('Server error - Please check backend logs');
    }
    if (error.response?.status === 404) {
      throw new Error('API endpoint not found - Please restart backend');
    }
    throw error;
  }
);

export const sendMessage = async (message: string, history: Message[]): Promise<ChatResponse> => {
  const response = await api.post('/chat', {
    message,
    history: history.slice(-10).map(msg => ({ // Keep last 10 messages
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.content,
    })),
  });
  
  return response.data;
};

export const checkStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};
