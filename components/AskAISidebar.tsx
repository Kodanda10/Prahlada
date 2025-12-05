import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';
import { apiService } from '../services/api';

interface AskAISidebarProps {
    tweetId: string;
}

interface Message {
    role: 'user' | 'ai';
    text: string;
}

const AskAISidebar: React.FC<AskAISidebarProps> = ({ tweetId }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleAsk = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', text: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response: any = await apiService.post('/api/review/ask-ai', {
                tweet_id: tweetId,
                question: input
            });

            const aiMessage: Message = { role: 'ai', text: response.answer };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Ask AI failed:', error);
            setMessages(prev => [...prev, {
                role: 'ai',
                text: 'क्षमा करें, कोई त्रुटि हुई। कृपया पुनः प्रयास करें।'
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ask-ai-sidebar visible bg-[#1e1b4b]/50 rounded-xl border border-white/10 p-4 h-full flex flex-col">
            <div className="mb-3">
                <h3 className="text-sm font-bold text-yellow-400 flex items-center gap-2 font-hindi">
                    <span className="text-lg">💬</span> एआई से पूछें
                </h3>
                <p className="text-[10px] text-slate-500 mt-1 font-hindi">
                    संज्ञानात्मक तर्क जानने के लिए प्रश्न करें
                </p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-2 mb-3">
                <AnimatePresence>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                            className={`p-3 rounded-lg text-xs ${msg.role === 'user'
                                ? 'bg-slate-700/50 text-slate-200 ml-4 border border-slate-600/50'
                                : 'bg-violet-500/20 text-violet-200 mr-4 border border-violet-500/30'
                                }`}
                        >
                            <div className="font-bold mb-1 text-[10px] opacity-70 font-hindi">
                                {msg.role === 'user' ? '👤 आप' : '🤖 एआई'}
                            </div>
                            <div className="whitespace-pre-wrap font-hindi leading-relaxed">
                                {msg.role === 'ai' ? (
                                    // Simple formatting: remove JSON/debug noise if present
                                    msg.text.split('\n').map((line, i) => {
                                        // Hide lines that look like raw JSON or debug keys unless explicitly asked
                                        if (line.trim().startsWith('{') || line.includes('"explicit":') || line.includes('Layers:')) {
                                            return null;
                                        }
                                        // Highlight key terms
                                        const parts = line.split(/(:)/);
                                        return (
                                            <div key={i} className="mb-1">
                                                {parts.map((part, pIdx) => (
                                                    <span key={pIdx} className={part.endsWith(':') ? 'font-bold text-violet-300' : ''}>
                                                        {part}
                                                    </span>
                                                ))}
                                            </div>
                                        );
                                    })
                                ) : (
                                    msg.text
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-2 rounded-lg bg-slate-600/20 text-slate-300 text-xs mr-4"
                    >
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
                            सोच रहा है...
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Input */}
            <div className="relative">
                <input
                    data-testid="ask-ai-input"
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAsk()}
                    placeholder="इस ट्वीट के बारे में पूछें..."
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 pr-10"
                />
                <button
                    data-testid="ask-ai-submit"
                    onClick={handleAsk}
                    disabled={loading || !input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-yellow-400 hover:text-yellow-300 disabled:opacity-30"
                >
                    <Send size={14} />
                </button>
            </div>
        </div>
    );
};

export default AskAISidebar;
