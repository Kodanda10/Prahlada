/**
 * usePremiumAnimations.ts
 * 
 * Global animation system for Project Dhruv.
 * Provides world-class animations for all interactive elements.
 * 
 * Features:
 * - Button animations (hover, tap, loading, success)
 * - Icon animations (idle, hover, active states)
 * - Navbar sliding selection indicator
 * - Entrance animations for cards/sections
 * - Background ambient animations
 * - Cursor following effects
 * - Microinteractions
 */

import { useCallback, useEffect, useState, useRef } from 'react';
import { MotionProps, Variants, useMotionValue, useSpring, useTransform } from 'framer-motion';

// ============================================================================
// ANIMATION PRESETS
// ============================================================================

/** Spring physics presets */
export const SPRING = {
    snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
    bouncy: { type: 'spring' as const, stiffness: 300, damping: 15 },
    smooth: { type: 'spring' as const, stiffness: 200, damping: 30 },
    gentle: { type: 'spring' as const, stiffness: 100, damping: 20 },
};

/** Easing presets */
export const EASE = {
    smooth: [0.4, 0, 0.2, 1] as const,
    bouncy: [0.68, -0.55, 0.265, 1.55] as const,
    sharp: [0.4, 0, 0.6, 1] as const,
};

// ============================================================================
// BUTTON ANIMATIONS
// ============================================================================

export const buttonVariants: Variants = {
    initial: { scale: 1 },
    hover: {
        scale: 1.05,
        boxShadow: '0 0 20px rgba(99, 102, 241, 0.3)',
        transition: SPRING.snappy,
    },
    tap: {
        scale: 0.95,
        transition: { duration: 0.1 },
    },
    loading: {
        scale: [1, 1.02, 1],
        transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
    },
    success: {
        scale: [1, 1.1, 1],
        boxShadow: ['0 0 0px rgba(16, 185, 129, 0)', '0 0 30px rgba(16, 185, 129, 0.5)', '0 0 10px rgba(16, 185, 129, 0.2)'],
        transition: { duration: 0.5 },
    },
};

export const iconButtonVariants: Variants = {
    initial: { scale: 1, rotate: 0 },
    hover: {
        scale: 1.15,
        rotate: 5,
        transition: SPRING.bouncy,
    },
    tap: { scale: 0.9 },
};

// ============================================================================
// ICON ANIMATIONS
// ============================================================================

export const iconVariants: Variants = {
    idle: { scale: 1, rotate: 0 },
    hover: { scale: 1.1, rotate: [0, -5, 5, 0], transition: { duration: 0.3 } },
    active: { scale: 1.2, transition: SPRING.snappy },
    loading: { rotate: 360, transition: { duration: 1, repeat: Infinity, ease: 'linear' } },
    success: { scale: [1, 1.3, 1], transition: { duration: 0.4 } },
};

// ============================================================================
// CARD / SECTION ANIMATIONS
// ============================================================================

export const cardVariants: Variants = {
    initial: { opacity: 0, y: 20, scale: 0.95 },
    animate: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { duration: 0.5, ease: EASE.smooth },
    },
    exit: {
        opacity: 0,
        y: -20,
        scale: 0.95,
        transition: { duration: 0.3 },
    },
    hover: {
        y: -5,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(99, 102, 241, 0.1)',
        transition: SPRING.smooth,
    },
};

export const glassCardVariants: Variants = {
    initial: { opacity: 0, backdropFilter: 'blur(0px)' },
    animate: {
        opacity: 1,
        backdropFilter: 'blur(20px)',
        transition: { duration: 0.6 },
    },
    hover: {
        backdropFilter: 'blur(30px)',
        boxShadow: '0 0 40px rgba(99, 102, 241, 0.15)',
    },
};

// ============================================================================
// NAVBAR ANIMATIONS
// ============================================================================

export const navItemVariants: Variants = {
    initial: { opacity: 0.7 },
    hover: {
        opacity: 1,
        scale: 1.05,
        transition: { duration: 0.2 },
    },
    active: {
        opacity: 1,
        scale: 1,
    },
};

/** Sliding selection indicator for navbar */
export const useNavbarIndicator = (activeIndex: number, itemWidths: number[]) => {
    const x = useMotionValue(0);
    const width = useMotionValue(100);

    useEffect(() => {
        let offset = 0;
        for (let i = 0; i < activeIndex; i++) {
            offset += itemWidths[i] || 100;
        }
        x.set(offset);
        width.set(itemWidths[activeIndex] || 100);
    }, [activeIndex, itemWidths, x, width]);

    return { x, width };
};

// ============================================================================
// ENTRANCE ANIMATIONS
// ============================================================================

export const staggerContainer: Variants = {
    initial: {},
    animate: {
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.1,
        },
    },
};

export const fadeInUp: Variants = {
    initial: { opacity: 0, y: 30 },
    animate: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5, ease: EASE.smooth },
    },
};

export const fadeInScale: Variants = {
    initial: { opacity: 0, scale: 0.8 },
    animate: {
        opacity: 1,
        scale: 1,
        transition: SPRING.bouncy,
    },
};

