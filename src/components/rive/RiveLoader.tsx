/**
 * RiveLoader.tsx
 * 
 * Premium loading animation component using Rive.
 * Replaces boring spinners with engaging, on-brand animations.
 * 
 * Features:
 * - Multiple loader variants (spinner, dots, pulse, orbital)
 * - Customizable colors and sizes
 * - Accessibility support
 * - Fallback CSS animations when Rive unavailable
 */

import React, { useMemo } from 'react';
import { useRive, Layout, Fit, Alignment, UseRiveParameters } from '@rive-app/react-canvas';
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

  // Rive configuration
  const riveParams = useMemo<UseRiveParameters>(() => ({
    src: `/rive/loader-${variant}.riv`,
    stateMachines: ['State Machine'],
    autoplay: !prefersReducedMotion,
    layout: new Layout({
      fit: Fit.Contain,
      alignment: Alignment.Center,
    }),
  }), [variant, prefersReducedMotion]);

  const { RiveComponent, rive } = useRive(riveParams);

  // Fallback: CSS-based premium loader
  const renderFallbackLoader = () => {
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
                scale: [1, 1.1, 1],
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
                  width: size * 0.15,
                  height: size * 0.15,
                  backgroundColor: secondaryColor,
                  boxShadow: `0 0 ${size / 4}px ${secondaryColor}`,
                }}
                initial={{
                  top: '50%',
                  left: '50%',
                  marginTop: -size * 0.075,
                  marginLeft: -size * 0.075,
                }}
                animate={{
                  rotate: 360,
                  x: Math.cos((i * 2 * Math.PI) / 3) * size * 0.35,
                  y: Math.sin((i * 2 * Math.PI) / 3) * size * 0.35,
                }}
                transition={{
                  rotate: {
                    duration: 2,
                    repeat: Infinity,
                    ease: 'linear',
                  },
                  x: { duration: 0 },
                  y: { duration: 0 },
                }}
              />
            ))}
            {/* Spinner fallback */}
            <motion.div
              className="absolute inset-0"
              animate={{ rotate: 360 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              }}
            >
              <Loader2 
                size={size} 
                className="text-transparent" 
                style={{ 
                  stroke: `url(#gradient-${variant})`,
                  strokeWidth: 1.5,
                }} 
              />
            </motion.div>
            {/* SVG gradient definition */}
            <svg width="0" height="0">
              <defs>
                <linearGradient id={`gradient-${variant}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor={color} stopOpacity="0.8" />
                  <stop offset="100%" stopColor={secondaryColor} stopOpacity="0.8" />
                </linearGradient>
              </defs>
            </svg>
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
      {/* Try Rive, fallback to CSS */}
      <div style={{ width: size, height: size }}>
        {rive ? <RiveComponent /> : renderFallbackLoader()}
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
