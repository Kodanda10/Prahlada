import React from 'react';
import { MapPin, Tag, Calendar, X } from 'lucide-react';

interface TweetFiltersProps {
    locationFilter: string;
    setLocationFilter: (value: string) => void;
    tagFilter: string;
    setTagFilter: (value: string) => void;
    dateFrom: string;
    setDateFrom: (value: string) => void;
    dateTo: string;
    setDateTo: (value: string) => void;
    totalCount: number;
    filteredCount: number;
    onClearFilters: () => void;
}

const TweetFilters: React.FC<TweetFiltersProps> = ({
    locationFilter,
    setLocationFilter,
    tagFilter,
    setTagFilter,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    totalCount,
    filteredCount,
    onClearFilters,
}) => {
    return (
        <div className="flex flex-col gap-4 w-full">
            <div className="flex flex-wrap gap-3 items-center w-full">
                {/* Location Filter */}
                <div className="relative group flex-1 min-w-[200px]">
                    <MapPin className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                    <input
                        type="text"
                        value={locationFilter}
                        onChange={(e) => setLocationFilter(e.target.value)}
                        placeholder="स्थान फ़िल्टर..."
                        className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500"
                    />
                </div>

                {/* Tag/Mention Filter */}
                <div className="relative group flex-1 min-w-[200px]">
                    <Tag className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                    <input
                        type="text"
                        value={tagFilter}
                        onChange={(e) => setTagFilter(e.target.value)}
                        placeholder="टैग/मेंशन फ़िल्टर..."
                        className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500"
                    />
                </div>

                {/* Date From */}
                <div className="relative group flex-1 min-w-[150px]">
                    <label className="text-[10px] text-slate-400 font-hindi absolute -top-4 left-1">तिथि से</label>
                    <Calendar className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-slate-300 focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500 cursor-pointer"
                        placeholder="dd/mm/yyyy"
                    />
                </div>

                {/* Date To */}
                <div className="relative group flex-1 min-w-[150px]">
                    <label className="text-[10px] text-slate-400 font-hindi absolute -top-4 left-1">तिथि तक</label>
                    <Calendar className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                    <input
                        type="date"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-slate-300 focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500 cursor-pointer"
                        placeholder="dd/mm/yyyy"
                    />
                </div>

                {/* Clear Filters Button */}
                <button
                    onClick={onClearFilters}
                    className="px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-xl transition-colors text-sm font-medium font-hindi flex items-center gap-2 whitespace-nowrap"
                >
                    <X size={16} /> फ़िल्टर साफ़ करें
                </button>
            </div>

            {/* Count Display */}
            <div className="text-sm text-slate-400 font-hindi px-1">
                दिखा रहे हैं: <span className="text-white font-bold">{filteredCount}</span> / {totalCount}
            </div>
        </div>
    );
};

export default TweetFilters;
