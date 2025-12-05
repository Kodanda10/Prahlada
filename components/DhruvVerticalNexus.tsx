import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Loader2, Cpu, Database, BrainCircuit, Save, Eye, FileCheck, BarChart3, Search } from 'lucide-react';
import { GEONEURO_THEMES, SPRING_PRESETS } from '../src/hooks/useGeoNeuroAnimations';
import { RiveSuccess } from '../src/components/rive';
import { RiveLoader } from '../src/components/rive';

// --- CONFIGURATION (Pure Hindi) ---
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
    currentStage?: number;
    stages?: typeof DEFAULT_STAGES;
    autoPlay?: boolean;
}

export default function DhruvVerticalNexus({
    currentStage: propCurrentStage,
    stages = DEFAULT_STAGES,
    autoPlay = false
}: DhruvVerticalNexusProps) {
    const [internalStage, setInternalStage] = useState(1);
    const [justCompleted, setJustCompleted] = useState<number | null>(null);

    const activeStage = propCurrentStage !== undefined ? propCurrentStage : internalStage;

    // Auto-Advance Simulator
    useEffect(() => {
        if (!autoPlay) return;
        const timer = setInterval(() => {
            setInternalStage(prev => {
                const next = prev < stages.length ? prev + 1 : 1;
                setJustCompleted(prev); // Track which stage just completed
                setTimeout(() => setJustCompleted(null), 800); // Reset after animation
                return next;
            });
        }, 2500);
        return () => clearInterval(timer);
    }, [autoPlay, stages.length]);

    // Detect stage completion for celebration animation
    useEffect(() => {
        if (propCurrentStage !== undefined) {
            setJustCompleted(propCurrentStage - 1);
            const timer = setTimeout(() => setJustCompleted(null), 800);
            return () => clearTimeout(timer);
        }
    }, [propCurrentStage]);

    return (
        <div className="flex items-start justify-center w-full h-full bg-geoneuro-default font-sans overflow-hidden rounded-3xl relative geoneuro-3d-container">
            {/* BACKGROUND: Neural ambient glow */}
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_50%_50%,_rgba(99,102,241,0.15),transparent_70%)] animate-geo-glow pointer-events-none" />

            <div className="relative z-10 w-full p-6">
                {/* HEADER */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] font-hindi">
                        प्रक्रिया पाइपलाइन
                    </h1>
                </div>

                {/* THE VERTICAL SPINE */}
                <div className="relative flex flex-col gap-6 pl-4">
                    {/* Background Line */}
                    <div className="absolute left-[2.5rem] top-4 bottom-4 w-0.5 bg-white/5" />

                    {/* Progress Beam */}
                    <motion.div
                        className="absolute left-[2.5rem] top-4 w-0.5 bg-geoneuro-primary shadow-geoneuro"
                        initial={{ height: "0%" }}
                        animate={{ height: `${((activeStage - 1) / (stages.length - 1)) * 100}%` }}
                        transition={{ duration: 0.8, ease: "easeInOut" }}
                    />

                    {stages.map((stage, index) => {
                        const stageId = index + 1;
                        const isActive = activeStage === stageId;
                        const isCompleted = activeStage > stageId;
                        const isPending = activeStage < stageId;
                        const wasJustCompleted = justCompleted === stageId;

                        return (
                            <div key={stage.id} className="relative z-10 flex items-center gap-5">
                                {/* THE ORB (Node) */}
                                <div className="relative flex-shrink-0">
                                    {/* Outer Glow Ring (Active) */}
                                    <AnimatePresence>
                                        {isActive && (
                                            <motion.div
                                                layoutId="active-ring"
                                                className="absolute -inset-3 rounded-full border border-indigo-500/30"
                                                initial={{ scale: 0.8, opacity: 0 }}
                                                animate={{ 
                                                    scale: [1, 1.2, 1], 
                                                    opacity: [0.5, 0.8, 0.5],
                                                    boxShadow: [
                                                        '0 0 20px rgba(99,102,241,0.2)',
                                                        '0 0 40px rgba(99,102,241,0.4)',
                                                        '0 0 20px rgba(99,102,241,0.2)',
                                                    ]
                                                }}
                                                exit={{ scale: 0.8, opacity: 0 }}
                                                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                                            />
                                        )}
                                    </AnimatePresence>

                                    {/* The Core Orb */}
                                    <motion.div
                                        className={`
                                            w-12 h-12 rounded-full flex items-center justify-center border-2 
                                            backdrop-blur-xl transition-all duration-500
                                            ${isCompleted
                                                ? "bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)]"
                                                : isActive
                                                    ? "bg-indigo-900/20 border-indigo-400 text-indigo-300 shadow-[0_0_20px_rgba(99,102,241,0.4)]"
                                                    : "bg-white/5 border-white/10 text-white/20"
                                            }
                                        `}
                                        animate={{ 
                                            scale: isActive ? 1.1 : 1,
                                            rotate: isActive ? [0, 5, -5, 0] : 0,
                                        }}
                                        transition={{ 
                                            scale: { type: 'spring', stiffness: 400, damping: 20 },
                                            rotate: { duration: 2, repeat: isActive ? Infinity : 0 }
                                        }}
                                    >
                                        {/* Completed: Show success animation */}
                                        {isCompleted && (
                                            <motion.div
                                                initial={{ scale: 0, rotate: -180 }}
                                                animate={{ scale: 1, rotate: 0 }}
                                                transition={{ type: 'spring', stiffness: 500, damping: 15 }}
                                            >
                                                <Check className="w-5 h-5 stroke-[3]" />
                                            </motion.div>
                                        )}

                                        {/* Active: Show premium loader */}
                                        {isActive && (
                                            <RiveLoader 
                                                size={24} 
                                                variant="neural" 
                                                color="#6366f1"
                                                secondaryColor="#a855f7"
                                            />
                                        )}

                                        {/* Pending: Show icon */}
                                        {isPending && (
                                            <stage.icon className="w-5 h-5" />
                                        )}
                                    </motion.div>

                                    {/* Just completed celebration */}
                                    {wasJustCompleted && (
                                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                            <RiveSuccess 
                                                isSuccess={true} 
                                                size={64} 
                                                variant="confetti"
                                                color="#10B981"
                                            />
                                        </div>
                                    )}
                                </div>

                                {/* THE DATA (Text) */}
                                <motion.div 
                                    className={`flex flex-col transition-all duration-500 ${isPending ? "opacity-30 blur-[1px]" : "opacity-100"}`}
                                    animate={{
                                        x: isActive ? 5 : 0,
                                    }}
                                    transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                                >
                                    <h3 className={`text-sm font-bold mb-0.5 font-hindi ${isActive ? "text-indigo-100" : isCompleted ? "text-emerald-200" : "text-white/80"}`}>
                                        {stage.label}
                                    </h3>
                                    <div className="flex items-center gap-2 text-[10px] font-medium font-mono text-white/50 uppercase tracking-wider">
                                        {isActive && (
                                            <motion.span
                                                animate={{ opacity: [0.5, 1, 0.5] }}
                                                transition={{ duration: 1.5, repeat: Infinity }}
                                                className="text-indigo-400"
                                            >
                                                ●
                                            </motion.span>
                                        )}
                                        <span className={isCompleted ? "text-emerald-400" : ""}>
                                            {isCompleted ? "✓ संपन्न" : isActive ? "प्रोसेसिंग..." : stage.sub}
                                        </span>
                                    </div>
                                </motion.div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
