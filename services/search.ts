import { apiService } from './api';

export interface SearchResult {
  id: string;
  title: string; // Mapped from text for now
  description: string; // Mapped from text
  category: string; // Default 'General'
  location?: string;
  timestamp: string;
  relevance: number;
}

export interface SearchFilters {
  query: string;
  tags?: string[];
  location?: string;
  dateRange?: { start: Date; end: Date };
}

export const searchService = {
  search: async (filters: SearchFilters): Promise<SearchResult[]> => {
    const { query, tags, location } = filters;

    // Call real backend search
    try {
      const results = await apiService.post('/api/search', { query, k: 20 }) as any[];

      // Map backend results to frontend SearchResult interface
      return results.map((res: any) => ({
        id: res.tweet_id,
        title: res.text.substring(0, 50) + (res.text.length > 50 ? '...' : ''),
        description: res.text,
        category: 'General', // Backend doesn't return category yet for search
        location: res.metadata?.location || 'Unknown',
        timestamp: new Date().toISOString(), // Placeholder, real timestamp needed from backend
        relevance: res.score
      }));
    } catch (error) {
      console.error("Search failed:", error);
      return [];
    }
  },

  getSuggestions: async (partialQuery: string): Promise<string[]> => {
    if (!partialQuery) return [];
    try {
      // Use existing search API to get relevant tweets
      // Request a small number of results to quickly generate suggestions
      const results = await apiService.post('/api/search', { query: partialQuery, k: 5 }) as any[];
      const suggestions = new Set<string>();

      results.forEach((res: any) => {
        // Add event types, location names, and people as potential suggestions
        if (res.parsed_data_v8?.event_type) suggestions.add(res.parsed_data_v8.event_type);
        if (res.parsed_data_v8?.location?.canonical) suggestions.add(res.parsed_data_v8.location.canonical);
        if (res.parsed_data_v8?.people_mentioned && res.parsed_data_v8.people_mentioned.length > 0) {
          res.parsed_data_v8.people_mentioned.forEach((person: string) => suggestions.add(person));
        }
        // Add the partial query itself as a suggestion if it yields results
        if (res.text && res.text.toLowerCase().includes(partialQuery.toLowerCase())) {
          suggestions.add(partialQuery);
        }
      });
      // Filter suggestions to ensure they start with the partial query and limit to 5
      return Array.from(suggestions)
        .filter(s => s.toLowerCase().startsWith(partialQuery.toLowerCase()))
        .slice(0, 5);
    } catch (error) {
      console.error("Failed to get suggestions:", error);
      return [];
    }
  }
};

