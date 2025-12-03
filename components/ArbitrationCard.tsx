import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, ExternalLink, MapPin, BrainCircuit, X, RotateCcw } from 'lucide-react';
import { apiService } from '../services/api';
import AskAISidebar from './AskAISidebar';
import DecisionConsole from './decision/DecisionConsole';
import { ParsedEvent } from '../types';
import Chip from './Chip';

interface ArbitrationCardProps {
    event: ParsedEvent;
    onApprove: (excludeFromAnalytics: boolean) => void;
}

interface ComparisonData {
    tweet_id: string;
    raw_text: string;
    comparison: Record<string, any>;
}

const LocationBreadcrumbs = ({ location }: { location: ParsedEvent['parsed_data_v8']['location'] }) => {
    if (!location) return <span className="text-red-400 text-xs font-mono">NO_LOCATION_DATA</span>;

    const isUrban = !!location.ulb;

    const BreadcrumbItem = ({ label, type, isLast }: { label?: string | null, type: string, isLast?: boolean }) => {
        if (!label) return null;
        return (
            <div className="flex items-center">
                <div className="flex flex-col">
                    <span className={`text-xs font-bold font-hindi ${isLast ? 'text-emerald-400' : 'text-slate-300'}`}>{label}</span>
                    <span className="text-[9px] text-slate-500 uppercase tracking-wider font-mono">{type}</span>
                </div>
                {!isLast && <span className="text-slate-700 mx-2">/</span>}
            </div>
        );
    };

    return (
        <div className="flex flex-wrap items-center gap-y-2 w-full">
            <BreadcrumbItem label={location.district} type="DISTRICT" />
            <BreadcrumbItem label={location.assembly} type="ASSEMBLY" />

            {isUrban ? (
                <>
                    <BreadcrumbItem label={location.ulb} type="ULB" />
                    <BreadcrumbItem label={location.zone} type="ZONE" />
                    <BreadcrumbItem label={location.ward} type="WARD" isLast />
                </>
            ) : (
                <>
                    <BreadcrumbItem label={location.block} type="BLOCK" />
                    <BreadcrumbItem label={location.gp} type="PANCHAYAT" />
                    <BreadcrumbItem label={location.village} type="VILLAGE" isLast />
                </>
            )}
        </div>
    );
};

