/**
 * RiveSuccess.tsx
 * 
 * Premium success/completion animation component.
 * Shows a satisfying checkmark or celebration animation.
 * 
 * Features:
 * - Multiple success variants
 * - Confetti effect
 * - Sound-ready (optional callbacks for haptic/audio)
 */

import React, { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, CheckCircle2, Sparkles } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type SuccessVariant = 'checkmark' | 'confetti' | 'pulse' | 'ring';

export interface RiveSuccessProps {
  /** Whether the success state is active */
  isSuccess: boolean;
  /** Size of the success indicator */
  size?: number;
  /** Variant of the success animation */
  variant?: SuccessVariant;
  /** Primary color */
  color?: string;
  /** Auto-hide after milliseconds (0 = never) */
  autoHideAfter?: number;
  /** Callback when animation completes */
  onComplete?: () => void;
  /** CSS class name */
  className?: string;
}

// ============================================================================
// CONFETTI PARTICLE
// ============================================================================

const ConfettiParticle: React.FC<{ index: number; size: number; color: string }> = ({ index, size, color }) => {
  const angle = (index * 360) / 12;
  const distance = size * 0.8;
  const endX = Math.cos((angle * Math.PI) / 180) * distance;
  const endY = Math.sin((angle * Math.PI) / 180) * distance;
  
  const colors = ['#10B981', '#6366F1', '#F59E0B', '#EC4899', '#14B8A6', color];
  const particleColor = colors[index % colors.length];

  return (
    <motion.div
      className="absolute rounded-full"
      style={{
        width: size * 0.08,
        height: size * 0.08,
        backgroundColor: particleColor,
        top: '50%',
        left: '50%',
        marginTop: -size * 0.04,
        marginLeft: -size * 0.04,
      }}
      initial={{ scale: 0, x: 0, y: 0, opacity: 1 }}
      animate={{
        scale: [0, 1.5, 1, 0],
        x: [0, endX * 0.5, endX],
        y: [0, endY * 0.5, endY],
        opacity: [1, 1, 0.8, 0],
      }}
      transition={{
        duration: 0.8,
        delay: index * 0.02,
        ease: 'easeOut',
      }}
    />
  );
};

// ============================================================================
// COMPONENT
// ============================================================================

export const RiveSuccess: React.FC<RiveSuccessProps> = ({
  isSuccess,
  size = 64,
  variant = 'confetti',
  color = '#10B981', // Emerald
  autoHideAfter = 0,
  onComplete,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);

  // Handle visibility
  useEffect(() => {
    if (isSuccess) {
      setIsVisible(true);
      
      if (autoHideAfter > 0) {
        const timer = setTimeout(() => {
          setIsVisible(false);
          onComplete?.();
        }, autoHideAfter);
        return () => clearTimeout(timer);
      }
    } else {
      setIsVisible(false);
    }
  }, [isSuccess, autoHideAfter, onComplete]);

  // Render function based on variant
  const renderSuccess = () => {
    switch (variant) {
      case 'checkmark':
        return (
          <motion.div
            className="relative flex items-center justify-center"
            style={{ width: size, height: size }}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 15 }}
          >
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background: `linear-gradient(135deg, ${color}, ${color}88)`,
                boxShadow: `0 0 ${size / 2}px ${color}50`,
              }}
            />
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 500, damping: 15 }}
            >
              <Check size={size * 0.5} strokeWidth={3} className="text-white relative z-10" />
            </motion.div>
          </motion.div>
        );

      case 'pulse':
        return (
          <motion.div
            className="relative flex items-center justify-center"
            style={{ width: size, height: size }}
          >
            {/* Pulse rings */}
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="absolute inset-0 rounded-full border-2"
                style={{ borderColor: color }}
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{
                  scale: [0.5, 1.5, 2],
                  opacity: [0.8, 0.4, 0],
                }}
                transition={{
                  duration: 1.5,
                  delay: i * 0.3,
                  repeat: 1,
                  ease: 'easeOut',
                }}
              />
            ))}
            {/* Center icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
            >
              <CheckCircle2 size={size * 0.6} className="text-emerald-400 relative z-10" />
            </motion.div>
          </motion.div>
        );

      case 'ring':
        return (
          <motion.div
            className="relative flex items-center justify-center"
            style={{ width: size, height: size }}
          >
            {/* Drawing ring */}
            <svg width={size} height={size} className="absolute inset-0">
              <motion.circle
                cx={size / 2}
                cy={size / 2}
                r={size / 2 - 4}
                fill="none"
                stroke={color}
                strokeWidth={3}
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </svg>
            {/* Center check */}
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 400, damping: 15 }}
            >
              <Check size={size * 0.4} strokeWidth={3} style={{ color }} />
            </motion.div>
          </motion.div>
        );

      case 'confetti':
      default:
        return (
          <motion.div
            className="relative flex items-center justify-center"
            style={{ width: size, height: size }}
          >
            {/* Confetti particles */}
            {Array.from({ length: 12 }).map((_, i) => (
              <ConfettiParticle key={i} index={i} size={size} color={color} />
            ))}
            
            {/* Sparkle effect */}
            <motion.div
              className="absolute"
              initial={{ scale: 0, rotate: 0 }}
              animate={{ scale: [0, 1.2, 1], rotate: [0, 180] }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              <Sparkles size={size * 0.3} className="text-amber-400" />
            </motion.div>

            {/* Center checkmark */}
            <motion.div
              className="relative z-10 flex items-center justify-center rounded-full"
              style={{
                width: size * 0.5,
                height: size * 0.5,
                background: `linear-gradient(135deg, ${color}, ${color}88)`,
                boxShadow: `0 0 ${size / 3}px ${color}50`,
              }}
              initial={{ scale: 0, rotate: -90 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 400, damping: 15 }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: 'spring', stiffness: 500, damping: 15 }}
              >
                <Check size={size * 0.25} strokeWidth={3} className="text-white" />
              </motion.div>
            </motion.div>
          </motion.div>
        );
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={`inline-flex items-center justify-center ${className}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 0.5 }}
          transition={{ duration: 0.2 }}
        >
          {renderSuccess()}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default RiveSuccess;