export const slideInFromLeft: Variants = {
    initial: { opacity: 0, x: -50 },
    animate: { opacity: 1, x: 0, transition: { duration: 0.5 } },
};

export const slideInFromRight: Variants = {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0, transition: { duration: 0.5 } },
};

// ============================================================================
// BACKGROUND ANIMATIONS
// ============================================================================

export const ambientGlowVariants: Variants = {
    initial: { opacity: 0.3 },
    animate: {
        opacity: [0.3, 0.6, 0.3],
        scale: [1, 1.1, 1],
        transition: {
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut',
        },
    },
};

export const floatingVariants: Variants = {
    initial: { y: 0 },
    animate: {
        y: [-10, 10, -10],
        transition: {
            duration: 6,
            repeat: Infinity,
            ease: 'easeInOut',
        },
    },
};

// ============================================================================
// CURSOR FOLLOWING EFFECT
// ============================================================================

export const useCursorFollow = (intensity: number = 1) => {
    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const springConfig = { damping: 25, stiffness: 150 };
    const springX = useSpring(x, springConfig);
    const springY = useSpring(y, springConfig);

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        x.set((e.clientX - centerX) * 0.1 * intensity);
        y.set((e.clientY - centerY) * 0.1 * intensity);
    }, [x, y, intensity]);

    const handleMouseLeave = useCallback(() => {
        x.set(0);
        y.set(0);
    }, [x, y]);

    return {
        style: { x: springX, y: springY },
        handlers: { onMouseMove: handleMouseMove, onMouseLeave: handleMouseLeave },
    };
};

// ============================================================================
// 3D TILT EFFECT
// ============================================================================

export const use3DTilt = (intensity: number = 10) => {
    const [tilt, setTilt] = useState({ x: 0, y: 0 });

    const handleMouseMove = useCallback((e: React.MouseEvent<HTMLElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width - 0.5) * intensity;
        const y = ((e.clientY - rect.top) / rect.height - 0.5) * -intensity;
        setTilt({ x, y });
    }, [intensity]);

    const handleMouseLeave = useCallback(() => {
        setTilt({ x: 0, y: 0 });
    }, []);

    return {
        style: {
            rotateX: tilt.y,
            rotateY: tilt.x,
            transformPerspective: 1000,
        },
        handlers: {
            onMouseMove: handleMouseMove,
            onMouseLeave: handleMouseLeave,
        },
    };
};

// ============================================================================
// MICROINTERACTIONS
// ============================================================================

export const pulseVariants: Variants = {
    initial: { scale: 1 },
    pulse: {
        scale: [1, 1.05, 1],
        transition: { duration: 0.3 },
    },
};

export const shakeVariants: Variants = {
    initial: { x: 0 },
    shake: {
        x: [-5, 5, -5, 5, 0],
        transition: { duration: 0.4 },
    },
};

export const successBounce: Variants = {
    initial: { scale: 0, opacity: 0 },
    animate: {
        scale: [0, 1.2, 1],
        opacity: 1,
        transition: SPRING.bouncy,
    },
};

// ============================================================================
// LOADING ANIMATIONS
// ============================================================================

export const spinnerVariants: Variants = {
    animate: {
        rotate: 360,
        transition: { duration: 1, repeat: Infinity, ease: 'linear' },
    },
};

export const dotsVariants: Variants = {
    animate: (i: number) => ({
        scale: [1, 1.2, 1],
        opacity: [0.5, 1, 0.5],
        transition: {
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.15,
        },
    }),
};

export const skeletonVariants: Variants = {
    animate: {
        backgroundPosition: ['200% 0', '-200% 0'],
        transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
        },
    },
};

// ============================================================================
// HOOK: GET ANIMATION PROPS
// ============================================================================

type AnimationType = 'button' | 'iconButton' | 'icon' | 'card' | 'glassCard' | 'navItem';

export const useAnimationProps = (type: AnimationType): MotionProps => {
    const variants = {
        button: buttonVariants,
        iconButton: iconButtonVariants,
        icon: iconVariants,
        card: cardVariants,
        glassCard: glassCardVariants,
        navItem: navItemVariants,
    }[type];

    return {
        variants,
        initial: 'initial',
        animate: 'animate',
        whileHover: 'hover',
        whileTap: 'tap',
    };
};

export default {
    // Presets
    SPRING,
    EASE,
    // Variants
    buttonVariants,
    iconButtonVariants,
    iconVariants,
    cardVariants,
    glassCardVariants,
    navItemVariants,
    staggerContainer,
    fadeInUp,
    fadeInScale,
    slideInFromLeft,
    slideInFromRight,
    ambientGlowVariants,
    floatingVariants,
    pulseVariants,
    shakeVariants,
    successBounce,
    spinnerVariants,
    dotsVariants,
    skeletonVariants,
    // Hooks
    useCursorFollow,
    use3DTilt,
    useNavbarIndicator,
    useAnimationProps,
};
