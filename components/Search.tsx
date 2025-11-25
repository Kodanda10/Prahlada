import React, { useState, useEffect } from 'react';
import { Search as SearchIcon, Loader2 } from 'lucide-react';
import { searchService, SearchResult } from '../services/search';

interface SearchProps {
  onResultSelect?: (result: SearchResult) => void;
  className?: string;
}

const Search: React.FC<SearchProps> = ({ onResultSelect, className = '' }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const debounceTimer = setTimeout(async () => {
      if (query.trim().length > 2) {
        setIsLoading(true);
        try {
          const data = await searchService.search({ query });
          setResults(data);
          setShowResults(true);
        } catch (error) {
          console.error('Search error:', error);
        } finally {
          setIsLoading(false);
        }
      } else {
        setResults([]);
        setShowResults(false);
      }
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [query]);

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="खोजें (Search)..."
          className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-full text-white placeholder-slate-400 focus:outline-none focus:border-[#8BF5E6] focus:ring-1 focus:ring-[#8BF5E6] transition-colors"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#8BF5E6] animate-spin" size={18} />
        )}
      </div>

      {showResults && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl max-h-96 overflow-y-auto z-50">
          {results.map((result) => (
            <div
              key={result.id}
              onClick={() => {
                onResultSelect?.(result);
                setShowResults(false);
                setQuery(result.title);
              }}
              className="p-3 hover:bg-white/5 cursor-pointer transition-colors border-b border-white/5 last:border-0"
            >
              <div className="font-medium text-white text-sm mb-1">{result.title}</div>
              <div className="text-xs text-slate-400 line-clamp-2">{result.description}</div>
              <div className="flex gap-2 mt-2">
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#8BF5E6]/10 text-[#8BF5E6]">
                  {result.category}
                </span>
                {result.location && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400">
                    {result.location}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Search;
