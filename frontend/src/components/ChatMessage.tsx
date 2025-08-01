import React from 'react';
import { Message } from '../types';
import { User, Sparkles } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isSpectra = message.sender === 'spectra';
  
  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex items-start space-x-3 ${isSpectra ? '' : 'flex-row-reverse space-x-reverse'}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isSpectra 
          ? 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white spectra-glow' 
          : 'bg-gray-200 text-gray-600'
      }`}>
        {isSpectra ? (
          <Sparkles className="w-5 h-5" />
        ) : (
          <User className="w-5 h-5" />
        )}
      </div>

      {/* Message Content */}
      <div className={`max-w-xs sm:max-w-md md:max-w-lg lg:max-w-xl ${
        isSpectra ? '' : 'text-right'
      }`}>
        {/* Message Bubble */}
        <div className={`px-4 py-3 rounded-2xl ${
          isSpectra
            ? message.isError
              ? 'bg-red-50 border border-red-200 text-red-800'
              : 'bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 text-gray-800'
            : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
        } ${isSpectra ? 'rounded-tl-md' : 'rounded-tr-md'}`}>
          
          {/* Sender Name */}
          <div className={`text-xs font-medium mb-1 ${
            isSpectra 
              ? message.isError 
                ? 'text-red-600' 
                : 'text-purple-600'
              : 'text-blue-100'
          }`}>
            {isSpectra ? 'Spectra' : 'You'}
          </div>

          {/* Message Text */}
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${
          isSpectra ? 'text-left' : 'text-right'
        }`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
