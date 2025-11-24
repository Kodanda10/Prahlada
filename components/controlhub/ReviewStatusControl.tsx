import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import ReviewStatusPanel from './ReviewStatusPanel';
import { AnimatePresence, motion } from 'framer-motion';

interface ReviewStatusControlProps {
    totalCount: number;
    approvedCount: number;
    pendingCount: number;
    skippedCount: number;
}

const ReviewStatusControl: React.FC<ReviewStatusControlProps> = (props) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div
            className="relative z-50"
            ref={containerRef}
            onMouseEnter={() => window.innerWidth >= 1024 && setIsOpen(true)}
            onMouseLeave={() => window.innerWidth >= 1024 && setIsOpen(false)}
        >
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all font-hindi border ${isOpen
                        ? 'bg-[#8BF5E6]/10 text-[#8BF5E6] border-[#8BF5E6]/30 shadow-[0_0_15px_rgba(139,245,230,0.2)]'
                        : 'bg-black/20 text-slate-300 border-white/10 hover:bg-white/5 hover:text-white'
                    }`}
            >
                <span>समीक्षा स्टेटस</span>
                <ChevronDown size={14} className={`transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute top-full right-0 mt-2 origin-top-right"
                    >
                        <ReviewStatusPanel {...props} />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ReviewStatusControl;
