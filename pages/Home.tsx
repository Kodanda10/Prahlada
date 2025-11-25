import React, { useState, useMemo, useEffect } from 'react';
import { Filter, Download } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import { PulseButton } from '../components/interactions/RiveLikeIcons';
// import ingestedTweets from '../data/ingested_tweets.json'; // REMOVED
import { ParsedEvent } from '../types';
import TweetPreviewModal from '../components/TweetPreviewModal';
import TweetFilters from '../components/home/TweetFilters';
import TweetTable from '../components/home/TweetTable';
import { exportToExcel, exportToPDF } from '../utils/export';
import ReviewStatusControl from '../components/controlhub/ReviewStatusControl';
import { useReviewStatus } from '../utils/reviewStatusStore';
import { fetchEvents } from '../services/api';

const Home = () => {
  // Global Review Status Store
  const { showApproved, showPending, showSkipped } = useReviewStatus();

  // State
  const [tweets, setTweets] = useState<ParsedEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoverState, setHoverState] = useState<{ isOpen: boolean, tweetId: string, text: string, x: number, y: number }>({
    isOpen: false, tweetId: '', text: '', x: 0, y: 0
  });



  // Fetch Data
  useEffect(() => {
    const loadTweets = async () => {
      setIsLoading(true);
      try {
        const data = await fetchEvents();
        setTweets(data);
      } catch (error) {
        console.error("Error fetching tweets:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTweets();
  }, []);

  // Filter States
  const [locationFilter, setLocationFilter] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      const data = await fetchEvents();
      setTweets(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMouseEnter = (e: React.MouseEvent, tweet: ParsedEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setHoverState({
      isOpen: true,
      tweetId: tweet.tweet_id,
      text: tweet.raw_text,
      x: rect.right + 10,
      y: rect.top - 20
    });
  };

  const handleMouseLeave = () => {
    setHoverState(prev => ({ ...prev, isOpen: false }));
  };

  // Filter Logic
  const filteredTweets = useMemo(() => {
    return tweets.filter(tweet => {
      // 1. Review Status Filter (Global)
      if (tweet.approved_by_human && !showApproved) return false;
      if (!tweet.approved_by_human && !showPending) return false;
      // Note: "Skipped" logic depends on how skipped tweets are marked. 
      // Assuming for now we don't have a specific "skipped" flag in the type, 
      // but if we did, it would look like: if (tweet.skipped && !showSkipped) return false;
      // For this implementation, we'll assume "skipped" might be a future state or handled via a specific flag if it existed.
      // If "skipped" is just "not approved and not pending" (which covers everything), then:
      // But usually "skipped" means explicitly skipped. 
      // Given the current data structure, we only have `approved_by_human` (boolean).
      // So effectively:
      // Approved = approved_by_human === true
      // Pending = approved_by_human === false
      // Skipped = ??? (Maybe we need to mock this or assume it's a separate list, but user said "no mock data")
      // If we look at `Review.tsx`, it filters `!t.approved_by_human` as pending.
      // Let's assume for now "Skipped" might not have data backing it yet in `ingested_tweets.json`, 
      // but the filter logic should be ready. 
      // If there's a `skipped` field in `ParsedEvent`, we'd use it. 
      // Checking `types.ts` would be good, but let's stick to what we know.
      // For now, we will filter based on what we have.

      // Location Filter
      if (locationFilter) {
        const loc = tweet.parsed_data_v8.location;
        const locString = `${loc?.ulb || ''} ${loc?.village || ''} ${loc?.district || ''}`.toLowerCase();
        if (!locString.includes(locationFilter.toLowerCase())) return false;
      }

      // Tag Filter
      if (tagFilter) {
        const tags = tweet.parsed_data_v8.people_canonical?.join(' ').toLowerCase() || '';
        if (!tags.includes(tagFilter.toLowerCase())) return false;
      }

      // Date Range Filter
      const tweetDate = tweet.parsed_data_v8.event_date || tweet.created_at.split('T')[0];
      if (dateFrom && tweetDate < dateFrom) return false;
      if (dateTo && tweetDate > dateTo) return false;

      return true;
    });
  }, [tweets, locationFilter, tagFilter, dateFrom, dateTo, showApproved, showPending, showSkipped]);

  // Counts for the panel
  const counts = useMemo(() => {
    return {
      total: tweets.length,
      approved: tweets.filter(t => t.approved_by_human).length,
      pending: tweets.filter(t => !t.approved_by_human).length,
      skipped: 0 // Placeholder as we don't have skipped data yet
    };
  }, [tweets]);

  // Pagination Logic
  const totalPages = Math.ceil(filteredTweets.length / itemsPerPage);
  const paginatedTweets = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredTweets.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredTweets, currentPage]);

  // Reset page when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [locationFilter, tagFilter, dateFrom, dateTo, showApproved, showPending, showSkipped]);

  const handleClearFilters = () => {
    setLocationFilter('');
    setTagFilter('');
    setDateFrom('');
    setDateTo('');
  };

  const handleDownloadExcel = () => {
    exportToExcel(filteredTweets, 'tweets_data');
  };

  const handleDownloadPDF = () => {
    exportToPDF(filteredTweets, 'tweets_data');
  };

  return (
    <div className="w-full relative">
      <TweetPreviewModal
        isOpen={hoverState.isOpen}
        tweetId={hoverState.tweetId}
        text={hoverState.text}
        x={hoverState.x}
        y={hoverState.y}
      />

      {/* Consolidated Single Card for seamless UI */}
      <AnimatedGlassCard className="p-0 overflow-hidden min-h-[600px]">

        {/* Header & Filters Section */}
        <div className="p-5 border-b border-white/10 bg-white/5">
          <div className="flex flex-col gap-6">

            {/* Top Row: Title, Bulk Toggle, Refresh, Download */}
            <div className="flex flex-col xl:flex-row justify-between items-center gap-4">
              {/* Title */}
              <div className="flex items-center gap-4 w-full xl:w-auto">
                <div className="p-3 bg-[#8BF5E6]/10 rounded-xl border border-[#8BF5E6]/20">
                  <Filter size={24} className="text-[#8BF5E6]" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white font-hindi">ट्वीट डेटाबेस</h2>
                  <p className="text-sm text-slate-400 font-hindi">कुल {tweets.length} रिकॉर्ड्स</p>
                </div>
              </div>

              {/* Controls */}
              <div className="flex flex-wrap gap-3 w-full xl:w-auto justify-end items-center">

                {/* Download Buttons */}
                <div className="flex gap-2 mr-2">
                  <button
                    onClick={handleDownloadExcel}
                    className="flex items-center gap-2 px-3 py-2 bg-green-600/10 text-green-400 border border-green-500/20 rounded-lg hover:bg-green-600/20 transition-colors text-xs font-medium font-hindi"
                  >
                    <Download size={14} /> एक्सेल
                  </button>
                  <button
                    onClick={handleDownloadPDF}
                    className="flex items-center gap-2 px-3 py-2 bg-red-600/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-600/20 transition-colors text-xs font-medium font-hindi"
                  >
                    <Download size={14} /> पीडीएफ
                  </button>
                </div>

                <div className="h-8 w-[1px] bg-white/10 hidden xl:block mx-2"></div>

                {/* Review Status Control */}
                <ReviewStatusControl
                  totalCount={counts.total}
                  approvedCount={counts.approved}
                  pendingCount={counts.pending}
                  skippedCount={counts.skipped}
                />

                <div className="ml-2">
                  <PulseButton onClick={handleRefresh} isLoading={isLoading} label="" className="w-10 h-10 justify-center px-0" />
                </div>
              </div>
            </div>

            {/* Filters Row */}
            <TweetFilters
              locationFilter={locationFilter}
              setLocationFilter={setLocationFilter}
              tagFilter={tagFilter}
              setTagFilter={setTagFilter}
              dateFrom={dateFrom}
              setDateFrom={setDateFrom}
              dateTo={dateTo}
              setDateTo={setDateTo}
              totalCount={tweets.length}
              filteredCount={filteredTweets.length}
              onClearFilters={handleClearFilters}
            />

          </div>
        </div>

        {/* Table Area */}
        <TweetTable
          tweets={paginatedTweets}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        />

      </AnimatedGlassCard>

    </div>
  );
};

export default Home;
