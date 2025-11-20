
import React, { useState } from 'react';
import { Check, X, Edit2, Search, RotateCw, Sparkles, ChevronRight, MapPin, Zap, CheckCircle } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import { MOCK_REVIEW_QUEUE } from '../services/mockData';
import { ParsedEvent } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import NumberTicker from '../components/NumberTicker';

// Helper component to render location breadcrumbs
const LocationBreadcrumbs = ({ location }: { location: ParsedEvent['location_canonical'] }) => {
  if (!location) return <span className="text-red-400 text-xs font-hindi">स्थान पार्स नहीं हुआ</span>;

  const isUrban = !!location.ulb;
  
  const BreadcrumbItem = ({ label, type, isLast }: { label?: string, type: string, isLast?: boolean }) => {
    if (!label) return null;
    return (
      <div className="flex items-center">
        <div className={`flex flex-col ${isLast ? 'opacity-100' : 'opacity-60 group-hover:opacity-80 transition-opacity'}`}>
          <span className={`text-xs font-bold font-hindi ${isLast ? 'text-[#8BF5E6]' : 'text-slate-300'}`}>{label}</span>
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-hindi">{type}</span>
        </div>
        {!isLast && <ChevronRight size={14} className="text-slate-700 mx-1.5" />}
      </div>
    );
  };

  return (
    <div className="flex flex-wrap items-center gap-y-2 bg-black/30 p-3 rounded-xl border border-white/10 w-full">
      <BreadcrumbItem label={location.district} type="जिला" />
      <BreadcrumbItem label={location.constituency} type="विधानसभा" />
      
      {isUrban ? (
        <>
          <BreadcrumbItem label={location.ulb} type="निकाय" />
          <BreadcrumbItem label={location.zone} type="जोन" />
          <BreadcrumbItem label={location.ward} type="वार्ड" isLast />
        </>
      ) : (
        <>
          <BreadcrumbItem label={location.block} type="विकासखंड" />
          <BreadcrumbItem label={location.gp} type="ग्राम पंचायत" />
          <BreadcrumbItem label={location.village} type="ग्राम" isLast />
        </>
      )}
    </div>
  );
};

const ReviewCard = ({ event, onAction }: { event: ParsedEvent, onAction: (type: string) => void }) => {
  return (
    <motion.div 
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="bg-white/5 p-5 rounded-2xl border border-white/10 mb-4 hover:bg-white/10 transition-colors group relative shadow-lg"
    >
      {/* Tweet Text */}
      <p className="text-sm text-slate-200 mb-4 leading-relaxed font-hindi bg-black/20 p-3 rounded-lg border border-white/5">
        "{event.clean_text}"
      </p>

      {/* Parsed Metadata */}
      <div className="space-y-4 mb-5">
        
        {/* Event Type & Confidence */}
        <div className="flex items-center justify-between">
           <div className="flex gap-2">
             {event.event_type.map(type => (
               <span key={type} className="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-lg border border-purple-500/30 font-medium font-hindi">
                 {type}
               </span>
             ))}
           </div>
           <div className="flex items-center gap-2 text-xs bg-black/30 px-3 py-1 rounded-full border border-white/10">
             <span className="text-slate-400 font-hindi">AI आत्मविश्वास:</span>
             <span className={`font-bold ${event.confidence_scores.faiss > 0.9 ? 'text-green-400' : 'text-yellow-400'}`}>
               {(event.confidence_scores.faiss * 100).toFixed(0)}%
             </span>
           </div>
        </div>

        {/* Hierarchical Location */}
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2 uppercase tracking-wider font-bold font-hindi">
            <MapPin size={12} className="text-[#8BF5E6]" /> अनुमानित स्थान पदानुक्रम
          </div>
          <LocationBreadcrumbs location={event.location_canonical} />
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <div className="flex gap-3">
          <button 
            onClick={() => onAction('approve')}
            className="flex-1 bg-green-600/20 text-green-400 py-2.5 rounded-xl hover:bg-green-600/30 transition-all text-xs border border-green-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi"
          >
            <Check size={16} /> स्वीकृत करें
          </button>
          <button className="flex-1 bg-blue-600/20 text-blue-400 py-2.5 rounded-xl hover:bg-blue-600/30 transition-all text-xs border border-blue-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi">
            <Edit2 size={16} /> संपादित करें
          </button>
          <button className="flex-1 bg-red-600/20 text-red-400 py-2.5 rounded-xl hover:bg-red-600/30 transition-all text-xs border border-red-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi">
            <X size={16} /> अस्वीकार करें
          </button>
        </div>
        
        {/* Micro-Hint for Dynamic Learning */}
        <div className="text-center pt-1">
           <span className="text-[10px] text-slate-500 flex items-center justify-center gap-1.5 opacity-60 group-hover:opacity-100 transition-opacity font-hindi">
             <Sparkles size={10} className="text-yellow-500" /> आपके सुधार AI को भविष्य में बेहतर बनाते हैं (डायनामिक लर्निंग)
           </span>
        </div>
      </div>
    </motion.div>
  );
};

