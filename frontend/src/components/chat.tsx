import React, { useState, KeyboardEvent } from 'react';
import { chatWithSpectra, ChatResponse } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const containerStyle: React.CSSProperties = {
  minHeight: 200,
  border: '1px solid #ddd',
  padding: 10,
  marginBottom: 10,
  overflowY: 'auto',
  maxHeight: 300,
};

const Chat: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState<boolean>(false);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;

    const newUserMessage: Message = { role: 'user', content: input.trim() };
    const newHistory = [...messages, newUserMessage];

    setIsSending(true);

    try {
      const result: ChatResponse = await chatWithSpectra(input.trim(), newHistory);
      const newBotMessage: Message = { role: 'assistant', content: result.response };
      setMessages([...newHistory, newBotMessage]);
      setInput('');
    } catch (error) {
      console.error('Chat error:', error);
      alert('Failed to contact Spectra backend.');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div>
      <div style={containerStyle} aria-live="polite" aria-label="Chat messages">
        {messages.length === 0 && <p>No messages yet. Say hello to Spectra!</p>}
        {messages.map((msg, idx) => (
          <p key={idx}>
            <strong>{msg.role === 'user' ? 'You' : 'Spectra'}:</strong> {msg.content}
          </p>
        ))}
      </div>

      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        style={{ width: '80%', marginRight: 10 }}
        aria-label="Chat input"
        disabled={isSending}
      />
      <button onClick={handleSend} disabled={!input.trim() || isSending} aria-label="Send message">
        {isSending ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
};

export default Chat;