import axios from 'axios';
import { Message, ChatResponse } from '../types';

// Dynamic API configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // Increased timeout to 2 minutes for AI responses
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
      throw new Error('Spectra is thinking deeply about your message... Please wait a moment and try again 💜');
    }
    if (error.response?.status === 500) {
      throw new Error('Spectra is having a moment of technical difficulty. Please try again 💜');
    }
    if (error.response?.status === 404) {
      throw new Error('Lost connection to Spectra. Please refresh the page 💜');
    }
    if (error.code === 'ECONNRESET' || error.message.includes('ECONNRESET')) {
      throw new Error('Connection was reset while Spectra was responding. Please try again 💜');
    }
    throw new Error('Having trouble connecting to Spectra right now. Please try again 💜');
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
