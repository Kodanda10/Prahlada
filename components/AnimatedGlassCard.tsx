
import React from 'react';
import { motion, Variants, HTMLMotionProps } from 'framer-motion';

interface GlassCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  title?: string;
  action?: React.ReactNode;
  delay?: number;
  // Allow manual override of variants
  variants?: Variants;
}

// Standard variants compatible with staggerChildren
const defaultVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.98
  },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 15,
      duration: 0.5
    }
  }
};

const AnimatedGlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  title,
  action,
  delay = 0,
  variants,
  ...rest
}) => {
  return (
    <motion.div
      // Use passed variants or defaults.
      // IMPORTANT: If no parent orchestrator, we set initial/animate here to ensure visibility.
      variants={variants || defaultVariants}
      initial={variants ? undefined : "hidden"}
      animate={variants ? undefined : "show"}
      transition={!variants ? { delay } : undefined}
      whileHover={{
        scale: 1.02,
        y: -5,
        boxShadow: "0 20px 40px rgba(0,0,0,0.4)",
        borderColor: "rgba(139, 245, 230, 0.4)"
      }}
      className={`relative overflow-hidden bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-6 shadow-xl transition-colors duration-300 hover:bg-white/[0.06] ${className}`}
      {...rest}
    >
      {/* Rive-like Ambient Glow Effect on Hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#8BF5E6]/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      {/* Top Shine Highlight */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50" />

      {(title || action) && (
        <div className="flex justify-between items-start mb-4 border-b border-white/5 pb-3 relative z-10">
          {title && (
            <h3 className="text-lg font-semibold text-white tracking-wide font-hindi drop-shadow-sm">
              {title}
            </h3>
          )}
          {action && (
            <div className="flex items-center">{action}</div>
          )}
        </div>
      )}
      <div className="relative z-10 h-full">
        {children}
      </div>
    </motion.div>
  );
};

export default AnimatedGlassCard;
