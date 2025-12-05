/**
 * useGeoNeuroAnimations.ts
 * 
 * Centralized Framer Motion variants and animation utilities
 * extracted from the canonical GeoNeuroResolver.tsx
 * 
 * Source of Truth: src/components/decision/GeoNeuroResolver.tsx
 */

import { useCallback, useState } from 'react';
import { Variants } from 'framer-motion';

// ============================================================================
// FRAMER MOTION VARIANTS
// ============================================================================

/**
 * Backdrop overlay animation - for modals and overlays
 */
export const backdropVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

/**
 * Modal container animation - spring-based entrance
 */
export const modalVariants: Variants = {
  hidden: { scale: 0.92, opacity: 0, y: 20 },
  visible: { 
    scale: 1, 
    opacity: 1, 
    y: 0, 
    transition: { type: 'spring', stiffness: 300, damping: 25 } 
  },
  exit: { scale: 0.95, opacity: 0, y: 10, transition: { duration: 0.2 } },
};

/**
 * Grid container animation - slide with blur
 */
export const gridVariants: Variants = {
  initial: { opacity: 0, x: 60, filter: 'blur(8px)' },
  animate: { 
    opacity: 1, 
    x: 0, 
    filter: 'blur(0px)', 
    transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } 
  },
  exit: { opacity: 0, x: -60, filter: 'blur(8px)', transition: { duration: 0.25, ease: 'easeIn' } },
};

/**
 * Chip/card animation - staggered entrance with hover/tap
 */
export const chipVariants: Variants = {
  initial: { opacity: 0, scale: 0.8, filter: 'blur(10px)' },
  animate: (i: number) => ({
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    transition: { delay: i * 0.04, type: 'spring', stiffness: 400, damping: 20 },
  }),
  exit: { opacity: 0, scale: 0, transition: { duration: 0.15 } },
  hover: { scale: 1.06, y: -3, transition: { type: 'spring', stiffness: 400, damping: 15 } },
  tap: { scale: 0.95 },
};

/**
 * Card entrance animation - fade up with scale
 */
export const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { type: 'spring', stiffness: 300, damping: 25 }
  },
  exit: { opacity: 0, y: -10, scale: 0.95, transition: { duration: 0.2 } },
};

/**
 * List item stagger animation
 */
export const listVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  },
};

export const listItemVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { type: 'spring', stiffness: 400, damping: 25 }
  },
};

/**
 * Button press animation
 */
export const buttonVariants: Variants = {
  idle: { scale: 1 },
  hover: { scale: 1.05 },
  tap: { scale: 0.95 },
};

/**
 * Pulse animation for active indicators
 */
export const pulseVariants: Variants = {
  pulse: {
    scale: [1, 1.3, 1],
    opacity: [1, 0.7, 1],
    transition: { repeat: Infinity, duration: 1.5 }
  }
};

// ============================================================================
// THEME DEFINITIONS (Design Tokens)
// ============================================================================

/**
 * GeoNeuro Color Themes - Rural vs Urban
 */
export const GEONEURO_THEMES = {
  RURAL: {
    gradient: 'from-emerald-950/95 via-green-900/90 to-teal-950/85',
    header: 'from-emerald-950/60 via-green-900/60 to-teal-950/60',
    accent: 'rgba(16,185,129,0.4)',
    secondary: 'rgba(20,184,166,0.3)',
    chipActive: 'bg-emerald-500/30 border-emerald-400/50 text-emerald-200 shadow-[0_0_20px_rgba(16,185,129,0.4)]',
    chipInactive: 'bg-white/5 border-white/10 text-slate-400 hover:bg-emerald-500/10 hover:border-emerald-400/30',
    glow: 'shadow-[0_0_30px_rgba(16,185,129,0.35)]',
    ring: 'ring-emerald-400/50',
  },
  URBAN: {
    gradient: 'from-slate-950/95 via-blue-900/90 to-indigo-950/85',
    header: 'from-slate-950/60 via-blue-900/60 to-indigo-950/60',
    accent: 'rgba(59,130,246,0.4)',
    secondary: 'rgba(99,102,241,0.3)',
    chipActive: 'bg-blue-500/30 border-blue-400/50 text-blue-200 shadow-[0_0_20px_rgba(59,130,246,0.4)]',
    chipInactive: 'bg-white/5 border-white/10 text-slate-400 hover:bg-blue-500/10 hover:border-blue-400/30',
    glow: 'shadow-[0_0_30px_rgba(59,130,246,0.35)]',
    ring: 'ring-blue-400/50',
  },
  // Default theme for non-geo contexts
  DEFAULT: {
    gradient: 'from-slate-950/95 via-purple-900/90 to-indigo-950/85',
    header: 'from-slate-950/60 via-purple-900/60 to-indigo-950/60',
    accent: 'rgba(99,102,241,0.4)',
    secondary: 'rgba(168,85,247,0.3)',
    chipActive: 'bg-indigo-500/30 border-indigo-400/50 text-indigo-200 shadow-[0_0_20px_rgba(99,102,241,0.4)]',
    chipInactive: 'bg-white/5 border-white/10 text-slate-400 hover:bg-indigo-500/10 hover:border-indigo-400/30',
    glow: 'shadow-[0_0_30px_rgba(99,102,241,0.35)]',
    ring: 'ring-indigo-400/50',
  },
};

