import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import { MessageSquare, Send, Sparkles, User, RefreshCw, Loader2 } from 'lucide-react';

export const Chat = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello! I am GreenMind AI, your personalized sustainability assistant. Ask me questions about carbon emissions, reductions, or eco-friendly habits. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (messageText) => {
    if (!messageText.trim()) return;

    const newMsg = { role: 'user', content: messageText };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setLoading(true);

    try {
      // Send chat request with current conversation history
      const response = await api.post('/api/chat', {
        message: messageText,
        history: messages
      });
      
      setMessages((prev) => [...prev, { role: 'assistant', content: response.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: "Sorry, I ran into an error processing that question. Please try again shortly!" }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend(input);
  };

  const quickPrompts = [
    "How can I reduce my car travel carbon?",
    "AC vs Fan: what's the carbon differences?",
    "Why does shopping online affect emissions?",
    "Suggest a simple vegan dinner recipe"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] max-w-4xl mx-auto animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200/50 dark:border-slate-800/40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400">
            <MessageSquare className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Eco Chatbot</h1>
            <p className="text-xs text-slate-500">Context-aware advice tailored to your carbon profile logs.</p>
          </div>
        </div>
        
        <button 
          onClick={() => setMessages([{ role: 'assistant', content: "Hello! Conversation reset. Ask me any sustainability questions!" }])}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl text-slate-400 hover:text-slate-600 transition-colors"
          title="Reset chat"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Pane */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1 scrollbar-thin">
        {messages.map((msg, i) => {
          const isUser = msg.role === 'user';
          return (
            <div 
              key={i} 
              className={`flex items-start gap-3 max-w-[85%] ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              <div className={`p-2 rounded-xl flex-shrink-0 border ${
                isUser 
                  ? 'bg-brand-500/10 border-brand-500/20 text-brand-600 dark:text-brand-400' 
                  : 'bg-slate-100 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 text-slate-500'
              }`}>
                {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
              </div>
              
              <div className={`p-4 rounded-2xl border text-sm leading-relaxed ${
                isUser 
                  ? 'bg-brand-600 border-brand-600 text-white rounded-tr-none' 
                  : 'bg-white dark:bg-slate-900/60 border-slate-200/50 dark:border-slate-800/40 text-slate-800 dark:text-slate-200 rounded-tl-none shadow-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          );
        })}
        
        {loading && (
          <div className="flex items-start gap-3 mr-auto max-w-[85%] animate-pulse">
            <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200/50 dark:border-slate-800/40 text-slate-400 rounded-tl-none shadow-sm flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider">
              <span>Coach is drafting response</span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Quick Prompts */}
      {messages.length === 1 && !loading && (
        <div className="py-3">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Suggested Questions</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="p-3 text-left rounded-xl bg-white/40 hover:bg-white dark:bg-slate-900/20 dark:hover:bg-slate-900 border border-slate-200/50 dark:border-slate-800/30 text-slate-700 dark:text-slate-300 text-xs font-semibold hover:border-brand-500 transition-all cursor-pointer truncate"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Input */}
      <form onSubmit={handleSubmit} className="mt-2 py-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          placeholder="Ask a question about your carbon score..."
          className="flex-1 px-4 py-3 bg-white/50 dark:bg-slate-900/60 border border-slate-300 dark:border-slate-800 rounded-2xl text-slate-950 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-3.5 bg-brand-600 hover:bg-brand-500 text-white rounded-2xl flex items-center justify-center disabled:opacity-50 transition-all cursor-pointer shadow-md shadow-brand-500/10"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
export default Chat;
