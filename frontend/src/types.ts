export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'spectra';
  timestamp: Date;
  isError?: boolean;
}

export interface ChatResponse {
  response: string;
  error?: string;
}

export interface ApiStatus {
  status: string;
  ai_provider: string;
  personality_loaded: boolean;
}