/**
 * Step-based themes for geo hierarchy
 */
export const STEP_THEMES = {
  DISTRICT: { chip: 'bg-blue-500/20 border-blue-400/30', glow: 'shadow-[0_0_30px_rgba(59,130,246,0.35)]', accent: 'text-blue-200', ring: 'ring-blue-400/50' },
  VIDHANSABHA: { chip: 'bg-purple-500/20 border-purple-400/30', glow: 'shadow-[0_0_30px_rgba(168,85,247,0.35)]', accent: 'text-purple-200', ring: 'ring-purple-400/50' },
  BLOCK: { chip: 'bg-pink-500/20 border-pink-400/30', glow: 'shadow-[0_0_30px_rgba(236,72,153,0.35)]', accent: 'text-pink-200', ring: 'ring-pink-400/50' },
  ULB: { chip: 'bg-amber-500/20 border-amber-400/30', glow: 'shadow-[0_0_30px_rgba(245,158,11,0.35)]', accent: 'text-amber-200', ring: 'ring-amber-400/50' },
  GP: { chip: 'bg-teal-500/20 border-teal-400/30', glow: 'shadow-[0_0_30px_rgba(20,184,166,0.35)]', accent: 'text-teal-200', ring: 'ring-teal-400/50' },
  VILLAGE: { chip: 'bg-emerald-500/20 border-emerald-400/30', glow: 'shadow-[0_0_30px_rgba(16,185,129,0.35)]', accent: 'text-emerald-200', ring: 'ring-emerald-400/50' },
  WARD: { chip: 'bg-cyan-500/20 border-cyan-400/30', glow: 'shadow-[0_0_30px_rgba(6,182,212,0.35)]', accent: 'text-cyan-200', ring: 'ring-cyan-400/50' },
};

// ============================================================================
// SHARED CSS CLASS UTILITIES
// ============================================================================

/**
 * GeoNeuro card base classes
 */
export const GEONEURO_CARD_CLASSES = {
  base: 'relative bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl backdrop-blur-xl',
  glow: 'shadow-[0_0_30px_rgba(99,102,241,0.2)]',
  hover: 'hover:border-white/20 hover:shadow-[0_0_40px_rgba(99,102,241,0.3)] transition-all duration-300',
  active: 'border-indigo-400/50 shadow-[0_0_40px_rgba(99,102,241,0.4)]',
};

/**
 * GeoNeuro chip base classes
 */
export const GEONEURO_CHIP_CLASSES = {
  base: 'px-4 py-2 rounded-xl border backdrop-blur-sm transition-all duration-300',
  interactive: 'cursor-pointer hover:scale-105 active:scale-95',
};

// ============================================================================
// HOOKS
// ============================================================================

/**
 * 3D Tilt effect hook
 * Extracted from GeoNeuroResolver.tsx
 */
export function useTiltEffect(sensitivity: number = 8) {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleTilt = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * sensitivity;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -sensitivity;
    setTilt({ x, y });
  }, [sensitivity]);

  const resetTilt = useCallback(() => setTilt({ x: 0, y: 0 }), []);

  return { tilt, handleTilt, resetTilt };
}

/**
 * Spring configuration presets
 */
export const SPRING_PRESETS = {
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
  bouncy: { type: 'spring' as const, stiffness: 300, damping: 15 },
  smooth: { type: 'spring' as const, stiffness: 200, damping: 30 },
  gentle: { type: 'spring' as const, stiffness: 100, damping: 20 },
};

/**
 * Ease presets for non-spring animations
 */
export const EASE_PRESETS = {
  smooth: [0.25, 0.1, 0.25, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
  snap: [0.4, 0, 0.2, 1],
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get stagger delay for list items
 */
export function getStaggerDelay(index: number, baseDelay: number = 0.04): number {
  return index * baseDelay;
}

/**
 * Combine base classes with conditional classes
 */
export function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export default {
  // Variants
  backdropVariants,
  modalVariants,
  gridVariants,
  chipVariants,
  cardVariants,
  listVariants,
  listItemVariants,
  buttonVariants,
  pulseVariants,
  // Themes
  GEONEURO_THEMES,
  STEP_THEMES,
  // Classes
  GEONEURO_CARD_CLASSES,
  GEONEURO_CHIP_CLASSES,
  // Hooks
  useTiltEffect,
  // Presets
  SPRING_PRESETS,
  EASE_PRESETS,
  // Utils
  getStaggerDelay,
  cn,
};
