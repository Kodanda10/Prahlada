import React from 'react';
import { motion } from 'framer-motion';

/**
 * Aurora Background - Deep Indigo/Violet mist showing system is "awake"
 * औरोरा पृष्ठभूमि - गहरी नीली धुंध जो दर्शाती है कि सिस्टम जागृत है
 */
export const AuroraBackground: React.FC = () => {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {/* Primary Aurora Wave - Deep Indigo */}
            <motion.div
                className="absolute w-full h-full"
                style={{
                    background: 'radial-gradient(ellipse at 30% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%)',
                    filter: 'blur(60px)',
                }}
                animate={{
                    x: ['0%', '10%', '0%'],
                    y: ['0%', '5%', '0%'],
                    scale: [1, 1.1, 1],
                }}
                transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: 'easeInOut',
                }}
            />

            {/* Secondary Aurora Wave - Deep Violet */}
            <motion.div
                className="absolute w-full h-full"
                style={{
                    background: 'radial-gradient(ellipse at 70% 40%, rgba(168, 85, 247, 0.12) 0%, transparent 50%)',
                    filter: 'blur(80px)',
                }}
                animate={{
                    x: ['0%', '-10%', '0%'],
                    y: ['0%', '-5%', '0%'],
                    scale: [1, 1.15, 1],
                }}
                transition={{
                    duration: 25,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 2,
                }}
            />

            {/* Tertiary Aurora Accent - Cyan */}
            <motion.div
                className="absolute w-full h-full"
                style={{
                    background: 'radial-gradient(ellipse at 50% 70%, rgba(139, 245, 230, 0.08) 0%, transparent 40%)',
                    filter: 'blur(100px)',
                }}
                animate={{
                    x: ['0%', '5%', '0%'],
                    y: ['0%', '10%', '0%'],
                    scale: [1, 1.2, 1],
                }}
                transition={{
                    duration: 30,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 5,
                }}
            />

            {/* Subtle particle field */}
            <div className="absolute inset-0">
                {[...Array(30)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute w-1 h-1 rounded-full"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            background: `rgba(139, 245, 230, ${Math.random() * 0.3})`,
                            boxShadow: '0 0 4px rgba(139, 245, 230, 0.5)',
                        }}
                        animate={{
                            opacity: [0, 1, 0],
                            scale: [0, 1.5, 0],
                            y: [0, -20, -40],
                        }}
                        transition={{
                            duration: 4 + Math.random() * 4,
                            repeat: Infinity,
                            delay: Math.random() * 5,
                            ease: 'easeInOut',
                        }}
                    />
                ))}
            </div>

            {/* Vignette effect */}
            <div
                className="absolute inset-0"
                style={{
                    background: 'radial-gradient(ellipse at center, transparent 30%, rgba(5, 5, 5, 0.8) 100%)',
                }}
            />
        </div>
    );
};
