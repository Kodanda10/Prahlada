/**
 * useRiveAnimation.ts
 * 
 * World-class Rive animation hook for the GeoNeuro visual system.
 * Provides unified state machine control, performance optimization,
 * and accessibility support.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRive, UseRiveParameters, RiveState, StateMachineInput, Layout, Fit, Alignment } from '@rive-app/react-canvas';

// ============================================================================
// TYPES
// ============================================================================

export type AnimationState = 'idle' | 'hover' | 'active' | 'loading' | 'success' | 'error';

export interface RiveAnimationConfig {
  src: string;
  stateMachine?: string;
  artboard?: string;
  autoplay?: boolean;
  fit?: Fit;
  alignment?: Alignment;
}

export interface UseRiveAnimationReturn {
  RiveComponent: React.FC<{ className?: string; style?: React.CSSProperties }>;
  rive: RiveState | null;
  isLoaded: boolean;
  error: Error | null;
  setState: (state: AnimationState) => void;
  currentState: AnimationState;
  play: () => void;
  pause: () => void;
  reset: () => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

export const RIVE_ASSETS = {
  // Neural/Brain icons
  NEURAL_NETWORK: '/rive/neural-network.riv',
  BRAIN_PULSE: '/rive/brain-pulse.riv',
  
  // Geo/Location icons
  LOCATION_PIN: '/rive/location-pin.riv',
  MAP_MARKER: '/rive/map-marker.riv',
  
  // Status/Action icons
  CHECK_SUCCESS: '/rive/check-success.riv',
  LOADING_SPINNER: '/rive/loading-spinner.riv',
  PROCESSING: '/rive/processing.riv',
  
  // Pipeline/Flow icons
  DATA_FLOW: '/rive/data-flow.riv',
  PIPELINE_NODE: '/rive/pipeline-node.riv',
  
  // Decision icons
  APPROVE: '/rive/approve.riv',
  REJECT: '/rive/reject.riv',
  EDIT: '/rive/edit.riv',
};

// State machine input names (convention)
export const STATE_INPUTS = {
  IS_IDLE: 'isIdle',
  IS_HOVER: 'isHover',
  IS_ACTIVE: 'isActive',
  IS_LOADING: 'isLoading',
  IS_SUCCESS: 'isSuccess',
  IS_ERROR: 'isError',
  TRIGGER: 'trigger',
};

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

export function useRiveAnimation(config: RiveAnimationConfig): UseRiveAnimationReturn {
  const [currentState, setCurrentState] = useState<AnimationState>('idle');
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // Rive parameters
  const riveParams = useMemo<UseRiveParameters>(() => ({
    src: config.src,
    stateMachines: config.stateMachine ? [config.stateMachine] : undefined,
    artboard: config.artboard,
    autoplay: config.autoplay ?? !prefersReducedMotion,
    layout: new Layout({
      fit: config.fit ?? Fit.Contain,
      alignment: config.alignment ?? Alignment.Center,
    }),
    onLoad: () => setIsLoaded(true),
    onLoadError: (err: Error) => setError(err),
  }), [config.src, config.stateMachine, config.artboard, config.autoplay, config.fit, config.alignment, prefersReducedMotion]);

  const { rive, RiveComponent } = useRive(riveParams);

  // State machine control
  const setState = useCallback((state: AnimationState) => {
    if (!rive || !config.stateMachine) return;
    
    setCurrentState(state);

    // Get state machine inputs
    const inputs = rive.stateMachineInputs(config.stateMachine);
    if (!inputs) return;

    // Reset all boolean inputs
    inputs.forEach((input: StateMachineInput) => {
      if (input.type === 56) { // Boolean type
        input.value = false;
      }
    });

    // Set the appropriate input based on state
    const inputMap: Record<AnimationState, string> = {
      idle: STATE_INPUTS.IS_IDLE,
      hover: STATE_INPUTS.IS_HOVER,
      active: STATE_INPUTS.IS_ACTIVE,
      loading: STATE_INPUTS.IS_LOADING,
      success: STATE_INPUTS.IS_SUCCESS,
      error: STATE_INPUTS.IS_ERROR,
    };

    const targetInput = inputs.find((i: StateMachineInput) => i.name === inputMap[state]);
    if (targetInput && targetInput.type === 56) {
      targetInput.value = true;
    }
  }, [rive, config.stateMachine]);

  // Playback controls
  const play = useCallback(() => {
    rive?.play();
  }, [rive]);

  const pause = useCallback(() => {
    rive?.pause();
  }, [rive]);

  const reset = useCallback(() => {
    rive?.reset();
    setCurrentState('idle');
  }, [rive]);

  return {
    RiveComponent,
    rive,
    isLoaded,
    error,
    setState,
    currentState,
    play,
    pause,
    reset,
  };
}

// ============================================================================
// PRESETS - Ready-to-use configurations
// ============================================================================

export const RIVE_PRESETS = {
  neuralIcon: {
    src: RIVE_ASSETS.NEURAL_NETWORK,
    stateMachine: 'State Machine',
    autoplay: true,
    fit: Fit.Contain,
  } as RiveAnimationConfig,
  
  locationPin: {
    src: RIVE_ASSETS.LOCATION_PIN,
    stateMachine: 'State Machine',
    autoplay: true,
    fit: Fit.Contain,
  } as RiveAnimationConfig,
  
  checkSuccess: {
    src: RIVE_ASSETS.CHECK_SUCCESS,
    stateMachine: 'State Machine',
    autoplay: false,
    fit: Fit.Contain,
  } as RiveAnimationConfig,
  
  loadingSpinner: {
    src: RIVE_ASSETS.LOADING_SPINNER,
    stateMachine: 'State Machine',
    autoplay: true,
    fit: Fit.Contain,
  } as RiveAnimationConfig,
  
  pipelineNode: {
    src: RIVE_ASSETS.PIPELINE_NODE,
    stateMachine: 'State Machine',
    autoplay: true,
    fit: Fit.Contain,
  } as RiveAnimationConfig,
};

export default useRiveAnimation;
