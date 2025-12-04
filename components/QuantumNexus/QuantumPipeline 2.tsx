import React, { useRef, useEffect, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { GravityOrb } from './GravityOrb';
import { PlasmaStream } from './PlasmaStream';
import { AuroraBackground } from './AuroraBackground';
import { MouseLight } from './MouseLight';

interface PipelineStage {
    id: string;
    label: string;
    status: 'idle' | 'active' | 'completed';
    progress?: number;
}

interface QuantumPipelineProps {
    stages: PipelineStage[];
    className?: string;
}

/**
 * ध्रुव क्वांटम नेक्सस (v4)
 * A sentient organism that embodies the data pipeline
 * Not a UI - a Living Experience (LX)
 */
export const QuantumPipeline: React.FC<QuantumPipelineProps> = ({ stages, className = '' }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isBreathing, setIsBreathing] = useState(true);

    // Mouse tracking for dynamic lighting
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    // Smooth spring physics for mouse follower
    const springConfig = { damping: 25, stiffness: 150 };
    const smoothMouseX = useSpring(mouseX, springConfig);
    const smoothMouseY = useSpring(mouseY, springConfig);

    // Track mouse position
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (containerRef.current) {
                const rect = containerRef.current.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                setMousePosition({ x, y });
                mouseX.set(x);
                mouseY.set(y);
            }
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, [mouseX, mouseY]);

    // Breathing animation - the system breathes even when idle
    const breathingVariants = {
        inhale: {
            scale: 1.02,
            transition: {
                duration: 4,
                ease: 'easeInOut',
            },
        },
        exhale: {
            scale: 1,
            transition: {
                duration: 4,
                ease: 'easeInOut',
            },
        },
    };

    // Prismatic flash on complete
    const allCompleted = stages.every(s => s.status === 'completed');
    const [showPrismaticFlash, setShowPrismaticFlash] = useState(false);

    useEffect(() => {
        if (allCompleted) {
            setShowPrismaticFlash(true);
            setTimeout(() => setShowPrismaticFlash(false), 2000);
        }
    }, [allCompleted]);

    return (
        <div
            ref={containerRef}
            className={`relative w-full h-full overflow-hidden rounded-3xl ${className}`}
            style={{
                background: '#050505', // Obsidian black
                minHeight: '600px', // Taller for vertical layout
            }}
        >
            {/* Aurora Background - Deep Indigo/Violet mist */}
            <AuroraBackground />

            {/* Mouse Light Follower - The "Torch" effect */}
            <MouseLight x={smoothMouseX} y={smoothMouseY} />

            {/* Main Pipeline Container with Breathing */}
            <motion.div
                className="relative w-full h-full flex items-center justify-center py-8 px-6"
                animate={isBreathing ? 'inhale' : 'exhale'}
                variants={breathingVariants}
                onAnimationComplete={() => setIsBreathing(!isBreathing)}
            >
                {/* The Quantum Nodes - VERTICAL LAYOUT */}
                <div className="relative w-full h-full flex flex-col items-center justify-start space-y-0">
                    {stages.map((stage, index) => (
                        <React.Fragment key={stage.id}>
                            {/* Gravity Orb Node */}
                            <div className="flex-shrink-0">
                                <GravityOrb
                                    stage={stage}
                                    index={index}
                                    mousePosition={mousePosition}
                                />
                            </div>

                            {/* Plasma Stream Connection (except after last node) */}
                            {index < stages.length - 1 && (
                                <div className="w-full flex items-center justify-center" style={{ height: '40px' }}>
                                    <PlasmaStream
                                        fromStatus={stage.status}
                                        toStatus={stages[index + 1].status}
                                        isActive={stage.status === 'completed'}
                                        isVertical={true}
                                    />
                                </div>
                            )}
                        </React.Fragment>
                    ))}
                </div>
            </motion.div>

            {/* Prismatic Flash on Complete */}
            {showPrismaticFlash && (
                <motion.div
                    className="absolute inset-0 pointer-events-none"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 2, times: [0, 0.5, 1] }}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 opacity-30 blur-3xl" />
                    <motion.div
                        className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white to-transparent"
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ duration: 1 }}
                    />
                    <motion.div
                        className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white to-transparent"
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ duration: 1 }}
                    />
                    <motion.div
                        className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-transparent via-white to-transparent"
                        initial={{ scaleY: 0 }}
                        animate={{ scaleY: 1 }}
                        transition={{ duration: 1 }}
                    />
                    <motion.div
                        className="absolute right-0 top-0 bottom-0 w-1 bg-gradient-to-b from-transparent via-white to-transparent"
                        initial={{ scaleY: 0 }}
                        animate={{ scaleY: 1 }}
                        transition={{ duration: 1 }}
                    />
                </motion.div>
            )}

            {/* Subtle grid overlay for depth */}
            <div
                className="absolute inset-0 pointer-events-none opacity-5"
                style={{
                    backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(139, 245, 230, 0.15) 1px, transparent 0)',
                    backgroundSize: '40px 40px',
                }}
            />
        </div>
    );
};

export default QuantumPipeline;
