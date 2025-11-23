import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Twitter, ExternalLink, Image as ImageIcon } from 'lucide-react';

interface TweetPreviewModalProps {
  isOpen: boolean;
  tweetId: string;
  text: string;
  x: number;
  y: number;
}

const TweetPreviewModal: React.FC<TweetPreviewModalProps> = ({ isOpen, tweetId, text, x, y }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 10 }}
          style={{ 
            position: 'fixed', 
            left: x, 
            top: y,
            zIndex: 100 
          }}
          className="w-80 pointer-events-none"
        >
          <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-[0_0_40px_rgba(0,0,0,0.5)] relative overflow-hidden">
            {/* Liquid Glass Effect */}
            <div className="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />
            
            {/* Header */}
            <div className="flex items-center gap-3 mb-3">
               <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                  <Twitter size={14} className="text-white fill-white" />
               </div>
               <div>
                  <div className="text-xs font-bold text-white">Twitter User</div>
                  <div className="text-[10px] text-slate-400">@username</div>
               </div>
               <ExternalLink size={12} className="ml-auto text-slate-500" />
            </div>

            {/* Content */}
            <p className="text-xs text-slate-200 leading-relaxed font-hindi mb-3">
               {text}
            </p>

            {/* Media Placeholder */}
            <div className="w-full h-32 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center justify-center gap-2 text-slate-500">
               <ImageIcon size={20} />
               <span className="text-[10px]">मीडिया पूर्वावलोकन (Media Preview)</span>
            </div>
            
            {/* Footer */}
            <div className="mt-3 pt-3 border-t border-white/5 flex justify-between text-[10px] text-slate-500">
               <span>10:30 AM · Nov 24, 2025</span>
               <span>Twitter for Android</span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default TweetPreviewModal;
