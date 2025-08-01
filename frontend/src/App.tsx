import React, { useState, useEffect, useRef } from 'react';
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check connection status on load
    checkConnection();
    inputRef.current?.focus();
  }, []);

  const checkConnection = async () => {
    try {
      await checkStatus();
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const handleSendMessage = async () => {
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
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-purple-100 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold gradient-text">
                Spectra AI
              </h1>
              <p className="text-sm text-gray-600">
                Your emotionally intelligent companion
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isConnected 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span>{isConnected ? 'Connected' : 'Offline'}</span>
            </div>
            
            <div className="flex items-center space-x-2 text-purple-600">
              <Music className="w-5 h-5" />
              <Heart className="w-5 h-5" />
              <Palette className="w-5 h-5" />
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-purple-100 overflow-hidden">
          {/* Messages */}
          <div className="h-[600px] overflow-y-auto chat-scrollbar p-6 space-y-4">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.95 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
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
              >
                <TypingIndicator />
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-purple-100 p-6 bg-gradient-to-r from-purple-50/50 to-indigo-50/50">
            <div className="flex items-end space-x-4">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share your thoughts with Spectra... 💜"
                  className="w-full px-4 py-3 pr-12 bg-white border border-purple-200 rounded-xl focus:outline-none input-focus resize-none"
                  disabled={isTyping}
                />
                
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg hover:from-purple-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 spectra-glow"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="mt-2 text-xs text-gray-500 text-center">
              Spectra is designed to help with creativity, music, and emotional support 🎵
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