const ArbitrationCard: React.FC<ArbitrationCardProps> = ({ event, onApprove }) => {
    const [comparison, setComparison] = useState<ComparisonData | null>(null);
    const [loading, setLoading] = useState(true);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
    const [isTablet, setIsTablet] = useState(window.innerWidth >= 768 && window.innerWidth < 1024);
    const [includeInAnalytics, setIncludeInAnalytics] = useState(true);

    // New State for Decision Console
    const [finalDecisionData, setFinalDecisionData] = useState<Record<string, any>>({});

    // Fetch comparison data
    useEffect(() => {
        const fetchComparison = async () => {
            try {
                // MOCK DATA FOR UI VERIFICATION (Commented out)
                /*
                const MOCK_DATA = {
                    tweet_id: event.tweet_id,
                    raw_text: event.raw_text,
                    comparison: {
                        event_type: { parser: { value: "बैठक" }, llm: { value: "समीक्षा" }, conflict: true },
                        people: { parser: { value: ["Raman Singh"] }, llm: { value: ["CM"] }, conflict: false },
                        schemes: { parser: { value: [] }, llm: { value: ["Kisan Nyay Yojana"] }, conflict: false },
                        communities: { parser: { value: ["Farmers"] }, llm: { value: [] }, conflict: false },
                        location: { parser: { value: { district: "Raipur", state: "Chhattisgarh" } }, llm: { value: "Raipur" }, conflict: false }
                    }
                };
                setComparison(MOCK_DATA);
                setLoading(false);
                */

                const response: any = await apiService.get(`/api/review/compare?tweet_id=${event.tweet_id}`);
                setComparison(response);
                setLoading(false);
            } catch (error) {
                console.error('Failed to fetch comparison:', error);
                setLoading(false);
            }
        };

        fetchComparison();
    }, [event.tweet_id]);

    // Handle responsive layout
    useEffect(() => {
        const handleResize = () => {
            const width = window.innerWidth;
            setIsMobile(width < 768);
            setIsTablet(width >= 768 && width < 1024);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const handleSkip = async () => {
        try {
            await apiService.post('/api/events/skip', {
                tweet_id: event.tweet_id
            });
            onApprove(false);
        } catch (error) {
            console.error('Skip failed:', error);
        }
    };

    const handleApprove = async () => {
        if (!comparison) return;

        // Construct final payload from finalDecisionData
        // We need to handle the structure expected by the backend
        // Backend expects final_data and feedback

        const final_data = { ...finalDecisionData };

        // Handle Location: Backend expects an object, but our UI might have array of objects or strings
        // If it's an array, take the first one as primary
        if (Array.isArray(final_data.location) && final_data.location.length > 0) {
            final_data.location = final_data.location[0];
        } else if (Array.isArray(final_data.location) && final_data.location.length === 0) {
            final_data.location = null;
        }

        // Feedback logic is simplified here as we are now "editing" directly
        // We can infer feedback by checking if final matches parser or LLM
        const feedback: Record<string, any> = {};

        // TODO: Implement detailed feedback logic if needed by backend
        // For now, we send the final data which is the most important part

        try {
            await apiService.post('/api/events/approve', {
                tweet_id: event.tweet_id,
                final_data,
                feedback,
                exclude_from_analytics: !includeInAnalytics
            });

            onApprove(false);
        } catch (error) {
            console.error('Approval failed:', error);
        }
    };

    if (loading || !comparison) {
        return (
            <div className="bg-white/5 p-5 rounded-2xl border border-white/10 mb-4">
                <div className="animate-pulse font-hindi text-slate-400">तुलना लोड हो रही है... (Loading comparison)</div>
            </div>
        );
    }

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12 relative max-w-6xl mx-auto"
        >
            {/* Tweet Header - Minimalist */}
            <div className="mb-8 pl-1">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700 font-mono tracking-wider">
                            {event.tweet_id}
                        </span>
                        <span className="text-xs text-slate-500 font-mono">
                            {new Date(event.created_at).toLocaleString()}
                        </span>
                    </div>
                    <a
                        href={`https://twitter.com/i/web/status/${event.tweet_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-500 hover:text-blue-400 transition-colors"
                    >
                        <ExternalLink size={14} />
                    </a>
                </div>
                <p className="text-lg leading-relaxed text-slate-200 font-hindi whitespace-pre-wrap break-words border-l-2 border-slate-700 pl-6 py-1">
                    {comparison?.raw_text || event.raw_text}
                </p>
            </div>

            {/* Metadata Grid - Compact Summary */}
            <div className="grid grid-cols-1 gap-6 mb-10">
                {/* Location Summary */}
                <div className="bg-black/20 p-5 rounded-xl border border-white/5">
                    <div className="flex items-center gap-2 text-[10px] text-slate-500 mb-4 uppercase tracking-widest font-bold font-hindi">
                        <MapPin size={12} className="text-emerald-500" /> लोकेशन मैपिंग (Current)
                    </div>
                    <LocationBreadcrumbs location={event.parsed_data_v8.location} />
                </div>
            </div>

            {/* Main Decision Console */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Console Column */}
                <div className="lg:col-span-2">
                    <DecisionConsole
                        event={event}
                        comparison={comparison}
                        onFinalDataChange={setFinalDecisionData}
                    />
                </div>

                {/* Ask AI Sidebar */}
                <div className={`${isTablet ? 'collapsed' : ''} ${isMobile ? 'hidden' : ''}`}>
                    <AskAISidebar tweetId={event.tweet_id} />
                </div>
            </div>

            {/* Approval Footer */}
            <div className="mt-10 pt-6 border-t border-white/5 flex items-center justify-between">
                <label className="flex items-center gap-3 cursor-pointer group select-none">
                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${includeInAnalytics ? 'bg-emerald-500/20 border-emerald-500' : 'border-slate-700 group-hover:border-slate-500 bg-black/20'}`}>
                        {includeInAnalytics && <Check size={10} className="text-emerald-500" />}
                    </div>
                    <span className={`text-xs font-hindi font-medium transition-colors ${includeInAnalytics ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-400'}`}>
                        Include in Analytics
                    </span>
                    <input
                        type="checkbox"
                        className="hidden"
                        checked={includeInAnalytics}
                        onChange={(e) => setIncludeInAnalytics(e.target.checked)}
                    />
                </label>

                <div className="flex gap-4">
                    <button
                        onClick={handleSkip}
                        className="px-6 py-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all text-xs font-bold uppercase tracking-wider font-hindi flex items-center gap-2"
                    >
                        Skip
                    </button>

                    <button
                        data-testid="approve-btn"
                        onClick={handleApprove}
                        className="px-8 py-2.5 rounded-lg bg-emerald-500 text-black hover:bg-emerald-400 transition-all text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)]"
                    >
                        <Check size={14} /> Approve
                    </button>
                </div>
            </div>
        </motion.div>
    );
};

export default ArbitrationCard;
