import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Send, Loader } from 'lucide-react';

const AuraChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endOfMessagesRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/conversations?user_id=1&limit=20');
      if (response.ok) {
        const data = await response.json();
        const history = data.map(msg => ({
          role: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.message
        }));
        setMessages(history.reverse()); // Data is most recent first, so reverse to chronological
      }
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = inputValue;
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/chat/think', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, message: userMessage, mode: 'Personal' })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "[SYSTEM_ERROR: Neural net disconnected.]" }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "[SYSTEM_ERROR: Uplink failed.]" }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="flex flex-col h-[500px] mt-8 bg-black/20 backdrop-blur-md border border-[#FFB000]/30 rounded-lg shadow-[0_0_15px_rgba(255,176,0,0.1)] relative overflow-hidden"
    >
      {/* Decorative corner brackets */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[#FFB000]"></div>
      <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[#FFB000]"></div>
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[#FFB000]"></div>
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[#FFB000]"></div>

      {/* Header */}
      <div className="flex items-center gap-2 p-3 border-b border-[#FFB000]/20 bg-black/40">
        <Terminal size={18} className="text-[#FFB000]" />
        <h3 className="text-xl tracking-widest uppercase text-glow font-bold">FRIDAY COM-LINK</h3>
        <span className="ml-auto flex items-center gap-2 text-xs opacity-70">
          <span className="w-2 h-2 rounded-full bg-[#FFB000] animate-pulse"></span>
          UPLINK ACTIVE
        </span>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center mt-20 opacity-50 tracking-widest">
            AWAITING DIRECTIVE...
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <motion.div 
            key={idx} 
            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <span className="text-xs tracking-widest opacity-50 mb-1">
              {msg.role === 'user' ? 'CHANDU' : 'AURA'}
            </span>
            <div className={`p-3 rounded-md max-w-[80%] ${
              msg.role === 'user' 
                ? 'bg-[#FFB000]/10 border border-[#FFB000]/30 text-right' 
                : 'bg-black/40 border-l-2 border-[#FFB000] text-left'
            }`}>
              <div className="text-lg leading-snug">{msg.content}</div>
            </div>
          </motion.div>
        ))}

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-start"
          >
            <span className="text-xs tracking-widest opacity-50 mb-1">AURA</span>
            <div className="p-3 rounded-md bg-black/40 border-l-2 border-[#FFB000] flex items-center gap-2">
              <Loader size={16} className="animate-spin text-[#FFB000]" />
              <span className="text-sm opacity-80 italic animate-pulse">Processing...</span>
            </div>
          </motion.div>
        )}

        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="border-t border-[#FFB000]/20 p-3 bg-black/40 flex items-center gap-3">
        <span className="text-[#FFB000] font-bold">{`>`}</span>
        <input 
          type="text" 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="ENTER COMMAND DIRECTIVE..."
          className="flex-1 bg-transparent border-none outline-none text-[#FFB000] text-lg tracking-wider placeholder-[#FFB000]/30 font-['VT323'] uppercase"
        />
        <button 
          type="submit" 
          disabled={!inputValue.trim() || isTyping}
          className="p-2 hover:bg-[#FFB000]/10 rounded transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <Send size={20} className="text-[#FFB000]" />
        </button>
      </form>
    </motion.div>
  );
};

export default AuraChat;
