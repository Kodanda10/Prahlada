import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

export interface TabItem {
  path: string;
  label: string;
  icon?: LucideIcon;
  protected?: boolean;
}

interface AnimatedNavTabsProps {
  tabs: TabItem[];
  activePath: string;
  isAuthenticated: boolean;
  className?: string;
}

const AnimatedNavTabs: React.FC<AnimatedNavTabsProps> = ({ tabs, activePath, isAuthenticated, className = '' }) => {
  return (
    <div className={`flex flex-wrap justify-center gap-1 p-1.5 bg-white/5 backdrop-blur-2xl border border-white/10 rounded-full shadow-2xl relative isolate ${className}`}>
      {tabs.map((tab) => {
        if (tab.protected && !isAuthenticated) return null;

        const isActive = activePath === tab.path;
        const Icon = tab.icon;

        return (
          <Link
            key={tab.path}
            to={tab.path}
            className="relative z-10"
          >
            <motion.div
              className={`flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium transition-colors duration-300 tab-button ${isActive ? 'text-[#0f172a] font-bold active' : 'text-slate-400'
                }`}
              whileHover={!isActive ? {
                scale: 1.05,
                color: '#e2e8f0',
              } : {}}
              whileTap={{ scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            >
              {/* The Fluid Background Pill - Premium Animation */}
              {isActive && (
                <motion.div
                  layoutId="active-pill"
                  className="absolute inset-0 bg-[#8BF5E6] rounded-full"
                  style={{ zIndex: -1 }}
                  initial={false}
                  animate={{
                    boxShadow: [
                      '0 0 20px rgba(139,245,230,0.4)',
                      '0 0 30px rgba(139,245,230,0.6)',
                      '0 0 20px rgba(139,245,230,0.4)',
                    ],
                  }}
                  transition={{
                    layout: { type: 'spring', stiffness: 300, damping: 30 },
                    boxShadow: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
                  }}
                />
              )}

              {/* Hover glow for inactive tabs */}
              {!isActive && (
                <motion.div
                  className="absolute inset-0 rounded-full bg-white/0"
                  style={{ zIndex: -1 }}
                  whileHover={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)',
                  }}
                  transition={{ duration: 0.2 }}
                />
              )}

              {/* Icon with hover animation */}
              {Icon && (
                <motion.span
                  whileHover={{ rotate: [0, -10, 10, 0], scale: 1.1 }}
                  transition={{ duration: 0.3 }}
                >
                  <Icon size={18} className="relative z-10" strokeWidth={isActive ? 2.5 : 2} />
                </motion.span>
              )}

              <span className="relative z-10 tracking-wide">{tab.label}</span>
            </motion.div>
          </Link>
        );
      })}
    </div>
  );
};

export default AnimatedNavTabs;

