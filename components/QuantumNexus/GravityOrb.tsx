import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface GravityOrbProps {
    stage: {
        id: string;
        label: string;
        status: 'idle' | 'active' | 'completed';
        progress?: number;
    };
    index: number;
    mousePosition: { x: number; y: number };
}

/**
 * Suspended Gravity Well - A levitating sphere that distorts space
 * ग्रैविटी ऑर्ब - अंतरिक्ष में तैरता हुआ गोला
 */
export const GravityOrb: React.FC<GravityOrbProps> = ({ stage, index, mousePosition }) => {
    const [showShockwave, setShowShockwave] = useState(false);

    // Trigger shockwave when transitioning to completed
    useEffect(() => {
        if (stage.status === 'completed') {
            setShowShockwave(true);
            setTimeout(() => setShowShockwave(false), 1000);
        }
    }, [stage.status]);

    // Color schemes for different states
    const getOrbColors = () => {
        switch (stage.status) {
            case 'idle':
                return {
                    primary: 'rgba(139, 245, 230, 0.1)', // Transparent cyan glass
                    glow: 'rgba(139, 245, 230, 0.0)',
                    smoke: 'rgba(100, 200, 255, 0.3)',
                };
            case 'active':
                return {
                    primary: 'rgba(255, 191, 0, 0.25)', // Liquid Gold
                    glow: 'rgba(255, 191, 0, 0.8)',
                    smoke: 'rgba(255, 140, 0, 0.6)',
                };
            case 'completed':
                return {
                    primary: 'rgba(16, 185, 129, 0.2)', // Emerald Neon
                    glow: 'rgba(16, 185, 129, 0.9)',
                    smoke: 'rgba(52, 211, 153, 0.4)',
                };
        }
    };

    const colors = getOrbColors();

    // Rotation speed based on status
    const rotationSpeed = stage.status === 'active' ? 4 : 20;

    return (
        <div className="relative flex flex-col items-center" style={{ flex: '0 0 auto' }}>
            {/* The Levitating Orb - Smaller for vertical layout */}
            <div className="relative w-20 h-20 mb-3">
                {/* Outer Glow Ring */}
                {stage.status !== 'idle' && (
                    <motion.div
                        className="absolute inset-0 rounded-full"
                        style={{
                            background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
                            filter: 'blur(20px)',
                        }}
                        animate={{
                            scale: stage.status === 'active' ? [1, 1.3, 1] : 1,
                            opacity: stage.status === 'active' ? [0.5, 0.8, 0.5] : 0.6,
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                    />
                )}

                {/* Main Glass Sphere */}
                <motion.div
                    className="absolute inset-0 rounded-full overflow-hidden"
                    style={{
                        background: colors.primary,
                        backdropFilter: 'blur(20px)',
                        boxShadow: `
              inset 0 0 30px ${colors.smoke},
              0 0 40px ${colors.glow},
              0 0 80px ${colors.glow}
            `,
                        border: `1px solid ${colors.primary}`,
                    }}
                    animate={{
                        rotateY: stage.status === 'active' ? 360 : 0,
                        scale: stage.status === 'active' ? [1, 1.05, 1] : 1,
                    }}
                    transition={{
                        rotateY: {
                            duration: rotationSpeed,
                            repeat: Infinity,
                            ease: 'linear',
                        },
                        scale: {
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        },
                    }}
                >
                    {/* Internal Smoke/Energy */}
                    <motion.div
                        className="absolute inset-0 rounded-full"
                        style={{
                            background: `radial-gradient(circle at 30% 30%, ${colors.smoke} 0%, transparent 60%)`,
                            filter: 'blur(15px)',
                        }}
                        animate={{
                            x: ['-10%', '10%', '-10%'],
                            y: ['-10%', '10%', '-10%'],
                            scale: [1, 1.2, 1],
                        }}
                        transition={{
                            duration: 8,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                    />

                    {/* Particle attraction effect for active state */}
                    {stage.status === 'active' && (
                        <>
                            {[...Array(6)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="absolute w-1 h-1 rounded-full bg-amber-400"
                                    style={{
                                        left: '50%',
                                        top: '50%',
                                    }}
                                    animate={{
                                        x: [
                                            Math.cos((i * Math.PI * 2) / 6) * 60,
                                            Math.cos((i * Math.PI * 2) / 6) * 20,
                                            0,
                                        ],
                                        y: [
                                            Math.sin((i * Math.PI * 2) / 6) * 60,
                                            Math.sin((i * Math.PI * 2) / 6) * 20,
                                            0,
                                        ],
                                        opacity: [0, 1, 0],
                                        scale: [0, 1.5, 0],
                                    }}
                                    transition={{
                                        duration: 2,
                                        repeat: Infinity,
                                        delay: i * 0.2,
                                        ease: 'easeInOut',
                                    }}
                                />
                            ))}
                        </>
                    )}

                    {/* Completion checkmark */}
                    {stage.status === 'completed' && (
                        <motion.div
                            className="absolute inset-0 flex items-center justify-center"
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                        >
                            <svg
                                width="40"
                                height="40"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                className="text-emerald-400"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                            >
                                <polyline points="20 6 9 17 4 12" />
                            </svg>
                        </motion.div>
                    )}
                </motion.div>

                {/* Shockwave on completion */}
                {showShockwave && (
                    <motion.div
                        className="absolute inset-0 rounded-full border-2 border-emerald-400"
                        initial={{ scale: 1, opacity: 0.8 }}
                        animate={{ scale: 3, opacity: 0 }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                    />
                )}

                {/* Progress ring for active state */}
                {stage.status === 'active' && stage.progress !== undefined && (
                    <svg className="absolute inset-0 w-full h-full -rotate-90">
                        <circle
                            cx="50%"
                            cy="50%"
                            r="62"
                            fill="none"
                            stroke="rgba(255, 191, 0, 0.3)"
                            strokeWidth="2"
                        />
                        <motion.circle
                            cx="50%"
                            cy="50%"
                            r="62"
                            fill="none"
                            stroke="rgba(255, 191, 0, 1)"
                            strokeWidth="2"
                            strokeLinecap="round"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: stage.progress / 100 }}
                            transition={{ duration: 0.5 }}
                            style={{
                                strokeDasharray: '390',
                                strokeDashoffset: 390 * (1 - (stage.progress || 0) / 100),
                            }}
                        />
                    </svg>
                )}
            </div>

            {/* Laser-Etched Label */}
            <motion.div
                className="relative text-center"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2 }}
            >
                <div
                    className="font-hindi text-sm font-bold tracking-widest uppercase"
                    style={{
                        color: stage.status === 'idle' ? 'rgba(139, 245, 230, 0.5)' : colors.glow,
                        textShadow: `
              0 0 10px ${colors.glow},
              0 0 20px ${colors.glow},
              0 0 30px ${colors.glow}
            `,
                        filter: stage.status !== 'idle' ? 'brightness(1.5)' : 'brightness(0.8)',
                        letterSpacing: '0.15em',
                    }}
                >
                    {stage.label}
                </div>

                {/* Subtitle based on status */}
                <motion.div
                    className="text-xs text-slate-500 mt-1 font-mono"
                    animate={{
                        opacity: stage.status === 'active' ? [0.5, 1, 0.5] : 0.6,
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'easeInOut',
                    }}
                >
                    {stage.status === 'idle' && '⏸ प्रतीक्षारत'}
                    {stage.status === 'active' && '⚡ सक्रिय'}
                    {stage.status === 'completed' && '✓ पूर्ण'}
                </motion.div>
            </motion.div>
        </div>
    );
};
