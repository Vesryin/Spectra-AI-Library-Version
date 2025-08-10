// src/components/Chat.jsx
import React, { useState } from 'react';
import { chatWithSpectra } from '../api/client';

export default function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  async function handleSend() {
    try {
      const result = await chatWithSpectra(input, messages);
      setMessages([...messages, { user: input }, { bot: result.response }]);
      setInput('');
    } catch (err) {
      console.error('Chat error:', err);
      alert('Error connecting to Spectra backend.');
    }
  }

  return (
    <div>
      <div style={{ minHeight: '200px', border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
        {messages.map((msg, i) => (
          <div key={i}>
            {msg.user && <p><b>You:</b> {msg.user}</p>}
            {msg.bot && <p><b>Spectra:</b> {msg.bot}</p>}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        style={{ width: '80%', marginRight: '10px' }}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}