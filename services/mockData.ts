
import { ParsedEvent, Stats } from '../types';

// DEPRECATED: Do not use. Fetch from API or use testDataLoader.ts for tests.
export const MOCK_STATS: Stats = {
  total_tweets: 0,
  parsed_success: 0,
  pending: 0,
  errors: 0
};

export const MOCK_EVENTS: ParsedEvent[] = [];

export const MOCK_REVIEW_QUEUE: ParsedEvent[] = [];


export const DISTRICT_DATA = [
  { name: 'रायगढ़', value: 450 },
  { name: 'जशपुर', value: 320 },
  { name: 'सरगुजा', value: 210 },
  { name: 'बिलासपुर', value: 180 },
  { name: 'कोरबा', value: 150 },
];

export const EVENT_TYPE_DATA = [
  { name: 'जनसम्पर्क', value: 400, fill: '#06b6d4' },
  { name: 'सभा', value: 300, fill: '#3b82f6' },
  { name: 'समीक्षा बैठक', value: 200, fill: '#8b5cf6' },
  { name: 'उद्घाटन', value: 150, fill: '#ec4899' },
  { name: 'अन्य', value: 100, fill: '#64748b' },
];
