import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach, type MockInstance } from 'vitest';
import Search from '../../components/Search';
import { searchService, SearchResult } from '../../services/search';
import { loadRealTweets } from '../../utils/testDataLoader';
import { ParsedEvent } from '../../types';

describe('SemanticSearchHindiMapping Integration', () => {
  let realTweets: ParsedEvent[];
  let searchServiceSpy: MockInstance;

  beforeAll(() => {
    realTweets = loadRealTweets();
    if (realTweets.length === 0) {
      throw new Error('No real tweets loaded for testing');
    }

    // Mock searchService.search to simulate semantic mapping
    searchServiceSpy = vi.spyOn(searchService, 'search').mockImplementation(async ({ query }) => {
      const lowerQuery = query.toLowerCase();
      const simulatedResults: SearchResult[] = [];

      // Simple semantic mapping simulation:
      // If query is in Hindi, look for exact match or known semantic equivalents in descriptions.
      // For simplicity, we'll map a few common Hindi terms to expected content in real tweets.

      const queryMap: { [key: string]: string[] } = {
        'विकास': ['development', 'प्रगति'], // "विकास" means development/progress
        'स्वास्थ्य': ['health', 'स्वास्थ्य'], // "स्वास्थ्य" means health
        'योजना': ['scheme', 'योजना'], // "योजना" means scheme/plan
        'रायपुर': ['raipur', 'रायपुर'], // Location
      };

      const searchTerms = queryMap[lowerQuery] || [lowerQuery]; // Default to exact query

      // Filter real tweets for content that matches semantic terms
      realTweets.forEach(tweet => {
        const text = tweet.raw_text.toLowerCase();
        const eventType = tweet.parsed_data_v8.event_type?.toLowerCase() || '';
        const location = tweet.parsed_data_v8.location?.canonical?.toLowerCase() || '';

        const isMatch = searchTerms.some(term =>
          text.includes(term.toLowerCase()) ||
          eventType.includes(term.toLowerCase()) ||
          location.includes(term.toLowerCase())
        );

        if (isMatch) {
          simulatedResults.push({
            id: tweet.tweet_id,
            title: tweet.parsed_data_v8.event_type || 'Unknown',
            description: tweet.raw_text,
            category: tweet.parsed_data_v8.event_type || 'General',
            location: tweet.parsed_data_v8.location?.canonical,
            timestamp: tweet.created_at,
            relevance: 0.9,
          });
        }
      });
      return simulatedResults.slice(0, 5); // Limit results
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('sends Hindi query and displays semantically mapped results', async () => {
    render(<Search />);

    const searchInput = screen.getByPlaceholderText('खोजें (Search)...');
    fireEvent.change(searchInput, { target: { value: 'विकास' } });

    await waitFor(() => {
      // Expect some results for 'विकास'
      expect(screen.getAllByText(/विकास|development|प्रगति/i).length).toBeGreaterThan(0);
      expect(searchServiceSpy).toHaveBeenCalledWith(expect.objectContaining({ query: 'विकास' }));
    }, { timeout: 1000 }); // Increase timeout for debounce

    fireEvent.change(searchInput, { target: { value: 'स्वास्थ्य' } });

    await waitFor(() => {
      // Expect some results for 'स्वास्थ्य'
      expect(screen.getAllByText(/स्वास्थ्य|health/i).length).toBeGreaterThan(0);
      expect(searchServiceSpy).toHaveBeenCalledWith(expect.objectContaining({ query: 'स्वास्थ्य' }));
    }, { timeout: 1000 });
  });

  it('displays location-based results for Hindi queries', async () => {
    render(<Search />);

    const searchInput = screen.getByPlaceholderText('खोजें (Search)...');
    fireEvent.change(searchInput, { target: { value: 'रायपुर' } });

    await waitFor(() => {
      // Expect results for 'रायपुर'
      expect(screen.getAllByText(/रायपुर|raipur/i).length).toBeGreaterThan(0);
      expect(searchServiceSpy).toHaveBeenCalledWith(expect.objectContaining({ query: 'रायपुर' }));
    }, { timeout: 1000 });
  });

  it('handles empty query without making API calls', async () => {
    render(<Search />);

    const searchInput = screen.getByPlaceholderText('खोजें (Search)...');
    fireEvent.change(searchInput, { target: { value: 'some query' } });
    await waitFor(() => expect(searchServiceSpy).toHaveBeenCalled());

    searchServiceSpy.mockClear(); // Clear previous calls
    fireEvent.change(searchInput, { target: { value: '' } }); // Clear query

    await waitFor(() => {
      expect(screen.queryByText('विकास')).not.toBeInTheDocument(); // Assuming 'विकास' was in prior results
      expect(searchServiceSpy).not.toHaveBeenCalled(); // No API call for empty query
    }, { timeout: 1000 });
  });
});
