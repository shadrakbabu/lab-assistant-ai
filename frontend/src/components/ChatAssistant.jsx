import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, AlertCircle, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { api } from '../services/api';

export function ChatAssistant({ manualId, activeExperiment }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I am your AI Laboratory Assistant. Ask me anything about ${
        activeExperiment ? `Experiment ${activeExperiment.experiment_number}: ${activeExperiment.title}` : 'your uploaded laboratory manual'
      }. All my answers are grounded strictly in your manual.`,
      citations: [],
      grounded: true
    }
  ]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('standard');
  const [isLoading, setIsLoading] = useState(false);
  const [openCitations, setOpenCitations] = useState({});
  const chatEndRef = useRef(null);

  const suggestionChips = [
    activeExperiment ? `What is the procedure for Experiment ${activeExperiment.experiment_number}?` : 'What experiments are in this manual?',
    'Explain the theory in simple terms.',
    'What equipment is required?',
    'What safety precautions should I take?',
    'What should I do if I get wrong results?'
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (queryText) => {
    const text = queryText || input;
    if (!text.trim() || isLoading) return;

    const userMsg = { id: `u_${Date.now()}`, role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setIsLoading(true);

    try {
      const response = await api.sendChatMessage({
        manualId,
        experimentId: activeExperiment?.id || null,
        query: text,
        mode
      });

      const botMsg = {
        id: `b_${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        citations: response.citations || [],
        grounded: response.grounded
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          role: 'assistant',
          content: '⚠️ Failed to connect to AI assistant service. Please check your backend connection.',
          citations: [],
          grounded: false
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCitation = (msgId) => {
    setOpenCitations((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      
      {/* Header */}
      <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-100 flex items-center gap-2">
              <span>Grounded Lab AI Assistant</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                No Hallucinations
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              {activeExperiment ? `Active: Exp ${activeExperiment.experiment_number}` : 'Full Manual Mode'}
            </p>
          </div>
        </div>

        {/* Mode dropdown */}
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-1 focus:outline-none"
        >
          <option value="standard">Standard Explanation</option>
          <option value="simple_explanation">Simple Student Mode</option>
          <option value="troubleshooting">Troubleshooting</option>
          <option value="safety">Safety Mode</option>
        </select>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/10'
                : 'bg-slate-800/80 border border-slate-700/80 text-slate-200'
            }`}>
              {msg.role === 'assistant' ? (
                <div className="prose prose-invert prose-xs max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <p>{msg.content}</p>
              )}

              {/* Citations Drawer */}
              {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-700/60">
                  <button
                    onClick={() => toggleCitation(msg.id)}
                    className="flex items-center gap-1.5 text-[11px] text-blue-400 hover:text-blue-300 font-semibold"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>{msg.citations.length} Grounded Source Excerpts</span>
                    {openCitations[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {openCitations[msg.id] && (
                    <div className="mt-2 space-y-2">
                      {msg.citations.map((cite, cIdx) => (
                        <div key={cIdx} className="p-2.5 bg-slate-950/60 border border-slate-800 rounded-lg text-[11px] text-slate-300">
                          <div className="flex items-center justify-between text-blue-400 font-bold mb-1">
                            <span>{cite.section_name} ({cite.experiment_title || 'Manual'})</span>
                            <span className="text-[10px] text-slate-500">Match: {(cite.score * 100).toFixed(0)}%</span>
                          </div>
                          <p className="italic text-slate-400 text-[10px]">"{cite.excerpt}"</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}

          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <span>Searching manual context & generating grounded answer...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Suggestion Chips */}
      <div className="px-4 py-2 bg-slate-950/40 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <Sparkles className="w-3.5 h-3.5 text-blue-400 shrink-0" />
        {suggestionChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-[11px] text-slate-300 whitespace-nowrap transition"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask about ${activeExperiment ? `Exp ${activeExperiment.experiment_number}` : 'manual procedures, safety, theory...'}`}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition shadow-md shadow-blue-600/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
