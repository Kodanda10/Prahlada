import React, { useState, useEffect, useMemo } from 'react';
import { Search, RotateCw, Sparkles, CheckCircle, Zap, Download, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import ArbitrationCard from '../components/ArbitrationCard';
import { ParsedEvent } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import NumberTicker from '../components/NumberTicker';
import { GeocodingService } from '../services/GeocodingService';
import { exportToExcel, exportToPDF } from '../utils/export';
import { apiService } from '../services/api';

import { useReviewStatus } from '../utils/reviewStatusStore';

import DhruvVerticalNexus from '../components/DhruvVerticalNexus';

const Review = () => {
  // Global Review Status Store
  const { showApproved, showPending, showSkipped } = useReviewStatus();

  const [allEvents, setAllEvents] = useState<ParsedEvent[]>([]);
  const [showToast, setShowToast] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'pending' | 'approved'>('pending');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      try {
        // MOCK EVENTS FOR UI VERIFICATION (Commented out for production)
        /*
        const MOCK_EVENTS: any[] = [
          {
            tweet_id: "12345",
            raw_text: "माननीय मुख्यमंत्री जी ने आज रायपुर में किसान सम्मान निधि योजना के तहत किसानों को राशि वितरित की। #Farmers #Raipur",
            created_at: new Date().toISOString(),
            review_status: "pending",
            parsed_data_v8: {
              location: { district: "Raipur", state: "Chhattisgarh" },
              word_buckets: ["Test Bucket"],
              event_type: "Scheme Distribution",
              people_canonical: ["CM"],
              schemes_mentioned: ["Kisan Samman Nidhi"],
              communities: ["Farmers"]
            }
          }
        ];
        setAllEvents(MOCK_EVENTS);
        setError(null);
        */

        // Fetch from live API using apiService (handles auth)
        const data = await apiService.get('/api/events') as ParsedEvent[];
        setAllEvents(data);
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

  // Derived lists
  const pendingEvents = useMemo(() =>
    allEvents.filter(e => e.review_status !== 'approved' && e.review_status !== 'skipped'),
    [allEvents]);

  const approvedEvents = useMemo(() =>
    allEvents.filter(e => e.review_status === 'approved'),
    [allEvents]);

  const currentEvent = pendingEvents[currentIndex];

  const handleApprove = async (excludeFromAnalytics: boolean) => {
    if (!currentEvent) return;

    // Optimistic Update
    const updatedEvent = { ...currentEvent, review_status: 'approved' as const, approved_by_human: true };
    setAllEvents(prev => prev.map(e => e.tweet_id === currentEvent.tweet_id ? updatedEvent : e));

    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);

    // Ensure index stays valid
    if (currentIndex >= pendingEvents.length - 1) {
      setCurrentIndex(Math.max(0, pendingEvents.length - 2));
    }

    // Background Geocoding
    if (!currentEvent.parsed_data_v8.location?.lat) {
      const locationStr = GeocodingService.getLocationString(currentEvent.parsed_data_v8.location);
      if (locationStr) {
        GeocodingService.geocode(locationStr).then(res => {
          if (res) console.log(`Geocoded ${locationStr} to`, res);
        });
      }
    }

    // API Call
    try {
      await apiService.approveTweet(currentEvent.tweet_id);
    } catch (error) {
      console.error("Failed to approve tweet:", error);
      // Revert optimistic update if needed (omitted for brevity)
    }
  };

  const handleNext = () => {
    if (currentIndex < pendingEvents.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const handleSkip = async () => {
    if (!currentEvent) return;

    // Optimistic Update
    const updatedEvent = { ...currentEvent, review_status: 'skipped' as const };
    setAllEvents(prev => prev.map(e => e.tweet_id === currentEvent.tweet_id ? updatedEvent : e));

    // Ensure index stays valid
    if (currentIndex >= pendingEvents.length - 1) {
      setCurrentIndex(Math.max(0, pendingEvents.length - 2));
    }
  };

  const learningStats = {
    total_reviews: approvedEvents.length,
    learning_files: Math.floor(approvedEvents.length / 10), // Mock logic
    last_run: "Just now"
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-16 h-16 border-4 border-[#8BF5E6]/30 border-t-[#8BF5E6] rounded-full animate-spin mb-4"></div>
        <p className="text-slate-400 font-hindi animate-pulse">समीक्षा डेटा लोड हो रहा है...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-xl text-center max-w-md">
          <h3 className="text-red-400 font-bold mb-2">Error Loading Data</h3>
          <p className="text-slate-400 text-sm mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-140px)]"
    >
      {/* Left Sidebar - Stats & Filters */}
      <div className="lg:col-span-1 space-y-6 overflow-y-auto pr-2 custom-scrollbar">
        <AnimatedGlassCard className="p-5 border-l-4 border-l-[#8BF5E6]">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2 font-hindi">
            समीक्षा स्थिति
          </h2>

          <div className="space-y-3">
            <button
              onClick={() => setViewMode('pending')}
              className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all ${viewMode === 'pending'
                ? 'bg-[#8BF5E6]/10 border-[#8BF5E6]/30 text-white shadow-[0_0_15px_rgba(139,245,230,0.1)]'
                : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10'
                }`}
            >
              <span className="font-hindi">लंबित (Pending)</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${viewMode === 'pending' ? 'bg-[#8BF5E6]/20 text-[#8BF5E6]' : 'bg-black/30'
                }`}>
                {pendingEvents.length}
              </span>
            </button>

            <button
              onClick={() => setViewMode('approved')}
              className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all ${viewMode === 'approved'
                ? 'bg-green-500/10 border-green-500/30 text-white shadow-[0_0_15px_rgba(34,197,94,0.1)]'
                : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10'
                }`}
            >
              <span className="font-hindi">स्वीकृत (Approved)</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${viewMode === 'approved' ? 'bg-green-500/20 text-green-400' : 'bg-black/30'
                }`}>
                {approvedEvents.length}
              </span>
            </button>
          </div>
        </AnimatedGlassCard>

        {/* Dhruv Vertical Nexus - The Kundalini Reactor */}
        <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
          <DhruvVerticalNexus
            currentStage={showToast ? 7 : 6}
          />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="lg:col-span-3 flex flex-col h-full overflow-hidden">
        {viewMode === 'pending' ? (
          pendingEvents.length > 0 ? (
            <div className="flex flex-col h-full">
              {/* Navigation Controls */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <button
                    onClick={handlePrev}
                    disabled={currentIndex === 0}
                    className={`p-2 rounded-lg border transition-all ${currentIndex === 0
                      ? 'bg-white/5 border-white/5 text-slate-600 cursor-not-allowed'
                      : 'bg-white/10 border-white/10 text-white hover:bg-white/20'
                      }`}
                  >
                    <ChevronLeft size={20} />
                  </button>
                  <span className="text-sm text-slate-400 font-mono">
                    {currentIndex + 1} / {pendingEvents.length}
                  </span>
                  <button
                    onClick={handleNext}
                    disabled={currentIndex === pendingEvents.length - 1}
                    className={`p-2 rounded-lg border transition-all ${currentIndex === pendingEvents.length - 1
                      ? 'bg-white/5 border-white/5 text-slate-600 cursor-not-allowed'
                      : 'bg-white/10 border-white/10 text-white hover:bg-white/20'
                      }`}
                  >
                    <ChevronRight size={20} />
                  </button>
                </div>

                <div className="text-xs text-slate-500 font-hindi">
                  समीक्षा के लिए {pendingEvents.length} ट्वीट शेष
                </div>
              </div>

              {/* Arbitration Card */}
              <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 pb-20">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentEvent.tweet_id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ArbitrationCard
                      event={currentEvent}
                      onApprove={handleApprove}
                    />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <CheckCircle size={48} className="text-green-500 mb-4 opacity-50" />
              <p className="text-lg font-hindi">सभी लंबित ट्वीट्स की समीक्षा पूर्ण हो चुकी है!</p>
              <p className="text-sm opacity-60 mt-2">नये ट्वीट्स का इंतज़ार करें...</p>
            </div>
          )
        ) : (
          <div className="h-full overflow-y-auto custom-scrollbar">
            <AnimatedGlassCard className="p-6">
              <h2 className="text-xl font-bold text-white mb-6 font-hindi flex items-center gap-2">
                <CheckCircle className="text-green-400" /> स्वीकृत ट्वीट्स (Approved Tweets)
              </h2>

              {approvedEvents.length === 0 ? (
                <div className="text-center py-10 text-slate-500">
                  कोई स्वीकृत ट्वीट नहीं है।
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-white/10 text-slate-400 text-xs uppercase tracking-wider">
                        <th className="p-3">ID</th>
                        <th className="p-3">Text</th>
                        <th className="p-3">Approved At</th>
                        <th className="p-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm text-slate-300">
                      {approvedEvents.map(event => (
                        <tr key={event.tweet_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                          <td className="p-3 font-mono text-xs text-[#8BF5E6]">{event.tweet_id}</td>
                          <td className="p-3 max-w-md truncate">{event.raw_text}</td>
                          <td className="p-3 text-slate-500">
                            {event.reviewed_at ? new Date(event.reviewed_at).toLocaleString() : '-'}
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs border border-green-500/30">
                              Approved
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </AnimatedGlassCard>
          </div>
        )}
      </div >

      {/* Toast Notification */}
      <AnimatePresence>
        {
          showToast && (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="fixed bottom-8 right-8 bg-green-500 text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 z-50"
            >
              <CheckCircle size={20} />
              <span className="font-medium">समीक्षा सफलतापूर्वक सहेजी गई!</span>
            </motion.div>
          )
        }
      </AnimatePresence >
    </motion.div >
  );
};

export default Review;
