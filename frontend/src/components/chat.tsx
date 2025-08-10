import React, { useState } from 'react';
import { chatWithSpectra, ChatResponse } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  async function handleSend() {
    if (!input.trim()) return;

    const newUserMessage: Message = { role: 'user', content: input };
    const newHistory = [...messages, newUserMessage];

    try {
      const result: ChatResponse = await chatWithSpectra(input, newHistory);
      const newBotMessage: Message = { role: 'assistant', content: result.response };
      setMessages([...newHistory, newBotMessage]);
      setInput('');
    } catch (error) {
      console.error('Chat error:', error);
      alert('Failed to contact Spectra backend.');
    }
  }

  return (
    <div>
      <div style={{ minHeight: 200, border: '1px solid #ddd', padding: 10, marginBottom: 10 }}>
        {messages.map((msg, idx) => (
          <p key={idx}>
            <strong>{msg.role === 'user' ? 'You' : 'Spectra'}:</strong> {msg.content}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        style={{ width: '80%', marginRight: 10 }}
        onKeyDown={e => {
          if (e.key === 'Enter') handleSend();
        }}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}