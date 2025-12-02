import React, { useState, useEffect } from 'react';
import { Search, RotateCw, Sparkles, CheckCircle, Zap, Download } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import ArbitrationCard from '../components/ArbitrationCard';
import { ParsedEvent } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import NumberTicker from '../components/NumberTicker';
import { GeocodingService } from '../services/GeocodingService';
import { exportToExcel, exportToPDF } from '../utils/export';
import { apiService } from '../services/api';

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

  // Filter queue based on global state
  const [queue, setQueue] = useState<ParsedEvent[]>([]);
  const [showToast, setShowToast] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      try {
        // Fetch from live API using apiService (handles auth)
        const data = await apiService.get('/api/events');

        // Show ALL tweets for review (don't filter by status)
        setQueue(data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch events:", err);
        setError("Failed to load live data. Please check backend connection.");
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [showApproved, showPending, showSkipped]);

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

      if (result.status === "success" && result.decision?.decision === "AUTO_DEPLOY") {
        // Show success toast
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
      }

    } catch (error) {
      console.error("Error triggering engine:", error);
    }
  };

  const handleDownloadExcel = () => {
    const dataToExport = queue.map(t => ({
      ID: t.tweet_id,
      Text: t.raw_text,
      Location: t.parsed_data_v8.location?.ulb || t.parsed_data_v8.location?.village || t.parsed_data_v8.location?.district || 'N/A',
      Category: t.parsed_data_v8.event_type || 'N/A',
      Status: t.approved_by_human ? 'Approved' : 'Pending'
    }));
    exportToExcel(dataToExport, 'review_queue');
  };

  const handleDownloadPDF = () => {
    const dataToExport = queue.map(t => ({
      ID: t.tweet_id,
      Text: t.raw_text,
      Location: t.parsed_data_v8.location?.ulb || t.parsed_data_v8.location?.village || t.parsed_data_v8.location?.district || 'N/A',
      Category: t.parsed_data_v8.event_type || 'N/A',
      Status: t.approved_by_human ? 'Approved' : 'Pending'
    }));
    exportToPDF(dataToExport, 'review_queue');
  };

  if (loading) {
    return <div className="flex h-full items-center justify-center text-slate-400 font-hindi">डेटा लोड हो रहा है...</div>;
  }

  return (
    <div className="h-full relative pb-10">
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

      {/* Main Review Section - Full Width */}
      <div className="max-w-7xl mx-auto">
        <AnimatedGlassCard
          title="🧾 समीक्षा कतार (Review Queue)"
          className="flex-1 flex flex-col"
          action={<span className="px-3 py-1 bg-yellow-500/10 text-yellow-300 text-xs rounded-full border border-yellow-500/20 font-bold font-hindi">लंबित: {queue.length}</span>}
          delay={0.1}
        >
          <div className="bg-black/20 rounded-2xl border border-white/5 p-4">
            {queue.length > 0 ? (
              <ArbitrationCard
                key={queue[0].tweet_id}
                event={queue[0]}
                onApprove={handleApprove}
              />
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500 font-hindi">
                समीक्षा के लिए कोई लंबित ईवेंट नहीं है।
              </div>
            )}
          </div>
        </AnimatedGlassCard>
      </div>
    </div>
  );
};

export default Review;
