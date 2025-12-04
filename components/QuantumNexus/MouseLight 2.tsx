import React from 'react';
import { motion, MotionValue } from 'framer-motion';

interface MouseLightProps {
    x: MotionValue<number>;
    y: MotionValue<number>;
}

/**
 * Mouse Light Follower - The "Torch" effect
 * माउस प्रकाश - मशाल प्रभाव
 * 
 * Makes glass and metal surfaces glow as the mouse moves over them
 */
export const MouseLight: React.FC<MouseLightProps> = ({ x, y }) => {
    return (
        <>
            {/* Primary spotlight */}
            <motion.div
                className="absolute pointer-events-none"
                style={{
                    left: x,
                    top: y,
                    width: '400px',
                    height: '400px',
                    background: 'radial-gradient(circle, rgba(139, 245, 230, 0.15) 0%, transparent 60%)',
                    filter: 'blur(40px)',
                    transform: 'translate(-50%, -50%)',
                }}
            />

            {/* Secondary glow - more focused */}
            <motion.div
                className="absolute pointer-events-none"
                style={{
                    left: x,
                    top: y,
                    width: '200px',
                    height: '200px',
                    background: 'radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
                    filter: 'blur(20px)',
                    transform: 'translate(-50%, -50%)',
                }}
            />

            {/* Core highlight - very bright center */}
            <motion.div
                className="absolute pointer-events-none"
                style={{
                    left: x,
                    top: y,
                    width: '60px',
                    height: '60px',
                    background: 'radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%)',
                    filter: 'blur(10px)',
                    transform: 'translate(-50%, -50%)',
                }}
            />

            {/* Ambient particles around cursor */}
            {[...Array(5)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute pointer-events-none w-1 h-1 rounded-full bg-cyan-400/50"
                    style={{
                        left: x,
                        top: y,
                    }}
                    animate={{
                        x: Math.cos((i * Math.PI * 2) / 5) * 30,
                        y: Math.sin((i * Math.PI * 2) / 5) * 30,
                        opacity: [0.3, 0.7, 0.3],
                        scale: [0.5, 1, 0.5],
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
    );
};
