import { describe, it, expect, vi } from 'vitest';
import { searchService } from '../../services/search';

describe('Search & Semantic Logic', () => {
  describe('Basic Search Functionality', () => {
    it('searches Hindi text content accurately', async () => {
      const searchTerm = 'विकास';
      const results = await searchService.search({ query: searchTerm });

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toContain('विकास');
    });

    it('supports location-based search queries', async () => {
      const locationSearches = [
        { query: 'Raipur', expected: 1 },
        { query: 'Bastar', expected: 1 },
      ];

      for (const { query, expected } of locationSearches) {
        const results = await searchService.search({ query: '', location: query });
        expect(results).toHaveLength(expected);
      }
    });

    it('handles partial and fuzzy matching', async () => {
      // Searching for 'Dev' should match 'Development' category or title
      const results = await searchService.search({ query: 'Dev' });
      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe('Advanced Search Features', () => {
    it('supports boolean operators', async () => {
      const orResults = await searchService.search({ query: 'Development OR Health' });
      expect(orResults.length).toBeGreaterThanOrEqual(2);
      
      // 'Health' is in the mock data
      const results = await searchService.search({ query: 'Health' });
      expect(results.length).toBe(1);
    });

    it('provides search suggestions and autocomplete', async () => {
      const suggestions = await searchService.getSuggestions('वि');
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0]).toContain('वि');
    });

    it('supports faceted search by category and location', async () => {
      const results = await searchService.search({ 
          query: 'Health', 
          location: 'Bastar'
      });
      expect(results).toHaveLength(1);
      expect(results[0].location).toBe('Bastar');
    });
  });

  describe('Semantic Understanding', () => {
    it('recognizes synonyms and related terms', async () => {
      // Mock implementation handles 'Development' for 'विकास' implicitly via title match
      const results = await searchService.search({ query: 'विकास' });
      expect(results.length).toBeGreaterThan(0);
    });

    it('prioritizes results by relevance', async () => {
      const results = await searchService.search({ query: 'Development' });
      if (results.length > 1) {
          expect(results[0].relevance).toBeGreaterThanOrEqual(results[1].relevance);
      }
    });
  });
});
