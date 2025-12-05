/**
 * RiveIcon.tsx
 * 
 * Premium animated icon component using Rive.
 * Supports hover, active, loading, and success states with smooth transitions.
 * 
 * Features:
 * - State machine driven animations
 * - Hover detection with smooth state transitions
 * - Accessibility support (reduced motion)
 * - Fallback to static icons when Rive fails
 */

import React, { useCallback, useState, useMemo, useEffect } from 'react';
import { useRive, Layout, Fit, Alignment, UseRiveParameters } from '@rive-app/react-canvas';
import { motion, AnimatePresence } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type RiveIconState = 'idle' | 'hover' | 'active' | 'loading' | 'success' | 'error';

export interface RiveIconProps {
  /** Path to the Rive file */
  src: string;
  /** Size of the icon in pixels */
  size?: number;
  /** Current state of the icon */
  state?: RiveIconState;
  /** State machine name in the Rive file */
  stateMachine?: string;
  /** Artboard name (optional) */
  artboard?: string;
  /** Enable hover state detection */
  enableHover?: boolean;
  /** Fallback Lucide icon when Rive fails */
  fallbackIcon?: LucideIcon;
  /** CSS class name */
  className?: string;
  /** Click handler */
  onClick?: () => void;
  /** Color for the glow effect */
  glowColor?: string;
  /** Whether to show glow effect */
  showGlow?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const RiveIcon: React.FC<RiveIconProps> = ({
  src,
  size = 24,
  state = 'idle',
  stateMachine = 'State Machine',
  artboard,
  enableHover = true,
  fallbackIcon: FallbackIcon,
  className = '',
  onClick,
  glowColor = 'rgba(99, 102, 241, 0.5)',
  showGlow = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Rive configuration
  const riveParams = useMemo<UseRiveParameters>(() => ({
    src,
    stateMachines: [stateMachine],
    artboard,
    autoplay: !prefersReducedMotion,
    layout: new Layout({
      fit: Fit.Contain,
      alignment: Alignment.Center,
    }),
    onLoad: () => setIsLoaded(true),
    onLoadError: () => setHasError(true),
  }), [src, stateMachine, artboard, prefersReducedMotion]);

  const { rive, RiveComponent } = useRive(riveParams);

  // Update state machine inputs based on state and hover
  useEffect(() => {
    if (!rive || !isLoaded) return;

    const inputs = rive.stateMachineInputs(stateMachine);
    if (!inputs) return;

    // Find and set the appropriate boolean inputs
    const setInput = (name: string, value: boolean) => {
      const input = inputs.find(i => i.name === name);
      if (input && input.type === 56) { // Boolean type
        input.value = value;
      }
    };

    // Determine effective state (hover takes precedence if enabled)
    const effectiveState = enableHover && isHovered && state === 'idle' ? 'hover' : state;

    // Reset all states
    setInput('isIdle', false);
    setInput('isHover', false);
    setInput('isActive', false);
    setInput('isLoading', false);
    setInput('isSuccess', false);
    setInput('isError', false);

    // Set current state
    switch (effectiveState) {
      case 'idle':
        setInput('isIdle', true);
        break;
      case 'hover':
        setInput('isHover', true);
        break;
      case 'active':
        setInput('isActive', true);
        break;
      case 'loading':
        setInput('isLoading', true);
        break;
      case 'success':
        setInput('isSuccess', true);
        break;
      case 'error':
        setInput('isError', true);
        break;
    }
  }, [rive, isLoaded, state, isHovered, enableHover, stateMachine]);

  // Event handlers
  const handleMouseEnter = useCallback(() => setIsHovered(true), []);
  const handleMouseLeave = useCallback(() => setIsHovered(false), []);

  // Calculate glow visibility
  const shouldShowGlow = showGlow || state === 'active' || state === 'success';

  // Render fallback if Rive failed
  if (hasError && FallbackIcon) {
    return (
      <motion.div
        className={`flex items-center justify-center ${className}`}
        style={{ width: size, height: size }}
        onClick={onClick}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <FallbackIcon size={size * 0.8} className="text-current" />
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`relative flex items-center justify-center cursor-pointer ${className}`}
      style={{ width: size, height: size }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      whileHover={{ scale: enableHover ? 1.1 : 1 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Glow effect */}
      <AnimatePresence>
        {shouldShowGlow && (
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

      {/* Rive canvas */}
      <div className="relative z-10 w-full h-full">
        <RiveComponent />
      </div>

      {/* Loading placeholder */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-1/2 h-1/2 rounded-full bg-white/10 animate-pulse" />
        </div>
      )}
    </motion.div>
  );
};

export default RiveIcon;
