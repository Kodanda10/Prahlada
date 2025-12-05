/**
 * RiveIcon.tsx
 * 
 * Premium animated icon component.
 * Supports hover, active, loading, and success states with smooth transitions.
 * 
 * Features:
 * - State-driven animations
 * - Hover detection with smooth state transitions
 * - Accessibility support (reduced motion)
 * - Uses Lucide icons with Framer Motion animations
 */

import React, { useCallback, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type RiveIconState = 'idle' | 'hover' | 'active' | 'loading' | 'success' | 'error';

export interface RiveIconProps {
  /** Lucide icon component */
  icon: LucideIcon;
  /** Size of the icon in pixels */
  size?: number;
  /** Current state of the icon */
  state?: RiveIconState;
  /** Enable hover state detection */
  enableHover?: boolean;
  /** CSS class name */
  className?: string;
  /** Click handler */
  onClick?: () => void;
  /** Color for the icon */
  color?: string;
  /** Color for the glow effect */
  glowColor?: string;
  /** Whether to show glow effect */
  showGlow?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const RiveIcon: React.FC<RiveIconProps> = ({
  icon: Icon,
  size = 24,
  state = 'idle',
  enableHover = true,
  className = '',
  onClick,
  color = 'currentColor',
  glowColor = 'rgba(99, 102, 241, 0.5)',
  showGlow = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Event handlers
  const handleMouseEnter = useCallback(() => setIsHovered(true), []);
  const handleMouseLeave = useCallback(() => setIsHovered(false), []);

  // Calculate effective state
  const effectiveState = enableHover && isHovered && state === 'idle' ? 'hover' : state;

  // Calculate glow visibility
  const shouldShowGlow = showGlow || effectiveState === 'active' || effectiveState === 'success';

  // Animation variants based on state
  const getAnimationProps = () => {
    if (prefersReducedMotion) {
      return {};
    }

    switch (effectiveState) {
      case 'loading':
        return {
          animate: { rotate: 360 },
          transition: { duration: 1, repeat: Infinity, ease: 'linear' },
        };
      case 'success':
        return {
          initial: { scale: 0, rotate: -180 },
          animate: { scale: 1, rotate: 0 },
          transition: { type: 'spring', stiffness: 400, damping: 15 },
        };
      case 'error':
        return {
          animate: { x: [-2, 2, -2, 2, 0] },
          transition: { duration: 0.4 },
        };
      case 'active':
        return {
          animate: { scale: [1, 1.1, 1] },
          transition: { duration: 0.3 },
        };
      default:
        return {};
    }
  };

  // Color based on state
  const getColor = () => {
    switch (effectiveState) {
      case 'success':
        return '#10B981'; // Emerald
      case 'error':
        return '#EF4444'; // Red
      case 'loading':
        return '#6366F1'; // Indigo
      case 'active':
        return '#6366F1'; // Indigo
      default:
        return color;
    }
  };

  return (
    <motion.div
      className={`relative flex items-center justify-center cursor-pointer ${className}`}
      style={{ width: size, height: size }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      whileHover={enableHover && !prefersReducedMotion ? { scale: 1.1 } : {}}
      whileTap={!prefersReducedMotion ? { scale: 0.95 } : {}}
    >
      {/* Glow effect */}
      <AnimatePresence>
        {shouldShowGlow && !prefersReducedMotion && (
          <motion.div
            className="absolute inset-0 rounded-full blur-lg"
            style={{ backgroundColor: glowColor }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 0.6, scale: 1.3 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </AnimatePresence>

      {/* Icon */}
      <motion.div
        className="relative z-10"
        {...getAnimationProps()}
      >
        <Icon 
          size={size * 0.8} 
          style={{ color: getColor() }}
        />
      </motion.div>
    </motion.div>
  );
};

export default RiveIcon;
