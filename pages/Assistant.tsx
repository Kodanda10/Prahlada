
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, MapPin, Calendar } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { ChatMessage } from '../types';

const Assistant = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'नमस्ते! मैं आपका AI सहायक हूँ। आप मुझसे कार्यक्रमों, योजनाओं या क्षेत्रीय गतिविधियों के बारे में पूछ सकते हैं।',
      timestamp: new Date()
    }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'पिछले महीने रायगढ़ जिले में कुल **14 जनसम्पर्क कार्यक्रम** और **5 समीक्षा बैठकें** हुईं। इनमें से मुख्य रूप से **प्रधानमंत्री आवास योजना** पर चर्चा की गई।',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);
    }, 1000);
  };

  const suggestions = [
    "पिछले महीने रायगढ़ में कितने कार्यक्रम हुए?",
    "जल जीवन मिशन की स्थिति क्या है?",
    "खरसिया ब्लॉक में जनसम्पर्क का विवरण दें।"
  ];

  return (
    <div className="h-[calc(100vh-140px)] flex gap-6">
      
      {/* Left Sidebar - Context Filters (Desktop only) */}
      <div className="hidden xl:flex w-64 flex-col gap-4">
        <GlassCard className="h-full p-4">
          <div className="text-xs font-bold text-slate-500 uppercase mb-4 font-hindi">संदर्भ फिल्टर</div>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-slate-300 font-hindi">तिथि सीमा</label>
              <select className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 font-hindi">
                <option>पिछले 30 दिन</option>
                <option>यह तिमाही</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300 font-hindi">जिला</label>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded border border-blue-500/30 font-hindi">रायगढ़</span>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
        {/* Chat Header */}
        <div className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white font-hindi">AI सहायक</h3>
            <p className="text-xs text-slate-400 flex items-center gap-1 font-hindi">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              ऑनलाइन | FAISS + Gemini द्वारा संचालित
            </p>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-slate-600' : 'bg-cyan-600'}`}>
                 {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
              </div>
              <div className={`max-w-[70%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-white/10 border border-white/10 text-slate-100 rounded-tl-none'
              }`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap font-hindi">{msg.content}</p>
                {msg.role === 'assistant' && (
                   <div className="mt-2 pt-2 border-t border-white/10 flex gap-2">
                      <button className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-hindi">
                        <Sparkles size={10} /> विश्लेषण देखें
                      </button>
                   </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/10 bg-white/5">
           {messages.length < 3 && (
             <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
               {suggestions.map((s, i) => (
                 <button 
                    key={i} 
                    onClick={() => setInput(s)}
                    className="whitespace-nowrap px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-slate-300 hover:bg-white/10 transition-colors font-hindi"
                  >
                   {s}
                 </button>
               ))}
             </div>
           )}
           <div className="relative flex gap-2">
             <input 
               type="text" 
               value={input}
               onChange={(e) => setInput(e.target.value)}
               onKeyDown={(e) => e.key === 'Enter' && handleSend()}
               placeholder="यहाँ अपना प्रश्न लिखें..."
               className="flex-1 bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-hindi"
             />
             <button 
               onClick={handleSend}
               className="p-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl transition-colors shadow-lg shadow-cyan-600/20"
             >
               <Send size={20} />
             </button>
           </div>
        </div>
      </div>

      {/* Right Sidebar - RAG Info (Desktop only) */}
      <div className="hidden xl:flex w-72 flex-col gap-4">
        <GlassCard className="h-1/2 overflow-y-auto">
          <div className="text-xs font-bold text-slate-500 uppercase mb-4 flex items-center gap-2 font-hindi">
            <Sparkles size={14} className="text-yellow-500"/> संबंधित घटनाएँ
          </div>
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/5 text-xs hover:bg-white/10 cursor-pointer transition-colors">
                <p className="text-slate-300 line-clamp-2 font-hindi">जनसम्पर्क अभियान के दौरान ग्रामीणों की समस्याएं सुनीं...</p>
                <div className="mt-2 flex items-center gap-2 text-slate-500">
                  <Calendar size={10} /> <span className="font-hindi">24 Oct</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
         <GlassCard className="h-1/2">
          <div className="text-xs font-bold text-slate-500 uppercase mb-4 flex items-center gap-2 font-hindi">
             <MapPin size={14} className="text-red-500"/> भौगोलिक संदर्भ
          </div>
          <div className="space-y-2">
             <div className="flex justify-between text-sm border-b border-white/5 pb-2">
                <span className="text-slate-400 font-hindi">जिला</span>
                <span className="text-white font-hindi">रायगढ़</span>
             </div>
             <div className="flex justify-between text-sm border-b border-white/5 pb-2">
                <span className="text-slate-400 font-hindi">विकासखंड</span>
                <span className="text-white font-hindi">खरसिया</span>
             </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default Assistant;
