import React from 'react';
import { motion } from 'framer-motion';

type ColorTheme = 'amber' | 'pink' | 'green' | 'blue' | 'purple' | 'cyan';

interface FieldDisplayProps {
    label: string;
    values: string[] | undefined | null;
    color: ColorTheme;
}

const colorClasses: Record<ColorTheme, string> = {
    amber: 'text-amber-300 bg-amber-500/20 border-amber-500/30',
    pink: 'text-pink-300 bg-pink-500/20 border-pink-500/30',
    green: 'text-green-300 bg-green-500/20 border-green-500/30',
    blue: 'text-blue-300 bg-blue-500/20 border-blue-500/30',
    purple: 'text-purple-300 bg-purple-500/20 border-purple-500/30',
    cyan: 'text-cyan-300 bg-cyan-500/20 border-cyan-500/30',
};

const FieldDisplay: React.FC<FieldDisplayProps> = ({ label, values, color }) => {
    const hasValues = values && values.length > 0;

    return (
        <div className="space-y-2">
            {/* Label */}
            <div className="flex items-center gap-1.5 text-xs text-slate-400 uppercase tracking-wider font-bold font-hindi">
                {label}
            </div>

            {/* Values or Empty State */}
            {hasValues ? (
                <div className="flex flex-wrap gap-2">
                    {values.map((value, index) => (
                        <motion.span
                            key={`${value}-${index}`}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.05 }}
                            className={`
                px-3 py-1.5 
                text-xs 
                rounded-lg 
                border 
                font-medium 
                font-hindi
                ${colorClasses[color]}
              `}
                        >
                            {value}
                        </motion.span>
                    ))}
                </div>
            ) : (
                <div className="text-xs text-slate-500 italic font-hindi bg-black/20 px-3 py-2 rounded-lg border border-white/5">
                    कोई डेटा नहीं
                </div>
            )}
        </div>
    );
};

export default FieldDisplay;
