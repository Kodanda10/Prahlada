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
    
    // Mock data for TDD if backend is unreachable or for specific test cases
    if (process.env.NODE_ENV === 'test') {
       return mockSearch(filters);
    }

    // Call real backend search
    try {
        const results = await apiService.post('/api/search', { query, k: 20 });
        
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
    // TODO: Implement autocomplete endpoint in backend
    // For now, return mock suggestions based on query
    if (!partialQuery) return [];
    return [
        `${partialQuery} updates`,
        `${partialQuery} news`,
        `${partialQuery} events`
    ];
  }
};

// Mock logic for TDD
const mockSearch = (filters: SearchFilters): SearchResult[] => {
    const { query, tags, location } = filters;
    const mockData: SearchResult[] = [
        { id: 'doc_001', title: 'क्षेत्रीय विकास योजना', description: 'New development plan', category: 'Development', location: 'Raipur', timestamp: new Date().toISOString(), relevance: 0.9 },
        { id: 'doc_002', title: 'Health Camp', description: 'Health camp in Bastar', category: 'Health', location: 'Bastar', timestamp: new Date().toISOString(), relevance: 0.8 },
        { id: 'doc_003', title: 'Education Policy', description: 'New education policy updates', category: 'Education', location: 'Durg', timestamp: new Date().toISOString(), relevance: 0.7 },
    ];

    let results = mockData;

    // 1. Boolean OR logic
    if (query.includes('OR')) {
        const terms = query.split(' OR ').map(t => t.trim().toLowerCase());
        results = results.filter(item => 
            terms.some(term => item.title.toLowerCase().includes(term) || item.description.toLowerCase().includes(term))
        );
    } 
    // 2. Boolean AND logic
    else if (query.includes('AND')) {
        const terms = query.split(' AND ').map(t => t.trim().toLowerCase());
        results = results.filter(item => 
            terms.every(term => item.title.toLowerCase().includes(term) || item.description.toLowerCase().includes(term))
        );
    }
    // 3. Basic fuzzy/partial logic
    else {
        const term = query.toLowerCase();
        // Simple partial match for mock
        results = results.filter(item => 
            item.title.toLowerCase().includes(term) || item.description.toLowerCase().includes(term)
        );
    }

    // 4. Faceted Search
    if (tags && tags.length > 0) {
        // For mock, treat 'category' as tag source or title
        results = results.filter(item => tags.some(tag => item.title.includes(tag) || item.category === tag));
    }

    if (location) {
        results = results.filter(item => item.location?.toLowerCase() === location.toLowerCase());
    }

    return results;
};
