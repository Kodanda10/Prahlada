
import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Loader2 } from 'lucide-react';

// Rive-style Pulse Button for "Refresh" actions
interface PulseButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  label?: string;
  className?: string;
}

export const PulseButton: React.FC<PulseButtonProps> = ({ onClick, isLoading, label = "रिफ्रेश", className }) => {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`relative group flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-900/20 border border-cyan-500/30 text-cyan-400 overflow-hidden ${className}`}
    >
      {/* Rive-like Ripple Background */}
      <div className="absolute inset-0 bg-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <motion.div
        animate={isLoading ? { rotate: 360 } : { rotate: 0 }}
        transition={isLoading ? { repeat: Infinity, duration: 1, ease: "linear" } : {}}
      >
        <RefreshCw size={16} className={isLoading ? "text-cyan-300" : "text-cyan-400"} />
      </motion.div>
      
      <span className="relative z-10 text-xs font-bold font-hindi tracking-wide">{label}</span>
      
      {/* Pulse Glow Ring */}
      {!isLoading && (
        <span className="absolute right-2 top-2 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping opacity-75"></span>
      )}
    </motion.button>
  );
};

// Rive-style Liquid Loader
export const LiquidLoader = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4 h-64">
      <div className="relative w-16 h-16">
        {/* Outer Ring */}
        <motion.div
          className="absolute inset-0 border-4 border-[#8BF5E6]/20 rounded-full"
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2 }}
        />
        {/* Inner Spinner */}
        <motion.div
          className="absolute inset-0 border-t-4 border-[#8BF5E6] rounded-full"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        />
        {/* Center Dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 bg-[#8BF5E6] rounded-full shadow-[0_0_10px_#8BF5E6]" />
        </div>
      </div>
      <p className="text-slate-400 text-sm font-hindi animate-pulse">डेटा लोड हो रहा है...</p>
    </div>
  );
};