const DynamicLearningPanel = () => {
  return (
    <div className="mt-6 pt-6 border-t border-white/10">
       <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 font-hindi">
            <Zap size={16} className="text-yellow-400 fill-yellow-400"/> डायनामिक लर्निंग (Dynamic Learning)
          </h3>
          <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-[10px] rounded-full border border-blue-500/30 font-medium animate-pulse font-hindi">
             सक्रिय (Labs)
          </span>
       </div>
       
       <div className="grid grid-cols-3 gap-3 mb-5">
          <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
             <NumberTicker value={128} className="text-xl font-bold text-white block" />
             <div className="text-[10px] text-slate-500 mt-1 font-hindi">कुल समीक्षा (सीखने में)</div>
          </div>
          <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
             <NumberTicker value={14} className="text-xl font-bold text-white block" />
             <div className="text-[10px] text-slate-500 mt-1 font-hindi">शिक्षण फाइलें</div>
          </div>
          <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
             <div className="text-xs font-bold text-green-400 mt-2 mb-1 font-hindi">अभी</div>
             <div className="text-[10px] text-slate-500 font-hindi">अंतिम रन</div>
          </div>
       </div>

       <div className="bg-black/20 rounded-xl p-4 border border-white/5">
          <h4 className="text-[10px] text-slate-400 mb-3 uppercase tracking-wider font-bold font-hindi">मानव-सत्यापित स्थान मैपिंग</h4>
          <ul className="space-y-2 text-xs">
             <li className="flex justify-between text-slate-300 bg-white/5 p-2 rounded-lg border border-white/5 font-hindi">
                <span>रायपुर → Raipur</span>
                <span className="text-green-400 font-mono">१२ बार सत्यापित</span>
             </li>
             <li className="flex justify-between text-slate-300 bg-white/5 p-2 rounded-lg border border-white/5 font-hindi">
                <span>अंबिकापुर → Ambikapur</span>
                <span className="text-green-400 font-mono">०७ बार सत्यापित</span>
             </li>
          </ul>
       </div>
    </div>
  )
}

