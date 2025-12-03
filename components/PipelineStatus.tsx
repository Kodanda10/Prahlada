import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Database, BrainCircuit, UserCheck, BarChart3, HardDrive, Zap, CheckCircle2 } from 'lucide-react';

interface PipelineStatusProps {
    isApproving?: boolean;
}

const PipelineStatus: React.FC<PipelineStatusProps> = ({ isApproving }) => {
    const [activeNode, setActiveNode] = useState<number>(2); // Default to 'Human Review' (index 2)
    const [systemHealth, setSystemHealth] = useState<'healthy' | 'busy' | 'error'>('healthy');

    // Simulate pipeline flow on approval
    useEffect(() => {
        if (isApproving) {
            setActiveNode(2); // Start at Review
            const t1 = setTimeout(() => setActiveNode(3), 500); // Move to Insights
            const t2 = setTimeout(() => setActiveNode(4), 1500); // Move to Memory
            const t3 = setTimeout(() => setActiveNode(2), 2500); // Reset to Review
            return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
        }
    }, [isApproving]);

    const steps = [
        { id: 'ingest', label: 'डाटा संग्रह', sub: 'Data Ingestion', icon: Database, color: 'cyan' },
        { id: 'ai', label: 'एआई विश्लेषण', sub: 'AI Processing', icon: BrainCircuit, color: 'violet' },
        { id: 'review', label: 'मानव समीक्षा', sub: 'Human Review', icon: UserCheck, color: 'emerald' }, // Central Node
        { id: 'analytics', label: 'इन्साइट्स', sub: 'Analytics', icon: BarChart3, color: 'amber' },
        { id: 'memory', label: 'स्मृति', sub: 'Long-term Memory', icon: HardDrive, color: 'blue' }
    ];

    return (
        <div className="w-full h-full relative overflow-hidden rounded-2xl bg-[#0f172a]/80 backdrop-blur-xl border border-white/10 shadow-2xl flex flex-col">
            {/* Background Ambient Glow */}
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-violet-500/5 to-emerald-500/5 animate-pulse-slow pointer-events-none" />

            {/* Grid Pattern Overlay */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none mix-blend-overlay" />

            {/* Header: System Vitals */}
            <div className="p-4 border-b border-white/5 bg-black/20 backdrop-blur-md z-20 shrink-0">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold font-hindi">सिस्टम स्थिति</span>
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${systemHealth === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'} animate-ping absolute opacity-75`} />
                        <div className={`w-2 h-2 rounded-full ${systemHealth === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'} relative z-10`} />
                    </div>
                </div>
                <div className={`text-sm font-bold font-hindi flex items-center gap-2 ${systemHealth === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    <Activity size={16} className="animate-pulse" />
                    {systemHealth === 'healthy' ? 'प्रणाली सक्रिय' : 'लोड अधिक'}
                </div>

                {/* Queue Indicator */}
                <div className="mt-3 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center gap-2">
                    <Zap size={14} className="text-amber-400 fill-amber-400/20 animate-pulse" />
                    <span className="text-xs font-bold text-amber-300 font-hindi uppercase tracking-wider">समीक्षा कतार सक्रिय</span>
                </div>
            </div>

            {/* Vertical Neural Pipeline */}
            <div className="flex-1 relative flex flex-col items-center justify-between py-8 px-4 overflow-hidden">

                {/* Connecting Line (The Neural Pathway) */}
                <div className="absolute left-[2.5rem] top-8 bottom-8 w-0.5 bg-slate-800 z-0">
                    {/* Animated Data Particle */}
                    <AnimatePresence>
                        {isApproving && (
                            <motion.div
                                initial={{ top: '40%', opacity: 1, height: '20px' }}
                                animate={{ top: '100%', opacity: 0, height: '5px' }}
                                transition={{ duration: 1.5, ease: "easeInOut", repeat: Infinity }}
                                className="absolute left-1/2 -translate-x-1/2 w-1 bg-gradient-to-b from-transparent via-emerald-400 to-transparent blur-[2px] z-10"
                            />
                        )}
                    </AnimatePresence>
                </div>

                {steps.map((step, index) => {
                    const isActive = index === activeNode;
                    const isPast = index < activeNode;
                    const Icon = step.icon;

                    return (
                        <div key={step.id} className="relative z-10 w-full flex items-center gap-6 group">
                            {/* Node Orb */}
                            <div className="relative shrink-0">
                                <motion.div
                                    animate={{
                                        scale: isActive ? [1, 1.1, 1] : 1,
                                        boxShadow: isActive
                                            ? `0 0 20px ${getColorHex(step.color, 0.4)}, 0 0 40px ${getColorHex(step.color, 0.2)}`
                                            : 'none'
                                    }}
                                    transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
                                    className={`
                                        w-14 h-14 rounded-xl rotate-45 flex items-center justify-center
                                        border-2 transition-all duration-500
                                        ${isActive
                                            ? `bg-${step.color}-500/20 border-${step.color}-500 text-${step.color}-400`
                                            : isPast
                                                ? 'bg-slate-800/80 border-slate-700 text-slate-500'
                                                : 'bg-black/60 border-slate-800 text-slate-700'
                                        }
                                    `}
                                >
                                    <div className="-rotate-45">
                                        <Icon size={24} strokeWidth={2} />
                                    </div>

                                    {/* Success Check for Past Nodes */}
                                    {isPast && (
                                        <div className="absolute -top-2 -right-2 bg-slate-900 rounded-full p-0.5 border border-slate-700 z-20 rotate-[-45deg]">
                                            <CheckCircle2 size={12} className="text-emerald-500" />
                                        </div>
                                    )}
                                </motion.div>

                                {/* Active Pulse Ring */}
                                {isActive && (
                                    <div className={`absolute inset-0 rounded-xl rotate-45 border border-${step.color}-500/50 animate-ping opacity-50 pointer-events-none`} />
                                )}
                            </div>

                            {/* Label */}
                            <div className={`
                                flex flex-col transition-all duration-500
                                ${isActive ? 'opacity-100 translate-x-0' : 'opacity-50 translate-x-2'}
                            `}>
                                <span className={`
                                    text-lg font-bold font-hindi tracking-wide
                                    ${isActive ? `text-${step.color}-400 drop-shadow-[0_0_8px_rgba(0,0,0,0.5)]` : 'text-slate-500'}
                                `}>
                                    {step.label}
                                </span>
                                <span className="text-[10px] uppercase tracking-wider text-slate-600 font-mono">
                                    {step.sub}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// Helper to get hex color for shadow interpolation (Tailwind colors approx)
const getColorHex = (color: string, opacity: number) => {
    const colors: Record<string, string> = {
        cyan: `rgba(6, 182, 212, ${opacity})`,
        violet: `rgba(139, 92, 246, ${opacity})`,
        emerald: `rgba(16, 185, 129, ${opacity})`,
        amber: `rgba(245, 158, 11, ${opacity})`,
        blue: `rgba(59, 130, 246, ${opacity})`
    };
    return colors[color] || `rgba(255, 255, 255, ${opacity})`;
};

export default PipelineStatus;
