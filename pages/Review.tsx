import React, { useState, useEffect } from 'react';
import { Search, RotateCw, Sparkles, CheckCircle, Zap, Download } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import ReviewCard from '../components/ReviewCard';
import { ParsedEvent } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import NumberTicker from '../components/NumberTicker';
import { GeocodingService } from '../services/GeocodingService';
import { exportToExcel, exportToPDF } from '../utils/export';
import { apiService, fetchEvents } from '../services/api';
import SectionWrapper from '../components/SectionWrapper';

import { useReviewStatus } from '../utils/reviewStatusStore';

interface DynamicLearningPanelProps {
  stats: {
    total_reviews: number;
    learning_files: number;
    last_run: string;
  }
}

const DynamicLearningPanel: React.FC<DynamicLearningPanelProps> = ({ stats }) => {
  return (
    <div className="mt-6 pt-6 border-t border-white/10">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 font-hindi">
          <Zap size={16} className="text-yellow-400 fill-yellow-400" /> डायनामिक लर्निंग (Dynamic Learning)
        </h3>
        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-[10px] rounded-full border border-blue-500/30 font-medium animate-pulse font-hindi">
          सक्रिय (Labs)
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
          <NumberTicker value={stats.total_reviews} className="text-xl font-bold text-white block" />
          <div className="text-[10px] text-slate-500 mt-1 font-hindi">कुल समीक्षा (सीखने में)</div>
        </div>
        <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
          <NumberTicker value={stats.learning_files} className="text-xl font-bold text-white block" />
          <div className="text-[10px] text-slate-500 mt-1 font-hindi">शिक्षण फाइलें</div>
        </div>
        <div className="bg-black/20 p-3 rounded-xl border border-white/5 text-center">
          <div className="text-xs font-bold text-green-400 mt-2 mb-1 font-hindi">{stats.last_run}</div>
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
  // Global Review Status Store
  const { showApproved, showPending, showSkipped } = useReviewStatus();
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Filter queue based on global state
  const [queue, setQueue] = useState<ParsedEvent[]>([]);
  const [showToast, setShowToast] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadEvents = async () => {
      setLoading(true);
      try {
        // Fetch from live API using the service (handles Auth)
        const data = await fetchEvents();

        // Filter based on global store
        const filteredTweets = data.filter(t => {
          // Check review_status from API
          const status = t.review_status as string;
          const isApproved = status === 'approved' || status === 'SUCCESS';

          // For now, let's assume 'pending' is default
          const isPending = !isApproved;

          if (isApproved && showApproved) return true;
          if (isPending && showPending) return true;
          return false;
        });

        setQueue(filteredTweets);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching events:', err);
        if (err.message && err.message.includes('401')) {
          logout();
          navigate('/login');
        } else {
          setError(err.message || 'Failed to load review queue');
        }
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, [showApproved, showPending, showSkipped, logout, navigate]);

  const handleApprove = async (excludeFromAnalytics: boolean) => {
    const currentTweet = queue[0];
    if (!currentTweet) return;

    // 1. Optimistic UI update: Remove from queue immediately
    const newQueue = queue.slice(1);
    setQueue(newQueue);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);

    // 2. Geocode if missing location (Background)
    if (!currentTweet.parsed_data_v8.location?.lat) {
      const locationStr = GeocodingService.getLocationString(currentTweet.parsed_data_v8.location);
      if (locationStr) {
        GeocodingService.geocode(locationStr).then(res => {
          if (res) {
            console.log(`Geocoded ${locationStr} to`, res);
            // In a real app, we would save this to the backend
          }
        });
      }
    }

    // 3. API Call
    console.log('Approved tweet:', currentTweet.tweet_id, 'Exclude:', excludeFromAnalytics);
    try {
      await apiService.approveTweet(currentTweet.tweet_id);
    } catch (error) {
      console.error("Failed to approve tweet:", error);
      // Ideally rollback UI state here, but for now just log
    }
  };

  const handleEdit = () => {
    console.log('Edit requested');
    // Implement edit modal logic here
  };

  const handleSave = async (newData: any) => {
    const currentTweet = queue[0];
    if (!currentTweet) return;

    console.log("Triggering Cognitive Engine with correction:", newData);

    // Optimistically update local state so the UI reflects changes immediately
    const updatedTweet = { ...currentTweet, parsed_data_v8: newData };
    const newQueue = [updatedTweet, ...queue.slice(1)];
    setQueue(newQueue);

    try {
      const response = await fetch('/api/cognitive/correct', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tweet_id: currentTweet.tweet_id,
          text: currentTweet.raw_text,
          old_data: currentTweet.parsed_data_v8,
          correction: newData
        }),
      });

      const result = await response.json();
      console.log("Cognitive Engine Result:", result);

      if (result.status === "success") {
        // Show success toast
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
      }

    } catch (error) {
      console.error("Error triggering engine:", error);
    }
  };

  // ... (rest of the code)

  // Performance: Only render the first 50 items to avoid DOM overload
  const visibleQueue = queue.slice(0, 50);

  return (
    <div className="h-full relative pb-10 space-y-6">
      {/* ... (header code) ... */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* ... (toast code) ... */}

        {/* Left Column: Main Review Queue */}
        <SectionWrapper id="review_queue">
          <div className="lg:col-span-1 flex flex-col gap-6">
            <AnimatedGlassCard
              title="🧾 समीक्षा कतार"
              className="flex-1 flex flex-col min-h-[600px]"
              action={<span className="px-3 py-1 bg-yellow-500/10 text-yellow-300 text-xs rounded-full border border-yellow-500/20 font-bold font-hindi">लंबित: {queue.length} (दिखा रहा है: {visibleQueue.length})</span>}
              delay={0.1}
            >
              <div className="flex-1 bg-black/20 rounded-2xl border border-white/5 p-1 overflow-y-auto scrollbar-none">
                <div className="p-2 space-y-2">
                  {visibleQueue.length > 0 ? (
                    <ReviewCard
                      key={visibleQueue[0].tweet_id}
                      event={visibleQueue[0]}
                      onApprove={handleApprove}
                      onEdit={handleEdit}
                      onSave={handleSave}
                    />
                  ) : (
                    <div className="h-64 flex items-center justify-center text-slate-500 font-hindi">
                      समीक्षा के लिए कोई लंबित ईवेंट नहीं है।
                    </div>
                  )}
                </div>
              </div>

              <DynamicLearningPanel stats={{
                total_reviews: queue.length, // Placeholder: Use real stats if available
                learning_files: 1, // Placeholder
                last_run: 'अभी'
              }} />
            </AnimatedGlassCard>
          </div>
        </SectionWrapper>

        {/* Right Column: AI Assistant & Tools */}
        <div className="flex flex-col gap-6">

          {/* AI Assistant Status */}
          <SectionWrapper id="review_ai_assistant">
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
          </SectionWrapper>

          {/* Semantic Search Tool */}
          <SectionWrapper id="review_semantic_search">
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
          </SectionWrapper>

          {/* Accuracy Metrics */}
          <SectionWrapper id="review_metrics">
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
          </SectionWrapper>

        </div>
      </div>
    </div>
  );
};

export default Review;
