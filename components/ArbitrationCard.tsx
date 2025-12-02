import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, ExternalLink, Sparkles, MapPin, BrainCircuit, Activity, X, SkipForward } from 'lucide-react';
import { apiService } from '../services/api';
import AskAISidebar from './AskAISidebar';
import ComparisonGrid from './ComparisonGrid';
import { ParsedEvent } from '../types';

interface ArbitrationCardProps {
    event: ParsedEvent;
    onApprove: (excludeFromAnalytics: boolean) => void;
}

interface FieldComparison {
    parser: { value: any; confidence: number; source?: string };
    llm: { value: any; confidence: number; source?: string };
    conflict: boolean;
}

interface ComparisonData {
    tweet_id: string;
    raw_text: string;
    comparison: Record<string, FieldComparison>;
}

const FIELD_ORDER = [
    'event_type',
    'people',
    'schemes',
    'communities',
    'location'
];

const LocationBreadcrumbs = ({ location }: { location: ParsedEvent['parsed_data_v8']['location'] }) => {
    if (!location) return <span className="text-red-400 text-xs font-hindi">स्थान पार्स नहीं हुआ</span>;

    const isUrban = !!location.ulb;

    const BreadcrumbItem = ({ label, type, isLast }: { label?: string | null, type: string, isLast?: boolean }) => {
        if (!label) return null;
        return (
            <div className="flex items-center">
                <div className={`flex flex-col ${isLast ? 'opacity-100' : 'opacity-60 group-hover:opacity-80 transition-opacity'}`}>
                    <span className={`text-xs font-bold font-hindi ${isLast ? 'text-[#8BF5E6]' : 'text-slate-300'}`}>{label}</span>
                    <span className="text-[9px] text-slate-500 uppercase tracking-wider font-hindi">{type}</span>
                </div>
                {!isLast && <span className="text-slate-700 mx-1.5">›</span>}
            </div>
        );
    };

    return (
        <div className="flex flex-wrap items-center gap-y-2 bg-black/30 p-3 rounded-xl border border-white/10 w-full">
            <BreadcrumbItem label={location.district} type="जिला" />
            <BreadcrumbItem label={location.assembly} type="विधानसभा" />

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

const ArbitrationCard: React.FC<ArbitrationCardProps> = ({ event, onApprove }) => {
    const [comparison, setComparison] = useState<ComparisonData | null>(null);
    const [selectedValues, setSelectedValues] = useState<Record<string, 'parser' | 'llm'>>({});
    const [loading, setLoading] = useState(true);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
    const [isTablet, setIsTablet] = useState(window.innerWidth >= 768 && window.innerWidth < 1024);
    const [activeTab, setActiveTab] = useState<'parser' | 'llm'>('parser');
    const [includeInAnalytics, setIncludeInAnalytics] = useState(true);
    const [manualValues, setManualValues] = useState<Record<string, any>>({});

    // Fetch comparison data
    useEffect(() => {
        const fetchComparison = async () => {
            try {
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

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const focusedField = document.activeElement?.getAttribute('data-field');
            if (!focusedField) return;

            if (e.key === '1') {
                setSelectedValues(prev => ({ ...prev, [focusedField]: 'parser' }));
            } else if (e.key === '2') {
                setSelectedValues(prev => ({ ...prev, [focusedField]: 'llm' }));
            } else if (e.key === 'Enter' && e.metaKey) {
                handleApprove();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [selectedValues]);

    const handleFieldSelection = (field: string, source: 'parser' | 'llm') => {
        setSelectedValues(prev => ({ ...prev, [field]: source }));
    };

    const handleManualEdit = (field: string, value: any) => {
        setManualValues(prev => ({ ...prev, [field]: value }));
    };

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

        // Build final_data and feedback from selections
        const final_data: Record<string, any> = {};
        const feedback: Record<string, any> = {};

        FIELD_ORDER.forEach(field => {
            const selected = selectedValues[field] || 'parser'; // Default to parser
            const fieldComp = comparison.comparison[field];

            if (fieldComp) {
                // Determine base value (Manual > Selection)
                let value;
                if (manualValues[field] !== undefined) {
                    value = manualValues[field];
                } else {
                    value = selected === 'parser' ? fieldComp.parser.value : fieldComp.llm.value;
                }

                // Filter removed tags if array
                if (Array.isArray(value)) {
                    value = value.filter((tag: string) => !removedTags.has(tag));
                }

                final_data[field] = value;

                feedback[field] = {
                    choice: selected === 'parser' ? 'parser_win' : 'llm_win',
                    disagreement_strength: fieldComp.conflict ? 1.0 : 0.0
                };
            }
        });

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

    // State for removed tags
    const [removedTags, setRemovedTags] = useState<Set<string>>(new Set());

    const handleRemoveTag = (tag: string) => {
        setRemovedTags(prev => {
            const next = new Set(prev);
            next.add(tag);
            return next;
        });
    };

    // Helper to get current values based on selection
    const getCurrentValue = (field: string): string[] => {
        if (!comparison) {
            // Fallback to event data if comparison not loaded
            if (field === 'people') return event.parsed_data_v8.people_canonical || [];
            if (field === 'schemes') return event.parsed_data_v8.schemes_mentioned || [];
            if (field === 'communities') {
                return [
                    ...(event.parsed_data_v8.target_groups || []),
                    ...(event.parsed_data_v8.communities || []),
                    ...(event.parsed_data_v8.organizations || [])
                ];
            }
            return [];
        }

        let value;
        if (manualValues[field] !== undefined) {
            value = manualValues[field];
        } else {
            const source = selectedValues[field] || 'parser';
            const fieldComp = comparison.comparison[field];
            if (!fieldComp) return [];
            value = source === 'parser' ? fieldComp.parser.value : fieldComp.llm.value;
        }

        return Array.isArray(value) ? value : [];
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
            className="bg-white/5 p-6 rounded-2xl border border-white/10 mb-6 relative shadow-xl backdrop-blur-sm"
        >
            {/* Tweet Header */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400 font-mono tracking-wider">ID: {event.tweet_id}</span>
                    <a
                        href={`https://twitter.com/i/web/status/${event.tweet_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 transition-colors p-1 hover:bg-blue-500/10 rounded-lg"
                    >
                        <ExternalLink size={16} />
                    </a>
                </div>
                <p className="text-base leading-relaxed text-slate-200 font-hindi bg-black/30 p-4 rounded-xl border border-white/5 shadow-inner whitespace-pre-wrap break-words">
                    {comparison.raw_text}
                </p>
            </div>

            {/* Rich Metadata Section (Breadcrumbs & Word Bucket) */}
            <div className="mb-8 space-y-6">
                {/* Hierarchical Location */}
                <div data-testid="location-breadcrumbs-section" className="bg-slate-900/40 p-5 rounded-xl border border-white/10 backdrop-blur-md">
                    <div className="flex items-center gap-2 text-xs text-slate-400 mb-4 uppercase tracking-wider font-bold font-hindi">
                        <MapPin size={14} className="text-emerald-400" /> अनुमानित स्थान (Location Hierarchy)
                    </div>
                    <LocationBreadcrumbs location={event.parsed_data_v8.location} />
                </div>

                {/* Word Bucket */}
                <div className="bg-slate-900/40 p-5 rounded-xl border border-white/10 backdrop-blur-md" data-testid="word-bucket-section">
                    <div className="flex items-center gap-2 text-xs text-slate-400 mb-4 font-hindi uppercase tracking-wider font-bold">
                        <BrainCircuit size={16} className="text-amber-400" />
                        <span>वर्ड बकेट (Cognitive Tags)</span>
                    </div>

                    <div className="flex flex-col gap-4">
                        {/* Locations (Read-only for now as it's complex) */}
                        {event.parsed_data_v8.location && (
                            <div className="flex items-start gap-3">
                                <div className="mt-1.5 p-1.5 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                                    <MapPin size={14} className="text-emerald-400" />
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        event.parsed_data_v8.location.district,
                                        event.parsed_data_v8.location.ulb,
                                        event.parsed_data_v8.location.village,
                                        event.parsed_data_v8.location.zone
                                    ].filter(Boolean).map((loc, i) => (
                                        <span key={`loc-${i}`} className="px-3 py-1.5 bg-emerald-500/5 text-emerald-300 text-sm rounded-lg border border-emerald-500/20 font-hindi font-medium hover:bg-emerald-500/10 transition-colors cursor-default shadow-sm">
                                            {loc}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* People */}
                        {(() => {
                            const people = getCurrentValue('people').filter(p => !removedTags.has(p));
                            if (people.length === 0) return null;
                            return (
                                <div className="flex items-start gap-3">
                                    <div className="mt-1.5 p-1.5 bg-blue-500/10 rounded-lg border border-blue-500/20">
                                        <Activity size={14} className="text-blue-400" />
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {people.map((person, i) => (
                                            <span key={`person-${i}`} className="group flex items-center gap-2 px-3 py-1.5 bg-blue-500/5 text-blue-300 text-sm rounded-lg border border-blue-500/20 font-hindi font-medium hover:bg-blue-500/10 transition-colors cursor-default shadow-sm">
                                                {person}
                                                <button
                                                    onClick={() => handleRemoveTag(person)}
                                                    className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-blue-500/20 rounded-full transition-all text-blue-400"
                                                >
                                                    <X size={12} />
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })()}

                        {/* Schemes */}
                        {(() => {
                            const schemes = getCurrentValue('schemes').filter(s => !removedTags.has(s));
                            if (schemes.length === 0) return null;
                            return (
                                <div className="flex items-start gap-3">
                                    <div className="mt-1.5 p-1.5 bg-purple-500/10 rounded-lg border border-purple-500/20">
                                        <Sparkles size={14} className="text-purple-400" />
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {schemes.map((scheme, i) => (
                                            <span key={`scheme-${i}`} className="group flex items-center gap-2 px-3 py-1.5 bg-purple-500/5 text-purple-300 text-sm rounded-lg border border-purple-500/20 font-hindi font-medium hover:bg-purple-500/10 transition-colors cursor-default shadow-sm">
                                                {scheme}
                                                <button
                                                    onClick={() => handleRemoveTag(scheme)}
                                                    className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-purple-500/20 rounded-full transition-all text-purple-400"
                                                >
                                                    <X size={12} />
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })()}

                        {/* Other Entities (Communities, etc.) */}
                        {(() => {
                            // Combine communities and others for display if needed, or just use communities
                            const communities = getCurrentValue('communities').filter(c => !removedTags.has(c));
                            if (communities.length === 0) return null;
                            return (
                                <div className="flex items-start gap-3">
                                    <div className="mt-1.5 p-1.5 bg-slate-500/10 rounded-lg border border-slate-500/20">
                                        <div className="w-3.5 h-3.5 rounded-full bg-slate-400/50" />
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {communities.map((item, i) => (
                                            <span key={`other-${i}`} className="group flex items-center gap-2 px-3 py-1.5 bg-slate-700/30 text-slate-300 text-sm rounded-lg border border-slate-600/30 font-hindi font-medium hover:bg-slate-700/50 transition-colors cursor-default shadow-sm">
                                                {item}
                                                <button
                                                    onClick={() => handleRemoveTag(item)}
                                                    className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-slate-500/20 rounded-full transition-all text-slate-400"
                                                >
                                                    <X size={12} />
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })()}
                    </div>
                </div>
            </div>

            {/* Mobile: Tabs */}
            {isMobile && (
                <div className="flex gap-2 mb-4">
                    <button
                        role="tab"
                        aria-label="Parser"
                        onClick={() => setActiveTab('parser')}
                        className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all font-hindi ${activeTab === 'parser'
                            ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-600/50 shadow-lg shadow-indigo-900/20'
                            : 'bg-white/5 text-slate-400 hover:bg-white/10'
                            }`}
                    >
                        🤖 पार्सर (Parser)
                    </button>
                    <button
                        role="tab"
                        aria-label="LLM"
                        onClick={() => setActiveTab('llm')}
                        className={`flex-1 py-3 rounded-xl text-sm font-bold transition-all font-hindi ${activeTab === 'llm'
                            ? 'bg-pink-600/30 text-pink-300 border border-pink-600/50 shadow-lg shadow-pink-900/20'
                            : 'bg-white/5 text-slate-400 hover:bg-white/10'
                            }`}
                    >
                        🧠 बौद्धिक इंजन (LLM)
                    </button>
                </div>
            )}

            {/* Comparison Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Parser + LLM Columns */}
                <div className="lg:col-span-2">
                    <ComparisonGrid
                        comparison={comparison.comparison}
                        selectedValues={selectedValues}
                        onFieldSelect={handleFieldSelection}
                        onManualEdit={handleManualEdit}
                        isMobile={isMobile}
                        activeTab={activeTab}
                    />
                </div>

                {/* Ask AI Sidebar */}
                <div className={`${isTablet ? 'collapsed' : ''} ${isMobile ? 'hidden' : ''}`}>
                    <AskAISidebar tweetId={event.tweet_id} />
                </div>
            </div>

            {/* Approval Footer */}
            <div className="mt-6 pt-6 border-t border-white/10">
                <div className="flex items-center justify-between mb-4 px-1">
                    <label className="flex items-center gap-2 cursor-pointer group select-none">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${includeInAnalytics ? 'bg-emerald-500/20 border-emerald-500' : 'border-slate-600 group-hover:border-slate-500 bg-black/20'}`}>
                            {includeInAnalytics && <Check size={10} className="text-emerald-500" />}
                        </div>
                        <span className={`text-xs font-hindi font-medium transition-colors ${includeInAnalytics ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-300'}`}>
                            एनालिटिक्स में शामिल करें (Include in Analytics)
                        </span>
                        <input
                            type="checkbox"
                            className="hidden"
                            checked={includeInAnalytics}
                            onChange={(e) => setIncludeInAnalytics(e.target.checked)}
                        />
                    </label>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={handleSkip}
                        className="px-5 py-3 rounded-xl bg-white/5 text-slate-400 hover:bg-white/10 hover:text-slate-200 transition-all text-xs font-bold font-hindi flex items-center gap-2 border border-white/5 hover:border-white/10 backdrop-blur-sm"
                    >
                        <SkipForward size={16} /> छोड़ें (Skip)
                    </button>

                    <button
                        data-testid="approve-btn"
                        onClick={handleApprove}
                        className="flex-1 bg-green-600/20 text-green-400 py-3 rounded-xl hover:bg-green-600/30 transition-all text-sm border border-green-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi shadow-lg shadow-green-900/20 backdrop-blur-sm"
                    >
                        <Check size={18} /> स्वीकृत करें (Approve)
                    </button>
                </div>

                <div className="text-center pt-4">
                    <span className="text-[10px] text-slate-500 flex items-center justify-center gap-1.5 opacity-60 font-hindi">
                        <Sparkles size={10} className="text-yellow-500" />
                        आपके सुधार AI को भविष्य में बेहतर बनाते हैं
                    </span>
                </div>
            </div>
        </motion.div>
    );
};

export default ArbitrationCard;
