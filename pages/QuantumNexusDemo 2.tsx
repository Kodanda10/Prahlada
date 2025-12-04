import React, { useState, useEffect } from 'react';
import { QuantumPipeline } from '../components/QuantumNexus';
import { motion } from 'framer-motion';
import { PlayCircle, PauseCircle, RotateCcw, Zap } from 'lucide-react';

/**
 * Demo page for the Dhruv Quantum Nexus (v4)
 * Showcases the living, breathing pipeline in all its states
 */
const QuantumNexusDemo = () => {
    const [autoPlay, setAutoPlay] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);

    // Auto-cycle through stages
    useEffect(() => {
        if (!autoPlay) return;

        const interval = setInterval(() => {
            setCurrentStep((prev) => (prev + 1) % 5);
        }, 3000);

        return () => clearInterval(interval);
    }, [autoPlay]);

    // Get stages based on current step
    const getStages = () => {
        const baseStages = [
            { id: 'acquisition', label: 'डेटा अधिग्रहण', status: 'idle' as const },
            { id: 'analysis', label: 'न्यूरल विश्लेषण', status: 'idle' as const },
            { id: 'decision', label: 'मानवीय निर्णय', status: 'idle' as const },
            { id: 'memory', label: 'सिस्टम स्मृति', status: 'idle' as const },
        ];

        return baseStages.map((stage, index) => {
            if (index < currentStep) {
                return { ...stage, status: 'completed' as const };
            } else if (index === currentStep) {
                return { ...stage, status: 'active' as const, progress: 65 };
            }
            return stage;
        });
    };

    return (
        <div className="min-h-screen bg-[#050505] p-8">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-7xl mx-auto space-y-8"
            >
                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.h1
                        className="text-5xl font-bold font-hindi bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
                        animate={{
                            backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                        }}
                        transition={{
                            duration: 5,
                            repeat: Infinity,
                            ease: 'linear',
                        }}
                        style={{
                            backgroundSize: '200% auto',
                        }}
                    >
                        ध्रुव क्वांटम नेक्सस
                    </motion.h1>
                    <p className="text-xl text-slate-400 font-hindi">
                        जीवित ऊर्जा क्षेत्र — The Sentient Organism
                    </p>
                    <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
                        <Zap size={16} className="text-cyan-400" />
                        <span className="font-mono">v4.0 — Beyond UI, Enter Living Experience (LX)</span>
                    </div>
                </div>

                {/* Control Panel */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center justify-center gap-4 p-6 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl"
                >
                    <button
                        onClick={() => setAutoPlay(!autoPlay)}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${autoPlay
                                ? 'bg-amber-500/20 text-amber-400 border-2 border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.3)]'
                                : 'bg-white/10 text-white hover:bg-white/20 border-2 border-white/10'
                            }`}
                    >
                        {autoPlay ? (
                            <>
                                <PauseCircle size={20} />
                                <span className="font-hindi">विराम (Pause)</span>
                            </>
                        ) : (
                            <>
                                <PlayCircle size={20} />
                                <span className="font-hindi">प्रारंभ (Play)</span>
                            </>
                        )}
                    </button>

                    <button
                        onClick={() => setCurrentStep(0)}
                        className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl border-2 border-white/10 transition-all font-medium"
                    >
                        <RotateCcw size={20} />
                        <span className="font-hindi">रीसेट (Reset)</span>
                    </button>

                    <div className="flex items-center gap-2 px-6 py-3 bg-black/30 rounded-xl border border-white/10">
                        <span className="text-slate-400 text-sm font-hindi">चरण:</span>
                        <span className="text-cyan-400 font-bold font-mono">{currentStep} / 4</span>
                    </div>
                </motion.div>

                {/* Main Quantum Pipeline */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-black/20 backdrop-blur-xl border border-white/5 rounded-3xl p-8 shadow-2xl"
                >
                    <QuantumPipeline stages={getStages()} />
                </motion.div>

                {/* Feature Highlights */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                    <div className="p-6 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl space-y-3">
                        <div className="text-cyan-400 font-bold text-lg font-hindi">🫁 साँस लेता है (Breathes)</div>
                        <p className="text-slate-400 text-sm">
                            The system inhales and exhales every 4 seconds, showing it's alive even when idle.
                        </p>
                    </div>

                    <div className="p-6 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl space-y-3">
                        <div className="text-amber-400 font-bold text-lg font-hindi">💡 प्रकाश अनुसरण (Light Follower)</div>
                        <p className="text-slate-400 text-sm">
                            Move your mouse — the "Torch" effect makes glass and metal glow dynamically.
                        </p>
                    </div>

                    <div className="p-6 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl space-y-3">
                        <div className="text-purple-400 font-bold text-lg font-hindi">⚡ तरल ऊर्जा (Liquid Energy)</div>
                        <p className="text-slate-400 text-sm">
                            Comet particles flow through organic, turbulent plasma streams between nodes.
                        </p>
                    </div>
                </motion.div>

                {/* Design Philosophy */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="p-8 bg-gradient-to-br from-purple-900/20 to-cyan-900/20 backdrop-blur-xl border border-white/10 rounded-3xl"
                >
                    <h2 className="text-2xl font-bold text-white mb-4 font-hindi">
                        मूल दर्शन (Core Philosophy)
                    </h2>
                    <div className="space-y-4 text-slate-300 leading-relaxed">
                        <p>
                            <span className="text-cyan-400 font-bold">We're not building a "screen".</span> We're
                            creating a <span className="text-purple-400 font-bold">Living Energy Field (जीवित ऊर्जा क्षेत्र)</span>.
                        </p>
                        <p>
                            This panel breathes. It doesn't just <em>display</em> data — it makes you <em>feel</em> it.
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                            <div className="p-4 bg-black/30 rounded-xl border border-cyan-500/20">
                                <div className="text-cyan-400 font-bold mb-2">❌ What v3 Did</div>
                                <ul className="text-sm text-slate-400 space-y-1 list-disc list-inside">
                                    <li>Linear flow (Left → Right)</li>
                                    <li>Static glassmorphism</li>
                                    <li>Predictable colors</li>
                                </ul>
                            </div>
                            <div className="p-4 bg-black/30 rounded-xl border border-purple-500/20">
                                <div className="text-purple-400 font-bold mb-2">✅ What v4 Does</div>
                                <ul className="text-sm text-slate-400 space-y-1 list-disc list-inside">
                                    <li>Organic growth & evolution</li>
                                    <li>Dynamic light & materiality</li>
                                    <li>Emotional, living data</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Technical Specs */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="p-6 bg-black/40 backdrop-blur-xl border border-white/5 rounded-2xl"
                >
                    <h3 className="text-lg font-bold text-white mb-4 font-mono">Technical Implementation</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="text-cyan-400 font-mono">Rendering:</span>
                            <p className="text-slate-400 ml-4">CSS backdrop-filter + mix-blend-mode: color-dodge</p>
                        </div>
                        <div>
                            <span className="text-purple-400 font-mono">Animation:</span>
                            <p className="text-slate-400 ml-4">Framer Motion (Spring physics)</p>
                        </div>
                        <div>
                            <span className="text-amber-400 font-mono">Particles:</span>
                            <p className="text-slate-400 ml-4">Custom Canvas API + SVG turbulence filters</p>
                        </div>
                        <div>
                            <span className="text-emerald-400 font-mono">Interaction:</span>
                            <p className="text-slate-400 ml-4">Mouse tracking + Radial gradient follower</p>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
};

export default QuantumNexusDemo;
