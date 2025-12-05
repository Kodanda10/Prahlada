/**
 * RiveLoader.tsx
 * 
 * Premium loading animation component.
 * Uses Framer Motion for smooth, world-class animations.
 * 
 * Features:
 * - Multiple loader variants (spinner, dots, pulse, orbital, neural)
 * - Customizable colors and sizes
 * - Accessibility support
 * - Reduced motion support
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type LoaderVariant = 'spinner' | 'dots' | 'pulse' | 'orbital' | 'neural';

export interface RiveLoaderProps {
  /** Size of the loader in pixels */
  size?: number;
  /** Loader variant */
  variant?: LoaderVariant;
  /** Primary color */
  color?: string;
  /** Secondary color */
  secondaryColor?: string;
  /** Loading text (optional) */
  text?: string;
  /** CSS class name */
  className?: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const RiveLoader: React.FC<RiveLoaderProps> = ({
  size = 48,
  variant = 'neural',
  color = '#6366f1', // Indigo
  secondaryColor = '#a855f7', // Purple
  text,
  className = '',
}) => {
  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Premium CSS-based loader
  const renderLoader = () => {
    // If user prefers reduced motion, show static version
    if (prefersReducedMotion) {
      return (
        <div 
          className="rounded-full"
          style={{
            width: size * 0.4,
            height: size * 0.4,
            background: `linear-gradient(135deg, ${color}, ${secondaryColor})`,
          }}
        />
      );
    }

    switch (variant) {
      case 'dots':
        return (
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="rounded-full"
                style={{
                  width: size / 4,
                  height: size / 4,
                  backgroundColor: color,
                }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 0.8,
                  repeat: Infinity,
                  delay: i * 0.15,
                  ease: 'easeInOut',
                }}
              />
            ))}
          </div>
        );

      case 'pulse':
        return (
          <motion.div
            className="rounded-full"
            style={{
              width: size,
              height: size,
              background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
            }}
            animate={{
              scale: [0.8, 1.2, 0.8],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        );

      case 'orbital':
        return (
          <div className="relative" style={{ width: size, height: size }}>
            {/* Outer ring */}
            <motion.div
              className="absolute inset-0 rounded-full border-2"
              style={{ borderColor: `${color}30` }}
            />
            {/* Orbiting dot */}
            <motion.div
              className="absolute rounded-full"
              style={{
                width: size / 6,
                height: size / 6,
                backgroundColor: color,
                top: 0,
                left: '50%',
                marginLeft: -size / 12,
                transformOrigin: `${size / 12}px ${size / 2}px`,
              }}
              animate={{ rotate: 360 }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          </div>
        );

      case 'spinner':
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            <Loader2 
              size={size} 
              style={{ color }} 
            />
          </motion.div>
        );

      case 'neural':
      default:
        return (
          <div className="relative" style={{ width: size, height: size }}>
            {/* Center core */}
            <motion.div
              className="absolute rounded-full"
              style={{
                width: size * 0.4,
                height: size * 0.4,
                top: '50%',
                left: '50%',
                marginTop: -size * 0.2,
                marginLeft: -size * 0.2,
                background: `linear-gradient(135deg, ${color}, ${secondaryColor})`,
                boxShadow: `0 0 ${size / 2}px ${color}50`,
              }}
              animate={{
                scale: [1, 1.15, 1],
                boxShadow: [
                  `0 0 ${size / 2}px ${color}50`,
                  `0 0 ${size}px ${color}70`,
                  `0 0 ${size / 2}px ${color}50`,
                ],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            {/* Orbiting nodes */}
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="absolute rounded-full"
                style={{
                  width: size * 0.12,
                  height: size * 0.12,
                  backgroundColor: secondaryColor,
                  boxShadow: `0 0 ${size / 4}px ${secondaryColor}`,
                  top: '50%',
                  left: '50%',
                  marginTop: -size * 0.06,
                  marginLeft: -size * 0.06,
                }}
                animate={{
                  x: [
                    Math.cos((i * 2 * Math.PI) / 3) * size * 0.35,
                    Math.cos((i * 2 * Math.PI) / 3 + Math.PI * 2) * size * 0.35,
                  ],
                  y: [
                    Math.sin((i * 2 * Math.PI) / 3) * size * 0.35,
                    Math.sin((i * 2 * Math.PI) / 3 + Math.PI * 2) * size * 0.35,
                  ],
                  scale: [1, 1.2, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'linear',
                  delay: i * 0.2,
                }}
              />
            ))}
          </div>
        );
    }
  };

  return (
    <div 
      className={`flex flex-col items-center justify-center gap-3 ${className}`}
      role="status"
      aria-label={text || "Loading..."}
    >
      <div style={{ width: size, height: size }} className="flex items-center justify-center">
        {renderLoader()}
      </div>

      {/* Optional text */}
      {text && (
        <motion.span
          className="text-sm font-medium text-slate-400 font-hindi"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          {text}
        </motion.span>
      )}
    </div>
  );
};

export default RiveLoader;

