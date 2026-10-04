import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId] = useState('test-user-001');
  const [conversationId] = useState('conv-001');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages([...messages, { role: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          conversation_id: conversationId,
          text: userMessage,
          language: 'gu'
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.ai_response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', text: 'Connection error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <div className="header-content">
          <div className="logo">🎤</div>
          <div>
            <h1>ReVaani</h1>
            <p>Gujarati AI Assistant</p>
          </div>
        </div>
      </div>

      <div className="chat-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>Start a conversation</h2>
            <p>Type or speak in Gujarati</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-content">
              {msg.text}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message message-assistant">
            <div className="message-content">
              <span className="typing">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Message ReVaani..."
          disabled={loading}
          className="message-input"
        />
        <button 
          onClick={sendMessage} 
          disabled={loading || !input.trim()}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;