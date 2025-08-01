import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-start space-x-3">
      {/* Spectra Avatar */}
      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white spectra-glow">
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
        </svg>
      </div>

      {/* Typing Animation */}
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 px-4 py-3 rounded-2xl rounded-tl-md max-w-xs">
        <div className="text-xs font-medium mb-1 text-purple-600">
          Spectra
        </div>
        <div className="flex items-center space-x-1">
          <div className="typing-indicator flex space-x-1">
            <span className="w-2 h-2 bg-purple-400 rounded-full inline-block"></span>
            <span className="w-2 h-2 bg-purple-400 rounded-full inline-block"></span>
            <span className="w-2 h-2 bg-purple-400 rounded-full inline-block"></span>
          </div>
          <span className="text-sm text-gray-500 ml-2">typing...</span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
