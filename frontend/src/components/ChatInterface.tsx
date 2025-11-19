import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Paperclip, Loader2, Bot, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(e.target.files);
      const formData = new FormData();
      for (let i = 0; i < e.target.files.length; i++) {
        formData.append('files', e.target.files[i]);
      }

      try {
        setUploadStatus('Uploading...');
        const response = await axios.post('/api/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        console.log('Upload response:', response.data);
        setUploadStatus(`Files uploaded: ${JSON.stringify(response.data.results)}`);
        setTimeout(() => setUploadStatus(''), 5000);
      } catch (error) {
        setUploadStatus('Error uploading files.');
        console.error('Upload error:', error);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        query: userMessage.content,
        api_key: apiKey || undefined,
        provider: 'groq',
        model: 'llama-3.3-70b-versatile'
      });

      const botMessage = {
        role: 'assistant' as const,
        content: response.data.answer,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error. Please check your connection or API key." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] w-full max-w-4xl mx-auto bg-black/40 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
      {/* Header / Settings */}
      <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
        <div className="flex items-center gap-2">
          <Bot className="text-orange-500" />
          <h2 className="font-bold text-lg">RAG Assistant</h2>
        </div>
        <div className="flex gap-4 items-center">
          <input
            type="password"
            placeholder="Groq API Key (Optional - Default provided)"
            className="bg-black/50 border border-white/20 rounded px-3 py-1 text-sm focus:outline-none focus:border-orange-500 transition-colors w-64"
            value={apiKey}
            onChange={(e: any) => setApiKey(e.target.value)}
          />
          <div className="relative">
            <input
              type="file"
              multiple
              id="file-upload"
              className="hidden"
              onChange={handleUpload}
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex items-center gap-2 text-sm hover:text-orange-400 transition-colors"
            >
              <Paperclip size={18} />
              {uploadStatus || "Upload Docs"}
            </label>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/20">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center text-white/50 mt-20"
            >
              <Bot size={48} className="mx-auto mb-4 opacity-50" />
              <p>Upload documents and start chatting!</p>
            </motion.div>
          )}
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-orange-600' : 'bg-purple-600'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-orange-600/20 border border-orange-500/30 text-white' 
                  : 'bg-white/10 border border-white/10 text-gray-100'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10 text-xs text-gray-400">
                    <p className="font-semibold mb-1">Sources:</p>
                    <ul className="list-disc pl-4 space-y-1">
                      {msg.sources.map((s: any, i: number) => (
                        <li key={i}>{s.filename} (Sim: {s.similarity.toFixed(2)})</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="bg-white/10 rounded-2xl px-4 py-3 flex items-center gap-2">
                <Loader2 className="animate-spin" size={16} />
                <span className="text-sm text-gray-400">Thinking...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white/5 border-t border-white/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 bg-black/50 border border-white/20 rounded-xl px-4 py-3 focus:outline-none focus:border-orange-500 transition-colors placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl px-6 transition-colors flex items-center justify-center"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
}
