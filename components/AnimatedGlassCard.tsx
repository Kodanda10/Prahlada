/**
 * CRITICAL COMPONENT - DO NOT EDIT WITHOUT APPROVAL
 * 
 * This component provides the glassmorphism card effect used throughout the dashboard.
 * 
 * Props:
 * - title: Optional title for the card header
 * - action: Optional action element (buttons, etc.) for the header
 * - children: Content to render inside the card
 * - className: Additional classes
 * 
 * Styling:
 * - Uses Tailwind utility classes for glass effect (backdrop-blur, bg-white/5, etc.)
 * - Uses framer-motion for animations
 */
import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedGlassCardProps {
    children: React.ReactNode;
    className?: string;
    delay?: number;
    hoverEffect?: boolean;
    title?: string;
    action?: React.ReactNode;
}

const AnimatedGlassCard: React.FC<AnimatedGlassCardProps> = ({
    children,
    className = '',
    delay = 0,
    hoverEffect = false,
    title,
    action
}) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            whileHover={hoverEffect ? { scale: 1.02, transition: { duration: 0.2 } } : undefined}
            className={`bg-white/10 backdrop-blur-md border border-white/20 rounded-xl shadow-xl overflow-hidden flex flex-col ${className}`}
        >
            {(title || action) && (
                <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                    {title && <h3 className="text-lg font-semibold text-white font-hindi">{title}</h3>}
                    {action && <div>{action}</div>}
                </div>
            )}
            <div className="p-4 flex-1">
                {children}
            </div>
        </motion.div>
    );
};

export default AnimatedGlassCard;
