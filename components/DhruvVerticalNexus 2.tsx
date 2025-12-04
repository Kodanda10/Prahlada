import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2, Cpu, Database, BrainCircuit, Save, Eye, FileCheck, BarChart3, Search } from 'lucide-react';

// --- CONFIGURATION (Pure Hindi) ---
// Extended to match the 9 stages from Review.tsx
const DEFAULT_STAGES = [
    { id: 1, label: "डेटा अधिग्रहण", sub: "स्रोतों से कच्चा डेटा", icon: Database },
    { id: 2, label: "पूर्व प्रसंस्करण", sub: "सफाई और मानकीकरण", icon: Cpu },
    { id: 3, label: "पार्सर विश्लेषण", sub: "नियम आधारित पार्सिंग", icon: FileCheck },
    { id: 4, label: "एलएलएम संवर्धन", sub: "AI संदर्भ संवर्धन", icon: BrainCircuit },
    { id: 5, label: "विरोध पहचान", sub: "डेटा विसंगति जाँच", icon: Search },
    { id: 6, label: "मानवीय समीक्षा", sub: "निर्णय और सुधार", icon: Eye },
    { id: 7, label: "अंतिम स्वीकृति", sub: "गुणवत्ता नियंत्रण", icon: Check },
    { id: 8, label: "सिस्टम स्मृति", sub: "सुरक्षित भंडारण", icon: Save },
    { id: 9, label: "विश्लेषण तैयार", sub: "डैशबोर्ड अपडेट", icon: BarChart3 },
];

interface DhruvVerticalNexusProps {
    currentStage?: number; // 1-based index
    stages?: typeof DEFAULT_STAGES;
    autoPlay?: boolean;
}

export default function DhruvVerticalNexus({
    currentStage: propCurrentStage,
    stages = DEFAULT_STAGES,
    autoPlay = false
}: DhruvVerticalNexusProps) {
    const [internalStage, setInternalStage] = useState(1);

    // Use prop if provided, otherwise internal state
    const activeStage = propCurrentStage !== undefined ? propCurrentStage : internalStage;

    // Auto-Advance Simulator (For Demo)
    useEffect(() => {
        if (!autoPlay) return;

        const timer = setInterval(() => {
            setInternalStage(prev => (prev < stages.length ? prev + 1 : 1));
        }, 2500);
        return () => clearInterval(timer);
    }, [autoPlay, stages.length]);

    return (
        // CONTAINER: Deep Void Black
        <div className="flex items-start justify-center w-full h-full bg-[#020408] font-sans overflow-hidden rounded-3xl relative">

            {/* BACKGROUND: Subtle moving fog */}
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_50%_50%,_rgba(6,182,212,0.15),transparent_70%)] animate-pulse pointer-events-none" />

            <div className="relative z-10 w-full p-6">

                {/* HEADER */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] font-hindi">
                        प्रक्रिया पाइपलाइन
                    </h1>
                </div>

                {/* THE VERTICAL SPINE */}
                <div className="relative flex flex-col gap-6 pl-4">

                    {/* THE BEAM (Background Line) */}
                    <div className="absolute left-[2.5rem] top-4 bottom-4 w-0.5 bg-white/5" />

                    {/* THE PROGRESS BEAM (Active Line) */}
                    <motion.div
                        className="absolute left-[2.5rem] top-4 w-0.5 bg-cyan-400 shadow-[0_0_15px_#22d3ee]"
                        initial={{ height: "0%" }}
                        animate={{ height: `${((activeStage - 1) / (stages.length - 1)) * 100}%` }}
                        transition={{ duration: 0.8, ease: "easeInOut" }}
                    />

                    {stages.map((stage, index) => {
                        const stageId = index + 1;
                        const isActive = activeStage === stageId;
                        const isCompleted = activeStage > stageId;
                        const isPending = activeStage < stageId;

                        return (
                            <div key={stage.id} className="relative z-10 flex items-center gap-5">

                                {/* 1. THE ORB (Node) */}
                                <div className="relative flex-shrink-0">
                                    {/* Outer Glow Ring (Only when Active) */}
                                    {isActive && (
                                        <motion.div
                                            layoutId="active-ring"
                                            className="absolute -inset-3 rounded-full border border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.2)]"
                                            initial={{ scale: 0.8, opacity: 0 }}
                                            animate={{ scale: 1, opacity: 1, rotate: 180 }}
                                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                        />
                                    )}

                                    {/* The Core Orb */}
                                    <motion.div
                                        className={`
                      w-12 h-12 rounded-full flex items-center justify-center border-2 
                      backdrop-blur-xl transition-all duration-500
                      ${isCompleted
                                                ? "bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)]"
                                                : isActive
                                                    ? "bg-cyan-900/20 border-cyan-400 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.4)]"
                                                    : "bg-white/5 border-white/10 text-white/20"
                                            }
                    `}
                                        animate={{ scale: isActive ? 1.1 : 1 }}
                                    >
                                        {isCompleted ? (
                                            <Check className="w-5 h-5 stroke-[3]" />
                                        ) : isActive ? (
                                            <stage.icon className="w-5 h-5 animate-pulse" />
                                        ) : (
                                            <stage.icon className="w-5 h-5" />
                                        )}
                                    </motion.div>
                                </div>

                                {/* 2. THE DATA (Text) */}
                                <div className={`flex flex-col transition-all duration-500 ${isPending ? "opacity-30 blur-[1px]" : "opacity-100"}`}>
                                    <h3 className={`text-sm font-bold mb-0.5 font-hindi ${isActive ? "text-cyan-100 text-shadow-glow" : "text-white/80"}`}>
                                        {stage.label}
                                    </h3>
                                    <div className="flex items-center gap-2 text-[10px] font-medium font-mono text-white/50 uppercase tracking-wider">
                                        {isActive && <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />}
                                        <span>
                                            {isCompleted ? "संपन्न" : isActive ? "प्रोसेसिंग..." : stage.sub}
                                        </span>
                                    </div>
                                </div>

                            </div>
                        );
                    })}
                </div>

            </div>
        </div>
    );
}
