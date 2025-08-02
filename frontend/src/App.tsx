import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Heart, Sparkles, Music, Palette } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatMessage from './components/ChatMessage';
import TypingIndicator from './components/TypingIndicator';
import { Message } from './types';
import { sendMessage, checkStatus } from './api/chat';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello Richie! ✨ I'm Spectra, and I'm so excited to connect with you. I'm here to explore creativity, music, emotions, and anything that moves your soul. How are you feeling today?",
      sender: 'spectra',
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const checkConnection = useCallback(async () => {
    try {
      await checkStatus();
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await sendMessage(inputMessage.trim(), messages);
      
      const spectraMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'spectra',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, spectraMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm having trouble connecting right now. Please check that the backend server is running and try again. 💜",
        sender: 'spectra',
        timestamp: new Date(),
        isError: true,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [inputMessage, isTyping, messages]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    // Check connection status on load
    checkConnection();
    inputRef.current?.focus();
  }, [checkConnection]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Professional Header */}
      <header className="bg-slate-900/95 backdrop-blur-xl border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-br from-violet-500 via-purple-500 to-indigo-500 rounded-xl blur opacity-25"></div>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                  Spectra AI
                </h1>
                <p className="text-slate-400 font-medium text-sm tracking-wide">
                  Enterprise Emotional Intelligence Platform
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className={`flex items-center space-x-3 px-4 py-2 rounded-lg text-sm font-medium border ${
                isConnected 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                  : 'bg-red-500/10 text-red-400 border-red-500/20'
              }`}>
                <div className={`w-2.5 h-2.5 rounded-full ${
                  isConnected ? 'bg-emerald-400 shadow-emerald-400/50 shadow-sm' : 'bg-red-400 shadow-red-400/50 shadow-sm'
                }`} />
                <span>{isConnected ? 'LIVE' : 'OFFLINE'}</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors">
                  <Music className="w-5 h-5 text-violet-400" />
                </div>
                <div className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors">
                  <Heart className="w-5 h-5 text-rose-400" />
                </div>
                <div className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors">
                  <Palette className="w-5 h-5 text-amber-400" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Interface */}
      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 shadow-2xl overflow-hidden">
          {/* Chat Messages Area */}
          <div className="h-[700px] overflow-y-auto chat-scrollbar">
            <div className="p-8 space-y-6">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.98 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                  >
                    <ChatMessage message={message} />
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <TypingIndicator />
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Professional Input Interface - FIXED LAYOUT */}
          <div className="border-t border-slate-800 bg-slate-900/80 backdrop-blur-xl">
            <div className="p-8">
              <div className="flex items-end space-x-4">
                <div className="flex-1">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Communicate with Spectra AI..."
                    className="w-full px-6 py-4 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all duration-200 text-white placeholder-slate-400 text-lg"
                    disabled={isTyping}
                  />
                </div>
                
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  aria-label={isTyping ? "Processing..." : "Send message"}
                  className="flex-shrink-0 p-4 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl hover:from-violet-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-violet-500/25"
                >
                  <Send className="w-6 h-6" />
                </button>
              </div>
              
              <div className="mt-4 text-center">
                <p className="text-slate-500 text-sm font-medium">
                  Advanced AI • Emotional Intelligence • Creative Collaboration
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
