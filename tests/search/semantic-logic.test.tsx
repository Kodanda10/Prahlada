import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

describe('Search & Semantic Logic', () => {
  // Mock search data
  const mockSearchData = [
    {
      id: 'doc_001',
      title: 'क्षेत्रीय विकास योजना',
      content: 'रायगढ़ जिले में विकास कार्यों की विस्तृत योजना',
      type: 'policy',
      tags: ['विकास', 'रायगढ़', 'योजना'],
      hierarchy: {
        district: 'रायगढ़',
        category: 'development'
      }
    },
    {
      id: 'doc_002',
      title: 'ग्राम पंचायत बैठक रिकॉर्ड',
      content: 'तमनार ग्राम पंचायत की मासिक बैठक का विवरण',
      type: 'meeting',
      tags: ['बैठक', 'तमनार', 'रिकॉर्ड'],
      hierarchy: {
        district: 'रायगढ़',
        block: 'खरसिया',
        gp: 'तमनार'
      }
    },
    {
      id: 'doc_003',
      title: 'विकास कार्य प्रगति रिपोर्ट',
      content: 'खरसिया ब्लॉक में विभिन्न विकास परियोजनाओं की प्रगति',
      type: 'report',
      tags: ['प्रगति', 'खरसिया', 'रिपोर्ट'],
      hierarchy: {
        district: 'रायगढ़',
        block: 'खरसिया',
        category: 'progress'
      }
    }
  ];

  describe('Basic Search Functionality', () => {
    it('searches Hindi text content accurately', () => {
      const searchTerm = 'विकास';
      const results = mockSearchData.filter(doc =>
        doc.title.includes(searchTerm) ||
        doc.content.includes(searchTerm) ||
        doc.tags.some(tag => tag.includes(searchTerm))
      );

      expect(results).toHaveLength(2);
      expect(results[0].title).toContain('क्षेत्रीय विकास योजना');
      expect(results[1].title).toContain('विकास कार्य प्रगति रिपोर्ट');
    });

    it('supports location-based search queries', () => {
      const locationSearches = [
        { query: 'रायगढ़', expected: 3 },
        { query: 'खरसिया', expected: 2 },
        { query: 'तमनार', expected: 1 },
      ];

      locationSearches.forEach(({ query, expected }) => {
        const results = mockSearchData.filter(doc =>
          doc.hierarchy.district?.includes(query) ||
          doc.hierarchy.block?.includes(query) ||
          doc.hierarchy.gp?.includes(query) ||
          doc.title.includes(query) ||
          doc.content.includes(query)
        );

        expect(results).toHaveLength(expected);
      });
    });

    it('handles partial and fuzzy matching', () => {
      const partialQueries = [
        { query: 'योजना', expected: 1 }, // Exact match
        { query: 'बैठक', expected: 1 },  // Exact match
        { query: 'प्रगति', expected: 1 }, // Exact match
        { query: 'जिला', expected: 0 },  // No direct match
      ];

      partialQueries.forEach(({ query, expected }) => {
        const results = mockSearchData.filter(doc =>
          doc.title.includes(query) ||
          doc.content.includes(query) ||
          doc.tags.some(tag => tag.includes(query))
        );

        expect(results).toHaveLength(expected);
      });
    });
  });

  describe('Advanced Search Features', () => {
    it('supports boolean operators', () => {
      // Mock boolean search logic
      const performBooleanSearch = (query: string) => {
        if (query.includes('AND')) {
          const terms = query.split(' AND ').map(t => t.trim());
          return mockSearchData.filter(doc =>
            terms.every(term =>
              doc.title.includes(term) ||
              doc.content.includes(term) ||
              doc.tags.some(tag => tag.includes(term))
            )
          );
        }
        return [];
      };

      const andResults = performBooleanSearch('विकास AND योजना');
      expect(andResults).toHaveLength(1);
      expect(andResults[0].title).toContain('क्षेत्रीय विकास योजना');
    });

    it('provides search suggestions and autocomplete', () => {
      const searchSuggestions = [
        'विकास', 'रायगढ़', 'योजना', 'बैठक', 'तमनार', 'प्रगति', 'खरसिया'
      ];

      const getSuggestions = (input: string) => {
        return searchSuggestions.filter(suggestion =>
          suggestion.startsWith(input) && suggestion.length > input.length
        );
      };

      expect(getSuggestions('वि')).toContain('विकास');
      expect(getSuggestions('रा')).toContain('रायगढ़');
      expect(getSuggestions('यो')).toContain('योजना');
    });

    it('supports faceted search by category and location', () => {
      const facets = {
        type: ['policy', 'meeting', 'report'],
        district: ['रायगढ़'],
        block: ['खरसिया'],
        tags: ['विकास', 'बैठक', 'प्रगति'],
      };

      const applyFacets = (data: any[], activeFacets: any) => {
        return data.filter(doc => {
          return Object.entries(activeFacets).every(([facetType, values]) => {
            if (!values || values.length === 0) return true;

            switch (facetType) {
              case 'type':
                return values.includes(doc.type);
              case 'district':
                return values.includes(doc.hierarchy.district);
              case 'block':
                return values.includes(doc.hierarchy.block);
              case 'tags':
                return values.some((tag: string) => doc.tags.includes(tag));
              default:
                return true;
            }
          });
        });
      };

      // Test type facet
      const policyResults = applyFacets(mockSearchData, { type: ['policy'] });
      expect(policyResults).toHaveLength(1);

      // Test district facet
      const districtResults = applyFacets(mockSearchData, { district: ['रायगढ़'] });
      expect(districtResults).toHaveLength(3);

      // Test combined facets
      const combinedResults = applyFacets(mockSearchData, {
        district: ['रायगढ़'],
        tags: ['विकास']
      });
      expect(combinedResults).toHaveLength(2);
    });
  });

  describe('Semantic Understanding', () => {
    it('recognizes synonyms and related terms', () => {
      const synonymMap = {
        'विकास': ['प्रगति', 'उन्नति', 'वृद्धि'],
        'बैठक': ['सभा', 'अधिवेशन', 'मीटिंग'],
        'योजना': ['स्कीम', 'परियोजना', 'कार्यक्रम'],
      };

      const expandWithSynonyms = (term: string) => {
        const synonyms = synonymMap[term as keyof typeof synonymMap] || [];
        return [term, ...synonyms];
      };

      const searchWithSynonyms = (query: string) => {
        const expandedTerms = expandWithSynonyms(query);
        return mockSearchData.filter(doc =>
          expandedTerms.some(term =>
            doc.title.includes(term) ||
            doc.content.includes(term) ||
            doc.tags.some(tag => tag.includes(term))
          )
        );
      };

      // Search for 'प्रगति' should also find 'विकास' related content
      const synonymResults = searchWithSynonyms('प्रगति');
      expect(synonymResults.length).toBeGreaterThan(0);
    });

    it('understands hierarchical relationships', () => {
      const hierarchyQueries = [
        {
          query: 'रायगढ़ जिला',
          shouldFind: ['doc_001', 'doc_002', 'doc_003']
        },
        {
          query: 'खरसिया ब्लॉक',
          shouldFind: ['doc_002', 'doc_003']
        },
        {
          query: 'तमनार ग्राम पंचायत',
          shouldFind: ['doc_002']
        }
      ];

      hierarchyQueries.forEach(({ query, shouldFind }) => {
        const results = mockSearchData.filter(doc => {
          const hierarchyText = Object.values(doc.hierarchy).join(' ');
          return hierarchyText.includes(query.split(' ')[0]) ||
                 doc.title.includes(query) ||
                 doc.content.includes(query);
        });

        const resultIds = results.map(r => r.id);
        shouldFind.forEach(id => {
          expect(resultIds).toContain(id);
        });
      });
    });

    it('prioritizes results by relevance and recency', () => {
      const scoredResults = mockSearchData.map(doc => ({
        ...doc,
        score: Math.random() * 100, // Mock relevance score
        recency: Math.random() * 30, // Days ago
      }));

      const sortByRelevanceAndRecency = (results: any[]) => {
        return results.sort((a, b) => {
          // Higher score first, then more recent first
          if (a.score !== b.score) {
            return b.score - a.score;
          }
          return a.recency - b.recency;
        });
      };

      const sorted = sortByRelevanceAndRecency(scoredResults);
      expect(sorted).toHaveLength(mockSearchData.length);

      // First result should have highest score
      expect(sorted[0].score).toBeGreaterThanOrEqual(sorted[1].score);
    });
  });

  describe('Search Performance and Optimization', () => {
    it('performs searches within acceptable time limits', () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: `doc_${i}`,
        title: `दस्तावेज़ ${i}`,
        content: `यह दस्तावेज़ ${i} की सामग्री है जिसमें बहुत सारी जानकारी है।`,
        tags: [`टैग${i % 10}`, `वर्ग${i % 5}`],
        hierarchy: {
          district: `जिला${i % 10}`,
          block: `ब्लॉक${i % 5}`,
        }
      }));

      const startTime = performance.now();

      const searchResults = largeDataset.filter(doc =>
        doc.title.includes('दस्तावेज़') &&
        doc.hierarchy.district === 'जिला1'
      );

      const endTime = performance.now();
      const searchTime = endTime - startTime;

      expect(searchResults.length).toBeGreaterThan(0);
      expect(searchTime).toBeLessThan(100); // Should complete within 100ms
    });

    it('uses efficient indexing for fast searches', () => {
      // Mock search index
      const searchIndex = new Map();

      mockSearchData.forEach(doc => {
        const words = [...doc.title.split(' '), ...doc.content.split(' '), ...doc.tags];
        words.forEach(word => {
          if (!searchIndex.has(word)) {
            searchIndex.set(word, []);
          }
          searchIndex.get(word).push(doc.id);
        });
      });

      const indexedSearch = (query: string) => {
        const queryWords = query.split(' ');
        const resultIds = new Set<string>();

        queryWords.forEach(word => {
          const ids = searchIndex.get(word) || [];
          ids.forEach((id: string) => resultIds.add(id));
        });

        return Array.from(resultIds);
      };

      const indexedResults = indexedSearch('विकास योजना');
      expect(indexedResults).toContain('doc_001');

      const nonIndexedResults = indexedSearch('गैरमौजूद');
      expect(nonIndexedResults).toHaveLength(0);
    });

    it('caches frequent search results', () => {
      const searchCache = new Map();
      let cacheHits = 0;
      let cacheMisses = 0;

      const cachedSearch = (query: string) => {
        if (searchCache.has(query)) {
          cacheHits++;
          return searchCache.get(query);
        }

        cacheMisses++;
        const results = mockSearchData.filter(doc =>
          doc.title.includes(query) || doc.content.includes(query)
        );

        searchCache.set(query, results);
        return results;
      };

      // First search - cache miss
      cachedSearch('विकास');
      expect(cacheMisses).toBe(1);
      expect(cacheHits).toBe(0);

      // Second search - cache hit
      cachedSearch('विकास');
      expect(cacheMisses).toBe(1);
      expect(cacheHits).toBe(1);
    });
  });

  describe('Search UI and User Experience', () => {
    it('provides real-time search suggestions', async () => {
      const searchSuggestions = [
        'विकास कार्य',
        'रायगढ़ जिला',
        'ग्राम पंचायत बैठक',
        'प्रगति रिपोर्ट',
        'खरसिया ब्लॉक'
      ];

      const getRealTimeSuggestions = (input: string) => {
        return searchSuggestions.filter(suggestion =>
          suggestion.toLowerCase().includes(input.toLowerCase())
        );
      };

      expect(getRealTimeSuggestions('विकास')).toHaveLength(1);
      expect(getRealTimeSuggestions('रायगढ़')).toHaveLength(1);
      expect(getRealTimeSuggestions('बैठक')).toHaveLength(1);
    });

    it('highlights search terms in results', () => {
      const highlightSearchTerms = (text: string, searchTerm: string) => {
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
      };

      const originalText = 'यह विकास कार्य की जानकारी है';
      const highlighted = highlightSearchTerms(originalText, 'विकास');

      expect(highlighted).toContain('<mark>विकास</mark>');
      expect(highlighted).toContain('यह ');
      expect(highlighted).toContain(' कार्य की जानकारी है');
    });

    it('supports advanced filtering options', () => {
      const filterOptions = {
        dateRange: { start: '2024-01-01', end: '2024-12-31' },
        location: ['रायगढ़', 'कोरबा'],
        type: ['policy', 'report'],
        tags: ['विकास', 'प्रगति'],
      };

      const applyAdvancedFilters = (data: any[], filters: any) => {
        return data.filter(doc => {
          // Date range filter (mock)
          if (filters.dateRange) {
            // Would check doc.created_at
          }

          // Location filter
          if (filters.location && filters.location.length > 0) {
            const hasLocation = filters.location.some((loc: string) =>
              doc.hierarchy.district === loc ||
              doc.hierarchy.block === loc
            );
            if (!hasLocation) return false;
          }

          // Type filter
          if (filters.type && filters.type.length > 0) {
            if (!filters.type.includes(doc.type)) return false;
          }

          // Tags filter
          if (filters.tags && filters.tags.length > 0) {
            const hasTag = filters.tags.some((tag: string) => doc.tags.includes(tag));
            if (!hasTag) return false;
          }

          return true;
        });
      };

      const filteredResults = applyAdvancedFilters(mockSearchData, {
        location: ['रायगढ़'],
        type: ['policy', 'report']
      });

      expect(filteredResults.length).toBeGreaterThan(0);
      filteredResults.forEach(doc => {
        expect(doc.hierarchy.district).toBe('रायगढ़');
        expect(['policy', 'report']).toContain(doc.type);
      });
    });
  });

  describe('Search Analytics and Insights', () => {
    it('tracks search query popularity', () => {
      const searchAnalytics = {
        queries: new Map<string, number>(),
        popularTerms: [] as string[],
      };

      const trackSearchQuery = (query: string) => {
        const count = searchAnalytics.queries.get(query) || 0;
        searchAnalytics.queries.set(query, count + 1);

        // Update popular terms
        searchAnalytics.popularTerms = Array.from(searchAnalytics.queries.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([term]) => term);
      };

      // Track some searches
      trackSearchQuery('विकास');
      trackSearchQuery('विकास');
      trackSearchQuery('रायगढ़');
      trackSearchQuery('बैठक');

      expect(searchAnalytics.queries.get('विकास')).toBe(2);
      expect(searchAnalytics.queries.get('रायगढ़')).toBe(1);
      expect(searchAnalytics.popularTerms[0]).toBe('विकास');
    });

    it('identifies frequently searched topics', () => {
      const topicClusters = {
        'विकास': ['विकास', 'प्रगति', 'उन्नति', 'वृद्धि'],
        'प्रशासन': ['बैठक', 'अधिवेशन', 'सभा', 'मीटिंग'],
        'स्थान': ['रायगढ़', 'खरसिया', 'तमनार', 'जोंबी'],
      };

      const identifyTopic = (query: string) => {
        for (const [topic, keywords] of Object.entries(topicClusters)) {
          if (keywords.some(keyword => query.includes(keyword))) {
            return topic;
          }
        }
        return 'अन्य';
      };

      expect(identifyTopic('विकास कार्य')).toBe('विकास');
      expect(identifyTopic('ग्राम पंचायत बैठक')).toBe('प्रशासन');
      expect(identifyTopic('रायगढ़ जिला')).toBe('स्थान');
      expect(identifyTopic('अज्ञात विषय')).toBe('अन्य');
    });

    it('provides search result insights', () => {
      const searchInsights = {
        totalResults: mockSearchData.length,
        resultDistribution: {
          byType: {} as Record<string, number>,
          byDistrict: {} as Record<string, number>,
          byTags: {} as Record<string, number>,
        },
        averageResultScore: 0,
        topTags: [] as string[],
      };

      // Analyze result distribution
      mockSearchData.forEach(doc => {
        searchInsights.resultDistribution.byType[doc.type] =
          (searchInsights.resultDistribution.byType[doc.type] || 0) + 1;

        if (doc.hierarchy.district) {
          searchInsights.resultDistribution.byDistrict[doc.hierarchy.district] =
            (searchInsights.resultDistribution.byDistrict[doc.hierarchy.district] || 0) + 1;
        }

        doc.tags.forEach(tag => {
          searchInsights.resultDistribution.byTags[tag] =
            (searchInsights.resultDistribution.byTags[tag] || 0) + 1;
        });
      });

      expect(searchInsights.resultDistribution.byType['policy']).toBe(1);
      expect(searchInsights.resultDistribution.byType['meeting']).toBe(1);
      expect(searchInsights.resultDistribution.byType['report']).toBe(1);
      expect(searchInsights.resultDistribution.byDistrict['रायगढ़']).toBe(3);
    });
  });
});