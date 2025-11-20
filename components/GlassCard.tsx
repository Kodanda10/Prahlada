import React from 'react';
import { motion } from 'framer-motion';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  action?: React.ReactNode;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', title, action }) => {
  return (
    <motion.div 
      whileHover={{ scale: 1.01, y: -4, boxShadow: "0 20px 40px rgba(0,0,0,0.4)" }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={`relative overflow-hidden bg-white/[0.03] backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl transition-colors duration-300 hover:bg-white/[0.05] ${className}`}
    >
      {(title || action) && (
        <div className="flex justify-between items-start mb-4 border-b border-white/5 pb-3">
          {title && (
            <h3 className="text-lg font-semibold text-white tracking-wide">
              {title}
            </h3>
          )}
          {action && (
            <div>{action}</div>
          )}
        </div>
      )}
      <div className="relative h-full">
        {children}
      </div>
    </motion.div>
  );
};

export default GlassCard;