/**
 * useGeoNeuroAnimations.ts
 * 
 * Animation utilities and presets for the GeoNeuro visual system.
 * Provides state machine-like animation control using Framer Motion.
 */

// ============================================================================
// TYPES
// ============================================================================

export type AnimationState = 'idle' | 'hover' | 'active' | 'loading' | 'success' | 'error';

export interface AnimationConfig {
  duration?: number;
  delay?: number;
  ease?: string | number[];
}

// ============================================================================
// ANIMATION PRESETS
// ============================================================================

export const SPRING_PRESETS = {
  snappy: { type: 'spring', stiffness: 400, damping: 25 },
  bouncy: { type: 'spring', stiffness: 300, damping: 15 },
  smooth: { type: 'spring', stiffness: 200, damping: 30 },
  gentle: { type: 'spring', stiffness: 100, damping: 20 },
};

export const EASE_PRESETS = {
  smooth: [0.4, 0, 0.2, 1],
  bouncy: [0.68, -0.55, 0.265, 1.55],
  sharp: [0.4, 0, 0.6, 1],
  linear: [0, 0, 1, 1],
};

// ============================================================================
// RIVE-LIKE ASSET PATHS (for future use)
// ============================================================================

export const RIVE_ASSETS = {
  NEURAL_NETWORK: '/rive/neural-network.riv',
  BRAIN_PULSE: '/rive/brain-pulse.riv',
  LOCATION_PIN: '/rive/location-pin.riv',
  MAP_MARKER: '/rive/map-marker.riv',
  CHECK_SUCCESS: '/rive/check-success.riv',
  LOADING_SPINNER: '/rive/loading-spinner.riv',
  PROCESSING: '/rive/processing.riv',
  DATA_FLOW: '/rive/data-flow.riv',
  PIPELINE_NODE: '/rive/pipeline-node.riv',
  APPROVE: '/rive/approve.riv',
  REJECT: '/rive/reject.riv',
  EDIT: '/rive/edit.riv',
};

// ============================================================================
// ANIMATION VARIANTS FOR FRAMER MOTION
// ============================================================================

export const stateAnimations = {
  idle: {
    scale: 1,
    opacity: 1,
    rotate: 0,
  },
  hover: {
    scale: 1.05,
    opacity: 1,
    rotate: 0,
  },
  active: {
    scale: [1, 1.1, 1],
    opacity: 1,
  },
  loading: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
  success: {
    scale: [0, 1.2, 1],
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  error: {
    x: [-5, 5, -5, 5, 0],
    transition: {
      duration: 0.4,
    },
  },
};

// ============================================================================
// GLOW EFFECTS
// ============================================================================

export const glowColors = {
  primary: 'rgba(99, 102, 241, 0.5)', // Indigo
  secondary: 'rgba(168, 85, 247, 0.5)', // Purple
  success: 'rgba(16, 185, 129, 0.5)', // Emerald
  error: 'rgba(239, 68, 68, 0.5)', // Red
  warning: 'rgba(245, 158, 11, 0.5)', // Amber
  info: 'rgba(14, 165, 233, 0.5)', // Sky
};

// ============================================================================
// PRESETS (for component configuration)
// ============================================================================

export const RIVE_PRESETS = {
  neuralIcon: {
    variant: 'neural' as const,
    color: '#6366f1',
    secondaryColor: '#a855f7',
  },
  
  locationPin: {
    variant: 'pulse' as const,
    color: '#10b981',
    secondaryColor: '#14b8a6',
  },
  
  checkSuccess: {
    variant: 'pulse' as const,
    color: '#10b981',
  },
  
  loadingSpinner: {
    variant: 'spinner' as const,
    color: '#6366f1',
  },
  
  pipelineNode: {
    variant: 'neural' as const,
    color: '#6366f1',
    secondaryColor: '#a855f7',
  },
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function getStateTransition(state: AnimationState, config?: AnimationConfig) {
  const baseTransition = stateAnimations[state];
  
  return {
    ...baseTransition,
    transition: {
      ...baseTransition.transition,
      ...config,
    },
  };
}

export function getGlowStyle(color: keyof typeof glowColors = 'primary', intensity: number = 0.5) {
  return {
    boxShadow: `0 0 20px ${glowColors[color].replace('0.5', String(intensity))}`,
  };
}

export default {
  stateAnimations,
  glowColors,
  SPRING_PRESETS,
  EASE_PRESETS,
  RIVE_ASSETS,
  RIVE_PRESETS,
  getStateTransition,
  getGlowStyle,
};
