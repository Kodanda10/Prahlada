import React from 'react';
import { MapPin, ExternalLink, ChevronLeft, ChevronRight } from 'lucide-react';
import { ParsedEvent } from '../../types';

interface TweetTableProps {
    tweets: ParsedEvent[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    onMouseEnter: (e: React.MouseEvent, tweet: ParsedEvent) => void;
    onMouseLeave: () => void;
}

const TweetTable: React.FC<TweetTableProps> = ({
    tweets,
    currentPage,
    totalPages,
    onPageChange,
    onMouseEnter,
    onMouseLeave,
}) => {

    // Helper to format date in Hindi: "Monday, 24 November 2025"
    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('hi-IN', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            }).format(date);
        } catch (e) {
            return dateString;
        }
    };

    // Pagination Logic
    const renderPagination = () => {
        if (totalPages <= 1) return null;

        const pages = [];
        // Simple pagination logic: show current, prev, next, first, last
        // For now, let's show a simplified version
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);

        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }

        for (let i = startPage; i <= endPage; i++) {
            pages.push(
                <button
                    key={i}
                    onClick={() => onPageChange(i)}
                    className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-medium transition-colors font-hindi ${currentPage === i
                        ? 'bg-[#8BF5E6] text-[#0f172a] font-bold'
                        : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
                        }`}
                >
                    {i}
                </button>
            );
        }

        return (
            <div className="flex items-center justify-center gap-2 mt-6 pb-2">
                <button
                    onClick={() => onPageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="p-2 rounded-lg bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronLeft size={16} />
                </button>

                {startPage > 1 && (
                    <>
                        <button onClick={() => onPageChange(1)} className="w-8 h-8 flex items-center justify-center rounded-lg bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white text-xs font-medium transition-colors font-hindi">1</button>
                        {startPage > 2 && <span className="text-slate-600">...</span>}
                    </>
                )}

                {pages}

                {endPage < totalPages && (
                    <>
                        {endPage < totalPages - 1 && <span className="text-slate-600">...</span>}
                        <button onClick={() => onPageChange(totalPages)} className="w-8 h-8 flex items-center justify-center rounded-lg bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white text-xs font-medium transition-colors font-hindi">{totalPages}</button>
                    </>
                )}

                <button
                    onClick={() => onPageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="p-2 rounded-lg bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <ChevronRight size={16} />
                </button>
            </div>
        );
    };

    return (
        <div className="flex flex-col">
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-white/5 text-slate-400 uppercase text-xs border-b border-white/5">
                        <tr>
                            <th className="px-6 py-5 font-medium tracking-wider font-hindi text-center whitespace-nowrap">दिन / दिनांक</th>
                            <th className="px-6 py-5 font-medium tracking-wider font-hindi text-center whitespace-nowrap">📍 स्थान</th>
                            <th className="px-6 py-5 font-medium tracking-wider font-hindi text-center whitespace-nowrap">🎯 दौरा / कार्यक्रम</th>
                            <th className="px-6 py-5 font-medium tracking-wider font-hindi text-center whitespace-nowrap">👥 कौन/टैग</th>
                            <th className="px-6 py-5 font-medium tracking-wider w-1/3 font-hindi text-center">📝 विवरण</th>
                            <th className="px-6 py-5 font-medium tracking-wider font-hindi text-center whitespace-nowrap">🔗 स्रोत</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-slate-300">
                        {tweets.map((tweet) => (
                            <tr key={tweet.tweet_id} className="hover:bg-white/5 transition-colors group">
                                <td className="px-6 py-4 whitespace-nowrap text-slate-400 font-hindi text-xs text-center">
                                    {formatDate(tweet.parsed_data_v8.event_date || tweet.created_at.split('T')[0])}
                                </td>
                                <td className="px-6 py-4 font-medium text-white text-center">
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="p-1.5 bg-white/5 rounded-full"><MapPin size={12} className="text-[#8BF5E6]" /></div>
                                        <span className="font-hindi">
                                            {tweet.parsed_data_v8.location?.ulb || tweet.parsed_data_v8.location?.village || tweet.parsed_data_v8.location?.district || "अज्ञात"}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium border font-hindi ${tweet.parsed_data_v8.event_type === 'बैठक' ? 'bg-blue-500/10 border-blue-500/20 text-blue-300' :
                                        tweet.parsed_data_v8.event_type === 'दौरा' ? 'bg-pink-500/10 border-pink-500/20 text-pink-300' :
                                            tweet.parsed_data_v8.event_type === 'जनसम्पर्क' ? 'bg-green-500/10 border-green-500/20 text-green-300' :
                                                'bg-slate-500/10 border-slate-500/20 text-slate-300'
                                        }`}>
                                        {tweet.parsed_data_v8.event_type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <div className="flex gap-1.5 flex-wrap justify-center">
                                        {tweet.parsed_data_v8.people_canonical?.length > 0 ? tweet.parsed_data_v8.people_canonical.slice(0, 2).map(tag => (
                                            <span key={tag} className="text-[10px] px-2 py-1 bg-white/5 rounded-md text-slate-400 border border-white/5 font-hindi">{tag}</span>
                                        )) : <span className="text-slate-600">-</span>}
                                    </div>
                                </td>
                                {/* Full text display - removed truncation classes */}
                                <td className="px-6 py-4 text-slate-400 group-hover:text-slate-200 transition-colors font-hindi text-center">
                                    {tweet.raw_text}
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <a
                                        href={`https://twitter.com/i/web/status/${tweet.tweet_id}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-400 hover:text-blue-300 transition-colors inline-block"
                                        onMouseEnter={(e) => onMouseEnter(e, tweet)}
                                        onMouseLeave={onMouseLeave}
                                    >
                                        <ExternalLink size={14} />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination Controls */}
            {renderPagination()}
        </div>
    );
};

export default TweetTable;
