import { describe, it, expect, vi, beforeEach } from 'vitest';
import { searchService } from '../../services/search';

// Set test environment
process.env.NODE_ENV = 'test';

describe('Search Service', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('search', () => {
        it('returns results for basic query', async () => {
            const results = await searchService.search({ query: 'Education' });

            expect(results.length).toBeGreaterThan(0);
            const educationResult = results.find(r => r.title.includes('Education'));
            expect(educationResult).toBeDefined();
        });

        it('supports OR boolean logic', async () => {
            const results = await searchService.search({
                query: 'Health OR Development'
            });

            expect(results.length).toBeGreaterThan(0);
            const hasHealthOrDev = results.some(r =>
                r.title.toLowerCase().includes('health') ||
                r.title.toLowerCase().includes('development')
            );
            expect(hasHealthOrDev).toBe(true);
        });

        it('supports AND boolean logic', async () => {
            const results = await searchService.search({
                query: 'Health AND Camp'
            });

            const hasHealthAndCamp = results.every(r =>
                r.description.toLowerCase().includes('health') &&
                r.description.toLowerCase().includes('camp')
            );
            expect(hasHealthAndCamp).toBe(true);
        });

        it('filters by location', async () => {
            const results = await searchService.search({
                query: '',
                location: 'Raipur',
            });

            results.forEach(result => {
                expect(result.location).toBe('Raipur');
            });
        });

        it('filters by tags/category', async () => {
            const results = await searchService.search({
                query: '',
                tags: ['Health'],
            });

            const hasHealthCategory = results.some(r => r.category === 'Health');
            expect(hasHealthCategory).toBe(true);
        });

        it('returns empty array for no matches', async () => {
            const results = await searchService.search({
                query: 'XYZ_NONEXISTENT_QUERY_123'
            });

            expect(results).toEqual([]);
        });

        it('returns results with relevance scores', async () => {
            const results = await searchService.search({ query: 'Health' });

            results.forEach(result => {
                expect(result.relevance).toBeGreaterThanOrEqual(0);
                expect(result.relevance).toBeLessThanOrEqual(1);
            });
        });
    });

    describe('getSuggestions', () => {
        it('returns suggestions for partial query', async () => {
            const suggestions = await searchService.getSuggestions('health');

            expect(suggestions.length).toBeGreaterThan(0);
            expect(suggestions.some(s => s.includes('health'))).toBe(true);
        });

        it('returns empty array for empty query', async () => {
            const suggestions = await searchService.getSuggestions('');

            expect(suggestions).toEqual([]);
        });

        it('includes common search suffixes', async () => {
            const suggestions = await searchService.getSuggestions('test');

            expect(suggestions).toContain('test updates');
            expect(suggestions).toContain('test news');
            expect(suggestions).toContain('test events');
        });
    });
});