const Review = () => {
  const [queue, setQueue] = useState<ParsedEvent[]>(MOCK_REVIEW_QUEUE);
  const [showToast, setShowToast] = useState(false);

  const handleAction = (type: string) => {
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full relative pb-10">
      
      {/* Success Toast */}
      <AnimatePresence>
        {showToast && (
          <motion.div 
            initial={{ opacity: 0, y: 50, x: '-50%', scale: 0.9 }}
            animate={{ opacity: 1, y: 0, x: '-50%', scale: 1 }}
            exit={{ opacity: 0, y: 50, x: '-50%', scale: 0.9 }}
            className="fixed bottom-12 left-1/2 z-50 flex items-center gap-3 px-6 py-3 bg-[#065f46] text-white rounded-full shadow-[0_0_30px_rgba(5,150,105,0.5)] border border-white/10 backdrop-blur-xl"
          >
            <CheckCircle size={20} className="text-[#8BF5E6]" />
            <span className="text-sm font-medium font-hindi">सुधार सुरक्षित — इस उदाहरण को सीखने के लिए जोड़ दिया गया।</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Left Column: Main Review Queue */}
      <div className="lg:col-span-1 flex flex-col gap-6">
        <AnimatedGlassCard 
          title="🧾 समीक्षा कतार" 
          className="flex-1 flex flex-col min-h-[600px]" 
          action={<span className="px-3 py-1 bg-yellow-500/10 text-yellow-300 text-xs rounded-full border border-yellow-500/20 font-bold font-hindi">लंबित: {queue.length}</span>}
          delay={0.1}
        >
          <div className="flex-1 bg-black/20 rounded-2xl border border-white/5 p-1 overflow-y-auto scrollbar-none">
             <div className="p-2 space-y-2">
               {queue.map(event => (
                 <ReviewCard key={event.tweet_id} event={event} onAction={handleAction} />
               ))}
               
               {queue.length === 0 && (
                 <div className="h-64 flex items-center justify-center text-slate-500 font-hindi">
                   समीक्षा के लिए कोई लंबित ईवेंट नहीं है।
                 </div>
               )}
             </div>
          </div>
          
          <DynamicLearningPanel />
        </AnimatedGlassCard>
      </div>

      {/* Right Column: AI Assistant & Tools */}
      <div className="flex flex-col gap-6">
        
        {/* AI Assistant Status */}
        <AnimatedGlassCard title="🤖 AI समीक्षा सहायक" className="min-h-[220px]" delay={0.2}>
          <div className="h-full flex flex-col items-center justify-center text-center p-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center mb-4 shadow-[0_0_30px_rgba(124,58,237,0.3)] animate-pulse border border-white/20">
                <Sparkles className="text-white" size={32} />
            </div>
            <h3 className="text-white font-bold text-lg mb-2 font-hindi">वेक्टर सर्च सक्रिय</h3>
            <p className="text-sm text-slate-400 max-w-sm leading-relaxed font-hindi">
              FAISS का उपयोग करके १४,०००+ अनुक्रमित भू-इकाइयों के साथ आने वाले ट्वीट्स की तुलना की जा रही है।
            </p>
          </div>
        </AnimatedGlassCard>

        {/* Semantic Search Tool */}
        <AnimatedGlassCard title="🔍 सिमेंटिक सर्च (Semantic Search)" className="min-h-[220px]" delay={0.3}>
          <div className="relative">
            <input 
              type="text" 
              placeholder="समान ईवेंट खोजें..." 
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-sm text-white focus:border-[#8BF5E6] outline-none transition-all focus:bg-black/30 font-hindi placeholder:text-slate-500"
            />
            <Search className="absolute left-4 top-4 text-slate-500" size={20} />
          </div>
          <div className="mt-6">
              <span className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-3 block font-hindi">हाल की खोजें:</span>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs px-3 py-1.5 bg-white/5 rounded-lg text-cyan-400 cursor-pointer hover:bg-white/10 transition-colors border border-white/5 font-hindi">"खरसिया में पीएम आवास"</span>
                <span className="text-xs px-3 py-1.5 bg-white/5 rounded-lg text-cyan-400 cursor-pointer hover:bg-white/10 transition-colors border border-white/5 font-hindi">"उद्घाटन समारोह"</span>
              </div>
          </div>
        </AnimatedGlassCard>

        {/* Accuracy Metrics */}
        <AnimatedGlassCard title="🧠 सटीकता मेट्रिक्स" className="min-h-[220px]" delay={0.4}>
          <div className="space-y-6">
            <div className="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/5">
              <span className="text-sm text-slate-300 font-medium font-hindi">ऑटो-मैच दर</span>
              <span className="font-bold text-green-400 text-xl">८२.५%</span>
            </div>
            <button className="w-full py-3 rounded-xl bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 hover:text-white transition-all text-sm flex items-center justify-center gap-2 font-medium group font-hindi">
              <RotateCw size={16} className="group-hover:rotate-180 transition-transform duration-500" /> पुनः इंडेक्स करें (Re-Index)
            </button>
          </div>
        </AnimatedGlassCard>

      </div>
    </div>
  );
};

export default Review;
