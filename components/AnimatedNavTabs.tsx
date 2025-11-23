import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

export interface TabItem {
  path: string;
  label: string;
  icon: LucideIcon;
  protected?: boolean;
}

interface AnimatedNavTabsProps {
  tabs: TabItem[];
  activePath: string;
  isAuthenticated: boolean;
}

const AnimatedNavTabs: React.FC<AnimatedNavTabsProps> = ({ tabs, activePath, isAuthenticated }) => {
  return (
    <div className="flex flex-wrap justify-center gap-1 p-1.5 bg-white/5 backdrop-blur-2xl border border-white/10 rounded-full shadow-2xl relative isolate">
      {tabs.map((tab) => {
        if (tab.protected && !isAuthenticated) return null;
        
        const isActive = activePath === tab.path;

        return (
          <Link
            key={tab.path}
            to={tab.path}
            className={`relative z-10 flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium transition-colors duration-300 ${
              isActive ? 'text-[#0f172a] font-bold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {/* The Fluid Background Pill - Rive/ProtoPie Feel */}
            {isActive && (
              <motion.div
                layoutId="active-pill"
                className="absolute inset-0 bg-[#8BF5E6] rounded-full shadow-[0_0_20px_rgba(139,245,230,0.4)]"
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                style={{ zIndex: -1 }}
              />
            )}
            
            <tab.icon size={18} className="relative z-10" strokeWidth={isActive ? 2.5 : 2} />
            <span className="relative z-10 tracking-wide">{tab.label}</span>
          </Link>
        );
      })}
    </div>
  );
};

export default AnimatedNavTabs;
